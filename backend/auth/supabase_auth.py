"""
Supabase Authentication module for GolfStats application.

This module provides authentication utilities using Supabase Auth.
"""
import os
import logging
import json
import time
import base64
from typing import Dict, Any, Optional, Tuple, Union
from flask import session, request, abort, redirect, url_for, g

# Add the project root directory to Python path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.supabase_client import get_supabase

# Configure logging
logger = logging.getLogger(__name__)

def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token with Supabase.
    
    Args:
        token: JWT token to verify
        
    Returns:
        The decoded payload if the token is valid, None otherwise
    """
    if not token:
        return None
        
    try:
        # Parse the JWT token
        parts = token.split('.')
        if len(parts) != 3:
            logger.warning("Invalid JWT format")
            return None
            
        # Decode the payload (middle part)
        payload_bytes = parts[1].encode('utf-8')
        # Add padding if needed
        payload_bytes += b'=' * (4 - len(payload_bytes) % 4) if len(payload_bytes) % 4 else b''
        
        try:
            payload = json.loads(base64.urlsafe_b64decode(payload_bytes).decode('utf-8'))
        except Exception as e:
            logger.warning(f"Failed to decode JWT payload: {str(e)}")
            return None
            
        # Check if the token has expired
        if 'exp' in payload and payload['exp'] < time.time():
            logger.warning("JWT token has expired")
            return None
            
        # Verify with Supabase - pass token to ensure RLS works properly
        supabase = get_supabase(token)
        user = supabase.auth.get_user(token)
        
        if user:
            # Store JWT payload for RLS policies
            payload['user_id'] = user.id
            return payload
            
    except Exception as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        
    return None

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user's information.
    
    Returns:
        User information dictionary or None if not authenticated
    """
    # Check if user is already stored in flask's g object (request context)
    if hasattr(g, 'user'):
        logger.info("Returning user from request context")
        return g.user
        
    # Check session first
    user_session = session.get('user')
    if user_session:
        # Store in request context
        logger.info("Returning user from session")
        g.user = user_session
        return user_session
        
    # Check if token is in request headers
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '')
        logger.info(f"Found Bearer token in header, length: {len(token)}")
        try:
            # Verify token with Supabase
            # Pass the token to get_supabase to set it on the client for RLS
            try:
                supabase = get_supabase(token)
                user_obj = supabase.auth.get_user()
                
                if user_obj and hasattr(user_obj, 'user'):
                    logger.info(f"Got user from Supabase: {user_obj.user.email}")
                    
                    # Get user preferences if they exist
                    from backend.database.supabase_data.user_preferences import get_user_preferences
                    preferences = get_user_preferences(user_obj.user.id, token) or {}
                    logger.info(f"Retrieved user preferences: {preferences}")
                    
                    user = {
                        'id': user_obj.user.id,
                        'email': user_obj.user.email,
                        'name': user_obj.user.user_metadata.get('full_name', ''),
                        'is_superuser': user_obj.user.app_metadata.get('is_superuser', False),
                        'token': token,
                        'preferences': preferences
                    }
                    
                    # If we have a display_name in preferences, use it
                    if preferences and 'display_name' in preferences:
                        user['name'] = preferences['display_name']
                        logger.info(f"Using display_name from preferences: {user['name']}")
                    
                    # Store in request context
                    g.user = user
                    logger.info(f"Successfully authenticated user {user['email']} with token")
                    return user
                else:
                    logger.warning("Token seems valid but user_obj is invalid")
            except Exception as e:
                logger.error(f"Error verifying token with Supabase: {str(e)}")
        except Exception as e:
            logger.warning(f"Failed to verify token: {str(e)}")
            return None
    else:
        logger.warning("No Authorization header with Bearer token found")
    
    logger.warning("No authenticated user found")
    return None

def get_authenticated_user() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Get the authenticated user and their token.
    
    This function attempts to retrieve the current authenticated user and their
    associated token from the request context, session, or Authorization header.
    
    Returns:
        A tuple of (user_info, token) where user_info is a dictionary containing
        user details and token is the JWT token string. Both will be None if
        authentication fails.
    """
    # Check if user is already stored in flask's g object (request context)
    if hasattr(g, 'user') and 'token' in g.user:
        return g.user, g.user['token']
        
    # Check session first
    user_session = session.get('user')
    if user_session and 'token' in user_session:
        # Store in request context
        g.user = user_session
        return user_session, user_session['token']
        
    # Check if token is in request headers
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '')
        try:
            # Verify token with Supabase
            # Pass the token to get_supabase to set it on the client for RLS
            try:
                supabase = get_supabase(token)
                user_obj = supabase.auth.get_user()
                if user_obj and hasattr(user_obj, 'user'):
                    user = {
                        'id': user_obj.user.id,
                        'email': user_obj.user.email,
                        'name': user_obj.user.user_metadata.get('full_name', ''),
                        'is_superuser': user_obj.user.app_metadata.get('is_superuser', False),
                        'token': token
                    }
                    # Store in request context
                    g.user = user
                    logger.info(f"Successfully authenticated user {user['email']} with token in get_authenticated_user")
                    return user, token
                else:
                    logger.warning("Token seems valid but user_obj is invalid in get_authenticated_user")
            except Exception as e:
                logger.error(f"Error verifying token with Supabase in get_authenticated_user: {str(e)}")
        except Exception as e:
            logger.warning(f"Failed to verify token in get_authenticated_user: {str(e)}")
            return None, None
    
    return None, None

def get_service_role_token() -> Optional[str]:
    """
    Get a service role token for admin operations.
    
    This is typically used to bypass RLS for administrative operations.
    
    Returns:
        Service role token or None if not available
    """
    try:
        # Try to get the service role token from Supabase
        supabase = get_supabase()
        # Note: This requires appropriate permissions and may not be available
        # in standard Supabase setups without custom configuration
        token = supabase.auth.create_client_token()
        return token
    except Exception as e:
        logger.warning(f"Failed to get service role token: {str(e)}")
        return None

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
            'is_superuser': response.user.app_metadata.get('is_superuser', False),
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
            'is_superuser': response.user.app_metadata.get('is_superuser', False),
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
    decorated.__name__ = f.__name__
    return decorated
    
def require_admin(f):
    """
    Decorator to require admin privileges for routes.
    """
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return abort(401, "Authentication required")
        if not user.get('is_superuser', False):
            return abort(403, "Admin privileges required")
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated
    
def request_password_reset(email: str) -> bool:
    """
    Request a password reset email to be sent to the user.
    
    Args:
        email: User email address
        
    Returns:
        True if password reset email sent successfully, False otherwise
    """
    try:
        supabase = get_supabase()
        
        # Use Supabase's password reset functionality
        response = supabase.auth.reset_password_email(email)
        
        logger.info(f"Password reset email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False
        
def update_user_password(token: str, new_password: str) -> bool:
    """
    Update a user's password with a reset token.
    
    Args:
        token: The recovery token from the reset email
        new_password: The new password to set
        
    Returns:
        True if password was updated successfully, False otherwise
    """
    try:
        supabase = get_supabase()
        
        # Update the user's password
        response = supabase.auth.update_user({
            "password": new_password
        }, token)
        
        logger.info("Password updated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to update password: {str(e)}")
        return False