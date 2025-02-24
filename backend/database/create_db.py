"""
Database creation script for GolfStats application.

This script creates the PostgreSQL database if it doesn't exist
and initializes the schema for the application.
"""
import logging
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy_utils import database_exists, create_database

from config.config import config
from backend.database.db_connection import init_db, engine, Base, DATABASE_URI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_postgres_db():
    """Create the PostgreSQL database if it doesn't exist."""
    if database_exists(DATABASE_URI):
        logger.info(f"Database already exists: {config['database']['postgresql']['database']}")
        return

    # Get database connection parameters
    pg_config = config["database"]["postgresql"]
    db_name = pg_config["database"]
    user = pg_config["user"]
    password = pg_config["password"]
    host = pg_config["host"]
    port = pg_config["port"]

    try:
        # Connect to PostgreSQL server with superuser privileges (usually postgres)
        conn = psycopg2.connect(
            host=host, 
            port=port, 
            user=user, 
            password=password, 
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE {db_name}")
        logger.info(f"Created database: {db_name}")
        
        # Close connection
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        logger.error(f"Error creating database: {e}")
        # Try SQLAlchemy method as fallback
        try:
            create_database(DATABASE_URI)
            logger.info(f"Created database using SQLAlchemy: {db_name}")
        except Exception as e2:
            logger.error(f"Could not create database: {e2}")
            raise

def main():
    """Main function to create and initialize the database."""
    # Check if we're using PostgreSQL
    db_type = config["database"]["type"]
    if db_type != "postgresql":
        logger.info(f"Using {db_type} database, no need to create it manually")
        init_db()
        return

    # Create PostgreSQL database
    create_postgres_db()
    
    # Initialize database schema
    init_db()
    
    logger.info("Database creation and initialization complete")

if __name__ == "__main__":
    main()