"""
Supabase client integration for GolfStats application.

This module provides a singleton client for accessing Supabase.
"""
import os
import logging
from typing import Dict, Any, Optional

from supabase import create_client, Client

# Add the project root directory to Python path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.config import config

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseClientSingleton:
    """Singleton class to manage Supabase client instance."""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """
        Return singleton instance of Supabase client.
        
        Returns:
            Supabase client instance
        """
        if cls._instance is None:
            # Get credentials from environment or config
            supabase_url = os.environ.get("SUPABASE_URL") or config["supabase"]["url"]
            # Try multiple environment variable names for the API key
            supabase_key = os.environ.get("SUPABASE_API_KEY") or os.environ.get("SUPABASE_KEY") or config["supabase"]["anon_key"]
            
            if not supabase_url or not supabase_key:
                logger.error("Supabase credentials not configured")
                raise ValueError("Supabase URL and key must be provided")
                
            # Create client
            cls._instance = create_client(supabase_url, supabase_key)
            logger.info(f"Supabase client initialized for {os.environ.get('APP_ENVIRONMENT', 'production')} environment")
            
        return cls._instance

# Function to get Supabase client
def get_supabase(jwt_token: str = None) -> Client:
    """
    Get Supabase client instance.
    
    Args:
        jwt_token: Optional JWT token to use for authorization
        
    Returns:
        Supabase client instance
    """
    # Get credentials from environment or config
    supabase_url = os.environ.get("SUPABASE_URL") or config["supabase"]["url"]
    supabase_key = os.environ.get("SUPABASE_API_KEY") or os.environ.get("SUPABASE_KEY") or config["supabase"]["anon_key"]
    
    # If a JWT token is provided, create a new client with the token
    if jwt_token:
        try:
            # Clean and validate the JWT token
            jwt_token = jwt_token.strip()
            
            if not jwt_token:
                logger.warning("Empty JWT token provided, falling back to anon client")
                return SupabaseClientSingleton.get_client()
                
            # Log some JWT information for debugging
            import base64
            import json
            
            # Decode the token to verify it's valid
            parts = jwt_token.split('.')
            if len(parts) != 3:
                logger.warning(f"Invalid JWT format (expected 3 parts, got {len(parts)}), falling back to anon client")
                return SupabaseClientSingleton.get_client()
                
            # Decode the payload part
            try:
                payload_bytes = parts[1].encode('utf-8')
                # Add padding if needed
                payload_bytes += b'=' * (4 - len(payload_bytes) % 4) if len(payload_bytes) % 4 else b''
                payload = json.loads(base64.urlsafe_b64decode(payload_bytes).decode('utf-8'))
                
                # Log detailed token info for debugging
                logger.info(f"JWT token details - role: {payload.get('role', 'unknown')}, "
                           f"sub: {payload.get('sub', 'unknown')}, "
                           f"exp: {payload.get('exp', 'unknown')}, "
                           f"aud: {payload.get('aud', 'unknown')}")
                
                # Check if token has expired
                if 'exp' in payload:
                    import time
                    current_time = time.time()
                    if payload['exp'] < current_time:
                        logger.warning(f"JWT token has expired, falling back to anon client (exp: {payload['exp']}, now: {current_time})")
                        return SupabaseClientSingleton.get_client()
                        
            except Exception as e:
                logger.warning(f"Failed to decode JWT payload: {str(e)}, falling back to anon client")
                return SupabaseClientSingleton.get_client()
            
            # Create a client with the JWT token
            from supabase import create_client
            client = create_client(supabase_url, supabase_key)
            
            # This is the correct pattern for supabase-py to use a JWT
            # Create a session with the provided token
            refresh_token = ""  # Not needed for session management, just access token
            client.auth.set_session(jwt_token, refresh_token)
            
            # Verify the session was set correctly by checking the current user
            try:
                user = client.auth.get_user()
                if user and hasattr(user, 'user'):
                    logger.info(f"JWT session confirmed with user_id: {user.user.id}")
                else:
                    logger.warning("JWT session created but user could not be retrieved, using it anyway")
            except Exception as e:
                logger.warning(f"Could not verify JWT session, but proceeding with authenticated client: {str(e)}")
            
            logger.info("Created Supabase client with JWT session")
            return client
            
        except Exception as e:
            logger.error(f"Error creating Supabase client with JWT: {str(e)}")
            # Fall back to regular client if there's an error
    
    # Use the singleton client when no token is provided or on error
    return SupabaseClientSingleton.get_client()