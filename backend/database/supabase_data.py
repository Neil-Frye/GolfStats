"""
Supabase data access module for GolfStats application.

This module provides functions to interact with Supabase tables.
This module is deprecated. Please use the backend.database.supabase_data package instead.

DEPRECATION WARNING: This module will be removed in a future version.
Import directly from the specific modules in the backend.database.supabase_data package instead:
    - backend.database.supabase_data.rounds
    - backend.database.supabase_data.shots
    - backend.database.supabase_data.stats
    - backend.database.supabase_data.clubs
    - backend.database.supabase_data.user_preferences
    - backend.database.supabase_data.common
"""

import warnings

warnings.warn(
    "The module backend.database.supabase_data is deprecated. "
    "Please import directly from the specific modules in the "
    "backend.database.supabase_data package instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all functions from the new package to maintain backward compatibility
from backend.database.supabase_data import (
    # Common utilities
    DateTimeEncoder,
    
    # Rounds
    get_golf_rounds,
    get_golf_round,
    create_golf_round,
    update_golf_round,
    delete_golf_round,
    
    # Shots and holes
    get_shots_for_round,
    add_shot,
    add_holes_for_round,
    add_shots_for_hole,
    
    # Stats
    create_round_stats,
    add_round_stats,
    get_user_rounds_stats,
    
    # User preferences
    get_user_preferences,
    update_user_preferences,
    
    # Clubs
    get_user_clubs,
    get_club,
    create_club,
    update_club,
    delete_club
)