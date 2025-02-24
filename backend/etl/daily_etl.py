"""
Daily ETL Process for GolfStats application.

This module handles the extraction, transformation, and loading of golf data
from various sources (Trackman, Arccos, SkyTrak) into the GolfStats database.
"""
import os
import sys
import logging
import datetime
from typing import List, Dict, Any, Optional

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.db_connection import get_db
from backend.scrapers.trackman_scraper import get_trackman_data
from backend.scrapers.arccos_scraper import get_arrcos_data
from backend.scrapers.skytrak_scraper import get_skytrak_data
from backend.models.user import User

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create file handler
logs_dir = os.path.join(project_root, 'logs')
os.makedirs(logs_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(logs_dir, 'daily_etl.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def extract_user_list() -> List[User]:
    """
    Extract list of users from database.
    
    Returns:
        List of User objects
    """
    users = []
    try:
        with get_db() as db:
            users = db.query(User).filter(User.is_active == True).all()
        logger.info(f"Found {len(users)} active users")
    except Exception as e:
        logger.error(f"Error extracting user list: {str(e)}")
    
    return users

def process_user_data(user: User) -> Dict[str, List[int]]:
    """
    Process golf data for a specific user from all sources.
    
    Args:
        user: User object
        
    Returns:
        Dictionary with results from each data source
    """
    results = {
        "trackman": [],
        "arccos": [],
        "skytrak": []
    }
    
    try:
        logger.info(f"Processing data for user {user.id} ({user.email})")
        
        # Process Trackman data
        if user.trackman_credentials_valid():
            try:
                logger.info(f"Processing Trackman data for user {user.id}")
                trackman_results = get_trackman_data(user_id=user.id, limit=20)
                results["trackman"] = trackman_results
                logger.info(f"Processed {len(trackman_results)} Trackman sessions")
            except Exception as e:
                logger.error(f"Error processing Trackman data for user {user.id}: {str(e)}")
        
        # Process Arccos data
        if user.arccos_credentials_valid():
            try:
                logger.info(f"Processing Arccos data for user {user.id}")
                arccos_results = get_arrcos_data(user_id=user.id, limit=20)
                results["arccos"] = arccos_results
                logger.info(f"Processed {len(arccos_results)} Arccos rounds")
            except Exception as e:
                logger.error(f"Error processing Arccos data for user {user.id}: {str(e)}")
        
        # Process SkyTrak data
        if user.skytrak_credentials_valid():
            try:
                logger.info(f"Processing SkyTrak data for user {user.id}")
                skytrak_results = get_skytrak_data(user_id=user.id, limit=20)
                results["skytrak"] = skytrak_results
                logger.info(f"Processed {len(skytrak_results)} SkyTrak sessions")
            except Exception as e:
                logger.error(f"Error processing SkyTrak data for user {user.id}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in process_user_data for user {user.id}: {str(e)}")
    
    return results

def run_daily_etl() -> Dict[str, Any]:
    """
    Run daily ETL process for all users.
    
    Returns:
        Dictionary with ETL results
    """
    start_time = datetime.datetime.now()
    results = {
        "start_time": start_time,
        "end_time": None,
        "users_processed": 0,
        "trackman_sessions": 0,
        "arccos_rounds": 0,
        "skytrak_sessions": 0,
        "errors": []
    }
    
    try:
        logger.info("Starting daily ETL process")
        
        # Get list of users
        users = extract_user_list()
        
        # Process each user
        for user in users:
            try:
                user_results = process_user_data(user)
                
                # Update results
                results["users_processed"] += 1
                results["trackman_sessions"] += len(user_results["trackman"])
                results["arccos_rounds"] += len(user_results["arccos"])
                results["skytrak_sessions"] += len(user_results["skytrak"])
                
            except Exception as e:
                error_msg = f"Error processing user {user.id}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        logger.info(f"Daily ETL completed - Processed {results['users_processed']} users, "
                   f"{results['trackman_sessions']} Trackman sessions, "
                   f"{results['arccos_rounds']} Arccos rounds, "
                   f"{results['skytrak_sessions']} SkyTrak sessions")
    
    except Exception as e:
        error_msg = f"Error in daily ETL process: {str(e)}"
        logger.error(error_msg)
        results["errors"].append(error_msg)
    
    # Record end time
    results["end_time"] = datetime.datetime.now()
    results["duration_seconds"] = (results["end_time"] - results["start_time"]).total_seconds()
    
    return results

if __name__ == "__main__":
    """
    Run the daily ETL process when the script is executed directly.
    """
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
