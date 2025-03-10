"""
Authentication routes for GolfStats application.

This module provides routes for user authentication using Supabase.
"""
import logging
import os
from typing import Dict, Any
from flask import Blueprint, request, jsonify, session, redirect, url_for

from .supabase_auth import login_with_email, logout, sign_up, get_current_user, is_authenticated
from .crypto_utils import encrypt_value, decrypt_value

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

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
        # Automatically log the user in after successful signup
        session['user'] = user
        return jsonify({"message": "Signup successful", "user": user}), 201
    else:
        return jsonify({"error": "Registration failed. Email may already be in use."}), 400

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
        
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password_route():
    """Handle password reset request."""
    from .supabase_auth import request_password_reset
    
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({"error": "Email is required"}), 400
    
    email = data.get('email')
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({"error": "Invalid email format"}), 400
    
    success = request_password_reset(email)
    
    if success:
        return jsonify({"message": "Password reset email sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send password reset email"}), 500

@auth_bp.route('/reset-password-confirm', methods=['POST'])
def reset_password_confirm_route():
    """Handle password reset confirmation with token."""
    from .supabase_auth import update_user_password
    
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization token is required"}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    # Get password from request body
    data = request.get_json()
    if not data or not data.get('password'):
        return jsonify({"error": "New password is required"}), 400
    
    password = data.get('password')
    
    # Validate password length
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    success = update_user_password(token, password)
    
    if success:
        return jsonify({"message": "Password has been reset successfully"}), 200
    else:
        return jsonify({"error": "Failed to reset password. Token may be invalid or expired."}), 401

@auth_bp.route('/me', methods=['GET'])
def me():
    """Get current user information."""
    user = get_current_user()
    if user:
        return jsonify({"authenticated": True, "user": user}), 200
    else:
        return jsonify({"authenticated": False}), 401
        
@auth_bp.route('/profile', methods=['POST'])
def update_profile():
    """Update user profile information."""
    import os
    import uuid
    from werkzeug.utils import secure_filename
    from backend.database.supabase_data import update_user_preferences, get_user_preferences
    
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401
    
    user = get_current_user()
    user_id = user['id']
    
    # Handle form data for file uploads
    if request.files and 'profile_image' in request.files:
        profile_image = request.files['profile_image']
        
        if profile_image and profile_image.filename:
            # Secure filename and generate unique name
            filename = secure_filename(profile_image.filename)
            unique_filename = f"{user_id}_{uuid.uuid4()}_{filename}"
            
            # Ensure upload directory exists
            upload_folder = os.path.join('frontend', 'uploads', 'profiles')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_folder, unique_filename)
            profile_image.save(file_path)
            
            # Generate URL
            avatar_url = f"/uploads/profiles/{unique_filename}"
            
            # Update user preferences with new avatar URL
            current_prefs = get_user_preferences(user_id) or {}
            current_prefs['avatar_url'] = avatar_url
            
            # Update in database
            success = update_user_preferences(user_id, current_prefs)
            if not success:
                return jsonify({"error": "Failed to update profile image"}), 500
    
    # Update other profile fields
    preferences_data = {}
    if request.form.get('handicap'):
        preferences_data['handicap'] = request.form.get('handicap')
    if request.form.get('phone'):
        preferences_data['phone'] = request.form.get('phone')
    if request.form.get('home_course'):
        preferences_data['home_course'] = request.form.get('home_course')
    
    # Update user preferences if we have data
    if preferences_data:
        # Get existing preferences
        current_prefs = get_user_preferences(user_id) or {}
        
        # Merge with new preferences
        current_prefs.update(preferences_data)
        
        # Update in database
        success = update_user_preferences(user_id, current_prefs)
        if not success:
            return jsonify({"error": "Failed to update preferences"}), 500
    
    # TODO: Update name and email in Supabase Auth
    # This would typically be handled by Supabase Auth APIs
    
    # Get updated user data
    updated_user = get_current_user()
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": updated_user
    }), 200