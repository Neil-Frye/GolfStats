"""
Supabase data access package for GolfStats application.

This package provides functions to interact with Supabase tables.
Functions are organized into modules by domain:
- rounds: Golf round management
- shots: Golf shot and hole management
- stats: Statistics and analytics
- clubs: Club management
- user_preferences: User preferences and settings
"""

# Re-export all functions to maintain backward compatibility
from backend.database.supabase_data.rounds import (
    get_golf_rounds,
    get_golf_round,
    create_golf_round,
    update_golf_round,
    delete_golf_round
)

from backend.database.supabase_data.shots import (
    get_shots_for_round,
    add_shot,
    add_holes_for_round,
    add_shots_for_hole
)

from backend.database.supabase_data.stats import (
    create_round_stats,
    add_round_stats,
    get_user_rounds_stats
)

from backend.database.supabase_data.clubs import (
    get_user_clubs,
    get_club,
    create_club,
    update_club,
    delete_club
)

from backend.database.supabase_data.user_preferences import (
    get_user_preferences,
    update_user_preferences
)

from backend.database.supabase_data.common import DateTimeEncoder