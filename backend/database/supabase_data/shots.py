"""
Supabase data access functions for golf shots.
"""
from typing import Dict, Any, List, Optional

from backend.database.supabase_data.common import logger, get_supabase

def get_golf_shots(hole_id: int, token: str = None) -> List[Dict[str, Any]]:
    """
    Get shots for a specific golf hole.
    
    Args:
        hole_id: Golf hole ID
        token: JWT token for authorization
        
    Returns:
        List of golf shots
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_shots') \
            .select('*') \
            .eq('hole_id', hole_id) \
            .order('shot_number', desc=False) \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting shots for golf hole {hole_id}: {str(e)}")
        return []

def add_golf_shot(hole_id: int, shot_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Add a shot to a golf hole.
    
    Args:
        hole_id: Golf hole ID
        shot_data: Shot data
        token: JWT token for authorization
        
    Returns:
        Created shot data or None if failed
    """
    try:
        # Ensure hole_id is set
        shot_data['hole_id'] = hole_id
        
        # Set shot_type to 'course' for on-course shots
        shot_data['shot_type'] = 'course'
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_shots') \
            .insert(shot_data) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error adding shot to golf hole {hole_id}: {str(e)}")
        return None

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
        # Ensure session_id is set and hole_id is null
        shot_data['session_id'] = session_id
        shot_data['hole_id'] = None
        
        # Set shot_type if not provided, default to 'range'
        if 'shot_type' not in shot_data:
            shot_data['shot_type'] = 'range'
            
        # Set source_system if not provided
        if 'source_system' not in shot_data:
            shot_data['source_system'] = 'manual'
        
        # Calculate derived metrics if possible
        if 'carry_distance_yards' in shot_data and 'ball_speed_mph' in shot_data and shot_data['ball_speed_mph'] > 0:
            shot_data['carry_efficiency'] = shot_data['carry_distance_yards'] / shot_data['ball_speed_mph']
            
        if 'height_feet' in shot_data and 'carry_distance_yards' in shot_data and shot_data['carry_distance_yards'] > 0:
            shot_data['height_to_carry_ratio'] = shot_data['height_feet'] / shot_data['carry_distance_yards']
            
        if 'spin_rate_rpm' in shot_data and 'launch_angle_degrees' in shot_data and shot_data['launch_angle_degrees'] > 0:
            shot_data['spin_to_launch_ratio'] = shot_data['spin_rate_rpm'] / shot_data['launch_angle_degrees']
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_shots') \
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
            shot_data['hole_id'] = None
            shot_data['shot_number'] = i + 1  # Auto-number shots
            
            # Set shot_type if not provided, default to 'range'
            if 'shot_type' not in shot_data:
                shot_data['shot_type'] = 'range'
                
            # Set source_system if not provided
            if 'source_system' not in shot_data:
                shot_data['source_system'] = 'manual'
            
            # Calculate derived metrics if possible
            if 'carry_distance_yards' in shot_data and 'ball_speed_mph' in shot_data and shot_data['ball_speed_mph'] > 0:
                shot_data['carry_efficiency'] = shot_data['carry_distance_yards'] / shot_data['ball_speed_mph']
                
            if 'height_feet' in shot_data and 'carry_distance_yards' in shot_data and shot_data['carry_distance_yards'] > 0:
                shot_data['height_to_carry_ratio'] = shot_data['height_feet'] / shot_data['carry_distance_yards']
                
            if 'spin_rate_rpm' in shot_data and 'launch_angle_degrees' in shot_data and shot_data['launch_angle_degrees'] > 0:
                shot_data['spin_to_launch_ratio'] = shot_data['spin_rate_rpm'] / shot_data['launch_angle_degrees']
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_shots') \
            .insert(shots_data) \
            .execute()
            
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error adding shots to range session {session_id}: {str(e)}")
        return []

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
        response = supabase.table('golf_shots') \
            .select('*') \
            .eq('session_id', session_id) \
            .order('shot_number', desc=False) \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting shots for range session {session_id}: {str(e)}")
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

def get_club_benchmark(user_id: str, club: str, shot_type: str = None, token: str = None) -> Optional[Dict[str, Any]]:
    """
    Get benchmark for a specific club of a user.
    
    Args:
        user_id: User ID
        club: Club name
        shot_type: Optional filter by shot type (course, sim, range)
        token: JWT token for authorization
        
    Returns:
        Club benchmark data or None if not found
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        query = supabase.from_('club_benchmark_data') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('club', club)
            
        # Add shot_type filter if provided
        if shot_type:
            query = query.eq('shot_type', shot_type)
            
        response = query.limit(1).execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error getting club benchmark for user {user_id}, club {club}: {str(e)}")
        return None
        
def add_shot(round_id: int, shot_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Add a shot to a golf round. This function is a higher-level wrapper that:
    1. Gets the appropriate hole data from the round
    2. Routes the shot to the correct add function based on shot type
    
    Args:
        round_id: Golf round ID
        shot_data: Shot data dictionary
        token: JWT token for authorization
        
    Returns:
        Created shot data or None if failed
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        
        # Get hole data if hole_number is provided
        hole_id = None
        if 'hole_number' in shot_data:
            hole_number = shot_data.pop('hole_number')  # Remove from shot data
            
            # Find the hole for this round with the matching hole_number
            hole_response = supabase.table('golf_holes') \
                .select('id') \
                .eq('round_id', round_id) \
                .eq('hole_number', hole_number) \
                .limit(1) \
                .execute()
                
            if hole_response.data:
                hole_id = hole_response.data[0]['id']
            else:
                logger.error(f"Hole number {hole_number} not found for round {round_id}")
                return None
                
        # Check shot_type if provided
        shot_type = shot_data.get('shot_type', 'course')  # Default to course
        
        if shot_type == 'range':
            # Add to range shots - using session_id instead of hole_id
            session_id = shot_data.get('session_id')
            if not session_id:
                logger.error("Session ID required for range shots")
                return None
            return add_range_shot(session_id, shot_data, token)
        else:
            # This is a course shot, requires hole_id
            if not hole_id:
                logger.error("Hole ID required for course shots")
                return None
            return add_golf_shot(hole_id, shot_data, token)
            
    except Exception as e:
        logger.error(f"Error adding shot to round {round_id}: {str(e)}")
        return None

def add_holes_for_round(round_id: int, holes_data: List[Dict[str, Any]], token: str = None) -> List[Dict[str, Any]]:
    """
    Add multiple holes to a golf round.
    
    Args:
        round_id: Golf round ID
        holes_data: List of hole data dictionaries
        token: JWT token for authorization
        
    Returns:
        List of created hole data or empty list if failed
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        
        # Ensure round_id is set for each hole
        for hole_data in holes_data:
            hole_data['round_id'] = round_id
            
        # Insert all holes at once
        response = supabase.table('golf_holes') \
            .insert(holes_data) \
            .execute()
            
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error adding holes for round {round_id}: {str(e)}")
        return []
        
def add_shots_for_hole(hole_id: int, shots_data: List[Dict[str, Any]], token: str = None) -> List[Dict[str, Any]]:
    """
    Add multiple shots to a golf hole.
    
    Args:
        hole_id: Golf hole ID
        shots_data: List of shot data dictionaries
        token: JWT token for authorization
        
    Returns:
        List of created shot data or empty list if failed
    """
    try:
        # Ensure hole_id is set for each shot and set shot_type to 'course'
        for shot_data in shots_data:
            shot_data['hole_id'] = hole_id
            shot_data['shot_type'] = shot_data.get('shot_type', 'course')
            
        # Insert all shots at once
        supabase = get_supabase(token)
        response = supabase.table('golf_shots') \
            .insert(shots_data) \
            .execute()
            
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error adding shots for hole {hole_id}: {str(e)}")
        return []

def get_shots_for_round(round_id: int, token: str = None) -> List[Dict[str, Any]]:
    """
    Get all shots for a specific golf round.
    
    Args:
        round_id: Golf round ID
        token: JWT token for authorization
        
    Returns:
        List of shots for the round
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        
        # First get all holes for this round
        holes_response = supabase.table('golf_holes') \
            .select('id') \
            .eq('round_id', round_id) \
            .execute()
            
        if not holes_response.data:
            logger.warning(f"No holes found for round {round_id}")
            return []
            
        # Get hole IDs
        hole_ids = [hole['id'] for hole in holes_response.data]
        
        # Get shots for all holes in this round
        shots_response = supabase.table('golf_shots') \
            .select('*') \
            .in_('hole_id', hole_ids) \
            .order('hole_id', desc=False) \
            .order('shot_number', desc=False) \
            .execute()
            
        return shots_response.data
    except Exception as e:
        logger.error(f"Error getting shots for round {round_id}: {str(e)}")
        return []