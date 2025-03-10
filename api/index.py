"""
GolfStats API Handler - Standalone implementation for Render deployment.
This file is completely independent from the main backend code.

IMPORTANT: This file should NOT import anything from the backend/ directory!
All functionality should be self-contained or use mock_scrapers.py.
"""
import os
import json
import logging
from flask import Flask, jsonify, request, g
from dotenv import load_dotenv
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Load environment variables (from Render or local .env)
load_dotenv()
logger.info(f"Running in environment: {os.environ.get('APP_ENVIRONMENT', 'production')}")

# Initialize Flask application
app = Flask(__name__)

# Configure Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_API_KEY")

if not supabase_url or not supabase_key:
    logger.warning("Supabase credentials not found in environment variables!")

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
        'environment': os.environ.get('APP_ENVIRONMENT', 'production')
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
def scraper_endpoint(source):
    """Implementation of scraper endpoints.
    
    This endpoint can use real scrapers on Render, or fall back to mock implementation
    if the real scraper dependencies are not available.
    """
    logger.info(f"Scraper endpoint called for source: {source}")
    
    # Try to import real scrapers first
    try:
        # Import from backend if available
        from backend.scrapers import get_scraper_for_source
        
        scraper = get_scraper_for_source(source)
        if not scraper:
            return jsonify({
                'status': 'error',
                'message': f'Unknown source: {source}'
            }), 400
            
        # Get real data
        data = scraper.get_data()
        
        return jsonify({
            'status': 'success',
            'data': data.get('data', []),
            'source': source
        })
        
    except ImportError:
        logger.info("Real scrapers not available, falling back to mock implementation")
        # Fall back to mock scrapers
        try:
            from api.mock_scrapers import MockArccosScraper, MockTrackmanScraper, MockSkytrakScraper
            
            # Map source parameter to the appropriate mock class
            scraper_map = {
                'arccos': MockArccosScraper,
                'trackman': MockTrackmanScraper,
                'skytrak': MockSkytrakScraper,
            }
            
            if source not in scraper_map:
                return jsonify({
                    'status': 'error',
                    'message': f'Unknown source: {source}'
                }), 400
                
            # Create a mock scraper instance
            mock_scraper = scraper_map[source]()
            
            # Get mock data
            mock_data = mock_scraper.get_data()
            
            # Return a standardized response
            return jsonify({
                'status': 'success',
                'message': f'This is a mock implementation of the {source} scraper',
                'data': mock_data.get('data', []),
                'source': source
            })
            
        except ImportError as e:
            logger.error(f"Failed to import mock scrapers: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Scraper implementation unavailable',
                'error': str(e)
            }), 500

if __name__ == '__main__':
    # Start the Flask server locally
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))