"""
Google OAuth Authentication for GolfStats application.

This module provides functionality to authenticate users via Google OAuth 2.0.
"""
from typing import Dict, Any, Optional, Tuple
import os
import sys
import logging
from flask import Blueprint, session, redirect

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Blueprint for Google OAuth routes (will be empty or minimal)
google_auth = Blueprint('google_auth', __name__, url_prefix='')

@google_auth.route('/logout')
def logout():
    """
    Log out the Google authenticated user.
    
    Returns:
        Redirect to the application home page
    """
    # Clear user session data
    session.pop('google_oauth_credentials', None)
    session.pop('user', None)
    session.pop('authenticated', None)
    
    logger.info("User logged out from Google authentication")
    
    # Return to the login page
    return redirect('/login.html')

def init_app(app):
    """
    Initialize the Google OAuth module with Flask application.
    
    Args:
        app: Flask application instance
    """
    # No blueprint registration needed if frontend handles Supabase OAuth directly
    # If there are any backend routes related to Google OAuth, they would be registered here.
    # For now, we'll keep the blueprint but it won't have any routes.
    app.register_blueprint(google_auth, url_prefix='/auth/google')
    
    # Disable HTTPS requirement for local development
    if app.debug or app.testing:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
