"""
GolfStats API Entry Point for Vercel
This module provides serverless function integration for Vercel.
"""
import os
import sys
from http.server import BaseHTTPRequestHandler
import logging
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

# Import Flask application
from backend.app import app as flask_app

# Create handler for Vercel serverless function
def handler(request, response):
    """
    Process the Vercel serverless function request with Flask.
    This adapts the Flask app to work within a serverless context.
    """
    # Get request path and method
    path = request['path']
    method = request['method']
    
    # Create a WSGI environment
    environ = {
        'wsgi.input': request.get('body', ''),
        'wsgi.errors': sys.stderr,
        'wsgi.version': (1, 0),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': request.get('query', ''),
        'CONTENT_TYPE': request.get('headers', {}).get('content-type', ''),
        'CONTENT_LENGTH': request.get('headers', {}).get('content-length', ''),
        'SERVER_NAME': 'vercel-serverless',
        'SERVER_PORT': '443',
        'HTTP_HOST': request.get('headers', {}).get('host', ''),
    }
    
    # Add all headers to the environment
    for header, value in request.get('headers', {}).items():
        key = 'HTTP_' + header.upper().replace('-', '_')
        environ[key] = value
    
    # Build the response
    status_code = 200
    headers = []
    body = []
    
    def start_response(status, response_headers):
        nonlocal status_code, headers
        status_code = int(status.split(' ')[0])
        headers = response_headers
    
    # Process the request through Flask
    resp = flask_app(environ, start_response)
    
    # Combine response body
    for data in resp:
        if isinstance(data, bytes):
            body.append(data.decode('utf-8'))
        else:
            body.append(data)
    
    # Return the response
    return {
        'statusCode': status_code,
        'headers': dict(headers),
        'body': ''.join(body)
    }

# Vercel serverless function entry point
class VercelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_PUT(self):
        self.handle_request('PUT')
    
    def do_DELETE(self):
        self.handle_request('DELETE')
    
    def handle_request(self, method):
        # Build request object
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        request = {
            'method': method,
            'path': self.path,
            'query': self.path.split('?')[1] if '?' in self.path else '',
            'headers': dict(self.headers),
            'body': body
        }
        
        # Process request
        try:
            response = handler(request, None)
            
            # Send response
            self.send_response(response['statusCode'])
            
            # Send headers
            for name, value in response['headers'].items():
                self.send_header(name, value)
            self.end_headers()
            
            # Send body
            self.wfile.write(response['body'].encode('utf-8'))
        
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal Server Error')

# Flask application is imported and configured above
# The app object is already initialized with all routes and blueprints
# Vercel will automatically use this handler function
def lambda_handler(event, context):
    """AWS Lambda compatible handler for Vercel."""
    return handler({
        'method': event.get('httpMethod', 'GET'),
        'path': event.get('path', '/'),
        'query': event.get('queryStringParameters', {}),
        'headers': event.get('headers', {}),
        'body': event.get('body', '')
    }, None)