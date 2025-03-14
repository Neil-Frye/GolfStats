# Supabase Data Access Layer

This directory contains modules for accessing and manipulating data in the Supabase database.

## Shot Data Handling

We've refactored the shot data handling to eliminate duplicated code between course shots and range shots. 

### Key Components:

1. **shot_utils.py**: Central utilities for shot data processing
   - `calculate_derived_metrics()`: Computes metrics like carry efficiency
   - `prepare_shot_data()`: Prepares shot data with proper context fields
   - `insert_shots()`: Universal function for inserting one or multiple shots

2. **shots.py**: Main API for golf shots (both course and range)
   - Uses shot_utils for all data processing and insertion
   - Provides context-specific wrapper functions

3. **range_shots.py**: (Deprecated) Range session management
   - Range shot functions now use shot_utils directly
   - Session management functions remain in this file

### Usage Examples:

#### Adding a Single Shot

```python
from backend.database.supabase_data.shot_utils import insert_shots

# Add a course shot
course_shot = {
    'club': 'Driver', 
    'ball_speed_mph': 150,
    'carry_distance_yards': 250
}
result = insert_shots(course_shot, hole_id, 'hole', token)

# Add a range shot
range_shot = {
    'club': 'Driver', 
    'ball_speed_mph': 150,
    'carry_distance_yards': 250
}
result = insert_shots(range_shot, session_id, 'session', token)
```

#### Adding Multiple Shots

```python
from backend.database.supabase_data.shot_utils import insert_shots

# Multiple shots (auto-numbered in sequence)
shots = [
    {'club': 'Driver', 'ball_speed_mph': 150},
    {'club': '7 Iron', 'ball_speed_mph': 120}
]

# Add to a hole
results = insert_shots(shots, hole_id, 'hole', token)

# Add to a range session
results = insert_shots(shots, session_id, 'session', token)
```

### Benefits of the Refactored Approach:

1. **Single source of truth** for shot data processing logic
2. **Reduced code duplication** between course and range shot handling
3. **Consistent treatment** of derived metrics calculation
4. **Unified interface** for adding both single and multiple shots
5. **Context-agnostic processing** with context type parameter

### Note on Deprecated Code:

The `range_shots.py` module contains several deprecated functions that now forward to the appropriate functions in `shots.py` or directly to `shot_utils.py`. These are maintained for backward compatibility but will be removed in a future update.