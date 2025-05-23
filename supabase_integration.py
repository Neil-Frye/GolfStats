import logging
from datetime import datetime, timezone
# from supabase import Client, create_client # Actual Supabase client import

# Setup basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# --- Custom Exceptions ---
class SupabaseDBError(Exception):
    """Base class for Supabase database integration errors."""
    pass

# --- Main Class ---
class SupabaseSkyTrakDB:
    """
    Handles saving SkyTrak golf session and shot data to a Supabase database.
    """

    def __init__(self, supabase_client):
        """
        Initializes the database integration class with a Supabase client.

        Args:
            supabase_client: An initialized Supabase client instance.
                             (e.g., from `supabase.create_client(SUPABASE_URL, SUPABASE_KEY)`)
        """
        # Type checking for supabase_client would be ideal if its type were known
        # For now, we assume it's a valid client object.
        if supabase_client is None:
            raise ValueError("Supabase client cannot be None.")
        self.supabase = supabase_client
        logger.info("SupabaseSkyTrakDB initialized.")

    def _prepare_session_data(self, session_dict: dict, user_id: str) -> dict:
        """
        Prepares a session dictionary for upsert into the 'golf_sessions' table.
        Maps keys from the SkyTrakDataExtractor output to database column names.

        Args:
            session_dict: A dictionary representing a single session's data.
                          Expected keys (based on SkyTrakDataExtractor):
                          'session_id', 'date', 'club_name', 'total_shots', 
                          'duration_minutes' (optional), 'location_name' (optional),
                          and the raw data itself for 'source_skytrak_session_data'.
            user_id: The UUID of the user.

        Returns:
            A dictionary formatted for the 'golf_sessions' table.
        """
        # --- Data Mapping Logic (Conceptual) ---
        # This function maps the keys from the SkyTrakDataExtractor's output
        # to the column names defined in the 'golf_sessions' table.
        # It also handles data type conversions if necessary, though the
        # extractor should ideally provide data in near-final types.

        # Ensure session_date is in ISO 8601 format with timezone
        # The database expects TIMESTAMPTZ. If 'date' is already a datetime object,
        # it might be fine, or it might need to be formatted as a string.
        # If it's a string, ensure it's ISO 8601. Supabase client might handle datetime objects.
        session_date_str = session_dict.get('date')
        if not session_date_str: # Or if it needs conversion from a different format
            logger.warning(f"Session {session_dict.get('session_id')} missing date, using current time.")
            session_date_iso = datetime.now(timezone.utc).isoformat()
        else:
            # Assuming session_dict.get('date') is already ISO 8601 or a compatible datetime object
            session_date_iso = session_date_str 


        prepared_data = {
            'session_id': session_dict.get('session_id'),
            'user_id': user_id,
            'session_date': session_date_iso,
            'club_name_session_level': session_dict.get('club_name_session_level') or session_dict.get('club_name'), # Prefer specific, fallback to general
            'total_shots_reported': session_dict.get('total_shots') or session_dict.get('total_shots_reported'),
            'duration_minutes': session_dict.get('duration_minutes'),
            'location_name': session_dict.get('location_name'),
            'source_skytrak_session_data': session_dict, # Store the original dict as JSONB
            # 'imported_at' and 'last_updated_at' are typically handled by DB defaults or triggers.
            # If 'last_updated_at' needs to be set on upsert, add it here:
            'last_updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Remove keys with None values if the database handles defaults appropriately,
        # or if you want to avoid overwriting existing values with NULL during an UPDATE part of UPSERT.
        # For many Supabase upserts, sending None will set the column to NULL.
        # return {k: v for k, v in prepared_data.items() if v is not None or k in ['session_id', 'user_id', 'session_date']}
        return prepared_data


    def _prepare_shot_data(self, shot_dict: dict, user_id: str) -> dict:
        """
        Prepares a shot dictionary for upsert into the 'golf_shots' table.
        Maps keys from the SkyTrakDataExtractor output to database column names.

        Args:
            shot_dict: A dictionary representing a single shot's data.
                       Expected keys (based on SkyTrakDataExtractor):
                       'shot_id', 'session_id', 'club_name', 'timestamp',
                       'ball_speed_mph', 'launch_angle_deg', 'side_angle_deg',
                       'back_spin_rpm', 'side_spin_rpm', 'carry_yards', 
                       'total_yards', 'offline_yards', 'descent_angle_deg',
                       'flight_time_sec', 'peak_height_yards', etc.
                       And the raw data itself for 'source_skytrak_shot_data'.
            user_id: The UUID of the user.

        Returns:
            A dictionary formatted for the 'golf_shots' table.
        """
        # --- Data Mapping Logic (Conceptual) ---
        # Map SkyTrakDataExtractor output keys to 'golf_shots' column names.
        # Handle potential type conversions (e.g., string to numeric).
        # The extractor should ideally provide data in near-final types.

        shot_timestamp_iso = shot_dict.get('timestamp')
        if not shot_timestamp_iso:
            logger.warning(f"Shot {shot_dict.get('shot_id')} missing timestamp, using current time.")
            shot_timestamp_iso = datetime.now(timezone.utc).isoformat()

        prepared_data = {
            'shot_id': shot_dict.get('shot_id'),
            'session_id': shot_dict.get('session_id'),
            'user_id': user_id,
            'club_name': shot_dict.get('club_name'),
            'shot_timestamp': shot_timestamp_iso,
            
            # Core Metrics - ensure these keys match the extractor output
            'ball_speed': shot_dict.get('ball_speed_mph') or shot_dict.get('ball_speed'),
            'club_head_speed': shot_dict.get('club_head_speed_mph') or shot_dict.get('club_head_speed'),
            'smash_factor': shot_dict.get('smash_factor'),
            'launch_angle': shot_dict.get('launch_angle_deg') or shot_dict.get('launch_angle'),
            'side_angle': shot_dict.get('side_angle_deg') or shot_dict.get('side_angle'),
            'back_spin': shot_dict.get('back_spin_rpm') or shot_dict.get('back_spin'),
            'side_spin': shot_dict.get('side_spin_rpm') or shot_dict.get('side_spin'),
            'carry_distance': shot_dict.get('carry_yards') or shot_dict.get('carry_distance'),
            'total_distance': shot_dict.get('total_yards') or shot_dict.get('total_distance'),
            'offline_distance': shot_dict.get('offline_yards') or shot_dict.get('offline_distance'),
            'descent_angle': shot_dict.get('descent_angle_deg') or shot_dict.get('descent_angle'),
            'flight_time': shot_dict.get('flight_time_sec') or shot_dict.get('flight_time'),
            'peak_height': shot_dict.get('peak_height_yards') or shot_dict.get('peak_height'),

            # Other potential metrics
            'face_angle': shot_dict.get('face_angle_deg') or shot_dict.get('face_angle'),
            'club_path': shot_dict.get('club_path_deg') or shot_dict.get('club_path'),
            'angle_of_attack': shot_dict.get('angle_of_attack_deg') or shot_dict.get('angle_of_attack'),
            
            'source_skytrak_shot_data': shot_dict, # Store the original dict as JSONB
            # 'imported_at' is typically handled by DB default.
        }
        # Remove None values to avoid accidentally nullifying fields during upsert if not desired.
        # return {k: v for k, v in prepared_data.items() if v is not None or k in ['shot_id', 'session_id', 'user_id']}
        return prepared_data

    def save_golf_data(self, user_id: str, sessions_data: list[dict], shots_data: list[dict]) -> dict:
        """
        Saves extracted SkyTrak golf sessions and associated shots to Supabase.
        Uses upsert to ensure idempotency.

        Args:
            user_id: The UUID of the user.
            sessions_data: A list of session dictionaries from SkyTrakDataExtractor.
            shots_data: A list of shot dictionaries from SkyTrakDataExtractor.

        Returns:
            A dictionary summarizing the results, e.g.,
            {"sessions_processed": count, "shots_processed": count, 
             "sessions_upserted": count, "shots_upserted": count}
        
        Raises:
            SupabaseDBError: If any database operation fails.
        """
        if not user_id:
            raise ValueError("user_id must be provided.")
        
        logger.info(f"Starting to save golf data for user_id: {user_id}")
        
        sessions_processed = 0
        sessions_upserted_count = 0
        shots_processed = 0
        shots_upserted_count = 0

        # --- Upsert Sessions ---
        # For performance, batch upserts are highly recommended.
        # The Supabase Python client's upsert method can handle a list of dicts.
        
        prepared_sessions_for_upsert = []
        for session_item in sessions_data:
            sessions_processed += 1
            try:
                prepared_session = self._prepare_session_data(session_item, user_id)
                prepared_sessions_for_upsert.append(prepared_session)
            except Exception as e:
                logger.error(f"Error preparing session data for session_id {session_item.get('session_id')}: {e}", exc_info=True)
                # Optionally, collect errors or skip this session

        if prepared_sessions_for_upsert:
            try:
                logger.info(f"Upserting {len(prepared_sessions_for_upsert)} session(s) to 'golf_sessions' table.")
                # --- Actual Supabase Client Call (Placeholder) ---
                # response = self.supabase.table('golf_sessions').upsert(
                #     prepared_sessions_for_upsert,
                #     on_conflict='session_id' # Assumes session_id is the PK or unique constraint for conflict
                # ).execute()
                #
                # if hasattr(response, 'data') and response.data:
                #     sessions_upserted_count = len(response.data)
                #     logger.info(f"Successfully upserted {sessions_upserted_count} session(s).")
                # elif hasattr(response, 'error') and response.error:
                #     logger.error(f"Supabase error during session upsert: {response.error}")
                #     raise SupabaseDBError(f"Supabase session upsert error: {response.error.message}")
                # else:
                #    # Handle cases where response structure might differ (e.g. older client versions)
                #    # Or if no data is returned on success but no error either.
                #    logger.info("Session upsert call executed, but response format not fully recognized or no data returned/modified.")
                #    # Assuming success if no error, but count might be inaccurate.
                #    sessions_upserted_count = len(prepared_sessions_for_upsert) # Tentative count

                # Placeholder for now, actual count would come from Supabase response
                sessions_upserted_count = len(prepared_sessions_for_upsert) 
                logger.info(f"Placeholder: Successfully upserted {sessions_upserted_count} session(s).")

            except Exception as e: # Catch generic Supabase client errors or other issues
                logger.error(f"Error during Supabase session upsert operation: {e}", exc_info=True)
                raise SupabaseDBError(f"Session upsert failed: {e}")


        # --- Upsert Shots ---
        # Similar to sessions, batch upserts are crucial for performance.
        prepared_shots_for_upsert = []
        for shot_item in shots_data:
            shots_processed += 1
            try:
                prepared_shot = self._prepare_shot_data(shot_item, user_id)
                prepared_shots_for_upsert.append(prepared_shot)
            except Exception as e:
                logger.error(f"Error preparing shot data for shot_id {shot_item.get('shot_id')}: {e}", exc_info=True)
                # Optionally, collect errors or skip this shot

        if prepared_shots_for_upsert:
            try:
                logger.info(f"Upserting {len(prepared_shots_for_upsert)} shot(s) to 'golf_shots' table.")
                # --- Actual Supabase Client Call (Placeholder) ---
                # response = self.supabase.table('golf_shots').upsert(
                #     prepared_shots_for_upsert,
                #     on_conflict='shot_id, session_id' # Assuming composite PK for conflict
                #     # If shot_id is globally unique and the PK, then on_conflict='shot_id'
                # ).execute()
                #
                # if hasattr(response, 'data') and response.data:
                #     shots_upserted_count = len(response.data)
                #     logger.info(f"Successfully upserted {shots_upserted_count} shot(s).")
                # elif hasattr(response, 'error') and response.error:
                #     logger.error(f"Supabase error during shot upsert: {response.error}")
                #     raise SupabaseDBError(f"Supabase shot upsert error: {response.error.message}")
                # else:
                #    logger.info("Shot upsert call executed, but response format not fully recognized or no data returned/modified.")
                #    shots_upserted_count = len(prepared_shots_for_upsert) # Tentative count

                # Placeholder for now
                shots_upserted_count = len(prepared_shots_for_upsert)
                logger.info(f"Placeholder: Successfully upserted {shots_upserted_count} shot(s).")

            except Exception as e: # Catch generic Supabase client errors
                logger.error(f"Error during Supabase shot upsert operation: {e}", exc_info=True)
                raise SupabaseDBError(f"Shot upsert failed: {e}")

        summary = {
            "sessions_processed": sessions_processed,
            "sessions_upserted": sessions_upserted_count,
            "shots_processed": shots_processed,
            "shots_upserted": shots_upserted_count
        }
        logger.info(f"Golf data saving finished. Summary: {summary}")
        return summary

# --- Usage Example (Commented Out) ---
# if __name__ == '__main__':
#     logger.info("Starting Supabase SkyTrak DB Integration Example...")

#     # --- Placeholder for Supabase Client Initialization ---
#     # SUPABASE_URL = os.environ.get("SUPABASE_URL")
#     # SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") # Use service role key for backend operations
#     # if not SUPABASE_URL or not SUPABASE_KEY:
#     #     logger.error("Supabase URL or Key not provided. Cannot run example.")
#     #     # exit(1) # Or handle appropriately
#     #     supabase_client = None # Ensure it's None
#     # else:
#     #     try:
#     #         supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
#     #         logger.info("Supabase client initialized successfully.")
#     #     except Exception as e:
#     #         logger.error(f"Failed to initialize Supabase client: {e}")
#     #         supabase_client = None


#     # --- Mock Supabase Client for testing structure without live DB ---
#     class MockSupabaseClient:
#         def table(self, table_name):
#             logger.info(f"MockSupabaseClient: Accessing table '{table_name}'")
#             return self # Return self to chain methods like .upsert().execute()
        
#         def upsert(self, data, on_conflict=None):
#             logger.info(f"MockSupabaseClient: Upserting data (on_conflict='{on_conflict}'): {data[:2]}...") # Log first 2 items
#             # Simulate Supabase response structure (simplified)
#             class MockPostgrestResponse:
#                 def __init__(self, data_list):
#                     self.data = data_list # Supabase returns the upserted data
#                     self.error = None
#                 def execute(self): # Older versions might have execute(), newer might not need it for upsert
#                     return self 
            
#             return MockPostgrestResponse(data) # Return the input data as if it was upserted

#         def execute(self): # For chains like .select().execute() if ever needed here
#             logger.info("MockSupabaseClient: Execute called")
#             return self
            
#     supabase_client = MockSupabaseClient() # Using the mock client

#     if supabase_client:
#         db_integrator = SupabaseSkyTrakDB(supabase_client)
        
#         # Example User ID (replace with actual user ID from your auth system)
#         example_user_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11" # Example UUID

#         # Example Data (mirroring structure from SkyTrakDataExtractor)
#         example_sessions_data = [
#             {
#                 "session_id": "skytrak_session_001", 
#                 "date": datetime.now(timezone.utc).isoformat(), 
#                 "club_name_session_level": "Driving Range", 
#                 "total_shots": 2,
#                 "duration_minutes": 30,
#                 "location_name": "Virtual Range"
#             },
#             {
#                 "session_id": "skytrak_session_002", 
#                 "date": datetime.now(timezone.utc).isoformat(), 
#                 "club_name_session_level": "Irons Practice", 
#                 "total_shots": 1,
#                 "duration_minutes": 15,
#             }
#         ]
#         example_shots_data = [
#             {
#                 "shot_id": "skytrak_shot_A001", "session_id": "skytrak_session_001", 
#                 "club_name": "Driver", "timestamp": datetime.now(timezone.utc).isoformat(),
#                 "ball_speed_mph": 150.1, "launch_angle_deg": 12.3, "side_angle_deg": 1.1,
#                 "back_spin_rpm": 2200, "side_spin_rpm": -250, "carry_yards": 250.5, "total_yards": 270.8
#             },
#             {
#                 "shot_id": "skytrak_shot_A002", "session_id": "skytrak_session_001", 
#                 "club_name": "Driver", "timestamp": datetime.now(timezone.utc).isoformat(),
#                 "ball_speed_mph": 155.6, "launch_angle_deg": 11.8, "side_angle_deg": -0.5,
#                 "back_spin_rpm": 2100, "side_spin_rpm": 150, "carry_yards": 260.1, "total_yards": 280.3
#             },
#             {
#                 "shot_id": "skytrak_shot_B001", "session_id": "skytrak_session_002", 
#                 "club_name": "7 Iron", "timestamp": datetime.now(timezone.utc).isoformat(),
#                 "ball_speed_mph": 120.0, "launch_angle_deg": 18.5, "side_angle_deg": 0.5,
#                 "back_spin_rpm": 6500, "side_spin_rpm": -100, "carry_yards": 165.0, "total_yards": 175.0
#             }
#         ]

#         try:
#             logger.info("\n--- Attempting to save golf data ---")
#             result_summary = db_integrator.save_golf_data(example_user_id, example_sessions_data, example_shots_data)
#             logger.info(f"Save operation summary: {result_summary}")

#         except SupabaseDBError as e:
#             logger.error(f"Database operation failed: {e}")
#         except Exception as e:
#             logger.error(f"An unexpected error occurred in example usage: {e}", exc_info=True)
#     else:
#         logger.error("Supabase client not initialized. Cannot run example.")
    
#     logger.info("\nSupabase SkyTrak DB Integration Example Finished.")
```
