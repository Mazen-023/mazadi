"""
Base price estimator class.
"""

from typing import Union
from ..utils.web_scraping import WebScrapingUtils
from ..utils.text_processing import TextProcessor


class PriceEstimationError(Exception):
    """Custom exception for price estimation errors."""
    pass


class BasePriceEstimator:
    """
    Base class for price estimators following DRY principles.
    
    This abstract base class defines the common interface and
    shared functionality for all price estimation sources.
    """

    def __init__(self):
        self.session = WebScrapingUtils.create_session()
        self.text_processor = TextProcessor()

    def estimate_price(self, name: str, description: str) -> Union[float, str]:
        """Abstract method to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement estimate_price method")
