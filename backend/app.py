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

# Initialize database
from backend.database.db_connection import init_db
init_db()

# Initialize authentication modules
from backend.auth import init_app as init_auth
init_auth(app)

@app.route('/')
def index():
    """Home page route."""
    return "Welcome to GolfStats!"

@app.route('/api/user')
def user_info():
    """Get current user information."""
    from backend.auth import get_current_user, is_authenticated
    
    if not is_authenticated():
        return jsonify({"authenticated": False}), 401
    
    user_data = get_current_user()
    return jsonify({
        "authenticated": True,
        "user": user_data
    })

# Import and register blueprints for other routes
# from backend.routes.api import api_blueprint
# app.register_blueprint(api_blueprint, url_prefix='/api')

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
