"""
Dubizzle Egypt price estimator.
"""

import logging
from typing import Union

import requests

from .base import BasePriceEstimator
from ..utils.web_scraping import WebScrapingUtils
from ..utils.search_strategies import SearchStrategyGenerator
from ..utils.dubizzle_parser import DubizzleParser
from ..utils.fallback_estimator import FallbackEstimator

logger = logging.getLogger('price_estimation')


class DubizzlePriceEstimator(BasePriceEstimator):
    """
    Dubizzle Egypt price estimator using requests.

    This estimator is more challenging than Amazon because:
    - User-generated content with inconsistent formats
    - URL length and character sensitivity
    - Heavy Arabic content mixing
    - More aggressive anti-bot measures
    """
    
    def __init__(self):
        super().__init__()
        self.strategy_generator = SearchStrategyGenerator()
        self.parser = DubizzleParser()
        self.fallback_estimator = FallbackEstimator()

    def estimate_price(self, name: str, description: str) -> Union[float, str]:
        """Estimate price from Dubizzle Egypt using requests."""
        # Prepare multiple search strategies with increasing simplicity
        search_strategies = self.strategy_generator.generate_dubizzle_strategies(name, description)

        for search_terms in search_strategies:
            urls_to_try = WebScrapingUtils.generate_dubizzle_urls(search_terms)
            
            for url in urls_to_try:
                try:
                    logger.debug(f"Trying Dubizzle URL: {url}")
                    
                    response = self.session.get(
                        url, 
                        headers=WebScrapingUtils.get_dubizzle_headers(), 
                        timeout=15
                    )

                    if response.status_code == 200:
                        prices = self.parser.extract_prices_from_page(response.text, name, description)
                        if prices:
                            average_price = sum(prices) / len(prices)
                            logger.info(f"Found {len(prices)} matching prices on Dubizzle")
                            return round(average_price, 2)
                    else:
                        logger.warning(f"Dubizzle returned status {response.status_code} for URL: {url}")
                        continue

                except requests.exceptions.RequestException as e:
                    logger.warning(f"Dubizzle request failed for URL {url}: {str(e)}")
                    continue
                except Exception as e:
                    logger.warning(f"Dubizzle parsing failed for URL {url}: {str(e)}")
                    continue

        # If all URLs failed, try a simple fallback approach
        logger.warning("All Dubizzle URL strategies failed, trying fallback approach")
        try:
            return self.fallback_estimator.estimate_dubizzle_fallback(name, description)
        except Exception as e:
            return str(e)
