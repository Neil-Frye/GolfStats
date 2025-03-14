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

# Import from the new centralized environment module
from config.env import env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get database connection information from the environment
db_type = env.get_database_type()
DATABASE_URI = env.get_database_uri()
connect_args = env.get_db_connect_args()

# Determine the appropriate pool class
poolclass = None
if db_type in ["postgresql", "supabase"]:
    poolclass = QueuePool

# Create database engine with appropriate settings
engine_args = {
    "echo": env["app"]["debug"],  # SQL echo for debugging
    "connect_args": connect_args
}

if poolclass:
    engine_args["poolclass"] = poolclass
    
    # Add pool settings if applicable
    if db_type in ["postgresql", "supabase"]:
        pool_settings = env.get_db_pool_settings()
        engine_args.update(pool_settings)

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

# Print database connection info for visibility
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
        mongo_config = env["database"]["mongodb"]
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