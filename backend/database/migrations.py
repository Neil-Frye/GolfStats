"""
Database migrations for GolfStats application.

This module allows running database migrations to add new columns or tables.
"""
import os
import sys
import logging
from sqlalchemy import text, inspect

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.db_connection import get_db, engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_if_column_exists(table_name, column_name):
    """
    Check if a column exists in a table.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column
        
    Returns:
        bool: True if column exists
    """
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns

def add_tracker_credentials_columns():
    """
    Add credentials columns to users table.
    """
    with get_db() as db:
        try:
            # Check if columns exist first
            if not check_if_column_exists('users', 'trackman_username'):
                db.execute(text("ALTER TABLE users ADD COLUMN trackman_username VARCHAR(255)"))
                logger.info("Added trackman_username column to users table")
            
            if not check_if_column_exists('users', 'trackman_password'):
                db.execute(text("ALTER TABLE users ADD COLUMN trackman_password VARCHAR(255)"))
                logger.info("Added trackman_password column to users table")
            
            if not check_if_column_exists('users', 'arccos_email'):
                db.execute(text("ALTER TABLE users ADD COLUMN arccos_email VARCHAR(255)"))
                logger.info("Added arccos_email column to users table")
            
            if not check_if_column_exists('users', 'arccos_password'):
                db.execute(text("ALTER TABLE users ADD COLUMN arccos_password VARCHAR(255)"))
                logger.info("Added arccos_password column to users table")
            
            if not check_if_column_exists('users', 'skytrak_username'):
                db.execute(text("ALTER TABLE users ADD COLUMN skytrak_username VARCHAR(255)"))
                logger.info("Added skytrak_username column to users table")
            
            if not check_if_column_exists('users', 'skytrak_password'):
                db.execute(text("ALTER TABLE users ADD COLUMN skytrak_password VARCHAR(255)"))
                logger.info("Added skytrak_password column to users table")
            
            db.commit()
            logger.info("All credential columns added successfully")
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding credential columns: {str(e)}")
            raise

def run_migrations():
    """
    Run all database migrations.
    """
    logger.info("Starting database migrations")
    
    try:
        # Add tracker credentials columns
        add_tracker_credentials_columns()
        
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")

if __name__ == "__main__":
    run_migrations()