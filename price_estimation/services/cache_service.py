"""
Caching service for price estimation.
"""

import hashlib
import logging
from datetime import timedelta
from typing import Dict, Optional
from decimal import Decimal

from django.utils import timezone
from ..models import PriceEstimationCache
from ..config.estimation_config import EstimationConfig

logger = logging.getLogger('price_estimation')


class CacheService:
    """Handles caching operations for price estimation."""
    
    def generate_cache_key(self, name: str, description: str) -> str:
        """Generate cache key for price estimation."""
        content = f"{name}_{description}".lower()
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_result(self, name: str, description: str) -> Optional[Dict]:
        """Get cached price estimation result."""
        cache_key = self.generate_cache_key(name, description)

        try:
            cache_entry = PriceEstimationCache.objects.get(
                cache_key=cache_key,
                expires_at__gt=timezone.now()
            )

            # Increment hit count
            cache_entry.increment_hit_count()

            return {
                'amazon_price': float(cache_entry.amazon_price) if cache_entry.amazon_price else None,
                'dubizzle_price': float(cache_entry.dubizzle_price) if cache_entry.dubizzle_price else None,
                'estimated_price': float(cache_entry.estimated_price) if cache_entry.estimated_price else None,
                'sources_used': cache_entry.sources_used,
                'estimation_date': cache_entry.created_at,
                'errors': cache_entry.estimation_errors,
                'cached': True
            }
        except PriceEstimationCache.DoesNotExist:
            return None

    def cache_result(self, name: str, description: str, result: Dict) -> None:
        """Cache price estimation result."""
        cache_key = self.generate_cache_key(name, description)
        expires_at = timezone.now() + timedelta(seconds=EstimationConfig.CACHE_TIMEOUT)

        try:
            # Update existing cache entry or create new one
            PriceEstimationCache.objects.update_or_create(
                cache_key=cache_key,
                defaults={
                    'estimated_price': self._safe_decimal_conversion(result['estimated_price']),
                    'amazon_price': self._safe_decimal_conversion(result['amazon_price']),
                    'dubizzle_price': self._safe_decimal_conversion(result['dubizzle_price']),
                    'sources_used': result['sources_used'],
                    'estimation_errors': result['errors'],
                    'expires_at': expires_at,
                }
            )

            logger.debug(f"Cached result for: {name}")

        except Exception as e:
            logger.error(f"Failed to cache result for {name}: {str(e)}")
            # Don't raise exception for caching failures

    def _safe_decimal_conversion(self, value):
        """Safely convert a value to Decimal, handling various edge cases."""
        if value is None:
            return None
        try:
            # Handle string values that might not be numeric
            if isinstance(value, str):
                # Remove any non-numeric characters except decimal point and minus
                cleaned_value = ''.join(c for c in value if c.isdigit() or c in '.-')
                if not cleaned_value or cleaned_value in ['.', '-', '.-']:
                    return None
                return Decimal(cleaned_value)
            else:
                return Decimal(str(value))
        except (ValueError, TypeError, Exception):
            return None
