# GolfStats Backend Application
import os
import sys
import logging
from typing import Dict, Any
from flask import Flask, request, jsonify, session, redirect

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Check if we're running in Render environment
is_render = os.environ.get('RENDER') == '1'

if is_render:
    logger.info("Detected Render environment")
    app.config['RENDER'] = True

# Load configuration
from config.config import config
app.config.update(
    SECRET_KEY=config["app"]["secret_key"],
    DEBUG=config["app"]["debug"]
)

# Initialize authentication modules - this will also set up the before_first_request handler
from backend.auth import init_app as init_auth
init_auth(app)

# Create API blueprint
from flask import Blueprint
from backend.integrations.routes import integrations_bp
from backend.auth.routes import auth_bp
from backend.range_shots.routes import range_shots_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import Supabase data access functions
from backend.database.supabase_data import (
    get_golf_rounds, get_golf_round, create_golf_round, 
    update_golf_round, delete_golf_round, get_shots_for_round,
    add_shot, get_user_preferences, update_user_preferences,
    get_user_rounds_stats, get_user_clubs, get_club, create_club,
    update_club, delete_club
)

# Import auth decorators
from backend.auth import require_auth

@app.route('/')
def index():
    """Home page route - serve index.html or redirect to login."""
    from flask import send_from_directory
    from backend.auth import is_authenticated
    
    # If user isn't authenticated, redirect to login page
    if not is_authenticated():
        return redirect('/login.html')
    
    # Otherwise serve the index.html file
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the frontend directory."""
    from flask import send_from_directory
    
    # Special case for login/signup pages - always accessible
    if path in ['login.html', 'signup.html']:
        return send_from_directory('../frontend', path)
    
    # Special case for login/signup related JS and CSS
    if path in ['login.js', 'login.css', 'signup.js']:
        return send_from_directory('../frontend', path)
    
    # For all other static files, check authentication
    from backend.auth import is_authenticated
    if not is_authenticated() and path != 'styles.css':
        return redirect('/login.html')
    
    return send_from_directory('../frontend', path)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "supabase": True,
        "rls_enabled": True,
        "environment": os.environ.get('APP_ENVIRONMENT', 'production'),
        "render": os.environ.get('RENDER') == '1'
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
    from backend.auth import get_current_user
    
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

@api_bp.route('/rounds', methods=['POST'])
@require_auth
def add_round():
    """Create a new round."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/rounds/<int:round_id>', methods=['PUT'])
@require_auth
def update_round(round_id):
    """Update a round."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/rounds/<int:round_id>', methods=['DELETE'])
@require_auth
def delete_round(round_id):
    """Delete a round."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/rounds/<int:round_id>/shots', methods=['POST'])
@require_auth
def add_shot_to_round(round_id):
    """Add a shot to a round."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/preferences')
@require_auth
def get_preferences():
    """Get user preferences."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/preferences', methods=['PUT'])
@require_auth
def update_preferences():
    """Update user preferences."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/stats')
@require_auth
def get_stats():
    """Get user statistics for various timeframes."""
    from backend.auth import get_current_user
    
    user = get_current_user()
    timeframe = request.args.get('timeframe', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    stats = get_user_rounds_stats(
        user_id=user['id'], 
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify({
        "stats": stats
    })

# Club management routes
@api_bp.route('/clubs')
@require_auth
def get_clubs():
    """Get clubs for current user."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/clubs/<int:club_id>')
@require_auth
def get_club_by_id(club_id):
    """Get a specific club."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/clubs', methods=['POST'])
@require_auth
def add_club():
    """Create a new club."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/clubs/<int:club_id>', methods=['PUT'])
@require_auth
def update_club_by_id(club_id):
    """Update a club."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/clubs/<int:club_id>', methods=['DELETE'])
@require_auth
def delete_club_by_id(club_id):
    """Delete a club."""
    from backend.auth import get_current_user
    
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

@api_bp.route('/admin/apply-rls', methods=['POST'])
@require_auth
def admin_apply_rls():
    """
    Admin endpoint to manually apply RLS policies.
    Only accessible to superusers.
    
    Note: This endpoint is currently disabled due to issues with
    Supabase RPC execution. RLS policies should be applied manually
    via the Supabase SQL editor instead.
    """
    # Return a message instructing to use Supabase SQL editor
    return jsonify({
        "success": False,
        "message": "Automatic RLS policy application is disabled. Please apply RLS policies manually using the Supabase SQL Editor with the contents of database/migrations/rls_policies.sql"
    }), 501  # 501 Not Implemented

# Register the API blueprint
app.register_blueprint(api_bp)
# auth_bp is already registered by init_auth
# app.register_blueprint(auth_bp)
app.register_blueprint(integrations_bp)
app.register_blueprint(range_shots_bp)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

# For local development only
if __name__ == '__main__':
    logger.info(f"Starting GolfStats backend server on port {os.environ.get('PORT', 8000)}")
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        debug=config["app"]["debug"]
    )
