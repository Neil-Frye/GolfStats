"""
Environment configuration module for the GolfStats application.

This module serves as a single source of truth for all environment variables
and configuration settings. It manages loading from .env files and provides
a consistent interface for accessing configuration across the application.
"""
import os
import re
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import copy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Environment:
    """Environment configuration manager for GolfStats application."""
    
    # Constants for environment types
    TEST = "test"
    PRODUCTION = "production"
    
    def __init__(self):
        """Initialize the environment configuration."""
        self._config = None
        self._load_environment_file()
        self._load_config()
    
    def _load_environment_file(self) -> None:
        """Load the appropriate .env file based on environment."""
        # Determine environment (test or production)
        self.env_name = os.getenv('APP_ENVIRONMENT', self.TEST).lower()
        
        # Set the right .env file based on environment
        env_file = f'.env.{self.env_name}'
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), env_file)
        
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"Loaded environment variables from {env_path} for {self.env_name} environment")
        else:
            logger.warning(f"{env_file} not found at {env_path}. Using environment variables or defaults.")
    
    def _load_config(self) -> None:
        """Load configuration from environment variables with defaults."""
        self._config = {
            "app": {
                "name": "GolfStats",
                "debug": os.getenv("APP_DEBUG", "true").lower() == "true",
                "environment": self.env_name,
                "secret_key": os.getenv("APP_SECRET_KEY", "dev-secret-key-change-in-production")
            },
            
            "supabase": {
                "url": os.getenv("SUPABASE_URL", ""),
                "anon_key": os.getenv("SUPABASE_API_KEY") or os.getenv("SUPABASE_KEY", ""),
                "db_url": os.getenv("SUPABASE_DB_URL", ""),
                "pooler_url": os.getenv("SUPABASE_POOLER_URL", ""),
                "use_pooler": os.getenv("SUPABASE_USE_POOLER", "false").lower() == "true"
            },
            
            "database": {
                "type": os.getenv("DB_TYPE", "supabase"),  # 'sqlite', 'postgresql', 'supabase', 'mongodb'
                "sqlite": {
                    "path": "data/golfstats.db"
                },
                "postgresql": {
                    "host": os.getenv("DB_HOST", "localhost"),
                    "port": int(os.getenv("DB_PORT", 5432)),
                    "database": os.getenv("DB_NAME", "golfstats"),
                    "user": os.getenv("DB_USER", "postgres"),
                    "password": os.getenv("DB_PASSWORD", "postgres")
                },
                "supabase": {
                    # Will be filled based on Supabase DB URL
                },
                "mongodb": {
                    "host": os.getenv("DB_HOST", "localhost"),
                    "port": int(os.getenv("DB_PORT", 27017)),
                    "database": os.getenv("DB_NAME", "golfstats")
                }
            },
            
            "scrapers": {
                "trackman": {
                    "url": "https://mytrackman.com",
                    "username": os.getenv("TRACKMAN_USERNAME", ""),
                    "password": os.getenv("TRACKMAN_PASSWORD", ""),
                    "headless": True
                },
                "arccos": {
                    "url": "https://dashboard.arccosgolf.com",
                    "email": os.getenv("ARCCOS_EMAIL", ""),
                    "password": os.getenv("ARCCOS_PASSWORD", ""),
                    "headless": True
                },
                "skytrak": {
                    "url": "https://app.skytrakgolf.com",
                    "username": os.getenv("SKYTRAK_USERNAME", ""),
                    "password": os.getenv("SKYTRAK_PASSWORD", ""),
                    "headless": True
                }
            },
            
            "google": {
                "oauth": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                    "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
                },
                "sheets": {
                    "api_key": os.getenv("GOOGLE_SHEETS_API_KEY", ""),
                    "spreadsheet_id": os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
                }
            },
            
            "etl": {
                "schedule": {
                    "daily_update": os.getenv("ETL_DAILY_UPDATE_SCHEDULE", "0 0 * * *"),
                    "weekly_report": os.getenv("ETL_WEEKLY_REPORT_SCHEDULE", "0 0 * * 0")
                },
                "output_dir": "data/etl"
            }
        }
        
        # Parse Supabase database connection URL if available
        self._parse_supabase_db_url()
    
    def _parse_supabase_db_url(self) -> None:
        """Parse the Supabase database URL into connection details."""
        if self._config["database"]["type"] != "supabase":
            return
            
        # Decide which URL to use: db_url vs. pooler_url
        db_url = self._config["supabase"]["pooler_url"] if self._config["supabase"]["use_pooler"] else self._config["supabase"]["db_url"]
        
        # Attempt to parse the URL
        if not db_url:
            # If no DB URL provided, try to construct one from the Supabase password
            supabase_password = os.getenv("SUPABASE_PASSWORD", "")
            if supabase_password:
                # Extract Supabase project ID from URL
                supabase_url = self._config["supabase"]["url"]
                project_id = None
                
                if supabase_url:
                    match = re.match(r'https?://([^.]+)\.supabase\.co', supabase_url)
                    if match:
                        project_id = match.group(1)
                
                if project_id:
                    db_url = f"postgresql://postgres:{supabase_password}@db.{project_id}.supabase.co:5432/postgres"
                    self._config["supabase"]["db_url"] = db_url
                    logger.info(f"Constructed Supabase DB URL using extracted project ID")
            else:
                logger.warning("No Supabase password found for direct database connection")
                return
        
        # Parse the URL to extract connection details
        match = re.match(r'^postgresql:\/\/([^:]+):([^@]+)@([^:]+):(\d+)\/([^?]+)(?:\?.*)?$', db_url)
        if match:
            user, password, host, port, database = match.groups()
            self._config["database"]["supabase"] = {
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

    def get_config(self) -> Dict[str, Any]:
        """
        Get the full configuration dictionary.
        
        Returns:
            Dict[str, Any]: The configuration dictionary.
        """
        return self._config
    
    def get_database_uri(self) -> str:
        """
        Get the database URI based on the configured database type.
        
        Returns:
            str: The database URI.
        """
        db_type = self._config["database"]["type"]
        
        if db_type == "sqlite":
            db_path = self._config["database"]["sqlite"]["path"]
            return f"sqlite:///{db_path}"
        
        elif db_type == "postgresql":
            pg_config = self._config["database"]["postgresql"]
            return f"postgresql://{pg_config['user']}:{pg_config['password']}@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
        
        elif db_type == "supabase":
            if "supabase" in self._config["database"] and "connection_url" in self._config["database"]["supabase"]:
                return self._config["database"]["supabase"]["connection_url"]
            elif self._config["supabase"]["db_url"]:
                return self._config["supabase"]["db_url"]
            else:
                # Fallback to a constructed URL if all else fails
                logger.warning("Using fallback method to construct Supabase DB URL")
                supabase_password = os.getenv("SUPABASE_PASSWORD", "")
                supabase_url = self._config["supabase"]["url"]
                project_id = None
                
                if supabase_url:
                    match = re.match(r'https?://([^.]+)\.supabase\.co', supabase_url)
                    if match:
                        project_id = match.group(1)
                
                if project_id and supabase_password:
                    return f"postgresql://postgres:{supabase_password}@db.{project_id}.supabase.co:5432/postgres"
                
                logger.error("Could not construct Supabase DB URL. Missing required parameters.")
                return ""
        
        elif db_type == "mongodb":
            mongo_config = self._config["database"]["mongodb"]
            return f"mongodb://{mongo_config['host']}:{mongo_config['port']}/{mongo_config['database']}"
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def get_db_connect_args(self) -> Dict[str, Any]:
        """
        Get database connection arguments based on database type.
        
        Returns:
            Dict[str, Any]: The connection arguments.
        """
        db_type = self._config["database"]["type"]
        
        if db_type == "sqlite":
            return {"check_same_thread": False}
        elif db_type in ["postgresql", "supabase"]:
            return {"sslmode": "require"} if db_type == "supabase" else {}
        else:
            return {}
    
    def get_db_pool_settings(self) -> Dict[str, Any]:
        """
        Get database connection pool settings.
        
        Returns:
            Dict[str, Any]: Pool settings dictionary.
        """
        db_type = self._config["database"]["type"]
        settings = {}
        
        if db_type in ["postgresql", "supabase"]:
            settings = {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_recycle": 1800
            }
            
            # Adjust for Supabase pooler
            if db_type == "supabase" and self._config["supabase"]["use_pooler"]:
                settings["pool_size"] = 2
                settings["max_overflow"] = 3
        
        return settings
    
    def get_masked_config(self) -> Dict[str, Any]:
        """
        Get a copy of the configuration with sensitive values masked.
        
        Returns:
            Dict[str, Any]: The masked configuration.
        """
        # Make a deep copy of the config to avoid modifying the original
        masked_config = copy.deepcopy(self._config)
        
        # Hide database passwords
        if "database" in masked_config:
            for db_type in ["postgresql", "supabase"]:
                if db_type in masked_config["database"] and "password" in masked_config["database"][db_type]:
                    masked_config["database"][db_type]["password"] = "********"
                if db_type in masked_config["database"] and "connection_url" in masked_config["database"][db_type]:
                    masked_config["database"][db_type]["connection_url"] = "********"
        
        # Hide scraper passwords
        if "scrapers" in masked_config:
            for scraper in masked_config["scrapers"].values():
                if "password" in scraper:
                    scraper["password"] = "********"
        
        # Hide Google client secret
        if "google" in masked_config and "oauth" in masked_config["google"]:
            masked_config["google"]["oauth"]["client_secret"] = "********"
        
        # Hide Supabase keys and URLs
        if "supabase" in masked_config:
            masked_config["supabase"]["anon_key"] = "********"
            masked_config["supabase"]["db_url"] = "********"
            masked_config["supabase"]["pooler_url"] = "********"
        
        return masked_config
    
    def is_production(self) -> bool:
        """
        Check if the application is running in production mode.
        
        Returns:
            bool: True if in production, False otherwise.
        """
        return self.env_name == self.PRODUCTION
    
    def is_test(self) -> bool:
        """
        Check if the application is running in test mode.
        
        Returns:
            bool: True if in test mode, False otherwise.
        """
        return self.env_name == self.TEST
    
    def get_database_type(self) -> str:
        """
        Get the configured database type.
        
        Returns:
            str: The database type.
        """
        return self._config["database"]["type"]
    
    def get_supabase_url(self) -> str:
        """
        Get the Supabase project URL.
        
        Returns:
            str: The Supabase URL.
        """
        return self._config["supabase"]["url"]
    
    def get_supabase_key(self) -> str:
        """
        Get the Supabase API key.
        
        Returns:
            str: The Supabase API key.
        """
        return self._config["supabase"]["anon_key"]
    
    def __getitem__(self, key: str) -> Any:
        """
        Allow dictionary-style access to configuration sections.
        
        Args:
            key: The configuration section key.
            
        Returns:
            Any: The configuration section.
        """
        return self._config[key]


# Create a singleton instance
env = Environment()

# For backwards compatibility with the previous config approach
config = env.get_config()