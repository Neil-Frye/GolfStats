"""
Supabase data access functions for golf round statistics.
"""
import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from statistics import mean, median
from collections import defaultdict

from backend.database.supabase_data.common import logger, get_supabase

def create_round_stats(round_id: int, stats_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Create stats for a golf round.
    
    Args:
        round_id: Golf round ID
        stats_data: Golf round stats
        token: JWT token for authorization
        
    Returns:
        Created stats data or None if failed
    """
    try:
        # Prepare stats data
        stats_record = {
            'round_id': round_id,
            'fairways_hit': stats_data.get('fairways_hit', 0),
            'fairways_total': stats_data.get('fairways_total', 14),
            'greens_in_regulation': stats_data.get('greens_in_regulation', 0),
            'putts_total': stats_data.get('putts_total', 0),
        }
        
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        response = supabase.table('round_stats') \
            .insert(stats_record) \
            .execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating round stats: {str(e)}")
        return None

def add_round_stats(round_id: int, stats_data: Dict[str, Any], token: str = None) -> Optional[Dict[str, Any]]:
    """
    Add or update statistics for a golf round.
    
    Args:
        round_id: Golf round ID
        stats_data: Round statistics data
        token: JWT token for authorization
        
    Returns:
        Created/updated stats data or None if failed
    """
    try:
        # Pass token to satisfy RLS policies
        supabase = get_supabase(token)
        
        # Check if stats already exist for this round
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