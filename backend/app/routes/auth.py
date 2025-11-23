"""Authentication routes blueprint"""
from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import logging
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = logging.getLogger(__name__)


def get_services():
    """Import services here to avoid circular imports"""
    from app.services import AvailabilityService
    return AvailabilityService()


def token_required(f):
    """Authentication decorator for protected routes"""
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
                return jsonify({'error': 'Token format invalid'}), 401
        else:
            logger.warning("No Authorization header found in request")
            logger.debug(f"Request headers: {dict(request.headers)}")
        
        if not token:
            logger.error("Token is missing from request")
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            from app.config import SECRET_KEY
            logger.debug(f"Attempting to decode token with secret key")
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = data['user_id']
            logger.info(f"Token decoded successfully for user: {current_user}")
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            logger.error(f"Token is invalid: {str(e)}")
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (requires admin approval)"""
    try:
        availability_service = get_services()
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        # Validate password length
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        existing_user = availability_service.get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'An account with this email already exists'}), 409
        
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
            password_hash=generate_password_hash(password),
            user_id=user_id
        )
        
        return jsonify({
            'message': 'User registered successfully. Please wait for admin approval.',
            'user_id': user.user_id
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed. Please try again later.'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and get JWT token (only for approved users)"""
    try:
        availability_service = get_services()
        from app.config import SECRET_KEY, JWT_EXPIRATION_HOURS
        
        data = request.get_json()
        
        logger.info(f"Login attempt for email: {data.get('email') if data else 'None'}")
        
        if not data or not data.get('email') or not data.get('password'):
            logger.warning("Login failed: Email and password required")
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']
        
        # Authenticate user (checks approval status)
        user_info = availability_service.authenticate_user(email, password)
        
        if not user_info:
            logger.warning(f"Login failed for {email}: Invalid credentials or not approved")
            return jsonify({'error': 'Invalid credentials or account not approved'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_info['user_id'],
            'email': user_info['email'],
            'is_admin': user_info['is_admin'],
            'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
        }, SECRET_KEY, algorithm='HS256')
        
        logger.info(f"Login successful for {email} (user_id: {user_info['user_id']})")
        logger.debug(f"Generated token: {token[:20]}...")
        
        return jsonify({
            'token': token,
            'user_id': user_info['user_id'],
            'email': user_info['email'],
            'is_admin': user_info['is_admin'],
            'is_approved': True,
            'expires_in': JWT_EXPIRATION_HOURS * 3600
        }), 200
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed. Please try again later.'}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information"""
    try:
        availability_service = get_services()
        logger.info(f"Getting current user info for: {current_user}")
        user = availability_service.get_user_by_id(current_user)
        if not user:
            logger.error(f"User not found: {current_user}")
            return jsonify({'error': 'User not found'}), 404
        
        logger.debug(f"Returning user info for: {user.email}")
        return jsonify({
            'id': user.id,
            'email': user.email,
            'username': user.user_id,
            'is_admin': user.is_admin,
            'is_approved': user.approved,
            'created_at': str(user.created_at)
        }), 200
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user information'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile information"""
    try:
        availability_service = get_services()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user = availability_service.update_user_profile(
            user_id=current_user,
            email=data.get('email')
        )
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
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
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500


@auth_bp.route('/password', methods=['PUT'])
@token_required
def update_password(current_user):
    """Update user password"""
    try:
        availability_service = get_services()
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        user = availability_service.update_user_password(
            user_id=current_user,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'message': 'Password updated successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Password update error: {str(e)}")
        return jsonify({'error': 'Failed to update password'}), 500
