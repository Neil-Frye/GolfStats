"""
Supabase data access functions for golf shots and holes.
"""
from typing import Dict, Any, List, Optional

from backend.database.supabase_data.common import logger, get_supabase

def get_shots_for_round(round_id: int, token: str = None) -> List[Dict[str, Any]]:
    """
    Get shots for a specific golf round.
    
    Args:
        round_id: Golf round ID
        token: JWT token for authorization
        
    Returns:
        List of golf shots
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_shots') \
            .select('*') \
            .eq('round_id', round_id) \
            .order('shot_number', desc=False) \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting shots for round {round_id}: {str(e)}")
        return []

def add_shot(round_id: int, shot_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Add a shot to a golf round.
    
    Args:
        round_id: Golf round ID
        shot_data: Shot data
        token: JWT token for authorization
        
    Returns:
        Created shot data or None if failed
    """
    try:
        # Ensure round_id is set
        shot_data['round_id'] = round_id
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_shots') \
            .insert(shot_data) \
            .execute()
            
        return response.data[0] if response.data else None
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
        # Ensure round_id is set for each hole
        for hole_data in holes_data:
            hole_data['round_id'] = round_id
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_holes') \
            .insert(holes_data) \
            .execute()
            
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error adding holes to round {round_id}: {str(e)}")
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
        # Ensure hole_id is set for each shot
        for shot_data in shots_data:
            shot_data['hole_id'] = hole_id
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_shots') \
            .insert(shots_data) \
            .execute()
            
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error adding shots to hole {hole_id}: {str(e)}")
        return []