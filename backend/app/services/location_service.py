from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import SQLALCHEMY_DATABASE_URI
from app.models import Location

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


class LocationService:
    """Service for managing location database operations.

    Returns Location database objects. Serialization to JSON/DTOs
    should be handled by the API routes.
    """

    def __init__(self):
        self.session = Session()

    def get_all_locations(self) -> list[Location]:
        """Get all locations from the database.

        Returns:
            list[Location]: List of Location database objects
        """
        return self.session.query(Location).all()

    def get_location_by_id(self, location_id: int) -> Location | None:
        """Get a single location by its ID.

        Args:
            location_id: The numeric location ID

        Returns:
            Location | None: Location database object or None if not found
        """
        return self.session.query(Location).filter(Location.id == location_id).first()

    def get_location_by_tenant(self, tenant_id: str) -> Location | None:
        """Get a location by tenant_id.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Location | None: Location database object or None if not found
        """
        return (
            self.session.query(Location).filter(Location.tenant_id == tenant_id).first()
        )

    def get_location_by_name_and_provider(
        self, name: str, provider: str
    ) -> Location | None:
        """Get a location by name and provider.

        Args:
            name: Location name
            provider: Provider name

        Returns:
            Location | None: Location database object or None if not found
        """
        return (
            self.session.query(Location)
            .filter(Location.name == name, Location.provider == provider)
            .first()
        )

    def add_or_update_location(self, location: Location) -> Location | None:
        """Add a new location to the database.

        Args:
            location: Location database object to add

        Returns:
            Location | None: The added Location database object or None if failed
        """
        existing_location = self.get_location_by_tenant(location.tenant_id)
        if existing_location:
            # Update existing location
            existing_location.name = location.name
            existing_location.slug = location.slug
            existing_location.address = location.address
            existing_location.opening_hours = location.opening_hours
            existing_location.sport = location.sport
            existing_location.communications_language = location.communications_language
            self.session.commit()
            return existing_location
        else:
            # Add new location
            self.session.add(location)
            self.session.commit()
            return location

    def get_or_create_location(self, name: str, provider: str) -> Location:
        """Get existing location or create a new one.

        Args:
            name: Location name
            provider: Provider name

        Returns:
            Location: Location database object
        """
        location = self.get_location_by_name_and_provider(name, provider)
        if not location:
            location = Location(name=name, provider=provider)
            location = self.add_or_update_location(location)
        return location

    def delete_location(self, location_id: int) -> bool:
        """Delete a location and all its associated data (courts, availabilities, notifications).

        Args:
            location_id: The numeric location ID to delete

        Returns:
            bool: True if location was deleted, False if location not found
        """
        location = (
            self.session.query(Location).filter(Location.id == location_id).first()
        )
        if not location:
            return False

        self.session.delete(location)
        self.session.commit()
        return True


location_service = LocationService()
