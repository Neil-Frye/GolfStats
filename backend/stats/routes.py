"""
API routes for golf statistics.
"""
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from backend.auth import require_auth, get_current_user
from backend.database.supabase_data.stats import (
    get_user_rounds_stats
)

# Create a blueprint for stats routes
stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')

@stats_bp.route('/', methods=['GET'])
@require_auth
def get_stats():
    """Get user statistics for various timeframes."""
    user = get_current_user()
    timeframe = request.args.get('timeframe', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    stats = get_user_rounds_stats(
        user_id=user['id'], 
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify({
        "stats": stats
    })