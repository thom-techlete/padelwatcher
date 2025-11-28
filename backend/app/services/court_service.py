from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import SQLALCHEMY_DATABASE_URI
from app.models import Court

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


class CourtService:
    """Service for managing court database operations.

    Returns Court database objects. Serialization to JSON/DTOs
    should be handled by the API routes.
    """

    def __init__(self):
        self.session = Session()

    def query(self, **filters) -> list[Court]:
        """General query function to fetch courts with flexible filters.

        Args:
            **filters: Keyword arguments matching Court model columns.
                      Supports both single values and lists for IN queries.
                      Examples:
                        - id=1 (single value)
                        - location_id=[1, 2, 3] (list - IN query)
                        - name="Court A" (single value)
                        - name=["Court A", "Court B"] (list - IN query)
                        - indoor=True (single value)

        Returns:
            list[Court]: List of Court database objects matching all filters
        """
        query_obj = self.session.query(Court)
        for key, value in filters.items():
            if hasattr(Court, key):
                column = getattr(Court, key)
                if isinstance(value, list):
                    query_obj = query_obj.filter(column.in_(value))
                else:
                    query_obj = query_obj.filter(column == value)
        return query_obj.all()

    def get_all_courts(self) -> list[Court]:
        """Get all courts from the database.

        Returns:
            list[Court]: List of Court database objects
        """
        return self.session.query(Court).all()

    def get_court_by_id(self, court_id: int) -> Court | None:
        """Get a single court by its ID.

        Args:
            court_id: The numeric court ID

        Returns:
            Court | None: Court database object or None if not found
        """
        return self.session.query(Court).filter(Court.id == court_id).first()

    def get_courts_by_location(self, location_id: int) -> list[Court]:
        """Get all courts for a specific location.

        Args:
            location_id: The numeric location ID

        Returns:
            list[Court]: List of Court database objects for the location
        """
        return self.session.query(Court).filter(Court.location_id == location_id).all()

    def get_court_by_resource_and_location(
        self, resource_id: str, location_id: str
    ) -> Court | None:
        """Get a court by its resource_id (provider court identifier).

        Args:
            resource_id: The provider's court resource identifier

        Returns:
            Court | None: Court database object or None if not found
        """
        return (
            self.session.query(Court)
            .filter(Court.resource_id == resource_id, Court.location_id == location_id)
            .first()
        )

    def add_court(self, court: Court) -> Court:
        """Add a new court to the database.

        Args:
            court: Court database object to add

        Returns:
            Court: The added Court database object
        """
        self.session.add(court)
        self.session.commit()
        return court

    def add_or_update_court(self, court: Court) -> Court:
        """Add or update a court in the database.

        Args:
            cour: Court database object to add or update

        Returns:
            Court: The added or updated Court database object
        """
        existing_court = self.get_court_by_resource_and_location(
            court.resource_id, court.location_id
        )
        if existing_court:
            # Update existing court fields
            existing_court.name = court.name
            existing_court.sport = court.sport
            existing_court.indoor = court.indoor
            existing_court.double = court.double
            self.session.commit()
            return existing_court
        else:
            # Add new court
            self.session.add(court)
            self.session.commit()
            return court

    def get_or_create_court(
        self,
        name: str,
        resource_id: str,
        location_id: int,
        sport: str | None = None,
        indoor: bool = False,
        double: bool = False,
    ) -> Court:
        """Get existing court or create a new one.

        Args:
            name: Court name
            resource_id: Provider's court resource identifier
            location_id: Location ID this court belongs to
            sport: Sport type (optional)
            indoor: Whether court is indoors (default False)
            double: Whether court is double (default False)

        Returns:
            Court: Existing or newly created Court database object
        """
        court = self.get_court_by_resource_and_location(resource_id, location_id)
        if not court:
            court = Court(
                name=name,
                resource_id=resource_id,
                location_id=location_id,
                sport=sport,
                indoor=indoor,
                double=double,
            )
            self.add_court(court)
        return court

    def delete_court(self, court_id: int) -> bool:
        """Delete a court and all its associated data (availabilities, notifications).

        Args:
            court_id: The numeric court ID to delete

        Returns:
            bool: True if court was deleted, False if court not found
        """
        court = self.session.query(Court).filter(Court.id == court_id).first()
        if not court:
            return False

        # SQLAlchemy will handle cascading deletes due to cascade="all, delete-orphan"
        # relationships defined in models.py
        self.session.delete(court)
        self.session.commit()
        return True


court_service = CourtService()
