"""
Custom Authentication for GolfStats application.

This module provides username/password authentication functionality.
"""
from typing import Dict, Any, Optional, Tuple
import re
import logging
import datetime
from flask import Blueprint, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

from backend.database.db_connection import get_db
from backend.models.user import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Blueprint for custom auth routes
custom_auth = Blueprint('custom_auth', __name__)

# Regular expression for validating email
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Regular expression for validating username
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')

# Password requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$')

def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        bool: True if email is valid
    """
    return bool(EMAIL_REGEX.match(email))

def validate_username(username: str) -> bool:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        bool: True if username is valid
    """
    return bool(USERNAME_REGEX.match(username))

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    
    if not PASSWORD_REGEX.match(password):
        return False, "Password must contain at least one lowercase letter, one uppercase letter, and one number"
    
    return True, None

@custom_auth.route('/register', methods=['POST'])
def register():
    """
    Register a new user with email and password.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "username": "username",
        "password": "Password123",
        "full_name": "Full Name"  # Optional
    }
    
    Returns:
        JSON response with registration result
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name')
    
    # Validate required fields
    if not email or not username or not password:
        return jsonify({"error": "Email, username and password are required"}), 400
    
    # Validate email format
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate username format
    if not validate_username(username):
        return jsonify({"error": "Username must be 3-20 characters and contain only letters, numbers, underscores, and hyphens"}), 400
    
    # Validate password strength
    is_valid, password_error = validate_password(password)
    if not is_valid:
        return jsonify({"error": password_error}), 400
    
    try:
        with get_db() as db:
            # Check if email already exists
            if db.query(User).filter(User.email == email).first():
                return jsonify({"error": "Email already registered"}), 400
            
            # Check if username already exists
            if db.query(User).filter(User.username == username).first():
                return jsonify({"error": "Username already taken"}), 400
            
            # Create new user
            new_user = User(
                email=email,
                username=username,
                hashed_password=generate_password_hash(password),
                full_name=full_name,
                auth_provider='custom',
                created_at=datetime.datetime.utcnow(),
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Set user session
            session['user'] = {
                'id': new_user.id,
                'email': new_user.email,
                'username': new_user.username,
                'full_name': new_user.full_name,
                'provider': 'custom'
            }
            session['authenticated'] = True
            
            logger.info(f"New user registered: {email}")
            
            return jsonify({
                "message": "Registration successful",
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "username": new_user.username
                }
            }), 201
            
    except SQLAlchemyError as e:
        logger.error(f"Database error during registration: {str(e)}")
        return jsonify({"error": "Registration failed due to a database error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        return jsonify({"error": "Registration failed"}), 500

@custom_auth.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user with email/username and password.
    
    Expected JSON payload:
    {
        "login": "user@example.com" or "username",
        "password": "Password123"
    }
    
    Returns:
        JSON response with login result
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    login = data.get('login')  # can be either email or username
    password = data.get('password')
    
    # Validate required fields
    if not login or not password:
        return jsonify({"error": "Login and password are required"}), 400
    
    try:
        with get_db() as db:
            # Try to find user by email or username
            user = db.query(User).filter(
                (User.email == login) | (User.username == login)
            ).first()
            
            if not user:
                return jsonify({"error": "Invalid login credentials"}), 401
            
            # Check if this is a Google OAuth user without a password
            if user.auth_provider == 'google' and not user.hashed_password:
                return jsonify({
                    "error": "This account uses Google Sign-In", 
                    "provider": "google"
                }), 401
            
            # Verify password
            if not user.hashed_password or not check_password_hash(user.hashed_password, password):
                return jsonify({"error": "Invalid login credentials"}), 401
            
            # Check if account is active
            if not user.is_active:
                return jsonify({"error": "Account is deactivated"}), 401
            
            # Set user session
            session['user'] = {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.full_name,
                'provider': 'custom'
            }
            session['authenticated'] = True
            
            logger.info(f"User logged in: {user.email}")
            
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username
                }
            }), 200
            
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}")
        return jsonify({"error": "Login failed due to a database error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        return jsonify({"error": "Login failed"}), 500

@custom_auth.route('/logout', methods=['POST'])
def logout():
    """
    Log out the current user.
    
    Returns:
        JSON response with logout result
    """
    session.pop('user', None)
    session.pop('authenticated', None)
    
    logger.info("User logged out")
    
    return jsonify({"message": "Logout successful"}), 200

@custom_auth.route('/password-reset-request', methods=['POST'])
def password_reset_request():
    """
    Request a password reset.
    
    Expected JSON payload:
    {
        "email": "user@example.com"
    }
    
    Returns:
        JSON response with request result
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    email = data.get('email')
    
    if not email or not validate_email(email):
        return jsonify({"error": "Valid email is required"}), 400
    
    # In a real implementation, this would:
    # 1. Generate a secure token
    # 2. Store the token with an expiration time
    # 3. Send an email with a reset link
    
    # For now, just log and return a success message
    logger.info(f"Password reset requested for: {email}")
    
    # Always return success to prevent email enumeration
    return jsonify({
        "message": "If an account exists with this email address, a password reset link will be sent."
    }), 200

@custom_auth.route('/change-password', methods=['POST'])
def change_password():
    """
    Change the current user's password.
    
    Expected JSON payload:
    {
        "current_password": "CurrentPass123",
        "new_password": "NewPass456"
    }
    
    Returns:
        JSON response with change result
    """
    # Check if user is authenticated
    if not session.get('authenticated') or not session.get('user'):
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({"error": "Current and new passwords are required"}), 400
    
    # Validate new password strength
    is_valid, password_error = validate_password(new_password)
    if not is_valid:
        return jsonify({"error": password_error}), 400
    
    user_id = session['user']['id']
    
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Verify current password
            if not user.hashed_password or not check_password_hash(user.hashed_password, current_password):
                return jsonify({"error": "Current password is incorrect"}), 401
            
            # Update password
            user.hashed_password = generate_password_hash(new_password)
            db.commit()
            
            logger.info(f"Password changed for user: {user.email}")
            
            return jsonify({"message": "Password changed successfully"}), 200
            
    except SQLAlchemyError as e:
        logger.error(f"Database error during password change: {str(e)}")
        return jsonify({"error": "Password change failed due to a database error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error during password change: {str(e)}")
        return jsonify({"error": "Password change failed"}), 500

def is_authenticated() -> bool:
    """
    Check if the user is currently authenticated.
    
    Returns:
        bool: True if user is authenticated
    """
    return session.get('authenticated', False) and 'user' in session

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the currently authenticated user's information.
    
    Returns:
        Dictionary with user information or None if not authenticated
    """
    if is_authenticated():
        return session.get('user')
    return None

def require_auth(view_func):
    """
    Decorator to require authentication for a view function.
    
    Args:
        view_func: The view function to protect
        
    Returns:
        Decorated function that checks authentication
    """
    def decorated(*args, **kwargs):
        if not is_authenticated():
            return jsonify({"error": "Authentication required"}), 401
        return view_func(*args, **kwargs)
    
    # Preserve the function name and docstring
    decorated.__name__ = view_func.__name__
    decorated.__doc__ = view_func.__doc__
    
    return decorated

def init_app(app):
    """
    Initialize the custom auth module with Flask application.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(custom_auth, url_prefix='/auth')