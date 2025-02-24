"""
Configuration settings for the GolfStats application.

This module provides configuration parameters for the application, including
API keys, database settings, and other environment-specific variables.
"""
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    logger.info(f"Loaded environment variables from {env_path}")
else:
    logger.warning(f".env file not found at {env_path}. Using default configuration or environment variables.")
    # Try loading from .env.example for development
    example_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.example')
    if os.path.exists(example_env_path):
        load_dotenv(example_env_path)
        logger.info(f"Loaded environment variables from {example_env_path} (for development only)")
    else:
        logger.warning(f".env.example file not found. Using default configuration or environment variables.")

# Default configuration
default_config = {
    # Application settings
    "app": {
        "name": "GolfStats",
        "debug": os.environ.get("APP_DEBUG", "true").lower() == "true",
        "environment": os.environ.get("APP_ENVIRONMENT", "development"),
        "secret_key": os.environ.get("APP_SECRET_KEY", "dev-secret-key-change-in-production")
    },
    
    # Database settings
    "database": {
        "type": os.environ.get("DB_TYPE", "postgresql"),  # 'sqlite', 'postgresql', 'mongodb'
        "sqlite": {
            "path": "data/golfstats.db"
        },
        "postgresql": {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": int(os.environ.get("DB_PORT", 5432)),
            "database": os.environ.get("DB_NAME", "golfstats"),
            "user": os.environ.get("DB_USER", "postgres"),
            "password": os.environ.get("DB_PASSWORD", "postgres")
        },
        "mongodb": {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": int(os.environ.get("DB_PORT", 27017)),
            "database": os.environ.get("DB_NAME", "golfstats")
        }
    },
    
    # Data scraper settings
    "scrapers": {
        "trackman": {
            "url": "https://mytrackman.com",
            "username": os.environ.get("TRACKMAN_USERNAME", ""),
            "password": os.environ.get("TRACKMAN_PASSWORD", ""),
            "headless": True
        },
        "arccos": {
            "url": "https://dashboard.arccosgolf.com",
            "email": os.environ.get("ARCCOS_EMAIL", ""),
            "password": os.environ.get("ARCCOS_PASSWORD", ""),
            "headless": True
        },
        "skytrak": {
            "url": "https://app.skytrakgolf.com",
            "username": os.environ.get("SKYTRAK_USERNAME", ""),
            "password": os.environ.get("SKYTRAK_PASSWORD", ""),
            "headless": True
        }
    },
    
    # Google API settings
    "google": {
        "oauth": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "redirect_uri": "http://localhost:8000/auth/google/callback"
        },
        "sheets": {
            "api_key": os.environ.get("GOOGLE_SHEETS_API_KEY", ""),
            "spreadsheet_id": os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID", "")
        }
    },
    
    # ETL job settings
    "etl": {
        "schedule": {
            "daily_update": os.environ.get("ETL_DAILY_UPDATE_SCHEDULE", "0 0 * * *"),  # Every day at midnight (cron format)
            "weekly_report": os.environ.get("ETL_WEEKLY_REPORT_SCHEDULE", "0 0 * * 0")   # Every Sunday at midnight
        },
        "output_dir": "data/etl"
    }
}

def load_config() -> Dict[str, Any]:
    """
    Load configuration, with environment variables overriding defaults.
    
    Returns:
        Dict containing merged configuration settings
    """
    # Since we're now using os.environ.get() with defaults in the default_config,
    # we don't need to do the individual overrides anymore.
    # Environment variables are already applied in the default_config.
    
    config = default_config.copy()
    
    # Log loaded configuration (excluding sensitive information)
    log_config = config.copy()
    # Remove sensitive information for logging
    if "database" in log_config and "postgresql" in log_config["database"]:
        log_config["database"]["postgresql"]["password"] = "********" if log_config["database"]["postgresql"]["password"] else ""
    
    if "scrapers" in log_config:
        for scraper in log_config["scrapers"].values():
            if "password" in scraper:
                scraper["password"] = "********" if scraper["password"] else ""
    
    if "google" in log_config and "oauth" in log_config["google"]:
        log_config["google"]["oauth"]["client_secret"] = "********" if log_config["google"]["oauth"]["client_secret"] else ""
    
    logger.info(f"Configuration loaded: {log_config}")
    
    return config

# Load configuration on module import
config = load_config()