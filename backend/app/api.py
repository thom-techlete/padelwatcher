"""
Flask API for Padel Court Availability Search Service
MVP with JWT authentication
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.courtfinder.padelmate import PadelMateService
from app.services import AvailabilityService
from app.config import SECRET_KEY, JWT_EXPIRATION_HOURS, DEBUG, HOST, PORT

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'], supports_credentials=True)

# Configuration
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_EXPIRATION_HOURS'] = JWT_EXPIRATION_HOURS

# Initialize services
padel_service = PadelMateService()
availability_service = AvailabilityService()


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow OPTIONS requests (preflight) to pass through
        if request.method == 'OPTIONS':
            logger.debug("OPTIONS request - allowing through")
            return f(*args, **kwargs)
        
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            logger.debug(f"Authorization header found: {auth_header[:20]}...")
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
                logger.debug(f"Extracted token: {token[:20]}...")
            except IndexError:
                logger.error("Token format invalid - could not split")
                return jsonify({'message': 'Token format invalid'}), 401
        else:
            logger.warning("No Authorization header found in request")
            logger.debug(f"Request headers: {dict(request.headers)}")
        
        if not token:
            logger.error("Token is missing from request")
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            logger.debug(f"Attempting to decode token with secret key")
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user_id']
            logger.info(f"Token decoded successfully for user: {current_user}")
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            logger.error(f"Token is invalid: {str(e)}")
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200


# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user (requires admin approval)"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password required'}), 400
    
    email = data['email']
    
    # Check if user already exists
    existing_user = availability_service.get_user_by_email(email)
    if existing_user:
        return jsonify({'message': 'User already exists'}), 409
    
    # Generate user_id from email
    user_id = f"user_{email.split('@')[0]}"
    
    # Check if user_id is unique
    if availability_service.get_user_by_id(user_id):
        # If not unique, add timestamp
        import time
        user_id = f"user_{email.split('@')[0]}_{int(time.time())}"
    
    # Create user (unapproved by default)
    user = availability_service.create_user(
        email=email,
        password_hash=generate_password_hash(data['password']),
        user_id=user_id
    )
    
    return jsonify({
        'message': 'User registered successfully. Please wait for admin approval.',
        'user_id': user.user_id
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login and get JWT token (only for approved users)"""
    data = request.get_json()
    
    logger.info(f"Login attempt for email: {data.get('email') if data else 'None'}")
    
    if not data or not data.get('email') or not data.get('password'):
        logger.warning("Login failed: Email and password required")
        return jsonify({'message': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    # Authenticate user (checks approval status)
    user_info = availability_service.authenticate_user(email, password)
    
    if not user_info:
        logger.warning(f"Login failed for {email}: Invalid credentials or not approved")
        return jsonify({'message': 'Invalid credentials or account not approved'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user_info['user_id'],
        'email': user_info['email'],
        'is_admin': user_info['is_admin'],
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    logger.info(f"Login successful for {email} (user_id: {user_info['user_id']})")
    logger.debug(f"Generated token: {token[:20]}...")
    
    return jsonify({
        'token': token,
        'user_id': user_info['user_id'],
        'email': user_info['email'],
        'is_admin': user_info['is_admin'],
        'is_approved': True,
        'expires_in': app.config['JWT_EXPIRATION_HOURS'] * 3600
    }), 200


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information"""
    logger.info(f"Getting current user info for: {current_user}")
    user = availability_service.get_user_by_id(current_user)
    if not user:
        logger.error(f"User not found: {current_user}")
        return jsonify({'message': 'User not found'}), 404
    
    logger.debug(f"Returning user info for: {user.email}")
    return jsonify({
        'id': user.id,
        'email': user.email,
        'username': user.user_id,  # Using user_id as username
        'is_admin': user.is_admin,
        'is_approved': user.approved,
        'created_at': str(user.created_at)
    }), 200


@app.route('/api/auth/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile information"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    try:
        user = availability_service.update_user_profile(
            user_id=current_user,
            email=data.get('email')
        )
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.user_id,
                'is_admin': user.is_admin,
                'is_approved': user.approved
            }
        }), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'message': 'Failed to update profile'}), 500


@app.route('/api/auth/password', methods=['PUT'])
@token_required
def update_password(current_user):
    """Update user password"""
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'message': 'Current password and new password are required'}), 400
    
    try:
        user = availability_service.update_user_password(
            user_id=current_user,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({'message': 'Password updated successfully'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Password update error: {str(e)}")
        return jsonify({'message': 'Failed to update password'}), 500


# Location endpoints
@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get all available locations/clubs"""
    locations = padel_service.get_all_clubs()
    return jsonify({'locations': locations}), 200


@app.route('/api/locations', methods=['POST'])
@token_required
def add_location(current_user):
    """Add a new location by slug"""
    data = request.get_json()
    
    if not data or not data.get('slug'):
        return jsonify({'message': 'Slug is required'}), 400
    
    try:
        location = padel_service.add_location_by_slug(
            slug=data['slug'],
            date_str=data.get('date', datetime.now().strftime('%Y-%m-%d'))
        )
        return jsonify({
            'message': 'Location added successfully',
            'location': {
                'id': location.id,
                'name': location.name,
                'slug': location.slug,
                'tenant_id': location.tenant_id
            }
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400


@app.route('/api/locations/<int:location_id>/courts', methods=['GET'])
def get_location_courts(location_id):
    """Get all courts for a specific location"""
    courts = padel_service.get_courts_for_location(location_id)
    return jsonify({'courts': courts}), 200


# Search endpoints
@app.route('/api/search/available', methods=['POST'])
@token_required
def search_available_courts(current_user):
    """Search for available courts on a specific date within a time range"""
    data = request.get_json()
    
    required_fields = ['date', 'start_time', 'end_time']
    if not all(field in data for field in required_fields):
        return jsonify({'message': f'Required fields: {", ".join(required_fields)}'}), 400
    
    try:
        from app.models import Availability, Court, Location
        from sqlalchemy import and_
        from datetime import datetime
        
        # Parse date in DD/MM/YYYY format
        date_str = data['date']
        try:
            search_date = datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            return jsonify({'message': 'Date must be in DD/MM/YYYY format'}), 400
        
        # Parse time in HH:MM format (24-hour)
        start_time_str = data['start_time']
        end_time_str = data['end_time']
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            return jsonify({'message': 'Times must be in HH:MM format'}), 400
        
        duration_minutes = data.get('duration_minutes', 60)
        court_type = data.get('court_type', 'all')
        court_config = data.get('court_config', 'all')  # 'all', 'single', 'double'
        live_search = data.get('live_search', False)  # Default to database-only search
        force_live_search = data.get('force_live_search', False)  # Admin override to force live search
        
        # Get location_ids, default to all locations if not specified
        location_ids = data.get('location_ids')
        if location_ids is None or (isinstance(location_ids, list) and len(location_ids) == 0):
            # Get all locations
            all_locations = availability_service.session.query(Location).all()
            location_ids = [loc.id for loc in all_locations]
        
        # Generate search hash for caching
        search_hash = availability_service.generate_search_hash(
            search_date, start_time, end_time, duration_minutes, court_type, court_config, location_ids
        )
        
        # Check for recent live search (within 15 minutes)
        recent_live_search = availability_service.get_recent_live_search(search_hash, max_age_minutes=15)
        used_cache = False
        
        # If user requested live search but we have recent data, use cached data instead
        # Unless force_live_search is True (admin override)
        if live_search and recent_live_search and not force_live_search:
            logger.info(f"Using cached data from recent live search (performed {recent_live_search.performed_at})")
            live_search = False
            used_cache = True
        
        # Force live search if admin override is requested
        if force_live_search:
            logger.info("Admin override: forcing live search")
            live_search = True
        
        # Fetch live availability data if requested
        if live_search:
            logger.info(f"Fetching live availability for date: {search_date}")
            api_date_str = search_date.strftime('%Y-%m-%d')
            total_slots = padel_service.fetch_and_store_all_availability(
                date_str=api_date_str,
                sport_id='PADEL'
            )
            logger.info(f"Fetched {total_slots} total slots from API")
            
            # Record the live search
            logger.info(f"Recording search request with hash: {search_hash}")
            try:
                availability_service.create_search_request_record(
                    search_hash=search_hash,
                    date=search_date,
                    start_time=start_time,
                    end_time=end_time,
                    duration_minutes=duration_minutes,
                    court_type=court_type,
                    court_config=court_config,
                    location_ids=location_ids,
                    live_search=True,
                    slots_found=total_slots
                )
                logger.info("Search request recorded successfully")
            except Exception as record_error:
                logger.error(f"Failed to record search request: {record_error}")
        
        # Build filter conditions - find availabilities that start within the time window
        filters = [
            Availability.date == search_date,
            Availability.start_time >= start_time,
            Availability.start_time <= end_time,
            Availability.duration == duration_minutes,  # Filter by requested duration
            Court.location_id.in_(location_ids),
            Availability.available == True
        ]
        
        # Filter by court type if specified
        if court_type == 'indoor':
            filters.append(Court.indoor == True)
        elif court_type == 'outdoor':
            filters.append(Court.indoor == False)
        
        # Filter by court configuration if specified
        if court_config == 'single':
            filters.append(Court.double == False)
        elif court_config == 'double':
            filters.append(Court.double == True)
        
        # Query availabilities from database
        query = availability_service.session.query(Availability).join(Court).join(Location).filter(and_(*filters))
        availabilities = query.all()
        logger.info(f"Found {len(availabilities)} availabilities matching search criteria")
        
        # If no results found and not doing a live search, automatically fetch fresh data
        if len(availabilities) == 0 and not live_search:
            logger.info(f"No data in database, automatically fetching from API for date: {search_date}")
            
            # First, ensure all locations have current court metadata (properties like indoor/double)
            # This is needed before fetching availabilities so courts have correct properties
            logger.info("Refreshing court metadata for all locations")
            for location in availability_service.get_all_locations():
                try:
                    padel_service.add_location_by_slug(location.slug)
                except Exception as e:
                    logger.warning(f"Could not refresh court metadata for {location.name}: {e}")
            
            api_date_str = search_date.strftime('%Y-%m-%d')
            total_slots = padel_service.fetch_and_store_all_availability(
                date_str=api_date_str,
                sport_id='PADEL'
            )
            logger.info(f"Fetched {total_slots} total slots from API")
            
            # After fetching, update court metadata again to match UUID-named courts with proper names and properties
            logger.info("Updating court metadata after availability fetch")
            for location in availability_service.get_all_locations():
                try:
                    padel_service.add_location_by_slug(location.slug)
                except Exception as e:
                    logger.warning(f"Could not update court metadata for {location.name}: {e}")
            
            # Re-query the database now that we have fresh data
            availabilities = query.all()
            logger.info(f"After fetch, found {len(availabilities)} availabilities matching search criteria")
            
            # Record the search
            try:
                availability_service.create_search_request_record(
                    search_hash=search_hash,
                    date=search_date,
                    start_time=start_time,
                    end_time=end_time,
                    duration_minutes=duration_minutes,
                    court_type=court_type,
                    court_config=court_config,
                    location_ids=location_ids,
                    live_search=False,
                    slots_found=total_slots
                )
            except Exception as record_error:
                logger.error(f"Failed to record search request: {record_error}")
        
        
        # Group results by court
        court_results = {}
        for avail in availabilities:
            court = availability_service.session.query(Court).filter(Court.id == avail.court_id).first()
            location = availability_service.session.query(Location).filter(Location.id == court.location_id).first()
            
            # If court name is a UUID, try to get the proper name from Playtomic API
            court_name = court.name
            import uuid
            try:
                uuid.UUID(court_name)
                # This is a UUID-named court, fetch proper name from Playtomic
                logger.info(f"Found UUID court name {court_name}, fetching proper name for location {location.slug}")
                try:
                    club_data = padel_service.fetch_club_info(location.slug, search_date.strftime('%Y-%m-%d'))
                    if club_data:
                        tenant = club_data.get('props', {}).get('pageProps', {}).get('tenant', {})
                        resources = tenant.get('resources', [])
                        # Find the court with matching resourceId (UUID)
                        for resource in resources:
                            if str(resource.get('resourceId')) == court_name:
                                proper_name = resource.get('name')
                                if proper_name:
                                    court_name = proper_name
                                    logger.info(f"Resolved court name from {court.name} to {court_name}")
                                    # Update the court name in database for future use
                                    court.name = court_name
                                    availability_service.session.commit()
                                break
                except Exception as e:
                    logger.warning(f"Failed to resolve court name for {court_name}: {e}")
            except ValueError:
                # Not a UUID, use the name as-is
                pass
            
            court_key = (court.id, court_name)
            if court_key not in court_results:
                court_results[court_key] = {
                    'court': {
                        'id': court.id,
                        'name': court_name,
                        'court_type': court.sport or 'standard',
                        'is_indoor': court.indoor or False,
                        'is_double': court.double or False,
                    },
                    'location': {
                        'id': location.id,
                        'name': location.name,
                        'address': location.address,
                    },
                    'availabilities': []
                }
            
            court_results[court_key]['availabilities'].append({
                'id': avail.id,
                'date': str(avail.date),
                'start_time': str(avail.start_time),
                'end_time': str(avail.end_time),
                'price': avail.price,
            })
        
        results = list(court_results.values())
        logger.info(f"Returning {len(results)} courts with availability")
        
        # Include cache information in response
        response_data = {
            'courts': results,
            'cached': used_cache,
            'cache_timestamp': recent_live_search.performed_at.isoformat() if recent_live_search else None
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'message': str(e)}), 400


# Search Order endpoints
@app.route('/api/search-orders', methods=['POST'])
@token_required
def create_search_order(current_user):
    """Create a new search order for automated availability checking"""
    data = request.get_json()
    
    required_fields = ['location_ids', 'date', 'start_time', 'end_time', 'duration_minutes']
    if not all(field in data for field in required_fields):
        return jsonify({'message': f'Required fields: {", ".join(required_fields)}'}), 400
    
    try:
        from app.models import SearchOrder
        from datetime import datetime
        import json
        
        # Parse date and time
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time_obj = datetime.strptime(data['end_time'], '%H:%M').time()
        
        # Create search order
        search_order = SearchOrder(
            user_id=current_user,
            location_ids=json.dumps(data['location_ids']),
            date=date_obj,
            start_time=start_time_obj,
            end_time=end_time_obj,
            duration_minutes=int(data['duration_minutes']),
            court_type=data.get('court_type', 'all'),
            court_config=data.get('court_config', 'all'),
            is_active=data.get('is_active', True)
        )
        
        availability_service.session.add(search_order)
        availability_service.session.commit()
        
        return jsonify({
            'message': 'Search order created successfully',
            'id': search_order.id,
            'user_id': search_order.user_id,
            'location_ids': json.loads(search_order.location_ids),
            'date': str(search_order.date),
            'start_time': str(search_order.start_time),
            'end_time': str(search_order.end_time),
            'duration_minutes': search_order.duration_minutes,
            'court_type': search_order.court_type,
            'court_config': search_order.court_config,
            'is_active': search_order.is_active,
            'created_at': str(search_order.created_at),
            'updated_at': str(search_order.updated_at) if search_order.updated_at else None,
            'last_check_at': str(search_order.last_check_at) if search_order.last_check_at else None
        }), 201
    except Exception as e:
        logger.error(f"Error creating search order: {str(e)}")
        return jsonify({'message': str(e)}), 400


@app.route('/api/search-orders', methods=['GET'])
@token_required
def get_user_search_orders(current_user):
    """Get all search orders for the current user"""
    from app.models import SearchOrder
    import json
    
    search_orders = availability_service.session.query(SearchOrder).filter(
        SearchOrder.user_id == current_user
    ).all()
    
    orders = []
    for order in search_orders:
        orders.append({
            'id': order.id,
            'user_id': order.user_id,
            'location_ids': json.loads(order.location_ids),
            'date': str(order.date),
            'start_time': str(order.start_time),
            'end_time': str(order.end_time),
            'duration_minutes': order.duration_minutes,
            'court_type': order.court_type,
            'court_config': order.court_config,
            'is_active': order.is_active,
            'created_at': str(order.created_at),
            'updated_at': str(order.updated_at) if order.updated_at else None,
            'last_check_at': str(order.last_check_at) if order.last_check_at else None
        })
    
    return jsonify({'search_orders': orders}), 200


@app.route('/api/search-orders/<int:order_id>', methods=['PUT'])
@token_required
def update_search_order(current_user, order_id):
    """Update a search order (e.g., activate/deactivate)"""
    from app.models import SearchOrder
    import json
    
    search_order = availability_service.session.query(SearchOrder).filter(
        SearchOrder.id == order_id
    ).first()
    
    if not search_order:
        return jsonify({'message': 'Search order not found'}), 404
    
    if search_order.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    if 'is_active' in data:
        search_order.is_active = data['is_active']
    if 'location_ids' in data:
        search_order.location_ids = json.dumps(data['location_ids'])
    if 'date' in data:
        from datetime import datetime
        search_order.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    if 'start_time' in data:
        from datetime import datetime
        search_order.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    if 'end_time' in data:
        from datetime import datetime
        search_order.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    if 'duration_minutes' in data:
        search_order.duration_minutes = int(data['duration_minutes'])
    if 'court_type' in data:
        search_order.court_type = data['court_type']
    if 'court_config' in data:
        search_order.court_config = data['court_config']
    
    availability_service.session.commit()
    
    return jsonify({
        'id': search_order.id,
        'user_id': search_order.user_id,
        'location_ids': json.loads(search_order.location_ids),
        'date': str(search_order.date),
        'start_time': str(search_order.start_time),
        'end_time': str(search_order.end_time),
        'duration_minutes': search_order.duration_minutes,
        'court_type': search_order.court_type,
        'court_config': search_order.court_config,
        'is_active': search_order.is_active,
        'created_at': str(search_order.created_at),
        'updated_at': str(search_order.updated_at) if search_order.updated_at else None,
        'last_check_at': str(search_order.last_check_at) if search_order.last_check_at else None
    }), 200


@app.route('/api/search-orders/<int:order_id>', methods=['GET'])
@token_required
def get_search_order_results(current_user, order_id):
    """Get a specific search order"""
    from app.models import SearchOrder
    import json
    
    search_order = availability_service.session.query(SearchOrder).filter(
        SearchOrder.id == order_id
    ).first()
    
    if not search_order:
        return jsonify({'message': 'Search order not found'}), 404
    
    if search_order.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    return jsonify({
        'id': search_order.id,
        'user_id': search_order.user_id,
        'location_ids': json.loads(search_order.location_ids),
        'date': str(search_order.date),
        'start_time': str(search_order.start_time),
        'end_time': str(search_order.end_time),
        'duration_minutes': search_order.duration_minutes,
        'court_type': search_order.court_type,
        'court_config': search_order.court_config,
        'is_active': search_order.is_active,
        'created_at': str(search_order.created_at),
        'updated_at': str(search_order.updated_at) if search_order.updated_at else None,
        'last_check_at': str(search_order.last_check_at) if search_order.last_check_at else None
    }), 200


@app.route('/api/search-orders/<int:order_id>', methods=['DELETE'])
@token_required
def cancel_search_order(current_user, order_id):
    """Delete a search order"""
    from app.models import SearchOrder
    
    search_order = availability_service.session.query(SearchOrder).filter(
        SearchOrder.id == order_id
    ).first()
    
    if not search_order:
        return jsonify({'message': 'Search order not found'}), 404
    
    if search_order.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    availability_service.session.delete(search_order)
    availability_service.session.commit()
    
    return jsonify({'message': 'Search order deleted'}), 200


@app.route('/api/search-orders/<int:order_id>/fetch', methods=['POST'])
@token_required
def fetch_search_order_availability(current_user, order_id):
    """Manually trigger availability fetch for a search order"""
    # Verify ownership
    search_order = availability_service.get_search_order(order_id)
    if not search_order:
        return jsonify({'message': 'Search order not found'}), 404
    
    if search_order.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        result = padel_service.fetch_and_search_availability(order_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400


# Admin endpoints
@app.route('/api/admin/users/pending', methods=['GET'])
@token_required
def get_pending_users(current_user):
    """Get all users waiting for approval (admin only)"""
    # Check if user is admin
    user = availability_service.get_user_by_id(current_user)
    if not user or not user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    pending_users = availability_service.get_pending_users()
    users_list = []
    for u in pending_users:
        users_list.append({
            'id': u.id,
            'email': u.email,
            'user_id': u.user_id,
            'active': u.active,
            'created_at': str(u.created_at)
        })
    
    return jsonify({'pending_users': users_list}), 200


@app.route('/api/admin/users/<user_id>/approve', methods=['POST'])
@token_required
def approve_user(current_user, user_id):
    """Approve a user account (admin only)"""
    # Check if user is admin
    admin_user = availability_service.get_user_by_id(current_user)
    if not admin_user or not admin_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    approved_user = availability_service.approve_user(user_id, current_user)
    if approved_user:
        return jsonify({
            'message': f'User {user_id} approved successfully',
            'user': {
                'id': approved_user.id,
                'email': approved_user.email,
                'user_id': approved_user.user_id,
                'approved_at': str(approved_user.approved_at)
            }
        }), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/api/admin/users/<user_id>/reject', methods=['DELETE'])
@token_required
def reject_user(current_user, user_id):
    """Reject a user account (admin only)"""
    # Check if user is admin
    admin_user = availability_service.get_user_by_id(current_user)
    if not admin_user or not admin_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    if availability_service.reject_user(user_id):
        return jsonify({'message': f'User {user_id} rejected and removed'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/api/admin/users/<user_id>/activate', methods=['POST'])
@token_required
def activate_user(current_user, user_id):
    """Activate a user account (admin only)"""
    # Check if user is admin
    admin_user = availability_service.get_user_by_id(current_user)
    if not admin_user or not admin_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    activated_user = availability_service.activate_user(user_id)
    if activated_user:
        return jsonify({
            'message': f'User {user_id} activated successfully',
            'user': {
                'id': activated_user.id,
                'email': activated_user.email,
                'user_id': activated_user.user_id,
                'active': activated_user.active
            }
        }), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/api/admin/users/<user_id>/deactivate', methods=['POST'])
@token_required
def deactivate_user(current_user, user_id):
    """Deactivate a user account (admin only)"""
    # Check if user is admin
    admin_user = availability_service.get_user_by_id(current_user)
    if not admin_user or not admin_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    deactivated_user = availability_service.deactivate_user(user_id)
    if deactivated_user:
        return jsonify({
            'message': f'User {user_id} deactivated successfully',
            'user': {
                'id': deactivated_user.id,
                'email': deactivated_user.email,
                'user_id': deactivated_user.user_id,
                'active': deactivated_user.active
            }
        }), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/api/locations/<int:location_id>', methods=['DELETE'])
@token_required
def delete_location(current_user, location_id):
    """Delete a location (admin only)"""
    # Check if user is admin
    user = availability_service.get_user_by_id(current_user)
    if not user or not user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    if availability_service.delete_location(location_id):
        return jsonify({'message': 'Location deleted successfully'}), 200
    else:
        return jsonify({'message': 'Location not found'}), 404


@app.route('/api/admin/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    """Get all users (admin only)"""
    # Check if user is admin
    user = availability_service.get_user_by_id(current_user)
    if not user or not user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    all_users = availability_service.get_all_users()
    users_list = []
    for u in all_users:
        users_list.append({
            'id': u.id,
            'email': u.email,
            'user_id': u.user_id,
            'approved': u.approved,
            'active': u.active,
            'is_admin': u.is_admin,
            'created_at': str(u.created_at),
            'approved_at': str(u.approved_at) if u.approved_at else None
        })
    
    return jsonify({'users': users_list}), 200


# Cache Management endpoints
@app.route('/api/admin/cache/clear', methods=['POST'])
@token_required
def clear_search_cache(current_user):
    """Clear search cache (admin only)"""
    # Check if user is admin
    user = availability_service.get_user_by_id(current_user)
    if not user or not user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    data = request.get_json() or {}
    older_than_minutes = data.get('older_than_minutes')  # Optional: only clear cache older than X minutes
    
    try:
        deleted_count = availability_service.clear_search_cache(older_than_minutes)
        message = f'Cache cleared successfully. Deleted {deleted_count} search request records.'
        if older_than_minutes:
            message += f' (older than {older_than_minutes} minutes)'
        
        return jsonify({
            'message': message,
            'deleted_count': deleted_count
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400


# Availability endpoints
@app.route('/api/availability/fetch', methods=['POST'])
@token_required
def fetch_availability(current_user):
    """Fetch and store availability for all locations"""
    data = request.get_json()
    date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    sport_id = data.get('sport_id', 'PADEL')
    
    try:
        total_slots = padel_service.fetch_and_store_all_availability(
            date_str=date_str,
            sport_id=sport_id
        )
        return jsonify({
            'message': 'Availability fetched successfully',
            'total_slots': total_slots
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400


# Admin refresh endpoints
@app.route('/api/admin/refresh-all-data', methods=['POST'])
@token_required
def refresh_all_data(current_user):
    """Refresh all locations, courts, and availability data (admin only)"""
    # Check if user is admin
    user = availability_service.get_user_by_id(current_user)
    if not user or not user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    try:
        from app.models import Availability, Court, SearchRequest
        
        # Get all locations
        all_locations = availability_service.get_all_locations()
        logger.info(f"Starting refresh of {len(all_locations)} locations")
        
        # Delete all availabilities (bulk delete for efficiency)
        availabilities_count = availability_service.session.query(Availability).delete()
        availability_service.session.commit()
        logger.info(f"Deleted {availabilities_count} availabilities")
        
        # Delete all search cache
        search_cache_count = availability_service.session.query(SearchRequest).delete()
        availability_service.session.commit()
        logger.info(f"Deleted {search_cache_count} cached searches")
        
        # For each location, delete courts and re-add location to refresh court data
        courts_deleted = 0
        courts_added = 0
        
        for location in all_locations:
            try:
                # Get courts to delete
                courts = availability_service.session.query(Court).filter(Court.location_id == location.id).all()
                courts_deleted += len(courts)
                
                # Delete courts
                for court in courts:
                    availability_service.session.delete(court)
                availability_service.session.commit()
                
                # Re-add location to fetch fresh court data
                date_str = datetime.now().strftime('%Y-%m-%d')
                padel_service.add_location_by_slug(location.slug, date_str)
                
                # Count new courts
                new_courts = availability_service.session.query(Court).filter(Court.location_id == location.id).all()
                courts_added += len(new_courts)
                
                logger.info(f"Refreshed location {location.name}: deleted {len(courts)}, added {len(new_courts)}")
            except Exception as loc_error:
                logger.error(f"Error refreshing location {location.name}: {str(loc_error)}")
        
        message = f"Data refresh complete. Deleted {courts_deleted} courts, added {courts_added} courts. Deleted {availabilities_count} availabilities and {search_cache_count} cached searches."
        logger.info(message)
        
        return jsonify({
            'message': message,
            'locations_refreshed': len(all_locations),
            'courts_deleted': courts_deleted,
            'courts_added': courts_added,
            'availabilities_deleted': availabilities_count,
            'search_cache_deleted': search_cache_count
        }), 200
    except Exception as e:
        logger.error(f"Error during refresh: {str(e)}")
        return jsonify({'message': str(e)}), 400


if __name__ == '__main__':
    # Development server
    app.run(debug=DEBUG, host=HOST, port=PORT)
