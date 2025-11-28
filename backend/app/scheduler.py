"""
Scheduler for background tasks in Padel Watcher
"""

import atexit
import logging
from datetime import UTC, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.email_service import email_service
from app.routes.search import perform_court_search
from app.services.search_order_service import search_order_service
from app.services.user_service import user_service

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
    try:
        logger.info(f"[SCHEDULER] Executing search order {order_id}")

        # Get the search order
        search_order = search_order_service.get_search_order(order_id)

        if not search_order or not search_order.is_active:
            logger.info(
                f"[SCHEDULER] Search order {order_id} is not active or not found"
            )
            return

        # Execute the search using the unified search function (force live data)
        results = perform_court_search(
            search_date=search_order.date,
            start_time=search_order.start_time,
            end_time=search_order.end_time,
            duration_minutes=search_order.duration_minutes,
            court_type=search_order.court_type,
            court_config=search_order.court_config,
            location_ids=search_order.location_ids,
            force_live=True,
        )

        # Update last_check_at
        search_order_service.update_search_order_last_check(order_id)

        logger.info(
            f"[SCHEDULER] Search order {order_id} completed: {len(results)} locations found"
        )

        # Send email notification if courts were found
        if len(results) > 0:
            logger.info(
                f"🎾 [SCHEDULER] COURTS FOUND for order {order_id}! Sending notification to user {search_order.user_id}"
            )

            # Get user email
            order_user = user_service.get_user_by_id(search_order.user_id)

            if order_user and order_user.email:
                # Prepare search parameters for email
                unique_locations = set()
                for result in results:
                    location = result.get("location", {})
                    if location.get("name"):
                        unique_locations.add(location.get("name"))

                search_params = {
                    "date": str(search_order.date),
                    "start_time": str(search_order.start_time),
                    "end_time": str(search_order.end_time),
                    "duration_minutes": search_order.duration_minutes,
                    "court_type": search_order.court_type,
                    "court_config": search_order.court_config,
                    "locations": list(unique_locations),
                }

                # Convert results to courts_found format for email (limit to 5 courts)
                courts_found = []
                for result in results:
                    for court_data in result.get("courts", []):
                        court = court_data.get("court", {})
                        location = result.get("location", {})
                        for avail in court_data.get("availabilities", []):
                            courts_found.append(
                                {
                                    "location": location.get("name", "Unknown"),
                                    "court": court.get("name", "Unknown"),
                                    "date": avail.get("date", ""),
                                    "timeslot": f"{avail.get('start_time', '')}-{avail.get('end_time', '')}",
                                    "price": avail.get("price", "N/A"),
                                    "provider": "PadelMate",
                                }
                            )
                            if len(courts_found) >= 5:
                                break
                        if len(courts_found) >= 5:
                            break
                    if len(courts_found) >= 5:
                        break

                # Add search URL for the button
                search_url = f"{email_service.frontend_base_url}/search-results?date={search_order.date.strftime('%d/%m/%Y')}&start_time={search_order.start_time.strftime('%H:%M')}&end_time={search_order.end_time.strftime('%H:%M')}&duration_minutes={search_order.duration_minutes}&court_type={search_order.court_type}&court_config={search_order.court_config}&location_ids={','.join(map(str, search_order.location_ids))}&live_search=true"
                search_params["search_url"] = search_url

                # Send email notification
                email_sent = email_service.send_court_found_notification(
                    recipient_email=order_user.email,
                    recipient_name=order_user.email.split("@")[0],
                    search_order_id=order_id,
                    courts_found=courts_found,
                    search_params=search_params,
                )

                if email_sent:
                    logger.info(
                        f"[SCHEDULER] Email notification sent successfully to {order_user.email}"
                    )
                else:
                    logger.error(
                        f"[SCHEDULER] Failed to send email notification to {order_user.email}"
                    )
            else:
                logger.warning(
                    f"[SCHEDULER] No email found for user {search_order.user_id}"
                )

    except Exception as e:
        logger.error(f"[SCHEDULER] Error executing search order {order_id}: {str(e)}")


def check_active_search_orders():
    """
    Check all active search orders and execute them.
    This function is called by the scheduler every 15 minutes.
    """
    logger.info("[SCHEDULER] Checking for active search orders...")

    try:
        # Get all active search orders for today or future dates
        today = datetime.now(UTC).date()
        active_orders = search_order_service.get_active_search_orders()

        # Filter for orders on today or future dates
        active_orders = [order for order in active_orders if order.date >= today]

        logger.info(f"[SCHEDULER] Found {len(active_orders)} active search orders")

        for order in active_orders:
            # Execute each order in a separate task
            execute_search_order_task(order.id)

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
