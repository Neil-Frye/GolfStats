import requests
from bs4 import BeautifulSoup
import logging
import re
import json # For printing the payload structure in main

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

class SkyTrakAuth:
    """
    A class to attempt authentication with SkyTrak Clubhouse.

    NOTE: Due to the JavaScript-heavy nature of the login page, automatically
    finding a CSRF token (authenticity_token) has been unsuccessful with the
    available tools. This module makes a best-effort attempt to log in
    but may require manual discovery of the CSRF token mechanism or a
    JavaScript-rendering environment for reliable authentication.
    """
    def __init__(self):
        self.session = requests.Session()
        # Standard headers that a browser might send
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://clubhouse.skytrakgolf.com', # Often required for POST requests
            'Referer': 'https://clubhouse.skytrakgolf.com/login', # Common referer for login
        })
        self.login_url = "https://clubhouse.skytrakgolf.com/login"
        # SkyTrak also uses "https://clubhouse.skytrakgolf.com/users/sign_in" which is a common Devise endpoint.
        # However, the prompt specified /login for the POST.
        self.login_post_url = self.login_url # Using the same URL for POST as per task
        self.logged_in = False

    def _extract_token_from_html(self, html_content):
        """Tries to extract authenticity_token from various HTML elements."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Try input field
        token_element = soup.find('input', {'name': 'authenticity_token'})
        if token_element and token_element.get('value'):
            token = token_element.get('value')
            logger.info(f"Found authenticity_token in HTML input field: {token}")
            return token
        
        # 2. Try meta tag
        csrf_token_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_token_meta and csrf_token_meta.get('content'):
            token = csrf_token_meta.get('content')
            logger.info(f"Found authenticity_token in HTML meta tag: {token}")
            return token

        # 3. Try searching in script tags (as attempted before)
        logger.debug("Attempting to extract token from script tags via regex.")
        patterns = [
            r'"csrfToken"\s*:\s*"([^"]+)"', r"'csrfToken'\s*:\s*'([^']+)'",
            r'"csrf-token"\s*:\s*"([^"]+)"', r"'csrf-token'\s*:\s*'([^']+)'",
            r'"authenticity_token"\s*:\s*"([^"]+)"', r"'authenticity_token'\s*:\s*'([^']+)'"
        ]
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                token = match.group(1)
                logger.info(f"Found potential token in script tag via regex ({pattern}): {token}")
                return token
        
        logger.warning("Could not find authenticity_token in HTML inputs, meta tags, or script contents.")
        return None

    def login(self, email, password):
        """
        Attempts to log in to SkyTrak Clubhouse.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            requests.Session: The session object if login is deemed successful.
                              The session will contain relevant cookies.
        Raises:
            Exception: If login fails or an error occurs.
        """
        try:
            logger.info(f"Fetching login page: {self.login_url} to get cookies and token.")
            get_response = self.session.get(self.login_url, allow_redirects=True)
            get_response.raise_for_status() # Ensure GET request was successful

            logger.info(f"GET request successful. URL: {get_response.url}")
            logger.info(f"Initial session cookies: {self.session.cookies.get_dict()}")

            authenticity_token = self._extract_token_from_html(get_response.text)
            
            if not authenticity_token:
                logger.error("CRITICAL: authenticity_token not found. Login will likely fail.")
                # Proceeding anyway to demonstrate the POST attempt, but this is usually a failure point.
            
            # Standard form payload
            payload = {
                'utf8': '✓', # Often present in Rails forms
                'user[email]': email,
                'user[password]': password,
                'commit': 'Login'
            }
            if authenticity_token:
                payload['authenticity_token'] = authenticity_token
            
            logger.info(f"Attempting POST to {self.login_post_url}")
            logger.info(f"Payload (form data, password omitted for logging, token status: {'Found' if authenticity_token else 'MISSING!'}): "
                        f"user[email]={email}, commit=Login, authenticity_token={authenticity_token if authenticity_token else 'N/A'}")

            # POST as form data
            post_response = self.session.post(self.login_post_url, data=payload, allow_redirects=True)
            # No explicit raise_for_status() here, as failed logins often return 200/4xx, not 5xx.

            logger.info(f"POST request completed. Final URL: {post_response.url}, Status: {post_response.status_code}")
            logger.info(f"Session cookies after POST: {self.session.cookies.get_dict()}")
            # logger.info(f"POST response headers: {post_response.headers}")
            # logger.debug(f"POST response content (first 300 chars): {post_response.text[:300]}")

            # Verification of successful login:
            # 1. Did the URL change from the login page significantly?
            # 2. Is there a user-specific session cookie? (e.g., _clubhouse_session)
            # 3. Does the page content indicate a successful login (e.g., no "Invalid email" message)?

            if self.login_url in post_response.url and post_response.status_code == 200:
                # Still on the login page or redirected back. Check for error messages.
                if "Invalid email or password" in post_response.text or \
                   "alert-danger" in post_response.text or \
                   "error" in post_response.text.lower(): # General error check
                    logger.error("Login failed: Error message found on response page or still on login page.")
                    logger.debug(f"Response snippet for error check: {post_response.text[post_response.text.lower().find('error')-50:post_response.text.lower().find('error')+50]}")
                    raise Exception("Login failed: Invalid credentials or CSRF token issue.")
                else:
                    logger.warning("Login status uncertain: Still on login page URL but no clear error message. Assuming failure.")
                    raise Exception("Login failed: Unknown error, still on login page.")
            
            # Check for a specific session cookie that usually appears after login
            # (e.g., _clubhouse_session, _skytrak_session - this is a guess)
            # For many Rails apps, a cookie like '_app_session' is set.
            # The actual cookie name would need to be known from a successful login observation.
            if not any(k.endswith('_session') for k in self.session.cookies.keys()):
                 logger.warning("Login status uncertain: No typical session cookie found after POST. This might indicate failure.")
                 # Not raising an exception here as some sites might not set cookies immediately or use different patterns.
            
            # If we are redirected to a different page AND status is 200, it's a good sign.
            if post_response.status_code == 200 and self.login_url not in post_response.url:
                logger.info("Login appears successful: Redirected to a new page and status is 200.")
                self.logged_in = True
                return self.session
            
            # If we made it here, the outcome is uncertain or not definitively successful by the checks.
            # Given the CSRF token issue, failure is the most likely outcome.
            logger.error(f"Login failed or status uncertain. Final URL: {post_response.url}, Status: {post_response.status_code}")
            raise Exception(f"Login failed or status uncertain. Final URL: {post_response.url}, Status: {post_response.status_code}")


        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during login: {e}")
            if e.response is not None:
                logger.error(f"Response content: {e.response.text[:500]}")
            raise Exception(f"HTTP error: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"A network or request error occurred: {e}")
            raise Exception(f"Request error: {e}") from e

# Main block for usage example
if __name__ == '__main__':
    print("SkyTrak Clubhouse Authentication Module Example")
    print("--------------------------------------------")
    print("This script attempts to log in to SkyTrak Clubhouse.")
    print("NOTE: CSRF token (authenticity_token) detection is problematic due to JavaScript.")
    print("Login will likely fail without a valid token.\n")

    # It's highly recommended to use environment variables or a secure config for credentials.
    # For this example, we'll use placeholders.
    # skytrak_email = os.environ.get("SKYTRAK_EMAIL", "your_email@example.com")
    # skytrak_password = os.environ.get("SKYTRAK_PASSWORD", "your_password")
    
    skytrak_email = "test@example.com"  # Replace with a real email for actual testing
    skytrak_password = "fakepassword123" # Replace with a real password for actual testing

    print(f"Attempting login for user: {skytrak_email}\n")

    auth = SkyTrakAuth()
    
    try:
        successful_session = auth.login(skytrak_email, skytrak_password)
        print("\nLogin reported as successful!")
        print(f"Session cookies: {successful_session.cookies.get_dict()}")
        # To use the session for subsequent requests:
        # response = successful_session.get("https://clubhouse.skytrakgolf.com/some_protected_page")
        # print(f"Protected page status: {response.status_code}")
    except Exception as e:
        print(f"\nLogin failed: {e}")

    print("\nPayload fields sent (if token was found):")
    payload_structure = {
        'utf8': '✓',
        'user[email]': skytrak_email,
        'user[password]': "********", # Masked for printing
        'authenticity_token': "Value fetched from page (if found, critical for success)",
        'commit': 'Login'
    }
    print(json.dumps(payload_structure, indent=2))
    print("\nThe 'authenticity_token' is the critical piece that this script struggles to find automatically.")
