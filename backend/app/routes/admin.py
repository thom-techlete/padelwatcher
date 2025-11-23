"""Admin routes blueprint"""

import logging
from datetime import datetime

from flask import Blueprint, jsonify, request

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
logger = logging.getLogger(__name__)


def get_services():
    """Import services here to avoid circular imports"""
    from app.courtfinder.padelmate import PadelMateService
    from app.services import AvailabilityService

    return AvailabilityService(), PadelMateService()


def token_required(f):
    """Import from auth module"""
    from app.routes.auth import token_required as auth_token_required

    return auth_token_required(f)


def require_admin(f):
    """Decorator to require admin access"""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        availability_service, _ = get_services()
        # current_user is passed as first argument after self
        current_user = args[0] if args else None
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        user = availability_service.get_user_by_id(current_user)
        if not user or not user.is_admin:
            return jsonify({"error": "Admin access required"}), 403

        return f(*args, **kwargs)

    return decorated


@admin_bp.route("/users/pending", methods=["GET"])
@token_required
@require_admin
def get_pending_users(current_user):
    """Get all users waiting for approval (admin only)"""
    try:
        availability_service, _ = get_services()

        pending_users = availability_service.get_pending_users()
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
@require_admin
def approve_user(current_user, user_id):
    """Approve a user account (admin only)"""
    try:
        availability_service, _ = get_services()

        approved_user = availability_service.approve_user(user_id, current_user)
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
@require_admin
def reject_user(current_user, user_id):
    """Reject a user account (admin only)"""
    try:
        availability_service, _ = get_services()

        if availability_service.reject_user(user_id):
            return jsonify({"message": f"User {user_id} rejected and removed"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logger.error(f"Error rejecting user: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/users/<user_id>/activate", methods=["POST"])
@token_required
@require_admin
def activate_user(current_user, user_id):
    """Activate a user account (admin only)"""
    try:
        availability_service, _ = get_services()

        activated_user = availability_service.activate_user(user_id)
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
@require_admin
def deactivate_user(current_user, user_id):
    """Deactivate a user account (admin only)"""
    try:
        availability_service, _ = get_services()

        deactivated_user = availability_service.deactivate_user(user_id)
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
@require_admin
def get_all_users(current_user):
    """Get all users (admin only)"""
    try:
        availability_service, _ = get_services()

        all_users = availability_service.get_all_users()
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
@require_admin
def clear_search_cache(current_user):
    """Clear search cache (admin only)"""
    try:
        availability_service, _ = get_services()

        data = request.get_json() or {}
        older_than_minutes = data.get("older_than_minutes")

        deleted_count = availability_service.clear_search_cache(older_than_minutes)
        message = f"Cache cleared successfully. Deleted {deleted_count} search request records."
        if older_than_minutes:
            message += f" (older than {older_than_minutes} minutes)"

        return jsonify({"message": message, "deleted_count": deleted_count}), 200
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/refresh-all-data", methods=["POST"])
@token_required
@require_admin
def refresh_all_data(current_user):
    """Refresh all locations, courts, and availability data (admin only)"""
    try:
        from app.models import Availability, Court, SearchRequest

        availability_service, padel_service = get_services()

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
                courts = (
                    availability_service.session.query(Court)
                    .filter(Court.location_id == location.id)
                    .all()
                )
                courts_deleted += len(courts)

                # Delete courts
                for court in courts:
                    availability_service.session.delete(court)
                availability_service.session.commit()

                # Re-add location to fetch fresh court data
                date_str = datetime.now().strftime("%Y-%m-%d")
                padel_service.add_location_by_slug(location.slug, date_str)

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


@admin_bp.route("/test-email", methods=["POST"])
@token_required
@require_admin
def test_email_notification(current_user):
    """Test email notification system (admin only)"""
    try:
        from app.email_service import email_service

        availability_service, _ = get_services()
        admin_user = availability_service.get_user_by_id(current_user)

        # Send test email to the admin
        test_courts = [
            {
                "location": "Test Location",
                "court": "Test Court 1",
                "date": "2025-11-22",
                "timeslot": "18:00 - 19:30",
                "price": "45.00 EUR",
                "provider": "PadelMate",
            }
        ]

        search_params = {
            "date": "2025-11-22",
            "start_time": "18:00",
            "end_time": "21:00",
            "duration_minutes": 90,
            "court_type": "all",
            "court_config": "double",
            "locations": ["Test Location"],
        }

        email_sent = email_service.send_court_found_notification(
            recipient_email=admin_user.email,
            recipient_name=admin_user.email.split("@")[0],
            search_order_id=999,
            courts_found=test_courts,
            search_params=search_params,
        )

        if email_sent:
            return (
                jsonify(
                    {"message": f"Test email sent successfully to {admin_user.email}"}
                ),
                200,
            )
        else:
            return jsonify({"error": "Failed to send test email"}), 500
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return jsonify({"error": str(e)}), 400


@admin_bp.route("/availability/fetch", methods=["POST"])
@token_required
@require_admin
def fetch_availability(current_user):
    """Fetch and store availability for all locations"""
    try:
        _, padel_service = get_services()
        data = request.get_json()
        date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        sport_id = data.get("sport_id", "PADEL")

        total_slots = padel_service.fetch_and_store_all_availability(
            date_str=date_str, sport_id=sport_id
        )
        return (
            jsonify(
                {
                    "message": "Availability fetched successfully",
                    "total_slots": total_slots,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error fetching availability: {str(e)}")
        return jsonify({"error": str(e)}), 400
