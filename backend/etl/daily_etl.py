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

def extract_user_list() -> List[Dict[str, Any]]:
    """
    Extract list of users from database.
    
    Returns:
        List of dictionaries with user data
    """
    users = []
    try:
        # Use Supabase to get all users and their preferences
        from backend.database.supabase_client import get_supabase_client
        
        # Get users from the auth.users table
        supabase = get_supabase_client()
        
        # First, get all users
        response = supabase.auth.admin.list_users()
        
        if response.data:
            for user_data in response.data:
                # Only include active users
                if user_data.get('email') and user_data.get('id'):
                    # Create a lightweight user record
                    user = {
                        'id': user_data.get('id'),
                        'email': user_data.get('email'),
                        'has_credentials': False
                    }
                    users.append(user)
        
        # Then, get user preferences for users with integration credentials
        prefs_response = supabase.table('user_preferences') \
            .select('user_id, arccos_email, arccos_password, trackman_username, trackman_password, skytrak_username, skytrak_password') \
            .execute()
            
        preferences = {}
        if prefs_response.data:
            for pref in prefs_response.data:
                user_id = pref.get('user_id')
                
                if user_id:
                    # Check for any service credentials
                    has_arccos = bool(pref.get('arccos_email') and pref.get('arccos_password'))
                    has_trackman = bool(pref.get('trackman_username') and pref.get('trackman_password'))
                    has_skytrak = bool(pref.get('skytrak_username') and pref.get('skytrak_password'))
                    
                    preferences[user_id] = {
                        'has_arccos': has_arccos,
                        'has_trackman': has_trackman,
                        'has_skytrak': has_skytrak
                    }
        
        # Merge user preferences with user data
        for user in users:
            user_id = user.get('id')
            if user_id in preferences:
                user['has_arccos'] = preferences[user_id].get('has_arccos', False)
                user['has_trackman'] = preferences[user_id].get('has_trackman', False)
                user['has_skytrak'] = preferences[user_id].get('has_skytrak', False)
                user['has_credentials'] = user['has_arccos'] or user['has_trackman'] or user['has_skytrak']
            else:
                user['has_arccos'] = False
                user['has_trackman'] = False
                user['has_skytrak'] = False
                user['has_credentials'] = False
        
        # Filter to users with credentials only
        users = [u for u in users if u.get('has_credentials', False)]
        
        logger.info(f"Found {len(users)} active users with integration credentials")
    except Exception as e:
        logger.error(f"Error extracting user list: {str(e)}")
    
    return users

def process_user_data(user: Dict[str, Any]) -> Dict[str, List[int]]:
    """
    Process golf data for a specific user from all sources.
    
    Args:
        user: Dictionary with user data
        
    Returns:
        Dictionary with results from each data source
    """
    results = {
        "trackman": [],
        "arccos": [],
        "skytrak": []
    }
    
    try:
        user_id = user.get('id')
        email = user.get('email')
        logger.info(f"Processing data for user {user_id} ({email})")
        
        # Process Trackman data
        if user.get('has_trackman', False):
            try:
                logger.info(f"Processing Trackman data for user {user_id}")
                trackman_data_list = get_trackman_data(user_id=user_id, limit=20, use_user_credentials=True)
                
                if trackman_data_list:
                    results["trackman"] = trackman_data_list
                
                logger.info(f"Processed and stored {len(results['trackman'])} Trackman sessions")
            except Exception as e:
                logger.error(f"Error processing Trackman data for user {user_id}: {str(e)}")
        
        # Process Arccos data
        if user.get('has_arccos', False):
            try:
                logger.info(f"Processing Arccos data for user {user_id}")
                # Get Arccos rounds - limit 10 for daily ETL to avoid overloading
                arccos_round_ids = get_arrcos_data(user_id=user_id, limit=10, use_user_credentials=True)
                
                if arccos_round_ids:
                    results["arccos"] = arccos_round_ids
                
                logger.info(f"Processed and stored {len(results['arccos'])} Arccos rounds")
            except Exception as e:
                logger.error(f"Error processing Arccos data for user {user_id}: {str(e)}")
        
        # Process SkyTrak data
        if user.get('has_skytrak', False):
            try:
                logger.info(f"Processing SkyTrak data for user {user_id}")
                skytrak_data_list = get_skytrak_data(user_id=user_id, limit=20, use_user_credentials=True)
                
                if skytrak_data_list:
                    results["skytrak"] = skytrak_data_list
                
                logger.info(f"Processed and stored {len(results['skytrak'])} SkyTrak sessions")
            except Exception as e:
                logger.error(f"Error processing SkyTrak data for user {user_id}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in process_user_data for user {user.get('id')}: {str(e)}")
    
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
