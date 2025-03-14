"""
API routes for golf shots management.
"""
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from backend.auth import require_auth, get_current_user
from backend.database.supabase_data.shots import (
    get_shots_for_round, add_shot
)
from backend.database.supabase_data.rounds import get_golf_round

# Create a blueprint for shots routes
shots_bp = Blueprint('shots', __name__, url_prefix='/api/rounds')

@shots_bp.route('/<int:round_id>/shots', methods=['POST'])
@require_auth
def add_shot_to_round(round_id):
    """Add a shot to a round."""
    user = get_current_user()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    # Check if round exists
    existing = get_golf_round(round_id)
    if not existing:
        return jsonify({"error": "Round not found"}), 404
    
    # Pass the token to satisfy RLS policies
    token = user.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
        
    shot_data = add_shot(round_id, data, token)
    
    if not shot_data:
        return jsonify({"error": "Failed to add shot"}), 500
        
    return jsonify({
        "message": "Shot added successfully",
        "shot": shot_data
    }), 201