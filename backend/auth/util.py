"""
Authentication utilities for the GolfStats application.
"""
from flask import request
from typing import Optional

def get_auth_token() -> Optional[str]:
    """
    Extract authentication token from request.
    
    Returns:
        The authentication token from the user session or Authorization header,
        or None if no token was found.
    """
    # Try to get token from user session
    from backend.auth import get_current_user
    
    user = get_current_user()
    token = user.get('token') if user else None
    
    # If no token in session, try Authorization header
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            
    return token