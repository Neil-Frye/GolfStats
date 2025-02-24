"""
Database connection management for GolfStats application.

This module provides database connection utilities for the application,
supporting SQLite, PostgreSQL, and optionally MongoDB.
"""
from typing import Generator, Optional, Any
import logging
import os
from contextlib import contextmanager

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

engine = create_engine(DATABASE_URI, **engine_args)

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
    from backend.models import user
    
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized with type: {db_type}")

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