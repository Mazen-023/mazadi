"""
Amazon Egypt price estimator.
"""

import logging
import time
from typing import Union

from selenium.webdriver.common.by import By

from .base import BasePriceEstimator, PriceEstimationError
from ..utils.web_scraping import WebScrapingUtils
from ..config.estimation_config import EstimationConfig

logger = logging.getLogger('price_estimation')


class AmazonPriceEstimator(BasePriceEstimator):
    """Amazon Egypt price estimator using Selenium."""

    def estimate_price(self, name: str, description: str) -> Union[float, str]:
        """Estimate price from Amazon Egypt using Selenium."""
        import re
        
        search_query = f"{name} {description}".replace(" ", "+")
        url = f"https://www.amazon.eg/s?k={search_query}"
        
        logger.debug(f"Amazon URL: {url}")
        
        driver = None
        try:
            driver = WebScrapingUtils.get_webdriver()
            driver.get(url)
            time.sleep(2)  # Wait for page to load
            
            # Find price elements
            price_elements = driver.find_elements(By.CLASS_NAME, "a-price-whole")
            
            for price_element in price_elements:
                price_text = price_element.text.replace(",", "").strip()
                if re.match(r'^\d+', price_text):
                    price = float(price_text)
                    
                    # Apply discount for used items
                    if self.text_processor.is_used_item(description):
                        price *= EstimationConfig.USED_DISCOUNT_FACTOR
                    
                    return round(price, 2)
            
            return "No price found on Amazon"
            
        except Exception as e:
            logger.error(f"Amazon scraping error: {str(e)}")
            raise PriceEstimationError(f"Amazon estimation failed: {str(e)}")
        finally:
            if driver:
                driver.quit()
