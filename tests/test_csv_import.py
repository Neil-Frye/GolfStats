"""
Tests for CSV import functionality.
"""
import unittest
import io
from unittest.mock import MagicMock, patch

from backend.database.supabase_data.csv_import import (
    detect_data_source,
    normalize_header,
    map_csv_field,
    parse_csv_data,
    import_csv_to_range_session
)

class TestCsvImport(unittest.TestCase):
    """Test cases for CSV import functionality."""
    
    def test_normalize_header(self):
        """Test header normalization function."""
        test_cases = [
            ("Ball Speed", "ball speed"),
            ("ball speed", "ball speed"),
            ("Ball-Speed", "ball speed"),
            ("Ball.Speed (mph)", "ball speed"),
            ("  Ball   Speed  ", "ball speed"),
            ("Ball_Speed", "ball speed"),
            ("ball_speed_mph", "ball speed mph"),
            ("LaunchAngle", "launch angle"),
            ("BallSpeed", "ball speed"),
            ("carry_distance_yards", "carry distance yards"),
            ("Carry (yards)", "carry"),
        ]
        
        for input_str, expected in test_cases:
            self.assertEqual(normalize_header(input_str), expected)
    
    def test_detect_data_source(self):
        """Test data source detection."""
        # Trackman headers
        trackman_headers = ["ClubSpeed", "BallSpeed", "SmashFactor", "LaunchAngle"]
        self.assertEqual(detect_data_source(trackman_headers), "trackman")
        
        # SkyTrak headers
        skytrak_headers = ["Club", "Speed", "Launch", "Backspin", "Carry"]
        self.assertEqual(detect_data_source(skytrak_headers), "skytrak")
        
        # Generic headers with no distinctive patterns
        generic_headers = ["Club", "Distance", "Notes"]
        self.assertEqual(detect_data_source(generic_headers), "default")
        
        # Mixed headers with more trackman
        mixed_headers = ["Club", "BallSpeed", "ClubSpeed", "Launch", "Carry"]
        self.assertEqual(detect_data_source(mixed_headers), "trackman")
    
    def test_map_csv_field(self):
        """Test CSV field mapping."""
        # Trackman fields
        self.assertEqual(map_csv_field("ClubSpeed", "trackman"), "club_speed_mph")
        self.assertEqual(map_csv_field("BallSpeed", "trackman"), "ball_speed_mph")
        
        # SkyTrak fields
        self.assertEqual(map_csv_field("Speed", "skytrak"), "ball_speed_mph")
        self.assertEqual(map_csv_field("Launch", "skytrak"), "launch_angle_degrees")
        
        # Default fields
        self.assertEqual(map_csv_field("Ball Speed", "default"), "ball_speed_mph")
        self.assertEqual(map_csv_field("Club Speed", "default"), "club_speed_mph")
        
        # Normalized fields
        self.assertEqual(map_csv_field("Ball-Speed", "default"), "ball_speed_mph")
        self.assertEqual(map_csv_field("Launch Angle (°)", "default"), "launch_angle_degrees")
        
        # Direct DB field matches (new functionality)
        self.assertEqual(map_csv_field("ball_speed_mph", "default"), "ball_speed_mph")
        self.assertEqual(map_csv_field("carry_distance_yards", "default"), "carry_distance_yards")
        self.assertEqual(map_csv_field("total_distance_yards", "default"), "total_distance_yards")
        
        # Normalized with underscores (new functionality)
        self.assertEqual(map_csv_field("Carry Distance Yards", "default"), "carry_distance_yards")
        self.assertEqual(map_csv_field("Ball Speed (mph)", "default"), "ball_speed_mph")
        self.assertEqual(map_csv_field("Launch_Angle_Degrees", "default"), "launch_angle_degrees")
        
        # Unknown field
        self.assertIsNone(map_csv_field("Unknown Field", "default"))
    
    def test_parse_csv_data(self):
        """Test CSV parsing."""
        # Simple CSV with common fields
        csv_content = """Club,Ball Speed,Launch Angle,Spin Rate,Carry,Total
Driver,150.3,12.5,2500,245.7,265.2
7 Iron,120.1,18.2,6500,155.3,160.5
"""
        shots, unmapped = parse_csv_data(csv_content)
        
        self.assertEqual(len(shots), 2)
        self.assertEqual(len(unmapped), 0)
        
        # Check first shot
        self.assertEqual(shots[0]["club"], "Driver")
        self.assertEqual(shots[0]["ball_speed_mph"], 150.3)
        self.assertEqual(shots[0]["launch_angle_degrees"], 12.5)
        self.assertEqual(shots[0]["spin_rate_rpm"], 2500)
        self.assertEqual(shots[0]["carry_distance_yards"], 245.7)
        self.assertEqual(shots[0]["total_distance_yards"], 265.2)
        
        # CSV with some unmapped fields
        csv_content = """Club,Ball Speed,Unknown Field,Carry,Another Unknown
Driver,150.3,some value,245.7,another value
"""
        shots, unmapped = parse_csv_data(csv_content)
        
        self.assertEqual(len(shots), 1)
        self.assertEqual(len(unmapped), 2)
        self.assertIn("Unknown Field", unmapped)
        self.assertIn("Another Unknown", unmapped)
    
    @patch('backend.database.supabase_data.csv_import.add_range_shots')
    def test_import_csv_to_range_session(self, mock_add_range_shots):
        """Test importing CSV to range session."""
        # Mock the add_range_shots function
        mock_shots = [{"id": 1, "club": "Driver"}, {"id": 2, "club": "7 Iron"}]
        mock_add_range_shots.return_value = mock_shots
        
        # Test CSV content
        csv_content = """Club,Ball Speed,Launch Angle,Spin Rate,Carry,Total
Driver,150.3,12.5,2500,245.7,265.2
7 Iron,120.1,18.2,6500,155.3,160.5
"""
        
        # Import CSV
        session_id = 123
        token = "test_token"
        shots, unmapped = import_csv_to_range_session(session_id, csv_content, token=token)
        
        # Verify results
        self.assertEqual(shots, mock_shots)
        self.assertEqual(len(unmapped), 0)
        
        # Verify the add_range_shots call
        mock_add_range_shots.assert_called_once()
        args = mock_add_range_shots.call_args[0]
        
        # Check session_id
        self.assertEqual(args[0], session_id)
        
        # Check shots data
        shots_data = args[1]
        self.assertEqual(len(shots_data), 2)
        
        # Check that session_id and shot_type are set
        for shot in shots_data:
            self.assertEqual(shot["session_id"], session_id)
            self.assertEqual(shot["shot_type"], "range")
            
        # Check token
        self.assertEqual(mock_add_range_shots.call_args[1]["token"], token)
        
    def test_parse_csv_with_invalid_numeric(self):
        """Test CSV parsing with invalid numeric values."""
        csv_content = """Club,Ball Speed,Launch Angle
Driver,not a number,12.5
"""
        shots, unmapped = parse_csv_data(csv_content)
        
        self.assertEqual(len(shots), 1)
        self.assertNotIn("ball_speed_mph", shots[0])
        self.assertEqual(shots[0]["launch_angle_degrees"], 12.5)
        
    def test_parse_csv_with_direct_db_fields(self):
        """Test CSV parsing with direct database field names."""
        csv_content = """club,ball_speed_mph,launch_angle_degrees,carry_distance_yards,total_distance_yards
Driver,150.2,12.5,245.7,265.2
7 Iron,120.1,18.2,155.3,160.5
"""
        shots, unmapped = parse_csv_data(csv_content)
        
        self.assertEqual(len(shots), 2)
        self.assertEqual(len(unmapped), 0)
        
        # Check first shot
        self.assertEqual(shots[0]["club"], "Driver")
        self.assertEqual(shots[0]["ball_speed_mph"], 150.2)
        self.assertEqual(shots[0]["launch_angle_degrees"], 12.5)
        self.assertEqual(shots[0]["carry_distance_yards"], 245.7)
        self.assertEqual(shots[0]["total_distance_yards"], 265.2)
        
    def test_parse_csv_with_mixed_field_naming(self):
        """Test CSV parsing with mixed field naming styles."""
        csv_content = """club,Ball Speed,launch_angle_degrees,Carry (yards),Total
Driver,150.2,12.5,245.7,265.2
7 Iron,120.1,18.2,155.3,160.5
"""
        shots, unmapped = parse_csv_data(csv_content)
        
        self.assertEqual(len(shots), 2)
        self.assertEqual(len(unmapped), 0)
        
        # Check first shot
        self.assertEqual(shots[0]["club"], "Driver")
        self.assertEqual(shots[0]["ball_speed_mph"], 150.2)
        self.assertEqual(shots[0]["launch_angle_degrees"], 12.5)
        self.assertEqual(shots[0]["carry_distance_yards"], 245.7)
        self.assertEqual(shots[0]["total_distance_yards"], 265.2)
        
if __name__ == '__main__':
    unittest.main()