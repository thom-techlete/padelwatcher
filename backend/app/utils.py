import logging
from datetime import date, time
from datetime import datetime as datetime_class
from functools import wraps

import jwt
from flask import jsonify, request

from app.config import SECRET_KEY

logger = logging.getLogger(__name__)


def serialize_model(model):
    """Convert a SQLAlchemy ORM model instance to a dictionary.

    Args:
        model: SQLAlchemy ORM model instance

    Returns:
        dict: Dictionary representation of the model
    """
    result = {}
    for column in model.__table__.columns:
        value = getattr(model, column.name)
        # Convert date/time objects to ISO format strings
        if isinstance(value, (date, time, datetime_class)):
            value = value.isoformat()
        result[column.name] = value
    return result


def serialize_models(models):
    """Convert a list of SQLAlchemy ORM model instances to a list of dictionaries.

    Args:
        models: List of SQLAlchemy ORM model instances

    Returns:
        list: List of dictionary representations
    """
    return [serialize_model(model) for model in models]


def get_provider(provider_name: str):
    """Dynamically instantiate and return a provider class by name.

    This function avoids circular imports by dynamically importing provider classes
    only when needed, rather than importing all providers at module load time.

    Args:
        provider_name: Name of the provider (e.g., 'playtomic')

    Returns:
        Instance of the provider class

    Raises:
        ValueError: If provider_name is not supported

    Example:
        provider = get_provider('playtomic')
        availability = provider.fetch_availability(tenant_id, date_str)
    """
    if provider_name == "playtomic":
        from app.courtfinder.playtomic import PlaytomicProvider

        return PlaytomicProvider()
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")


def validate_request_fields(required_fields: list[str] | tuple[str, ...]):
    """Decorator to validate required fields in JSON request body.

    Args:
        required_fields: List or tuple of required field names in the request JSON

    Returns:
        Decorator function that validates fields and returns 400 error if missing

    Example:
        @app.route('/api/search', methods=['POST'])
        @validate_request_fields(['date', 'start_time', 'end_time'])
        def search_courts():
            data = request.get_json()
            # data is guaranteed to have 'date', 'start_time', 'end_time'
    """

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json()

            # Check if JSON data exists
            if not data:
                logger.warning("Request body is empty or not JSON")
                return jsonify({"error": "Request body must be valid JSON"}), 400

            # Check if all required fields are present
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                logger.warning(f"Missing required fields: {missing_fields}")
                return (
                    jsonify(
                        {
                            "error": f"Missing required fields: {', '.join(missing_fields)}"
                        }
                    ),
                    400,
                )

            logger.debug(f"Request validation passed for fields: {required_fields}")
            return f(*args, **kwargs)

        return decorated

    return decorator


def token_required(f):
    """Authentication decorator for protected routes"""

    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow OPTIONS requests (preflight) to pass through
        if request.method == "OPTIONS":
            logger.debug("OPTIONS request - allowing through")
            return f(*args, **kwargs)

        token = None

        # Check for token in Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            logger.debug(f"Authorization header found: {auth_header[:20]}...")
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
                logger.debug(f"Extracted token: {token[:20]}...")
            except IndexError:
                logger.error("Token format invalid - could not split")
                return jsonify({"error": "Token format invalid"}), 401
        else:
            logger.warning("No Authorization header found in request")
            logger.debug(f"Request headers: {dict(request.headers)}")

        if not token:
            logger.error("Token is missing from request")
            return jsonify({"error": "Token is missing"}), 401

        try:
            logger.debug("Attempting to decode token with secret key")
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data["user_id"]
            logger.info(f"Token decoded successfully for user: {current_user}")
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            logger.error(f"Token is invalid: {str(e)}")
            return jsonify({"error": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    """Authorization decorator to require admin access"""

    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # Import here to avoid circular imports
        from app.services.user_service import user_service

        try:
            user = user_service.get_user_by_id(current_user)

            if not user:
                logger.error(f"User not found: {current_user}")
                return jsonify({"error": "User not found"}), 404

            if not user.is_admin:
                logger.warning(f"Admin access denied for user: {current_user}")
                return jsonify({"error": "Admin access required"}), 403

            logger.info(f"Admin access granted for user: {current_user}")
            return f(current_user, *args, **kwargs)

        except Exception as e:
            logger.error(f"Error checking admin status: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    return decorated
