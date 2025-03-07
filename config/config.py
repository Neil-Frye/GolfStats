"""
Configuration settings for the GolfStats application.

This module provides configuration parameters for the application, including
API keys, database settings, and other environment-specific variables.
"""
import os
import re
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables based on APP_ENVIRONMENT
env = os.getenv('APP_ENVIRONMENT', 'test').lower()
env_file = '.env.production' if env == 'production' else '.env.test'
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), env_file)

if os.path.exists(env_path):
    load_dotenv(env_path)
    logger.info(f"Loaded environment variables from {env_path} for {env} environment")
else:
    logger.warning(f"{env_file} not found at {env_path}. Using environment variables or defaults.")

default_config = {
    "app": {
        "name": "GolfStats",
        "debug": os.environ.get("APP_DEBUG", "true").lower() == "true",
        "environment": os.environ.get("APP_ENVIRONMENT", "development"),
        "secret_key": os.environ.get("APP_SECRET_KEY", "dev-secret-key-change-in-production")
    },
    
    "supabase": {
        "url": os.environ.get("SUPABASE_URL", ""),
        "anon_key": os.environ.get("SUPABASE_API_KEY") or os.environ.get("SUPABASE_KEY", ""),
        "db_url": os.environ.get("SUPABASE_DB_URL", ""),   # read from env
        "pooler_url": os.environ.get("SUPABASE_POOLER_URL", ""),
        "use_pooler": os.environ.get("SUPABASE_USE_POOLER", "false").lower() == "true"
    },
    
    "database": {
        "type": os.environ.get("DB_TYPE", "supabase"),  # 'sqlite', 'postgresql', 'supabase', 'mongodb'
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
        "supabase": {
            # will be filled in once we parse the supabase DB URL
        },
        "mongodb": {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": int(os.environ.get("DB_PORT", 27017)),
            "database": os.environ.get("DB_NAME", "golfstats")
        }
    },
    
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
    
    "google": {
        "oauth": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
        },
        "sheets": {
            "api_key": os.environ.get("GOOGLE_SHEETS_API_KEY", ""),
            "spreadsheet_id": os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID", "")
        }
    },
    
    "etl": {
        "schedule": {
            "daily_update": os.environ.get("ETL_DAILY_UPDATE_SCHEDULE", "0 0 * * *"),
            "weekly_report": os.environ.get("ETL_WEEKLY_REPORT_SCHEDULE", "0 0 * * 0")
        },
        "output_dir": "data/etl"
    }
}

def load_config() -> Dict[str, Any]:
    config = default_config.copy()
    
    # Always read environment for supabase (could change after import)
    config["supabase"] = {
        "url": os.environ.get("SUPABASE_URL", config["supabase"]["url"]),
        "anon_key": os.environ.get("SUPABASE_API_KEY", os.environ.get("SUPABASE_KEY", config["supabase"]["anon_key"])),
        "db_url": os.environ.get("SUPABASE_DB_URL", config["supabase"]["db_url"]),
        "pooler_url": os.environ.get("SUPABASE_POOLER_URL", config["supabase"]["pooler_url"]),
        "use_pooler": os.environ.get("SUPABASE_USE_POOLER", "false").lower() == "true"
    }
    
    if config["database"]["type"] == "supabase":
        # Decide which URL to use: db_url vs. pooler_url
        db_url = config["supabase"]["pooler_url"] if config["supabase"]["use_pooler"] else config["supabase"]["db_url"]
        
        # Attempt to parse it (optional, best-effort)
        # This pattern tolerates ?sslmode= etc. at the end:
        #   postgresql://user:pass@host:5432/dbname?sslmode=require
        match = re.match(r'^postgresql:\/\/([^:]+):([^@]+)@([^:]+):(\d+)\/([^?]+)(?:\?.*)?$', db_url)
        if match:
            user, password, host, port, database = match.groups()
            config["database"]["supabase"] = {
                "host": host,
                "port": int(port),
                "database": database,
                "user": user,
                "password": password,
                "connection_url": db_url
            }
            logger.info(f"Parsed Supabase DB URL for host: {host}")
        else:
            logger.warning("Could not parse Supabase DB URL; will rely on environment variables directly.")
    
    # IMPORTANT: Make a DEEP copy for logging that redacts sensitive fields
    # A regular copy() is shallow and might modify nested dictionaries in the original
    import copy
    log_config = copy.deepcopy(config)
    
    # Hide DB passwords & connection URLs in the COPY only
    if "database" in log_config:
        for db_type in ["postgresql", "supabase"]:
            if db_type in log_config["database"] and "password" in log_config["database"][db_type]:
                log_config["database"][db_type]["password"] = "********"
            if db_type in log_config["database"] and "connection_url" in log_config["database"][db_type]:
                log_config["database"][db_type]["connection_url"] = "********"
    
    # Hide scraper passwords in the COPY only
    if "scrapers" in log_config:
        for scraper in log_config["scrapers"].values():
            if "password" in scraper:
                scraper["password"] = "********"
    
    # Hide Google client secret in the COPY only
    if "google" in log_config and "oauth" in log_config["google"]:
        log_config["google"]["oauth"]["client_secret"] = "********"
    
    # Hide supabase anon key and DB URLs in the COPY only
    if "supabase" in log_config:
        log_config["supabase"]["anon_key"] = "********"
        log_config["supabase"]["db_url"] = "********"
        log_config["supabase"]["pooler_url"] = "********"
        
    # Verify we didn't accidentally modify the original config (debug)
    if "supabase" in config and "db_url" in config["supabase"]:
        has_stars = "********" in str(config["supabase"]["db_url"])
        logger.info(f"Original config supabase.db_url contains stars: {has_stars}")
        
    if "database" in config and "supabase" in config["database"] and "connection_url" in config["database"]["supabase"]:
        has_stars = "********" in str(config["database"]["supabase"]["connection_url"])
        logger.info(f"Original config database.supabase.connection_url contains stars: {has_stars}")
    
    logger.info(f"Configuration loaded: {log_config}")
    
    return config

config = load_config()
