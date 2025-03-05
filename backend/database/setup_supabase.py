"""
Setup Supabase database for GolfStats application.

This script creates all necessary tables and initializes user profiles.
"""
import logging
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database.supabase_tables import create_tables
from backend.database.init_user_profiles import init_user_profiles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_supabase():
    """Run the complete Supabase setup process."""
    logger.info("Starting Supabase setup process")
    
    # Step 1: Create database tables
    logger.info("Step 1: Creating database tables")
    tables_success = create_tables()
    
    if not tables_success:
        logger.error("Failed to create all database tables")
        return False
    
    # Step 2: Initialize user profiles
    logger.info("Step 2: Initializing user profiles")
    profiles_success = init_user_profiles()
    
    if not profiles_success:
        logger.warning("Note: User profile initialization had issues")
        # Continue anyway - this might be expected if no users exist yet
    
    logger.info("Supabase setup process complete!")
    return True

if __name__ == "__main__":
    setup_supabase()