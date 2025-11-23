from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Provider, Location, Court, Availability, InternalAvailabilityDTO, SearchOrder, SearchOrderNotification, User, SearchRequest
from app.config import SQLALCHEMY_DATABASE_URI
from datetime import datetime, timedelta, timezone

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

class AvailabilityService:
    def __init__(self):
        self.session = Session()

    def get_all_providers(self):
        return self.session.query(Provider).all()

    def get_provider_by_name(self, name):
        return self.session.query(Provider).filter(Provider.name == name).first()

    def add_provider(self, provider):
        self.session.add(provider)
        self.session.commit()
        return provider

    def get_or_create_provider(self, name):
        provider = self.get_provider_by_name(name)
        if not provider:
            provider = Provider(name=name)
            self.add_provider(provider)
        return provider

    def get_all_locations(self):
        return self.session.query(Location).all()

    def get_location_by_name_and_provider(self, name, provider_id):
        return self.session.query(Location).filter(Location.name == name, Location.provider_id == provider_id).first()

    def add_location(self, location):
        self.session.add(location)
        self.session.commit()
        return location

    def get_or_create_location(self, name, provider_id):
        location = self.get_location_by_name_and_provider(name, provider_id)
        if not location:
            location = Location(name=name, provider_id=provider_id)
            self.add_location(location)
        return location

    def get_all_courts(self):
        return self.session.query(Court).all()

    def get_court_by_name_and_location(self, name, location_id):
        return self.session.query(Court).filter(Court.name == name, Court.location_id == location_id).first()

    def add_court(self, court):
        self.session.add(court)
        self.session.commit()
        return court

    def get_or_create_court(self, name, location_id):
        court = self.get_court_by_name_and_location(name, location_id)
        if not court:
            court = Court(name=name, location_id=location_id)
            self.add_court(court)
        return court

    def get_all_availabilities(self):
        return self.session.query(Availability).all()

    def add_availability(self, availability):
        self.session.add(availability)
        self.session.commit()
        return availability

    def store_internal_availabilities(self, internal_list):
        # NOTE: Courts should be created by add_location_by_slug() with proper properties
        # This method stores availability, potentially creating temporary UUID-named courts
        # that will be updated and merged by add_location_by_slug() later
        
        for item in internal_list:
            # Get location
            location = self.session.query(Location).filter(Location.name == item.location).first()
            if not location:
                continue
            
            # Try to find court by resource_id (UUID)
            court = self.session.query(Court).filter(
                Court.location_id == location.id,
                Court.name == item.court  # Try matching by UUID
            ).first()
            
            if not court:
                # UUID-named court not found
                # Create one temporarily with UUID name - add_location_by_slug() will update it later with proper name
                court = Court(
                    name=item.court,  # Use resource_id (UUID) as name
                    location_id=location.id
                    # Properties (indoor, double) default to False/NULL - will be set by add_location_by_slug()
                )
                self.session.add(court)
                self.session.flush()  # Flush to get the ID
            
            # Parse timeslot
            start_str, end_str = item.timeslot.split('-')
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
            duration = (datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), start_time)).seconds // 60
            date_obj = datetime.strptime(item.date, '%Y-%m-%d').date()
            
            # Check if this exact availability already exists (court_id, date, start_time, end_time)
            existing_avail = self.session.query(Availability).filter(
                Availability.court_id == court.id,
                Availability.date == date_obj,
                Availability.start_time == start_time,
                Availability.end_time == end_time
            ).first()
            
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
                    available=item.available
                )
                self.session.add(avail)
        
        self.session.commit()

    def get_available_courts_in_time_range(self, date, start_time_range, end_time_range, duration, indoor=None):
        from sqlalchemy import and_
        
        # Find availabilities where:
        # 1. Date matches
        # 2. Available is True
        # 3. Duration matches
        # 4. Start time is within the search range
        # 5. End time fits within the search range (start_time + duration <= end_time_range)
        query = self.session.query(Availability).filter(
            and_(
                Availability.date == date,
                Availability.available == True,
                Availability.duration == duration,
                Availability.start_time >= start_time_range,
                Availability.start_time <= end_time_range
            )
        )
        
        if indoor is not None:
            query = query.join(Court).filter(Court.indoor == indoor)
        
        availabilities = query.all()
        
        results = []
        for avail in availabilities:
            # Check if this slot fits within the time range
            slot_end_time = (datetime.combine(date, avail.start_time) + timedelta(minutes=duration)).time()
            if slot_end_time <= end_time_range:
                court = self.session.query(Court).filter(Court.id == avail.court_id).first()
                if court:
                    location = self.session.query(Location).filter(Location.id == court.location_id).first()
                    results.append({
                        'court_name': court.name,
                        'location': location.name if location else 'Unknown',
                        'start_time': str(avail.start_time),
                        'end_time': str(avail.end_time),
                        'price': avail.price,
                        'indoor': court.indoor
                    })
        
        return results

    def get_available_courts(self, date, start_time, duration, indoor=None):
        from sqlalchemy import and_
        from datetime import timedelta
        
        end_time = (datetime.combine(date, start_time) + timedelta(minutes=duration)).time()
        
        query = self.session.query(Availability).filter(
            and_(
                Availability.date == date,
                Availability.start_time == start_time,
                Availability.end_time == end_time,
                Availability.available == True
            )
        )
        
        if indoor is not None:
            query = query.join(Court).filter(Court.indoor == indoor)
        
        availabilities = query.all()
        
        results = []
        for avail in availabilities:
            court = self.session.query(Court).filter(Court.id == avail.court_id).first()
            if court:
                location = self.session.query(Location).filter(Location.id == court.location_id).first()
                results.append({
                    'court_name': court.name,
                    'location': location.name if location else 'Unknown',
                    'start_time': str(avail.start_time),
                    'end_time': str(avail.end_time),
                    'price': avail.price,
                    'indoor': court.indoor
                })
        
        return results

    # Search Order Methods
    def create_search_order(self, date, start_time_range, end_time_range, duration, indoor=None, user_id=None):
        """Create a new search order for a user to search for available courts within a time range"""
        search_order = SearchOrder(
            date=date,
            start_time_range=start_time_range,
            end_time_range=end_time_range,
            duration=duration,
            indoor=indoor,
            user_id=user_id,
            status='active'
        )
        self.session.add(search_order)
        self.session.commit()
        return search_order

    def get_active_search_orders(self):
        """Get all active search orders"""
        return self.session.query(SearchOrder).filter(SearchOrder.status == 'active').all()

    def get_search_order(self, search_order_id):
        """Get a specific search order by ID"""
        return self.session.query(SearchOrder).filter(SearchOrder.id == search_order_id).first()

    def update_search_order_status(self, search_order_id, status):
        """Update search order status (active, completed, cancelled)"""
        search_order = self.get_search_order(search_order_id)
        if search_order:
            search_order.status = status
            self.session.commit()
            return search_order
        return None

    def match_availabilities_to_search_order(self, search_order_id):
        """
        Match current availabilities to a specific search order within a time range.
        Returns list of matching courts where the slot fits within the time range.
        """
        search_order = self.get_search_order(search_order_id)
        if not search_order:
            return []
        
        from sqlalchemy import and_
        
        # Calculate the end time for the duration
        slot_end_time = (datetime.combine(search_order.date, search_order.start_time_range) + 
                        timedelta(minutes=search_order.duration)).time()
        
        # Find availabilities where:
        # 1. Date matches
        # 2. Available is True
        # 3. Duration matches
        # 4. Start time is within the search range
        # 5. End time fits within the search range (start_time + duration <= end_time_range)
        query = self.session.query(Availability).filter(
            and_(
                Availability.date == search_order.date,
                Availability.available == True,
                Availability.duration == search_order.duration,
                Availability.start_time >= search_order.start_time_range,
                Availability.start_time <= search_order.end_time_range,
                # Ensure the slot fits: start_time + duration <= end_time_range
                slot_end_time <= search_order.end_time_range
            )
        )
        
        if search_order.indoor is not None:
            query = query.join(Court).filter(Court.indoor == search_order.indoor)
        
        availabilities = query.all()
        
        results = []
        for avail in availabilities:
            court = self.session.query(Court).filter(Court.id == avail.court_id).first()
            if court:
                location = self.session.query(Location).filter(Location.id == court.location_id).first()
                results.append({
                    'court_name': court.name,
                    'location': location.name if location else 'Unknown',
                    'start_time': str(avail.start_time),
                    'end_time': str(avail.end_time),
                    'price': avail.price,
                    'indoor': court.indoor
                })
        
        return results

    def get_notification_candidates(self, search_order_id):
        """
        Get courts that match a search order within time range and haven't been notified yet.
        Returns list of (availability, court, location) tuples.
        """
        search_order = self.get_search_order(search_order_id)
        if not search_order:
            return []
        
        from sqlalchemy import and_, not_
        
        # Calculate the end time for the duration
        slot_end_time = (datetime.combine(search_order.date, search_order.start_time_range) + 
                        timedelta(minutes=search_order.duration)).time()
        
        # Get available courts that match the search criteria within time range
        query = self.session.query(Availability, Court, Location).join(
            Court, Availability.court_id == Court.id
        ).join(
            Location, Court.location_id == Location.id
        ).filter(
            and_(
                Availability.date == search_order.date,
                Availability.available == True,
                Availability.duration == search_order.duration,
                Availability.start_time >= search_order.start_time_range,
                Availability.start_time <= search_order.end_time_range,
                # Ensure the slot fits: start_time + duration <= end_time_range
                slot_end_time <= search_order.end_time_range
            )
        )
        
        if search_order.indoor is not None:
            query = query.filter(Court.indoor == search_order.indoor)
        
        availabilities = query.all()
        
        # Filter out already notified
        candidates = []
        for avail, court, location in availabilities:
            existing_notification = self.session.query(SearchOrderNotification).filter(
                and_(
                    SearchOrderNotification.search_order_id == search_order_id,
                    SearchOrderNotification.availability_id == avail.id
                )
            ).first()
            
            if not existing_notification:
                candidates.append({
                    'availability_id': avail.id,
                    'court_id': court.id,
                    'court_name': court.name,
                    'location': location.name,
                    'start_time': str(avail.start_time),
                    'end_time': str(avail.end_time),
                    'price': avail.price,
                    'indoor': court.indoor
                })
        
        return candidates

    def create_notification_record(self, search_order_id, court_id, availability_id):
        """Create a notification record to track that a user has been notified"""
        notification = SearchOrderNotification(
            search_order_id=search_order_id,
            court_id=court_id,
            availability_id=availability_id,
            notified=False  # Will be set to True after actual notification is sent
        )
        self.session.add(notification)
        self.session.commit()
        return notification

    def mark_notification_sent(self, notification_id):
        """Mark a notification as sent"""
        notification = self.session.query(SearchOrderNotification).filter(
            SearchOrderNotification.id == notification_id
        ).first()
        if notification:
            notification.notified = True
            notification.notified_at = datetime.now(timezone.utc)
            self.session.commit()
            return notification
        return None

    def create_search_request_record(self, search_hash, date, start_time, end_time, duration_minutes, court_type, court_config, location_ids, live_search, slots_found):
        """Create a record of a search request, updating existing record if hash already exists"""
        import json
        from sqlalchemy.exc import IntegrityError
        
        search_request = SearchRequest(
            search_hash=search_hash,
            date=date,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            court_type=court_type,
            court_config=court_config,
            location_ids=json.dumps(location_ids),
            live_search=live_search,
            slots_found=slots_found
        )
        
        try:
            self.session.add(search_request)
            self.session.commit()
            return search_request
        except IntegrityError:
            # If unique constraint fails, rollback and update existing record
            self.session.rollback()
            
            # Find existing record and update it
            existing_request = self.session.query(SearchRequest).filter(
                SearchRequest.search_hash == search_hash
            ).first()
            
            if existing_request:
                existing_request.date = date
                existing_request.start_time = start_time
                existing_request.end_time = end_time
                existing_request.duration_minutes = duration_minutes
                existing_request.court_type = court_type
                existing_request.court_config = court_config
                existing_request.location_ids = json.dumps(location_ids)
                existing_request.live_search = live_search
                existing_request.slots_found = slots_found
                existing_request.performed_at = datetime.now(timezone.utc)  # Update timestamp
                self.session.commit()
                return existing_request
            
            # If we can't find the existing record, re-raise the error
            raise

    def get_recent_live_search(self, search_hash, max_age_minutes=15):
        """Check if there's a recent live search with the same parameters"""
        from datetime import timedelta
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
        
        recent_search = self.session.query(SearchRequest).filter(
            SearchRequest.search_hash == search_hash,
            SearchRequest.live_search == True,
            SearchRequest.performed_at >= cutoff_time
        ).order_by(SearchRequest.performed_at.desc()).first()
        
        return recent_search

    def generate_search_hash(self, date, start_time, end_time, duration_minutes, court_type, court_config, location_ids):
        """Generate a hash for search parameters to identify identical searches"""
        import hashlib
        import json
        
        # Sort location_ids to ensure consistent hashing
        sorted_location_ids = sorted(location_ids) if isinstance(location_ids, list) else location_ids
        
        # Only cache based on date and locations since live API search is the same regardless of duration, time, or court type
        search_data = {
            'date': str(date),
            'location_ids': sorted_location_ids
        }
        
        search_string = json.dumps(search_data, sort_keys=True)
        return hashlib.md5(search_string.encode()).hexdigest()

    def clear_search_cache(self, older_than_minutes=None):
        """Clear search request cache. If older_than_minutes is specified, only clear records older than that."""
        if older_than_minutes is not None:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=older_than_minutes)
            deleted_count = self.session.query(SearchRequest).filter(
                SearchRequest.performed_at < cutoff_time
            ).delete()
        else:
            # Clear all search requests
            deleted_count = self.session.query(SearchRequest).delete()
        
        self.session.commit()
        return deleted_count

    # User Management Methods
    def create_user(self, email, password_hash, user_id, is_admin=False):
        """Create a new user account (unapproved by default)"""
        user = User(
            email=email,
            password_hash=password_hash,
            user_id=user_id,
            approved=False,  # New users need approval
            is_admin=is_admin,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_email(self, email):
        """Get user by email"""
        return self.session.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id):
        """Get user by user_id"""
        return self.session.query(User).filter(User.user_id == user_id).first()

    def get_user_by_id_numeric(self, id):
        """Get user by numeric ID"""
        return self.session.query(User).filter(User.id == id).first()

    def approve_user(self, user_id, approved_by_user_id):
        """Approve a user account"""
        user = self.get_user_by_id_numeric(user_id)
        if user:
            user.approved = True
            user.approved_at = datetime.now(timezone.utc)
            user.approved_by = approved_by_user_id
            self.session.commit()
            return user
        return None

    def reject_user(self, user_id):
        """Reject a user account (delete it)"""
        user = self.get_user_by_id_numeric(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def get_pending_users(self):
        """Get all users waiting for approval"""
        return self.session.query(User).filter(User.approved == False).all()

    def get_approved_users(self):
        """Get all approved users"""
        return self.session.query(User).filter(User.approved == True).all()

    def get_all_users(self):
        """Get all users"""
        return self.session.query(User).all()

    def activate_user(self, user_id):
        """Activate a user account"""
        user = self.get_user_by_id_numeric(user_id)
        if user:
            user.active = True
            self.session.commit()
            return user
        return None

    def deactivate_user(self, user_id):
        """Deactivate a user account"""
        user = self.get_user_by_id(user_id)
        if user:
            user.active = False
            self.session.commit()
            return user
        return None

    def delete_location(self, location_id):
        """Delete a location and all its associated data"""
        from app.models import Location, Court, Availability, SearchOrderNotification
        
        location = self.session.query(Location).filter(Location.id == location_id).first()
        if not location:
            return False
        
        # Delete associated data in order
        # Delete search order notifications
        self.session.query(SearchOrderNotification).filter(
            SearchOrderNotification.court_id.in_(
                self.session.query(Court.id).filter(Court.location_id == location_id)
            )
        ).delete(synchronize_session=False)
        
        # Delete availabilities
        self.session.query(Availability).filter(
            Availability.court_id.in_(
                self.session.query(Court.id).filter(Court.location_id == location_id)
            )
        ).delete(synchronize_session=False)
        
        # Delete courts
        self.session.query(Court).filter(Court.location_id == location_id).delete()
        
        # Delete location
        self.session.delete(location)
        self.session.commit()
        return True

    def authenticate_user(self, email, password):
        """Authenticate a user and return user info if approved and active"""
        user = self.get_user_by_email(email)
        if user and user.approved and user.active:
            # Import here to avoid circular imports
            from werkzeug.security import check_password_hash
            if check_password_hash(user.password_hash, password):
                return {
                    'user_id': user.user_id,
                    'email': user.email,
                    'is_admin': user.is_admin
                }
        return None

    def update_user_profile(self, user_id, email=None):
        """Update user profile information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update email if provided and not already taken
        if email and email != user.email:
            existing_user = self.get_user_by_email(email)
            if existing_user:
                raise ValueError("Email already in use")
            user.email = email
        
        self.session.commit()
        return user

    def update_user_password(self, user_id, current_password, new_password):
        """Update user password after verifying current password"""
        from werkzeug.security import check_password_hash, generate_password_hash
        
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            raise ValueError("Current password is incorrect")
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        self.session.commit()
        return user