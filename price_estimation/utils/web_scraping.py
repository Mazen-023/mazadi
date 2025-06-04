"""
Web scraping utilities for price estimation.

Contains common functionality for web scraping operations.
"""

import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger('price_estimation')


class WebScrapingUtils:
    """Utility class for common web scraping operations."""
    
    @staticmethod
    def create_session():
        """Create and configure requests session."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        })
        return session
    
    @staticmethod
    def get_webdriver():
        """Get configured Chrome WebDriver."""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            logger.error(f"WebDriver initialization failed: {str(e)}")
            raise

    @staticmethod
    def get_amazon_webdriver():
        """Get Chrome WebDriver with enhanced anti-detection for Amazon."""
        options = Options()

        # Enhanced anti-detection for Amazon
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Use a more recent user agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

        # Add realistic browser preferences
        prefs = {
            "profile.default_content_setting_values": {
                "popups": 2,  # Block popups
                "geolocation": 2,  # Block location sharing
                "notifications": 2,  # Block notifications
                "media_stream": 2,  # Block media stream
            }
        }
        options.add_experimental_option("prefs", prefs)

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # Execute stealth scripts
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")

            return driver
        except Exception as e:
            logger.error(f"Amazon WebDriver initialization failed: {str(e)}")
            raise

    @staticmethod
    def get_dubizzle_headers():
        """Get headers for Dubizzle requests."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.dubizzle.com.eg/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
        }
    
    @staticmethod
    def generate_dubizzle_urls(search_terms: str):
        """Generate multiple Dubizzle URL patterns."""
        import urllib.parse
        
        return [
            f"https://www.dubizzle.com.eg/ads/q-{search_terms.replace(' ', '-')}/",
            f"https://www.dubizzle.com.eg/search?q={urllib.parse.quote(search_terms)}",
            f"https://www.dubizzle.com.eg/en/search?q={urllib.parse.quote(search_terms)}",
            f"https://www.dubizzle.com.eg/classified/{search_terms.replace(' ', '-')}",
        ]
