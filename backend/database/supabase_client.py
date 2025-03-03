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
            supabase_key = os.environ.get("SUPABASE_KEY") or config["supabase"]["anon_key"]
            
            if not supabase_url or not supabase_key:
                logger.error("Supabase credentials not configured")
                raise ValueError("Supabase URL and key must be provided")
                
            cls._instance = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized")
            
        return cls._instance

# Function to get Supabase client
def get_supabase() -> Client:
    """
    Get Supabase client instance.
    
    Returns:
        Supabase client instance
    """
    return SupabaseClientSingleton.get_client()