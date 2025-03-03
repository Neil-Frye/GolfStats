"""
Supabase data access module for GolfStats application.

This module provides functions to interact with Supabase tables.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import json
import datetime

from supabase import Client

# Add the project root directory to Python path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.supabase_client import get_supabase

# Configure logging
logger = logging.getLogger(__name__)

# Utility class for JSON serialization
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

# Golf round functions
def get_golf_rounds(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get golf rounds for a user.
    
    Args:
        user_id: Supabase user ID
        limit: Maximum number of rounds to retrieve
        
    Returns:
        List of golf rounds
    """
    try:
        supabase = get_supabase()
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

def get_golf_round(round_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific golf round.
    
    Args:
        round_id: Golf round ID
        
    Returns:
        Golf round data or None if not found
    """
    try:
        supabase = get_supabase()
        response = supabase.table('golf_rounds') \
            .select('*') \
            .eq('id', round_id) \
            .single() \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting golf round {round_id}: {str(e)}")
        return None

def create_golf_round(user_id: str, round_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new golf round.
    
    Args:
        user_id: Supabase user ID
        round_data: Golf round data
        
    Returns:
        Created golf round data or None if failed
    """
    try:
        # Ensure user_id is set
        round_data['user_id'] = user_id
        
        supabase = get_supabase()
        response = supabase.table('golf_rounds') \
            .insert(round_data) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating golf round: {str(e)}")
        return None

def update_golf_round(round_id: int, round_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a golf round.
    
    Args:
        round_id: Golf round ID
        round_data: Updated golf round data
        
    Returns:
        Updated golf round data or None if failed
    """
    try:
        supabase = get_supabase()
        response = supabase.table('golf_rounds') \
            .update(round_data) \
            .eq('id', round_id) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error updating golf round {round_id}: {str(e)}")
        return None

def delete_golf_round(round_id: int) -> bool:
    """
    Delete a golf round.
    
    Args:
        round_id: Golf round ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase()
        response = supabase.table('golf_rounds') \
            .delete() \
            .eq('id', round_id) \
            .execute()
            
        return True
    except Exception as e:
        logger.error(f"Error deleting golf round {round_id}: {str(e)}")
        return False

# Golf shot functions
def get_shots_for_round(round_id: int) -> List[Dict[str, Any]]:
    """
    Get shots for a specific golf round.
    
    Args:
        round_id: Golf round ID
        
    Returns:
        List of golf shots
    """
    try:
        supabase = get_supabase()
        response = supabase.table('golf_shots') \
            .select('*') \
            .eq('round_id', round_id) \
            .order('shot_number', desc=False) \
            .execute()
            
        return response.data
    except Exception as e:
        logger.error(f"Error getting shots for round {round_id}: {str(e)}")
        return []

def add_shot(round_id: int, shot_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Add a shot to a golf round.
    
    Args:
        round_id: Golf round ID
        shot_data: Shot data
        
    Returns:
        Created shot data or None if failed
    """
    try:
        # Ensure round_id is set
        shot_data['round_id'] = round_id
        
        supabase = get_supabase()
        response = supabase.table('golf_shots') \
            .insert(shot_data) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error adding shot to round {round_id}: {str(e)}")
        return None

# User preferences functions
def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """
    Get user preferences.
    
    Args:
        user_id: Supabase user ID
        
    Returns:
        User preferences data
    """
    try:
        supabase = get_supabase()
        response = supabase.table('user_preferences') \
            .select('*') \
            .eq('user_id', user_id) \
            .single() \
            .execute()
            
        return response.data or {}
    except Exception as e:
        logger.error(f"Error getting user preferences for {user_id}: {str(e)}")
        return {}

def update_user_preferences(user_id: str, preferences: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update user preferences.
    
    Args:
        user_id: Supabase user ID
        preferences: User preferences data
        
    Returns:
        Updated user preferences data or None if failed
    """
    try:
        # Check if preferences exist first
        existing = get_user_preferences(user_id)
        
        supabase = get_supabase()
        
        if existing:
            # Update existing preferences
            response = supabase.table('user_preferences') \
                .update(preferences) \
                .eq('user_id', user_id) \
                .execute()
        else:
            # Create new preferences
            preferences['user_id'] = user_id
            response = supabase.table('user_preferences') \
                .insert(preferences) \
                .execute()
                
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error updating user preferences for {user_id}: {str(e)}")
        return None