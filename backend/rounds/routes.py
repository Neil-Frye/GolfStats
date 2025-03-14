"""
API routes for golf rounds management.
"""
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from backend.auth import require_auth, get_current_user
from backend.database.supabase_data.rounds import (
    get_golf_rounds, get_golf_round, create_golf_round, 
    update_golf_round, delete_golf_round
)

# Create a blueprint for rounds routes
rounds_bp = Blueprint('rounds', __name__, url_prefix='/api/rounds')

@rounds_bp.route('/', methods=['GET'])
@require_auth
def list_rounds():
    """Get rounds for current user."""
    user = get_current_user()
    rounds = get_golf_rounds(user['id'])
    
    return jsonify({
        "rounds": rounds
    })

@rounds_bp.route('/<int:round_id>', methods=['GET'])
@require_auth
def get_round(round_id):
    """Get a specific round with all shot data."""
    from backend.database.supabase_data.shots import get_shots_for_round
    
    user = get_current_user()
    
    # Pass the token to satisfy RLS policies
    token = user.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    round_data = get_golf_round(round_id, token)
    if not round_data:
        return jsonify({"error": "Round not found"}), 404
        
    # Get shots for this round
    shots = get_shots_for_round(round_id, token)
    
    # Add shots to round data
    round_data['shots'] = shots
    
    return jsonify({
        "round": round_data
    })

@rounds_bp.route('/', methods=['POST'])
@require_auth
def add_round():
    """Create a new round."""
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
    
    round_data = create_golf_round(user['id'], data, token)
    
    if not round_data:
        return jsonify({"error": "Failed to create round"}), 500
        
    return jsonify({
        "message": "Round created successfully",
        "round": round_data
    }), 201

@rounds_bp.route('/<int:round_id>', methods=['PUT'])
@require_auth
def update_round(round_id):
    """Update a round."""
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
        
    round_data = update_golf_round(round_id, data, token)
    
    if not round_data:
        return jsonify({"error": "Failed to update round"}), 500
        
    return jsonify({
        "message": "Round updated successfully",
        "round": round_data
    })

@rounds_bp.route('/<int:round_id>', methods=['DELETE'])
@require_auth
def delete_round(round_id):
    """Delete a round."""
    user = get_current_user()
    
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
        
    success = delete_golf_round(round_id, token)
    
    if not success:
        return jsonify({"error": "Failed to delete round"}), 500
        
    return jsonify({
        "message": "Round deleted successfully"
    })