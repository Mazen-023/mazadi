"""
Fallback estimation utilities.
"""

import logging
from .text_processing import TextProcessor
from ..config.estimation_config import EstimationConfig

logger = logging.getLogger('price_estimation')


class FallbackEstimator:
    """Provides fallback price estimation when scraping fails."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def estimate_dubizzle_fallback(self, name: str, description: str) -> str:
        """
        Fallback method when all Dubizzle scraping attempts fail.

        Instead of providing estimated prices, we return a clear message
        that no real price was found, following user preferences for
        no hardcoded fallback prices.
        """
        logger.info("All Dubizzle scraping attempts failed")

        # Extract brand and category for logging purposes only
        brand = self.text_processor.extract_brand(name, description, EstimationConfig.BRANDS)
        category = self.text_processor.extract_category(name, description, EstimationConfig.CATEGORIES)

        logger.info(f"Could not find real price for {brand} {category} on Dubizzle")

        # Return clear message instead of estimated price
        return "No price found on Dubizzle - website structure may have changed"
