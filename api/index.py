"""
GolfStats Vercel Handler - Exposes Flask app as WSGI application
with optimized dependencies for serverless deployment.
"""
import sys
import os
import importlib.util

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Replace heavy scraper modules with lightweight mocks for Vercel deployment
# This must happen before importing the Flask app
sys.modules['backend.scrapers.arccos_scraper'] = importlib.import_module('api.mock_scrapers')
sys.modules['backend.scrapers.trackman_scraper'] = importlib.import_module('api.mock_scrapers') 
sys.modules['backend.scrapers.skytrak_scraper'] = importlib.import_module('api.mock_scrapers')

# Import the Flask app instance from backend/app.py
from backend.app import app

# That's it! No handler function needed - Vercel's Python runtime will detect
# the 'app' WSGI application and use it automatically