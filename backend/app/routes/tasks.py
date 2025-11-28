"""Task routes blueprint for background search task management"""

import logging
import threading
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import and_

from app.models import Availability, Court, Location
from app.services.availability_service import availability_service
from app.services.location_service import location_service
from app.services.search_service import search_service
from app.services.task_service import task_service
from app.utils import get_provider, token_required, validate_request_fields

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")
logger = logging.getLogger(__name__)


def run_search_task(task_id: str, search_params: dict):
    """Execute the search task in background

    This function runs in a separate thread and updates progress as it processes each location.
    """
    try:
        # Start the task
        task_service.start_task(task_id)

        # Extract search parameters
        search_date = datetime.strptime(search_params["date"], "%d/%m/%Y").date()
        start_time = datetime.strptime(search_params["start_time"], "%H:%M").time()
        end_time = datetime.strptime(search_params["end_time"], "%H:%M").time()
        duration_minutes = search_params.get("duration_minutes", 90)
        court_type = search_params.get("court_type", "all")
        court_config = search_params.get("court_config", "all")
        force_live = search_params.get("force_live_search", False)
        sport = search_params.get("sport", "PADEL")
        location_ids = search_params.get("location_ids", [])

        # If no locations specified, get all
        if not location_ids:
            location_ids = [loc.id for loc in location_service.get_all_locations()]

        total_locations = len(location_ids)
        date_str = search_date.strftime("%Y-%m-%d")

        # Update task with total locations
        task_service.update_task_progress(
            task_id,
            progress=5,
            current_step=f"Found {total_locations} locations to search",
            processed_locations=0,
        )

        # Fetch availability for each location
        live_locations = {}
        for _idx, loc_id in enumerate(location_ids):
            search_hash = search_service.generate_search_hash(search_date, loc_id)
            recent_live_search = search_service.get_recent_live_search(
                search_hash, max_age_minutes=15
            )

            if not force_live and recent_live_search:
                logger.info(f"[TASK] Using cached search data for location {loc_id}")
            else:
                live_locations[loc_id] = search_hash

        # Update task with live locations count
        task_service.update_task_progress(
            task_id,
            progress=5,
            current_step=f"Fetching availability for {len(live_locations)} locations...",
            processed_locations=0,
            total_locations=len(live_locations),
        )
        logger.info(
            f"[TASK] {task_id} - Initial: progress=5%, live_locations={len(live_locations)}, total_locations={len(live_locations)}"
        )

        # Process locations that need live fetch
        processed = 0
        for idx, (loc_id, search_hash) in enumerate(live_locations.items()):
            try:
                location = location_service.get_location_by_id(loc_id)
                if not location:
                    logger.warning(
                        f"[TASK] {task_id} - Location {loc_id} not found, skipping"
                    )
                    continue

                logger.info(
                    f"[TASK] {task_id} - Before fetch: processed={processed}, idx={idx}, len(live_locations)={len(live_locations)}"
                )

                provider = get_provider(location.provider)
                slots_stats = provider.fetch_and_store_availability(
                    loc_id, date_str, sport
                )
                logger.info(
                    f"[TASK] {task_id} - Fetched {location.name}: added={slots_stats['added']}, updated={slots_stats['updated']}"
                )

                # Record the search
                try:
                    search_service.create_search_request_record(
                        search_hash=search_hash,
                        date=search_date,
                        start_time=start_time,
                        end_time=end_time,
                        duration_minutes=duration_minutes,
                        court_type=court_type,
                        court_config=court_config,
                        location_id=loc_id,
                        live_search=True,
                        slots_found=slots_stats["added"] + slots_stats["updated"],
                    )
                except Exception as record_error:
                    logger.error(
                        f"[TASK] Failed to record search request: {record_error}"
                    )

                processed += 1

                # Update progress AFTER incrementing processed count
                # Map processed count (1 to len(live_locations)) to progress (5 to 85)
                progress = int(5 + (processed / max(len(live_locations), 1)) * 80)
                logger.info(
                    f"[TASK] {task_id} - After fetch: processed={processed}, progress={progress}%"
                )
                task_service.update_task_progress(
                    task_id,
                    progress=progress,
                    current_step=f"Fetched {location.name}",
                    processed_locations=processed,
                )

            except Exception as loc_error:
                logger.error(f"[TASK] Error fetching location {loc_id}: {loc_error}")

        # Update progress before querying results
        task_service.update_task_progress(
            task_id,
            progress=85,
            current_step="Compiling search results...",
            processed_locations=len(live_locations),
        )
        logger.info(
            f"[TASK] {task_id} - Compiling: progress=85%, processed_locations={len(live_locations)}"
        )

        # Build availability filters
        filters = [
            Availability.date == search_date,
            Availability.start_time >= start_time,
            Availability.start_time <= end_time,
            Availability.duration == duration_minutes,
            Availability.available,
            Court.location_id.in_(location_ids),
        ]

        if court_type == "indoor":
            filters.append(Court.indoor)
        elif court_type == "outdoor":
            filters.append(not Court.indoor)

        if court_config == "single":
            filters.append(not Court.double)
        elif court_config == "double":
            filters.append(Court.double)

        # Query availabilities
        query = (
            availability_service.session.query(Availability, Court, Location)
            .join(Court, Availability.court_id == Court.id)
            .join(Location, Court.location_id == Location.id)
            .filter(and_(*filters))
            .order_by(Availability.start_time)
        )

        results_tuples = query.all()

        # Group results by location and court
        locations_dict = {}
        for avail, court, location in results_tuples:
            location_id = location.id
            court_id = court.id

            if location_id not in locations_dict:
                locations_dict[location_id] = {
                    "location": {
                        "id": location.id,
                        "name": location.name,
                        "slug": location.slug,
                        "address": location.address,
                    },
                    "courts": {},
                    "provider": get_provider(location.provider),
                }

            provider = locations_dict[location_id]["provider"]

            if court_id not in locations_dict[location_id]["courts"]:
                locations_dict[location_id]["courts"][court_id] = {
                    "court": {
                        "id": court.id,
                        "name": court.name,
                        "court_type": court.sport or "standard",
                        "is_indoor": court.indoor or False,
                        "is_double": court.double or False,
                    },
                    "availabilities": [],
                }

            locations_dict[location_id]["courts"][court_id]["availabilities"].append(
                {
                    "id": avail.id,
                    "date": str(avail.date),
                    "start_time": str(avail.start_time),
                    "end_time": str(avail.end_time),
                    "price": avail.price,
                    "booking_url": provider.generate_booking_url(
                        tenant_id=location.tenant_id,
                        resource_id=court.resource_id,
                        availability_date=str(avail.date),
                        availability_start_time=str(avail.start_time),
                        duration_minutes=avail.duration,
                        location_timezone=location.timezone,
                    ),
                }
            )

        # Convert to final format
        results = []
        for _location_id, location_data in sorted(
            locations_dict.items(), key=lambda x: x[1]["location"]["name"]
        ):
            courts_list = []
            for _court_id, court_data in location_data["courts"].items():
                courts_list.append(court_data)
            results.append(
                {"location": location_data["location"], "courts": courts_list}
            )

        # Complete the task with results
        task_service.complete_task(
            task_id,
            {
                "locations": results,
                "cached": False,
                "cache_timestamp": None,
            },
        )

        logger.info(
            f"[TASK] Task {task_id} completed with {len(results)} locations - Final progress should be 100%"
        )

    except Exception as e:
        logger.error(f"[TASK] Task {task_id} failed: {str(e)}")
        task_service.fail_task(task_id, str(e))


@tasks_bp.route("/search/start", methods=["POST"])
@token_required
@validate_request_fields(["date", "start_time", "end_time"])
def start_search_task(current_user):
    """Start a new background search task

    Returns immediately with a task_id that can be used to poll for progress.
    current_user is a string (user_id) from the token_required decorator.
    """
    try:
        data = request.get_json()

        # Validate date format
        try:
            datetime.strptime(data["date"], "%d/%m/%Y")
        except ValueError:
            return jsonify({"error": "Date must be in DD/MM/YYYY format"}), 400

        # Validate time format
        try:
            datetime.strptime(data["start_time"], "%H:%M")
            datetime.strptime(data["end_time"], "%H:%M")
        except ValueError:
            return jsonify({"error": "Times must be in HH:MM format"}), 400

        # Get location_ids, default to all locations if not specified
        location_ids = data.get("location_ids")
        if location_ids is None or (
            isinstance(location_ids, list) and len(location_ids) == 0
        ):
            location_ids = [loc.id for loc in location_service.get_all_locations()]

        # Prepare search parameters
        search_params = {
            "date": data["date"],
            "start_time": data["start_time"],
            "end_time": data["end_time"],
            "duration_minutes": data.get("duration_minutes", 90),
            "court_type": data.get("court_type", "all"),
            "court_config": data.get("court_config", "all"),
            "location_ids": location_ids,
            "force_live_search": data.get("force_live_search", False),
            "sport": data.get("sport", "PADEL"),
        }

        # Create the task - current_user is a string (user_id) from token_required
        task = task_service.create_task(current_user, search_params)

        # Start the search in a background thread
        thread = threading.Thread(
            target=run_search_task, args=(task.task_id, search_params)
        )
        thread.daemon = True
        thread.start()

        return (
            jsonify(
                {
                    "task_id": task.task_id,
                    "status": task.status,
                    "message": "Search task started",
                }
            ),
            202,
        )

    except Exception as e:
        logger.error(f"[TASK] Failed to start task: {str(e)}")
        return jsonify({"error": str(e)}), 400


@tasks_bp.route("/search/<task_id>", methods=["GET"])
@token_required
def get_search_task_status(current_user, task_id):
    """Get the status and progress of a search task
    current_user is a string (user_id) from the token_required decorator
    """
    task = task_service.get_task_for_user(task_id, current_user)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task_service.to_dict(task)), 200


@tasks_bp.route("/search/<task_id>/cancel", methods=["POST"])
@token_required
def cancel_search_task(current_user, task_id):
    """Cancel a running search task
    current_user is a string (user_id) from the token_required decorator
    """
    task = task_service.get_task_for_user(task_id, current_user)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task.status not in ("pending", "running"):
        return jsonify({"error": "Task cannot be cancelled"}), 400

    task_service.cancel_task(task_id)
    return jsonify({"message": "Task cancelled", "task_id": task_id}), 200
