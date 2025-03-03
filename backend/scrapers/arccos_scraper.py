"""
Arccos Golf Data Scraper for GolfStats application.

This module provides functionality to scrape golf data from Arccos Golf website
using Selenium to automate browser interactions.
"""
import os
import sys
import time
import datetime
import json
import re
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
    log_file=os.path.join(logs_dir, 'arccos_scraper.log')
)

class ArccosScraper:
    """
    Scraper for retrieving golf data from Arccos Golf website.
    """
    
    def __init__(self, user_id: int, headless: bool = True):
        """
        Initialize ArccosScraper with user credentials.
        
        Args:
            user_id: ID of the user in the database
            headless: Whether to run the browser in headless mode
        """
        self.user_id = user_id
        self.email = config["scrapers"]["arccos"]["email"]
        self.password = config["scrapers"]["arccos"]["password"]
        self.base_url = config["scrapers"]["arccos"]["url"]
        self.headless = headless
        self.driver = None
        self.wait = None
        
        # Directory for error screenshots
        self.screenshot_dir = os.path.join(project_root, 'data', 'screenshots', 'arccos')
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Validate credentials
        if not self.email or not self.password:
            logger.error("Arccos credentials not configured")
            raise ValueError("Arccos credentials missing in configuration")
    
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
        Log in to Arccos Golf website with retry capability.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("Attempting to log in to Arccos Golf")
            
            # Arccos login URL is actually at dashboard.arccosgolf.com/login
            self.driver.get("https://dashboard.arccosgolf.com/login")
            
            # Check for any CAPTCHA
            if CaptchaDetector.is_captcha_present(self.driver):
                CaptchaDetector.handle_captcha(self.driver, self.driver.current_url)
            
            # Wait for login form to load - Arccos uses both email and username fields
            email_field = safe_wait_for_element(
                self.driver, By.CSS_SELECTOR, "input[type='email']", timeout=15,
                condition=EC.presence_of_element_located
            )
            
            if not email_field:
                # Try alternate selector
                email_field = safe_wait_for_element(
                    self.driver, By.ID, "email", timeout=5,
                    condition=EC.presence_of_element_located
                )
            
            if not email_field:
                logger.error("Login page did not load properly - email field not found")
                take_error_screenshot(self.driver, "login_form_missing", self.screenshot_dir)
                return False
                
            # Find password field - try multiple selectors
            password_field = None
            for selector in ["input[type='password']", "#password", "input[name='password']"]:
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
                "button.login-button",
                "button:contains('Sign In')",
                "button:contains('Log In')",
                "input[type='submit']"
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
            email_field.clear()
            email_field.send_keys(self.email)
            
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
            # Arccos dashboard usually has these elements
            dashboard_selectors = [
                "//div[contains(@class, 'dashboard')]",
                "//div[contains(@class, 'home')]",
                "//a[contains(text(), 'Dashboard')]",
                "//h1[contains(text(), 'Dashboard')]",
                "//div[contains(@class, 'user-profile')]",
                "//div[contains(@class, 'rounds')]",
                "//a[contains(text(), 'Rounds')]"
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
            
            logger.info("Successfully logged in to Arccos Golf")
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
    def get_round_list(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of recent Arccos Golf rounds with retry capability.
        
        Args:
            limit: Maximum number of rounds to retrieve
            
        Returns:
            List of round information dictionaries
        """
        rounds = []
        try:
            logger.info(f"Retrieving recent Arccos Golf rounds (limit={limit})")
            
            # Navigate to rounds page (real Arccos URL)
            self.driver.get("https://dashboard.arccosgolf.com/rounds")
            
            # Check for CAPTCHA
            if CaptchaDetector.is_captcha_present(self.driver):
                CaptchaDetector.handle_captcha(self.driver, self.driver.current_url)
            
            # Wait for rounds list to load safely
            # Look for a container that holds the rounds
            rounds_container = safe_wait_for_element(
                self.driver, By.XPATH, 
                "//div[contains(@class, 'rounds-list') or contains(@class, 'rounds-container')]",
                timeout=15, condition=EC.presence_of_element_located
            )
            
            if not rounds_container:
                logger.warning("Rounds container not found, looking for individual round elements")
            
            # Try several different selectors for round cards
            round_elements = None
            round_selectors = [
                "//div[contains(@class, 'round-card')]",
                "//div[contains(@class, 'round-item')]",
                "//div[contains(@class, 'round-container')]",
                "//div[contains(@class, 'round-entry')]",
                "//div[contains(@class, 'round')][@data-id]",
                "//article[contains(@class, 'round')]"
            ]
            
            for selector in round_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements and len(elements) > 0:
                        round_elements = elements
                        logger.info(f"Found {len(elements)} rounds using selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not round_elements:
                logger.error("Could not find any round elements on the page")
                take_error_screenshot(self.driver, "no_rounds_found", self.screenshot_dir)
                return []
            
            # Add a short pause to ensure all elements are properly loaded
            time.sleep(1)
            
            # Process round elements (limited to specified limit)
            for idx, element in enumerate(round_elements[:limit]):
                try:
                    # Extract round details (try multiple possible selectors)
                    round_info = {}
                    
                    # Try to extract round ID
                    round_id = None
                    for attr in ['data-round-id', 'data-id', 'id']:
                        try:
                            round_id = element.get_attribute(attr)
                            if round_id and not round_id.isspace():
                                break
                        except Exception:
                            pass
                    
                    if not round_id:
                        # Try to extract from URL in an anchor tag
                        try:
                            anchor = element.find_element(By.TAG_NAME, "a")
                            href = anchor.get_attribute("href")
                            if href and '/rounds/' in href:
                                round_id = href.split('/rounds/')[1].split('/')[0].split('?')[0]
                        except Exception:
                            pass
                    
                    if not round_id:
                        logger.warning(f"Could not extract round ID for element {idx+1}")
                        continue
                    
                    round_info["id"] = round_id
                    round_info["url"] = f"https://dashboard.arccosgolf.com/rounds/{round_id}"
                    
                    # Try to extract date using multiple selectors
                    date_text = None
                    date_selectors = [
                        ".//div[contains(@class, 'round-date')]",
                        ".//span[contains(@class, 'date')]",
                        ".//time",
                        ".//div[contains(@class, 'date')]",
                        ".//span[contains(text(), '/') or contains(text(), '-')]" # Common date format indicators
                    ]
                    
                    for date_selector in date_selectors:
                        try:
                            elements = element.find_elements(By.XPATH, date_selector)
                            if elements:
                                date_text = elements[0].text
                                break
                        except Exception:
                            pass
                    
                    round_info["date"] = date_text or "Unknown date"
                    
                    # Try to extract course name using multiple selectors
                    course_text = None
                    course_selectors = [
                        ".//div[contains(@class, 'course-name')]",
                        ".//span[contains(@class, 'course')]",
                        ".//div[contains(@class, 'course')]",
                        ".//h3",
                        ".//h4"
                    ]
                    
                    for course_selector in course_selectors:
                        try:
                            elements = element.find_elements(By.XPATH, course_selector)
                            if elements:
                                course_text = elements[0].text
                                break
                        except Exception:
                            pass
                    
                    round_info["course"] = course_text or f"Round {round_id}"
                    
                    # Try to extract score using multiple selectors
                    score_text = None
                    score_selectors = [
                        ".//div[contains(@class, 'score')]",
                        ".//span[contains(@class, 'score')]",
                        ".//div[contains(text(), '+') or contains(text(), '-') or contains(text(), 'E')]", # Look for +/- scores or Even
                        ".//span[contains(text(), '+') or contains(text(), '-') or contains(text(), 'E')]"
                    ]
                    
                    for score_selector in score_selectors:
                        try:
                            elements = element.find_elements(By.XPATH, score_selector)
                            if elements:
                                score_text = elements[0].text
                                break
                        except Exception:
                            pass
                    
                    round_info["score"] = score_text or "N/A"
                    
                    logger.debug(f"Extracted round: ID={round_info['id']}, Course={round_info['course']}, Date={round_info['date']}")
                    rounds.append(round_info)
                    
                except NoSuchElementException as e:
                    logger.warning(f"Error extracting data for round {idx+1}: {str(e)}")
                    continue
                except Exception as e:
                    logger.warning(f"Unexpected error processing round {idx+1}: {str(e)}")
                    continue
            
            if not rounds:
                logger.warning("No rounds could be extracted from the page")
                take_error_screenshot(self.driver, "rounds_extraction_failed", self.screenshot_dir)
            else:
                logger.info(f"Successfully extracted {len(rounds)} rounds")
                
                # Save rounds to JSON for debugging/recovery
                save_json_data(
                    rounds,
                    generate_timestamp_filename("arccos_rounds", "json"),
                    os.path.join(project_root, 'data', 'arccos')
                )
            
            return rounds
            
        except TimeoutException as e:
            logger.error(f"Timeout waiting for rounds list to load: {str(e)}")
            take_error_screenshot(self.driver, "rounds_list_timeout", self.screenshot_dir)
            raise  # Will be caught by retry decorator
            
        except Exception as e:
            logger.error(f"Error retrieving rounds list: {str(e)}")
            take_error_screenshot(self.driver, "rounds_list_error", self.screenshot_dir)
            return []
    
    def get_round_details(self, round_id: str) -> Dict[str, Any]:
        """
        Get detailed data for a specific Arccos Golf round.
        
        Args:
            round_id: The round ID to retrieve
            
        Returns:
            Dictionary containing round data
        """
        round_data = {
            "round_id": round_id, 
            "holes": [], 
            "shots": [],
            "stats": {}
        }
        
        try:
            logger.info(f"Retrieving details for round {round_id}")
            
            # Navigate to round page
            self.driver.get(f"{self.base_url}/rounds/{round_id}")
            
            # Wait for round data to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'round-details')]"))
            )
            
            # Get round metadata
            try:
                course_name = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'course-name')]").text
                round_date = self.driver.find_element(By.XPATH, "//div[contains(@class, 'round-date')]").text
                location = self.driver.find_element(By.XPATH, "//div[contains(@class, 'course-location')]").text
                total_score = self.driver.find_element(By.XPATH, "//div[contains(@class, 'total-score')]").text
                
                # Extract scorecard data
                try:
                    total_par = self.driver.find_element(By.XPATH, "//div[contains(@class, 'total-par')]").text
                    front_nine = self.driver.find_element(By.XPATH, "//div[contains(@class, 'front-nine-score')]").text
                    back_nine = self.driver.find_element(By.XPATH, "//div[contains(@class, 'back-nine-score')]").text
                    
                    # Clean and convert to integers
                    total_score_int = int(re.sub(r'\D', '', total_score))
                    total_par_int = int(re.sub(r'\D', '', total_par))
                    front_nine_int = int(re.sub(r'\D', '', front_nine))
                    back_nine_int = int(re.sub(r'\D', '', back_nine))
                    
                    round_data.update({
                        "total_score": total_score_int,
                        "total_par": total_par_int,
                        "front_nine_score": front_nine_int,
                        "back_nine_score": back_nine_int
                    })
                except (NoSuchElementException, ValueError) as e:
                    logger.warning(f"Could not extract some scorecard data: {str(e)}")
                
                round_data.update({
                    "course_name": course_name,
                    "date": round_date,
                    "location": location
                })
            except NoSuchElementException as e:
                logger.warning(f"Could not extract some round metadata: {str(e)}")
            
            # Get hole data
            try:
                hole_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'hole-card')]")
                
                for hole_idx, hole_element in enumerate(hole_elements):
                    try:
                        hole_num = hole_element.find_element(By.XPATH, ".//div[contains(@class, 'hole-number')]").text
                        hole_par = hole_element.find_element(By.XPATH, ".//div[contains(@class, 'hole-par')]").text
                        hole_score = hole_element.find_element(By.XPATH, ".//div[contains(@class, 'hole-score')]").text
                        hole_distance = hole_element.find_element(By.XPATH, ".//div[contains(@class, 'hole-distance')]").text
                        
                        # Clean data
                        hole_num_int = int(re.sub(r'\D', '', hole_num))
                        hole_par_int = int(re.sub(r'\D', '', hole_par))
                        hole_score_int = int(re.sub(r'\D', '', hole_score))
                        hole_distance_int = int(re.sub(r'\D', '', hole_distance))
                        
                        # Check fairway hit and GIR indicators
                        fairway_hit = "fairway-hit" in hole_element.get_attribute("class")
                        gir = "gir" in hole_element.get_attribute("class")
                        
                        hole_data = {
                            "hole_number": hole_num_int,
                            "par": hole_par_int,
                            "score": hole_score_int,
                            "distance_yards": hole_distance_int,
                            "fairway_hit": fairway_hit,
                            "green_in_regulation": gir
                        }
                        
                        # Get putts for this hole
                        try:
                            putts = hole_element.find_element(By.XPATH, ".//div[contains(@class, 'putts')]").text
                            hole_data["putts"] = int(re.sub(r'\D', '', putts))
                        except (NoSuchElementException, ValueError):
                            hole_data["putts"] = None
                        
                        round_data["holes"].append(hole_data)
                        
                        # Click on hole to get shot data
                        hole_element.click()
                        
                        # Wait for shot data to load
                        time.sleep(1)  # Small delay for animation
                        
                        # Get shots for this hole
                        try:
                            shot_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'shot-item')]")
                            
                            for shot_idx, shot_element in enumerate(shot_elements):
                                try:
                                    club = shot_element.find_element(By.XPATH, ".//div[contains(@class, 'club')]").text
                                    distance = shot_element.find_element(By.XPATH, ".//div[contains(@class, 'distance')]").text
                                    
                                    # Determine location based on class
                                    from_location = "unknown"
                                    to_location = "unknown"
                                    
                                    if "tee-shot" in shot_element.get_attribute("class"):
                                        from_location = "tee"
                                    elif "fairway-shot" in shot_element.get_attribute("class"):
                                        from_location = "fairway"
                                    elif "rough-shot" in shot_element.get_attribute("class"):
                                        from_location = "rough"
                                    elif "sand-shot" in shot_element.get_attribute("class"):
                                        from_location = "sand"
                                    elif "green-shot" in shot_element.get_attribute("class"):
                                        from_location = "green"
                                    
                                    if "to-fairway" in shot_element.get_attribute("class"):
                                        to_location = "fairway"
                                    elif "to-rough" in shot_element.get_attribute("class"):
                                        to_location = "rough"
                                    elif "to-sand" in shot_element.get_attribute("class"):
                                        to_location = "sand"
                                    elif "to-green" in shot_element.get_attribute("class"):
                                        to_location = "green"
                                    elif "to-hole" in shot_element.get_attribute("class"):
                                        to_location = "hole"
                                    
                                    is_penalty = "penalty" in shot_element.get_attribute("class")
                                    
                                    shot_data = {
                                        "hole_number": hole_num_int,
                                        "shot_number": shot_idx + 1,
                                        "club": club,
                                        "distance_yards": float(re.sub(r'[^\d.]', '', distance)) if distance else None,
                                        "from_location": from_location,
                                        "to_location": to_location,
                                        "is_penalty": is_penalty
                                    }
                                    
                                    round_data["shots"].append(shot_data)
                                except Exception as e:
                                    logger.warning(f"Error processing shot {shot_idx+1} for hole {hole_num_int}: {str(e)}")
                            
                        except NoSuchElementException:
                            logger.warning(f"No shot data found for hole {hole_num_int}")
                        
                        # Close hole details
                        close_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'close-button')]")
                        close_button.click()
                        time.sleep(0.5)  # Small delay for animation
                        
                    except Exception as e:
                        logger.warning(f"Error processing hole {hole_idx+1}: {str(e)}")
                
                logger.info(f"Retrieved {len(round_data['holes'])} holes and {len(round_data['shots'])} shots for round {round_id}")
            
            except Exception as e:
                logger.error(f"Error retrieving hole data: {str(e)}")
            
            # Get round statistics
            try:
                # Click on stats tab
                stats_tab = self.driver.find_element(By.XPATH, "//a[contains(@class, 'stats-tab')]")
                stats_tab.click()
                
                # Wait for stats to load
                time.sleep(1)
                
                # Extract stats
                fairways_hit = self.driver.find_element(By.XPATH, "//div[contains(@class, 'fairways-hit')]").text
                fairways_total = self.driver.find_element(By.XPATH, "//div[contains(@class, 'fairways-total')]").text
                gir = self.driver.find_element(By.XPATH, "//div[contains(@class, 'gir')]").text
                putts = self.driver.find_element(By.XPATH, "//div[contains(@class, 'putts-total')]").text
                avg_drive = self.driver.find_element(By.XPATH, "//div[contains(@class, 'avg-drive')]").text
                
                # Clean and convert
                fh_match = re.search(r'(\d+)/(\d+)', fairways_hit)
                if fh_match:
                    fairways_hit_int = int(fh_match.group(1))
                    fairways_total_int = int(fh_match.group(2))
                else:
                    fairways_hit_int = None
                    fairways_total_int = None
                
                gir_match = re.search(r'(\d+)', gir)
                gir_int = int(gir_match.group(1)) if gir_match else None
                
                putts_match = re.search(r'(\d+)', putts)
                putts_int = int(putts_match.group(1)) if putts_match else None
                
                avg_drive_match = re.search(r'(\d+)', avg_drive)
                avg_drive_float = float(avg_drive_match.group(1)) if avg_drive_match else None
                
                # Calculate putts per hole
                putts_per_hole = round(putts_int / len(round_data["holes"]), 1) if putts_int and round_data["holes"] else None
                
                # Add to round data
                round_data["stats"] = {
                    "fairways_hit": fairways_hit_int,
                    "fairways_total": fairways_total_int,
                    "greens_in_regulation": gir_int,
                    "putts_total": putts_int,
                    "putts_per_hole": putts_per_hole,
                    "average_drive_yards": avg_drive_float
                }
                
                logger.info("Retrieved round statistics")
            except Exception as e:
                logger.warning(f"Error retrieving round statistics: {str(e)}")
            
            return round_data
        
        except TimeoutException:
            logger.error(f"Timeout waiting for round {round_id} data to load")
            return round_data
        except Exception as e:
            logger.error(f"Error retrieving round details: {str(e)}")
            return round_data
    
    def transform_to_golf_data(self, round_data: Dict[str, Any]) -> Tuple[GolfRound, List[GolfHole], List[GolfShot], Optional[RoundStats]]:
        """
        Transform Arccos round data to GolfStats data model.
        
        Args:
            round_data: Round data retrieved from Arccos
            
        Returns:
            Tuple of (GolfRound, list of GolfHole objects, list of GolfShot objects, RoundStats)
        """
        try:
            logger.info(f"Transforming Arccos round {round_data['round_id']} to GolfStats model")
            
            # Parse date
            try:
                # This date format might need adjustment based on actual Arccos format
                date_str = round_data.get("date", "")
                date_obj = datetime.datetime.strptime(date_str, "%b %d, %Y")
            except ValueError:
                logger.warning(f"Could not parse date: {round_data.get('date')}, using current time")
                date_obj = datetime.datetime.now()
            
            # Create golf round
            golf_round = GolfRound(
                user_id=self.user_id,
                date=date_obj,
                course_name=round_data.get("course_name", "Unknown Course"),
                course_location=round_data.get("location", ""),
                total_score=round_data.get("total_score"),
                total_par=round_data.get("total_par"),
                front_nine_score=round_data.get("front_nine_score"),
                back_nine_score=round_data.get("back_nine_score"),
                source_system="arccos",
                notes=f"Arccos Round ID: {round_data['round_id']}"
            )
            
            # Process holes
            golf_holes = []
            hole_dict = {}  # Map hole numbers to hole objects
            
            for hole_data in round_data.get("holes", []):
                golf_hole = GolfHole(
                    hole_number=hole_data.get("hole_number"),
                    par=hole_data.get("par"),
                    score=hole_data.get("score"),
                    fairway_hit=hole_data.get("fairway_hit"),
                    green_in_regulation=hole_data.get("green_in_regulation"),
                    putts=hole_data.get("putts"),
                    distance_yards=hole_data.get("distance_yards")
                )
                
                # Add hole to round
                golf_round.holes.append(golf_hole)
                golf_holes.append(golf_hole)
                
                # Store in dictionary for shot mapping
                hole_dict[golf_hole.hole_number] = golf_hole
            
            # Process shots
            golf_shots = []
            for shot_data in round_data.get("shots", []):
                hole_number = shot_data.get("hole_number")
                if hole_number in hole_dict:
                    golf_hole = hole_dict[hole_number]
                    
                    golf_shot = GolfShot(
                        shot_number=shot_data.get("shot_number"),
                        club=shot_data.get("club"),
                        distance_yards=shot_data.get("distance_yards"),
                        from_location=shot_data.get("from_location"),
                        to_location=shot_data.get("to_location"),
                        is_penalty=shot_data.get("is_penalty")
                    )
                    
                    # Add shot to hole
                    golf_hole.shots.append(golf_shot)
                    golf_shots.append(golf_shot)
            
            # Create round stats
            stats_data = round_data.get("stats", {})
            if stats_data:
                # Calculate score to par
                score_to_par = None
                if round_data.get("total_score") is not None and round_data.get("total_par") is not None:
                    score_to_par = round_data["total_score"] - round_data["total_par"]
                
                round_stats = RoundStats(
                    score_to_par=score_to_par,
                    fairways_hit=stats_data.get("fairways_hit"),
                    fairways_total=stats_data.get("fairways_total"),
                    greens_in_regulation=stats_data.get("greens_in_regulation"),
                    putts_total=stats_data.get("putts_total"),
                    putts_per_hole=stats_data.get("putts_per_hole"),
                    average_drive_yards=stats_data.get("average_drive_yards")
                )
                
                # Add stats to round
                golf_round.stats = round_stats
            else:
                round_stats = None
            
            logger.info(f"Transformed {len(golf_holes)} holes and {len(golf_shots)} shots")
            return golf_round, golf_holes, golf_shots, round_stats
        
        except Exception as e:
            logger.error(f"Error transforming round data: {str(e)}")
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
                # Check if this round already exists (based on date, course and source_system ID)
                existing_round = db.query(GolfRound).filter(
                    GolfRound.user_id == self.user_id,
                    GolfRound.date == golf_round.date,
                    GolfRound.course_name == golf_round.course_name,
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
        Run the Arccos scraper to extract and store data.
        
        Args:
            limit: Maximum number of rounds to process
            
        Returns:
            List of golf round IDs that were processed
        """
        round_ids = []
        
        try:
            logger.info(f"Starting Arccos scraper for user {self.user_id}")
            
            # Set up WebDriver
            self.setup_driver()
            
            # Login
            if not self.login():
                logger.error("Login failed, aborting")
                return round_ids
            
            # Get round list
            rounds = self.get_round_list(limit=limit)
            logger.info(f"Found {len(rounds)} rounds to process")
            
            # Process each round
            for round_data in rounds:
                try:
                    # Get round details
                    round_id = round_data["id"]
                    detailed_data = self.get_round_details(round_id)
                    
                    # Transform data
                    golf_round, _, _, _ = self.transform_to_golf_data(detailed_data)
                    
                    # Save to database
                    db_round_id = self.save_to_database(golf_round)
                    round_ids.append(db_round_id)
                    
                except Exception as e:
                    logger.error(f"Error processing round {round_data.get('id', 'unknown')}: {str(e)}")
            
            logger.info(f"Arccos scraper completed - processed {len(round_ids)} rounds")
            
        except Exception as e:
            logger.error(f"Arccos scraper failed: {str(e)}")
        
        finally:
            # Clean up
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
        
        return round_ids

def get_arrcos_data(user_id: int, limit: int = 10) -> List[int]:
    """
    Scrape Arccos Golf data for a specific user.
    
    Args:
        user_id: The database ID of the user
        limit: Maximum number of rounds to process
        
    Returns:
        List of golf round IDs that were processed
    """
    scraper = ArccosScraper(user_id=user_id)
    return scraper.run(limit=limit)
