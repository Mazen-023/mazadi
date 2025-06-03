"""
Configuration data for price estimation.

Contains brands, categories, price ranges, and other configuration data.
"""


class EstimationConfig:
    """Configuration class for price estimation data."""
    
    # Common electronics brands in Egyptian market
    BRANDS = [
        'samsung', 'apple', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'sony', 'lg',
        'huawei', 'xiaomi', 'oppo', 'vivo', 'nokia', 'intel', 'amd', 'nvidia',
        'microsoft', 'google', 'canon', 'nikon', 'bose', 'jbl', 'beats',
        'logitech', 'razer', 'corsair', 'steelseries', 'hyperx'
    ]
    
    # Product categories with keywords
    CATEGORIES = {
        'laptop': ['laptop', 'notebook', 'macbook'],
        'phone': ['phone', 'iphone', 'smartphone', 'mobile'],
        'tablet': ['tablet', 'ipad'],
        'monitor': ['monitor', 'screen', 'display', 'شاشة'],
        'keyboard': ['keyboard', 'كيبورد'],
        'mouse': ['mouse', 'ماوس'],
        'headphones': ['headphones', 'earphones', 'headset'],
        'speaker': ['speaker', 'speakers'],
        'camera': ['camera', 'كاميرا'],
        'tv': ['tv', 'television', 'smart tv']
    }
    
    # Basic price ranges for Egyptian market (in EGP)
    PRICE_RANGES = {
        'phone': {
            'samsung': (3000, 25000), 
            'apple': (15000, 50000), 
            'xiaomi': (2000, 15000), 
            'default': (1500, 20000)
        },
        'laptop': {
            'dell': (15000, 60000), 
            'hp': (12000, 50000), 
            'lenovo': (10000, 45000), 
            'default': (8000, 40000)
        },
        'tablet': {
            'apple': (12000, 35000), 
            'samsung': (8000, 25000), 
            'default': (5000, 20000)
        },
        'monitor': {
            'samsung': (5000, 25000), 
            'lg': (4000, 20000), 
            'default': (3000, 15000)
        },
        'tv': {
            'samsung': (8000, 50000), 
            'lg': (7000, 40000), 
            'default': (5000, 30000)
        },
        'default': {
            'default': (1000, 10000)
        }
    }
    
    # Constants
    USED_DISCOUNT_FACTOR = 0.8
    SIMILARITY_THRESHOLD = 0.58
    MAX_SEARCH_LENGTH = 50
    CACHE_TIMEOUT = 3600  # 1 hour in seconds
