"""Search Orders routes blueprint"""
from flask import Blueprint, request, jsonify
import logging
import json
from datetime import datetime, timezone

search_orders_bp = Blueprint('search_orders', __name__, url_prefix='/api/search-orders')
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
    """Import from search module"""
    from app.routes.search import perform_court_search as search_perform_court_search
    return search_perform_court_search(search_date, start_time, end_time, duration_minutes, court_type, court_config, location_ids, force_live)


@search_orders_bp.route('', methods=['POST'])
@token_required
def create_search_order(current_user):
    """Create a new search order for automated availability checking"""
    try:
        from app.models import SearchOrder
        
        availability_service, _ = get_services()
        data = request.get_json()
        
        required_fields = ['location_ids', 'date', 'start_time', 'end_time', 'duration_minutes']
        if not all(field in data for field in required_fields):
            return jsonify({'message': f'Required fields: {", ".join(required_fields)}'}), 400
        
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
        return jsonify({'error': str(e)}), 400


@search_orders_bp.route('', methods=['GET'])
@token_required
def get_user_search_orders(current_user):
    """Get all search orders for the current user"""
    try:
        from app.models import SearchOrder
        
        availability_service, _ = get_services()
        
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
    except Exception as e:
        logger.error(f"Error getting search orders: {str(e)}")
        return jsonify({'error': str(e)}), 400


@search_orders_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_search_order_results(current_user, order_id):
    """Get a specific search order"""
    try:
        from app.models import SearchOrder
        
        availability_service, _ = get_services()
        
        search_order = availability_service.session.query(SearchOrder).filter(
            SearchOrder.id == order_id
        ).first()
        
        if not search_order:
            return jsonify({'error': 'Search order not found'}), 404
        
        if search_order.user_id != current_user:
            return jsonify({'error': 'Unauthorized'}), 403
        
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
    except Exception as e:
        logger.error(f"Error getting search order: {str(e)}")
        return jsonify({'error': str(e)}), 400


@search_orders_bp.route('/<int:order_id>', methods=['PUT'])
@token_required
def update_search_order(current_user, order_id):
    """Update a search order (e.g., activate/deactivate)"""
    try:
        from app.models import SearchOrder
        
        availability_service, _ = get_services()
        
        search_order = availability_service.session.query(SearchOrder).filter(
            SearchOrder.id == order_id
        ).first()
        
        if not search_order:
            return jsonify({'error': 'Search order not found'}), 404
        
        if search_order.user_id != current_user:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        if 'is_active' in data:
            search_order.is_active = data['is_active']
        if 'location_ids' in data:
            search_order.location_ids = json.dumps(data['location_ids'])
        if 'date' in data:
            search_order.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'start_time' in data:
            search_order.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        if 'end_time' in data:
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
    except Exception as e:
        logger.error(f"Error updating search order: {str(e)}")
        return jsonify({'error': str(e)}), 400


@search_orders_bp.route('/<int:order_id>', methods=['DELETE'])
@token_required
def cancel_search_order(current_user, order_id):
    """Delete a search order"""
    try:
        from app.models import SearchOrder
        
        availability_service, _ = get_services()
        
        search_order = availability_service.session.query(SearchOrder).filter(
            SearchOrder.id == order_id
        ).first()
        
        if not search_order:
            return jsonify({'error': 'Search order not found'}), 404
        
        if search_order.user_id != current_user:
            return jsonify({'error': 'Unauthorized'}), 403
        
        availability_service.session.delete(search_order)
        availability_service.session.commit()
        
        return jsonify({'message': 'Search order deleted'}), 200
    except Exception as e:
        logger.error(f"Error deleting search order: {str(e)}")
        return jsonify({'error': str(e)}), 400


@search_orders_bp.route('/<int:order_id>/execute', methods=['POST'])
@token_required
def execute_search_order(current_user, order_id):
    """Manually execute a search order (for testing or immediate check)"""
    try:
        from app.models import SearchOrder, User
        
        availability_service, _ = get_services()
        from app.email_service import email_service
        
        search_order = availability_service.session.query(SearchOrder).filter(
            SearchOrder.id == order_id
        ).first()
        
        if not search_order:
            return jsonify({'error': 'Search order not found'}), 404
        
        # Check if user is admin or owns the order
        user = availability_service.get_user_by_id(current_user)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if search_order.user_id != current_user and not user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Execute the search order using its original parameters
        search_date = search_order.date
        start_time = search_order.start_time
        end_time = search_order.end_time
        duration_minutes = search_order.duration_minutes
        court_type = search_order.court_type
        court_config = search_order.court_config
        location_ids = json.loads(search_order.location_ids)
        
        logger.info(f"[EXECUTE] Executing search order {order_id} - date: {search_date}, time: {start_time}-{end_time}")
        
        # Use the unified search function with force_live to always fetch fresh data
        results = perform_court_search(
            search_date=search_date,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            court_type=court_type,
            court_config=court_config,
            location_ids=location_ids,
            force_live=True
        )
        
        # Update last_check_at
        search_order.last_check_at = datetime.now(timezone.utc)
        availability_service.session.commit()
        
        logger.info(f"[EXECUTE] Search order {order_id} completed - found {len(results)} courts")
        
        # Send email notification if courts were found
        if len(results) > 0:
            logger.info(f"[EXECUTE] Courts found! Sending email notification to user {search_order.user_id}")
            
            # Get user to get their email
            order_user = availability_service.session.query(User).filter(
                User.user_id == search_order.user_id
            ).first()
            
            if order_user and order_user.email:
                # Prepare search parameters for email
                unique_locations = set()
                for result in results:
                    location = result.get('location', {})
                    if location.get('name'):
                        unique_locations.add(location.get('name'))
                
                search_params = {
                    'date': str(search_date),
                    'start_time': str(start_time),
                    'end_time': str(end_time),
                    'duration_minutes': duration_minutes,
                    'court_type': court_type,
                    'court_config': court_config,
                    'locations': list(unique_locations)
                }
                
                # Convert results to courts_found format for email (limit to 5 courts)
                courts_found = []
                for result in results:
                    court = result.get('court', {})
                    location = result.get('location', {})
                    for avail in result.get('availabilities', []):
                        courts_found.append({
                            'location': location.get('name', 'Unknown'),
                            'court': court.get('name', 'Unknown'),
                            'date': avail.get('date', ''),
                            'timeslot': f"{avail.get('start_time', '')}-{avail.get('end_time', '')}",
                            'price': avail.get('price', 'N/A'),
                            'provider': 'PadelMate'
                        })
                        if len(courts_found) >= 5:
                            break
                    if len(courts_found) >= 5:
                        break
                
                # Add search URL for the button
                search_url = f"{email_service.frontend_base_url}/search-results?date={search_date.strftime('%d/%m/%Y')}&start_time={start_time.strftime('%H:%M')}&end_time={end_time.strftime('%H:%M')}&duration_minutes={duration_minutes}&court_type={court_type}&court_config={court_config}&location_ids={','.join(map(str, location_ids))}&live_search=true"
                search_params['search_url'] = search_url
                
                # Send email notification
                email_sent = email_service.send_court_found_notification(
                    recipient_email=order_user.email,
                    recipient_name=order_user.email.split('@')[0],
                    search_order_id=order_id,
                    courts_found=courts_found,
                    search_params=search_params
                )
                
                if email_sent:
                    logger.info(f"[EXECUTE] Email notification sent successfully to {order_user.email}")
                else:
                    logger.error(f"[EXECUTE] Failed to send email notification to {order_user.email}")
            else:
                logger.warning(f"[EXECUTE] No email found for user {search_order.user_id}")
        
        return jsonify({
            'courts': results,
            'total_courts': len(results)
        }), 200
    except Exception as e:
        logger.error(f"[EXECUTE] Error executing search order {order_id}: {str(e)}")
        return jsonify({'error': str(e)}), 400
