"""
Search strategy utilities for price estimation.
"""

from typing import List
from .text_processing import TextProcessor
from ..config.estimation_config import EstimationConfig


class SearchStrategyGenerator:
    """Generates search strategies for different price estimation sources."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def generate_dubizzle_strategies(self, name: str, description: str) -> List[str]:
        """
        Prepare multiple search strategies with increasing simplicity.

        This approach tries different levels of detail to maximize success:
        1. Detailed search with key terms
        2. Brand + model only
        3. Brand + category only
        4. Just the main product name
        """
        strategies = []

        # Clean the inputs
        name_clean = self.text_processor.clean_search_text(name)
        description_clean = self.text_processor.clean_search_text(description)

        # Extract key information
        brand = self.text_processor.extract_brand(name_clean, description_clean, EstimationConfig.BRANDS)
        category = self.text_processor.extract_category(name_clean, description_clean, EstimationConfig.CATEGORIES)
        key_specs = self.text_processor.extract_key_specs(description_clean)

        # Determine if item is new or used for Arabic keyword enhancement
        is_used = self.text_processor.is_used_item(f"{name} {description}")
        condition_keyword = "" if is_used else " جديد"  # Add "new" in Arabic for new items

        # Strategy 1: Brand + key specs (most specific)
        if brand and key_specs:
            strategy1 = f"{brand} {' '.join(key_specs[:2])}{condition_keyword}"
            if len(strategy1) <= EstimationConfig.MAX_SEARCH_LENGTH:
                strategies.append(strategy1.lower())

        # Strategy 2: Brand + category
        if brand and category:
            strategy2 = f"{brand} {category}{condition_keyword}"
            if len(strategy2) <= EstimationConfig.MAX_SEARCH_LENGTH:
                strategies.append(strategy2.lower())

        # Strategy 3: Just brand + first word of name
        if brand:
            first_word = name_clean.split()[0] if name_clean.split() else ""
            if first_word and first_word.lower() != brand.lower():
                strategy3 = f"{brand} {first_word}{condition_keyword}"
                if len(strategy3) <= EstimationConfig.MAX_SEARCH_LENGTH:
                    strategies.append(strategy3.lower())

        # Strategy 4: Just the brand
        if brand:
            strategy4 = f"{brand}{condition_keyword}"
            if len(strategy4) <= EstimationConfig.MAX_SEARCH_LENGTH:
                strategies.append(strategy4.lower())

        # Strategy 5: First few words of name (fallback)
        name_words = name_clean.split()[:3]  # Max 3 words
        if name_words:
            fallback = f"{' '.join(name_words)}{condition_keyword}"
            if len(fallback) <= EstimationConfig.MAX_SEARCH_LENGTH:
                strategies.append(fallback.lower())

        # Remove duplicates while preserving order
        unique_strategies = []
        for strategy in strategies:
            if strategy not in unique_strategies:
                unique_strategies.append(strategy)

        return unique_strategies[:4]  # Max 4 strategies to avoid too many requests
