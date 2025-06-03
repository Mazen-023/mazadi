"""
Text processing utilities for price estimation.

Contains functions for text cleaning, similarity calculation, and data extraction.
"""

import re
import difflib
from typing import List


class TextProcessor:
    """Utility class for text processing operations."""
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity score between two texts."""
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    @staticmethod
    def is_used_item(text: str) -> bool:
        """
        Enhanced condition detection with Arabic support.
        
        Detects various ways to express 'used' condition in both English and Arabic.
        """
        text_lower = text.lower()
        
        # English used indicators
        used_english = ["used", "second hand", "pre-owned", "refurbished", "open box"]
        
        # Arabic used indicators
        used_arabic = ["مستعمل", "مستخدم", "مستعمله", "ثاني هاند", "مفتوح"]
        
        # Check English terms
        for term in used_english:
            if term in text_lower:
                return True
        
        # Check Arabic terms (case-sensitive for Arabic)
        for term in used_arabic:
            if term in text:
                return True
        
        return False
    
    @staticmethod
    def clean_search_text(text: str) -> str:
        """Clean text for URL-safe search terms."""
        # Remove newlines and extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that cause URL issues
        text = re.sub(r'[^\w\s\u0600-\u06FF-]', ' ', text)  # Keep Arabic, alphanumeric, spaces, hyphens
        
        # Remove model numbers and technical specs that are too specific
        text = re.sub(r'\b[A-Z0-9]{5,}\b', '', text)  # Remove long alphanumeric codes
        text = re.sub(r'\[[^\]]*\]', '', text)  # Remove content in brackets
        text = re.sub(r'\([^)]*\)', '', text)  # Remove content in parentheses
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_brand(name: str, description: str, brands: List[str]) -> str:
        """Extract brand name from product name or description."""
        text = f"{name} {description}".lower()
        for brand in brands:
            if brand in text:
                return brand
        return ""
    
    @staticmethod
    def extract_category(name: str, description: str, categories: dict) -> str:
        """Extract product category from name or description."""
        text = f"{name} {description}".lower()
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        return ""
    
    @staticmethod
    def extract_key_specs(text: str) -> List[str]:
        """Extract key specifications like size, storage, etc."""
        specs = []
        text_lower = text.lower()
        
        # Extract sizes (inches, GB, TB, etc.)
        sizes = re.findall(r'\b\d+(?:inch|gb|tb|hz)\b', text_lower)
        specs.extend(sizes[:2])  # Max 2 size specs
        
        # Extract standalone numbers that might be important
        numbers = re.findall(r'\b\d{1,3}\b', text_lower)
        specs.extend(numbers[:1])  # Max 1 standalone number
        
        return specs[:3]  # Max 3 specs total
    
    @staticmethod
    def extract_price_from_text(price_text: str) -> float:
        """Extract price from text using multiple patterns."""
        price_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:EGP|جنيه|LE|L\.E\.)',  # With currency
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Just numbers
            r'(\d+(?:\.\d{3})*(?:,\d{2})?)',  # European format
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, price_text)
            if price_match:
                try:
                    price_str = price_match.group(1).replace(",", "")
                    price = float(price_str)
                    if 100 <= price <= 1000000:  # Reasonable price range
                        return price
                except ValueError:
                    continue
        
        return None
