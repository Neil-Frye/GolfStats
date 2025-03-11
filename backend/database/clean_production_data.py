"""
Clean test data from production Supabase database.

This script connects to the production Supabase instance and removes any test/placeholder
data that might exist in the database tables, ensuring a clean production environment.
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure we're using production environment
os.environ['APP_ENVIRONMENT'] = 'production'

# Import Supabase client after setting environment
from backend.database.supabase_client import get_supabase
from config.config import config

def clean_table(table_name: str) -> int:
    """
    Clean data from a specific table in production.
    
    Args:
        table_name: Name of the table to clean
        
    Returns:
        Number of rows deleted
    """
    try:
        supabase = get_supabase()
        
        # First, get count of rows in the table
        count_response = supabase.table(table_name).select('*', count='exact').execute()
        initial_count = count_response.count if hasattr(count_response, 'count') else len(count_response.data)
        
        # Delete all data from the table
        delete_response = supabase.table(table_name).delete().execute()
        
        logger.info(f"Deleted {initial_count} rows from {table_name} table")
        return initial_count
    except Exception as e:
        logger.error(f"Error cleaning table {table_name}: {str(e)}")
        return 0

def clean_all_tables() -> Dict[str, int]:
    """
    Clean data from all tables in production.
    
    Note: This function preserves user authentication data but removes
    all application data.
    
    Returns:
        Dictionary mapping table names to number of rows deleted
    """
    supabase = get_supabase()
    
    # Tables to clean, in order (to handle foreign key constraints)
    tables = [
        "golf_shots",
        "golf_holes",
        "round_stats",
        "golf_rounds",
        "clubs",
        "user_preferences"
    ]
    
    # Note: We don't clean auth tables as those are managed by Supabase Auth
    
    results = {}
    
    for table in tables:
        deleted = clean_table(table)
        results[table] = deleted
    
    return results

def main():
    """Main function to clean production environment."""
    logger.info("=== Cleaning production Supabase database ===")
    logger.info(f"Using Supabase URL: {config['supabase']['url']}")
    
    # Verify we're in production environment
    if config['app']['environment'] != 'production':
        logger.error("Not in production environment! Aborting.")
        logger.error("Make sure APP_ENVIRONMENT=production is set")
        return 1
    
    # Confirmation
    confirm = input("This will DELETE ALL DATA from the production database. Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        logger.info("Operation cancelled by user")
        return 0
    
    # Clean all tables
    logger.info("Cleaning all tables...")
    results = clean_all_tables()
    
    # Summary
    logger.info("\n=== Cleaning Summary ===")
    total_rows = sum(results.values())
    logger.info(f"Total rows deleted: {total_rows}")
    
    for table, count in results.items():
        logger.info(f"{table}: {count} rows deleted")
    
    logger.info("\n✅ Production database cleaned successfully!")
    
    # Next steps
    logger.info("\nNext steps:")
    logger.info("1. Setup user profiles for any existing users")
    logger.info("2. If needed, run python -m backend.database.init_user_profiles")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())