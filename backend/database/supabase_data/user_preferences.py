"""
Supabase data access functions for user preferences.
"""
from typing import Dict, Any, Optional

from backend.database.supabase_data.common import logger, get_supabase

def get_user_preferences(user_id: str, token: str = None) -> Dict[str, Any]:
    """
    Get user preferences.
    
    Args:
        user_id: Supabase user ID
        token: JWT token for authorization
        
    Returns:
        User preferences data
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('user_preferences') \
            .select('*') \
            .eq('user_id', user_id) \
            .maybe_single() \
            .execute()
            
        return response.data or {}
    except Exception as e:
        logger.error(f"Error getting user preferences for {user_id}: {str(e)}")
        return {}

def update_user_preferences(user_id: str, preferences: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Update user preferences.
    
    Args:
        user_id: Supabase user ID
        preferences: User preferences data
        token: JWT token for authorization
        
    Returns:
        Updated user preferences data or None if failed
    """
    try:
        # Check if preferences exist first - pass token for RLS
        existing = get_user_preferences(user_id, token)
        
        # Pass token to get_supabase to satisfy RLS policies
        supabase = get_supabase(token)
        
        # Enhanced logging
        logger.info(f"User ID: {user_id}, Token present: {bool(token)}")
        logger.info(f"Existing preferences: {existing}")
        logger.info(f"New preferences to save: {preferences}")
        
        if existing:
            # Update existing preferences
            response = supabase.table('user_preferences') \
                .update(preferences) \
                .eq('user_id', user_id) \
                .execute()
            logger.info(f"Updated preferences for user {user_id}")
        else:
            # Create new preferences
            preferences['user_id'] = user_id
            logger.info(f"Creating new preferences for user {user_id}: {preferences}")
            response = supabase.table('user_preferences') \
                .insert(preferences) \
                .execute()
                
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error updating user preferences for {user_id}: {str(e)}")
        return None