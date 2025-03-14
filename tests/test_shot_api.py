
import unittest
import json
import os
from unittest.mock import patch, MagicMock

# Make sure test environment is set
os.environ['APP_ENVIRONMENT'] = 'test'

# Import app after setting environment
from backend.app import app

class TestShotAPI(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.test_user = {'id': 'test-user-id', 'email': 'test@example.com'}
        self.mock_token = 'mock-token'
        
        # Setup auth mock
        self.auth_patcher = patch('backend.range_shots.routes.get_authenticated_user')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = (self.test_user, self.mock_token)
        
        # Setup Supabase client mock
        self.supabase_patcher = patch('backend.range_shots.routes.get_supabase')
        self.mock_supabase = self.supabase_patcher.start()
        self.mock_supabase_client = MagicMock()
        self.mock_supabase.return_value = self.mock_supabase_client
        
    def tearDown(self):
        self.auth_patcher.stop()
        self.supabase_patcher.stop()
        
    def test_get_shot(self):
        # Mock shot data
        test_shot = {
            'id': 'test-shot-id',
            'session_id': 'test-session-id',
            'shot_number': 1,
            'club': 'Driver',
            'distance_yards': 250
        }
        
        # Mock Supabase responses
        mock_shot_response = MagicMock()
        mock_shot_response.data = [test_shot]
        
        mock_session_response = MagicMock()
        mock_session_response.data = [{'id': 'test-session-id'}]
        
        # Setup query chain
        mock_shots_query = MagicMock()
        mock_shots_query.select.return_value = mock_shots_query
        mock_shots_query.eq.return_value = mock_shots_query
        mock_shots_query.execute.return_value = mock_shot_response
        
        mock_sessions_query = MagicMock()
        mock_sessions_query.select.return_value = mock_sessions_query
        mock_sessions_query.eq.side_effect = lambda field, value: mock_sessions_query
        mock_sessions_query.execute.return_value = mock_session_response
        
        # Setup table mocks
        self.mock_supabase_client.table.side_effect = lambda table_name: mock_shots_query if table_name == 'golf_shots' else mock_sessions_query
        
        # Make the request
        response = self.client.get('/api/shots/test-shot-id')
        data = json.loads(response.data)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['shot'], test_shot)
        
    def test_update_shot(self):
        # Mock existing and updated shot data
        test_shot = {
            'id': 'test-shot-id',
            'session_id': 'test-session-id',
            'shot_number': 1,
            'club': 'Driver',
            'distance_yards': 250
        }
        
        updated_shot = {
            'id': 'test-shot-id',
            'session_id': 'test-session-id',
            'shot_number': 1,
            'club': '3 Wood',  # Changed
            'distance_yards': 230  # Changed
        }
        
        # Mock Supabase responses
        mock_get_shot_response = MagicMock()
        mock_get_shot_response.data = [test_shot]
        
        mock_session_response = MagicMock()
        mock_session_response.data = [{'id': 'test-session-id'}]
        
        mock_update_response = MagicMock()
        mock_update_response.data = [updated_shot]
        
        # Setup query chains
        mock_shots_query = MagicMock()
        mock_shots_query.select.return_value = mock_shots_query
        mock_shots_query.eq.return_value = mock_shots_query
        mock_shots_query.execute.return_value = mock_get_shot_response
        
        mock_update_query = MagicMock()
        mock_update_query.update.return_value = mock_update_query
        mock_update_query.eq.return_value = mock_update_query
        mock_update_query.execute.return_value = mock_update_response
        
        mock_sessions_query = MagicMock()
        mock_sessions_query.select.return_value = mock_sessions_query
        mock_sessions_query.eq.side_effect = lambda field, value: mock_sessions_query
        mock_sessions_query.execute.return_value = mock_session_response
        
        # Setup table mocks with different behaviors for get and update
        self.mock_supabase_client.table.side_effect = lambda table_name: mock_shots_query if table_name == 'golf_shots' else mock_sessions_query
        
        # Mock the update_shot function
        with patch('backend.range_shots.routes.update_shot') as mock_update_shot:
            mock_update_shot.return_value = updated_shot
            
            # Make the request
            update_data = {'club': '3 Wood', 'distance_yards': 230}
            response = self.client.put('/api/shots/test-shot-id', 
                                      data=json.dumps(update_data),
                                      content_type='application/json')
            data = json.loads(response.data)
            
            # Assert response
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['shot'], updated_shot)
            
            # Assert the update_shot function was called correctly
            mock_update_shot.assert_called_once_with('test-shot-id', update_data, self.mock_token)
        
    def test_delete_shot(self):
        # Mock shot data
        test_shot = {
            'id': 'test-shot-id',
            'session_id': 'test-session-id',
            'shot_number': 1,
            'club': 'Driver',
            'distance_yards': 250
        }
        
        # Mock Supabase responses
        mock_shot_response = MagicMock()
        mock_shot_response.data = [test_shot]
        
        mock_session_response = MagicMock()
        mock_session_response.data = [{'id': 'test-session-id'}]
        
        mock_delete_response = MagicMock()
        mock_delete_response.data = [test_shot]  # Return the deleted item
        
        # Setup query chains
        mock_shots_query = MagicMock()
        mock_shots_query.select.return_value = mock_shots_query
        mock_shots_query.eq.return_value = mock_shots_query
        mock_shots_query.execute.return_value = mock_shot_response
        
        mock_sessions_query = MagicMock()
        mock_sessions_query.select.return_value = mock_sessions_query
        mock_sessions_query.eq.side_effect = lambda field, value: mock_sessions_query
        mock_sessions_query.execute.return_value = mock_session_response
        
        # Setup table mocks
        self.mock_supabase_client.table.side_effect = lambda table_name: mock_shots_query if table_name == 'golf_shots' else mock_sessions_query
        
        # Mock the delete_shot function
        with patch('backend.range_shots.routes.delete_shot') as mock_delete_shot:
            mock_delete_shot.return_value = True
            
            # Make the request
            response = self.client.delete('/api/shots/test-shot-id')
            data = json.loads(response.data)
            
            # Assert response
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            
            # Assert the delete_shot function was called correctly
            mock_delete_shot.assert_called_once_with('test-shot-id', self.mock_token)

if __name__ == '__main__':
    unittest.main()

