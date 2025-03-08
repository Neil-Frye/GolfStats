"""
GolfStats Vercel Minimal Handler
"""
import sys
import json

# Ultra-minimal handler - no logging, no framework
def handler(event, context):
    """Absolute minimal handler to avoid any Python 3.12 compatibility issues"""
    # Build simple response
    data = {
        "message": "Hello from GolfStats",
        "python": sys.version
    }
    
    # Return direct response
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data)
    }