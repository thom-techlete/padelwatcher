"""
Scheduler implementation for the search order workflow.

This module provides a ready-to-use scheduler that:
1. Runs the search job every 15 minutes
2. Processes all active search orders
3. Logs results and errors
4. Can be integrated into a FastAPI or other web service

Install: pip install apscheduler
"""

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from courtfinder.padelmate import PadelMateService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchOrderScheduler:
    """Manages scheduled search jobs for finding available courts"""

    def __init__(self, search_interval_minutes=15):
        """
        Initialize the scheduler.

        Args:
            search_interval_minutes: How often to search (default: 15 minutes)
        """
        self.scheduler = BackgroundScheduler()
        self.search_interval_minutes = search_interval_minutes
        self.service = PadelMateService()
        self.is_running = False

    def search_job(self):
        """
        Main search job that processes all active search orders.
        This runs every 15 minutes.
        """
        start_time = datetime.now()
        logger.info(f"Starting search job at {start_time}")

        try:
            # Get all active search orders
            active_orders = self.service.service.get_active_search_orders()
            logger.info(f"Found {len(active_orders)} active search orders")

            total_candidates = 0
            total_fetched = 0

            for order in active_orders:
                try:
                    # Execute search and fetch workflow
                    result = self.service.fetch_and_search_availability(order.id)

                    total_fetched += result["fetched_slots"]
                    total_candidates += len(result["notification_candidates"])

                    # Log results
                    if result["notification_candidates"]:
                        logger.info(
                            f"[Order {order.id}] Found {len(result['notification_candidates'])} "
                            f"new courts matching criteria"
                        )

                        # Log each candidate
                        for candidate in result["notification_candidates"]:
                            logger.info(
                                f"  - {candidate['court_name']} at {candidate['location']} "
                                f"({candidate['start_time']} - {candidate['end_time']}, "
                                f"{candidate['price']})"
                            )
                    else:
                        logger.debug(f"[Order {order.id}] No new courts found")

                    # Check if search should be completed
                    if self._should_complete_search(order):
                        self.service.service.update_search_order_status(
                            order.id, "completed"
                        )
                        logger.info(
                            f"[Order {order.id}] Search completed (date passed)"
                        )

                except Exception as e:
                    logger.error(
                        f"Error processing search order {order.id}: {e}", exc_info=True
                    )

            # Log summary
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Search job completed in {duration:.2f}s - "
                f"Fetched {total_fetched} slots, "
                f"Found {total_candidates} notification candidates"
            )

        except Exception as e:
            logger.error(f"Critical error in search job: {e}", exc_info=True)

    def _should_complete_search(self, search_order):
        """Check if a search order should be marked as completed"""
        from datetime import date

        return date.today() > search_order.date

    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        # Add the search job
        self.scheduler.add_job(
            self.search_job,
            trigger=IntervalTrigger(minutes=self.search_interval_minutes),
            id="search_order_job",
            name="Search Order Processing Job",
            replace_existing=True,
        )

        # Start the scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info(
            f"Scheduler started - Running search job every {self.search_interval_minutes} minutes"
        )

    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")

    def get_status(self):
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "search_interval_minutes": self.search_interval_minutes,
            "next_run_time": (
                str(self.scheduler.get_job("search_order_job").next_run_time)
                if self.scheduler.get_job("search_order_job")
                else None
            ),
        }


# Global scheduler instance
_scheduler_instance = None


def get_scheduler(search_interval_minutes=15):
    """Get or create the global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = SearchOrderScheduler(search_interval_minutes)
    return _scheduler_instance


# FastAPI integration example
"""
from fastapi import FastAPI
from search_scheduler import get_scheduler

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    scheduler = get_scheduler(search_interval_minutes=15)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler = get_scheduler()
    scheduler.stop()

@app.get("/scheduler/status")
async def scheduler_status():
    scheduler = get_scheduler()
    return scheduler.get_status()

@app.post("/scheduler/force-search")
async def force_search():
    scheduler = get_scheduler()
    scheduler.search_job()
    return {"message": "Search job executed"}
"""


if __name__ == "__main__":
    # Example standalone usage
    scheduler = SearchOrderScheduler(search_interval_minutes=15)

    print("Starting scheduler...")
    scheduler.start()

    try:
        # Keep the scheduler running
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped")
