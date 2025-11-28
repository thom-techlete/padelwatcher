"""Search routes blueprint"""

import logging
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import and_

from app.models import Availability, Court, Location
from app.services.availability_service import availability_service
from app.services.location_service import location_service
from app.services.search_service import search_service
from app.utils import get_provider, token_required, validate_request_fields

search_bp = Blueprint("search", __name__, url_prefix="/api/search")
logger = logging.getLogger(__name__)


def live_fetch_availabilities_locations(
    live_locations,
    search_date,
    start_time,
    end_time,
    duration_minutes,
    court_type,
    court_config,
    sport,
):
    """Fetch and store availabilities for multiple locations"""
    added, updated = 0, 0
    date_str = search_date.strftime("%Y-%m-%d")
    for location_id, search_hash in live_locations.items():
        location = location_service.get_location_by_id(location_id)
        provider = get_provider(location.provider)
        slots_stats = provider.fetch_and_store_availability(
            location_id, date_str, sport
        )
        added += slots_stats["added"]
        updated += slots_stats["updated"]

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
                location_id=location_id,
                live_search=True,
                slots_found=added + updated,
            )
        except Exception as record_error:
            logger.error(f"[SEARCH] Failed to record search request: {record_error}")

    logger.info(
        f"[SEARCH] Added {added} new slots from API and updated {updated} slots"
    )

    return added, updated


def perform_court_search(
    search_date,
    start_time,
    end_time,
    duration_minutes,
    court_type,
    court_config,
    location_ids,
    sport="PADEL",
    force_live=False,
):
    """
    Unified search function used by both normal search and execute search order endpoints.

    Args:
        search_date: date object
        start_time: time object
        end_time: time object
        duration_minutes: int
        court_type: 'all', 'indoor', 'outdoor'
        court_config: 'all', 'single', 'double'
        location_ids: list of location IDs
        force_live: bool - force live search from API

    Returns:
        list of court results with availabilities
    """
    logger.info(
        f"[SEARCH] Searching for courts: date={search_date}, time={start_time}-{end_time}, duration={duration_minutes}min, type={court_type}, config={court_config}"
    )

    live_locations = {}
    for loc_id in location_ids:
        search_hash = search_service.generate_search_hash(
            search_date,
            loc_id,
        )
        recent_live_search = search_service.get_recent_live_search(
            search_hash, max_age_minutes=15
        )

        if not force_live and recent_live_search:
            # If not forcing live search and cache exists, use cached data
            logger.info(f"[SEARCH] Using cached search data for location {loc_id}")
        else:
            live_locations[loc_id] = search_hash
            # Fetch fresh availability data from API
            logger.info(f"[SEARCH] Fetching live availability for location: {loc_id}")

    live_fetch_availabilities_locations(
        live_locations,
        search_date,
        start_time,
        end_time,
        duration_minutes,
        court_type,
        court_config,
        sport,
    )

    # Build availability filters - find availabilities that start within the time window
    filters = [
        Availability.date == search_date,
        Availability.start_time >= start_time,
        Availability.start_time <= end_time,
        Availability.duration == duration_minutes,
        Availability.available,
        Court.location_id.in_(location_ids),
    ]

    # Filter by court type if specified
    if court_type == "indoor":
        filters.append(Court.indoor)
    elif court_type == "outdoor":
        filters.append(not Court.indoor)

    # Filter by court configuration if specified
    if court_config == "single":
        filters.append(not Court.double)
    elif court_config == "double":
        filters.append(Court.double)

    # Query availabilities with joined court and location info, ordered by start time
    query = (
        availability_service.session.query(Availability, Court, Location)
        .join(Court, Availability.court_id == Court.id)
        .join(Location, Court.location_id == Location.id)
        .filter(and_(*filters))
        .order_by(Availability.start_time)
    )

    results_tuples = query.all()
    logger.info(
        f"[SEARCH] Found {len(results_tuples)} availabilities matching criteria"
    )

    # Group by location, then by court, with availabilities ordered by start time
    locations_dict = {}

    for avail, court, location in results_tuples:
        location_id = location.id
        court_id = court.id

        # Initialize location if not exists
        if location_id not in locations_dict:
            locations_dict[location_id] = {
                "location": {
                    "id": location.id,
                    "name": location.name,
                    "slug": location.slug,
                    "address": location.address,
                },
                "courts": {},
                "provider": get_provider(
                    location.provider
                ),  # Get provider instance for this location
            }

        # Get provider from location dict
        provider = locations_dict[location_id]["provider"]

        # Initialize court if not exists
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

        # Add availability to court
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
                ),
            }
        )

    # Convert to final format: list of locations with courts
    results = []
    for _location_id, location_data in sorted(
        locations_dict.items(), key=lambda x: x[1]["location"]["name"]
    ):
        courts_list = []
        for _court_id, court_data in location_data["courts"].items():
            courts_list.append(court_data)

        results.append({"location": location_data["location"], "courts": courts_list})

    logger.info(
        f"[SEARCH] Returning {len(results)} locations with {sum(len(loc['courts']) for loc in results)} courts total"
    )
    return results


@search_bp.route("/available", methods=["POST"])
@token_required
@validate_request_fields(["date", "start_time", "end_time"])
def search_available_courts(current_user):
    """Search for available courts on a specific date within a time range"""
    try:
        data = request.get_json()
        try:
            search_date = datetime.strptime(data["date"], "%d/%m/%Y").date()
        except ValueError:
            return jsonify({"error": "Date must be in DD/MM/YYYY format"}), 400

        # Parse time in HH:MM format (24-hour)
        start_time_str = data["start_time"]
        end_time_str = data["end_time"]
        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Times must be in HH:MM format"}), 400

        duration_minutes = data.get("duration_minutes", 90)
        court_type = data.get("court_type", "all")
        court_config = data.get("court_config", "all")
        force_live_search = data.get("force_live_search", False)
        sport = data.get("sport", "PADEL")

        # Get location_ids, default to all locations if not specified
        location_ids = data.get("location_ids")
        if location_ids is None or (
            isinstance(location_ids, list) and len(location_ids) == 0
        ):
            # Get all locations
            location_ids = [loc.id for loc in location_service.get_all_locations()]

        # Perform the search
        results = perform_court_search(
            search_date=search_date,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            court_type=court_type,
            court_config=court_config,
            location_ids=location_ids,
            sport=sport,
            force_live=force_live_search,
        )

        # Include cache information in response
        response_data = {"locations": results, "cached": False, "cache_timestamp": None}

        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": str(e)}), 400
