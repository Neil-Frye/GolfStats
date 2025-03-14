"""
Supabase data access functions for range sessions and shots.
DEPRECATED: The functions for range shots have been moved to shots.py
Only range session management remains in this file.
"""
from typing import Dict, Any, List, Optional

from backend.database.supabase_data.common import logger, get_supabase
from backend.database.supabase_data.shots import get_shots, add_shot_to_context, add_shots_to_context

def get_range_sessions(user_id: str, limit: int = 50, token: str = None) -> List[Dict[str, Any]]:
    """
    Get range sessions for a user.
    
    Args:
        user_id: User ID
        limit: Maximum number of sessions to return
        token: JWT token for authorization
        
    Returns:
        List of range sessions
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('range_sessions') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('date', desc=True) \
            .limit(limit) \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting range sessions for user {user_id}: {str(e)}")
        return []

def get_range_session(session_id: int, token: str = None) -> Optional[Dict[str, Any]]:
    """
    Get a specific range session.
    
    Args:
        session_id: Range session ID
        token: JWT token for authorization
        
    Returns:
        Range session data or None if not found
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('range_sessions') \
            .select('*') \
            .eq('id', session_id) \
            .limit(1) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error getting range session {session_id}: {str(e)}")
        return None

def create_range_session(user_id: str, session_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Create a new range session.
    
    Args:
        user_id: User ID
        session_data: Range session data
        token: JWT token for authorization
        
    Returns:
        Created range session data or None if failed
    """
    try:
        # Create a copy of session_data to avoid modifying the original
        session_data_copy = session_data.copy()
        
        # Ensure user_id is set correctly in a format that works with RLS policies
        session_data_copy['user_id'] = str(user_id)
        
        # Log the user ID type and value for debugging
        logger.info(f"Creating range session with user_id type: {type(user_id)}, value: {user_id}")
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('range_sessions') \
            .insert(session_data_copy) \
            .execute()
            
        # Log the response for debugging
        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase range session error: {response.error}")
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating range session for user {user_id}: {str(e)}")
        logger.exception(e)  # Log full exception with traceback
        return None

def update_range_session(session_id: int, session_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Update a range session.
    
    Args:
        session_id: Range session ID
        session_data: Updated range session data
        token: JWT token for authorization
        
    Returns:
        Updated range session data or None if failed
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('range_sessions') \
            .update(session_data) \
            .eq('id', session_id) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error updating range session {session_id}: {str(e)}")
        return None

def delete_range_session(session_id: int, token: str = None) -> bool:
    """
    Delete a range session.
    
    Args:
        session_id: Range session ID
        token: JWT token for authorization
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('range_sessions') \
            .delete() \
            .eq('id', session_id) \
            .execute()
            
        # Check if anything was deleted
        return bool(response.data)
    except Exception as e:
        logger.error(f"Error deleting range session {session_id}: {str(e)}")
        return False

def get_range_shots(session_id: int, token: str = None) -> List[Dict[str, Any]]:
    """
    Get shots for a specific range session.
    
    Args:
        session_id: Range session ID
        token: JWT token for authorization
        
    Returns:
        List of range shots
    """
    # DEPRECATED: Use shots.get_shots(session_id, 'session', token) instead
    return get_shots(session_id, 'session', token)

def add_range_shot(session_id: int, shot_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Add a shot to a range session.
    
    Args:
        session_id: Range session ID
        shot_data: Shot data
        token: JWT token for authorization
        
    Returns:
        Created shot data or None if failed
    """
    # DEPRECATED: Use shots.add_shot_to_context(session_id, shot_data, 'session', token) instead
    return add_shot_to_context(session_id, shot_data, 'session', token)

def add_range_shots(session_id: int, shots_data: List[Dict[str, Any]], token: str = None) -> List[Dict[str, Any]]:
    """
    Add multiple shots to a range session.
    
    Args:
        session_id: Range session ID
        shots_data: List of shot data dictionaries
        token: JWT token for authorization
        
    Returns:
        List of created shot data or empty list if failed
    """
    # DEPRECATED: Use shots.add_shots_to_context(session_id, shots_data, 'session', token) instead
    return add_shots_to_context(session_id, shots_data, 'session', token)

# Club benchmark functions are deprecated in this file and moved to shots.py
# These implementations remain here for backward compatibility but will be removed in a future update

def get_club_benchmarks(user_id: str, token: str = None) -> List[Dict[str, Any]]:
    """
    Get benchmarks for all clubs of a user.
    
    Args:
        user_id: User ID
        token: JWT token for authorization
        
    Returns:
        List of club benchmark data
    """
    # Import here to avoid circular imports
    from backend.database.supabase_data.shots import get_club_benchmarks as shots_get_club_benchmarks
    return shots_get_club_benchmarks(user_id, token)

def get_club_benchmark(user_id: str, club: str, token: str = None) -> Optional[Dict[str, Any]]:
    """
    Get benchmark for a specific club of a user.
    
    Args:
        user_id: User ID
        club: Club name
        token: JWT token for authorization
        
    Returns:
        Club benchmark data or None if not found
    """
    # Import here to avoid circular imports
    from backend.database.supabase_data.shots import get_club_benchmark as shots_get_club_benchmark
    return shots_get_club_benchmark(user_id, club, None, token)