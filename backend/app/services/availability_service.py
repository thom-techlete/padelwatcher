from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker

from app.config import SQLALCHEMY_DATABASE_URI
from app.models import Availability, Court, InternalAvailabilityDTO, Location

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


class AvailabilityService:
    """Service for managing availability database operations.

    Returns Availability database objects. Serialization to JSON/DTOs
    should be handled by the API routes.
    """

    def __init__(self):
        self.session = Session()

    def get_all_availabilities(self) -> list[Availability]:
        """Get all availabilities from the database.

        Returns:
            list[Availability]: List of Availability database objects
        """
        return self.session.query(Availability).all()

    def add_availability(self, availability: Availability) -> Availability:
        """Add a new availability to the database.

        Args:
            availability: Availability database object to add

        Returns:
            Availability: The added Availability database object
        """
        self.session.add(availability)
        self.session.commit()
        return availability

    def bulk_add_availabilities(self, availabilities: list[Availability]) -> dict:
        """Add multiple availabilities to the database in bulk.

        Automatically handles duplicates by updating existing records instead of creating new ones.
        Detects duplicates by: court_id, date, start_time, end_time

        Args:
            availabilities: List of Availability database objects to add

        Returns:
            dict: Statistics with keys:
                - 'added': Number of new availabilities created
                - 'updated': Number of existing availabilities updated
                - 'total': Total availabilities processed
        """
        stats = {"added": 0, "updated": 0, "total": len(availabilities)}

        for availability in availabilities:
            # Check if this availability already exists
            existing = (
                self.session.query(Availability)
                .filter(
                    Availability.court_id == availability.court_id,
                    Availability.date == availability.date,
                    Availability.start_time == availability.start_time,
                    Availability.end_time == availability.end_time,
                )
                .first()
            )

            if existing:
                # Update existing availability
                existing.price = availability.price
                existing.available = availability.available
                existing.duration = availability.duration
                stats["updated"] += 1
            else:
                # Add new availability
                self.session.add(availability)
                stats["added"] += 1

        self.session.commit()
        return stats

    def delete_availability(self, availability_id: int) -> bool:
        """Delete a single availability by ID.

        Args:
            availability_id: The numeric availability ID to delete

        Returns:
            bool: True if deleted, False if not found
        """
        availability = (
            self.session.query(Availability)
            .filter(Availability.id == availability_id)
            .first()
        )
        if not availability:
            return False

        self.session.delete(availability)
        self.session.commit()
        return True

    def delete_all_availabilities(self) -> int:
        """Delete all availabilities from the database.

        Returns:
            int: Number of availabilities deleted
        """
        num_deleted = self.session.query(Availability).delete()
        self.session.commit()
        return num_deleted

    def store_internal_availabilities(
        self, internal_list: list[InternalAvailabilityDTO]
    ) -> None:
        """Store internal availability DTOs to the database.

        Args:
            internal_list: List of InternalAvailabilityDTO objects to store
        """
        # NOTE: Courts should be created by add_location_by_slug() with proper properties
        # This method stores availability, potentially creating temporary UUID-named courts
        # that will be updated and merged by add_location_by_slug() later

        for item in internal_list:
            # Get location
            location = (
                self.session.query(Location)
                .filter(Location.name == item.location)
                .first()
            )
            if not location:
                continue

            # Try to find court by resource_id (UUID)
            court = (
                self.session.query(Court)
                .filter(
                    Court.location_id == location.id,
                    Court.name == item.court,  # Try matching by UUID
                )
                .first()
            )

            if not court:
                # UUID-named court not found
                # Create one temporarily with UUID name - add_location_by_slug() will update it later with proper name
                court = Court(
                    name=item.court,  # Use resource_id (UUID) as name
                    location_id=location.id,
                    # Properties (indoor, double) default to False/NULL - will be set by add_location_by_slug()
                )
                self.session.add(court)
                self.session.flush()  # Flush to get the ID

            # Parse timeslot
            start_str, end_str = item.timeslot.split("-")
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            duration = (
                datetime.combine(datetime.today(), end_time)
                - datetime.combine(datetime.today(), start_time)
            ).seconds // 60
            date_obj = datetime.strptime(item.date, "%Y-%m-%d").date()

            # Check if this exact availability already exists (court_id, date, start_time, end_time)
            existing_avail = (
                self.session.query(Availability)
                .filter(
                    Availability.court_id == court.id,
                    Availability.date == date_obj,
                    Availability.start_time == start_time,
                    Availability.end_time == end_time,
                )
                .first()
            )

            if existing_avail:
                # Update price if it changed
                existing_avail.price = item.price
                existing_avail.available = item.available
            else:
                # Create new availability
                avail = Availability(
                    court_id=court.id,
                    date=date_obj,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    price=item.price,
                    available=item.available,
                )
                self.session.add(avail)

        self.session.commit()

    def get_available_courts_in_time_range(
        self,
        date: date,
        start_time_range: time,
        end_time_range: time,
        duration: int,
        indoor: bool | None = None,
    ) -> list[dict]:
        """Find available courts within a date and time range.

        Args:
            date: The search date
            start_time_range: Start of time range to search
            end_time_range: End of time range to search
            duration: Duration in minutes of desired slot
            indoor: Filter by indoor courts (None = any)

        Returns:
            list[dict]: List of available court dictionaries
        """
        # Find availabilities where:
        # 1. Date matches
        # 2. Available is True
        # 3. Duration matches
        # 4. Start time is within the search range
        # 5. End time fits within the search range (start_time + duration <= end_time_range)
        query = self.session.query(Availability).filter(
            and_(
                Availability.date == date,
                Availability.available,
                Availability.duration == duration,
                Availability.start_time >= start_time_range,
                Availability.start_time <= end_time_range,
            )
        )

        if indoor is not None:
            query = query.join(Court).filter(Court.indoor == indoor)

        availabilities = query.all()

        results = []
        for avail in availabilities:
            # Check if this slot fits within the time range
            slot_end_time = (
                datetime.combine(date, avail.start_time) + timedelta(minutes=duration)
            ).time()
            if slot_end_time <= end_time_range:
                court = (
                    self.session.query(Court).filter(Court.id == avail.court_id).first()
                )
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

    def get_available_courts(
        self,
        date: date,
        start_time: time,
        duration: int,
        indoor: bool | None = None,
    ) -> list[dict]:
        """Find available courts for a specific date, time, and duration.

        Args:
            date: The search date
            start_time: The desired start time
            duration: Duration in minutes of desired slot
            indoor: Filter by indoor courts (None = any)

        Returns:
            list[dict]: List of available court dictionaries
        """
        end_time = (
            datetime.combine(date, start_time) + timedelta(minutes=duration)
        ).time()

        query = self.session.query(Availability).filter(
            and_(
                Availability.date == date,
                Availability.start_time == start_time,
                Availability.end_time == end_time,
                Availability.available,
            )
        )

        if indoor is not None:
            query = query.join(Court).filter(Court.indoor == indoor)

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

    def get_availability_for_location(
        self,
        location_id: int,
        date: date,
    ) -> list[Availability]:
        """Get all availabilities for a specific location and date.

        Args:
            location_id: The numeric location ID
            date: The search date
        """
        pass


availability_service = AvailabilityService()
