"""
Authentication module for GolfStats application.

This module provides authentication utilities using Supabase Auth.
"""
from backend.auth.supabase_auth import (
    login_with_email,
    logout,
    sign_up,
    get_current_user,
    is_authenticated,
    require_auth,
    get_authenticated_user,
    verify_jwt
)

from .crypto_utils import encrypt_value, decrypt_value

def init_app(app):
    """Initialize authentication for the Flask app."""
    # Import and register Google OAuth if configured
    try:
        from .google_oauth import google_auth, is_configured
        if is_configured():
            app.register_blueprint(google_auth, url_prefix='/api/auth/google')
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Google OAuth blueprint registered at /api/auth/google")
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Google OAuth not configured, skipping blueprint registration")
    except ImportError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not import Google OAuth module: {e}")