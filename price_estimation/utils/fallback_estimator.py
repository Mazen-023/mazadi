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
    
    def estimate_dubizzle_fallback(self, name: str, description: str) -> float:
        """
        Fallback method when all Dubizzle scraping attempts fail.

        Since Dubizzle has changed their URL structure and search endpoints,
        we provide a graceful fallback that still adds value to users.
        """
        logger.info("Using fallback Dubizzle estimation method")

        # Try to provide a reasonable estimate based on product category and condition
        try:
            # Extract brand and category for basic estimation
            brand = self.text_processor.extract_brand(name, description, EstimationConfig.BRANDS)
            category = self.text_processor.extract_category(name, description, EstimationConfig.CATEGORIES)

            # Get price range
            category_prices = EstimationConfig.PRICE_RANGES.get(category, EstimationConfig.PRICE_RANGES['default'])
            brand_range = category_prices.get(brand, category_prices['default'])

            # Calculate middle price (used market typically 60-70% of new)
            min_price, max_price = brand_range
            if self.text_processor.is_used_item(description) or self.text_processor.is_used_item(name):
                estimated_price = (min_price + max_price) * 0.35  # 35% of average for used
            else:
                estimated_price = (min_price + max_price) * 0.5   # 50% of average for new

            logger.info(f"Fallback estimation: {estimated_price} EGP for {brand} {category}")
            return round(estimated_price, 2)

        except Exception as e:
            logger.error(f"Fallback estimation failed: {str(e)}")
            raise Exception("Dubizzle temporarily unavailable - using Amazon price only")
