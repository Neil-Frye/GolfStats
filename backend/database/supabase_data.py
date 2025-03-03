"""
Supabase data access module for GolfStats application.

This module provides functions to interact with Supabase tables.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import json
import datetime
from statistics import mean, median
from collections import defaultdict

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

def add_holes_for_round(round_id: int, holes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add multiple holes to a golf round.
    
    Args:
        round_id: Golf round ID
        holes_data: List of hole data dictionaries
        
    Returns:
        List of created hole data or empty list if failed
    """
    try:
        # Ensure round_id is set for each hole
        for hole_data in holes_data:
            hole_data['round_id'] = round_id
        
        supabase = get_supabase()
        response = supabase.table('golf_holes') \
            .insert(holes_data) \
            .execute()
            
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error adding holes to round {round_id}: {str(e)}")
        return []

def add_shots_for_hole(hole_id: int, shots_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add multiple shots to a golf hole.
    
    Args:
        hole_id: Golf hole ID
        shots_data: List of shot data dictionaries
        
    Returns:
        List of created shot data or empty list if failed
    """
    try:
        # Ensure hole_id is set for each shot
        for shot_data in shots_data:
            shot_data['hole_id'] = hole_id
        
        supabase = get_supabase()
        response = supabase.table('golf_shots') \
            .insert(shots_data) \
            .execute()
            
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error adding shots to hole {hole_id}: {str(e)}")
        return []

def add_round_stats(round_id: int, stats_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Add or update statistics for a golf round.
    
    Args:
        round_id: Golf round ID
        stats_data: Round statistics data
        
    Returns:
        Created/updated stats data or None if failed
    """
    try:
        # Check if stats already exist for this round
        supabase = get_supabase()
        existing = supabase.table('round_stats') \
            .select('id') \
            .eq('round_id', round_id) \
            .execute()
            
        stats_data['round_id'] = round_id
        
        if existing.data and len(existing.data) > 0:
            # Update existing stats
            stats_id = existing.data[0]['id']
            response = supabase.table('round_stats') \
                .update(stats_data) \
                .eq('id', stats_id) \
                .execute()
        else:
            # Create new stats
            response = supabase.table('round_stats') \
                .insert(stats_data) \
                .execute()
                
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error adding/updating stats for round {round_id}: {str(e)}")
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
        
# Statistics and aggregated data functions
def get_user_rounds_stats(user_id: str, timeframe: str = 'all', 
                          start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get aggregated statistics for a user's rounds.
    
    Args:
        user_id: Supabase user ID
        timeframe: Time period for stats (all, year, 90days, 30days, custom)
        start_date: Start date for custom timeframe (ISO format)
        end_date: End date for custom timeframe (ISO format)
        
    Returns:
        Dictionary of aggregated statistics
    """
    try:
        # Get rounds based on timeframe
        supabase = get_supabase()
        query = supabase.table('golf_rounds').select('*').eq('user_id', user_id)
        
        now = datetime.datetime.now()
        
        if timeframe == 'year':
            year_start = datetime.datetime(now.year, 1, 1).isoformat()
            query = query.gte('date', year_start)
        elif timeframe == '90days':
            ninety_days_ago = (now - datetime.timedelta(days=90)).isoformat()
            query = query.gte('date', ninety_days_ago)
        elif timeframe == '30days':
            thirty_days_ago = (now - datetime.timedelta(days=30)).isoformat()
            query = query.gte('date', thirty_days_ago)
        elif timeframe == 'custom' and start_date and end_date:
            query = query.gte('date', start_date).lte('date', end_date)
            
        rounds_response = query.order('date', desc=True).execute()
        rounds = rounds_response.data
        
        if not rounds:
            return {
                'rounds_count': 0,
                'average_score': 0,
                'statistics': {}
            }
            
        # Get all round IDs
        round_ids = [r['id'] for r in rounds]
        
        # Get round statistics for these rounds
        stats_response = supabase.table('round_stats').select('*') \
            .in_('round_id', round_ids) \
            .execute()
        round_stats = stats_response.data
        
        # Get all shots for these rounds
        shots_response = supabase.table('golf_shots').select('*') \
            .in_('round_id', round_ids) \
            .execute()
        shots = shots_response.data
        
        # Prepare results
        results = {
            'rounds_count': len(rounds),
            'rounds_dates': [r['date'] for r in rounds],
            'courses': [r['course'] for r in rounds],
            'scores': [r['total_score'] for r in rounds if 'total_score' in r],
            'statistics': {}
        }
        
        # Process basic statistics
        if rounds and 'total_score' in rounds[0]:
            results['average_score'] = round(sum(r['total_score'] for r in rounds if 'total_score' in r) / len(rounds), 1)
            results['lowest_score'] = min(r['total_score'] for r in rounds if 'total_score' in r)
            results['highest_score'] = max(r['total_score'] for r in rounds if 'total_score' in r)
        
        # Aggregate round statistics
        if round_stats:
            agg_stats = defaultdict(list)
            
            # Collect all values for each statistic
            for stat in round_stats:
                for key, value in stat.items():
                    if key not in ('id', 'round_id', 'created_at', 'updated_at') and value is not None:
                        agg_stats[key].append(value)
            
            # Calculate averages for each statistic
            for key, values in agg_stats.items():
                if values and all(isinstance(v, (int, float)) for v in values):
                    results['statistics'][key] = {
                        'average': round(mean(values), 2),
                        'median': round(median(values), 2),
                        'min': min(values),
                        'max': max(values),
                        'trend': [values[-min(5, len(values)):]]  # Recent values for trend
                    }
        
        # Process shot data for club statistics
        if shots:
            club_stats = defaultdict(list)
            
            for shot in shots:
                if 'club' in shot and shot['club'] and 'distance' in shot and shot['distance']:
                    club_stats[shot['club']].append(shot['distance'])
            
            results['club_distances'] = {}
            for club, distances in club_stats.items():
                if distances:
                    results['club_distances'][club] = {
                        'average': round(mean(distances), 1),
                        'median': round(median(distances), 1),
                        'min': min(distances),
                        'max': max(distances)
                    }
        
        # Calculate fairways hit percentage
        fairways_hit = sum(1 for stat in round_stats if 'fairways_hit' in stat and 'fairways_total' in stat 
                            and stat['fairways_hit'] is not None and stat['fairways_total'] is not None 
                            and stat['fairways_total'] > 0)
        fairways_total = sum(stat['fairways_total'] for stat in round_stats if 'fairways_total' in stat 
                            and stat['fairways_total'] is not None)
        
        if fairways_total > 0:
            results['fairways_percentage'] = round((fairways_hit / fairways_total) * 100, 1)
        
        # Calculate greens in regulation percentage
        gir_hit = sum(1 for stat in round_stats if 'gir' in stat and 'gir_total' in stat 
                      and stat['gir'] is not None and stat['gir_total'] is not None 
                      and stat['gir_total'] > 0)
        gir_total = sum(stat['gir_total'] for stat in round_stats if 'gir_total' in stat 
                       and stat['gir_total'] is not None)
        
        if gir_total > 0:
            results['gir_percentage'] = round((gir_hit / gir_total) * 100, 1)
        
        # Calculate average putts per round
        if round_stats and any('total_putts' in stat for stat in round_stats):
            results['average_putts'] = round(sum(stat['total_putts'] for stat in round_stats 
                                                if 'total_putts' in stat and stat['total_putts'] is not None) 
                                           / sum(1 for stat in round_stats if 'total_putts' in stat 
                                                and stat['total_putts'] is not None), 1)
        
        # Identify strengths and weaknesses based on percentiles
        if 'statistics' in results and results['statistics']:
            # For demonstration, we'll use some default benchmarks
            # In a real app, these would be compared to user goals or standard benchmarks
            strengths = []
            weaknesses = []
            
            # Example metrics to check
            metrics = {
                'average_drive_distance': {'good': 240, 'label': 'Driving Distance'},
                'fairways_percentage': {'good': 60, 'label': 'Fairways Hit'},
                'gir_percentage': {'good': 55, 'label': 'Greens in Regulation'},
                'average_putts': {'good': 33, 'label': 'Putts Per Round', 'lower_is_better': True},
                'sand_save_percentage': {'good': 40, 'label': 'Sand Saves'}
            }
            
            for metric, benchmark in metrics.items():
                # Check if we have this metric in our results
                value = None
                if metric in results:
                    value = results[metric]
                elif metric in results.get('statistics', {}):
                    value = results['statistics'][metric].get('average')
                
                if value is not None:
                    is_better = value <= benchmark['good'] if benchmark.get('lower_is_better') else value >= benchmark['good']
                    if is_better:
                        strengths.append({
                            'label': benchmark['label'],
                            'value': value,
                            'percentage': min(100, round((value / benchmark['good'] * 100) if not benchmark.get('lower_is_better') 
                                              else (benchmark['good'] / value * 100), 0))
                        })
                    else:
                        weaknesses.append({
                            'label': benchmark['label'],
                            'value': value,
                            'percentage': min(100, round((value / benchmark['good'] * 100) if not benchmark.get('lower_is_better') 
                                              else (benchmark['good'] / value * 100), 0))
                        })
            
            results['strengths'] = sorted(strengths, key=lambda x: x['percentage'], reverse=True)[:3]
            results['weaknesses'] = sorted(weaknesses, key=lambda x: x['percentage'])[:3]
            
        return results
            
    except Exception as e:
        logger.error(f"Error getting user rounds statistics: {str(e)}")
        return {
            'rounds_count': 0,
            'error': str(e)
        }