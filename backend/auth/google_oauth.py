"""
Google OAuth Authentication for GolfStats application.

This module provides functionality to authenticate users via Google OAuth 2.0.
"""
from typing import Dict, Any, Optional, Tuple
import os
import sys
import json
import logging
import requests
from flask import Blueprint, request, redirect, session, url_for, current_app
import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.config import config
from backend.database.db_connection import get_db
from backend.models.user import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure OAuth2 access scopes
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

# Optional Google Sheets API scope
if config['google']['sheets']['api_key']:
    SCOPES.append('https://www.googleapis.com/auth/spreadsheets.readonly')

# Create Blueprint for Google OAuth routes
google_auth = Blueprint('google_auth', __name__)

def is_configured() -> bool:
    """
    Check if Google OAuth is properly configured.
    
    Returns:
        bool: True if Google OAuth credentials are configured
    """
    return bool(
        config['google']['oauth']['client_id'] and 
        config['google']['oauth']['client_secret']
    )

def get_oauth_flow(redirect_uri: Optional[str] = None) -> google_auth_oauthlib.flow.Flow:
    """
    Create an OAuth2 flow instance to manage the OAuth 2.0 Authorization Grant Flow.
    
    Args:
        redirect_uri: The OAuth redirect URI. If None, uses the configured default.
        
    Returns:
        Flow instance for OAuth authentication
    """
    client_config = {
        "web": {
            "client_id": config['google']['oauth']['client_id'],
            "client_secret": config['google']['oauth']['client_secret'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                redirect_uri or config['google']['oauth']['redirect_uri']
            ]
        }
    }
    
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri or config['google']['oauth']['redirect_uri']
    )
    
    return flow

def credentials_to_dict(credentials: google.oauth2.credentials.Credentials) -> Dict[str, Any]:
    """
    Convert Google OAuth credentials to a dictionary for storage.
    
    Args:
        credentials: Google OAuth credentials object
        
    Returns:
        Dictionary of credential information
    """
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_user_info(credentials: google.oauth2.credentials.Credentials) -> Dict[str, Any]:
    """
    Get Google user information using OAuth credentials.
    
    Args:
        credentials: Google OAuth credentials
        
    Returns:
        Dictionary containing user information
    """
    try:
        oauth2_service = build('oauth2', 'v2', credentials=credentials)
        user_info = oauth2_service.userinfo().get().execute()
        return user_info
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        return {}

# Routes for Google OAuth
@google_auth.route('/login')
def login():
    """
    Start the Google OAuth login flow.
    
    Returns:
        Redirect to Google's OAuth authorization page
    """
    if not is_configured():
        logger.error("Google OAuth not configured properly")
        return {"error": "Google OAuth not configured"}, 500
    
    # Create flow instance
    flow = get_oauth_flow()
    
    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    # Store the state in the session for later validation
    session['google_auth_state'] = state
    
    # Redirect to Google's OAuth page
    return redirect(authorization_url)

@google_auth.route('/callback')
def callback():
    """
    Handle the Google OAuth callback.
    
    Returns:
        Redirect to the application home page
    """
    if not is_configured():
        logger.error("Google OAuth not configured properly")
        return {"error": "Google OAuth not configured"}, 500
    
    # Verify state matches
    state = session.get('google_auth_state')
    if state is None or state != request.args.get('state'):
        logger.error("State mismatch in OAuth callback")
        return {"error": "Invalid state parameter"}, 400
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        logger.error("No authorization code received")
        return {"error": "No authorization code received"}, 400
    
    # Create flow instance
    flow = get_oauth_flow()
    
    # Exchange authorization code for tokens
    flow.fetch_token(code=code)
    
    # Get credentials from the flow
    credentials = flow.credentials
    
    # Get user info
    user_info = get_user_info(credentials)
    
    # Store credentials and user info in session
    session['google_oauth_credentials'] = credentials_to_dict(credentials)
    
    # Save or update user in database
    oauth_data = {
        'id': user_info.get('id'),
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture'),
        'provider': 'google'
    }
    
    with get_db() as db:
        # Check if user already exists
        user = db.query(User).filter(User.email == user_info.get('email')).first()
        
        if user:
            # Update existing user
            user.oauth_id = user_info.get('id')
            user.oauth_access_token = credentials.token
            user.oauth_refresh_token = credentials.refresh_token
            user.profile_picture = user_info.get('picture')
            user.auth_provider = 'google'
        else:
            # Create new user
            user = User.from_oauth(oauth_data)
            user.oauth_access_token = credentials.token
            user.oauth_refresh_token = credentials.refresh_token
            db.add(user)
        
        db.commit()
        
        # Store user data in session
        session['user'] = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'profile_picture': user.profile_picture,
            'provider': 'google'
        }
        session['authenticated'] = True
    
    logger.info(f"User authenticated via Google: {user_info.get('email')}")
    
    # Return to the main page
    return redirect(url_for('index'))

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
    
    # Return to the main page
    return redirect(url_for('index'))

def is_authenticated() -> bool:
    """
    Check if the user is currently authenticated via Google.
    
    Returns:
        bool: True if user is authenticated
    """
    return session.get('authenticated', False) and 'google_oauth_credentials' in session

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the currently authenticated user's information.
    
    Returns:
        Dictionary with user information or None if not authenticated
    """
    if is_authenticated():
        return session.get('user')
    return None

def refresh_credentials() -> Tuple[bool, Optional[str]]:
    """
    Refresh OAuth credentials if they're expired.
    
    Returns:
        Tuple of (success, error_message)
    """
    if 'google_oauth_credentials' not in session:
        return False, "No credentials to refresh"
    
    try:
        credentials = google.oauth2.credentials.Credentials(
            **session['google_oauth_credentials']
        )
        
        # Refresh token if expired
        if credentials.expired:
            credentials.refresh(Request())
            session['google_oauth_credentials'] = credentials_to_dict(credentials)
            logger.info("OAuth credentials refreshed successfully")
        
        return True, None
    except Exception as e:
        logger.error(f"Error refreshing credentials: {str(e)}")
        return False, str(e)

def init_app(app):
    """
    Initialize the Google OAuth module with Flask application.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(google_auth, url_prefix='/auth/google')
    
    # Disable HTTPS requirement for local development
    if app.debug or app.testing:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'