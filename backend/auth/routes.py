"""
Authentication routes for GolfStats application.

This module provides routes for user authentication using Supabase.
"""
import logging
import os
from typing import Dict, Any
from flask import Blueprint, request, jsonify, session, redirect, url_for

from .supabase_auth import login_with_email, logout, sign_up, get_current_user, is_authenticated, verify_jwt
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
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    token = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '')
        
    # Verify the JWT token first to ensure RLS will work
    if token:
        jwt_payload = verify_jwt(token)
        logger.info(f"JWT verification result: {bool(jwt_payload)}")
        if not jwt_payload:
            logger.warning("Invalid JWT token provided")
            return jsonify({"authenticated": False, "error": "Invalid token"}), 401
    
    # Get current user with validated token
    user = get_current_user()
    if user:
        # Log the user ID for debugging
        logger.info(f"Current authenticated user ID: {user.get('id')}, type: {type(user.get('id'))}")
        return jsonify({
            "authenticated": True, 
            "user": user,
            "token_valid": True if token else False
        }), 200
    else:
        logger.warning("No authenticated user found")
        return jsonify({"authenticated": False}), 401
        
@auth_bp.route('/profile', methods=['POST'])
def update_profile():
    """Update user profile information."""
    import os
    import uuid
    from werkzeug.utils import secure_filename
    from backend.database.supabase_data.user_preferences import update_user_preferences, get_user_preferences
    
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401
    
    # Enhanced logging for debugging request
    logger.info(f"Profile update request received. Form data: {request.form}")
    logger.info(f"Files in request: {request.files.keys() if request.files else 'None'}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Get token from Authorization header for RLS
    auth_header = request.headers.get('Authorization')
    token = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '')
        logger.info(f"Bearer token extracted, length: {len(token)}")
    else:
        logger.warning("No Bearer token found in Authorization header")
    
    # Verify the JWT token first to ensure RLS will work
    if token:
        jwt_payload = verify_jwt(token)
        logger.info(f"JWT verification result: {bool(jwt_payload)}")
        if not jwt_payload:
            logger.warning("Invalid JWT token provided")
            return jsonify({"error": "Invalid token"}), 401
    else:
        logger.warning("No token available for verification")
    
    # Get current user with validated token
    user = get_current_user()
    if not user:
        logger.warning("No authenticated user found")
        return jsonify({"error": "Authentication required"}), 401
        
    user_id = user['id']
    logger.info(f"Processing profile update for user_id: {user_id}")
    
    # Handle form data for file uploads
    if request.files and 'profile_image' in request.files:
        profile_image = request.files['profile_image']
        logger.info(f"Profile image found: {profile_image.filename if profile_image else 'None'}")
        
        if profile_image and profile_image.filename:
            # Secure filename and generate unique name
            filename = secure_filename(profile_image.filename)
            unique_filename = f"{user_id}_{uuid.uuid4()}_{filename}"
            logger.info(f"Generated unique filename: {unique_filename}")
            
            # Ensure upload directory exists - use absolute path to be safe
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            upload_folder = os.path.join(base_dir, 'frontend', 'uploads', 'profiles')
            logger.info(f"Creating upload directory at: {upload_folder}")
            
            try:
                os.makedirs(upload_folder, exist_ok=True)
                logger.info(f"Upload directory created/verified")
                
                # Save file
                file_path = os.path.join(upload_folder, unique_filename)
                logger.info(f"Saving file to: {file_path}")
                profile_image.save(file_path)
                logger.info(f"File saved successfully")
                
                # Generate URL and verify file exists
                avatar_url = f"/uploads/profiles/{unique_filename}"
                if os.path.exists(file_path):
                    logger.info(f"File verified at {file_path}, size: {os.path.getsize(file_path)} bytes")
                else:
                    logger.error(f"File save failed - file does not exist at {file_path}")
                    return jsonify({"error": "Failed to save profile image"}), 500
                
                # Update user preferences with new avatar URL - pass token for RLS
                current_prefs = get_user_preferences(user_id, token) or {}
                current_prefs['avatar_url'] = avatar_url
                
                # Update in database - pass token for RLS
                logger.info(f"Updating preferences with new avatar_url: {avatar_url}")
                success = update_user_preferences(user_id, current_prefs, token)
                if not success:
                    logger.error("Failed to update profile image in preferences")
                    return jsonify({"error": "Failed to update profile image"}), 500
                logger.info("Profile image updated successfully")
            except Exception as e:
                logger.error(f"Error handling profile image: {str(e)}")
                return jsonify({"error": f"Error handling profile image: {str(e)}"}), 500
    
    # Update other profile fields - always include all form fields
    preferences_data = {}
    
    # Always include all form fields, even if empty
    for field in ['handicap', 'phone', 'home_course']:
        if field in request.form:
            preferences_data[field] = request.form.get(field) or ''
            logger.info(f"Setting {field} to: '{preferences_data[field]}'")
    
    # Update user preferences if we have any form data
    if preferences_data:
        logger.info(f"Updating preferences with data: {preferences_data}")
        
        try:
            # Get existing preferences - pass token for RLS
            current_prefs = get_user_preferences(user_id, token) or {}
            logger.info(f"Current preferences before update: {current_prefs}")
            
            # Merge with new preferences
            current_prefs.update(preferences_data)
            logger.info(f"Merged preferences: {current_prefs}")
            
            # Update in database - pass token for RLS
            success = update_user_preferences(user_id, current_prefs, token)
            if not success:
                logger.error("Failed to update preferences in database")
                return jsonify({"error": "Failed to update preferences"}), 500
            logger.info("Preferences updated successfully")
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            return jsonify({"error": f"Error updating preferences: {str(e)}"}), 500
    
    # Update name in preferences for display purposes
    # Always update name field, even if empty
    try:
        logger.info(f"Processing name update: '{request.form.get('name')}'")
        # Get existing preferences - pass token for RLS
        current_prefs = get_user_preferences(user_id, token) or {}
        
        # Always update the display_name, even if empty
        if 'name' in request.form:
            current_prefs['display_name'] = request.form.get('name') or ''
            logger.info(f"Setting display_name to: '{current_prefs['display_name']}'")
            
            # Update in database - pass token for RLS
            success = update_user_preferences(user_id, current_prefs, token)
            if not success:
                logger.error("Failed to update display name in preferences")
                return jsonify({"error": "Failed to update name preference"}), 500
            logger.info("Display name updated successfully")
    except Exception as e:
        logger.error(f"Error updating display name: {str(e)}")
        return jsonify({"error": f"Error updating display name: {str(e)}"}), 500
            
    # TODO: Update name and email in Supabase Auth using admin API
    # This requires admin privileges or service_role token
    
    # Get updated user data
    try:
        updated_user = get_current_user()
        logger.info(f"Got updated user: {updated_user is not None}")
        
        # Get fresh preferences directly
        if updated_user:
            # Reload preferences to ensure we have the latest data
            fresh_prefs = get_user_preferences(user_id, token) or {}
            logger.info(f"Fresh preferences: {fresh_prefs}")
            
            # Merge preferences into user object
            updated_user['preferences'] = fresh_prefs
            
            # If we stored display name in preferences, use it for the response
            if 'display_name' in fresh_prefs:
                updated_user['name'] = fresh_prefs['display_name']
                logger.info(f"Set display name in response to: '{updated_user['name']}'")
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": updated_user
        }), 200
    except Exception as e:
        logger.error(f"Error preparing response: {str(e)}")
        return jsonify({
            "message": "Profile updated but error preparing response data",
            "error": str(e)
        }), 200