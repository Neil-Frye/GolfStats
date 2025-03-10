"""
GolfStats Vercel Handler - Custom lightweight implementation for serverless deployment.
This is a completely independent version that doesn't import the main backend code,
avoiding all heavy dependencies.
"""
import os
import json
from flask import Flask, jsonify, request, g
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configure Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_API_KEY")

def get_supabase() -> Client:
    """Get or create a Supabase client for the current request."""
    if not hasattr(g, 'supabase'):
        g.supabase = create_client(supabase_url, supabase_key)
    return g.supabase

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'environment': os.environ.get('APP_ENVIRONMENT', 'production'),
        'serverless': True
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get the current authenticated user."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        supabase = get_supabase()
        user = supabase.auth.get_user(token)
        return jsonify({'user': user})
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@app.route('/api/users/<int:user_id>/rounds', methods=['GET'])
def get_user_rounds(user_id):
    """Get golf rounds for a specific user."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        supabase = get_supabase()
        
        # Get rounds from database
        response = supabase.table('golf_rounds').select('*').eq('user_id', user_id).execute()
        
        return jsonify({
            'rounds': response.data,
            'count': len(response.data),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scraper/<source>', methods=['GET'])
def mock_scraper_endpoint(source):
    """Mock implementation of scraper endpoints."""
    return jsonify({
        'status': 'success',
        'message': f'This is a mock implementation of the {source} scraper for serverless deployment',
        'data': [],
        'source': source,
        'serverless': True
    })

if __name__ == '__main__':
    # Only for local testing - Vercel uses the app variable directly
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))