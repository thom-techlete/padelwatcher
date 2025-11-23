"""
Scheduler for background tasks in Padel Watcher
"""

import atexit
import json
import logging
from datetime import UTC, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.courtfinder.padelmate import PadelMateService
from app.email_service import email_service
from app.services import AvailabilityService

logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


def execute_search_order_task(order_id):
    """
    Execute a search order and find available courts.
    This runs as a background task triggered by the scheduler.

    Args:
        order_id: ID of the SearchOrder to execute
    """
    from sqlalchemy import and_

    from app.models import Availability, Court, Location, SearchOrder, User

    try:
        logger.info(f"[SCHEDULER] Executing search order {order_id}")

        # Get fresh service instances for this task
        task_service = AvailabilityService()
        task_padel_service = PadelMateService()

        # Get the search order
        order = (
            task_service.session.query(SearchOrder)
            .filter(SearchOrder.id == order_id)
            .first()
        )

        if not order or not order.is_active:
            logger.info(
                f"[SCHEDULER] Search order {order_id} is not active or not found"
            )
            return

        # Parse location IDs
        location_ids = json.loads(order.location_ids)

        # Get location details
        locations = (
            task_service.session.query(Location)
            .filter(Location.id.in_(location_ids))
            .all()
        )

        if not locations:
            logger.warning(
                f"[SCHEDULER] No valid locations found for search order {order_id}"
            )
            return

        all_courts = []

        # Execute live search for each location
        for location in locations:
            logger.info(
                f"[SCHEDULER] Searching location: {location.name} (slug: {location.slug})"
            )

            try:
                # Fetch fresh availability data from the booking platform (FORCE LIVE)
                slots_fetched = task_padel_service.fetch_and_store_availability(
                    location_id=location.id,
                    date_str=order.date.strftime("%Y-%m-%d"),
                    sport_id="PADEL",
                )
                logger.info(
                    f"[SCHEDULER] Fetched {slots_fetched} slots for {location.name}"
                )

                # Query the database for availabilities that match our criteria
                availabilities = (
                    task_service.session.query(Availability)
                    .join(Court)
                    .filter(
                        and_(
                            Availability.date == order.date,
                            Availability.start_time >= order.start_time,
                            Availability.start_time <= order.end_time,
                            Availability.duration == order.duration_minutes,
                            Court.location_id == location.id,
                            Availability.available,
                        )
                    )
                    .all()
                )

                logger.info(
                    f"[SCHEDULER] Found {len(availabilities)} matching availabilities for {location.name}"
                )

                # Filter by court type and config
                for avail in availabilities:
                    court = (
                        task_service.session.query(Court)
                        .filter(Court.id == avail.court_id)
                        .first()
                    )

                    # Check court type filter
                    if order.court_type != "all" and court:
                        if order.court_type == "indoor" and not court.indoor:
                            continue
                        if order.court_type == "outdoor" and court.indoor:
                            continue

                    # Check court config filter
                    if order.court_config != "all" and court:
                        if order.court_config == "single" and court.double:
                            continue
                        if order.court_config == "double" and not court.double:
                            continue

                    all_courts.append(
                        {
                            "location": location.name,
                            "court": court.name if court else avail.court_id,
                            "date": str(avail.date),
                            "timeslot": f"{avail.start_time.strftime('%H:%M')}-{avail.end_time.strftime('%H:%M')}",
                            "price": avail.price,
                            "provider": "PadelMate",
                        }
                    )

            except Exception as e:
                logger.error(
                    f"[SCHEDULER] Error searching location {location.name}: {str(e)}"
                )
                continue

        # Update last_check_at
        order.last_check_at = datetime.now(UTC)
        task_service.session.commit()

        logger.info(
            f"[SCHEDULER] Search order {order_id} completed: {len(all_courts)} courts found"
        )

        # Send email notification if courts were found
        if len(all_courts) > 0:
            logger.info(
                f"🎾 [SCHEDULER] COURTS FOUND for order {order_id}! Sending notification to user {order.user_id}"
            )

            # Get user email
            user = (
                task_service.session.query(User)
                .filter(User.user_id == order.user_id)
                .first()
            )

            if user and user.email:
                # Prepare search parameters for email
                search_params = {
                    "date": str(order.date),
                    "start_time": str(order.start_time),
                    "end_time": str(order.end_time),
                    "duration_minutes": order.duration_minutes,
                    "court_type": order.court_type,
                    "court_config": order.court_config,
                    "locations": [loc.name for loc in locations],
                }

                # Send email notification
                email_sent = email_service.send_court_found_notification(
                    recipient_email=user.email,
                    recipient_name=user.email.split("@")[0],
                    search_order_id=order.id,
                    courts_found=all_courts,
                    search_params=search_params,
                )

                if email_sent:
                    logger.info(
                        f"[SCHEDULER] Email notification sent successfully to {user.email}"
                    )
                else:
                    logger.error(
                        f"[SCHEDULER] Failed to send email notification to {user.email}"
                    )
            else:
                logger.warning(f"[SCHEDULER] No email found for user {order.user_id}")

        task_service.session.close()

    except Exception as e:
        logger.error(f"[SCHEDULER] Error executing search order {order_id}: {str(e)}")


def check_active_search_orders():
    """
    Check all active search orders and execute them.
    This function is called by the scheduler every 15 minutes.
    """
    logger.info("[SCHEDULER] Checking for active search orders...")

    try:
        # Get fresh service instance
        scheduler_service = AvailabilityService()

        # Get all active search orders for today or future dates
        today = datetime.now(UTC).date()
        from app.models import SearchOrder

        active_orders = (
            scheduler_service.session.query(SearchOrder)
            .filter(SearchOrder.is_active, SearchOrder.date >= today)
            .all()
        )

        logger.info(f"[SCHEDULER] Found {len(active_orders)} active search orders")

        for order in active_orders:
            # Execute each order in a separate task
            execute_search_order_task(order.id)

        scheduler_service.session.close()
        logger.info("[SCHEDULER] Search cycle completed")

    except Exception as e:
        logger.error(f"[SCHEDULER] Error in scheduler: {str(e)}")


# Schedule the job to run every 15 minutes
scheduler.add_job(
    func=check_active_search_orders,
    trigger=IntervalTrigger(minutes=15),
    id="search_order_checker",
    name="Check active search orders every 15 minutes",
    replace_existing=True,
)

logger.info("Search order scheduler initialized - running every 15 minutes")
