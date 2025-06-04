"""
Dubizzle Egypt price estimator.
"""

import logging
import time
from typing import Union

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import BasePriceEstimator
from ..utils.web_scraping import WebScrapingUtils
from ..utils.text_processing import TextProcessor
from ..config.estimation_config import EstimationConfig

logger = logging.getLogger('price_estimation')


class DubizzlePriceEstimator(BasePriceEstimator):
    """
    Dubizzle Egypt price estimator using Selenium (like Amazon approach).

    This estimator now uses browser automation for better reliability:
    - Handles dynamic content loading
    - Bypasses anti-bot measures
    - Works with current website structure
    - More reliable than requests-based approach
    """

    def __init__(self):
        super().__init__()
        self.text_processor = TextProcessor()

    def estimate_price(self, name: str, description: str) -> Union[float, str]:
        """Estimate price from Dubizzle Egypt using Selenium."""
        driver = None
        try:
            driver = WebScrapingUtils.get_webdriver()

            # Go to homepage first
            driver.get("https://www.dubizzle.com.eg")
            time.sleep(2)

            # Find search box and perform search
            search_box = driver.find_element(By.CSS_SELECTOR, 'input[type="search"]')
            search_query = f"{name} {description}".strip()

            logger.debug(f"Searching Dubizzle for: {search_query}")

            search_box.clear()
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(4)  # Wait for search results to load

            logger.debug(f"Search results URL: {driver.current_url}")

            # Look for price elements using multiple selectors
            prices = self._extract_prices_from_page(driver, name, description)

            if prices:
                average_price = sum(prices) / len(prices)
                logger.info(f"Found {len(prices)} matching prices on Dubizzle")

                # Apply discount for used items
                if self.text_processor.is_used_item(description) or self.text_processor.is_used_item(name):
                    average_price *= EstimationConfig.USED_DISCOUNT_FACTOR

                return round(average_price, 2)

            return "No price found on Dubizzle"

        except Exception as e:
            logger.error(f"Dubizzle scraping error: {str(e)}")
            return f"Dubizzle estimation failed: {str(e)}"
        finally:
            if driver:
                driver.quit()

    def _extract_prices_from_page(self, driver, name: str, description: str) -> list:
        """Extract prices from Dubizzle search results page."""
        prices = []

        try:
            # Wait a bit more for dynamic content to load
            time.sleep(2)

            # Use the correct selector for Dubizzle listings (based on debugging)
            listings = driver.find_elements(By.CSS_SELECTOR, "article")

            if not listings:
                logger.warning("No article listings found on Dubizzle page")
                return prices

            logger.debug(f"Found {len(listings)} article listings")

            # Extract prices from each listing
            for i, listing in enumerate(listings[:20]):  # Limit to first 20 listings
                try:
                    price = self._extract_price_from_listing(listing, name, description)
                    if price:
                        prices.append(price)
                        logger.debug(f"Extracted price {price} from listing {i+1}")
                except Exception as e:
                    logger.debug(f"Failed to extract price from listing {i+1}: {str(e)}")
                    continue

            logger.debug(f"Total prices extracted: {len(prices)}")
            return prices

        except Exception as e:
            logger.error(f"Error extracting prices from Dubizzle page: {str(e)}")
            return prices

    def _extract_price_from_listing(self, listing, name: str, description: str) -> float:
        """Extract price from a single Dubizzle listing."""
        try:
            # Get the full text of the listing first
            listing_text = listing.text.strip()

            if not listing_text:
                return None

            logger.debug(f"Found listing text: {listing_text[:100]}...")

            # Calculate similarity using the full listing text
            search_text = f"{name} {description}".lower()
            similarity = self.text_processor.calculate_similarity(listing_text.lower(), search_text)

            # Use a lower threshold for Dubizzle since listings are more varied
            dubizzle_threshold = 0.25  # Lower than the default 0.58
            logger.debug(f"Similarity score: {round(similarity, 2)} (threshold: {dubizzle_threshold})")

            if similarity < dubizzle_threshold:
                return None

            logger.debug(f"Matched listing with similarity {round(similarity, 2)}")

            # Extract price from the listing text using text processor
            price = self.text_processor.extract_price_from_text(listing_text)
            if price:
                logger.debug(f"Extracted price: {price}")
                return price

            # If text processor didn't find price, try to find specific price elements
            price_elements = listing.find_elements(By.CSS_SELECTOR, "*")
            for element in price_elements:
                try:
                    element_text = element.text.strip()
                    if element_text and ('ج.م' in element_text or 'EGP' in element_text or 'جنيه' in element_text):
                        price = self.text_processor.extract_price_from_text(element_text)
                        if price:
                            logger.debug(f"Found price in element: {price}")
                            return price
                except:
                    continue

            return None

        except Exception as e:
            logger.debug(f"Error extracting price from listing: {str(e)}")
            return None
