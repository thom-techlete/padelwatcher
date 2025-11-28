"""Admin routes blueprint"""

import logging

from flask import Blueprint, jsonify, request

from app.models import Court
from app.services.availability_service import availability_service
from app.services.location_service import location_service
from app.services.search_service import search_service
from app.services.user_service import user_service
from app.utils import admin_required, get_provider, token_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
logger = logging.getLogger(__name__)


@admin_bp.route("/users/pending", methods=["GET"])
@token_required
@admin_required
def get_pending_users(current_user):
    """Get all users waiting for approval (admin only)"""
    try:
        pending_users = user_service.get_pending_users()
        users_list = []
        for u in pending_users:
            users_list.append(
                {
                    "id": u.id,
                    "email": u.email,
                    "user_id": u.user_id,
                    "active": u.active,
                    "created_at": str(u.created_at),
                }
            )

        return jsonify({"pending_users": users_list}), 200
    except Exception as e:
        logger.error(f"Error getting pending users: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/users/<user_id>/approve", methods=["POST"])
@token_required
@admin_required
def approve_user(current_user, user_id):
    """Approve a user account (admin only)"""
    try:
        approved_user = user_service.approve_user(user_id, current_user)
        if approved_user:
            return (
                jsonify(
                    {
                        "message": f"User {user_id} approved successfully",
                        "user": {
                            "id": approved_user.id,
                            "email": approved_user.email,
                            "user_id": approved_user.user_id,
                            "approved_at": str(approved_user.approved_at),
                        },
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logger.error(f"Error approving user: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/users/<user_id>/reject", methods=["DELETE"])
@token_required
@admin_required
def reject_user(current_user, user_id):
    """Reject a user account (admin only)"""
    try:
        if user_service.reject_user(user_id):
            return jsonify({"message": f"User {user_id} rejected and removed"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logger.error(f"Error rejecting user: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/users/<user_id>/activate", methods=["POST"])
@token_required
@admin_required
def activate_user(current_user, user_id):
    """Activate a user account (admin only)"""
    try:
        activated_user = user_service.activate_user(user_id)
        if activated_user:
            return (
                jsonify(
                    {
                        "message": f"User {user_id} activated successfully",
                        "user": {
                            "id": activated_user.id,
                            "email": activated_user.email,
                            "user_id": activated_user.user_id,
                            "active": activated_user.active,
                        },
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logger.error(f"Error activating user: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/users/<user_id>/deactivate", methods=["POST"])
@token_required
@admin_required
def deactivate_user(current_user, user_id):
    """Deactivate a user account (admin only)"""
    try:
        deactivated_user = user_service.deactivate_user(user_id)
        if deactivated_user:
            return (
                jsonify(
                    {
                        "message": f"User {user_id} deactivated successfully",
                        "user": {
                            "id": deactivated_user.id,
                            "email": deactivated_user.email,
                            "user_id": deactivated_user.user_id,
                            "active": deactivated_user.active,
                        },
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logger.error(f"Error deactivating user: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/users", methods=["GET"])
@token_required
@admin_required
def get_all_users(current_user):
    """Get all users (admin only)"""
    try:
        all_users = user_service.get_all_users()
        users_list = []
        for u in all_users:
            users_list.append(
                {
                    "id": u.id,
                    "email": u.email,
                    "user_id": u.user_id,
                    "approved": u.approved,
                    "active": u.active,
                    "is_admin": u.is_admin,
                    "created_at": str(u.created_at),
                    "approved_at": str(u.approved_at) if u.approved_at else None,
                }
            )

        return jsonify({"users": users_list}), 200
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/cache/clear", methods=["POST"])
@token_required
@admin_required
def clear_search_cache(current_user):
    """Clear search cache (admin only)"""
    try:
        data = request.get_json() or {}
        older_than_minutes = data.get("older_than_minutes")

        deleted_count = search_service.clear_search_cache(older_than_minutes)
        message = f"Cache cleared successfully. Deleted {deleted_count} search request records."
        if older_than_minutes:
            message += f" (older than {older_than_minutes} minutes)"

        return jsonify({"message": message, "deleted_count": deleted_count}), 200
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/refresh-all-data", methods=["POST"])
@token_required
@admin_required
def refresh_all_data(current_user):
    """Refresh all locations, courts, and availability data (admin only)"""
    try:
        # Get all locations
        all_locations = location_service.get_all_locations()
        logger.info(f"Starting refresh of {len(all_locations)} locations")

        # Delete all availabilities (bulk delete for efficiency)
        availabilities_count = availability_service.delete_all_availabilities()
        logger.info(f"Deleted {availabilities_count} availabilities")

        # Delete all search cache
        search_cache_count = search_service.clear_search_cache()
        logger.info(f"Deleted {search_cache_count} cached searches")

        # For each location, delete courts and re-add location to refresh court data
        courts_deleted = 0
        courts_added = 0

        for location in all_locations:
            try:
                # Get courts to delete
                courts = (
                    availability_service.session.query(Court)
                    .filter(Court.location_id == location.id)
                    .all()
                )
                courts_deleted += len(courts)
                provider = get_provider(location.provider)

                # Delete courts
                for court in courts:
                    availability_service.session.delete(court)
                availability_service.session.commit()

                # Re-add location to fetch fresh court data
                provider.add_location_by_slug(location.slug)

                # Count new courts
                new_courts = (
                    availability_service.session.query(Court)
                    .filter(Court.location_id == location.id)
                    .all()
                )
                courts_added += len(new_courts)

                logger.info(
                    f"Refreshed location {location.name}: deleted {len(courts)}, added {len(new_courts)}"
                )
            except Exception as loc_error:
                logger.error(
                    f"Error refreshing location {location.name}: {str(loc_error)}"
                )

        message = f"Data refresh complete. Deleted {courts_deleted} courts, added {courts_added} courts. Deleted {availabilities_count} availabilities and {search_cache_count} cached searches."
        logger.info(message)

        return (
            jsonify(
                {
                    "message": message,
                    "locations_refreshed": len(all_locations),
                    "courts_deleted": courts_deleted,
                    "courts_added": courts_added,
                    "availabilities_deleted": availabilities_count,
                    "search_cache_deleted": search_cache_count,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error during refresh: {str(e)}")
        return jsonify({"error": str(e)}), 400
