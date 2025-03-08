"""
GolfStats API Entry Point for Vercel - Python 3.9 Compatibility Test
This module provides the simplest possible handler that doesn't rely on any complex dependencies.
"""
import os
import sys
import json
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vercel-function")

# Log important diagnostic information
logger.info(f"Python version: {sys.version}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Environment variables: APP_ENVIRONMENT={os.environ.get('APP_ENVIRONMENT')}")

# Simple direct handler - no Flask, no WSGI, no complex imports
def handler(event, context):
    """
    Ultra-minimal handler designed to work with any Python version on Vercel.
    This avoids all the complexity and just returns a simple JSON response.
    Specifically avoiding BaseHTTPRequestHandler and other classes that cause issubclass errors.
    """
    logger.info(f"Event received: {event}")
    logger.info(f"Running on Python version: {sys.version}")
    
    # Create a very simple response
    response_data = {
        "success": True,
        "message": "GolfStats compatibility test successful",
        "diagnostics": {
            "python_version": sys.version,
            "environment": os.environ.get("APP_ENVIRONMENT", "unknown"),
            "vercel": os.environ.get("VERCEL") == "1",
            "now": os.environ.get("NOW_REGION"),
            "supabase_url_set": bool(os.environ.get("SUPABASE_URL")),
            "path": event.get("path", "/"),
            "method": event.get("httpMethod", "GET")
        }
    }
    
    # Return a formatted response in the format Vercel expects
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "X-Python-Version": sys.version
        },
        "body": json.dumps(response_data, indent=2)
    }