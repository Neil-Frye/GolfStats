# GolfStats Backend Application
import os
import sys
import logging
from typing import Dict, Any
from flask import Flask

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """
    Application factory for creating the Flask app.
    
    Returns:
        Flask application instance
    """
    # Create Flask application
    app = Flask(__name__)
    
    # Check if we're running in Render environment
    is_render = os.environ.get('RENDER') == '1'
    
    if is_render:
        logger.info("Detected Render environment")
        app.config['RENDER'] = True
    
    # Load configuration from the centralized environment module
    from config.env import env
    app.config.update(
        SECRET_KEY=env["app"]["secret_key"],
        DEBUG=env["app"]["debug"],
        ENV=env.env_name
    )
    
    logger.info(f"Application configured for {env.env_name} environment")
    
    # Initialize authentication modules - this will also set up the before_first_request handler
    from backend.auth import init_app as init_auth
    init_auth(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_blueprints(app):
    """
    Register all application blueprints.
    
    Args:
        app: Flask application instance
    """
    # Import blueprints
    from backend.auth.routes import auth_bp
    from backend.integrations.routes import integrations_bp
    from backend.range_shots.routes import range_shots_bp
    from backend.rounds.routes import rounds_bp
    from backend.shots.routes import shots_bp
    from backend.clubs.routes import clubs_bp
    from backend.stats.routes import stats_bp
    from backend.preferences.routes import preferences_bp
    from backend.user.routes import user_bp
    from backend.static.routes import static_bp
    
    # Register API-related blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(integrations_bp)
    app.register_blueprint(range_shots_bp)
    app.register_blueprint(rounds_bp)
    app.register_blueprint(shots_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(preferences_bp)
    app.register_blueprint(user_bp)
    
    # Register blueprint for health check
    from flask import Blueprint, jsonify
    health_bp = Blueprint('health', __name__)
    
    # Import the environment module for the health check endpoint
    from config.env import env
    
    @health_bp.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "supabase": True,
            "rls_enabled": True,
            "environment": env.env_name,
            "render": os.environ.get('RENDER') == '1'
        })
    
    app.register_blueprint(health_bp)
    
    # Register admin endpoints
    admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
    
    @admin_bp.route('/apply-rls', methods=['POST'])
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
    
    app.register_blueprint(admin_bp)
    
    # Register static routes last (lowest priority)
    app.register_blueprint(static_bp)

def register_error_handlers(app):
    """
    Register error handlers for the application.
    
    Args:
        app: Flask application instance
    """
    from flask import jsonify
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors."""
        return jsonify({"error": "Internal server error"}), 500

# Create the application
app = create_app()

# For local development only
if __name__ == '__main__':
    logger.info(f"Starting GolfStats backend server on port {os.environ.get('PORT', 8000)}")
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        debug=app.config["DEBUG"]
    )