"""
GolfStats Vercel Handler - Exposes Flask app as WSGI application
"""
import sys
import os

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the Flask app instance from backend/app.py
from backend.app import app

# That's it! No handler function needed - Vercel's Python runtime will detect
# the 'app' WSGI application and use it automatically