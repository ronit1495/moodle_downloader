"""Authentication service for the Moodle Downloader."""

import logging
import re
from bs4 import BeautifulSoup
from config.config import LOGIN_URL, DASHBOARD_URL, USERNAME, PASSWORD
from src.utils.request_utils import safe_request

logger = logging.getLogger(__name__)

def login(session):
    """Log in to Moodle."""
    logger.info("Fetching login page...")
    
    # Get login token
    login_page = safe_request(session, "GET", LOGIN_URL)
    if not login_page:
        logger.error("Failed to fetch login page")
        return False
        
    soup = BeautifulSoup(login_page.text, "html.parser")
    token_input = soup.find("input", {"name": "logintoken"})
    login_token = token_input["value"] if token_input else ""
    
    if not login_token:
        logger.warning("No login token found, attempting login without token")
    
    # Login
    logger.info("Logging in...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "logintoken": login_token
    }
    response = safe_request(session, "POST", LOGIN_URL, data=login_data)
    if not response:
        logger.error("Login request failed")
        return False
    
    # Debug login response
    logger.debug(f"Login response status: {response.status_code}")
    logger.debug(f"Login response URL: {response.url}")
    
    if "Dashboard" not in response.text:
        logger.error("Login failed! Response doesn't contain Dashboard")
        logger.debug(f"Response content: {response.text[:500]}...")
        return False
    
    logger.info("Login successful!")
    return True

def get_sesskey(session):
    """Extract sesskey from dashboard page."""
    logger.info("Getting sesskey...")
    try:
        response = safe_request(session, "GET", DASHBOARD_URL)
        if response:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Method 1: Look for sesskey in script tags
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and "M.cfg.sesskey" in script.string:
                    match = re.search(r'M\.cfg\.sesskey\s*=\s*["\']([^"\']+)["\']', script.string)
                    if match:
                        return match.group(1)
            
            # Method 2: Look for sesskey in any link that contains it
            links = soup.find_all("a", href=lambda href: href and "sesskey=" in href)
            if links:
                href = links[0].get("href", "")
                sesskey = href.split("sesskey=")[1].split("&")[0]
                return sesskey
            
            # Method 3: Look for hidden input with sesskey
            sesskey_input = soup.find("input", {"name": "sesskey"})
            if sesskey_input:
                return sesskey_input.get("value", "")
    except Exception as e:
        logger.error(f"Error getting sesskey: {str(e)}")
    return None 