"""
Base provider class for court booking platforms.

This module defines the abstract base class that all provider implementations
must inherit from. It ensures consistency across different providers while
allowing provider-specific customizations.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from app.models import Availability
from app.services.availability_service import availability_service
from app.services.location_service import location_service


class BaseCourtProvider(ABC):
    """
    Abstract base class for court booking platform providers.

    All provider implementations (Playtomic, Padelmate, etc.) should inherit
    from this class and implement the required abstract methods.

    Common functionality is implemented here, while provider-specific
    methods should be implemented in the concrete classes.
    """

    def __init__(self):
        """Initialize the provider with a service instance."""
        self.provider = "not_set"

    # ===== ABSTRACT METHODS (Must be implemented by all providers) =====

    @abstractmethod
    def fetch_availability(
        self, tenant_id: str, date_str: str, sport_id: str = "PADEL"
    ) -> list[Availability]:
        """
        Fetch availability data from the provider's API.

        Args:
            tenant_id: The provider-specific identifier for the location/club
            date_str: Date in YYYY-MM-DD format
            sport_id: Sport type (default: "PADEL")

        Returns:
            Raw API response data (format varies by provider)

        Raises:
            NotImplementedError: If the provider doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement fetch_availability()"
        )

    @abstractmethod
    def fetch_club_info(self, club_slug: str) -> dict | None:
        """
        Fetch club/location information from the provider.

        Args:
            club_slug: Provider-specific club identifier/slug
            date_str: Date in YYYY-MM-DD format

        Returns:
            Dictionary containing club information, or None if not found

        Raises:
            NotImplementedError: If the provider doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement fetch_club_info()"
        )

    @abstractmethod
    def add_location_by_slug(self, slug: str, provider_name: str | None = None):
        """
        Add a new location to the database by fetching info using the slug.

        Args:
            slug: Provider-specific location/club identifier
            date_str: Date for fetching info (default: today or provider default)
            provider_name: Name of the provider (default: class name)

        Returns:
            Location object from the database

        Raises:
            NotImplementedError: If the provider doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement add_location_by_slug()"
        )

    @abstractmethod
    def generate_booking_url(
        self,
        tenant_id: str | None,
        resource_id: str | None,
        availability_date: str,
        availability_start_time: str,
        duration_minutes: int,
    ) -> str | None:
        """
        Generate a provider-specific booking URL for an availability slot.

        This method must be implemented by each provider as the URL format
        and structure is specific to the booking platform.

        Args:
            tenant_id: Tenant/location ID from the provider
            resource_id: Resource/court ID from the provider
            availability_date: Date in YYYY-MM-DD format
            availability_start_time: Start time in HH:MM format
            duration_minutes: Duration of the slot in minutes

        Returns:
            Booking URL string or None if URL cannot be generated

        Raises:
            NotImplementedError: If the provider doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement generate_booking_url()"
        )

    # ===== COMMON METHODS (Implemented for all providers) =====

    def fetch_and_store_availability(
        self, location_id: int, date_str: str | None = None, sport_id: str = "PADEL"
    ) -> int:
        """
        Fetch, parse, and store availability data using location ID from DB.

        Args:
            location_id: Database ID of the location
            date_str: Date in YYYY-MM-DD format (default: today)
            sport_id: Sport type (default: "PADEL")

        Returns:
            Number of availability slots stored

        Raises:
            ValueError: If location not found in database
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        location_obj = location_service.get_location_by_id(location_id)

        if not location_obj:
            raise ValueError(f"Location with ID {location_id} not found")

        tenant_id = location_obj.tenant_id

        # Fetch data
        availabilites = self.fetch_availability(tenant_id, date_str, sport_id)

        stats = availability_service.bulk_add_availabilities(availabilites)

        return stats

    def fetch_and_store_all_availability(
        self, date_str: str | None = None, sport_id: str = "PADEL"
    ) -> int:
        """
        Fetch and store availability for all locations in the DB.

        Args:
            date_str: Date in YYYY-MM-DD format (default: today)
            sport_id: Sport type (default: "PADEL")

        Returns:
            Total number of availability slots stored across all locations
        """
        locations = self.service.get_all_locations()
        total_slots = 0
        for loc in locations:
            try:
                slots = self.fetch_and_store_availability(loc.id, date_str, sport_id)
                total_slots += slots
                print(f"Fetched {slots} slots for {loc.name}")
            except Exception as e:
                print(f"Error fetching availability for {loc.name}: {e}")
        return total_slots

    def get_available_courts(self, date_obj, start_time, end_time):
        """
        Get available courts in a time range.

        Args:
            date_obj: Date object
            start_time: Start time object
            end_time: End time object

        Returns:
            List of available courts matching the criteria
        """
        return self.service.get_available_courts_in_time_range(
            date_obj, start_time, end_time
        )

    def get_available_indoor_courts(self, date_obj, start_time, end_time):
        """
        Get available indoor courts in a time range.

        Args:
            date_obj: Date object
            start_time: Start time object
            end_time: End time object

        Returns:
            List of available indoor courts
        """
        from sqlalchemy import and_

        from app.models import Availability, Court

        availabilities = (
            self.service.session.query(Availability)
            .filter(
                and_(
                    Availability.date == date_obj,
                    Availability.available,
                    Availability.start_time >= start_time,
                    Availability.end_time <= end_time,
                )
            )
            .all()
        )

        results = []
        for avail in availabilities:
            court = (
                self.service.session.query(Court)
                .filter(Court.id == avail.court_id)
                .first()
            )
            if court and court.indoor:
                location_name = court.location.name if court.location else "Unknown"
                results.append(
                    {
                        "court_name": court.name,
                        "location": location_name,
                        "start_time": str(avail.start_time),
                        "end_time": str(avail.end_time),
                        "price": avail.price,
                    }
                )
        return results

    def search_available_courts(
        self,
        date_str: str,
        start_time_range_str: str,
        end_time_range_str: str,
        duration: int,
        indoor: bool | None = None,
    ):
        """
        Search for available courts within a time range for a specific duration.

        Args:
            date_str: Date in YYYY-MM-DD format
            start_time_range_str: Start time in HH:MM format
            end_time_range_str: End time in HH:MM format
            duration: Duration in minutes
            indoor: Optional filter for indoor (True) or outdoor (False) courts

        Returns:
            List of available courts matching the criteria
        """
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time_range = datetime.strptime(start_time_range_str, "%H:%M").time()
        end_time_range = datetime.strptime(end_time_range_str, "%H:%M").time()
        return self.service.get_available_courts_in_time_range(
            date_obj, start_time_range, end_time_range, duration, indoor
        )

    def create_search_order(
        self,
        date_str: str,
        start_time_range_str: str,
        end_time_range_str: str,
        duration: int,
        indoor: bool | None = None,
        user_id: str | None = None,
    ):
        """
        Create a search order for a user within a time range.

        Args:
            date_str: Date in YYYY-MM-DD format
            start_time_range_str: Start time in HH:MM format
            end_time_range_str: End time in HH:MM format
            duration: Duration in minutes
            indoor: Optional filter for indoor (True) or outdoor (False) courts
            user_id: Optional user identifier

        Returns:
            Created search order object
        """
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time_range = datetime.strptime(start_time_range_str, "%H:%M").time()
        end_time_range = datetime.strptime(end_time_range_str, "%H:%M").time()
        return self.service.create_search_order(
            date_obj, start_time_range, end_time_range, duration, indoor, user_id
        )

    def fetch_and_search_availability(self, search_order_id: int) -> dict:
        """
        Main orchestration function for searching availability.

        This function:
        1. Fetches latest availability from provider API for all locations
        2. Saves fetched availabilities to DB
        3. Matches against the search order criteria
        4. Returns notification candidates (courts that match and haven't been notified)

        Args:
            search_order_id: ID of the search order to process

        Returns:
            Dictionary containing:
            - search_order_id: ID of the processed search order
            - total_matched_courts: Total number of courts matching criteria
            - notification_candidates: List of new courts to notify about
            - fetched_slots: Total number of availability slots fetched

        Raises:
            ValueError: If search order not found
        """
        search_order = self.service.get_search_order(search_order_id)
        if not search_order:
            raise ValueError(f"Search order {search_order_id} not found")

        # Convert date to string format for API
        date_str = search_order.date.strftime("%Y-%m-%d")

        # Fetch and store availability for all locations
        print(f"[Search Order {search_order_id}] Fetching availability for {date_str}")
        total_slots = self.fetch_and_store_all_availability(date_str=date_str)
        print(
            f"[Search Order {search_order_id}] Fetched and stored {total_slots} slots"
        )

        # Get matching courts
        matching_courts = self.service.match_availabilities_to_search_order(
            search_order_id
        )
        print(
            f"[Search Order {search_order_id}] Found {len(matching_courts)} matching courts"
        )

        # Get notification candidates (not yet notified)
        notification_candidates = self.service.get_notification_candidates(
            search_order_id
        )
        print(
            f"[Search Order {search_order_id}] Found {len(notification_candidates)} new notification candidates"
        )

        # Create notification records for candidates
        for candidate in notification_candidates:
            self.service.create_notification_record(
                search_order_id, candidate["court_id"], candidate["availability_id"]
            )

        return {
            "search_order_id": search_order_id,
            "total_matched_courts": len(matching_courts),
            "notification_candidates": notification_candidates,
            "fetched_slots": total_slots,
        }

    def get_search_order_results(self, search_order_id: int) -> dict | None:
        """
        Get all results for a search order (matched courts and notification status).

        Args:
            search_order_id: ID of the search order

        Returns:
            Dictionary containing search order details and results, or None if not found
        """
        search_order = self.service.get_search_order(search_order_id)
        if not search_order:
            return None

        matching_courts = self.service.match_availabilities_to_search_order(
            search_order_id
        )

        # Get notification records
        from app.models import SearchOrderNotification

        notifications = (
            self.service.session.query(SearchOrderNotification)
            .filter(SearchOrderNotification.search_order_id == search_order_id)
            .all()
        )

        return {
            "search_order_id": search_order_id,
            "date": str(search_order.date),
            "start_time_range": str(search_order.start_time_range),
            "end_time_range": str(search_order.end_time_range),
            "duration": search_order.duration,
            "indoor": search_order.indoor,
            "status": search_order.status,
            "created_at": str(search_order.created_at),
            "total_matched_courts": len(matching_courts),
            "matching_courts": matching_courts,
            "total_notifications": len(notifications),
            "notified": sum(1 for n in notifications if n.notified),
            "pending_notifications": sum(1 for n in notifications if not n.notified),
        }

    def get_all_clubs(self) -> list[dict]:
        """
        Get all clubs/locations from the database.

        Returns:
            List of dictionaries containing location information
        """
        from app.models import Location, Provider

        locations = self.service.session.query(Location).join(Provider).all()
        return [
            {
                "id": loc.id,
                "name": loc.name,
                "tenant_id": loc.tenant_id,
                "slug": loc.slug,
                "address": loc.address,
                "provider": loc.provider.name if loc.provider else "Unknown",
            }
            for loc in locations
        ]

    def get_courts_for_location(self, location_id: int) -> list[dict]:
        """
        Get all courts for a specific location.

        Args:
            location_id: Database ID of the location

        Returns:
            List of dictionaries containing court information
        """
        from app.models import Court

        courts = (
            self.service.session.query(Court)
            .filter(Court.location_id == location_id)
            .all()
        )
        return [
            {
                "name": court.name,
                "sport": court.sport,
                "indoor": court.indoor,
                "double": court.double,
            }
            for court in courts
        ]

    # ===== PROVIDER-SPECIFIC METHODS (Optional implementation) =====

    def find_courts(self, location: str):
        """
        Find courts by location (provider-specific implementation).

        Args:
            location: Location search string

        Raises:
            NotImplementedError: If the provider doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement find_courts(). "
            "This is a provider-specific feature."
        )

    def book_court(self, court_id: int, time_slot: str):
        """
        Book a court (provider-specific implementation).

        Args:
            court_id: ID of the court to book
            time_slot: Time slot to book

        Raises:
            NotImplementedError: If the provider doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement book_court(). "
            "This is a provider-specific feature."
        )
