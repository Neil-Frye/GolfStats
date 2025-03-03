"""
Common utilities for GolfStats scrapers.

This module provides shared functionality used across different scraper modules,
including error handling, logging, and data persistence utilities.
"""
from typing import Dict, List, Any, Optional, Tuple, Callable
import os
import sys
import json
import time
import logging
import traceback
import functools
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException,
    ElementNotInteractableException,
    WebDriverException
)

# Set up project root path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Name of the logger
        log_file: Path to the log file (optional)
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Define formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Clear existing handlers
    logger.handlers = []
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is provided
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Set up main logger
logger = setup_logger(__name__)

# Error handling decorators
def retry(max_attempts=3, delay=2, backoff=2, exceptions=(Exception,), logger=None):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier
        exceptions: Tuple of exceptions to catch and retry
        logger: Logger to use
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or logging.getLogger(func.__module__)
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        log.error(f"Failed after {max_attempts} attempts: {str(e)}")
                        raise
                    log.warning(f"Attempt {attempt} failed: {str(e)}, retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

def log_exceptions(logger=None):
    """
    Decorator to log exceptions.
    
    Args:
        logger: Logger to use
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.error(f"Exception in {func.__name__}: {str(e)}")
                log.error(f"Traceback: {traceback.format_exc()}")
                raise
        return wrapper
    return decorator

class CaptchaDetector:
    """Utility class to detect and handle CAPTCHAs."""
    
    @staticmethod
    def is_captcha_present(driver, common_captcha_keywords=None):
        """
        Check if a CAPTCHA is present on the page.
        
        Args:
            driver: WebDriver instance
            common_captcha_keywords: List of keywords that might indicate a CAPTCHA
            
        Returns:
            Boolean indicating if a CAPTCHA was detected
        """
        if common_captcha_keywords is None:
            common_captcha_keywords = [
                "captcha", "robot", "human verification", "security check", 
                "prove you're human", "not a robot"
            ]
            
        page_source = driver.page_source.lower()
        
        # Check for common CAPTCHA indicators in the page source
        for keyword in common_captcha_keywords:
            if keyword.lower() in page_source:
                logger.warning(f"Possible CAPTCHA detected: found '{keyword}' on the page")
                return True
                
        # Check for common CAPTCHA service elements
        captcha_indicators = [
            "//iframe[contains(@src, 'recaptcha')]",
            "//iframe[contains(@src, 'hcaptcha')]",
            "//iframe[contains(@src, 'arkoselabs')]",
            "//div[contains(@class, 'captcha')]",
            "//div[contains(@class, 'g-recaptcha')]",
            "//div[contains(@id, 'captcha')]"
        ]
        
        for xpath in captcha_indicators:
            try:
                elements = driver.find_elements_by_xpath(xpath)
                if elements:
                    logger.warning(f"CAPTCHA element detected with selector: {xpath}")
                    return True
            except Exception:
                pass
                
        return False
    
    @staticmethod
    def handle_captcha(driver, url):
        """
        Handle a detected CAPTCHA by logging and taking a screenshot.
        
        Args:
            driver: WebDriver instance
            url: URL where the CAPTCHA was detected
            
        Returns:
            None
        """
        logger.error(f"CAPTCHA detected at URL: {url}")
        
        # Take a screenshot for manual inspection
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = ensure_data_directory('./data/captcha_screenshots')
        screenshot_path = os.path.join(screenshot_dir, f"captcha_{timestamp}.png")
        
        try:
            driver.save_screenshot(screenshot_path)
            logger.info(f"CAPTCHA screenshot saved to: {screenshot_path}")
        except Exception as e:
            logger.error(f"Failed to save CAPTCHA screenshot: {str(e)}")
            
        # You can add additional CAPTCHA handling logic here
        
        raise Exception("CAPTCHA detected, manual intervention required")

def safe_wait_for_element(driver, by, selector, timeout=10, condition=EC.presence_of_element_located):
    """
    Safely wait for an element to be present, with timeout handling.
    
    Args:
        driver: WebDriver instance
        by: Selenium By locator
        selector: Element selector
        timeout: How long to wait for the element
        condition: Expected condition to wait for
        
    Returns:
        The element if found, None otherwise
    """
    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(condition((by, selector)))
        return element
    except TimeoutException:
        logger.warning(f"Timeout waiting for element: {selector}")
        return None
    except Exception as e:
        logger.warning(f"Error waiting for element {selector}: {str(e)}")
        return None

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
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data saved to: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {str(e)}")
        raise

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

def take_error_screenshot(driver, error_type, directory="./data/error_screenshots"):
    """
    Take a screenshot when an error occurs.
    
    Args:
        driver: WebDriver instance
        error_type: Type of error (for filename)
        directory: Directory to save the screenshot
        
    Returns:
        Path to the screenshot or None if failed
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = ensure_data_directory(directory)
        filename = f"{error_type}_{timestamp}.png"
        screenshot_path = os.path.join(screenshot_dir, filename)
        
        driver.save_screenshot(screenshot_path)
        logger.info(f"Error screenshot saved to: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        logger.error(f"Failed to save error screenshot: {str(e)}")
        return None