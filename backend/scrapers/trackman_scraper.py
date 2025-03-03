"""
Trackman Data Scraper for GolfStats application.

This module provides functionality to scrape golf data from Trackman website
using Selenium to automate browser interactions with robust error handling.
"""
import os
import sys
import time
import datetime
import json
from typing import Dict, List, Any, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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
from webdriver_manager.chrome import ChromeDriverManager

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.config import config
from backend.database.db_connection import get_db
from backend.models.golf_data import GolfRound, GolfHole, GolfShot, RoundStats
from backend.scrapers.common import (
    setup_logger, retry, log_exceptions, CaptchaDetector,
    safe_wait_for_element, take_error_screenshot, 
    save_json_data, generate_timestamp_filename
)

# Set up logger
logs_dir = os.path.join(project_root, 'logs')
os.makedirs(logs_dir, exist_ok=True)
logger = setup_logger(
    __name__, 
    log_file=os.path.join(logs_dir, 'trackman_scraper.log')
)

class TrackmanScraper:
    """
    Scraper for retrieving golf data from Trackman website with enhanced error handling.
    """
    
    def __init__(self, user_id: int, headless: bool = True):
        """
        Initialize TrackmanScraper with user credentials.
        
        Args:
            user_id: ID of the user in the database
            headless: Whether to run the browser in headless mode
        """
        self.user_id = user_id
        self.username = config["scrapers"]["trackman"]["username"]
        self.password = config["scrapers"]["trackman"]["password"]
        self.base_url = config["scrapers"]["trackman"]["url"]
        self.headless = headless
        self.driver = None
        self.wait = None
        self.session_data = {}
        
        # Directory for error screenshots
        self.screenshot_dir = os.path.join(project_root, 'data', 'screenshots', 'trackman')
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Validate credentials
        if not self.username or not self.password:
            logger.error("Trackman credentials not configured")
            raise ValueError("Trackman credentials missing in configuration")
    
    @log_exceptions()
    def setup_driver(self) -> None:
        """
        Set up the Selenium WebDriver with appropriate options.
        """
        try:
            logger.info("Setting up Chrome WebDriver")
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Set user agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")
            
            # Disable automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set up driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set a reasonable page load timeout
            self.driver.set_page_load_timeout(30)
            
            # Configure wait timeouts
            self.wait = WebDriverWait(self.driver, 20)  # 20 seconds timeout
            
            logger.info("Chrome WebDriver setup complete")
        except Exception as e:
            logger.error(f"Failed to set up WebDriver: {str(e)}")
            raise
    
    @retry(max_attempts=3, delay=2, backoff=2, 
           exceptions=(TimeoutException, ElementClickInterceptedException))
    @log_exceptions()
    def login(self) -> bool:
        """
        Log in to Trackman website with retry capability.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Attempting to log in to Trackman")
            
            # Navigate to login page
            self.driver.get(f"{self.base_url}/login")
            
            # Check for any CAPTCHA
            if CaptchaDetector.is_captcha_present(self.driver):
                CaptchaDetector.handle_captcha(self.driver, self.driver.current_url)
            
            # Wait for login form to load
            username_field = safe_wait_for_element(
                self.driver, By.ID, "username", timeout=15,
                condition=EC.presence_of_element_located
            )
            
            if not username_field:
                logger.error("Login page did not load properly - username field not found")
                take_error_screenshot(self.driver, "login_form_missing", self.screenshot_dir)
                return False
                
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Enter credentials
            username_field.clear()
            username_field.send_keys(self.username)
            
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login with explicit wait
            try:
                login_button.click()
            except ElementClickInterceptedException:
                # Try JavaScript click if normal click is intercepted
                logger.warning("Login button click intercepted, trying JavaScript click")
                self.driver.execute_script("arguments[0].click();", login_button)
            
            # Wait for dashboard to load (checking for a common element on dashboard)
            dashboard_loaded = safe_wait_for_element(
                self.driver, By.XPATH, 
                "//div[contains(@class, 'dashboard') or contains(@class, 'home')]",
                timeout=20, condition=EC.presence_of_element_located
            )
            
            if not dashboard_loaded:
                # Check for error messages
                error_msgs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'error-message') or contains(@class, 'alert-danger')]")
                if error_msgs:
                    for msg in error_msgs:
                        logger.error(f"Login error message: {msg.text}")
                
                # Take screenshot of the failed login attempt
                take_error_screenshot(self.driver, "login_failed", self.screenshot_dir)
                return False
            
            logger.info("Successfully logged in to Trackman")
            return True
            
        except TimeoutException as e:
            logger.error(f"Timeout during login: {str(e)}")
            take_error_screenshot(self.driver, "login_timeout", self.screenshot_dir)
            raise  # Will be caught by retry decorator
            
        except NoSuchElementException as e:
            logger.error(f"Element not found during login: {str(e)}")
            take_error_screenshot(self.driver, "login_element_missing", self.screenshot_dir)
            return False
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            take_error_screenshot(self.driver, "login_error", self.screenshot_dir)
            return False
    
    @retry(max_attempts=2, delay=3, 
           exceptions=(TimeoutException, StaleElementReferenceException))
    @log_exceptions()
    def get_session_list(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get list of recent Trackman sessions with retry capability.
        
        Args:
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of session information dictionaries
        """
        sessions = []
        try:
            logger.info(f"Retrieving recent Trackman sessions (limit={limit})")
            
            # Navigate to sessions page
            self.driver.get(f"{self.base_url}/sessions")
            
            # Check for CAPTCHA
            if CaptchaDetector.is_captcha_present(self.driver):
                CaptchaDetector.handle_captcha(self.driver, self.driver.current_url)
            
            # Wait for sessions list to load with safe wait
            session_container = safe_wait_for_element(
                self.driver, By.XPATH, 
                "//div[contains(@class, 'sessions-container') or contains(@class, 'session-list')]",
                timeout=15, condition=EC.presence_of_element_located
            )
            
            if not session_container:
                logger.warning("Session list container not found, attempting to proceed anyway")
            
            # Add a short pause to let the sessions load fully
            time.sleep(2)
            
            # Get session elements, using try/except to be robust against HTML changes
            session_elements = None
            for xpath in [
                "//div[contains(@class, 'session-item')]",
                "//div[contains(@class, 'session-card')]",
                "//div[contains(@class, 'session-row')]",
                "//tr[contains(@class, 'session')]"
            ]:
                try:
                    session_elements = self.driver.find_elements(By.XPATH, xpath)
                    if session_elements:
                        logger.info(f"Found {len(session_elements)} sessions using selector: {xpath}")
                        break
                except Exception:
                    continue
            
            if not session_elements:
                logger.error("Could not find any session elements on the page")
                take_error_screenshot(self.driver, "no_sessions_found", self.screenshot_dir)
                
                # Save the page source for analysis
                page_source_path = os.path.join(self.screenshot_dir, f"sessions_page_source_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                with open(page_source_path, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.info(f"Saved page source to {page_source_path}")
                
                return []
            
            # Process session elements (limited to specified limit)
            for idx, element in enumerate(session_elements[:limit]):
                try:
                    # Different sites might have different structures - try multiple XPaths
                    session_info = {}
                    
                    # Try to extract session ID
                    session_id = None
                    for attr in ['data-session-id', 'id', 'data-id']:
                        try:
                            session_id = element.get_attribute(attr)
                            if session_id and not session_id.isspace():
                                break
                        except Exception:
                            pass
                    
                    if not session_id:
                        # Try to extract from URL in an anchor tag
                        try:
                            anchor = element.find_element(By.TAG_NAME, "a")
                            href = anchor.get_attribute("href")
                            if href and '/sessions/' in href:
                                session_id = href.split('/sessions/')[1].split('/')[0]
                        except Exception:
                            pass
                    
                    if not session_id:
                        logger.warning(f"Could not extract session ID for element {idx+1}")
                        continue
                    
                    session_info["id"] = session_id
                    session_info["url"] = f"{self.base_url}/sessions/{session_id}"
                    
                    # Try to extract date using multiple XPaths
                    date_text = None
                    for date_xpath in [
                        ".//div[contains(@class, 'session-date')]",
                        ".//span[contains(@class, 'date')]",
                        ".//div[contains(text(), '/') or contains(text(), '-')]",  # Common date format indicators
                        ".//time"
                    ]:
                        try:
                            date_elements = element.find_elements(By.XPATH, date_xpath)
                            if date_elements:
                                date_text = date_elements[0].text
                                break
                        except Exception:
                            pass
                    
                    session_info["date"] = date_text or "Unknown date"
                    
                    # Try to extract session name using multiple XPaths
                    name_text = None
                    for name_xpath in [
                        ".//div[contains(@class, 'session-name')]",
                        ".//div[contains(@class, 'title')]",
                        ".//h2",
                        ".//h3",
                        ".//div[contains(@class, 'session-title')]"
                    ]:
                        try:
                            name_elements = element.find_elements(By.XPATH, name_xpath)
                            if name_elements:
                                name_text = name_elements[0].text
                                break
                        except Exception:
                            pass
                    
                    session_info["name"] = name_text or f"Session {session_id}"
                    
                    sessions.append(session_info)
                    logger.debug(f"Extracted session: {session_info}")
                    
                except NoSuchElementException as e:
                    logger.warning(f"Error extracting data for session {idx+1}: {str(e)}")
                    continue
                except Exception as e:
                    logger.warning(f"Unexpected error processing session {idx+1}: {str(e)}")
                    continue
            
            if not sessions:
                logger.warning("No sessions could be extracted from the page")
                take_error_screenshot(self.driver, "sessions_extraction_failed", self.screenshot_dir)
            else:
                logger.info(f"Successfully extracted {len(sessions)} sessions")
                
                # Save sessions to JSON for debugging/recovery
                save_json_data(
                    sessions,
                    generate_timestamp_filename("trackman_sessions", "json"),
                    os.path.join(project_root, 'data', 'trackman')
                )
            
            return sessions
            
        except TimeoutException as e:
            logger.error(f"Timeout waiting for session list to load: {str(e)}")
            take_error_screenshot(self.driver, "sessions_list_timeout", self.screenshot_dir)
            raise  # Will be caught by retry decorator
            
        except Exception as e:
            logger.error(f"Error retrieving session list: {str(e)}")
            take_error_screenshot(self.driver, "sessions_list_error", self.screenshot_dir)
            return []
    
    @retry(max_attempts=2, delay=3, 
           exceptions=(TimeoutException, StaleElementReferenceException))
    @log_exceptions()
    def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed data for a specific Trackman session with retry capability.
        
        Args:
            session_id: The session ID to retrieve
            
        Returns:
            Dictionary containing session data
        """
        session_data = {"session_id": session_id, "shots": []}
        
        try:
            logger.info(f"Retrieving details for session {session_id}")
            
            # Navigate to session page
            self.driver.get(f"{self.base_url}/sessions/{session_id}")
            
            # Check for CAPTCHA
            if CaptchaDetector.is_captcha_present(self.driver):
                CaptchaDetector.handle_captcha(self.driver, self.driver.current_url)
            
            # Wait for session data to load
            session_details = safe_wait_for_element(
                self.driver, By.XPATH, 
                "//div[contains(@class, 'session-details')]",
                timeout=15, condition=EC.presence_of_element_located
            )
            
            if not session_details:
                logger.warning(f"Session details container not found for session {session_id}")
                take_error_screenshot(self.driver, f"session_{session_id}_not_found", self.screenshot_dir)
            
            # Get session metadata
            try:
                # Try multiple selectors for robustness
                session_title = None
                for title_xpath in [
                    "//h1[contains(@class, 'session-title')]",
                    "//h2[contains(@class, 'session-title')]",
                    "//div[contains(@class, 'session-title')]",
                    "//h1", "//h2"
                ]:
                    try:
                        elements = self.driver.find_elements(By.XPATH, title_xpath)
                        if elements:
                            session_title = elements[0].text
                            break
                    except Exception:
                        pass
                
                # Try multiple selectors for session date
                session_date = None
                for date_xpath in [
                    "//div[contains(@class, 'session-date')]",
                    "//span[contains(@class, 'date')]",
                    "//div[contains(text(), '/') or contains(text(), '-')]",
                    "//time"
                ]:
                    try:
                        elements = self.driver.find_elements(By.XPATH, date_xpath)
                        if elements:
                            session_date = elements[0].text
                            break
                    except Exception:
                        pass
                
                # Try multiple selectors for location
                location = None
                for location_xpath in [
                    "//div[contains(@class, 'session-location')]",
                    "//div[contains(@class, 'location')]",
                    "//span[contains(@class, 'location')]"
                ]:
                    try:
                        elements = self.driver.find_elements(By.XPATH, location_xpath)
                        if elements:
                            location = elements[0].text
                            break
                    except Exception:
                        pass
                
                session_data.update({
                    "title": session_title or f"Session {session_id}",
                    "date": session_date or datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "location": location or "Unknown location"
                })
                
                logger.info(f"Session metadata: Title='{session_data['title']}', Date='{session_data['date']}'")
                
            except Exception as e:
                logger.warning(f"Error extracting session metadata: {str(e)}")
                take_error_screenshot(self.driver, f"session_{session_id}_metadata_error", self.screenshot_dir)
            
            # Get shot data
            try:
                # Try multiple table selectors for shots
                shot_rows = None
                for shots_xpath in [
                    "//table[contains(@class, 'shots-table')]//tr[contains(@class, 'shot-row')]",
                    "//table[contains(@class, 'shots')]//tr",
                    "//div[contains(@class, 'shots-container')]//div[contains(@class, 'shot')]"
                ]:
                    try:
                        elements = self.driver.find_elements(By.XPATH, shots_xpath)
                        if elements and len(elements) > 0:
                            shot_rows = elements
                            logger.info(f"Found {len(elements)} shots using selector: {shots_xpath}")
                            break
                    except Exception:
                        pass
                
                if not shot_rows:
                    logger.warning(f"No shot data found for session {session_id}")
                    shot_rows = []
                
                for idx, shot_row in enumerate(shot_rows):
                    try:
                        shot_data = {
                            "shot_number": idx + 1,
                        }
                        
                        # Try to extract shot data with multiple XPath patterns
                        # Extract club
                        club = None
                        for club_xpath in [".//td[contains(@class, 'club')]", ".//div[contains(@class, 'club')]"]:
                            try:
                                elements = shot_row.find_elements(By.XPATH, club_xpath)
                                if elements:
                                    club = elements[0].text
                                    break
                            except Exception:
                                pass
                        
                        # Extract ball speed
                        ball_speed = None
                        for speed_xpath in [".//td[contains(@class, 'ball-speed')]", ".//div[contains(@class, 'ball-speed')]"]:
                            try:
                                elements = shot_row.find_elements(By.XPATH, speed_xpath)
                                if elements:
                                    ball_speed = elements[0].text
                                    break
                            except Exception:
                                pass
                        
                        # Similarly for other metrics
                        club_speed = None
                        for xpath in [".//td[contains(@class, 'club-speed')]", ".//div[contains(@class, 'club-speed')]"]:
                            try:
                                elements = shot_row.find_elements(By.XPATH, xpath)
                                if elements:
                                    club_speed = elements[0].text
                                    break
                            except Exception:
                                pass
                        
                        smash = None
                        for xpath in [".//td[contains(@class, 'smash')]", ".//div[contains(@class, 'smash')]"]:
                            try:
                                elements = shot_row.find_elements(By.XPATH, xpath)
                                if elements:
                                    smash = elements[0].text
                                    break
                            except Exception:
                                pass
                        
                        launch_angle = None
                        for xpath in [".//td[contains(@class, 'launch-angle')]", ".//div[contains(@class, 'launch')]"]:
                            try:
                                elements = shot_row.find_elements(By.XPATH, xpath)
                                if elements:
                                    launch_angle = elements[0].text
                                    break
                            except Exception:
                                pass
                        
                        spin_rate = None
                        for xpath in [".//td[contains(@class, 'spin-rate')]", ".//div[contains(@class, 'spin')]"]:
                            try:
                                elements = shot_row.find_elements(By.XPATH, xpath)
                                if elements:
                                    spin_rate = elements[0].text
                                    break
                            except Exception:
                                pass
                        
                        carry = None
                        for xpath in [".//td[contains(@class, 'carry')]", ".//div[contains(@class, 'carry')]"]:
                            try:
                                elements = shot_row.find_elements(By.XPATH, xpath)
                                if elements:
                                    carry = elements[0].text
                                    break
                            except Exception:
                                pass
                        
                        total = None
                        for xpath in [".//td[contains(@class, 'total')]", ".//div[contains(@class, 'total')]"]:
                            try:
                                elements = shot_row.find_elements(By.XPATH, xpath)
                                if elements:
                                    total = elements[0].text
                                    break
                            except Exception:
                                pass
                        
                        # Clean data and convert to proper types
                        shot_data.update({
                            "club": club.strip() if club else None,
                            "ball_speed_mph": self._safe_parse_float(ball_speed, 'mph') if ball_speed else None,
                            "club_speed_mph": self._safe_parse_float(club_speed, 'mph') if club_speed else None,
                            "smash_factor": self._safe_parse_float(smash) if smash else None,
                            "launch_angle_degrees": self._safe_parse_float(launch_angle, '°') if launch_angle else None,
                            "spin_rate_rpm": self._safe_parse_float(spin_rate, 'rpm') if spin_rate else None,
                            "carry_distance_yards": self._safe_parse_float(carry, 'yds') if carry else None,
                            "total_distance_yards": self._safe_parse_float(total, 'yds') if total else None
                        })
                        
                        session_data["shots"].append(shot_data)
                        logger.debug(f"Processed shot {idx+1}: club={shot_data['club']}, carry={shot_data['carry_distance_yards']}")
                        
                    except Exception as e:
                        logger.warning(f"Error processing shot {idx+1}: {str(e)}")
                
                logger.info(f"Retrieved {len(session_data['shots'])} shots for session {session_id}")
                
                # Save session data to JSON for debugging/recovery
                save_json_data(
                    session_data,
                    f"trackman_session_{session_id}.json",
                    os.path.join(project_root, 'data', 'trackman')
                )
                
            except Exception as e:
                logger.error(f"Error processing shots for session {session_id}: {str(e)}")
                take_error_screenshot(self.driver, f"session_{session_id}_shots_error", self.screenshot_dir)
            
            return session_data
        
        except TimeoutException as e:
            logger.error(f"Timeout waiting for session {session_id} data to load: {str(e)}")
            take_error_screenshot(self.driver, f"session_{session_id}_timeout", self.screenshot_dir)
            raise  # Will be caught by retry decorator
            
        except Exception as e:
            logger.error(f"Error retrieving session details for {session_id}: {str(e)}")
            take_error_screenshot(self.driver, f"session_{session_id}_error", self.screenshot_dir)
            return session_data
    
    def _safe_parse_float(self, value_str, remove_text=None):
        """
        Safely parse a float value from a string, optionally removing text.
        
        Args:
            value_str: String value to parse
            remove_text: Text to remove from the string before parsing
            
        Returns:
            Float value or None if parsing fails
        """
        if not value_str:
            return None
            
        try:
            # Clean the string
            cleaned = value_str.strip()
            if remove_text:
                cleaned = cleaned.replace(remove_text, '').strip()
                
            # Handle comma as decimal separator
            cleaned = cleaned.replace(',', '.')
            
            # Parse the float
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    @log_exceptions()
    def transform_to_golf_round(self, session_data: Dict[str, Any]) -> Tuple[GolfRound, List[GolfShot]]:
        """
        Transform Trackman session data to GolfStats data model.
        
        Args:
            session_data: Session data retrieved from Trackman
            
        Returns:
            Tuple of (GolfRound, list of GolfShot objects)
        """
        try:
            logger.info(f"Transforming Trackman session {session_data['session_id']} to GolfStats model")
            
            # Parse date with multiple format attempts
            date_obj = None
            date_str = session_data.get("date", "")
            if date_str:
                # Try multiple date formats
                date_formats = [
                    "%Y-%m-%d %H:%M",
                    "%Y/%m/%d %H:%M",
                    "%m/%d/%Y %H:%M",
                    "%d/%m/%Y %H:%M",
                    "%Y-%m-%d",
                    "%m/%d/%Y",
                    "%d/%m/%Y",
                    "%b %d, %Y",
                    "%d %b %Y"
                ]
                
                for date_format in date_formats:
                    try:
                        date_obj = datetime.datetime.strptime(date_str, date_format)
                        logger.debug(f"Successfully parsed date '{date_str}' with format '{date_format}'")
                        break
                    except ValueError:
                        continue
            
            if not date_obj:
                logger.warning(f"Could not parse date: '{date_str}', using current time")
                date_obj = datetime.datetime.now()
            
            # Create golf round
            golf_round = GolfRound(
                user_id=self.user_id,
                date=date_obj,
                course_name=session_data.get("title", "Trackman Session"),
                course_location=session_data.get("location", ""),
                source_system="trackman",
                notes=f"Trackman Session ID: {session_data['session_id']}"
            )
            
            # Create default hole for shot data
            # (Trackman range sessions don't have holes, so we create a virtual one)
            golf_hole = GolfHole(
                hole_number=1,
                par=4,  # Default par
                distance_yards=None
            )
            
            # Add hole to round
            golf_round.holes.append(golf_hole)
            
            # Process shots
            golf_shots = []
            for shot_data in session_data.get("shots", []):
                # Skip shots with no data
                if not shot_data.get("carry_distance_yards") and not shot_data.get("ball_speed_mph"):
                    logger.debug(f"Skipping shot with no data: {shot_data}")
                    continue
                    
                golf_shot = GolfShot(
                    shot_number=shot_data.get("shot_number", 1),
                    club=shot_data.get("club"),
                    ball_speed_mph=shot_data.get("ball_speed_mph"),
                    club_speed_mph=shot_data.get("club_speed_mph"),
                    smash_factor=shot_data.get("smash_factor"),
                    launch_angle_degrees=shot_data.get("launch_angle_degrees"),
                    spin_rate_rpm=shot_data.get("spin_rate_rpm"),
                    carry_distance_yards=shot_data.get("carry_distance_yards"),
                    total_distance_yards=shot_data.get("total_distance_yards"),
                    from_location="range",  # Default for Trackman sessions
                    to_location="range"
                )
                
                # Add shot to hole
                golf_hole.shots.append(golf_shot)
                golf_shots.append(golf_shot)
            
            logger.info(f"Transformed {len(golf_shots)} shots")
            return golf_round, golf_shots
        
        except Exception as e:
            logger.error(f"Error transforming session data: {str(e)}")
            raise
    
    @retry(max_attempts=2, delay=2, 
           exceptions=(Exception,))
    @log_exceptions()
    def save_to_database(self, golf_round: GolfRound) -> int:
        """
        Save golf round data to database with retry capability.
        
        Args:
            golf_round: The golf round object to save
            
        Returns:
            The ID of the saved golf round
        """
        try:
            logger.info("Saving golf round to database")
            
            with get_db() as db:
                # Check if this round already exists (based on date and source_system ID)
                existing_round = db.query(GolfRound).filter(
                    GolfRound.user_id == self.user_id,
                    GolfRound.date == golf_round.date,
                    GolfRound.notes.like(f"%{golf_round.notes}%")
                ).first()
                
                if existing_round:
                    logger.info(f"Round already exists in database (ID: {existing_round.id})")
                    return existing_round.id
                
                # Add new round to database
                db.add(golf_round)
                db.commit()
                db.refresh(golf_round)
                
                logger.info(f"Saved golf round to database (ID: {golf_round.id})")
                return golf_round.id
        
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            raise
    
    @log_exceptions()
    def run(self, limit: int = 10) -> List[int]:
        """
        Run the Trackman scraper to extract and store data.
        
        Args:
            limit: Maximum number of sessions to process
            
        Returns:
            List of golf round IDs that were processed
        """
        round_ids = []
        start_time = datetime.datetime.now()
        logger.info(f"Starting Trackman scraper for user {self.user_id} at {start_time}")
        
        try:
            # Set up WebDriver
            self.setup_driver()
            
            # Login
            login_success = self.login()
            if not login_success:
                logger.error("Login failed, aborting")
                return round_ids
            
            # Get session list
            sessions = self.get_session_list(limit=limit)
            session_count = len(sessions)
            logger.info(f"Found {session_count} sessions to process")
            
            # Process each session
            for i, session in enumerate(sessions):
                try:
                    session_id = session.get("id")
                    if not session_id:
                        logger.warning(f"Session {i+1}/{session_count} has no ID, skipping")
                        continue
                        
                    logger.info(f"Processing session {i+1}/{session_count}: {session_id}")
                    
                    # Get session details
                    session_data = self.get_session_details(session_id)
                    
                    # Check if we got any shots
                    if not session_data.get("shots"):
                        logger.warning(f"No shots found for session {session_id}, skipping")
                        continue
                    
                    # Transform data
                    golf_round, shots = self.transform_to_golf_round(session_data)
                    
                    # Skip if no shots were transformed
                    if not shots:
                        logger.warning(f"No valid shots transformed for session {session_id}, skipping")
                        continue
                    
                    # Save to database
                    round_id = self.save_to_database(golf_round)
                    round_ids.append(round_id)
                    logger.info(f"Saved round {round_id} with {len(shots)} shots")
                    
                except Exception as e:
                    logger.error(f"Error processing session {session.get('id', 'unknown')}: {str(e)}")
            
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Trackman scraper completed in {duration:.1f} seconds - processed {len(round_ids)}/{session_count} rounds")
            
        except Exception as e:
            logger.error(f"Trackman scraper failed: {str(e)}")
        
        finally:
            # Clean up
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("WebDriver closed")
                except Exception as e:
                    logger.warning(f"Error closing WebDriver: {str(e)}")
        
        return round_ids

@log_exceptions()
def get_trackman_data(user_id: int, limit: int = 10) -> List[int]:
    """
    Scrape Trackman data for a specific user.
    
    Args:
        user_id: The database ID of the user
        limit: Maximum number of sessions to process
        
    Returns:
        List of golf round IDs that were processed
    """
    logger.info(f"Starting Trackman data retrieval for user {user_id}")
    scraper = TrackmanScraper(user_id=user_id)
    results = scraper.run(limit=limit)
    logger.info(f"Completed Trackman data retrieval: {len(results)} rounds processed")
    return results
