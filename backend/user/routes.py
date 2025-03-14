"""
API routes for user management.
"""
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from backend.auth import require_auth, get_current_user

# Create a blueprint for user routes
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/', methods=['GET'])
@require_auth
def user_info():
    """Get current user information."""
    user_data = get_current_user()
    return jsonify({
        "authenticated": True,
        "user": user_data
    })