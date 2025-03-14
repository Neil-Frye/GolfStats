"""
API routes for golf clubs management.
"""
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from backend.auth import require_auth, get_current_user
from backend.database.supabase_data.clubs import (
    get_user_clubs, get_club, create_club, update_club, delete_club
)

# Create a blueprint for clubs routes
clubs_bp = Blueprint('clubs', __name__, url_prefix='/api/clubs')

@clubs_bp.route('/', methods=['GET'])
@require_auth
def get_clubs():
    """Get clubs for current user."""
    user = get_current_user()
    
    # Pass the token to satisfy RLS policies
    token = user.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    clubs = get_user_clubs(user['id'], token)
    
    return jsonify({
        "clubs": clubs
    })

@clubs_bp.route('/<int:club_id>', methods=['GET'])
@require_auth
def get_club_by_id(club_id):
    """Get a specific club."""
    user = get_current_user()
    
    # Pass the token to satisfy RLS policies
    token = user.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    club_data = get_club(club_id, token)
    if not club_data:
        return jsonify({"error": "Club not found"}), 404
        
    return jsonify({
        "club": club_data
    })

@clubs_bp.route('/', methods=['POST'])
@require_auth
def add_club():
    """Create a new club."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['name', 'club_type']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Pass the token to satisfy RLS policies
        token = user.get('token')
        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '')
        
        # Log the request data for debugging
        current_app.logger.info(f"Creating club with data: {data}")
        current_app.logger.info(f"User ID: {user['id']}")
                
        club_data = create_club(user['id'], data, token)
        
        if not club_data:
            return jsonify({"error": "Database error: Failed to create club"}), 500
            
        return jsonify({
            "message": "Club created successfully",
            "club": club_data
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error creating club: {str(e)}")
        current_app.logger.exception(e)  # Log full exception with traceback
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@clubs_bp.route('/<int:club_id>', methods=['PUT'])
@require_auth
def update_club_by_id(club_id):
    """Update a club."""
    user = get_current_user()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    # Check if club exists
    existing = get_club(club_id)
    if not existing:
        return jsonify({"error": "Club not found"}), 404
    
    # Pass the token to satisfy RLS policies
    token = user.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
        
    club_data = update_club(club_id, data, token)
    
    if not club_data:
        return jsonify({"error": "Failed to update club"}), 500
        
    return jsonify({
        "message": "Club updated successfully",
        "club": club_data
    })

@clubs_bp.route('/<int:club_id>', methods=['DELETE'])
@require_auth
def delete_club_by_id(club_id):
    """Delete a club."""
    user = get_current_user()
    
    # Check if club exists
    existing = get_club(club_id)
    if not existing:
        return jsonify({"error": "Club not found"}), 404
    
    # Pass the token to satisfy RLS policies
    token = user.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
        
    success = delete_club(club_id, token)
    
    if not success:
        return jsonify({"error": "Failed to delete club"}), 500
        
    return jsonify({
        "message": "Club deleted successfully"
    })