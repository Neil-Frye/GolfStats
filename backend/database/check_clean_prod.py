"""
Check and verify the production Supabase database is clean.

This script connects to the production Supabase instance and checks for existing data.
It also verifies OAuth setup for Google login works properly.
"""
import os
import sys
import logging
from typing import Dict, Any, List

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

def check_tables_empty() -> Dict[str, bool]:
    """
    Check if each table in production Supabase is empty.
    
    Returns:
        Dictionary mapping table names to boolean (True if empty)
    """
    supabase = get_supabase()
    tables = [
        "user_preferences",
        "golf_rounds",
        "golf_holes",
        "golf_shots",
        "round_stats",
        "clubs"
    ]
    
    results = {}
    
    for table in tables:
        try:
            response = supabase.table(table).select('*').execute()
            is_empty = len(response.data) == 0
            results[table] = is_empty
            logger.info(f"Table {table}: {'Empty' if is_empty else f'Contains {len(response.data)} rows'}")
        except Exception as e:
            logger.error(f"Error checking table {table}: {str(e)}")
            results[table] = None
    
    return results

def check_google_oauth_config() -> bool:
    """
    Check if Google OAuth is properly configured.
    
    Returns:
        True if Google OAuth appears to be properly configured
    """
    # Check for Google OAuth credentials
    client_id = config['google']['oauth']['client_id']
    client_secret = config['google']['oauth']['client_secret']
    redirect_uri = config['google']['oauth']['redirect_uri']
    
    has_credentials = bool(client_id and client_secret)
    
    if has_credentials:
        logger.info(f"Google OAuth configured with client ID: {client_id[:5]}...{client_id[-5:]} and redirect URI: {redirect_uri}")
    else:
        logger.warning("Google OAuth credentials are missing")
    
    return has_credentials

def check_supabase_redirect_urls() -> Dict[str, Any]:
    """
    Check Supabase auth settings for proper redirect URLs.
    
    Note: This cannot be done through the API without admin credentials.
    This function only provides information on what needs to be set.
    
    Returns:
        Dictionary with information about required redirect URLs
    """
    # This is informational only - redirects must be set in Supabase dashboard
    app_url = os.environ.get('APP_URL', 'https://golfstats-prod.vercel.app')
    
    required_redirects = [
        f"{app_url}/",
        f"{app_url}/auth/callback",
        f"{app_url}/auth/google/callback"
    ]
    
    logger.info("Required redirect URLs for Supabase Auth settings:")
    for url in required_redirects:
        logger.info(f"  - {url}")
    
    return {
        "app_url": app_url,
        "required_redirects": required_redirects
    }

def main():
    """Main function to check and verify production environment."""
    logger.info("Checking production Supabase environment...")
    logger.info(f"Using Supabase URL: {config['supabase']['url']}")
    
    logger.info("\n1. Checking if tables are empty...")
    table_status = check_tables_empty()
    
    all_empty = all(status for status in table_status.values() if status is not None)
    if all_empty:
        logger.info("✅ All tables are empty")
    else:
        non_empty_tables = [table for table, status in table_status.items() if status is False]
        logger.info(f"⚠️ The following tables are not empty: {', '.join(non_empty_tables)}")
    
    logger.info("\n2. Checking Google OAuth configuration...")
    oauth_configured = check_google_oauth_config()
    if oauth_configured:
        logger.info("✅ Google OAuth appears to be configured")
    else:
        logger.info("❌ Google OAuth is not properly configured")
        logger.info("  You need to set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env.production file")
    
    logger.info("\n3. Checking Supabase Auth redirect settings (informational)...")
    redirect_info = check_supabase_redirect_urls()
    logger.info("⚠️ Make sure these redirect URLs are configured in your Supabase Auth settings")
    
    # Summary
    logger.info("\n=== Summary ===")
    logger.info(f"Production Supabase URL: {config['supabase']['url']}")
    logger.info(f"Tables empty: {'All empty' if all_empty else 'Some have data'}")
    logger.info(f"Google OAuth: {'Configured' if oauth_configured else 'Not configured'}")
    logger.info(f"Application URL: {redirect_info['app_url']}")
    
    logger.info("\nIMPORTANT: If you need to create tables in production, run:")
    logger.info("  APP_ENVIRONMENT=production python -m backend.database.supabase_tables")
    
    logger.info("\nNext steps for setting up user preferences:")
    logger.info("  1. After Google login, you'll need to create preferences in the user_preferences table")
    logger.info("  2. You can edit backend/database/init_user_profiles.py to customize this process")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())