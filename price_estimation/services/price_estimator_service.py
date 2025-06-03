"""
Main price estimation service orchestrator.

This is the main entry point for price estimation functionality.
"""

import logging
from typing import Dict, Optional, Union

from django.utils import timezone
from ..estimators.amazon import AmazonPriceEstimator
from ..estimators.dubizzle import DubizzlePriceEstimator
from .cache_service import CacheService

logger = logging.getLogger('price_estimation')


class PriceEstimatorService:
    """
    Main service class for price estimation following Django best practices.
    
    This service:
    - Uses dependency injection for estimators
    - Implements caching to avoid repeated requests
    - Follows DRY principles
    - Provides comprehensive error handling
    """

    def __init__(self):
        self.estimators = {
            'amazon': AmazonPriceEstimator(),
            'dubizzle': DubizzlePriceEstimator(),
        }
        self.cache_service = CacheService()
    
    def estimate_price(self, name: str, description: str, use_cache: bool = True) -> Dict[str, Union[float, str, None]]:
        """
        Main method to estimate price from multiple sources.
        
        Args:
            name: Product name
            description: Product description
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing price estimates and metadata
        """
        logger.info(f"Starting price estimation for: {name}")
        
        # Check cache first if enabled
        if use_cache:
            cached_result = self.cache_service.get_cached_result(name, description)
            if cached_result:
                logger.info(f"Returning cached result for: {name}")
                return cached_result
        
        result = {
            'amazon_price': None,
            'dubizzle_price': None,
            'estimated_price': None,
            'sources_used': [],
            'estimation_date': timezone.now(),
            'errors': []
        }
        
        # Get prices from all estimators
        for source_name, estimator in self.estimators.items():
            try:
                price = estimator.estimate_price(name, description)
                if isinstance(price, (int, float)):
                    result[f'{source_name}_price'] = float(price)
                    result['sources_used'].append(source_name)
                else:
                    result['errors'].append(f"{source_name}: {price}")
            except Exception as e:
                logger.error(f"{source_name} price estimation failed: {str(e)}")
                result['errors'].append(f"{source_name}: {str(e)}")
        
        # Calculate final estimate
        result['estimated_price'] = self._calculate_final_estimate(
            result['amazon_price'],
            result['dubizzle_price']
        )
        
        # Cache the result if caching is enabled
        if use_cache:
            self.cache_service.cache_result(name, description, result)

        logger.info(f"Price estimation completed for: {name}. Estimated price: {result['estimated_price']}")
        return result

    def _calculate_final_estimate(self, amazon_price: Optional[float], dubizzle_price: Optional[float]) -> Optional[float]:
        """Calculate final price estimate from available sources."""
        if amazon_price and dubizzle_price:
            return round((amazon_price + dubizzle_price) / 2, 2)
        elif amazon_price:
            return amazon_price
        elif dubizzle_price:
            return dubizzle_price
        return None
