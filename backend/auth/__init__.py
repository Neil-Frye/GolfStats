"""
Authentication package for GolfStats application.

This package provides authentication functionality via both custom username/password
authentication and Google OAuth.
"""
from typing import Dict, Any
import logging
from flask import Flask, session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_current_user() -> Dict[str, Any]:
    """
    Get the currently authenticated user from session.
    
    Returns:
        Dictionary containing user information or empty dict if not authenticated
    """
    return session.get('user', {})

def is_authenticated() -> bool:
    """
    Check if a user is currently authenticated.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    return session.get('authenticated', False)

def init_app(app: Flask) -> None:
    """
    Initialize authentication modules with Flask application.
    
    Args:
        app: Flask application instance
    """
    from .google_oauth import init_app as init_google_oauth
    from .custom_auth import init_app as init_custom_auth
    
    # Generate a secret key if not set
    if not app.secret_key:
        import os
        app.secret_key = os.urandom(24)
        logger.warning("Generated random secret key. For production, set a fixed secret key.")
    
    # Initialize auth modules
    init_google_oauth(app)
    init_custom_auth(app)
    
    logger.info("Authentication modules initialized")