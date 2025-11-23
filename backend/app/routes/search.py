"""Search routes blueprint"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, time
from sqlalchemy import and_

search_bp = Blueprint('search', __name__, url_prefix='/api/search')
logger = logging.getLogger(__name__)


def get_services():
    """Import services here to avoid circular imports"""
    from app.services import AvailabilityService
    from app.courtfinder.padelmate import PadelMateService
    return AvailabilityService(), PadelMateService()


def token_required(f):
    """Import from auth module"""
    from app.routes.auth import token_required as auth_token_required
    return auth_token_required(f)


def perform_court_search(search_date, start_time, end_time, duration_minutes, court_type, court_config, location_ids, force_live=False):
    """
    Unified search function used by both normal search and execute search order endpoints.
    
    Args:
        search_date: date object
        start_time: time object
        end_time: time object
        duration_minutes: int
        court_type: 'all', 'indoor', 'outdoor'
        court_config: 'all', 'single', 'double'
        location_ids: list of location IDs
        force_live: bool - force live search from API
    
    Returns:
        list of court results with availabilities
    """
    from app.models import Availability, Court, Location
    import uuid
    
    availability_service, padel_service = get_services()
    
    logger.info(f"[SEARCH] Searching for courts: date={search_date}, time={start_time}-{end_time}, duration={duration_minutes}min, type={court_type}, config={court_config}")
    
    # Generate search hash for caching
    search_hash = availability_service.generate_search_hash(
        search_date, start_time, end_time, duration_minutes, court_type, court_config, location_ids
    )
    
    # If not forcing live search, check for cached results
    if not force_live:
        recent_live_search = availability_service.get_recent_live_search(search_hash, max_age_minutes=15)
        if recent_live_search:
            logger.info(f"[SEARCH] Using cached data from recent live search (performed {recent_live_search.performed_at})")
    
    # Always refresh court metadata before searching
    logger.info("[SEARCH] Refreshing court metadata for all locations")
    for location in availability_service.get_all_locations():
        try:
            padel_service.add_location_by_slug(location.slug)
        except Exception as e:
            logger.warning(f"[SEARCH] Could not refresh court metadata for {location.name}: {e}")
    
    # Fetch fresh availability data from API
    logger.info(f"[SEARCH] Fetching live availability for date: {search_date}")
    api_date_str = search_date.strftime('%Y-%m-%d')
    total_slots = padel_service.fetch_and_store_all_availability(
        date_str=api_date_str,
        sport_id='PADEL'
    )
    logger.info(f"[SEARCH] Fetched {total_slots} total slots from API")
    
    # After fetching, update court metadata again
    logger.info("[SEARCH] Updating court metadata after availability fetch")
    for location in availability_service.get_all_locations():
        try:
            padel_service.add_location_by_slug(location.slug)
        except Exception as e:
            logger.warning(f"[SEARCH] Could not update court metadata for {location.name}: {e}")
    
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
            live_search=True,
            slots_found=total_slots
        )
    except Exception as record_error:
        logger.error(f"[SEARCH] Failed to record search request: {record_error}")
    
    # Build filter conditions - find availabilities that start within the time window
    filters = [
        Availability.date == search_date,
        Availability.start_time >= start_time,
        Availability.start_time <= end_time,
        Availability.duration == duration_minutes,
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
    logger.info(f"[SEARCH] Found {len(availabilities)} availabilities matching criteria")
    
    # Group results by court
    court_results = {}
    for avail in availabilities:
        court = availability_service.session.query(Court).filter(Court.id == avail.court_id).first()
        location = availability_service.session.query(Location).filter(Location.id == court.location_id).first()
        
        # If court name is a UUID, try to get the proper name from Playtomic API
        court_name = court.name
        try:
            uuid.UUID(court_name)
            # This is a UUID-named court, fetch proper name from Playtomic
            logger.info(f"[SEARCH] Found UUID court name {court_name}, fetching proper name for location {location.slug}")
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
                                logger.info(f"[SEARCH] Resolved court name from {court.name} to {court_name}")
                                # Update the court name in database for future use
                                court.name = court_name
                                availability_service.session.commit()
                            break
            except Exception as e:
                logger.warning(f"[SEARCH] Failed to resolve court name for {court_name}: {e}")
        except ValueError:
            # Not a UUID, use the name as-is
            pass
        
        # Use only court.id as the key to ensure uniqueness
        court_key = court.id
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
                    'slug': location.slug,
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
    
    # Group results by location
    locations_dict = {}
    for court_data in court_results.values():
        location_id = court_data['location']['id']
        if location_id not in locations_dict:
            locations_dict[location_id] = {
                'location': court_data['location'],
                'courts': []
            }
        
        # Add court with its availabilities to the location
        locations_dict[location_id]['courts'].append({
            'court': court_data['court'],
            'availabilities': court_data['availabilities']
        })
    
    # Convert to list and sort by location name
    results = sorted(locations_dict.values(), key=lambda x: x['location']['name'])
    
    logger.info(f"[SEARCH] Returning {len(results)} locations with {len(court_results)} courts total")
    return results


@search_bp.route('/available', methods=['POST'])
@token_required
def search_available_courts(current_user):
    """Search for available courts on a specific date within a time range"""
    try:
        from app.models import Location
        
        availability_service, _ = get_services()
        data = request.get_json()
        
        required_fields = ['date', 'start_time', 'end_time']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Required fields: {", ".join(required_fields)}'}), 400
        
        # Parse date in DD/MM/YYYY format
        date_str = data['date']
        try:
            search_date = datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            return jsonify({'error': 'Date must be in DD/MM/YYYY format'}), 400
        
        # Parse time in HH:MM format (24-hour)
        start_time_str = data['start_time']
        end_time_str = data['end_time']
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Times must be in HH:MM format'}), 400
        
        duration_minutes = data.get('duration_minutes', 60)
        court_type = data.get('court_type', 'all')
        court_config = data.get('court_config', 'all')
        force_live_search = data.get('force_live_search', False)
        
        # Get location_ids, default to all locations if not specified
        location_ids = data.get('location_ids')
        if location_ids is None or (isinstance(location_ids, list) and len(location_ids) == 0):
            # Get all locations
            all_locations = availability_service.session.query(Location).all()
            location_ids = [loc.id for loc in all_locations]
        
        # Perform the search
        results = perform_court_search(
            search_date=search_date,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            court_type=court_type,
            court_config=court_config,
            location_ids=location_ids,
            force_live=force_live_search
        )
        
        # Include cache information in response
        response_data = {
            'locations': results,
            'cached': False,
            'cache_timestamp': None
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 400
