"""
Utility functions for handling golf shots data.
This module provides common functionality shared between course shots and range shots.
"""
from typing import Dict, Any, List, Optional, Union, Literal
from backend.database.supabase_data.common import logger, get_supabase

ShotContextType = Literal['hole', 'session']

def calculate_derived_metrics(shot_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate derived metrics for a shot based on available data.
    
    Args:
        shot_data: Shot data dictionary
        
    Returns:
        Shot data with calculated derived metrics
    """
    # Create a copy to avoid modifying the original
    shot_data_copy = shot_data.copy()
    
    # Calculate carry efficiency
    if ('carry_distance_yards' in shot_data_copy and 
        'ball_speed_mph' in shot_data_copy and 
        shot_data_copy.get('ball_speed_mph', 0) > 0):
        shot_data_copy['carry_efficiency'] = shot_data_copy['carry_distance_yards'] / shot_data_copy['ball_speed_mph']
        
    # Calculate height to carry ratio
    if ('height_feet' in shot_data_copy and 
        'carry_distance_yards' in shot_data_copy and 
        shot_data_copy.get('carry_distance_yards', 0) > 0):
        shot_data_copy['height_to_carry_ratio'] = shot_data_copy['height_feet'] / shot_data_copy['carry_distance_yards']
        
    # Calculate spin to launch ratio
    if ('spin_rate_rpm' in shot_data_copy and 
        'launch_angle_degrees' in shot_data_copy and 
        shot_data_copy.get('launch_angle_degrees', 0) > 0):
        shot_data_copy['spin_to_launch_ratio'] = shot_data_copy['spin_rate_rpm'] / shot_data_copy['launch_angle_degrees']
    
    return shot_data_copy

def prepare_shot_data(
    shot_data: Dict[str, Any], 
    context_id: int, 
    context_type: ShotContextType,
    shot_number: Optional[int] = None
) -> Dict[str, Any]:
    """
    Prepare shot data for insertion by setting common fields and calculating derived metrics.
    
    Args:
        shot_data: Original shot data dictionary
        context_id: ID of the context (hole_id or session_id)
        context_type: Type of context ('hole' or 'session')
        shot_number: Optional shot number (for sequencing)
        
    Returns:
        Prepared shot data
    """
    # Create a copy to avoid modifying the original
    prepared_data = shot_data.copy()
    
    # Set the appropriate ID field based on context type
    field_name = 'hole_id' if context_type == 'hole' else 'session_id'
    prepared_data[field_name] = context_id
    
    # If this is a hole shot, ensure session_id is None and vice versa
    if context_type == 'hole':
        prepared_data['session_id'] = None
        prepared_data['shot_type'] = prepared_data.get('shot_type', 'course')
    else:
        prepared_data['hole_id'] = None
        prepared_data['shot_type'] = prepared_data.get('shot_type', 'range')
        
    # Set source_system if not provided
    if 'source_system' not in prepared_data:
        prepared_data['source_system'] = 'manual'
    
    # Set shot number if provided
    if shot_number is not None:
        prepared_data['shot_number'] = shot_number
        
    # Calculate derived metrics
    return calculate_derived_metrics(prepared_data)

def insert_shots(
    shots_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    context_id: int,
    context_type: ShotContextType = 'hole',
    token: str = None
) -> Union[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Insert one or multiple shots into the database.
    
    Args:
        shots_data: Single shot data dictionary or list of shot dictionaries
        context_id: ID of the context (hole_id or session_id)
        context_type: Type of context ('hole' or 'session')
        token: JWT token for authorization
        
    Returns:
        Inserted shot data (single dict or list) or None/empty list if failed
    """
    try:
        # Handle single shot vs multiple shots
        is_single_shot = not isinstance(shots_data, list)
        shots_list = [shots_data] if is_single_shot else shots_data
        
        # Prepare each shot
        prepared_shots = []
        for i, shot in enumerate(shots_list):
            prepared_shots.append(prepare_shot_data(
                shot, 
                context_id, 
                context_type,
                shot_number=i+1 if len(shots_list) > 1 else shot.get('shot_number')
            ))
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('golf_shots').insert(prepared_shots).execute()
        
        # Return appropriate result based on input type
        if is_single_shot:
            return response.data[0] if response.data else None
        else:
            return response.data if response.data else []
            
    except Exception as e:
        error_msg = f"Error inserting {'shot' if is_single_shot else 'shots'} to {context_type} {context_id}: {str(e)}"
        logger.error(error_msg)
        return None if is_single_shot else []