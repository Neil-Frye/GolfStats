# Supabase Data Access Package

This package provides modular access to Supabase data tables for the GolfStats application.

## Package Structure

The package is organized into domain-specific modules:

- `rounds.py`: Golf round management functions
- `shots.py`: Golf shot and hole management functions
- `stats.py`: Statistics and analytics functions
- `clubs.py`: Club management functions
- `user_preferences.py`: User preferences and settings functions
- `common.py`: Shared utilities and base classes

Each module contains functions related to a specific domain, making the code more maintainable and easier to understand.

## Usage

You can import functions directly from the specific module:

```python
from backend.database.supabase_data.rounds import get_golf_rounds
from backend.database.supabase_data.clubs import get_user_clubs
```

Or you can import from the package itself, which re-exports all functions:

```python
from backend.database.supabase_data import get_golf_rounds, get_user_clubs
```

## Migration

The legacy module `backend.database.supabase_data.py` has been refactored into this package structure. The original module is now deprecated and re-exports functions from this package to maintain backward compatibility.

## Design Considerations

- **Domain-Driven Design**: Functions are grouped by their domain to improve code organization.
- **Backward Compatibility**: All functions are re-exported from the package's `__init__.py` to maintain backward compatibility.
- **Modular Architecture**: Each module focuses on a specific concern, making the code more maintainable.
- **Type Hints**: All functions include proper type hints for better IDE support and code safety.
- **Error Handling**: Consistent error handling patterns across all modules.