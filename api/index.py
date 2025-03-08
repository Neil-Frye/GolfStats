"""
GolfStats API Entry Point for Vercel - Test Deployment
This module provides a simple test endpoint to verify Python runtime.
"""
import os
import sys
import json
import logging
from flask import Flask, jsonify

# Configure logging for serverless environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log Python version
logger.info(f"Python version: {sys.version}")

# Create a simple Flask application for testing
test_app = Flask(__name__)

@test_app.route('/', methods=['GET'])
def hello():
    return jsonify({
        "message": "Hello from GolfStats test deployment!",
        "python_version": sys.version,
        "environment": os.environ.get('APP_ENVIRONMENT', 'unknown')
    })

@test_app.route('/env', methods=['GET'])
def environment():
    """Return environment information for debugging."""
    env_info = {
        "python_version": sys.version,
        "app_environment": os.environ.get('APP_ENVIRONMENT'),
        "vercel": os.environ.get('VERCEL') == '1',
        "supabase_url_set": bool(os.environ.get('SUPABASE_URL')),
        "supabase_key_set": bool(os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_API_KEY'))
    }
    return jsonify(env_info)

# Handler for Vercel serverless function
def handler(event, context):
    """
    Simple handler function for Vercel.
    This returns a minimal HTTP response for testing.
    """
    logger.info(f"Test handler received event: {event}")
    
    try:
        # Extract request path
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')
        
        logger.info(f"Processing {http_method} request for path: {path}")
        
        # Create a minimal WSGI environment
        environ = {
            'REQUEST_METHOD': http_method,
            'PATH_INFO': path,
            'QUERY_STRING': '',
            'SERVER_NAME': 'vercel',
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.input': '',
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        
        # Process query string parameters
        query_params = event.get('queryStringParameters') or {}
        if query_params:
            environ['QUERY_STRING'] = '&'.join([f"{k}={v}" for k, v in query_params.items()])
            
        # Add headers to environment
        headers = event.get('headers') or {}
        for key, value in headers.items():
            header_key = f"HTTP_{key.replace('-', '_').upper()}"
            environ[header_key] = value
            
        # Prepare response handling
        response_body = []
        status_info = [200, 'OK']
        response_headers = []
        
        def start_response(status, headers):
            status_code = int(status.split(' ')[0])
            status_info[0] = status_code
            status_info[1] = status.split(' ', 1)[1] if ' ' in status else ''
            response_headers.extend(headers)
            
        # Call Flask app
        result = test_app(environ, start_response)
        
        # Process response body
        for data in result:
            if isinstance(data, bytes):
                response_body.append(data.decode('utf-8'))
            else:
                response_body.append(data)
                
        if hasattr(result, 'close'):
            result.close()
            
        body = ''.join(response_body)
        
        # Build Vercel response
        response = {
            'statusCode': status_info[0],
            'headers': {k: v for k, v in response_headers},
            'body': body
        }
        
        logger.info(f"Returning response with status {status_info[0]}")
        return response
        
    except Exception as e:
        logger.error(f"Error in test handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e),
                'python_version': sys.version
            })
        }