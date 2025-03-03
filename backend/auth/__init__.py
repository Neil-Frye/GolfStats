"""
Authentication package for GolfStats application.

This package provides authentication functionality via Supabase Auth.
"""
from typing import Dict, Any, Optional
import logging
from flask import Flask, session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import from supabase_auth module to expose key functions at package level
from .supabase_auth import get_current_user, is_authenticated, require_auth

def init_app(app: Flask) -> None:
    """
    Initialize authentication modules with Flask application.
    
    Args:
        app: Flask application instance
    """
    # Generate a secret key if not set
    if not app.secret_key:
        import os
        app.secret_key = os.urandom(24)
        logger.warning("Generated random secret key. For production, set a fixed secret key.")
    
    # Register authentication routes
    from . import routes
    
    # Register the auth blueprint with the app
    app.register_blueprint(routes.auth_bp)
    
    logger.info("Supabase authentication initialized")