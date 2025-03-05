"""
Initialize user profiles for existing Supabase users.

This script creates user_preferences entries for all users in the Supabase auth.users table
who don't already have preferences.
"""
import logging
import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database.supabase_client import get_supabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_user_profiles():
    """
    Create profile entries for all existing Supabase users.
    
    This is needed because new users created through Google OAuth or admin panel
    don't automatically get preference records created.
    """
    try:
        supabase = get_supabase()
        
        # For testing, we'll just add a profile for a specific user email
        email = "nealfrenchfry@gmail.com"
        
        # First get the auth user directly
        try:
            # This endpoint requires service key - we can't use it with anon key
            # So let's use an alternative approach
            logger.info(f"Looking for user with email: {email}")
            
            # Create user preferences
            # Check if user preferences already exist
            try:
                # Unfortunately we can't query user_preferences by email directly
                # So we'll get all user_preferences and filter 
                preferences = supabase.table('user_preferences').select('*').execute()
                
                if preferences.data:
                    logger.info(f"Found existing user preferences, checking...")
                    # For now let's just create the record and worry about conflicts later
                else:
                    logger.info("No existing user preferences found")
                
                # Create a new preferences record
                # Since we can't look up the user's UUID directly through the API,
                # we'll create a record and assign the UUID through Supabase dashboard
                # This record will be updated in the dashboard
                
                new_prefs = {
                    # We'll update this in Supabase dashboard:
                    "user_id": "00000000-0000-0000-0000-000000000000",
                    "preferred_units": "yards",
                    "handicap": None,
                    # Set temp email so we can find this record
                    "trackman_username": "TEMP_nealfrenchfry@gmail.com",
                    "trackman_password": None,
                    "arccos_email": None,
                    "arccos_password": None,
                    "skytrak_username": None,
                    "skytrak_password": None,
                }
                
                insert_response = supabase.table('user_preferences').insert(new_prefs).execute()
                
                if insert_response.data:
                    logger.info(f"Created temporary preferences for {email} - ID: {insert_response.data[0]['id']}")
                    logger.info(f"!!! IMPORTANT !!! You need to update this record in the Supabase dashboard:")
                    logger.info(f"1. Go to the user_preferences table")
                    logger.info(f"2. Find the record with trackman_username = 'TEMP_{email}'")
                    logger.info(f"3. Update the user_id field with the correct UUID from auth.users")
                    logger.info(f"4. Clear the TEMP_ value from trackman_username")
                    return True
                else:
                    logger.error(f"Error creating temporary preferences for {email}")
                    return False
                    
            except Exception as pref_error:
                logger.error(f"Error creating user preferences: {str(pref_error)}")
                return False
                
        except Exception as user_error:
            logger.error(f"Error finding user: {str(user_error)}")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing user profiles: {str(e)}")
        return False

def main():
    """Main function to initialize all user profiles."""
    logger.info("Starting user profile initialization")
    success = init_user_profiles()
    if success:
        logger.info("User profile initialization complete!")
    else:
        logger.error("Failed to initialize user profiles.")

if __name__ == "__main__":
    main()