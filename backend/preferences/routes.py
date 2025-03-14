"""
API routes for user preferences management.
"""
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from backend.auth import require_auth, get_current_user
from backend.database.supabase_data.user_preferences import (
    get_user_preferences, update_user_preferences
)

# Create a blueprint for preferences routes
preferences_bp = Blueprint('preferences', __name__, url_prefix='/api/preferences')

@preferences_bp.route('/', methods=['GET'])
@require_auth
def get_preferences():
    """Get user preferences."""
    user = get_current_user()
    
    # Pass the token to satisfy RLS policies
    token = user.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    preferences = get_user_preferences(user['id'], token)
    
    return jsonify({
        "preferences": preferences
    })

@preferences_bp.route('/', methods=['PUT'])
@require_auth
def update_preferences():
    """Update user preferences."""
    user = get_current_user()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    # Pass the token to satisfy RLS policies
    token = user.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    preferences = update_user_preferences(user['id'], data, token)
    
    if not preferences:
        return jsonify({"error": "Failed to update preferences"}), 500
        
    return jsonify({
        "message": "Preferences updated successfully",
        "preferences": preferences
    })