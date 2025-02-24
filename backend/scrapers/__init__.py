"""
GolfStats scrapers package for collecting data from various golf tracking systems.

This package contains scrapers for different golf tracking platforms, including
Trackman, Arccos Golf, and SkyTrak.
"""

from typing import Dict, Union, Any, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)