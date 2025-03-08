"""
GolfStats API Entry Point for Vercel
This module provides serverless function integration for Vercel.
"""
import os
import sys
import logging
import importlib.util
from typing import Dict, Any

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Configure logging for serverless environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log Python version
logger.info(f"Python version: {sys.version}")

# Use mock scrapers instead of selenium-based scrapers in the serverless environment
# This reduces the deployment size significantly
logger.info("Setting up mock scrapers for serverless environment")
sys.modules['backend.scrapers.arccos_scraper'] = importlib.import_module('api.mock_scrapers')
sys.modules['backend.scrapers.trackman_scraper'] = importlib.import_module('api.mock_scrapers')
sys.modules['backend.scrapers.skytrak_scraper'] = importlib.import_module('api.mock_scrapers')

# Log environment variables
logger.info("==== ENVIRONMENT VARIABLES ====")
logger.info(f"APP_ENVIRONMENT: {os.environ.get('APP_ENVIRONMENT')}")
logger.info(f"SUPABASE_URL set: {bool(os.environ.get('SUPABASE_URL'))}")
logger.info(f"SUPABASE_KEY set: {bool(os.environ.get('SUPABASE_KEY'))}")
logger.info(f"SUPABASE_API_KEY set: {bool(os.environ.get('SUPABASE_API_KEY'))}")
logger.info(f"GOOGLE_CLIENT_ID set: {bool(os.environ.get('GOOGLE_CLIENT_ID'))}")
logger.info(f"GOOGLE_CLIENT_SECRET set: {bool(os.environ.get('GOOGLE_CLIENT_SECRET'))}")
logger.info("==============================")

logger.info("Importing database modules...")
# First import database modules
from backend.database.db_connection import get_db
from backend.database.supabase_client import get_supabase

logger.info("Importing Flask application...")
# Import Flask application
try:
    from backend.app import app as flask_app
    logger.info("Flask application imported successfully")
except Exception as e:
    logger.error(f"Error importing Flask application: {str(e)}")
    raise

logger.info("Vercel serverless function initialized")

# Create handler for Vercel serverless function
def handler(event, context):
    """
    Process the serverless function request with Flask.
    This adapts the Flask app to work within a serverless context.
    
    This is the main entry point used by Vercel's Python runtime.
    """
    logger.info(f"Processing request: {event}")
    
    # Extract request details
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    query_params = event.get('queryStringParameters', {}) or {}
    body = event.get('body', '')
    
    logger.info(f"Processing {http_method} request for path: {path}")
    
    # Create WSGI environment
    environ = {
        'wsgi.input': body,
        'wsgi.errors': sys.stderr,
        'wsgi.version': (1, 0),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join([f"{k}={v}" for k, v in query_params.items()]),
        'SERVER_NAME': 'vercel-serverless',
        'SERVER_PORT': '443',
        'SERVERLESS_CONTEXT': 'true',  # Indicate we're in a serverless environment
    }
    
    # Add content type and length if present
    if 'content-type' in headers:
        environ['CONTENT_TYPE'] = headers['content-type']
    if 'content-length' in headers:
        environ['CONTENT_LENGTH'] = headers['content-length']
    
    # Add headers to environment
    for header, value in headers.items():
        key = 'HTTP_' + header.upper().replace('-', '_')
        environ[key] = value
    
    # Response builder
    status_code = 200
    response_headers = []
    response_body = []
    
    def start_response(status, headers):
        nonlocal status_code, response_headers
        status_code = int(status.split(' ')[0])
        response_headers = headers
    
    # Call the Flask application
    try:
        output = flask_app(environ, start_response)
        
        # Gather response body
        for data in output:
            if isinstance(data, bytes):
                response_body.append(data.decode('utf-8'))
            else:
                response_body.append(data)
        
        # Close the application response if it's a file-like object
        if hasattr(output, 'close'):
            output.close()
            
        body_content = ''.join(response_body)
        logger.info(f"Response status: {status_code}, headers: {response_headers}")
        
        # Build response dictionary
        response = {
            'statusCode': status_code,
            'headers': dict(response_headers),
            'body': body_content
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Internal Server Error'
        }