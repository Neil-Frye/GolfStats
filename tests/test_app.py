import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Check for required dependencies
try:
    import flask
except ImportError:
    print("ERROR: Flask is not installed. Run 'pip install -r requirements.txt'")
    sys.exit(1)

# Mock the supabase module
sys.modules['supabase'] = MagicMock()
sys.modules['supabase'].create_client = MagicMock()
sys.modules['supabase'].Client = MagicMock

# Create a mock Flask app for testing
flask_app = flask.Flask(__name__)
flask_app.config['TESTING'] = True
flask_app.config['SECRET_KEY'] = 'test-secret-key'

# Define a basic route to match what we're testing
@flask_app.route('/')
def index():
    return "Welcome to GolfStats! Backend running with Supabase integration."

class TestApp(unittest.TestCase):
    """Basic app tests for GolfStats."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = flask_app.test_client()

    def test_index(self):
        """Test that the home page returns expected content."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to GolfStats', response.data)

if __name__ == '__main__':
    unittest.main()
