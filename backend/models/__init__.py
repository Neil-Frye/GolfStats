"""
Models package for GolfStats application.

This package contains SQLAlchemy ORM models for the application's database.
"""

# Import models to make them available
from . import user
from . import golf_data

# List of all models for imports
__all__ = ['user', 'golf_data']