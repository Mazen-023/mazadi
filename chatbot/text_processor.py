import string
import re
import logging
from typing import List

# Try to import optional dependencies
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

logger = logging.getLogger(__name__)


class TextProcessor:
    """Handles text processing and semantic similarity calculations"""

    def __init__(self, sentence_model=None):
        self.sentence_model = sentence_model
        self.stopwords = self.get_stopwords()

    def get_stopwords(self):
        """Get stopwords with fallback"""
        try:
            if NLTK_AVAILABLE:
                english_stops = set(stopwords.words('english'))
                try:
                    arabic_stops = set(stopwords.words('arabic'))
                    return english_stops.union(arabic_stops)
                except:
                    return english_stops
            else:
                # Fallback stopwords
                return {
                    'the', 'a', 'an', 'in', 'on', 'at', 'and', 'or', 'is', 'are', 'was', 'were',
                    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                    'would', 'could', 'should', 'may', 'might', 'must', 'can', 'to', 'of', 'for',
                    'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
                    'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these', 'those'
                }
        except Exception as e:
            logger.warning(f"Error loading stopwords: {e}")
            return set()

    def tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into words"""
        try:
            if NLTK_AVAILABLE:
                return word_tokenize(text.lower())
            else:
                # Fallback tokenization
                text = text.lower()
                # Remove punctuation
                for p in string.punctuation:
                    text = text.replace(p, ' ')
                return text.split()
        except Exception as e:
            logger.warning(f"Error tokenizing text: {e}")
            # Simple fallback
            text = text.lower()
            for p in string.punctuation:
                text = text.replace(p, ' ')
            return text.split()

    def preprocess_text(self, text: str) -> str:
        """Preprocess text by removing stopwords and cleaning"""
        try:
            # Basic cleaning
            text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)  # Keep Arabic and English chars
            text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace

            # Tokenize
            tokens = self.tokenize_text(text)

            # Remove stopwords
            filtered_tokens = [token for token in tokens if token not in self.stopwords and len(token) > 1]

            return ' '.join(filtered_tokens)
        except Exception as e:
            logger.warning(f"Error preprocessing text: {e}")
            return text.lower().strip()

    def get_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        try:
            if not self.sentence_model or not SKLEARN_AVAILABLE:
                return self.simple_similarity(text1, text2)

            # Use sentence transformer for semantic similarity
            embeddings = self.sentence_model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)

        except Exception as e:
            logger.warning(f"Error calculating semantic similarity: {e}")
            return self.simple_similarity(text1, text2)

    def simple_similarity(self, text1: str, text2: str) -> float:
        """Simple word-based similarity as fallback"""
        try:
            words1 = set(self.preprocess_text(text1).split())
            words2 = set(self.preprocess_text(text2).split())

            if not words1 or not words2:
                return 0.0

            intersection = words1.intersection(words2)
            union = words1.union(words2)

            return len(intersection) / len(union) if union else 0.0

        except Exception as e:
            logger.warning(f"Error calculating simple similarity: {e}")
            return 0.0

    def detect_language(self, text: str) -> str:
        """Detect if text is Arabic or English"""
        try:
            # Count Arabic characters
            arabic_chars = set('ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوي')
            arabic_count = sum(1 for char in text if char in arabic_chars)

            # Count English characters
            english_count = sum(1 for char in text if char.isascii() and char.isalpha())

            total_chars = arabic_count + english_count

            if total_chars == 0:
                return 'en'  # Default to English

            arabic_ratio = arabic_count / total_chars

            return 'ar' if arabic_ratio > 0.3 else 'en'

        except Exception as e:
            logger.warning(f"Error detecting language: {e}")
            return 'en'  # Default to English

    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract important keywords from text"""
        try:
            processed_text = self.preprocess_text(text)
            words = processed_text.split()

            # Simple keyword extraction based on word length and frequency
            word_freq = {}
            for word in words:
                if len(word) > 2:  # Only consider words longer than 2 characters
                    word_freq[word] = word_freq.get(word, 0) + 1

            # Sort by frequency and word length
            keywords = sorted(word_freq.keys(),
                            key=lambda x: (word_freq[x], len(x)),
                            reverse=True)

            return keywords[:max_keywords]

        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return []
