import hashlib
import json
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import SQLALCHEMY_DATABASE_URI
from app.models import SearchRequest

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


class SearchService:
    """Service for managing search request cache and analytics.

    Returns SearchRequest database objects. Serialization to JSON/DTOs
    should be handled by the API routes.
    """

    def __init__(self):
        self.session = Session()

    def create_search_request_record(
        self,
        search_hash: str,
        date: date,
        start_time: time,
        end_time: time,
        duration_minutes: int,
        court_type: str,
        court_config: str,
        location_id: int,
        live_search: bool,
        slots_found: int,
    ) -> SearchRequest:
        """Create a record of a search request, updating existing record if hash already exists.

        Args:
            search_hash: Hash of search parameters
            date: Search date
            start_time: Start time of search range
            end_time: End time of search range
            duration_minutes: Desired duration in minutes
            court_type: Court type filter
            court_config: Court configuration filter
            location_id: Location ID searched
            live_search: Whether this is a live API search
            slots_found: Number of available slots found

        Returns:
            SearchRequest: The created or updated SearchRequest database object
        """
        from sqlalchemy.exc import IntegrityError

        # Check if this search hash already exists
        existing_search = (
            self.session.query(SearchRequest)
            .filter(SearchRequest.search_hash == search_hash)
            .first()
        )

        if existing_search:
            # Update the existing record
            existing_search.performed_at = datetime.now(UTC)
            existing_search.slots_found = slots_found
            existing_search.live_search = live_search
            self.session.commit()
            return existing_search

        # Create new record if it doesn't exist
        search_request = SearchRequest(
            search_hash=search_hash,
            date=date,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            court_type=court_type,
            court_config=court_config,
            location_id=location_id,
            live_search=live_search,
            slots_found=slots_found,
        )

        try:
            self.session.add(search_request)
            self.session.commit()
            return search_request
        except IntegrityError:
            # In case of race condition, fetch and update the existing record
            self.session.rollback()
            existing_search = (
                self.session.query(SearchRequest)
                .filter(SearchRequest.search_hash == search_hash)
                .first()
            )
            if existing_search:
                existing_search.performed_at = datetime.now(UTC)
                existing_search.slots_found = slots_found
                existing_search.live_search = live_search
                self.session.commit()
                return existing_search
            raise

    def get_recent_live_search(
        self, search_hash: str, max_age_minutes: int = 15
    ) -> SearchRequest | None:
        """Check if there's a recent live search with the same parameters.

        Args:
            search_hash: Hash of search parameters
            max_age_minutes: Maximum age of search to return (default 15 minutes)

        Returns:
            SearchRequest | None: Recent search record or None if not found
        """
        cutoff_time = datetime.now(UTC) - timedelta(minutes=max_age_minutes)

        recent_search = (
            self.session.query(SearchRequest)
            .filter(
                SearchRequest.search_hash == search_hash,
                SearchRequest.live_search,
                SearchRequest.performed_at >= cutoff_time,
            )
            .order_by(SearchRequest.performed_at.desc())
            .first()
        )

        return recent_search

    def generate_search_hash(
        self,
        date: date,
        location_id: int,
    ) -> str:
        """Generate a hash for search parameters to identify identical searches.

        Args:
            date: Search date
            start_time: Start time
            end_time: End time
            duration_minutes: Duration in minutes
            court_type: Court type filter
            court_config: Court configuration filter
            location_ids: List of location IDs

        Returns:
            str: MD5 hash of search parameters
        """

        # Only cache based on date and locations since live API search is the same regardless of duration, time, or court type
        search_data = {"date": str(date), "location_id": location_id}

        search_string = json.dumps(search_data, sort_keys=True)
        return hashlib.md5(search_string.encode()).hexdigest()

    def clear_search_cache(self, older_than_minutes: int | None = None) -> int:
        """Clear search request cache.

        If older_than_minutes is specified, only clear records older than that.

        Args:
            older_than_minutes: Only delete records older than this many minutes (optional)

        Returns:
            int: Number of records deleted
        """
        if older_than_minutes is not None:
            cutoff_time = datetime.now(UTC) - timedelta(minutes=older_than_minutes)
            deleted_count = (
                self.session.query(SearchRequest)
                .filter(SearchRequest.performed_at < cutoff_time)
                .delete()
            )
        else:
            # Clear all search requests
            deleted_count = self.session.query(SearchRequest).delete()

        self.session.commit()
        return deleted_count


search_service = SearchService()
