#!/usr/bin/env python
"""
Entry point for running the GolfStats application.

This module sets up the Python path and starts the Flask application,
optionally with background ETL scheduler.

Usage:
    python run.py              # Run just the web app
    python run.py --scheduler  # Run the web app with ETL scheduler
    python run.py --etl        # Run a one-time ETL process and exit
"""
import os
import sys
import argparse
import threading

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Import configuration
from config.config import config

def run_webapp(host='0.0.0.0', port=8000):
    """
    Run the Flask web application.
    
    Args:
        host: Host to bind to
        port: Port to listen on
    """
    from backend.app import app
    app.run(host=host, port=port, debug=config["app"]["debug"])

def run_scheduler():
    """
    Run the background ETL scheduler.
    """
    from backend.scheduler import run_scheduler
    run_scheduler()

def run_etl():
    """
    Run a one-time ETL process.
    """
    from backend.etl.daily_etl import run_daily_etl
    results = run_daily_etl()
    print(f"ETL Process Summary:")
    print(f"- Start Time: {results['start_time']}")
    print(f"- End Time: {results['end_time']}")
    print(f"- Duration: {results['duration_seconds']} seconds")
    print(f"- Users Processed: {results['users_processed']}")
    print(f"- Trackman Sessions: {results['trackman_sessions']}")
    print(f"- Arccos Rounds: {results['arccos_rounds']}")
    print(f"- SkyTrak Sessions: {results['skytrak_sessions']}")
    print(f"- Errors: {len(results['errors'])}")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"- {error}")

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="GolfStats Application Server")
    parser.add_argument('--scheduler', action='store_true', help='Run with ETL scheduler')
    parser.add_argument('--etl', action='store_true', help='Run a one-time ETL process and exit')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the web server on')
    args = parser.parse_args()
    
    if args.etl:
        # Run ETL only
        run_etl()
    elif args.scheduler:
        # Run both web app and scheduler
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Run web app in main thread
        run_webapp(port=args.port)
    else:
        # Run just the web app
        run_webapp(port=args.port)