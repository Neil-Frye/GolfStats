"""
Common utilities for GolfStats scrapers.

This module provides shared functionality used across different scraper modules.
"""
from typing import Dict, List, Any, Optional
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_data_directory(directory: str = "./data") -> str:
    """
    Ensure that the data directory exists.
    
    Args:
        directory: Path to the data directory
        
    Returns:
        The absolute path to the data directory
    """
    abs_path = os.path.abspath(directory)
    os.makedirs(abs_path, exist_ok=True)
    logger.info(f"Ensured data directory exists at: {abs_path}")
    return abs_path

def save_json_data(data: Any, filename: str, directory: str = "./data") -> str:
    """
    Save data as JSON to the specified file.
    
    Args:
        data: Data to save (must be JSON serializable)
        filename: Name of the file to save
        directory: Directory to save the file in
        
    Returns:
        The absolute path to the saved file
    """
    dir_path = ensure_data_directory(directory)
    file_path = os.path.join(dir_path, filename)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Data saved to: {file_path}")
    return file_path

def load_json_data(filename: str, directory: str = "./data") -> Optional[Any]:
    """
    Load data from a JSON file.
    
    Args:
        filename: Name of the file to load
        directory: Directory containing the file
        
    Returns:
        The loaded data, or None if the file doesn't exist
    """
    file_path = os.path.join(os.path.abspath(directory), filename)
    
    if not os.path.exists(file_path):
        logger.warning(f"File does not exist: {file_path}")
        return None
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Data loaded from: {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {str(e)}")
        return None

def generate_timestamp_filename(prefix: str, extension: str = "json") -> str:
    """
    Generate a filename with a timestamp.
    
    Args:
        prefix: Prefix for the filename
        extension: File extension (without dot)
        
    Returns:
        A filename with the format: {prefix}_{timestamp}.{extension}
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"