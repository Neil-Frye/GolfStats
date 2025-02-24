"""
Configuration settings for the GolfStats application.

This module provides configuration parameters for the application, including
API keys, database settings, and other environment-specific variables.
"""
import os
from typing import Dict, Any

# Default configuration
default_config = {
    # Application settings
    "app": {
        "name": "GolfStats",
        "debug": True,
        "environment": "development",
        "secret_key": "dev-secret-key-change-in-production"
    },
    
    # Database settings
    "database": {
        "type": "sqlite",  # 'sqlite', 'postgresql', 'mongodb'
        "sqlite": {
            "path": "data/golfstats.db"
        },
        "postgresql": {
            "host": "localhost",
            "port": 5432,
            "database": "golfstats",
            "user": "postgres",
            "password": ""
        },
        "mongodb": {
            "host": "localhost",
            "port": 27017,
            "database": "golfstats"
        }
    },
    
    # Data scraper settings
    "scrapers": {
        "trackman": {
            "url": "https://mytrackman.com",
            "username": "",
            "password": "",
            "headless": True
        },
        "arccos": {
            "url": "https://dashboard.arccosgolf.com",
            "email": "",
            "password": "",
            "headless": True
        },
        "skytrak": {
            "url": "https://app.skytrakgolf.com",
            "username": "",
            "password": "",
            "headless": True
        }
    },
    
    # Google API settings
    "google": {
        "oauth": {
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "http://localhost:5000/auth/google/callback"
        },
        "sheets": {
            "api_key": "",
            "spreadsheet_id": ""
        }
    },
    
    # ETL job settings
    "etl": {
        "schedule": {
            "daily_update": "0 0 * * *",  # Every day at midnight (cron format)
            "weekly_report": "0 0 * * 0"   # Every Sunday at midnight
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
    config = default_config.copy()
    
    # Override with environment variables
    # Database settings
    if os.environ.get("DB_TYPE"):
        config["database"]["type"] = os.environ.get("DB_TYPE")
        
    if os.environ.get("DB_HOST"):
        config["database"]["postgresql"]["host"] = os.environ.get("DB_HOST")
        config["database"]["mongodb"]["host"] = os.environ.get("DB_HOST")
        
    if os.environ.get("DB_PORT"):
        try:
            port = int(os.environ.get("DB_PORT"))
            config["database"]["postgresql"]["port"] = port
            config["database"]["mongodb"]["port"] = port
        except ValueError:
            pass
            
    if os.environ.get("DB_NAME"):
        config["database"]["postgresql"]["database"] = os.environ.get("DB_NAME")
        config["database"]["mongodb"]["database"] = os.environ.get("DB_NAME")
        
    if os.environ.get("DB_USER"):
        config["database"]["postgresql"]["user"] = os.environ.get("DB_USER")
        
    if os.environ.get("DB_PASSWORD"):
        config["database"]["postgresql"]["password"] = os.environ.get("DB_PASSWORD")
        
    # Scraper credentials
    if os.environ.get("TRACKMAN_USERNAME"):
        config["scrapers"]["trackman"]["username"] = os.environ.get("TRACKMAN_USERNAME")
        
    if os.environ.get("TRACKMAN_PASSWORD"):
        config["scrapers"]["trackman"]["password"] = os.environ.get("TRACKMAN_PASSWORD")
        
    if os.environ.get("ARCCOS_EMAIL"):
        config["scrapers"]["arccos"]["email"] = os.environ.get("ARCCOS_EMAIL")
        
    if os.environ.get("ARCCOS_PASSWORD"):
        config["scrapers"]["arccos"]["password"] = os.environ.get("ARCCOS_PASSWORD")
        
    if os.environ.get("SKYTRAK_USERNAME"):
        config["scrapers"]["skytrak"]["username"] = os.environ.get("SKYTRAK_USERNAME")
        
    if os.environ.get("SKYTRAK_PASSWORD"):
        config["scrapers"]["skytrak"]["password"] = os.environ.get("SKYTRAK_PASSWORD")
        
    # Google API settings
    if os.environ.get("GOOGLE_CLIENT_ID"):
        config["google"]["oauth"]["client_id"] = os.environ.get("GOOGLE_CLIENT_ID")
        
    if os.environ.get("GOOGLE_CLIENT_SECRET"):
        config["google"]["oauth"]["client_secret"] = os.environ.get("GOOGLE_CLIENT_SECRET")
        
    if os.environ.get("GOOGLE_SHEETS_API_KEY"):
        config["google"]["sheets"]["api_key"] = os.environ.get("GOOGLE_SHEETS_API_KEY")
        
    if os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID"):
        config["google"]["sheets"]["spreadsheet_id"] = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
    
    return config

# Load configuration on module import
config = load_config()