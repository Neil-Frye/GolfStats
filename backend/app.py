# GolfStats Backend Application
import os
import sys
from typing import Dict, Any
from flask import Flask, request, jsonify, session

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Create Flask application
app = Flask(__name__)

# Load configuration
from config.config import config
app.config.update(
    SECRET_KEY=config["app"]["secret_key"],
    DEBUG=config["app"]["debug"]
)

# Initialize authentication modules
from backend.auth import init_app as init_auth
init_auth(app)

# Create API blueprint
from flask import Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import Supabase data access functions
from backend.database.supabase_data import (
    get_golf_rounds, get_golf_round, create_golf_round, 
    update_golf_round, delete_golf_round, get_shots_for_round,
    add_shot, get_user_preferences, update_user_preferences
)

# Import auth decorator
from backend.auth import require_auth

@app.route('/')
def index():
    """Home page route."""
    return "Welcome to GolfStats! Backend running with Supabase integration."

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "supabase": True
    })

@api_bp.route('/user')
@require_auth
def user_info():
    """Get current user information."""
    from backend.auth import get_current_user
    
    user_data = get_current_user()
    return jsonify({
        "authenticated": True,
        "user": user_data
    })

@api_bp.route('/rounds')
@require_auth
def list_rounds():
    """Get rounds for current user."""
    from backend.auth import get_current_user
    
    user = get_current_user()
    rounds = get_golf_rounds(user['id'])
    
    return jsonify({
        "rounds": rounds
    })

@api_bp.route('/rounds/<int:round_id>')
@require_auth
def get_round(round_id):
    """Get a specific round with all shot data."""
    round_data = get_golf_round(round_id)
    if not round_data:
        return jsonify({"error": "Round not found"}), 404
        
    # Get shots for this round
    shots = get_shots_for_round(round_id)
    
    # Add shots to round data
    round_data['shots'] = shots
    
    return jsonify({
        "round": round_data
    })

@api_bp.route('/rounds', methods=['POST'])
@require_auth
def add_round():
    """Create a new round."""
    from backend.auth import get_current_user
    
    user = get_current_user()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    round_data = create_golf_round(user['id'], data)
    
    if not round_data:
        return jsonify({"error": "Failed to create round"}), 500
        
    return jsonify({
        "message": "Round created successfully",
        "round": round_data
    }), 201

@api_bp.route('/rounds/<int:round_id>', methods=['PUT'])
@require_auth
def update_round(round_id):
    """Update a round."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    # Check if round exists
    existing = get_golf_round(round_id)
    if not existing:
        return jsonify({"error": "Round not found"}), 404
        
    round_data = update_golf_round(round_id, data)
    
    if not round_data:
        return jsonify({"error": "Failed to update round"}), 500
        
    return jsonify({
        "message": "Round updated successfully",
        "round": round_data
    })

@api_bp.route('/rounds/<int:round_id>', methods=['DELETE'])
@require_auth
def delete_round(round_id):
    """Delete a round."""
    # Check if round exists
    existing = get_golf_round(round_id)
    if not existing:
        return jsonify({"error": "Round not found"}), 404
        
    success = delete_golf_round(round_id)
    
    if not success:
        return jsonify({"error": "Failed to delete round"}), 500
        
    return jsonify({
        "message": "Round deleted successfully"
    })

@api_bp.route('/rounds/<int:round_id>/shots', methods=['POST'])
@require_auth
def add_shot_to_round(round_id):
    """Add a shot to a round."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    # Check if round exists
    existing = get_golf_round(round_id)
    if not existing:
        return jsonify({"error": "Round not found"}), 404
        
    shot_data = add_shot(round_id, data)
    
    if not shot_data:
        return jsonify({"error": "Failed to add shot"}), 500
        
    return jsonify({
        "message": "Shot added successfully",
        "shot": shot_data
    }), 201

@api_bp.route('/preferences')
@require_auth
def get_preferences():
    """Get user preferences."""
    from backend.auth import get_current_user
    
    user = get_current_user()
    preferences = get_user_preferences(user['id'])
    
    return jsonify({
        "preferences": preferences
    })

@api_bp.route('/preferences', methods=['PUT'])
@require_auth
def update_preferences():
    """Update user preferences."""
    from backend.auth import get_current_user
    
    user = get_current_user()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    preferences = update_user_preferences(user['id'], data)
    
    if not preferences:
        return jsonify({"error": "Failed to update preferences"}), 500
        
    return jsonify({
        "message": "Preferences updated successfully",
        "preferences": preferences
    })

# Register the API blueprint
app.register_blueprint(api_bp)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        debug=config["app"]["debug"]
    )
