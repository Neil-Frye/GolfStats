"""
Mock Scrapers for GolfStats application.

This module provides mock implementations of the scraper functionality for use in
serverless environments or when Selenium dependencies are not available.
"""
import logging
from typing import List, Dict, Any, Optional
import uuid
import datetime
import random

# Configure logging
logger = logging.getLogger(__name__)

def get_mock_arccos_data(user_id: str, limit: int = 10, use_user_credentials: bool = True) -> List[int]:
    """
    Mock implementation of Arccos data scraper.
    
    Args:
        user_id: ID of the user in the database
        limit: Maximum number of rounds to retrieve
        use_user_credentials: Whether to use user-specific credentials
        
    Returns:
        Empty list - mock implementation doesn't actually scrape data
    """
    logger.info(f"Mock Arccos scraper called for user {user_id} with limit {limit}")
    return []

def get_mock_trackman_data(user_id: str, limit: int = 20, use_user_credentials: bool = True) -> List[int]:
    """
    Mock implementation of Trackman data scraper.
    
    Args:
        user_id: ID of the user in the database
        limit: Maximum number of sessions to retrieve
        use_user_credentials: Whether to use user-specific credentials
        
    Returns:
        Empty list - mock implementation doesn't actually scrape data
    """
    logger.info(f"Mock Trackman scraper called for user {user_id} with limit {limit}")
    return []

def get_mock_skytrak_data(user_id: str, limit: int = 20, use_user_credentials: bool = True) -> List[int]:
    """
    Mock implementation of SkyTrak data scraper.
    
    Args:
        user_id: ID of the user in the database
        limit: Maximum number of sessions to retrieve
        use_user_credentials: Whether to use user-specific credentials
        
    Returns:
        Empty list - mock implementation doesn't actually scrape data
    """
    logger.info(f"Mock SkyTrak scraper called for user {user_id} with limit {limit}")
    return []