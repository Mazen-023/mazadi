"""
Dubizzle-specific parsing utilities.
"""

import logging
import re
from typing import List, Optional

from bs4 import BeautifulSoup

from .text_processing import TextProcessor
from ..config.estimation_config import EstimationConfig

logger = logging.getLogger('price_estimation')


class DubizzleParser:
    """Handles parsing of Dubizzle pages and listings."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def extract_prices_from_page(self, html_content: str, name: str, description: str) -> List[float]:
        """Extract prices from Dubizzle page HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try multiple selectors for listings
        listings = (
            soup.find_all('article') or
            soup.find_all('div', class_='listing') or
            soup.find_all('div', class_='item') or
            soup.find_all('div', attrs={'data-testid': 'listing-card'})
        )

        logger.debug(f"Found {len(listings)} potential listings")
        
        prices = []
        for listing in listings[:20]:  # Limit to first 20 listings
            price = self._extract_price_from_listing(listing, name, description)
            if price:
                prices.append(price)

        logger.debug(f"Extracted {len(prices)} valid prices")
        return prices
    
    def _extract_price_from_listing(self, listing, name: str, description: str) -> Optional[float]:
        """Extract price from a Dubizzle listing if it matches the product."""
        # Try multiple selectors for title
        title_element = (
            listing.find('h2') or
            listing.find('h3') or
            listing.find('a', class_='title') or
            listing.find('div', class_='title') or
            listing.find('[data-testid="listing-title"]')
        )

        # Try multiple selectors for price
        price_element = (
            listing.find('span', class_="_1f2a2b47") or
            listing.find('span', class_='price') or
            listing.find('div', class_='price') or
            listing.find('[data-testid="listing-price"]') or
            listing.find('span', string=re.compile(r'\d+.*EGP|جنيه')) or
            listing.find('div', string=re.compile(r'\d+.*EGP|جنيه'))
        )

        # If we can't find both title and price, skip this listing
        if not title_element or not price_element:
            return None

        title = title_element.get_text().strip()
        logger.debug(f"Found listing title: {title[:50]}...")

        # Calculate similarity with a more lenient approach
        search_text = f"{name} {description}".lower()
        similarity = self.text_processor.calculate_similarity(title.lower(), search_text)

        logger.debug(f"Similarity score: {round(similarity, 2)} (threshold: {EstimationConfig.SIMILARITY_THRESHOLD})")

        if similarity >= EstimationConfig.SIMILARITY_THRESHOLD:
            logger.debug(f"Matched listing: {title} (Similarity: {round(similarity, 2)})")

            price_text = price_element.get_text().replace(",", "").strip()
            logger.debug(f"Price text: {price_text}")

            price = self.text_processor.extract_price_from_text(price_text)
            if price:
                logger.debug(f"Extracted price: {price}")
                return price

        return None
