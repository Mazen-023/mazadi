"""
Dubizzle Egypt price estimator.
"""

import logging
import time
from typing import Union

from selenium.webdriver.common.by import By

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

            # Create a shorter, more focused search query
            search_query = self._create_search_query(name, description)
            logger.debug(f"Searching Dubizzle for: {search_query}")

            # Go directly to search results page instead of using search box
            search_url = f"https://www.dubizzle.com.eg/ads/q-{search_query.replace(' ', '-')}/"
            driver.get(search_url)
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

    def _create_search_query(self, name: str, description: str) -> str:
        """Create a focused search query for Dubizzle."""
        # Extract key terms from name and description
        combined_text = f"{name} {description}".lower()

        # Extract brand names
        brands = ['iphone', 'samsung', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'apple', 'huawei', 'xiaomi', 'oppo', 'realme', 'honor']
        found_brand = None
        for brand in brands:
            if brand in combined_text:
                found_brand = brand
                break

        # Extract model/product type
        words = name.split()[:3]  # Take first 3 words from name

        # Create focused query
        if found_brand:
            query_parts = [found_brand] + [word for word in words if word.lower() != found_brand]
        else:
            query_parts = words

        # Limit to 3-4 words maximum
        search_query = ' '.join(query_parts[:4])

        # Clean up the query
        search_query = search_query.replace('–', '').replace('-', ' ').strip()

        return search_query

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

            # Calculate similarity using a more focused approach
            search_text = self._create_search_query(name, description).lower()
            similarity = self.text_processor.calculate_similarity(listing_text.lower(), search_text)

            # Use a much lower threshold for Dubizzle since listings are more varied
            dubizzle_threshold = 0.15  # Much lower than the default 0.58
            logger.debug(f"Similarity score: {round(similarity, 2)} (threshold: {dubizzle_threshold})")

            # Also check if any key words from search query appear in listing
            search_words = search_text.split()
            listing_words = listing_text.lower().split()
            word_matches = sum(1 for word in search_words if any(word in listing_word for listing_word in listing_words))
            word_match_ratio = word_matches / len(search_words) if search_words else 0

            logger.debug(f"Word match ratio: {round(word_match_ratio, 2)} ({word_matches}/{len(search_words)} words)")

            # Accept if either similarity is good OR word match ratio is good
            if similarity < dubizzle_threshold and word_match_ratio < 0.5:
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
