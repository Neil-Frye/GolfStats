"""
Authentication routes for GolfStats application.

This module provides routes for user authentication using Supabase.
"""
import logging
from typing import Dict, Any
from flask import Blueprint, request, jsonify, session, redirect, url_for

from .supabase_auth import login_with_email, logout, sign_up, get_current_user, is_authenticated

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login via email/password."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400
    
    success, user = login_with_email(data['email'], data['password'])
    
    if success:
        return jsonify({"message": "Login successful", "user": user}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Handle user registration."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400
    
    # Additional user data
    user_data = {
        "full_name": data.get('name', ''),
    }
    
    success, user = sign_up(data['email'], data['password'], user_data)
    
    if success:
        return jsonify({"message": "Signup successful", "user": user}), 201
    else:
        return jsonify({"error": "Registration failed"}), 400

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    """Handle user logout."""
    if is_authenticated():
        success = logout()
        if success:
            return jsonify({"message": "Logout successful"}), 200
        else:
            return jsonify({"error": "Logout failed"}), 500
    else:
        return jsonify({"message": "Not logged in"}), 200

@auth_bp.route('/me', methods=['GET'])
def me():
    """Get current user information."""
    user = get_current_user()
    if user:
        return jsonify({"authenticated": True, "user": user}), 200
    else:
        return jsonify({"authenticated": False}), 401