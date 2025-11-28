from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker

from app.config import SQLALCHEMY_DATABASE_URI
from app.models import (
    Availability,
    Court,
    Location,
    SearchOrder,
    SearchOrderNotification,
)

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


class SearchOrderService:
    """Service for managing search order database operations.

    Returns SearchOrder database objects. Serialization to JSON/DTOs
    should be handled by the API routes.
    """

    def __init__(self):
        self.session = Session()

    def create_search_order(
        self,
        date: date,
        start_time_range: time,
        end_time_range: time,
        duration: int,
        user_id: str | None = None,
        location_ids: list[int] | None = None,
        court_type: str = "all",
        court_config: str = "all",
        indoor: bool | None = None,
    ) -> SearchOrder:
        """Create a new search order for a user to search for available courts within a time range.

        Args:
            date: Date to search for
            start_time_range: Start of time range to search
            end_time_range: End of time range to search
            duration: Duration in minutes of desired slot
            user_id: User ID creating the search order
            location_ids: List of location IDs to search
            court_type: Court type filter ('all', 'indoor', 'outdoor')
            court_config: Court configuration filter ('all', 'single', 'double')
            indoor: Deprecated parameter (use court_type instead)

        Returns:
            SearchOrder: The created SearchOrder database object
        """
        search_order = SearchOrder(
            user_id=user_id,
            location_ids=location_ids or [],
            date=date,
            start_time=start_time_range,
            end_time=end_time_range,
            duration_minutes=duration,
            court_type=court_type,
            court_config=court_config,
            is_active=True,
        )
        self.session.add(search_order)
        self.session.commit()
        return search_order

    def get_search_order(self, search_order_id: int) -> SearchOrder | None:
        """Get a specific search order by ID.

        Args:
            search_order_id: The numeric search order ID

        Returns:
            SearchOrder | None: SearchOrder database object or None if not found
        """
        return (
            self.session.query(SearchOrder)
            .filter(SearchOrder.id == search_order_id)
            .first()
        )

    def get_search_orders_by_user(self, user_id: str) -> list[SearchOrder]:
        """Get all search orders for a specific user.

        Args:
            user_id: The user ID to get search orders for

        Returns:
            list[SearchOrder]: List of SearchOrder database objects for the user
        """
        return (
            self.session.query(SearchOrder).filter(SearchOrder.user_id == user_id).all()
        )

    def get_active_search_orders(self) -> list[SearchOrder]:
        """Get all active search orders across all users.

        Returns:
            list[SearchOrder]: List of active SearchOrder database objects
        """
        return self.session.query(SearchOrder).filter(SearchOrder.is_active).all()

    def update_search_order(self, search_order_id: int, **kwargs) -> SearchOrder | None:
        """Update a search order with provided fields.

        Args:
            search_order_id: The numeric search order ID to update
            **kwargs: Field names and values to update

        Returns:
            SearchOrder | None: Updated SearchOrder database object or None if not found
        """
        search_order = self.get_search_order(search_order_id)
        if search_order:
            for key, value in kwargs.items():
                if hasattr(search_order, key):
                    setattr(search_order, key, value)
            search_order.updated_at = datetime.now(UTC)
            self.session.commit()
            return search_order
        return None

    def delete_search_order(self, search_order_id: int) -> bool:
        """Delete a search order.

        Args:
            search_order_id: The numeric search order ID to delete

        Returns:
            bool: True if deleted, False if not found
        """
        search_order = self.get_search_order(search_order_id)
        if search_order:
            self.session.delete(search_order)
            self.session.commit()
            return True
        return False

    def match_availabilities_to_search_order(self, search_order_id: int) -> list[dict]:
        """Match current availabilities to a specific search order within a time range.

        Returns list of matching courts where the slot fits within the time range.

        Args:
            search_order_id: The numeric search order ID to match against

        Returns:
            list[dict]: List of matching court dictionaries
        """
        search_order = self.get_search_order(search_order_id)
        if not search_order:
            return []

        # Calculate the end time for the duration
        slot_end_time = (
            datetime.combine(search_order.date, search_order.start_time)
            + timedelta(minutes=search_order.duration_minutes)
        ).time()

        # Find availabilities where:
        # 1. Date matches
        # 2. Available is True
        # 3. Duration matches
        # 4. Start time is within the search range
        # 5. End time fits within the search range (start_time + duration <= end_time_range)
        query = self.session.query(Availability).filter(
            and_(
                Availability.date == search_order.date,
                Availability.available,
                Availability.duration == search_order.duration_minutes,
                Availability.start_time >= search_order.start_time,
                Availability.start_time <= search_order.end_time,
                # Ensure the slot fits: start_time + duration <= end_time_range
                slot_end_time <= search_order.end_time,
            )
        )

        if search_order.court_type == "indoor":
            query = query.join(Court).filter(Court.indoor)
        elif search_order.court_type == "outdoor":
            query = query.join(Court).filter(not Court.indoor)

        if search_order.court_config == "single":
            query = query.join(Court).filter(not Court.double)
        elif search_order.court_config == "double":
            query = query.join(Court).filter(Court.double)

        availabilities = query.all()

        results = []
        for avail in availabilities:
            court = self.session.query(Court).filter(Court.id == avail.court_id).first()
            if court:
                location = (
                    self.session.query(Location)
                    .filter(Location.id == court.location_id)
                    .first()
                )
                results.append(
                    {
                        "court_name": court.name,
                        "location": location.name if location else "Unknown",
                        "start_time": str(avail.start_time),
                        "end_time": str(avail.end_time),
                        "price": avail.price,
                        "indoor": court.indoor,
                    }
                )

        return results

    def get_notification_candidates(self, search_order_id: int) -> list[dict]:
        """Get courts that match a search order within time range and haven't been notified yet.

        Returns list of courts available for notification.

        Args:
            search_order_id: The numeric search order ID

        Returns:
            list[dict]: List of notification candidate dictionaries
        """
        search_order = self.get_search_order(search_order_id)
        if not search_order:
            return []

        # Calculate the end time for the duration
        slot_end_time = (
            datetime.combine(search_order.date, search_order.start_time)
            + timedelta(minutes=search_order.duration_minutes)
        ).time()

        # Get available courts that match the search criteria within time range
        query = (
            self.session.query(Availability, Court, Location)
            .join(Court, Availability.court_id == Court.id)
            .join(Location, Court.location_id == Location.id)
            .filter(
                and_(
                    Availability.date == search_order.date,
                    Availability.available,
                    Availability.duration == search_order.duration_minutes,
                    Availability.start_time >= search_order.start_time,
                    Availability.start_time <= search_order.end_time,
                    # Ensure the slot fits: start_time + duration <= end_time_range
                    slot_end_time <= search_order.end_time,
                )
            )
        )

        if search_order.court_type == "indoor":
            query = query.filter(Court.indoor)
        elif search_order.court_type == "outdoor":
            query = query.filter(not Court.indoor)

        if search_order.court_config == "single":
            query = query.filter(not Court.double)
        elif search_order.court_config == "double":
            query = query.filter(Court.double)

        availabilities = query.all()

        # Filter out already notified
        candidates = []
        for avail, court, location in availabilities:
            existing_notification = (
                self.session.query(SearchOrderNotification)
                .filter(
                    and_(
                        SearchOrderNotification.search_order_id == search_order_id,
                        SearchOrderNotification.availability_id == avail.id,
                    )
                )
                .first()
            )

            if not existing_notification:
                candidates.append(
                    {
                        "availability_id": avail.id,
                        "court_id": court.id,
                        "court_name": court.name,
                        "location": location.name,
                        "start_time": str(avail.start_time),
                        "end_time": str(avail.end_time),
                        "price": avail.price,
                        "indoor": court.indoor,
                    }
                )

        return candidates

    def create_notification_record(
        self, search_order_id: int, court_id: int, availability_id: int
    ) -> SearchOrderNotification:
        """Create a notification record to track that a user has been notified.

        Args:
            search_order_id: The search order ID
            court_id: The court ID
            availability_id: The availability ID

        Returns:
            SearchOrderNotification: The created notification record
        """
        notification = SearchOrderNotification(
            search_order_id=search_order_id,
            court_id=court_id,
            availability_id=availability_id,
            notified=False,  # Will be set to True after actual notification is sent
        )
        self.session.add(notification)
        self.session.commit()
        return notification

    def mark_notification_sent(
        self, notification_id: int
    ) -> SearchOrderNotification | None:
        """Mark a notification as sent.

        Args:
            notification_id: The numeric notification ID to mark as sent

        Returns:
            SearchOrderNotification | None: Updated notification or None if not found
        """
        notification = (
            self.session.query(SearchOrderNotification)
            .filter(SearchOrderNotification.id == notification_id)
            .first()
        )
        if notification:
            notification.notified = True
            notification.notified_at = datetime.now(UTC)
            self.session.commit()
            return notification
        return None

    def update_search_order_last_check(
        self, search_order_id: int
    ) -> SearchOrder | None:
        """Update the last_check_at timestamp for a search order.

        Args:
            search_order_id: The numeric search order ID to update

        Returns:
            SearchOrder | None: Updated SearchOrder or None if not found
        """
        search_order = self.get_search_order(search_order_id)
        if search_order:
            search_order.last_check_at = datetime.now(UTC)
            self.session.commit()
            return search_order
        return None


search_order_service = SearchOrderService()
