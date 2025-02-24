#!/usr/bin/env python
"""
Entry point for running the GolfStats application.

This module sets up the Python path and starts the Flask application.
"""
import os
import sys

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Now import the app
from backend.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)