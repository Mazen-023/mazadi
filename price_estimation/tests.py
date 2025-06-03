"""
Tests for price estimation app following Django best practices.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from .services import PriceEstimatorService

User = get_user_model()


class PriceEstimatorServiceTest(TestCase):
    """Test cases for PriceEstimatorService."""

    def setUp(self):
        """Set up test data."""
        self.service = PriceEstimatorService()
        self.test_name = "iPhone 15"
        self.test_description = "128GB, excellent condition"

    @patch('price_estimation.services.AmazonPriceEstimator.estimate_price')
    @patch('price_estimation.services.DubizzlePriceEstimator.estimate_price')
    def test_estimate_price_success(self, mock_dubizzle, mock_amazon):
        """Test successful price estimation from both sources."""
        # Mock return values
        mock_amazon.return_value = 25000.0
        mock_dubizzle.return_value = 23000.0

        result = self.service.estimate_price(self.test_name, self.test_description, use_cache=False)

        self.assertEqual(result['amazon_price'], 25000.0)
        self.assertEqual(result['dubizzle_price'], 23000.0)
        self.assertEqual(result['estimated_price'], 24000.0)  # Average
        self.assertEqual(result['sources_used'], ['amazon', 'dubizzle'])
        self.assertEqual(len(result['errors']), 0)
