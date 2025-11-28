import json
import logging
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup
from pytz import timezone as tz

from app.courtfinder.base_provider import BaseCourtProvider
from app.models import Availability, Court, Location
from app.services.court_service import court_service
from app.services.location_service import location_service

logger = logging.getLogger(__name__)


class PlaytomicProvider(BaseCourtProvider):
    """
    Playtomic court booking platform provider.

    This provider handles fetching availability and location data from
    the Playtomic API (playtomic.com).
    """

    def __init__(self):
        super().__init__()
        self.provider = "playtomic"

    def __call__(self, *args, **kwds):
        return super().__call__(*args, **kwds)

    def fetch_availability(
        self, tenant_id: str, date_str: str, sport="PADEL"
    ) -> list[Availability]:
        """Fetch availability data from Playtomic API"""
        url = f"https://playtomic.com/api/clubs/availability?tenant_id={tenant_id}&date={date_str}&sport_id={sport}"
        response = httpx.get(url)
        response.raise_for_status()

        location_obj = location_service.get_location_by_tenant(tenant_id)
        if not location_obj:
            raise ValueError(f"Location with tenant_id {tenant_id} not found in DB.")
        availabilities = self._parse_availability(response.json(), location_obj.id)

        return availabilities

    def _parse_availability(self, data: dict, location_id: str) -> list[Availability]:
        """Parse raw API data into Availability database objects.

        Creates Availability objects (in memory, not in DB yet).
        These should be saved to database via availability_service.add_availability().

        Args:
            data: Raw API response data
            location_id: Location ID

        Returns:
            list[Availability]: List of Availability database objects ready to be saved
        """
        results: list[Availability] = []

        # Get location to determine timezone
        location_obj = location_service.get_location_by_id(location_id)
        if not location_obj:
            raise ValueError(f"Location with ID {location_id} not found in DB.")

        # Get timezone for this location (default to Europe/Amsterdam if not set)
        location_tz = tz(location_obj.timezone or "Europe/Amsterdam")
        utc_tz = tz("UTC")

        for resource in data:
            court = resource["resource_id"]
            court_obj = court_service.get_court_by_resource_and_location(
                str(court), location_id
            )
            # TODO: if courts doesnt exists refresh location and courts data
            date_str = resource["start_date"]

            for slot in resource["slots"]:
                start_str = slot["start_time"]
                duration = slot["duration"]

                # Parse UTC time from API (times are in UTC)
                # Create a full datetime on the API's date in UTC timezone
                start_utc = datetime.strptime(
                    f"{date_str} {start_str}", "%Y-%m-%d %H:%M:%S"
                )
                start_utc = utc_tz.localize(start_utc)

                # Convert to location timezone
                start_local = start_utc.astimezone(location_tz)
                end_local = start_local + timedelta(minutes=duration)

                # Use the date from the converted local time
                local_date = start_local.date()

                # Create Availability object (exists in memory, not in DB yet)
                availability = Availability(
                    court_id=int(court_obj.id),
                    date=local_date,
                    start_time=start_local.time(),
                    end_time=end_local.time(),
                    duration=duration,
                    price=slot["price"],
                    available=True,
                )
                results.append(availability)

        return results

    def fetch_club_info(self, club_slug):
        """Fetch club information from Playtomic HTML page"""
        url = f"https://playtomic.com/clubs/{club_slug}"
        response = httpx.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        next_data_element = soup.find(id="__NEXT_DATA__")

        if next_data_element:
            return json.loads(next_data_element.string)
        return None

    def _create_or_update_location(self, slug, club_data):
        tenant = club_data.get("props", {}).get("pageProps", {}).get("tenant", {})
        tenant_id = tenant.get("tenant_id")
        tenant_name = tenant.get("tenant_name")

        if not tenant_name:
            raise ValueError(f"No tenant name found for slug: {slug}")

        location = Location(
            name=tenant_name,
            tenant_id=tenant_id,
            slug=slug,
            address=tenant.get("address") or {},
            opening_hours=tenant.get("opening_hours", {}),
            sport=tenant.get("sport_ids", []),
            communications_language=tenant.get("communications_language"),
            provider=self.provider,
        )
        location = location_service.add_or_update_location(location)

        return tenant, location

    def _update_or_create_court(self, court_info, location):
        court = Court(
            name=court_info["name"],
            location_id=location.id,
            resource_id=str(court_info["resourceId"]),
            sport=court_info.get("sport"),
            indoor="indoor" in court_info.get("features", []),
            double="double" in court_info.get("features", []),
        )
        court = court_service.add_or_update_court(court)
        return court

    def add_location_by_slug(self, slug):
        """Add a new location to the DB by fetching info using the slug"""
        # Fetch club data
        club_data = self.fetch_club_info(slug)
        if not club_data:
            raise ValueError(f"Could not fetch data for slug: {slug}")

        tenant, location = self._create_or_update_location(slug, club_data)

        # Now update courts for this location
        courts = tenant.get("resources", [])
        for _idx, court_info in enumerate(courts):
            self._update_or_create_court(court_info, location)

        return location

    def generate_booking_url(
        self,
        tenant_id: str | None,
        resource_id: str | None,
        availability_date: str,
        availability_start_time: str,
        duration_minutes: int,
    ) -> str | None:
        """Generate a Playtomic-specific booking URL for an availability slot.

        Creates a direct link to the Playtomic payment page with pre-filled
        availability details (court, date, time, duration).

        Args:
            tenant_id: Playtomic tenant ID for the location
            resource_id: Playtomic resource ID for the court
            availability_date: Date in YYYY-MM-DD format
            availability_start_time: Start time (HH:MM or HH:MM:SS format)
            duration_minutes: Duration of the slot in minutes

        Returns:
            Booking URL to Playtomic payment page or None if parameters invalid

        Example:
            url = provider.generate_booking_url(
                'fdac3d26-3abd-4dfc-825b-b299a8cdc38e',
                'b1af00be-621f-4c07-9f86-331cd6691edd',
                '2025-11-30',
                '20:00',
                90
            )
            # Returns: https://app.playtomic.com/login?return_url=...\
        """
        if not tenant_id or not resource_id:
            return None

        try:
            from urllib.parse import quote

            # Extract HH:MM from time string (in case it's HH:MM:SS)
            time_parts = str(availability_start_time).split(":")
            time_hm = f"{time_parts[0]}:{time_parts[1]}"

            # Construct ISO 8601 timestamp in UTC with Z suffix
            start_datetime_str = f"{availability_date}T{time_hm}:00.000Z"

            # Encode the start timestamp (this will encode colons as %3A)
            encoded_start = quote(start_datetime_str, safe="")

            # Build the return_url path with encoded start parameter
            return_url_path = f"/payments?type=CUSTOMER_MATCH&tenant_id={tenant_id}&resource_id={resource_id}&start={encoded_start}&duration={duration_minutes}"

            # Encode the entire return_url as a query parameter
            encoded_return_url = quote(return_url_path, safe="")

            # Build the final booking URL
            booking_url = (
                f"https://app.playtomic.com/login?return_url={encoded_return_url}"
            )
            return booking_url
        except Exception as e:
            logger.error(f"Error generating Playtomic booking URL: {str(e)}")
            return None
