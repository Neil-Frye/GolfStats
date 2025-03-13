"""
Supabase data access functions for range sessions and shots.
"""
from typing import Dict, Any, List, Optional

from backend.database.supabase_data.common import logger, get_supabase

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
        # Ensure user_id is set
        session_data['user_id'] = user_id
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('range_sessions') \
            .insert(session_data) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating range session for user {user_id}: {str(e)}")
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
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('range_shots') \
            .select('*') \
            .eq('session_id', session_id) \
            .order('shot_number', desc=False) \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting shots for range session {session_id}: {str(e)}")
        return []

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
    try:
        # Ensure session_id is set
        shot_data['session_id'] = session_id
        
        # Calculate derived metrics if possible
        if 'carry_distance_yards' in shot_data and 'ball_speed_mph' in shot_data and shot_data['ball_speed_mph'] > 0:
            shot_data['carry_efficiency'] = shot_data['carry_distance_yards'] / shot_data['ball_speed_mph']
            
        if 'height_feet' in shot_data and 'carry_distance_yards' in shot_data and shot_data['carry_distance_yards'] > 0:
            shot_data['height_to_carry_ratio'] = shot_data['height_feet'] / shot_data['carry_distance_yards']
            
        if 'spin_rate_rpm' in shot_data and 'launch_angle_degrees' in shot_data and shot_data['launch_angle_degrees'] > 0:
            shot_data['spin_to_launch_ratio'] = shot_data['spin_rate_rpm'] / shot_data['launch_angle_degrees']
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('range_shots') \
            .insert(shot_data) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error adding shot to range session {session_id}: {str(e)}")
        return None

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
    try:
        # Ensure session_id and derived metrics are set for each shot
        for i, shot_data in enumerate(shots_data):
            shot_data['session_id'] = session_id
            shot_data['shot_number'] = i + 1  # Auto-number shots
            
            # Calculate derived metrics if possible
            if 'carry_distance_yards' in shot_data and 'ball_speed_mph' in shot_data and shot_data['ball_speed_mph'] > 0:
                shot_data['carry_efficiency'] = shot_data['carry_distance_yards'] / shot_data['ball_speed_mph']
                
            if 'height_feet' in shot_data and 'carry_distance_yards' in shot_data and shot_data['carry_distance_yards'] > 0:
                shot_data['height_to_carry_ratio'] = shot_data['height_feet'] / shot_data['carry_distance_yards']
                
            if 'spin_rate_rpm' in shot_data and 'launch_angle_degrees' in shot_data and shot_data['launch_angle_degrees'] > 0:
                shot_data['spin_to_launch_ratio'] = shot_data['spin_rate_rpm'] / shot_data['launch_angle_degrees']
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('range_shots') \
            .insert(shots_data) \
            .execute()
            
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error adding shots to range session {session_id}: {str(e)}")
        return []

def get_club_benchmarks(user_id: str, token: str = None) -> List[Dict[str, Any]]:
    """
    Get benchmarks for all clubs of a user.
    
    Args:
        user_id: User ID
        token: JWT token for authorization
        
    Returns:
        List of club benchmark data
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.from_('club_benchmark_data') \
            .select('*') \
            .eq('user_id', user_id) \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting club benchmarks for user {user_id}: {str(e)}")
        return []

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
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.from_('club_benchmark_data') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('club', club) \
            .limit(1) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error getting club benchmark for user {user_id}, club {club}: {str(e)}")
        return None