"""
Database migrations for GolfStats application.

This module allows running database migrations to add new columns or tables
as well as configuring Supabase RLS policies for data security.
"""
import os
import sys
import logging
import re
from typing import List
from sqlalchemy import text, inspect

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.db_connection import get_db, engine, Base
from backend.database.supabase_client import get_supabase

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

def recreate_database():
    """
    Recreate the entire database schema from models.
    
    This is a more thorough approach that ensures all models are properly created.
    """
    logger.info("Recreating database schema from models")
    
    try:
        # Import all models to ensure they're registered with Base
        from backend.models import user, golf_data
        
        # Drop all tables
        Base.metadata.drop_all(engine)
        logger.info("Dropped all existing tables")
        
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Created all tables from models")
        
        return True
    except Exception as e:
        logger.error(f"Error recreating database: {str(e)}")
        return False

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

def read_sql_file(filename: str) -> str:
    """
    Read SQL file contents.
    
    Args:
        filename: Path to SQL file
        
    Returns:
        SQL file contents as string
    """
    file_path = os.path.join(project_root, 'database/migrations', filename)
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading SQL file {filename}: {str(e)}")
        return ""

def split_sql_statements(sql: str) -> List[str]:
    """
    Split SQL string into individual statements by semicolon.
    Handles SQL comments and statement boundaries correctly.
    
    Args:
        sql: SQL script containing multiple statements
        
    Returns:
        List of individual SQL statements
    """
    # Remove comments first
    sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)
    
    # Split by semicolons, but not semicolons inside quotes
    statements = []
    current_statement = ""
    in_quote = False
    quote_char = None
    
    for char in sql:
        if char in ("'", '"') and (not in_quote or quote_char == char):
            in_quote = not in_quote
            if in_quote:
                quote_char = char
            else:
                quote_char = None
        
        if char == ';' and not in_quote:
            statements.append(current_statement)
            current_statement = ""
        else:
            current_statement += char
    
    # Add the last statement if not empty
    if current_statement.strip():
        statements.append(current_statement)
    
    return statements

def setup_rpc_for_sql_execution() -> bool:
    """
    Set up an RPC function in Supabase to execute SQL statements.
    This allows executing SQL from the client securely.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase()
        
        # SQL to create the RPC function for executing SQL
        rpc_function_sql = """
        CREATE OR REPLACE FUNCTION exec_sql(sql text)
        RETURNS void
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
          EXECUTE sql;
        END;
        $$;
        """
        
        # Execute the RPC function creation directly using supabase-py's raw SQL execution
        # This requires appropriate permissions
        try:
            response = supabase.table('_rpc').select('*').execute()
            # If we get here, try to create the function
            try:
                # Use a direct REST call to execute SQL
                response = supabase.postgrest.rpc('exec_sql', {'sql': rpc_function_sql}).execute()
                logger.info("Successfully created exec_sql RPC function")
                return True
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("exec_sql RPC function already exists")
                    return True
                else:
                    logger.error(f"Error creating RPC function: {str(e)}")
                    return False
        except Exception as e:
            logger.error(f"Error verifying RPC access: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Error setting up RPC for SQL execution: {str(e)}")
        return False

def apply_rls_policies() -> bool:
    """
    Apply RLS policies for data security.
    These policies ensure users can only access their own data.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # First check if we can execute SQL via RPC
        if not setup_rpc_for_sql_execution():
            logger.warning("Could not set up SQL execution function. RLS policies may not be applied.")
            return False
            
        # Read RLS policies SQL file
        sql_content = read_sql_file('rls_policies.sql')
        if not sql_content:
            logger.error("RLS policies SQL file not found or empty")
            return False
            
        # Split into individual statements
        statements = split_sql_statements(sql_content)
        
        # Execute each statement
        supabase = get_supabase()
        success_count = 0
        total_statements = len(statements)
        
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
                
            try:
                # Try to execute the statement via RPC
                response = supabase.postgrest.rpc('exec_sql', {'sql': stmt}).execute()
                success_count += 1
                logger.info(f"Successfully executed RLS policy statement ({success_count}/{total_statements})")
            except Exception as e:
                logger.warning(f"Error executing RLS policy statement: {str(e)}")
                # Continue with the next statement rather than failing completely
        
        if success_count > 0:
            logger.info(f"Applied {success_count} of {total_statements} RLS policy statements")
            return True
        else:
            logger.error("Failed to apply any RLS policy statements")
            return False
            
    except Exception as e:
        logger.error(f"Error applying RLS policies: {str(e)}")
        return False

def run_migrations():
    """
    Run all database migrations.
    """
    logger.info("Starting database migrations")
    
    try:
        # Recreate database from models (preferred method for development)
        if recreate_database():
            logger.info("Database schema recreated from models")
        else:
            # Fall back to adding columns manually if recreation fails
            logger.warning("Database recreation failed, attempting manual column addition")
            add_tracker_credentials_columns()
        
        # Apply RLS policies
        logger.info("Applying Row Level Security (RLS) policies...")
        if apply_rls_policies():
            logger.info("RLS policies applied successfully")
        else:
            logger.warning("Failed to apply some or all RLS policies")
        
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")

if __name__ == "__main__":
    run_migrations()