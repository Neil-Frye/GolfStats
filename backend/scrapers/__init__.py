"""
Scrapers module for GolfStats application.

This module provides unified access to all scrapers (Trackman, Arccos, SkyTrak),
with graceful fallbacks when web scraping dependencies aren't available.
"""
import os
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Import mock implementations
from .mock import (
    get_mock_arccos_data,
    get_mock_trackman_data,
    get_mock_skytrak_data
)

# Check if we're in a serverless environment that may not have selenium
try:
    # Try to import the real scrapers
    from .arccos_scraper import get_arrcos_data as _real_get_arccos_data
    from .trackman_scraper import get_trackman_data as _real_get_trackman_data
    from .skytrak_scraper import get_skytrak_data as _real_get_skytrak_data
    
    HAS_SELENIUM = True
    logger.info("Selenium available - using real scrapers")
except ImportError:
    # Mark that we don't have the selenium dependency
    HAS_SELENIUM = False
    logger.warning("Selenium not available - using mock scrapers")

# Unified interface for Arccos data
def get_arccos_data(user_id: str, limit: int = 10, use_user_credentials: bool = True) -> List[int]:
    """
    Get Arccos golf data for a user.
    
    Args:
        user_id: ID of the user in the database
        limit: Maximum number of rounds to retrieve
        use_user_credentials: Whether to use user-specific credentials
        
    Returns:
        List of round IDs that were successfully processed
    """
    if HAS_SELENIUM:
        try:
            return _real_get_arccos_data(user_id, limit, use_user_credentials)
        except Exception as e:
            logger.error(f"Error using real Arccos scraper: {str(e)}")
            logger.info("Falling back to mock implementation")
    
    # Use the mock implementation
    logger.info(f"Using mock Arccos scraper for user {user_id}")
    return get_mock_arccos_data(user_id, limit, use_user_credentials)

# Unified interface for Trackman data
def get_trackman_data(user_id: str, limit: int = 20, use_user_credentials: bool = True) -> List[int]:
    """
    Get Trackman golf data for a user.
    
    Args:
        user_id: ID of the user in the database
        limit: Maximum number of sessions to retrieve
        use_user_credentials: Whether to use user-specific credentials
        
    Returns:
        List of session IDs that were successfully processed
    """
    if HAS_SELENIUM:
        try:
            return _real_get_trackman_data(user_id, limit, use_user_credentials)
        except Exception as e:
            logger.error(f"Error using real Trackman scraper: {str(e)}")
            logger.info("Falling back to mock implementation")
    
    # Use the mock implementation
    logger.info(f"Using mock Trackman scraper for user {user_id}")
    return get_mock_trackman_data(user_id, limit, use_user_credentials)

# Unified interface for SkyTrak data
def get_skytrak_data(user_id: str, limit: int = 20, use_user_credentials: bool = True) -> List[int]:
    """
    Get SkyTrak golf data for a user.
    
    Args:
        user_id: ID of the user in the database
        limit: Maximum number of sessions to retrieve
        use_user_credentials: Whether to use user-specific credentials
        
    Returns:
        List of session IDs that were successfully processed
    """
    if HAS_SELENIUM:
        try:
            return _real_get_skytrak_data(user_id, limit, use_user_credentials)
        except Exception as e:
            logger.error(f"Error using real SkyTrak scraper: {str(e)}")
            logger.info("Falling back to mock implementation")
    
    # Use the mock implementation
    logger.info(f"Using mock SkyTrak scraper for user {user_id}")
    return get_mock_skytrak_data(user_id, limit, use_user_credentials)