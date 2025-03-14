"""
Routes for serving static content from the frontend directory.
"""
from flask import Blueprint, request, jsonify, current_app, send_from_directory, redirect
from typing import Dict, Any

from backend.auth import is_authenticated

# Create a blueprint for static routes
static_bp = Blueprint('static', __name__)

@static_bp.route('/')
def index():
    """Home page route - serve index.html or redirect to login."""
    # If user isn't authenticated, redirect to login page
    if not is_authenticated():
        return redirect('/login.html')
    
    # Otherwise serve the index.html file
    return send_from_directory('../frontend', 'index.html')

@static_bp.route('/<path:path>')
def serve_static(path):
    """Serve static files from the frontend directory."""
    # Special case for login/signup pages - always accessible
    if path in ['login.html', 'signup.html']:
        return send_from_directory('../frontend', path)
    
    # Special case for login/signup related JS and CSS
    if path in ['login.js', 'login.css', 'signup.js']:
        return send_from_directory('../frontend', path)
    
    # For all other static files, check authentication
    if not is_authenticated() and path != 'styles.css':
        return redirect('/login.html')
    
    return send_from_directory('../frontend', path)