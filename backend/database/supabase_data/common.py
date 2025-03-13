"""
Common utilities for Supabase data access.
"""
import os
import logging
import json
import datetime
from typing import Dict, Any

# Add the project root directory to Python path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.supabase_client import get_supabase

# Configure logging
logger = logging.getLogger(__name__)

# Utility class for JSON serialization
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)