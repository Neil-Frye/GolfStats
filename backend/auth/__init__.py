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
from .supabase_auth import get_current_user, is_authenticated, require_auth, verify_jwt

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
    
    # Initialize the Supabase client and ensure it's authenticated for admin operations
    from backend.database.supabase_client import get_supabase
    
    # Initialize the database migrations (including RLS policies)
    from backend.database.migrations import run_migrations
    
    # Flask 2.0+ removed before_first_request
    with app.app_context():
        try:
            # Run database migrations (including RLS policies)
            logger.info("Setting up Supabase authentication and RLS policies...")
            run_migrations()
            logger.info("Supabase setup complete.")
        except Exception as e:
            logger.error(f"Error setting up Supabase: {str(e)}")
    
    logger.info("Supabase authentication initialized")