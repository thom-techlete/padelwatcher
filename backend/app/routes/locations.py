"""Locations routes blueprint"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

locations_bp = Blueprint('locations', __name__, url_prefix='/api/locations')
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


@locations_bp.route('', methods=['GET'])
def get_locations():
    """Get all available locations/clubs"""
    try:
        _, padel_service = get_services()
        locations = padel_service.get_all_clubs()
        return jsonify({'locations': locations}), 200
    except Exception as e:
        logger.error(f"Error getting locations: {str(e)}")
        return jsonify({'error': str(e)}), 400


@locations_bp.route('', methods=['POST'])
@token_required
def add_location(current_user):
    """Add a new location by slug"""
    try:
        _, padel_service = get_services()
        data = request.get_json()
        
        if not data or not data.get('slug'):
            return jsonify({'error': 'Slug is required'}), 400
        
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
        logger.error(f"Error adding location: {str(e)}")
        return jsonify({'error': str(e)}), 400


@locations_bp.route('/<int:location_id>/courts', methods=['GET'])
def get_location_courts(location_id):
    """Get all courts for a specific location"""
    try:
        _, padel_service = get_services()
        courts = padel_service.get_courts_for_location(location_id)
        return jsonify({'courts': courts}), 200
    except Exception as e:
        logger.error(f"Error getting location courts: {str(e)}")
        return jsonify({'error': str(e)}), 400


@locations_bp.route('/<int:location_id>', methods=['DELETE'])
@token_required
def delete_location(current_user, location_id):
    """Delete a location (admin only)"""
    try:
        availability_service, _ = get_services()
        
        # Check if user is admin
        user = availability_service.get_user_by_id(current_user)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        if availability_service.delete_location(location_id):
            return jsonify({'message': 'Location deleted successfully'}), 200
        else:
            return jsonify({'error': 'Location not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting location: {str(e)}")
        return jsonify({'error': str(e)}), 400
