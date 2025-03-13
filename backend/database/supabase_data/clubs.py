"""
Supabase data access functions for golf clubs.
"""
from typing import Dict, Any, List, Optional

from backend.database.supabase_data.common import logger, get_supabase

def get_user_clubs(user_id: str, token: str = None) -> List[Dict[str, Any]]:
    """
    Get clubs for a user.
    
    Args:
        user_id: Supabase user ID
        token: JWT token for authorization
        
    Returns:
        List of clubs
    """
    try:
        # Pass token to get_supabase to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('clubs') \
            .select('*') \
            .eq('user_id', user_id) \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting clubs for user {user_id}: {str(e)}")
        return []

def get_club(club_id: int, token: str = None) -> Optional[Dict[str, Any]]:
    """
    Get a specific club.
    
    Args:
        club_id: Club ID
        token: JWT token for authorization
        
    Returns:
        Club data or None if not found
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('clubs') \
            .select('*') \
            .eq('id', club_id) \
            .maybe_single() \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting club {club_id}: {str(e)}")
        return None

def create_club(user_id: str, club_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Create a new club.
    
    Args:
        user_id: Supabase user ID
        club_data: Club data
        token: JWT token for authorization
        
    Returns:
        Created club data or None if failed
    """
    try:
        # Ensure user_id is set and is a string
        club_data['user_id'] = str(user_id)
        
        # Log the user ID type and value for debugging
        logger.info(f"Creating club with user_id type: {type(user_id)}, value: {user_id}")
        
        # Pass token to get_supabase to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('clubs') \
            .insert(club_data) \
            .execute()
            
        # Log the response for debugging
        logger.info(f"Supabase club insert response: {response.data}")
        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase club error: {response.error}")
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating club for user {user_id}: {str(e)}")
        logger.exception(e)  # Log full exception with traceback
        return None

def update_club(club_id: int, club_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Update a club.
    
    Args:
        club_id: Club ID
        club_data: Updated club data
        token: JWT token for authorization
        
    Returns:
        Updated club data or None if failed
    """
    try:
        # Pass token to get_supabase to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('clubs') \
            .update(club_data) \
            .eq('id', club_id) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error updating club {club_id}: {str(e)}")
        return None

def delete_club(club_id: int, token: str = None) -> bool:
    """
    Delete a club.
    
    Args:
        club_id: Club ID
        token: JWT token for authorization
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Pass token to get_supabase to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('clubs') \
            .delete() \
            .eq('id', club_id) \
            .execute()
            
        return True
    except Exception as e:
        logger.error(f"Error deleting club {club_id}: {str(e)}")
        return False