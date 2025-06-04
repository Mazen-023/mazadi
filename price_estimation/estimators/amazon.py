"""
Amazon Egypt price estimator.
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


class AmazonPriceEstimator(BasePriceEstimator):
    """Amazon Egypt price estimator using Selenium."""

    def __init__(self):
        super().__init__()
        self.text_processor = TextProcessor()

    def estimate_price(self, name: str, description: str) -> Union[float, str]:
        """Estimate price from Amazon Egypt using Selenium."""
        # Create a focused search query (like Dubizzle)
        search_query = self._create_search_query(name, description)
        url = f"https://www.amazon.eg/s?k={search_query.replace(' ', '+')}"

        logger.debug(f"Amazon URL: {url}")

        driver = None
        try:
            driver = WebScrapingUtils.get_amazon_webdriver()
            driver.get(url)
            time.sleep(3)  # Wait for page to load

            # Extract prices from search results
            prices = self._extract_prices_from_page(driver, name, description)

            if prices:
                average_price = sum(prices) / len(prices)
                logger.info(f"Found {len(prices)} matching prices on Amazon")

                # Apply discount for used items
                if self.text_processor.is_used_item(description) or self.text_processor.is_used_item(name):
                    average_price *= EstimationConfig.USED_DISCOUNT_FACTOR

                return round(average_price, 2)

            return "No price found on Amazon"

        except Exception as e:
            logger.error(f"Amazon scraping error: {str(e)}")
            return f"Amazon estimation failed: {str(e)}"
        finally:
            if driver:
                driver.quit()

    def _create_search_query(self, name: str, description: str) -> str:
        """Create a focused search query for Amazon."""
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
        """Extract prices from Amazon search results page."""
        prices = []

        try:
            # Find product containers
            product_containers = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')

            if not product_containers:
                logger.warning("No product containers found on Amazon page")
                return prices

            logger.debug(f"Found {len(product_containers)} product containers")

            # Extract prices from each product
            for i, container in enumerate(product_containers[:15]):  # Limit to first 15 products
                try:
                    price = self._extract_price_from_product(container, name, description)
                    if price:
                        prices.append(price)
                        logger.debug(f"Extracted price {price} from product {i+1}")
                except Exception as e:
                    logger.debug(f"Failed to extract price from product {i+1}: {str(e)}")
                    continue

            logger.debug(f"Total prices extracted: {len(prices)}")
            return prices

        except Exception as e:
            logger.error(f"Error extracting prices from Amazon page: {str(e)}")
            return prices

    def _extract_price_from_product(self, container, name: str, description: str) -> float:
        """Extract price from a single Amazon product container."""
        try:
            # Get product title
            title_selectors = ['h2 a span', 'h2 span', '.a-size-base-plus', '.a-size-mini']
            title_text = ""

            for selector in title_selectors:
                try:
                    title_element = container.find_element(By.CSS_SELECTOR, selector)
                    title_text = title_element.text.strip()
                    if title_text:
                        break
                except:
                    continue

            if not title_text:
                return None

            logger.debug(f"Found product title: {title_text[:50]}...")

            # Calculate similarity
            search_text = self._create_search_query(name, description).lower()
            similarity = self.text_processor.calculate_similarity(title_text.lower(), search_text)

            # Use a lower threshold for Amazon (similar to Dubizzle)
            amazon_threshold = 0.15
            logger.debug(f"Similarity score: {round(similarity, 2)} (threshold: {amazon_threshold})")

            if similarity < amazon_threshold:
                return None

            logger.debug(f"Matched product with similarity {round(similarity, 2)}")

            # Find price element
            price_selectors = ['.a-price-whole', '.a-price .a-offscreen', '.a-price-range .a-price .a-offscreen']

            for selector in price_selectors:
                try:
                    price_element = container.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_element.text.strip()

                    if price_text:
                        # Extract price using text processor
                        price = self.text_processor.extract_price_from_text(price_text)
                        if price:
                            logger.debug(f"Extracted price: {price}")
                            return price
                except:
                    continue

            return None

        except Exception as e:
            logger.debug(f"Error extracting price from product: {str(e)}")
            return None
