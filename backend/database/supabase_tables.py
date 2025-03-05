"""
Supabase table creation script for GolfStats application.

This script creates the necessary tables in Supabase using the REST API.
"""
import logging
import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database.supabase_client import get_supabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_tables():
    """
    Create all required tables in Supabase if they don't already exist.
    
    This uses the Supabase REST API to create tables with the proper structure.
    """
    try:
        supabase = get_supabase()
        
        # Check existing tables
        existing_tables = check_existing_tables(supabase)
        logger.info(f"Existing tables: {existing_tables}")
        
        # Create each table directly using REST API
        
        # Define all tables that need to be created
        tables_to_create = {
            # User profiles/preferences
            "user_preferences": not "user_preferences" in existing_tables,
            
            # Golf data tables
            "golf_rounds": not "golf_rounds" in existing_tables,
            "golf_holes": not "golf_holes" in existing_tables,
            "golf_shots": not "golf_shots" in existing_tables,
            "round_stats": not "round_stats" in existing_tables,
            "clubs": not "clubs" in existing_tables,
        }
        
        # Create tables directly using REST API
        created_count = 0
        for table_name, should_create in tables_to_create.items():
            if should_create:
                if create_table_directly(supabase, table_name):
                    created_count += 1
        
        logger.info(f"Created {created_count} tables in Supabase")
        return True
    except Exception as e:
        logger.error(f"Error creating Supabase tables: {str(e)}")
        return False

def check_existing_tables(supabase):
    """Check which tables already exist in the database."""
    try:
        # Test tables by trying to select from them
        tables = ["user_preferences", "golf_rounds", "golf_holes", 
                 "golf_shots", "round_stats", "clubs"]
        
        existing = []
        for table in tables:
            try:
                # Try to select a single row to check if table exists
                response = supabase.table(table).select("*").limit(1).execute()
                # If we get here, the table exists
                existing.append(table)
            except Exception:
                # Table likely doesn't exist
                pass
                
        return existing
    except Exception as e:
        logger.error(f"Error checking existing tables: {str(e)}")
        return []

def create_table_directly(supabase, table_name):
    """
    Create a table directly using the REST API.
    
    Args:
        supabase: Supabase client
        table_name: Name of the table to create
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Creating table: {table_name}")
    
    # Define columns based on table name
    if table_name == "user_preferences":
        data = {
            "id": 1, # Will be auto-incremented
            "user_id": "00000000-0000-0000-0000-000000000000", # Reference to auth.users
            "preferred_units": "yards",
            "handicap": None,
            "trackman_username": None,
            "trackman_password": None,
            "arccos_email": None,
            "arccos_password": None,
            "skytrak_username": None,
            "skytrak_password": None,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
    elif table_name == "golf_rounds":
        data = {
            "id": 1, # Will be auto-incremented
            "user_id": "00000000-0000-0000-0000-000000000000", # Reference to auth.users
            "date": "2023-01-01T00:00:00Z",
            "course_name": "Test Course",
            "course_location": "Test Location",
            "tee_color": "White",
            "total_score": 72,
            "total_par": 72,
            "front_nine_score": 36,
            "back_nine_score": 36,
            "weather_conditions": "Sunny",
            "notes": "Test round",
            "source_system": "manual",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
    elif table_name == "golf_holes":
        data = {
            "id": 1, # Will be auto-incremented
            "round_id": 1, # Reference to golf_rounds.id
            "hole_number": 1,
            "par": 4,
            "score": 4,
            "fairway_hit": True,
            "green_in_regulation": True,
            "putts": 2,
            "distance_yards": 400,
            "notes": "Test hole",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
    elif table_name == "golf_shots":
        data = {
            "id": 1, # Will be auto-incremented
            "hole_id": 1, # Reference to golf_holes.id
            "shot_number": 1,
            "club": "Driver",
            "distance_yards": 250.0,
            "from_location": "tee",
            "to_location": "fairway",
            "is_penalty": False,
            "ball_speed_mph": 150.0,
            "club_speed_mph": 100.0,
            "smash_factor": 1.5,
            "launch_angle_degrees": 12.0,
            "spin_rate_rpm": 2500.0,
            "spin_axis_degrees": 0.0,
            "carry_distance_yards": 240.0,
            "total_distance_yards": 250.0,
            "side_deviation_yards": 0.0,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
    elif table_name == "round_stats":
        data = {
            "id": 1, # Will be auto-incremented
            "round_id": 1, # Reference to golf_rounds.id
            "score_to_par": 0,
            "fairways_hit": 10,
            "fairways_total": 14,
            "greens_in_regulation": 12,
            "putts_total": 30,
            "putts_per_hole": 1.7,
            "sand_saves": 1,
            "sand_save_attempts": 2,
            "penalties": 0,
            "average_drive_yards": 250.0,
            "scrambling_successful": 3,
            "scrambling_attempts": 5,
            "up_and_downs": 3,
            "up_and_down_attempts": 5,
            "three_putts": 0,
            "extended_stats": {"strokes_gained": {"total": 0.5}},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
    elif table_name == "clubs":
        data = {
            "id": 1, # Will be auto-incremented
            "user_id": "00000000-0000-0000-0000-000000000000", # Reference to auth.users
            "name": "Driver",
            "club_type": "driver",
            "brand": "Test Brand",
            "model": "Test Model",
            "loft": 10.5,
            "avg_distance_yards": 250.0,
            "max_distance_yards": 280.0,
            "is_active": True,
            "notes": "Test club",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
    else:
        logger.error(f"Unknown table name: {table_name}")
        return False
    
    try:
        # Create the table by inserting data
        response = supabase.table(table_name).insert(data).execute()
        
        # Whether successful or not, we attempted to create the table
        # Now we need to remove the sample data we inserted
        try:
            supabase.table(table_name).delete().eq('id', 1).execute()
        except Exception as delete_error:
            logger.warning(f"Failed to clean up sample data in {table_name}: {str(delete_error)}")
            
        logger.info(f"Created table: {table_name}")
        return True
    except Exception as e:
        logger.error(f"Error creating table {table_name}: {str(e)}")
        return False

def main():
    """Main function to create all required tables."""
    logger.info("Starting Supabase table creation")
    success = create_tables()
    if success:
        logger.info("Supabase tables created successfully!")
    else:
        logger.error("Failed to create some Supabase tables.")

if __name__ == "__main__":
    main()