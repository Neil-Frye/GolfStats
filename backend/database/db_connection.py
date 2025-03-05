"""
Database connection management for GolfStats application.

This module provides database connection utilities for the application,
supporting SQLite, PostgreSQL, and optionally MongoDB.
"""
from typing import Generator, Optional, Any
import logging
import os
import sys
from contextlib import contextmanager

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from config.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Determine which database to use from config
db_type = config["database"]["type"]

# Build the database URI based on configuration
if db_type == "sqlite":
    db_path = config["database"]["sqlite"]["path"]
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    DATABASE_URI = f"sqlite:///{db_path}"
    connect_args = {"check_same_thread": False}
    poolclass = None
    
elif db_type == "postgresql":
    pg_config = config["database"]["postgresql"]
    DATABASE_URI = f"postgresql://{pg_config['user']}:{pg_config['password']}@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
    connect_args = {}
    poolclass = QueuePool
    
elif db_type == "supabase":
    # Initialize DATABASE_URI to empty to avoid reference errors
    DATABASE_URI = ""
    
    # Get Supabase credentials
    supabase_password = os.environ.get("SUPABASE_PASSWORD", "")
    supabase_api_key = os.environ.get("SUPABASE_API_KEY", "") or os.environ.get("SUPABASE_KEY", "")
    supabase_db_url = os.environ.get("SUPABASE_DB_URL", "")
    
    logger.info(f"Supabase credentials available: password={bool(supabase_password)}, API key={bool(supabase_api_key)}, DB URL={bool(supabase_db_url)}")
    
    # Debug the supabase configuration we're receiving
    if "supabase" in config:
        logger.info(f"Config has supabase section: {list(config['supabase'].keys())}")
        has_db_url = "db_url" in config["supabase"] and config["supabase"]["db_url"]
        db_url_is_stars = has_db_url and "********" in str(config["supabase"]["db_url"])
        logger.info(f"Config supabase.db_url exists: {has_db_url}, contains stars: {db_url_is_stars}")
    
    if "database" in config and "supabase" in config["database"]:
        logger.info(f"Config has database.supabase section: {list(config['database']['supabase'].keys())}")
        has_conn_url = "connection_url" in config["database"]["supabase"] and config["database"]["supabase"]["connection_url"]
        conn_url_is_stars = has_conn_url and "********" in str(config["database"]["supabase"]["connection_url"])
        logger.info(f"Config database.supabase.connection_url exists: {has_conn_url}, contains stars: {conn_url_is_stars}")
    
    # Try different methods to construct the DATABASE_URI
    if "supabase" in config["database"] and "connection_url" in config["database"]["supabase"] and config["database"]["supabase"]["connection_url"]:
        # Method 1: Use the pre-parsed connection URL from config
        DATABASE_URI = config["database"]["supabase"]["connection_url"]
        
        # Make sure we don't have stars in the actual connection string
        if "********" in DATABASE_URI:
            logger.warning("Connection URL contains stars! This suggests a logging issue. Falling back to environment variables.")
            DATABASE_URI = ""  # Reset since it contains stars
        else:
            logger.info(f"Using Supabase connection URL from parsed config at {config['database']['supabase']['host']}")
    
    # If we don't have a valid DATABASE_URI yet, try other methods
    if not DATABASE_URI:
        if supabase_db_url:
            # Method 2: Use the DB_URL environment variable directly
            DATABASE_URI = supabase_db_url
            logger.info(f"Using SUPABASE_DB_URL environment variable directly")
        else:
            # Method 3: Construct the URL using available credentials
            # For Supabase, some sources say to use the password, others say to use the API key
            # We'll try both options but prefer the dedicated password
            db_password = supabase_password or supabase_api_key
            
            if not db_password:
                logger.warning("No Supabase password or API key found! Connection will likely fail.")
                db_password = ""
            
            DATABASE_URI = f"postgresql://postgres:{db_password}@db.qfuvwfghevxhnkfrwmwk.supabase.co:5432/postgres"
            logger.info(f"Constructed Supabase connection URL with explicit parameters")
    
    # Debug output - mask password for security but show structure
    debug_uri = DATABASE_URI
    if '@' in debug_uri:
        parts = debug_uri.split('@')
        auth_part = parts[0].split(':')
        # Replace password with ****** but keep structure visible
        if len(auth_part) > 2:
            masked_uri = f"{auth_part[0]}:******@{parts[1]}"
            logger.info(f"Final connection string structure: {masked_uri}")
    
    # SSL required for Supabase connections
    connect_args = {"sslmode": "require"}
    poolclass = QueuePool
    
elif db_type == "mongodb":
    # MongoDB support would require pymongo instead of SQLAlchemy
    # This is a placeholder for potential future implementation
    mongo_config = config["database"]["mongodb"]
    logger.warning("MongoDB support is not yet fully implemented")
    DATABASE_URI = f"mongodb://{mongo_config['host']}:{mongo_config['port']}/{mongo_config['database']}"
    connect_args = {}
    poolclass = None
    
else:
    raise ValueError(f"Unsupported database type: {db_type}")

# Create database engine with appropriate settings
engine_args = {
    "echo": config["app"]["debug"],  # SQL echo for debugging
    "connect_args": connect_args
}

if poolclass:
    engine_args["poolclass"] = poolclass
    # Configure PostgreSQL specific pooling settings
    if db_type in ["postgresql", "supabase"]:
        engine_args["pool_size"] = 5  # Number of connections to keep open
        engine_args["max_overflow"] = 10  # Max number of connections to create beyond pool_size
        engine_args["pool_timeout"] = 30  # Seconds to wait before giving up on getting a connection
        engine_args["pool_recycle"] = 1800  # Recycle connections after 30 minutes
        
        # For Supabase pooler connections, adjust settings
        if db_type == "supabase" and config["supabase"]["use_pooler"]:
            # Pooler already manages connection pooling, so we use minimal SQLAlchemy pooling
            engine_args["pool_size"] = 2
            engine_args["max_overflow"] = 3

# For logging, mask credentials but still show the host
if '@' in DATABASE_URI:
    # Extract user:pass and host part
    parts = DATABASE_URI.split('@')
    # Display only the host part for privacy, not the credentials
    host_part = parts[-1]
    logger.info(f"Connecting to database: {db_type} at {host_part}")
else:
    logger.info(f"Connecting to database: {db_type} at {DATABASE_URI}")

# Additional debug info
logger.info(f"Engine arguments: {engine_args}")
logger.info(f"SSL mode: {connect_args.get('sslmode', 'not specified')}")

# Print without logging to ensure visibility
print(f"\n*** DATABASE CONNECTION INFORMATION ***")
print(f"Database type: {db_type}")
if '@' in DATABASE_URI:
    user_part = DATABASE_URI.split('@')[0].split(':')[0]
    host_part = DATABASE_URI.split('@')[1]
    print(f"Connection: {user_part}:*****@{host_part}")
else:
    print(f"Connection: {DATABASE_URI}")
print(f"Engine arguments: {str(engine_args)}")
print(f"*** END DATABASE INFO ***\n")

try:
    engine = create_engine(DATABASE_URI, **engine_args)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    print(f"\n*** DATABASE CONNECTION ERROR ***")
    print(f"Error: {str(e)}")
    print(f"*** END ERROR ***\n")
    raise

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the declarative base for ORM models
Base = declarative_base()
metadata = MetaData()

# For SQLite, enable foreign key support
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if db_type == "sqlite":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get a database session from the pool.
    
    Yields:
        SQLAlchemy Session
        
    Usage:
        with get_db() as db:
            db.query(...)
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

def get_db_session() -> Generator[Session, None, None]:
    """
    Get a database session as a generator (for dependency injection).
    
    Yields:
        SQLAlchemy Session
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

def init_db():
    """
    Initialize the database by creating all tables.
    
    This should be called when the application starts.
    """
    # Import all models to ensure they're registered with Base
    from backend.models import user, golf_data
    
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized with type: {db_type}")
    
    if db_type == "postgresql":
        # Check if database exists and create it if it doesn't
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Found existing tables: {tables}")

def get_mongodb_client() -> Optional[Any]:
    """
    Get a MongoDB client if MongoDB is configured.
    
    Returns:
        MongoDB client or None if not configured
    """
    if db_type != "mongodb":
        return None
    
    try:
        from pymongo import MongoClient
        mongo_config = config["database"]["mongodb"]
        client = MongoClient(
            host=mongo_config["host"],
            port=mongo_config["port"]
        )
        return client[mongo_config["database"]]
    except ImportError:
        logger.error("pymongo not installed, MongoDB support unavailable")
        return None
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        return None