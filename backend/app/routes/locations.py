"""Locations routes blueprint"""

import logging

from flask import Blueprint, jsonify, request

from app.routes.auth import token_required
from app.services.court_service import court_service
from app.services.location_service import location_service
from app.services.user_service import user_service
from app.utils import (
    get_provider,
    serialize_models,
    validate_request_fields,
)

locations_bp = Blueprint("locations", __name__, url_prefix="/api/locations")
logger = logging.getLogger(__name__)


@locations_bp.route("", methods=["GET"])
def get_locations():
    """Get all available locations/clubs"""
    try:
        locations = location_service.get_all_locations()
        return jsonify({"locations": serialize_models(locations)}), 200
    except Exception as e:
        logger.error(f"Error getting locations: {str(e)}")
        return jsonify({"error": str(e)}), 400


@locations_bp.route("", methods=["POST"])
@token_required
@validate_request_fields(["slug", "provider"])
def add_location(current_user):
    """Add a new location by slug"""
    try:
        data = request.get_json()
        provider = get_provider(data["provider"])
        location = provider.add_location_by_slug(slug=data["slug"])
        return (
            jsonify(
                {
                    "message": "Location added successfully",
                    "location": {
                        "id": location.id,
                        "name": location.name,
                        "slug": location.slug,
                        "tenant_id": location.tenant_id,
                    },
                }
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Error adding location: {str(e)}")
        return jsonify({"error": str(e)}), 400


@locations_bp.route("/<int:location_id>/courts", methods=["GET"])
def get_location_courts(location_id):
    """Get all courts for a specific location"""
    try:
        courts = court_service.get_courts_by_location(location_id)
        return jsonify({"courts": serialize_models(courts)}), 200
    except Exception as e:
        logger.error(f"Error getting location courts: {str(e)}")
        return jsonify({"error": str(e)}), 400


@locations_bp.route("/<int:location_id>", methods=["DELETE"])
@token_required
def delete_location(current_user, location_id):
    """Delete a location (admin only)"""
    try:
        # Check if user is admin
        user = user_service.get_user_by_id(current_user)
        if not user or not user.is_admin:
            return jsonify({"error": "Admin access required"}), 403

        if location_service.delete_location(location_id):
            return jsonify({"message": "Location deleted successfully"}), 200
        else:
            return jsonify({"error": "Location not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting location: {str(e)}")
        return jsonify({"error": str(e)}), 400
