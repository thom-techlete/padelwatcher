import httpx
from datetime import datetime, timedelta, date, time
from app.services import AvailabilityService
from app.models import InternalAvailabilityDTO, Court, Location, Availability
from sqlalchemy import and_

class PadelMateService:
    def __init__(self):
        self.service = AvailabilityService()

    def fetch_availability(self, tenant_id, date_str, sport_id):
        """Fetch availability data from Playtomic API"""
        url = f"https://playtomic.com/api/clubs/availability?tenant_id={tenant_id}&date={date_str}&sport_id={sport_id}"
        response = httpx.get(url)
        response.raise_for_status()
        return response.json()

    def parse_availability(self, data, provider="Playtomic", location="Unknown"):
        """Parse raw API data into internal format"""
        results = []
        for resource in data:
            court = resource['resource_id']
            date_str = resource['start_date']
            for slot in resource['slots']:
                start_str = slot['start_time']
                duration = slot['duration']
                start = datetime.strptime(start_str, "%H:%M:%S")
                end = start + timedelta(minutes=duration)
                timeslot = f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
                results.append({
                    "provider": provider,
                    "court": court,
                    "location": location,
                    "date": date_str,
                    "timeslot": timeslot,
                    "price": slot['price'],
                    "available": True
                })
        return results

    def fetch_and_store_availability(self, location_id, date_str=None, sport_id="PADEL"):
        """Fetch, parse, and store availability data using location ID from DB"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Get location from DB
        location_obj = self.service.session.query(Location).filter(Location.id == location_id).first()
        if not location_obj:
            raise ValueError(f"Location with ID {location_id} not found")
        
        tenant_id = location_obj.tenant_id
        location_name = location_obj.name
        
        # Get provider name
        from app.models import Provider
        provider_obj = self.service.session.query(Provider).filter(Provider.id == location_obj.provider_id).first()
        provider_name = provider_obj.name if provider_obj else "Unknown"
        
        # Fetch data
        data = self.fetch_availability(tenant_id, date_str, sport_id)
        parsed_data = self.parse_availability(data, provider_name, location_name)
        parsed_dtos = [InternalAvailabilityDTO(**item) for item in parsed_data]
        self.service.store_internal_availabilities(parsed_dtos)
        return len(parsed_dtos)

    def get_available_courts(self, date_obj, start_time, end_time):
        """Get available courts in a time range"""
        return self.service.get_available_courts_in_time_range(date_obj, start_time, end_time)

    def get_available_indoor_courts(self, date_obj, start_time, end_time):
        """Get available indoor courts in a time range"""
        from app.models import Availability, Court
        availabilities = self.service.session.query(Availability).filter(
            and_(
                Availability.date == date_obj,
                Availability.available == True,
                Availability.start_time >= start_time,
                Availability.end_time <= end_time
            )
        ).all()
        
        results = []
        for avail in availabilities:
            court = self.service.session.query(Court).filter(Court.id == avail.court_id).first()
            if court and court.indoor:
                location_name = court.location.name if court.location else 'Unknown'
                results.append({
                    'court_name': court.name,
                    'location': location_name,
                    'start_time': str(avail.start_time),
                    'end_time': str(avail.end_time),
                    'price': avail.price
                })
        return results

    def search_available_courts(self, date_str, start_time_range_str, end_time_range_str, duration, indoor=None):
        """Search for available courts on a specific date within a time range for a specific duration, optionally filtering by indoor/outdoor"""
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time_range = datetime.strptime(start_time_range_str, '%H:%M').time()
        end_time_range = datetime.strptime(end_time_range_str, '%H:%M').time()
        return self.service.get_available_courts_in_time_range(date_obj, start_time_range, end_time_range, duration, indoor)

    def create_search_order(self, date_str, start_time_range_str, end_time_range_str, duration, indoor=None, user_id=None):
        """Create a search order for a user within a time range"""
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time_range = datetime.strptime(start_time_range_str, '%H:%M').time()
        end_time_range = datetime.strptime(end_time_range_str, '%H:%M').time()
        return self.service.create_search_order(date_obj, start_time_range, end_time_range, duration, indoor, user_id)

    def fetch_and_search_availability(self, search_order_id):
        """
        Main orchestration function for searching availability.
        This function:
        1. Fetches latest availability from Playtomic API for all locations
        2. Saves fetched availabilities to DB
        3. Matches against the search order criteria
        4. Returns notification candidates (courts that match and haven't been notified)
        """
        search_order = self.service.get_search_order(search_order_id)
        if not search_order:
            raise ValueError(f"Search order {search_order_id} not found")
        
        # Convert date to string format for API
        date_str = search_order.date.strftime('%Y-%m-%d')
        
        # Fetch and store availability for all locations
        print(f"[Search Order {search_order_id}] Fetching availability for {date_str}")
        total_slots = self.fetch_and_store_all_availability(date_str=date_str)
        print(f"[Search Order {search_order_id}] Fetched and stored {total_slots} slots")
        
        # Get matching courts
        matching_courts = self.service.match_availabilities_to_search_order(search_order_id)
        print(f"[Search Order {search_order_id}] Found {len(matching_courts)} matching courts")
        
        # Get notification candidates (not yet notified)
        notification_candidates = self.service.get_notification_candidates(search_order_id)
        print(f"[Search Order {search_order_id}] Found {len(notification_candidates)} new notification candidates")
        
        # Create notification records for candidates
        for candidate in notification_candidates:
            self.service.create_notification_record(
                search_order_id,
                candidate['court_id'],
                candidate['availability_id']
            )
        
        return {
            'search_order_id': search_order_id,
            'total_matched_courts': len(matching_courts),
            'notification_candidates': notification_candidates,
            'fetched_slots': total_slots
        }

    def get_search_order_results(self, search_order_id):
        """Get all results for a search order (matched courts and notification status)"""
        search_order = self.service.get_search_order(search_order_id)
        if not search_order:
            return None
        
        matching_courts = self.service.match_availabilities_to_search_order(search_order_id)
        
        # Get notification records
        from app.models import SearchOrderNotification
        notifications = self.service.session.query(SearchOrderNotification).filter(
            SearchOrderNotification.search_order_id == search_order_id
        ).all()
        
        return {
            'search_order_id': search_order_id,
            'date': str(search_order.date),
            'start_time_range': str(search_order.start_time_range),
            'end_time_range': str(search_order.end_time_range),
            'duration': search_order.duration,
            'indoor': search_order.indoor,
            'status': search_order.status,
            'created_at': str(search_order.created_at),
            'total_matched_courts': len(matching_courts),
            'matching_courts': matching_courts,
            'total_notifications': len(notifications),
            'notified': sum(1 for n in notifications if n.notified),
            'pending_notifications': sum(1 for n in notifications if not n.notified)
        }

    def find_courts(self, location):
        """Find courts by location (placeholder for future implementation)"""
        # This would integrate with a location search API
        pass

    def book_court(self, court_id, time_slot):
        """Book a court (placeholder for future implementation)"""
        # This would integrate with booking API
        pass
    
    def get_all_clubs(self):
        """Get all clubs/tenants from the database"""
        from app.models import Provider
        locations = self.service.session.query(Location).join(Provider).all()
        return [{
            "id": loc.id,
            "name": loc.name, 
            "tenant_id": loc.tenant_id, 
            "slug": loc.slug, 
            "address": loc.address,
            "provider": loc.provider.name if loc.provider else "Unknown"
        } for loc in locations]
    
    def get_courts_for_location(self, location_id):
        """Get all courts for a specific location"""
        from app.models import Court
        courts = self.service.session.query(Court).filter(Court.location_id == location_id).all()
        return [{"name": court.name, "sport": court.sport, "indoor": court.indoor, "double": court.double} for court in courts]
    
    def fetch_and_store_all_availability(self, date_str=None, sport_id="PADEL"):
        """Fetch and store availability for all locations in the DB"""
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
    
    def fetch_club_info(self, club_slug, date_str):
        """Fetch club information from Playtomic HTML page"""
        url = f"https://playtomic.com/clubs/{club_slug}?date={date_str}"
        response = httpx.get(url)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        import json
        
        soup = BeautifulSoup(response.text, 'html.parser')
        next_data_element = soup.find(id='__NEXT_DATA__')
        
        if next_data_element:
            return json.loads(next_data_element.string)
        return None

    def add_location_by_slug(self, slug, date_str="2025-11-13", provider_name="Playtomic"):
        """Add a new location to the DB by fetching info using the slug"""
        # Fetch club data
        club_data = self.fetch_club_info(slug, date_str)
        if not club_data:
            raise ValueError(f"Could not fetch data for slug: {slug}")
        
        # Extract tenant data
        tenant = club_data.get('props', {}).get('pageProps', {}).get('tenant', {})
        tenant_id = tenant.get('tenant_id')
        tenant_name = tenant.get('tenant_name')
        
        if not tenant_name:
            raise ValueError(f"No tenant name found for slug: {slug}")
        
        # Check if location already exists by tenant_id or slug
        existing_location = None
        if tenant_id:
            existing_location = self.service.session.query(Location).filter(
                Location.tenant_id == tenant_id
            ).first()
        if not existing_location:
            existing_location = self.service.session.query(Location).filter(
                Location.slug == slug
            ).first()
        
        if existing_location:
            # Update existing location
            location = existing_location
        else:
            # Create new location
            provider = self.service.get_or_create_provider(provider_name)
            location = Location(
                name=tenant_name,
                provider_id=provider.id,
                tenant_id=tenant_id,
                slug=slug
            )
            self.service.session.add(location)
        
        # Update all location fields
        import json
        location.name = tenant_name
        location.tenant_id = tenant_id
        location.slug = slug
        location.address = json.dumps(tenant.get('address') or {})
        location.opening_hours = json.dumps(tenant.get('opening_hours', {}))
        location.sport_ids = json.dumps(tenant.get('sport_ids', []))
        location.communications_language = tenant.get('communications_language')
        self.service.session.commit()
        
        # Now update courts for this location
        courts = tenant.get('resources', [])
        for idx, court_info in enumerate(courts):
            court_name = court_info['name']
            resource_id = str(court_info['resourceId'])
            sport = court_info.get('sport')
            features = court_info.get('features', [])
            
            # Parse features - check for both positive and negative cases
            # Default to True if not explicitly stated otherwise
            indoor = 'indoor' in features if any(x in features for x in ['indoor', 'outdoor']) else None
            double = 'double' in features if any(x in features for x in ['double', 'single']) else None
            
            # First, try to find existing court by the actual court name
            court_obj = self.service.session.query(Court).filter(
                Court.location_id == location.id,
                Court.name == court_name
            ).first()
            
            # If not found by name, try to find by resource_id (UUID)
            uuid_court = None
            if not court_obj:
                uuid_court = self.service.session.query(Court).filter(
                    Court.location_id == location.id,
                    Court.name == resource_id
                ).first()
            
            if court_obj:
                # Update existing court with latest features
                court_obj.sport = sport
                court_obj.indoor = indoor
                court_obj.double = double
            elif uuid_court:
                # Rename UUID-named court to proper name and update features
                uuid_court.name = court_name
                uuid_court.sport = sport
                uuid_court.indoor = indoor
                uuid_court.double = double
                court_obj = uuid_court
            else:
                # Create new court
                court_obj = Court(
                    name=court_name,
                    location_id=location.id,
                    sport=sport,
                    indoor=indoor,
                    double=double
                )
                self.service.session.add(court_obj)
            
            self.service.session.commit()
        
        # Clean up any duplicate or UUID-named courts
        # This handles the case where both UUID-named and proper-named courts exist
        from uuid import UUID
        import uuid
        
        # Get all courts for this location
        all_courts = self.service.session.query(Court).filter(Court.location_id == location.id).all()
        
        # Group courts by proper name (from resources)
        court_names_map = {str(c['resourceId']): c['name'] for c in courts}
        
        for court in all_courts:
            try:
                # Check if this is a UUID-named court
                uuid.UUID(court.name)
                # This is a UUID-named court
                proper_name = court_names_map.get(court.name)
                
                if proper_name:
                    # Find if there's already a court with the proper name
                    proper_court = self.service.session.query(Court).filter(
                        Court.location_id == location.id,
                        Court.name == proper_name,
                        Court.id != court.id
                    ).first()
                    
                    if proper_court:
                        # Merge: move availabilities from UUID court to proper court
                        # But first check for duplicates to avoid creating them
                        uuid_court_avails = self.service.session.query(Availability).filter(
                            Availability.court_id == court.id
                        ).all()
                        
                        for avail in uuid_court_avails:
                            # Check if this exact availability already exists on the proper court
                            existing = self.service.session.query(Availability).filter(
                                Availability.court_id == proper_court.id,
                                Availability.date == avail.date,
                                Availability.start_time == avail.start_time,
                                Availability.end_time == avail.end_time
                            ).first()
                            
                            if existing:
                                # Duplicate exists, just delete this one
                                self.service.session.delete(avail)
                            else:
                                # No duplicate, transfer it
                                avail.court_id = proper_court.id
                        
                        # Delete the UUID-named duplicate court
                        self.service.session.delete(court)
                    else:
                        # No proper-named court exists, just rename this one
                        court.name = proper_name
                else:
                    # UUID court with no availability and no matching proper name, safe to delete
                    avail_count = self.service.session.query(Availability).filter(
                        Availability.court_id == court.id
                    ).count()
                    if avail_count == 0:
                        self.service.session.delete(court)
            except (ValueError, TypeError):
                # Not a UUID, keep it as is
                pass
        
        self.service.session.commit()
        
        return location
    
    