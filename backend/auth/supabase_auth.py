"""
Supabase Authentication module for GolfStats application.

This module provides authentication utilities using Supabase Auth.
"""
import os
import logging
from typing import Dict, Any, Optional, Tuple
from flask import session, request, abort, redirect, url_for

# Add the project root directory to Python path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.supabase_client import get_supabase

# Configure logging
logger = logging.getLogger(__name__)

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user's information.
    
    Returns:
        User information dictionary or None if not authenticated
    """
    user_session = session.get('user')
    if not user_session:
        # Check if token is in request headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            try:
                # Verify token with Supabase
                user = get_supabase().auth.get_user(token)
                return {
                    'id': user.id,
                    'email': user.email,
                    'name': user.user_metadata.get('full_name', ''),
                    'token': token
                }
            except Exception as e:
                logger.warning(f"Failed to verify token: {str(e)}")
                return None
        return None
        
    return user_session

def is_authenticated() -> bool:
    """
    Check if the current user is authenticated.
    
    Returns:
        True if authenticated, False otherwise
    """
    return get_current_user() is not None

def login_with_email(email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Login with email and password.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Tuple of (success, user_data)
    """
    try:
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        user = {
            'id': response.user.id,
            'email': response.user.email,
            'name': response.user.user_metadata.get('full_name', ''),
            'token': response.session.access_token
        }
        
        # Store in session
        session['user'] = user
        
        logger.info(f"User {email} logged in successfully")
        return True, user
    except Exception as e:
        logger.error(f"Login failed for {email}: {str(e)}")
        return False, None

def logout() -> bool:
    """
    Logout the current user.
    
    Returns:
        True if logout successful, False otherwise
    """
    try:
        # Clear session
        if 'user' in session:
            session.pop('user')
        
        # Invalidate token with Supabase
        get_supabase().auth.sign_out()
        
        logger.info("User logged out successfully")
        return True
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        return False
        
def sign_up(email: str, password: str, user_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Register a new user.
    
    Args:
        email: User email
        password: User password
        user_data: Additional user data
        
    Returns:
        Tuple of (success, user_data)
    """
    try:
        supabase = get_supabase()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_data
            }
        })
        
        user = {
            'id': response.user.id,
            'email': response.user.email,
            'name': response.user.user_metadata.get('full_name', ''),
            'token': response.session.access_token if response.session else None
        }
        
        logger.info(f"User {email} registered successfully")
        return True, user
    except Exception as e:
        logger.error(f"Registration failed for {email}: {str(e)}")
        return False, None

def require_auth(f):
    """
    Decorator to require authentication for routes.
    """
    def decorated(*args, **kwargs):
        if not is_authenticated():
            return abort(401, "Authentication required")
        return f(*args, **kwargs)
    return decorated