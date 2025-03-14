"""
API routes for range sessions and shots.
"""
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from backend.auth.supabase_auth import get_authenticated_user
from backend.database.supabase_data.common import get_supabase
from backend.database.supabase_data.range_shots import (
    get_range_sessions, 
    get_range_session, 
    create_range_session, 
    update_range_session, 
    delete_range_session
)
from backend.database.supabase_data.shots import (
    get_range_shots,
    add_range_shot,
    add_range_shots,
    get_club_benchmarks,
    get_club_benchmark,
    update_shot,
    delete_shot
)
from backend.database.supabase_data.csv_import import import_csv_to_range_session

# Create a blueprint for range shots routes
range_shots_bp = Blueprint('range_shots', __name__)

@range_shots_bp.route('/api/range-sessions', methods=['GET'])
def api_get_range_sessions():
    """
    Get all range sessions for the authenticated user.
    
    Returns:
        JSON response with range sessions data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get limit from query params
        limit = request.args.get('limit', default=50, type=int)
        
        # Get range sessions
        sessions = get_range_sessions(user['id'], limit, token)
        
        return jsonify({
            "success": True,
            "sessions": sessions
        })
    except Exception as e:
        current_app.logger.error(f"Error getting range sessions: {str(e)}")
        return jsonify({"error": "Failed to get range sessions"}), 500

@range_shots_bp.route('/api/range-sessions/<int:session_id>', methods=['GET'])
def api_get_range_session(session_id: int):
    """
    Get a specific range session.
    
    Args:
        session_id: Range session ID
        
    Returns:
        JSON response with range session data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get range session
        session = get_range_session(session_id, token)
        
        if not session:
            return jsonify({"error": "Range session not found"}), 404
            
        # Check if session belongs to the user
        if session['user_id'] != user['id']:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Get shots for this session
        shots = get_range_shots(session_id, token)
        
        return jsonify({
            "success": True,
            "session": session,
            "shots": shots
        })
    except Exception as e:
        current_app.logger.error(f"Error getting range session {session_id}: {str(e)}")
        return jsonify({"error": "Failed to get range session"}), 500

@range_shots_bp.route('/api/range-sessions', methods=['POST'])
def api_create_range_session():
    """
    Create a new range session.
    
    Returns:
        JSON response with created range session data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get session data from request
        session_data = request.json
        if not session_data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['date', 'location']
        for field in required_fields:
            if field not in session_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Log the request data for debugging
        current_app.logger.info(f"Creating range session with data: {session_data}")
        current_app.logger.info(f"User ID: {user['id']}")
        
        # Create range session
        session = create_range_session(user['id'], session_data, token)
        
        if not session:
            return jsonify({"error": "Database error: Failed to create range session"}), 500
            
        return jsonify({
            "success": True,
            "session": session
        })
    except Exception as e:
        current_app.logger.error(f"Error creating range session: {str(e)}")
        current_app.logger.exception(e)  # Log full exception with traceback
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@range_shots_bp.route('/api/range-sessions/<int:session_id>', methods=['PUT'])
def api_update_range_session(session_id: int):
    """
    Update a range session.
    
    Args:
        session_id: Range session ID
        
    Returns:
        JSON response with updated range session data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get current session to verify ownership
        session = get_range_session(session_id, token)
        
        if not session:
            return jsonify({"error": "Range session not found"}), 404
            
        # Check if session belongs to the user
        if session['user_id'] != user['id']:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get session data from request
        session_data = request.json
        
        # Update range session
        updated_session = update_range_session(session_id, session_data, token)
        
        if not updated_session:
            return jsonify({"error": "Failed to update range session"}), 500
            
        return jsonify({
            "success": True,
            "session": updated_session
        })
    except Exception as e:
        current_app.logger.error(f"Error updating range session {session_id}: {str(e)}")
        return jsonify({"error": "Failed to update range session"}), 500

@range_shots_bp.route('/api/range-sessions/<int:session_id>', methods=['DELETE'])
def api_delete_range_session(session_id: int):
    """
    Delete a range session.
    
    Args:
        session_id: Range session ID
        
    Returns:
        JSON response with success status
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get current session to verify ownership
        session = get_range_session(session_id, token)
        
        if not session:
            return jsonify({"error": "Range session not found"}), 404
            
        # Check if session belongs to the user
        if session['user_id'] != user['id']:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Delete range session
        success = delete_range_session(session_id, token)
        
        if not success:
            return jsonify({"error": "Failed to delete range session"}), 500
            
        return jsonify({
            "success": True
        })
    except Exception as e:
        current_app.logger.error(f"Error deleting range session {session_id}: {str(e)}")
        return jsonify({"error": "Failed to delete range session"}), 500

@range_shots_bp.route('/api/range-sessions/<int:session_id>/shots', methods=['GET'])
def api_get_range_shots(session_id: int):
    """
    Get shots for a range session.
    
    Args:
        session_id: Range session ID
        
    Returns:
        JSON response with range shots data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get current session to verify ownership
        session = get_range_session(session_id, token)
        
        if not session:
            return jsonify({"error": "Range session not found"}), 404
            
        # Check if session belongs to the user
        if session['user_id'] != user['id']:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get shots
        shots = get_range_shots(session_id, token)
        
        return jsonify({
            "success": True,
            "shots": shots
        })
    except Exception as e:
        current_app.logger.error(f"Error getting range shots for session {session_id}: {str(e)}")
        return jsonify({"error": "Failed to get range shots"}), 500

@range_shots_bp.route('/api/range-sessions/<int:session_id>/shots', methods=['POST'])
def api_add_range_shot(session_id: int):
    """
    Add a shot to a range session.
    
    Args:
        session_id: Range session ID
        
    Returns:
        JSON response with created shot data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get current session to verify ownership
        session = get_range_session(session_id, token)
        
        if not session:
            return jsonify({"error": "Range session not found"}), 404
            
        # Check if session belongs to the user
        if session['user_id'] != user['id']:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get shot data from request
        shot_data = request.json
        
        # Add shot number if not provided
        if 'shot_number' not in shot_data:
            # Get current shots to determine the next shot number
            current_shots = get_range_shots(session_id, token)
            shot_data['shot_number'] = len(current_shots) + 1
        
        # Determine shot_type if not provided
        if 'shot_type' not in shot_data:
            # Default to 'range' for manually added shots
            shot_data['shot_type'] = 'range'
        
        # Determine source_system based on value or defaults
        if 'source_system' not in shot_data:
            # Default based on shot_type
            if shot_data.get('shot_type') == 'sim':
                # Try to determine which sim system
                if session.get('source_system'):
                    shot_data['source_system'] = session.get('source_system')
                else:
                    shot_data['source_system'] = 'simulator'
            else:
                shot_data['source_system'] = 'manual'
        
        # Add shot
        shot = add_range_shot(session_id, shot_data, token)
        
        if not shot:
            return jsonify({"error": "Failed to add range shot"}), 500
            
        return jsonify({
            "success": True,
            "shot": shot
        })
    except Exception as e:
        current_app.logger.error(f"Error adding range shot to session {session_id}: {str(e)}")
        return jsonify({"error": "Failed to add range shot"}), 500

@range_shots_bp.route('/api/range-sessions/<int:session_id>/shots/batch', methods=['POST'])
def api_add_range_shots(session_id: int):
    """
    Add multiple shots to a range session.
    
    Args:
        session_id: Range session ID
        
    Returns:
        JSON response with created shots data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get current session to verify ownership
        session = get_range_session(session_id, token)
        
        if not session:
            return jsonify({"error": "Range session not found"}), 404
            
        # Check if session belongs to the user
        if session['user_id'] != user['id']:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get shots data from request
        shots_data = request.json
        
        if not isinstance(shots_data, list):
            return jsonify({"error": "Shots data must be an array"}), 400
        
        # Process each shot to set defaults
        for shot in shots_data:
            # Determine shot_type if not provided
            if 'shot_type' not in shot:
                # Default to 'range' for manually added shots
                shot['shot_type'] = 'range'
            
            # Determine source_system based on value or defaults
            if 'source_system' not in shot:
                # Default based on shot_type
                if shot.get('shot_type') == 'sim':
                    # Try to determine which sim system
                    if session.get('source_system'):
                        shot['source_system'] = session.get('source_system')
                    else:
                        shot['source_system'] = 'simulator'
                else:
                    shot['source_system'] = 'manual'
        
        # Add shots
        shots = add_range_shots(session_id, shots_data, token)
        
        if not shots:
            return jsonify({"error": "Failed to add range shots"}), 500
            
        return jsonify({
            "success": True,
            "shots": shots
        })
    except Exception as e:
        current_app.logger.error(f"Error adding range shots to session {session_id}: {str(e)}")
        return jsonify({"error": "Failed to add range shots"}), 500

@range_shots_bp.route('/api/club-benchmarks', methods=['GET'])
def api_get_club_benchmarks():
    """
    Get benchmarks for all clubs of the authenticated user.
    
    Returns:
        JSON response with club benchmarks data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get shot_type filter if provided
        shot_type = request.args.get('shot_type')
        
        # Get club benchmarks
        benchmarks = get_club_benchmarks(user['id'], token)
        
        # Filter by shot_type if provided
        if shot_type and benchmarks:
            benchmarks = [b for b in benchmarks if b.get('shot_type') == shot_type]
        
        return jsonify({
            "success": True,
            "benchmarks": benchmarks
        })
    except Exception as e:
        current_app.logger.error(f"Error getting club benchmarks: {str(e)}")
        return jsonify({"error": "Failed to get club benchmarks"}), 500

@range_shots_bp.route('/api/club-benchmarks/<string:club>', methods=['GET'])
def api_get_club_benchmark(club: str):
    """
    Get benchmark for a specific club of the authenticated user.
    
    Args:
        club: Club name
        
    Returns:
        JSON response with club benchmark data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get shot_type filter if provided
        shot_type = request.args.get('shot_type')
        
        # Get club benchmark
        benchmark = get_club_benchmark(user['id'], club, shot_type, token)
        
        if not benchmark:
            return jsonify({"error": "Club benchmark not found"}), 404
            
        return jsonify({
            "success": True,
            "benchmark": benchmark
        })
    except Exception as e:
        current_app.logger.error(f"Error getting club benchmark for {club}: {str(e)}")
        return jsonify({"error": "Failed to get club benchmark"}), 500
        
@range_shots_bp.route('/api/shots/<string:shot_id>', methods=['PUT'])
def api_update_shot(shot_id: str):
    """
    Update a golf shot (works for both range and course shots).
    
    Args:
        shot_id: Shot ID
        
    Returns:
        JSON response with updated shot data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get shot data from request
        shot_data = request.json
        if not shot_data:
            return jsonify({"error": "No data provided"}), 400
            
        # First verify that the shot exists and belongs to the user
        supabase = get_supabase(token)
        
        # Get the shot to check its context (session or hole)
        shot_query = supabase.table('golf_shots') \
            .select('*') \
            .eq('id', shot_id) \
            .execute()
        
        if not shot_query.data:
            return jsonify({"error": "Shot not found"}), 404
            
        shot_info = shot_query.data[0]
        
        # Check ownership based on context
        if shot_info.get('session_id'):
            # This is a range shot, check if session belongs to user
            session_query = supabase.table('range_sessions') \
                .select('id') \
                .eq('id', shot_info['session_id']) \
                .eq('user_id', user['id']) \
                .execute()
                
            if not session_query.data:
                return jsonify({"error": "You do not have permission to update this shot"}), 403
        elif shot_info.get('hole_id'):
            # This is a course shot, check if hole's round belongs to user
            hole_query = supabase.table('golf_holes') \
                .select('round_id') \
                .eq('id', shot_info['hole_id']) \
                .execute()
                
            if not hole_query.data:
                return jsonify({"error": "Shot is associated with non-existent hole"}), 404
                
            round_id = hole_query.data[0]['round_id']
            
            round_query = supabase.table('golf_rounds') \
                .select('id') \
                .eq('id', round_id) \
                .eq('user_id', user['id']) \
                .execute()
                
            if not round_query.data:
                return jsonify({"error": "You do not have permission to update this shot"}), 403
        else:
            return jsonify({"error": "Shot is not associated with a session or hole"}), 400
            
        # Update the shot
        updated_shot = update_shot(shot_id, shot_data, token)
        
        if not updated_shot:
            return jsonify({"error": "Failed to update shot"}), 500
            
        return jsonify({
            "success": True,
            "shot": updated_shot
        })
    except Exception as e:
        current_app.logger.error(f"Error updating shot {shot_id}: {str(e)}")
        return jsonify({"error": f"Failed to update shot: {str(e)}"}), 500
        
@range_shots_bp.route('/api/shots/<string:shot_id>', methods=['GET'])
def api_get_shot(shot_id: str):
    """
    Get a golf shot (works for both range and course shots).
    
    Args:
        shot_id: Shot ID
        
    Returns:
        JSON response with shot data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get the shot
        supabase = get_supabase(token)
        shot_query = supabase.table('golf_shots') \
            .select('*') \
            .eq('id', shot_id) \
            .execute()
        
        if not shot_query.data:
            return jsonify({"error": "Shot not found"}), 404
            
        shot_info = shot_query.data[0]
        
        # Check ownership based on context
        if shot_info.get('session_id'):
            # This is a range shot, check if session belongs to user
            session_query = supabase.table('range_sessions') \
                .select('id') \
                .eq('id', shot_info['session_id']) \
                .eq('user_id', user['id']) \
                .execute()
                
            if not session_query.data:
                return jsonify({"error": "You do not have permission to view this shot"}), 403
        elif shot_info.get('hole_id'):
            # This is a course shot, check if hole's round belongs to user
            hole_query = supabase.table('golf_holes') \
                .select('round_id') \
                .eq('id', shot_info['hole_id']) \
                .execute()
                
            if not hole_query.data:
                return jsonify({"error": "Shot is associated with non-existent hole"}), 404
                
            round_id = hole_query.data[0]['round_id']
            
            round_query = supabase.table('golf_rounds') \
                .select('id') \
                .eq('id', round_id) \
                .eq('user_id', user['id']) \
                .execute()
                
            if not round_query.data:
                return jsonify({"error": "You do not have permission to view this shot"}), 403
        else:
            return jsonify({"error": "Shot is not associated with a session or hole"}), 400
        
        return jsonify({
            "success": True,
            "shot": shot_info
        })
    except Exception as e:
        current_app.logger.error(f"Error getting shot {shot_id}: {str(e)}")
        return jsonify({"error": f"Failed to get shot: {str(e)}"}), 500

@range_shots_bp.route('/api/shots/<string:shot_id>', methods=['DELETE'])
def api_delete_shot(shot_id: str):
    """
    Delete a golf shot (works for both range and course shots).
    
    Args:
        shot_id: Shot ID
        
    Returns:
        JSON response with success status
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # First verify that the shot exists and belongs to the user
        supabase = get_supabase(token)
        
        # Get the shot to check its context (session or hole)
        shot_query = supabase.table('golf_shots') \
            .select('*') \
            .eq('id', shot_id) \
            .execute()
        
        if not shot_query.data:
            return jsonify({"error": "Shot not found"}), 404
            
        shot_info = shot_query.data[0]
        
        # Check ownership based on context
        if shot_info.get('session_id'):
            # This is a range shot, check if session belongs to user
            session_query = supabase.table('range_sessions') \
                .select('id') \
                .eq('id', shot_info['session_id']) \
                .eq('user_id', user['id']) \
                .execute()
                
            if not session_query.data:
                return jsonify({"error": "You do not have permission to delete this shot"}), 403
        elif shot_info.get('hole_id'):
            # This is a course shot, check if hole's round belongs to user
            hole_query = supabase.table('golf_holes') \
                .select('round_id') \
                .eq('id', shot_info['hole_id']) \
                .execute()
                
            if not hole_query.data:
                return jsonify({"error": "Shot is associated with non-existent hole"}), 404
                
            round_id = hole_query.data[0]['round_id']
            
            round_query = supabase.table('golf_rounds') \
                .select('id') \
                .eq('id', round_id) \
                .eq('user_id', user['id']) \
                .execute()
                
            if not round_query.data:
                return jsonify({"error": "You do not have permission to delete this shot"}), 403
        else:
            return jsonify({"error": "Shot is not associated with a session or hole"}), 400
            
        # Delete the shot
        success = delete_shot(shot_id, token)
        
        if not success:
            return jsonify({"error": "Failed to delete shot"}), 500
            
        return jsonify({
            "success": True
        })
    except Exception as e:
        current_app.logger.error(f"Error deleting shot {shot_id}: {str(e)}")
        return jsonify({"error": f"Failed to delete shot: {str(e)}"}), 500

@range_shots_bp.route('/api/range-sessions/<int:session_id>/import-csv', methods=['POST'])
def api_import_csv(session_id: int):
    """
    Import shots from CSV file to a range session.
    
    Args:
        session_id: Range session ID
        
    Returns:
        JSON response with imported shots data
    """
    # Authenticate user
    user, token = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get current session to verify ownership
        session = get_range_session(session_id, token)
        
        if not session:
            return jsonify({"error": "Range session not found"}), 404
            
        # Check if session belongs to the user
        if session['user_id'] != user['id']:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Check if file was included in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        csv_file = request.files['file']
        
        # Check if the file has a name
        if csv_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Check if the file is a CSV
        if not csv_file.filename.endswith('.csv'):
            return jsonify({"error": "File must be a CSV"}), 400
        
        # Read CSV content
        csv_content = csv_file.read().decode('utf-8')
        
        # Get optional parameters
        source_system = request.form.get('source_system', None)
        shot_type = request.form.get('shot_type', 'range')
        
        # Enable debug mode if requested
        if request.form.get('debug_import', '0') == '1':
            import os
            os.environ['DEBUG_IMPORT'] = '1'
            current_app.logger.info("CSV import debug mode enabled")
        
        # Import CSV data with enhanced error handling
        shots, unmapped_fields, import_stats = import_csv_to_range_session(
            session_id, 
            csv_content,
            source_system,
            shot_type,
            token
        )
        
        # Check if import was successful
        if not shots:
            error_message = "No shots were imported"
            
            # Include any error messages from the import process
            if import_stats.get("errors"):
                error_message = import_stats["errors"][0]
                
            return jsonify({
                "success": False,
                "error": error_message,
                "unmapped_fields": unmapped_fields,
                "import_stats": import_stats
            }), 400
            
        # Success response with detailed stats
        response = {
            "success": True,
            "shots": shots,
            "count": len(shots),
            "unmapped_fields": unmapped_fields,
            "import_stats": import_stats
        }
        
        # Add any warnings to the response
        if import_stats.get("warnings"):
            response["warnings"] = import_stats["warnings"]
            
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Error importing CSV to session {session_id}: {str(e)}")
        current_app.logger.exception(e)  # Log the full traceback for debugging
        return jsonify({
            "error": f"Failed to import CSV: {str(e)}",
            "success": False
        }), 500