"""
SkyTrak Data Scraper for GolfStats application.

This module provides functionality to scrape golf data from SkyTrak website
using Selenium to automate browser interactions.
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
    log_file=os.path.join(logs_dir, 'skytrak_scraper.log')
)

class SkyTrakScraper:
    """
    Scraper for retrieving golf data from SkyTrak website.
    """
    
    def __init__(self, user_id: int, headless: bool = True):
        """
        Initialize SkyTrakScraper with user credentials.
        
        Args:
            user_id: ID of the user in the database
            headless: Whether to run the browser in headless mode
        """
        self.user_id = user_id
        self.username = config["scrapers"]["skytrak"]["username"]
        self.password = config["scrapers"]["skytrak"]["password"]
        self.base_url = config["scrapers"]["skytrak"]["url"] or "https://app.skytrakgolf.com"
        self.headless = headless
        self.driver = None
        self.wait = None
        
        # Directory for error screenshots
        self.screenshot_dir = os.path.join(project_root, 'data', 'screenshots', 'skytrak')
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Validate credentials
        if not self.username or not self.password:
            logger.error("SkyTrak credentials not configured")
            raise ValueError("SkyTrak credentials missing in configuration")
    
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
        Log in to SkyTrak website with retry capability.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Attempting to log in to SkyTrak")
            
            # SkyTrak login URL may be at app.skytrakgolf.com/login
            self.driver.get(f"{self.base_url}/login")
            
            # Check for any CAPTCHA
            if CaptchaDetector.is_captcha_present(self.driver):
                CaptchaDetector.handle_captcha(self.driver, self.driver.current_url)
            
            # Wait for login form to load with multiple possible selectors
            username_field = safe_wait_for_element(
                self.driver, By.ID, "username", timeout=15,
                condition=EC.presence_of_element_located
            )
            
            if not username_field:
                # Try alternative selectors
                for selector in ["input[name='username']", "#user", "input[type='text']"]:
                    username_field = safe_wait_for_element(
                        self.driver, By.CSS_SELECTOR, selector, timeout=5,
                        condition=EC.presence_of_element_located
                    )
                    if username_field:
                        break
            
            if not username_field:
                # Try email field instead (some sites use email instead of username)
                username_field = safe_wait_for_element(
                    self.driver, By.CSS_SELECTOR, "input[type='email'], #email", timeout=5,
                    condition=EC.presence_of_element_located
                )
            
            if not username_field:
                logger.error("Login page did not load properly - username/email field not found")
                take_error_screenshot(self.driver, "login_form_missing", self.screenshot_dir)
                return False
                
            # Find password field - try multiple selectors
            password_field = None
            for selector in ["#password", "input[type='password']", "input[name='password']"]:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if password_field:
                        break
                except NoSuchElementException:
                    continue
                    
            if not password_field:
                logger.error("Password field not found")
                take_error_screenshot(self.driver, "password_field_missing", self.screenshot_dir)
                return False
                
            # Find login button - try multiple selectors
            login_button = None
            button_selectors = [
                "button[type='submit']", 
                "input[type='submit']",
                "button.login-button",
                ".login-button",
                "#login-button",
                "button:contains('Sign In')",
                "button:contains('Log In')"
            ]
            
            for selector in button_selectors:
                try:
                    if "contains" in selector:
                        # Use XPath for text contains
                        xpath = selector.replace("button:contains('", "//button[contains(text(), '").replace("')", "')]")
                        login_button = self.driver.find_element(By.XPATH, xpath)
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_button:
                        break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                logger.error("Login button not found")
                take_error_screenshot(self.driver, "login_button_missing", self.screenshot_dir)
                return False
            
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
            
            # Wait for dashboard elements to confirm successful login
            # SkyTrak dashboard usually has these elements
            dashboard_selectors = [
                "//div[contains(@class, 'dashboard')]",
                "//div[contains(@class, 'home')]",
                "//div[contains(@class, 'user-profile')]",
                "//div[contains(@class, 'sessions')]",
                "//a[contains(text(), 'Sessions')]",
                "//a[contains(text(), 'Practice')]",
                "//a[contains(text(), 'Data')]",
                "//h1[contains(text(), 'Dashboard')]",
                "//div[contains(@class, 'welcome')]"
            ]
            
            # Check for any successful login indicator
            dashboard_loaded = False
            for selector in dashboard_selectors:
                element = safe_wait_for_element(
                    self.driver, By.XPATH, selector,
                    timeout=5, condition=EC.presence_of_element_located
                )
                if element:
                    dashboard_loaded = True
                    logger.debug(f"Found dashboard element with selector: {selector}")
                    break
            
            if not dashboard_loaded:
                # Check for error messages
                error_msgs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'error')] | //p[contains(@class, 'error')] | //span[contains(@class, 'error-message')]")
                if error_msgs:
                    for msg in error_msgs:
                        logger.error(f"Login error message: {msg.text}")
                
                # Take screenshot of the failed login attempt
                take_error_screenshot(self.driver, "login_failed", self.screenshot_dir)
                return False
            
            logger.info("Successfully logged in to SkyTrak")
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
    
    def get_session_list(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of recent SkyTrak practice sessions.
        
        Args:
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of session information dictionaries
        """
        sessions = []
        try:
            logger.info(f"Retrieving recent SkyTrak sessions (limit={limit})")
            
            # Navigate to sessions page
            self.driver.get(f"{self.base_url}/sessions")
            
            # Wait for sessions list to load
            session_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'session-item') or contains(@class, 'practice-session')]"))
            )
            
            # Process session elements (limited to specified limit)
            for idx, element in enumerate(session_elements[:limit]):
                try:
                    # Extract session details
                    date_element = element.find_element(By.XPATH, ".//div[contains(@class, 'session-date')]")
                    name_element = element.find_element(By.XPATH, ".//div[contains(@class, 'session-name')]")
                    session_id = element.get_attribute("data-session-id")
                    
                    session = {
                        "id": session_id,
                        "date": date_element.text,
                        "name": name_element.text,
                        "url": f"{self.base_url}/sessions/{session_id}"
                    }
                    
                    sessions.append(session)
                except NoSuchElementException as e:
                    logger.warning(f"Error extracting session data: {str(e)}")
                except Exception as e:
                    logger.warning(f"Unexpected error processing session element: {str(e)}")
            
            logger.info(f"Retrieved {len(sessions)} sessions")
            return sessions
        except TimeoutException:
            logger.error("Timeout waiting for session list to load")
            return []
        except Exception as e:
            logger.error(f"Error retrieving session list: {str(e)}")
            return []
    
    def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed data for a specific SkyTrak session.
        
        Args:
            session_id: The session ID to retrieve
            
        Returns:
            Dictionary containing session data
        """
        session_data = {
            "session_id": session_id,
            "shots": []
        }
        
        try:
            logger.info(f"Retrieving details for session {session_id}")
            
            # Navigate to session details page
            self.driver.get(f"{self.base_url}/sessions/{session_id}")
            
            # Wait for session data to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'session-details')]"))
            )
            
            # Get session metadata
            try:
                session_title = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'session-title')]").text
                session_date = self.driver.find_element(By.XPATH, "//div[contains(@class, 'session-date')]").text
                
                session_data.update({
                    "title": session_title,
                    "date": session_date
                })
            except NoSuchElementException as e:
                logger.warning(f"Could not extract some session metadata: {str(e)}")
            
            # Get shot data table
            try:
                # Check if we need to navigate to a data tab
                try:
                    data_tab = self.driver.find_element(By.XPATH, "//a[contains(@class, 'data-tab')]")
                    data_tab.click()
                    time.sleep(1)  # Wait for tab content to load
                except NoSuchElementException:
                    logger.info("No data tab found, assuming we're already on the data view")
                
                # Find shot table
                shot_rows = self.driver.find_elements(By.XPATH, "//table[contains(@class, 'shots-table')]//tr[not(contains(@class, 'header'))]")
                
                for idx, shot_row in enumerate(shot_rows):
                    try:
                        # Extract cells (adjust the selectors based on actual page structure)
                        cells = shot_row.find_elements(By.TAG_NAME, "td")
                        
                        if len(cells) < 8:  # Basic validation
                            continue
                        
                        # Ensure consistent indexing by checking headers or using robust selectors
                        # This is a simplified example; real implementation would map cells to actual data points
                        club = cells[0].text if len(cells) > 0 else None
                        ball_speed = cells[1].text if len(cells) > 1 else None
                        club_speed = cells[2].text if len(cells) > 2 else None
                        smash = cells[3].text if len(cells) > 3 else None
                        launch_angle = cells[4].text if len(cells) > 4 else None
                        spin_rate = cells[5].text if len(cells) > 5 else None
                        carry = cells[6].text if len(cells) > 6 else None
                        total = cells[7].text if len(cells) > 7 else None
                        
                        # Clean and convert data
                        shot_data = {
                            "shot_number": idx + 1,
                            "club": club,
                            "ball_speed_mph": self._extract_numeric(ball_speed),
                            "club_speed_mph": self._extract_numeric(club_speed),
                            "smash_factor": self._extract_numeric(smash),
                            "launch_angle_degrees": self._extract_numeric(launch_angle),
                            "spin_rate_rpm": self._extract_numeric(spin_rate),
                            "carry_distance_yards": self._extract_numeric(carry),
                            "total_distance_yards": self._extract_numeric(total)
                        }
                        
                        session_data["shots"].append(shot_data)
                    except Exception as e:
                        logger.warning(f"Error processing shot {idx+1}: {str(e)}")
                
                logger.info(f"Retrieved {len(session_data['shots'])} shots for session {session_id}")
            except NoSuchElementException:
                logger.warning(f"No shot data table found for session {session_id}")
            except Exception as e:
                logger.error(f"Error retrieving shot data: {str(e)}")
            
            return session_data
        
        except TimeoutException:
            logger.error(f"Timeout waiting for session {session_id} data to load")
            return session_data
        except Exception as e:
            logger.error(f"Error retrieving session details: {str(e)}")
            return session_data
    
    def _extract_numeric(self, text: Optional[str]) -> Optional[float]:
        """
        Extract numeric value from text.
        
        Args:
            text: Text to extract numeric value from
            
        Returns:
            Extracted numeric value or None
        """
        if not text:
            return None
        
        try:
            # Remove non-numeric characters except decimal point and negative sign
            numeric_text = ''.join(c for c in text if c.isdigit() or c == '.' or c == '-')
            return float(numeric_text) if numeric_text else None
        except ValueError:
            return None
    
    def transform_to_golf_round(self, session_data: Dict[str, Any]) -> Tuple[GolfRound, List[GolfShot]]:
        """
        Transform SkyTrak session data to GolfStats data model.
        
        Args:
            session_data: Session data retrieved from SkyTrak
            
        Returns:
            Tuple of (GolfRound, list of GolfShot objects)
        """
        try:
            logger.info(f"Transforming SkyTrak session {session_data['session_id']} to GolfStats model")
            
            # Parse date
            try:
                # This date format might need adjustment based on actual SkyTrak format
                date_str = session_data.get("date", "")
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                logger.warning(f"Could not parse date: {session_data.get('date')}, using current time")
                date_obj = datetime.datetime.now()
            
            # Create golf round (practice session)
            golf_round = GolfRound(
                user_id=self.user_id,
                date=date_obj,
                course_name=session_data.get("title", "SkyTrak Practice Session"),
                course_location="Practice Range",  # Default for practice sessions
                source_system="skytrak",
                notes=f"SkyTrak Session ID: {session_data['session_id']}"
            )
            
            # Create default hole for shots (practice sessions don't have holes)
            golf_hole = GolfHole(
                hole_number=1,
                par=4,  # Default par for practice
                distance_yards=None
            )
            
            # Add hole to round
            golf_round.holes.append(golf_hole)
            
            # Process shots
            golf_shots = []
            for shot_data in session_data.get("shots", []):
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
                    from_location="range",  # Default for SkyTrak sessions
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
    
    def save_to_database(self, golf_round: GolfRound) -> int:
        """
        Save golf round data to database.
        
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
    
    def run(self, limit: int = 10) -> List[int]:
        """
        Run the SkyTrak scraper to extract and store data.
        
        Args:
            limit: Maximum number of sessions to process
            
        Returns:
            List of golf round IDs that were processed
        """
        round_ids = []
        
        try:
            logger.info(f"Starting SkyTrak scraper for user {self.user_id}")
            
            # Set up WebDriver
            self.setup_driver()
            
            # Login
            if not self.login():
                logger.error("Login failed, aborting")
                return round_ids
            
            # Get session list
            sessions = self.get_session_list(limit=limit)
            logger.info(f"Found {len(sessions)} sessions to process")
            
            # Process each session
            for session in sessions:
                try:
                    # Get session details
                    session_id = session["id"]
                    session_data = self.get_session_details(session_id)
                    
                    # Transform data
                    golf_round, _ = self.transform_to_golf_round(session_data)
                    
                    # Save to database
                    round_id = self.save_to_database(golf_round)
                    round_ids.append(round_id)
                    
                except Exception as e:
                    logger.error(f"Error processing session {session.get('id', 'unknown')}: {str(e)}")
            
            logger.info(f"SkyTrak scraper completed - processed {len(round_ids)} rounds")
            
        except Exception as e:
            logger.error(f"SkyTrak scraper failed: {str(e)}")
        
        finally:
            # Clean up
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
        
        return round_ids

def get_skytrak_data(user_id: int, limit: int = 10) -> List[int]:
    """
    Scrape SkyTrak data for a specific user.
    
    Args:
        user_id: The database ID of the user
        limit: Maximum number of sessions to process
        
    Returns:
        List of golf round IDs that were processed
    """
    scraper = SkyTrakScraper(user_id=user_id)
    return scraper.run(limit=limit)
