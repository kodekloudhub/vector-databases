"""
Configuration settings for Bedrock-Streamlit Recommendation System
"""

import os
from typing import Dict, Any

# AWS Bedrock Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Bedrock Model Configuration
EMBEDDING_MODEL_ID = 'amazon.titan-embed-text-v1'
TEXT_MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'

# Application Settings
MAX_RECOMMENDATIONS = 5
SIMILARITY_THRESHOLD = 0.3
DEFAULT_FALLBACK_COUNT = 5
CACHE_EMBEDDINGS = True

# Data Paths
DATA_DIR = 'data'
CUSTOMERS_FILE = f'{DATA_DIR}/customers.json'
PRODUCTS_FILE = f'{DATA_DIR}/products.json'
DEFAULTS_FILE = f'{DATA_DIR}/defaults.json'

# Streamlit Configuration
STREAMLIT_CONFIG = {
    'page_title': '🛍️ AI-Powered Recommendation System',
    'page_icon': '🛍️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Customer Demographics for UAE
UAE_LOCATIONS = [
    'Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 
    'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain'
]

PRODUCT_CATEGORIES = {
    'Electronics': {
        'subcategories': ['Audio', 'Computers', 'Mobile', 'Gaming', 'Cameras', 'Smart Home'],
        'price_range': (50, 2000),
        'age_preference': (18, 50),
        'gender_neutral': True
    },
    'Clothing': {
        'subcategories': ['Men', 'Women', 'Kids', 'Shoes', 'Accessories', 'Sportswear'],
        'price_range': (20, 500),
        'age_preference': (16, 60),
        'gender_neutral': False
    },
    'Home & Garden': {
        'subcategories': ['Furniture', 'Kitchen', 'Decor', 'Tools', 'Garden', 'Storage'],
        'price_range': (15, 1000),
        'age_preference': (25, 65),
        'gender_neutral': True
    }
}

# Default Recommendations Configuration
DEFAULT_RECOMMENDATIONS_CONFIG = {
    'popular_threshold': 0.8,
    'new_customer_fallback': True,
    'category_based_fallback': True,
    'seasonal_adjustment': True
}

# Bedrock API Configuration
BEDROCK_CONFIG = {
    'max_retries': 3,
    'retry_delay': 1,
    'timeout': 30,
    'embedding_dimensions': 1536  # Titan Embeddings G1 - Text output dimension
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/recommendation_system.log'
}

def get_bedrock_config() -> Dict[str, Any]:
    """Get Bedrock client configuration"""
    return {
        'region_name': AWS_REGION,
        'aws_access_key_id': AWS_ACCESS_KEY_ID,
        'aws_secret_access_key': AWS_SECRET_ACCESS_KEY
    }

def validate_config() -> bool:
    """Validate configuration settings"""
    required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    
    for var in required_env_vars:
        if not os.getenv(var):
            print(f"Warning: {var} environment variable not set")
            return False
    
    return True

# Sample customer profiles for generation
SAMPLE_CUSTOMER_PROFILES = [
    {
        'age_range': (22, 28),
        'gender': 'F',
        'location': 'Dubai',
        'preferences': ['Electronics', 'Clothing'],
        'price_sensitivity': 0.6,
        'lifestyle': 'Young Professional'
    },
    {
        'age_range': (30, 40),
        'gender': 'M',
        'location': 'Abu Dhabi',
        'preferences': ['Electronics', 'Home & Garden'],
        'price_sensitivity': 0.3,
        'lifestyle': 'Family Man'
    },
    {
        'age_range': (25, 35),
        'gender': 'F',
        'location': 'Sharjah',
        'preferences': ['Clothing', 'Home & Garden'],
        'price_sensitivity': 0.7,
        'lifestyle': 'Homemaker'
    }
]