"""
Configuration settings for the GolfStats application.

This module is maintained for backward compatibility.
All configuration is now centralized in the env.py module.
"""
import logging
from typing import Dict, Any
from config.env import env, config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# For backward compatibility, log the configuration
logger.info(f"Configuration loaded from env module")

# Export the config for backward compatibility
__all__ = ['config', 'env']