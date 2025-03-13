"""
Supabase data access functions for golf rounds.
"""
from typing import Dict, Any, List, Optional

from backend.database.supabase_data.common import logger, get_supabase

def get_golf_rounds(user_id: str, limit: int = 100, token: str = None) -> List[Dict[str, Any]]:
    """
    Get golf rounds for a user.
    
    Args:
        user_id: Supabase user ID
        limit: Maximum number of rounds to retrieve
        token: JWT token for authorization
        
    Returns:
        List of golf rounds
    """
    try:
        # Pass token to the client to ensure RLS policies are respected
        supabase = get_supabase(token)
        response = supabase.table('golf_rounds') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('date', desc=True) \
            .limit(limit) \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting golf rounds: {str(e)}")
        return []

def get_golf_round(round_id: int, token: str = None) -> Optional[Dict[str, Any]]:
    """
    Get a specific golf round.
    
    Args:
        round_id: Golf round ID
        token: JWT token for authorization
        
    Returns:
        Golf round data or None if not found
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_rounds') \
            .select('*') \
            .eq('id', round_id) \
            .maybe_single() \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting golf round {round_id}: {str(e)}")
        return None

def create_golf_round(user_id: str, round_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Create a new golf round.
    
    Args:
        user_id: Supabase user ID
        round_data: Golf round data
        token: JWT token for authorization
        
    Returns:
        Created golf round data or None if failed
    """
    try:
        # Extract stats if present
        stats_data = round_data.pop('stats', None)
        
        # Ensure user_id is set and is a string
        round_data['user_id'] = str(user_id)
        
        # Log the user ID type and value for debugging
        logger.info(f"Creating golf round with user_id type: {type(user_id)}, value: {user_id}")
        
        # Pass token to get_supabase to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_rounds') \
            .insert(round_data) \
            .execute()
            
        # Log the response for debugging
        logger.info(f"Supabase insert response: {response.data}")
        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error: {response.error}")
            
        round_result = response.data[0] if response.data else None
        
        # If round was created and stats data exists, create stats record
        if round_result and stats_data:
            from backend.database.supabase_data.stats import create_round_stats
            create_round_stats(round_result['id'], stats_data, token)
            
        return round_result
    except Exception as e:
        logger.error(f"Error creating golf round: {str(e)}")
        logger.exception(e)  # Log full exception with traceback
        return None

def update_golf_round(round_id: int, round_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Update a golf round.
    
    Args:
        round_id: Golf round ID
        round_data: Updated golf round data
        token: JWT token for authorization
        
    Returns:
        Updated golf round data or None if failed
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_rounds') \
            .update(round_data) \
            .eq('id', round_id) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error updating golf round {round_id}: {str(e)}")
        return None

def delete_golf_round(round_id: int, token: str = None) -> bool:
    """
    Delete a golf round.
    
    Args:
        round_id: Golf round ID
        token: JWT token for authorization
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_rounds') \
            .delete() \
            .eq('id', round_id) \
            .execute()
            
        return True
    except Exception as e:
        logger.error(f"Error deleting golf round {round_id}: {str(e)}")
        return False