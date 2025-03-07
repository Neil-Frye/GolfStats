"""
Set up the production Supabase database from scratch.

This script creates all the necessary tables in the production environment
and ensures proper configuration for Google OAuth login.
"""
import os
import sys
import logging
import json
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

# Now import the rest of our modules
from backend.database.supabase_client import get_supabase
from backend.database.supabase_tables import create_tables
from config.config import config

def setup_production_database() -> bool:
    """
    Set up the production database with all required tables.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check Supabase credentials
        if not config['supabase']['url'] or not config['supabase']['anon_key']:
            logger.error("Production Supabase credentials not configured.")
            logger.error("Make sure SUPABASE_URL and SUPABASE_API_KEY are set in .env.production")
            return False
            
        # Get Supabase client to verify connection
        logger.info("Connecting to production Supabase...")
        supabase = get_supabase()
        
        # Create tables using the existing function
        logger.info("Creating database tables...")
        result = create_tables()
        
        if result:
            logger.info("✅ Successfully created all tables in production Supabase")
        else:
            logger.error("❌ Failed to create all tables in production")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error setting up production database: {str(e)}")
        return False

def verify_oauth_configuration() -> bool:
    """
    Verify that Google OAuth is properly configured for production.
    
    Returns:
        bool: True if correctly configured
    """
    # Check for Google OAuth credentials
    client_id = config['google']['oauth']['client_id']
    client_secret = config['google']['oauth']['client_secret']
    redirect_uri = config['google']['oauth']['redirect_uri']
    
    if not client_id or not client_secret:
        logger.error("Google OAuth credentials not configured.")
        logger.error("Make sure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set in .env.production")
        return False
    
    # Check if the redirect URI is properly set for production
    prod_url = os.environ.get('APP_URL', 'https://golfstats-prod.vercel.app')
    if prod_url not in redirect_uri and 'localhost' in redirect_uri:
        logger.warning(f"⚠️ Redirect URI ({redirect_uri}) may not be suitable for production")
        logger.warning(f"Consider setting it to {prod_url}/auth/google/callback")
    else:
        logger.info(f"✅ Google OAuth redirect URI looks good: {redirect_uri}")
    
    logger.info("Google OAuth configuration verification:")
    logger.info(f"- Client ID: {client_id[:5]}...{client_id[-5:] if len(client_id) > 10 else ''}")
    logger.info(f"- Redirect URI: {redirect_uri}")
    
    return True

def main():
    """Main function to set up production environment."""
    logger.info("=== Setting up production Supabase environment ===")
    
    # First, check if we have the required credentials
    if not config['supabase']['url']:
        logger.error("Missing SUPABASE_URL in configuration")
        logger.error("Make sure you've set up .env.production with your production credentials")
        return 1
    
    # Display environment info
    logger.info(f"Using Supabase URL: {config['supabase']['url']}")
    logger.info(f"Environment: {config['app']['environment']}")
    
    # Set up the database
    logger.info("\n1. Setting up production database tables...")
    db_success = setup_production_database()
    
    # Verify Google OAuth
    logger.info("\n2. Verifying Google OAuth configuration...")
    oauth_success = verify_oauth_configuration()
    
    # Print manual configuration reminders
    logger.info("\n3. Manual configuration reminders...")
    app_url = os.environ.get('APP_URL', 'https://golfstats-prod.vercel.app')
    
    logger.info("Required Supabase Auth redirect URLs (configure in Supabase dashboard):")
    for url in [f"{app_url}/", f"{app_url}/auth/callback", f"{app_url}/auth/google/callback"]:
        logger.info(f"  - {url}")
    
    # Final summary
    logger.info("\n=== Setup Summary ===")
    logger.info(f"Database setup: {'✅ Success' if db_success else '❌ Failed'}")
    logger.info(f"OAuth verification: {'✅ Success' if oauth_success else '❌ Failed'}")
    
    logger.info("\nNext steps:")
    logger.info("1. If using Vercel, make sure all environment variables are configured in Vercel dashboard")
    logger.info("2. Configure the Auth settings in Supabase dashboard")
    logger.info("3. Test Google OAuth login in the production environment")
    
    if db_success and oauth_success:
        logger.info("\n✅ Production setup completed successfully!")
        return 0
    else:
        logger.error("\n❌ Production setup had issues, see logs above for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())