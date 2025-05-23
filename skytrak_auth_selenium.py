import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

class SkyTrakSeleniumAuth:
    def __init__(self, chromedriver_path=None):
        logger.info("Initializing SkyTrakSeleniumAuth...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('window-size=1920x1080')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")

        if chromedriver_path:
            service = ChromeService(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            self.driver = webdriver.Chrome(options=options)
        
        self.login_url = "https://clubhouse.skytrakgolf.com/login"
        self.logged_in = False
        logger.info("WebDriver initialized in headless mode.")

    def _get_csrf_token(self):
        logger.info(f"Navigating to login page: {self.login_url}")
        self.driver.get(self.login_url)
        
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, 'user[email]'))
            )
            logger.info("Login page basic elements (email field) seem to be loaded.")
        except TimeoutException:
            logger.error("Timeout waiting for basic login page elements (e.g., email field). Page might not be loading correctly.")
            self.driver.save_screenshot("debug_page_load_timeout.png")
            logger.debug(f"Page source at timeout:\n{self.driver.page_source[:2000]}")
            raise Exception("Failed to load essential login page elements.")

        possible_token_names = ['authenticity_token', 'csrf-token', '_csrf', 'YII_CSRF_TOKEN', 'csrfmiddlewaretoken']
        csrf_token_value = None
        token_field_found = None

        logger.info(f"Attempting to find CSRF token input field with names: {possible_token_names}")
        for name in possible_token_names:
            try:
                token_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, name))
                )
                logger.info(f"Found potential CSRF input field with name: {name}")
                WebDriverWait(self.driver, 15).until(
                    lambda d: token_field.get_attribute('value') != "" and token_field.get_attribute('value') is not None
                )
                csrf_token_value = token_field.get_attribute('value')
                if csrf_token_value:
                    logger.info(f"Successfully extracted CSRF token '{csrf_token_value}' from field '{name}'")
                    token_field_found = token_field
                    break 
            except TimeoutException:
                logger.debug(f"Timeout or no value for token field named: {name}")
            except NoSuchElementException:
                logger.debug(f"Token field not found with name: {name}")
        
        if not csrf_token_value:
            logger.info("CSRF token not found in input fields. Checking common meta tags...")
            meta_tag_names = ['csrf-token', 'X-CSRF-Token', 'authenticity-token']
            for meta_name in meta_tag_names:
                try:
                    meta_tag = self.driver.find_element(By.CSS_SELECTOR, f"meta[name='{meta_name}']")
                    csrf_token_value = meta_tag.get_attribute('content')
                    if csrf_token_value:
                        logger.info(f"Successfully extracted CSRF token '{csrf_token_value}' from meta tag '{meta_name}'")
                        return csrf_token_value, None 
                except NoSuchElementException:
                    logger.debug(f"No meta tag found with name: {meta_name}")
        
        if not csrf_token_value:
            logger.error("Failed to find CSRF token in common input fields or meta tags after all attempts.")
            self.driver.save_screenshot("debug_csrf_final_fail.png")
            logger.debug(f"Page source at final CSRF search failure:\n{self.driver.page_source[:3000]}")
            raise ValueError("CSRF token could not be found on the page.")

        return csrf_token_value, token_field_found

    def login(self, email, password):
        try:
            csrf_token, token_input_field_obj = self._get_csrf_token()

            logger.info("Locating email and password fields...")
            email_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, 'user[email]'))
            )
            password_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, 'user[password]'))
            )
            
            logger.info(f"Filling login form with email (password not logged). CSRF: {csrf_token}")
            email_field.clear()
            email_field.send_keys(email)
            password_field.clear()
            password_field.send_keys(password)
            
            if token_input_field_obj:
                 logger.info(f"Token field '{token_input_field_obj.get_attribute('name')}' already has value: {token_input_field_obj.get_attribute('value')}. Ensuring it matches fetched token.")
                 if token_input_field_obj.get_attribute('value') != csrf_token:
                    logger.warning(f"Value of token field '{token_input_field_obj.get_attribute('name')}' ('{token_input_field_obj.get_attribute('value')}') does not match fetched token ('{csrf_token}'). Attempting to set with JS.")
                    self.driver.execute_script(f"arguments[0].value = '{csrf_token}';", token_input_field_obj)
            elif csrf_token: 
                try:
                    hidden_csrf_field = self.driver.find_element(By.NAME, 'authenticity_token')
                    self.driver.execute_script(f"arguments[0].value = '{csrf_token}';", hidden_csrf_field)
                    logger.info(f"Set value of hidden field 'authenticity_token' using CSRF from meta tag.")
                except NoSuchElementException:
                    logger.warning("No 'authenticity_token' input field found to inject meta-tag CSRF token into. Login might fail if form expects it.")

            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, 'commit'))
            )
            logger.info("Submitting login form...")
            login_button.click()

            logger.info("Waiting for page navigation after login submission...")
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.any_of(
                        EC.url_contains("/activity"), 
                        EC.url_contains("/dashboard"),
                        EC.url_matches("https://clubhouse.skytrakgolf.com/$"), 
                        EC.not_(EC.url_contains(self.login_url.split('/')[-1])) 
                    )
                )
                current_url = self.driver.current_url
                logger.info(f"Login successful or navigated away from login page. Current URL: {current_url}")
                
                if self.login_url.split('/')[-1] in current_url: # Check if still on /login
                     logger.error("Login failed: Still on the login page, but expected navigation.")
                     self.driver.save_screenshot("debug_login_still_on_loginpage.png")
                     raise Exception("Login failed: Still on login page after submission.")

                self.logged_in = True
                return True

            except TimeoutException:
                logger.warning("URL did not change significantly or to a known success page after 20 seconds.")
                page_text = self.driver.page_source.lower() 
                if "invalid email or password" in page_text or \
                   "incorrect username or password" in page_text or \
                   self.driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'invalid email or password')]"):
                    logger.error("Login failed: Invalid credentials error message found on page.")
                    self.driver.save_screenshot("debug_login_invalid_creds.png")
                    raise Exception("Login failed: Invalid email or password.")
                else:
                    logger.error("Login failed: URL did not change, and no standard error message detected. Unknown error.")
                    self.driver.save_screenshot("debug_login_unknown_error.png")
                    logger.debug(f"Page source at unknown error:\n{self.driver.page_source[:3000]}")
                    raise Exception("Login failed: Page did not redirect and no clear error message.")
        
        except NoSuchElementException as e:
            msg = e.msg if hasattr(e, 'msg') else str(e) # Selenium 4 uses e.msg
            logger.error(f"Could not find an element during login: {msg}")
            self.driver.save_screenshot("debug_login_no_such_element.png")
            raise Exception(f"Login failed: Element not found ({msg})") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred during login: {e}")
            if not "debug_" in str(e).lower() and hasattr(self.driver, 'save_screenshot'): # Avoid saving again if specific error already did
                 self.driver.save_screenshot("debug_login_unexpected_error.png")
            if not isinstance(e, (TimeoutException, ValueError, NoSuchElementException)): 
                raise Exception(f"Login failed due to an unexpected error: {e}") from e
            else:
                raise 

    def get_current_cookies(self):
        if not self.driver:
            logger.warning("WebDriver not initialized. Cannot get cookies.")
            return {}
        logger.info("Fetching current browser cookies.")
        return self.driver.get_cookies()

    def close_browser(self):
        if self.driver:
            logger.info("Closing WebDriver...")
            self.driver.quit()
            self.driver = None 
            logger.info("WebDriver closed.")

if __name__ == '__main__':
    logger.info("SkyTrak Clubhouse Selenium Authentication Module Example")
    logger.info("----------------------------------------------------")
    logger.info("This script attempts to log in to SkyTrak Clubhouse using Selenium.")
    
    skytrak_email = "test@example.com" 
    skytrak_password = "fakepassword123" 

    auth = None 
    login_successful = False
    try:
        auth = SkyTrakSeleniumAuth() 
        logger.info(f"Attempting login for user: {skytrak_email}")
        login_successful = auth.login(skytrak_email, skytrak_password)
        
        if login_successful:
            logger.info("Login process reported SUCCESS.")
            cookies = auth.get_current_cookies()
            logger.info(f"Session cookies: {cookies}")
        else:
            logger.warning("Login process completed but reported NOT successful (and did not raise an exception). This is unexpected.")

    except Exception as e:
        logger.error(f"Login process FAILED: {e}")
    finally:
        if auth: 
            auth.close_browser()

    logger.info("----------------------------------------------------")
    logger.info("Method to find and extract CSRF token:")
    logger.info("1. Navigate to the login page using Selenium (headless Chrome).")
    logger.info("2. Wait for JavaScript and page elements (like email field) to load.")
    logger.info("3. Search for CSRF token in hidden input fields (common names like 'authenticity_token', 'csrf-token') and wait for their 'value'.")
    logger.info("4. If not in input, check common meta tags (e.g., 'csrf-token').")
    logger.info("5. Extract the token value.")
    logger.info("6. Fill this token, along with username and password, into the form using Selenium (setting hidden field value via JS if necessary).")
    logger.info("7. Submit the form by clicking the login button.")
    logger.info(f"Script finished. Login success status: {login_successful}")
```
