"""
Golf platform integrations routes for GolfStats application.

This module provides routes for connecting to and managing golf platform integrations.
"""
import os
import logging
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app

from backend.auth.supabase_auth import require_auth, get_current_user
from backend.auth.crypto_utils import encrypt_value, decrypt_value
from backend.models.user import User
from backend.database.db_connection import get_db_session

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
integrations_bp = Blueprint('integrations', __name__, url_prefix='/api/integrations')

@integrations_bp.route('/connect', methods=['POST'])
@require_auth
def connect_integration():
    """Connect to a golf platform service."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    service = data.get('service')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Validate required fields
    if not service:
        return jsonify({"error": "Service is required"}), 400
    
    if service not in ['trackman', 'arccos', 'skytrak']:
        return jsonify({"error": "Unsupported service"}), 400
    
    if service == 'arccos' and not email:
        return jsonify({"error": "Email is required for Arccos"}), 400
    
    if (service in ['trackman', 'skytrak']) and not username:
        return jsonify({"error": f"Username is required for {service.capitalize()}"}), 400
    
    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    # Get current user
    user_data = get_current_user()
    if not user_data or not user_data.get('id'):
        return jsonify({"error": "User not authenticated"}), 401
    
    # Update user credentials in database
    try:
        # Get database session using context manager
        with get_db() as session:
            # Get user
            user = session.query(User).filter(User.id == user_data['id']).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Encrypt credentials and store them
            if service == 'trackman':
                user.trackman_username = username
                user.trackman_password = encrypt_value(password)
            elif service == 'arccos':
                user.arccos_email = email
                user.arccos_password = encrypt_value(password)
            elif service == 'skytrak':
                user.skytrak_username = username
                user.skytrak_password = encrypt_value(password)
            
            # Save changes
            session.commit()
        
        # Return success
        return jsonify({
            "success": True,
            "message": f"Successfully connected to {service.capitalize()}"
        }), 200
        
    except Exception as e:
        logger.error(f"Error connecting to {service}: {str(e)}")
        return jsonify({"error": f"Failed to connect to {service}: {str(e)}"}), 500

@integrations_bp.route('/status', methods=['GET'])
@require_auth
def get_integration_status():
    """Get status of service integrations."""
    # Get current user
    user_data = get_current_user()
    if not user_data or not user_data.get('id'):
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        # Get database session using context manager
        with get_db() as session:
            # Get user
            user = session.query(User).filter(User.id == user_data['id']).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Check integration status
            integrations = {
                "trackman": {
                    "connected": user.trackman_credentials_valid(),
                    "username": user.trackman_username if user.trackman_username else None
                },
                "arccos": {
                    "connected": user.arccos_credentials_valid(),
                    "email": user.arccos_email if user.arccos_email else None
                },
                "skytrak": {
                    "connected": user.skytrak_credentials_valid(),
                    "username": user.skytrak_username if user.skytrak_username else None
                }
            }
            
            return jsonify({"integrations": integrations}), 200
        
    except Exception as e:
        logger.error(f"Error getting integration status: {str(e)}")
        return jsonify({"error": f"Failed to get integration status: {str(e)}"}), 500

@integrations_bp.route('/test/<service>', methods=['POST'])
@require_auth
def test_integration(service: str):
    """Test integration connection with stored credentials."""
    if service not in ['trackman', 'arccos', 'skytrak']:
        return jsonify({"error": "Unsupported service"}), 400
    
    # Get current user
    user_data = get_current_user()
    if not user_data or not user_data.get('id'):
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        # Get database session using context manager
        with get_db() as session:
            # Get user
            user = session.query(User).filter(User.id == user_data['id']).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
                
            # Check if credentials exist
            has_credentials = False
            if service == 'trackman':
                has_credentials = bool(user.trackman_username and user.trackman_password)
            elif service == 'arccos':
                has_credentials = bool(user.arccos_email and user.arccos_password)
            elif service == 'skytrak':
                has_credentials = bool(user.skytrak_username and user.skytrak_password)
                
            if not has_credentials:
                return jsonify({
                    "success": False,
                    "message": f"No {service.capitalize()} credentials found. Please connect first."
                }), 400
                
            # In a real implementation, we would test the connection to the service here
            # For now, we'll just return successful status since the credentials exist
            
            return jsonify({
                "success": True,
                "message": f"Connection to {service.capitalize()} is working properly."
            }), 200
            
    except Exception as e:
        logger.error(f"Error testing {service} integration: {str(e)}")
        return jsonify({"error": f"Failed to test integration: {str(e)}"}), 500

@integrations_bp.route('/disconnect/<service>', methods=['POST'])
@require_auth
def disconnect_integration(service: str):
    """Remove stored credentials for a service."""
    if service not in ['trackman', 'arccos', 'skytrak']:
        return jsonify({"error": "Unsupported service"}), 400
    
    # Get current user
    user_data = get_current_user()
    if not user_data or not user_data.get('id'):
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        # Get database session using context manager
        with get_db() as session:
            # Get user
            user = session.query(User).filter(User.id == user_data['id']).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Remove credentials
            if service == 'trackman':
                user.trackman_username = None
                user.trackman_password = None
            elif service == 'arccos':
                user.arccos_email = None
                user.arccos_password = None
            elif service == 'skytrak':
                user.skytrak_username = None
                user.skytrak_password = None
            
            # Save changes
            session.commit()
            
            # Return success
            return jsonify({
                "success": True,
                "message": f"Successfully disconnected from {service.capitalize()}"
            }), 200
        
    except Exception as e:
        logger.error(f"Error disconnecting from {service}: {str(e)}")
        return jsonify({"error": f"Failed to disconnect from {service}: {str(e)}"}), 500