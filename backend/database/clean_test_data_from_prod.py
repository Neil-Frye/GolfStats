"""
Clean test data from production Supabase database, but preserve real user data.

This script connects to the production Supabase instance and identifies/removes
test or placeholder data while preserving any legitimate user data.
"""
import os
import sys
import logging
import re
from typing import Dict, Any, List, Optional, Set

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

# Patterns that identify test data (customize based on your test data patterns)
TEST_PATTERNS = [
    re.compile(r'test', re.IGNORECASE),
    re.compile(r'dummy', re.IGNORECASE),
    re.compile(r'placeholder', re.IGNORECASE),
    re.compile(r'sample', re.IGNORECASE),
    re.compile(r'example', re.IGNORECASE),
    # Add other patterns specific to your test data
]

def is_test_data(data: Dict[str, Any]) -> bool:
    """
    Check if a row looks like test data based on patterns.
    
    Args:
        data: Row data dictionary
        
    Returns:
        True if it appears to be test data
    """
    # Convert values to strings and check against patterns
    string_values = [str(val) for val in data.values() if val is not None]
    
    for value in string_values:
        for pattern in TEST_PATTERNS:
            if pattern.search(value):
                return True
    
    return False

def get_real_user_ids() -> Set[str]:
    """
    Get IDs of real users (non-test users).
    
    Returns:
        Set of user IDs that appear to be real users
    """
    try:
        supabase = get_supabase()
        
        # Get user preferences - this is where we might identify real vs test users
        response = supabase.table('user_preferences').select('*').execute()
        preferences = response.data
        
        # Filter out test users based on patterns in their data
        real_users = set()
        test_users = set()
        
        for pref in preferences:
            if 'user_id' in pref and pref['user_id']:
                if is_test_data(pref):
                    test_users.add(pref['user_id'])
                else:
                    real_users.add(pref['user_id'])
        
        # If a user is in both lists (some real data, some test data), consider them real
        real_users = real_users.difference(test_users)
        
        logger.info(f"Identified {len(real_users)} real users and {len(test_users)} test users")
        return real_users
    
    except Exception as e:
        logger.error(f"Error identifying real users: {str(e)}")
        return set()

def clean_test_data_from_table(table_name: str, user_id_field: str = 'user_id',
                               real_user_ids: Optional[Set[str]] = None) -> int:
    """
    Clean test data from a specific table while preserving real user data.
    
    Args:
        table_name: Name of the table to clean
        user_id_field: Name of the user ID field in this table
        real_user_ids: Set of real user IDs to preserve (if None, identify based on patterns)
        
    Returns:
        Number of rows deleted
    """
    try:
        supabase = get_supabase()
        
        # Get all rows from the table
        response = supabase.table(table_name).select('*').execute()
        rows = response.data
        
        if not rows:
            logger.info(f"Table {table_name} is empty")
            return 0
        
        logger.info(f"Found {len(rows)} total rows in {table_name}")
        
        # Identify rows to delete
        rows_to_delete = []
        preserved_rows = []
        
        for row in rows:
            # If we have real user IDs list and this row belongs to a real user, preserve it
            if real_user_ids and user_id_field in row and row[user_id_field] in real_user_ids:
                preserved_rows.append(row)
                continue
                
            # Otherwise check patterns to see if it looks like test data
            if is_test_data(row):
                rows_to_delete.append(row)
            else:
                preserved_rows.append(row)
        
        # Delete identified test rows
        deleted_count = 0
        for row in rows_to_delete:
            if 'id' in row:
                delete_response = supabase.table(table_name).delete().eq('id', row['id']).execute()
                deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} test rows from {table_name}, preserved {len(preserved_rows)} rows")
        return deleted_count
    
    except Exception as e:
        logger.error(f"Error cleaning test data from {table_name}: {str(e)}")
        return 0

def clean_test_data_from_all_tables() -> Dict[str, int]:
    """
    Clean test data from all tables in production, preserving real user data.
    
    Returns:
        Dictionary mapping table names to number of rows deleted
    """
    # Get real user IDs first
    real_user_ids = get_real_user_ids()
    
    # Tables to clean in order (to handle foreign key constraints)
    tables = [
        {"name": "golf_shots", "user_id_field": "user_id"},
        {"name": "golf_holes", "user_id_field": "user_id"},
        {"name": "round_stats", "user_id_field": "user_id"},
        {"name": "golf_rounds", "user_id_field": "user_id"},
        {"name": "clubs", "user_id_field": "user_id"},
        {"name": "user_preferences", "user_id_field": "user_id"}
    ]
    
    results = {}
    
    for table_info in tables:
        deleted = clean_test_data_from_table(
            table_info["name"], 
            table_info["user_id_field"],
            real_user_ids
        )
        results[table_info["name"]] = deleted
    
    return results

def main():
    """Main function to clean test data from production environment."""
    logger.info("=== Cleaning test data from production Supabase database ===")
    logger.info(f"Using Supabase URL: {config['supabase']['url']}")
    
    # Verify we're in production environment
    if config['app']['environment'] != 'production':
        logger.error("Not in production environment! Aborting.")
        logger.error("Make sure APP_ENVIRONMENT=production is set")
        return 1
    
    # Confirmation
    confirm = input("This will DELETE TEST DATA from the production database. Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        logger.info("Operation cancelled by user")
        return 0
    
    # Clean test data from all tables
    logger.info("Cleaning test data from all tables...")
    results = clean_test_data_from_all_tables()
    
    # Summary
    logger.info("\n=== Cleaning Summary ===")
    total_rows = sum(results.values())
    logger.info(f"Total test rows deleted: {total_rows}")
    
    for table, count in results.items():
        logger.info(f"{table}: {count} test rows deleted")
    
    logger.info("\n✅ Test data cleaned from production database successfully!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())