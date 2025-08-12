"""
Data management for local JSON storage
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd

from config import CUSTOMERS_FILE, PRODUCTS_FILE, DEFAULTS_FILE, DATA_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    """Manages local JSON data storage for customers, products, and defaults"""
    
    def __init__(self):
        """Initialize data manager and ensure data directory exists"""
        self.customers_file = CUSTOMERS_FILE
        self.products_file = PRODUCTS_FILE
        self.defaults_file = DEFAULTS_FILE
        
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Initialize empty files if they don't exist
        self._initialize_data_files()
        
        logger.info("Data manager initialized")
    
    def _initialize_data_files(self):
        """Initialize empty data files if they don't exist"""
        files_to_init = [
            (self.customers_file, {}),
            (self.products_file, {}),
            (self.defaults_file, {
                "popular_products": [],
                "category_defaults": {},
                "new_customer_recommendations": []
            })
        ]
        
        for file_path, default_content in files_to_init:
            if not os.path.exists(file_path):
                self._save_json(file_path, default_content)
                logger.info(f"Initialized {file_path}")
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return {}
    
    def _save_json(self, file_path: str, data: Dict[str, Any]):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved data to {file_path}")
        except Exception as e:
            logger.error(f"Error saving to {file_path}: {str(e)}")
            raise
    
    # Customer data methods
    def load_customers(self) -> Dict[str, Dict[str, Any]]:
        """Load all customer data"""
        return self._load_json(self.customers_file)
    
    def save_customers(self, customers: Dict[str, Dict[str, Any]]):
        """Save customer data"""
        self._save_json(self.customers_file, customers)
    
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get specific customer data"""
        customers = self.load_customers()
        return customers.get(customer_id)
    
    def add_customer(self, customer_id: str, customer_data: Dict[str, Any]):
        """Add or update customer data"""
        customers = self.load_customers()
        customer_data['last_updated'] = datetime.now().isoformat()
        customers[customer_id] = customer_data
        self.save_customers(customers)
        logger.info(f"Added/updated customer: {customer_id}")
    
    def get_customer_list(self) -> List[str]:
        """Get list of all customer IDs"""
        customers = self.load_customers()
        return list(customers.keys())
    
    # Product data methods
    def load_products(self) -> Dict[str, Dict[str, Any]]:
        """Load all product data"""
        return self._load_json(self.products_file)
    
    def save_products(self, products: Dict[str, Dict[str, Any]]):
        """Save product data"""
        self._save_json(self.products_file, products)
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get specific product data"""
        products = self.load_products()
        return products.get(product_id)
    
    def add_product(self, product_id: str, product_data: Dict[str, Any]):
        """Add or update product data"""
        products = self.load_products()
        product_data['last_updated'] = datetime.now().isoformat()
        products[product_id] = product_data
        self.save_products(products)
        logger.info(f"Added/updated product: {product_id}")
    
    def get_products_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get products filtered by category"""
        products = self.load_products()
        return {
            pid: pdata for pid, pdata in products.items()
            if pdata.get('category') == category
        }
    
    def get_product_list(self) -> List[str]:
        """Get list of all product IDs"""
        products = self.load_products()
        return list(products.keys())
    
    # Default recommendations methods
    def load_defaults(self) -> Dict[str, Any]:
        """Load default recommendations"""
        return self._load_json(self.defaults_file)
    
    def save_defaults(self, defaults: Dict[str, Any]):
        """Save default recommendations"""
        self._save_json(self.defaults_file, defaults)
    
    def get_popular_products(self) -> List[Dict[str, Any]]:
        """Get popular products for default recommendations"""
        defaults = self.load_defaults()
        return defaults.get('popular_products', [])
    
    def get_category_defaults(self, category: str) -> List[str]:
        """Get default product IDs for a category"""
        defaults = self.load_defaults()
        category_defaults = defaults.get('category_defaults', {})
        return category_defaults.get(category, [])
    
    def get_new_customer_recommendations(self) -> List[Dict[str, Any]]:
        """Get default recommendations for new customers"""
        defaults = self.load_defaults()
        return defaults.get('new_customer_recommendations', [])
    
    # Analytics and utility methods
    def get_customer_analytics(self) -> Dict[str, Any]:
        """Get analytics data about customers"""
        customers = self.load_customers()
        
        if not customers:
            return {}
        
        # Convert to DataFrame for analysis
        customer_data = []
        for cid, cdata in customers.items():
            metadata = cdata.get('customer_metadata', {})
            customer_data.append({
                'customer_id': cid,
                'age': metadata.get('age', 0),
                'gender': metadata.get('gender', 'Unknown'),
                'location': metadata.get('location', 'Unknown'),
                'preferences': metadata.get('preferences', []),
                'price_sensitivity': metadata.get('price_sensitivity', 0.5)
            })
        
        df = pd.DataFrame(customer_data)
        
        analytics = {
            'total_customers': len(customers),
            'age_distribution': df['age'].describe().to_dict() if not df.empty else {},
            'gender_distribution': df['gender'].value_counts().to_dict() if not df.empty else {},
            'location_distribution': df['location'].value_counts().to_dict() if not df.empty else {},
            'avg_price_sensitivity': df['price_sensitivity'].mean() if not df.empty else 0
        }
        
        # Most popular preferences
        all_preferences = []
        for prefs in df['preferences']:
            if isinstance(prefs, list):
                all_preferences.extend(prefs)
        
        if all_preferences:
            pref_counts = pd.Series(all_preferences).value_counts()
            analytics['popular_preferences'] = pref_counts.to_dict()
        
        return analytics
    
    def get_product_analytics(self) -> Dict[str, Any]:
        """Get analytics data about products"""
        products = self.load_products()
        
        if not products:
            return {}
        
        # Convert to DataFrame for analysis
        product_data = []
        for pid, pdata in products.items():
            product_data.append({
                'product_id': pid,
                'product_name': pdata.get('product_name', 'Unknown'),
                'category': pdata.get('category', 'Unknown'),
                'subcategory': pdata.get('subcategory', 'Unknown'),
                'price': pdata.get('price', 0),
                'brand': pdata.get('brand', 'Unknown'),
                'rating': pdata.get('rating', 0),
                'in_stock': pdata.get('in_stock', True)
            })
        
        df = pd.DataFrame(product_data)
        
        analytics = {
            'total_products': len(products),
            'category_distribution': df['category'].value_counts().to_dict() if not df.empty else {},
            'price_distribution': df['price'].describe().to_dict() if not df.empty else {},
            'avg_rating': df['rating'].mean() if not df.empty else 0,
            'in_stock_count': df['in_stock'].sum() if not df.empty else 0,
            'brand_distribution': df['brand'].value_counts().head(10).to_dict() if not df.empty else {}
        }
        
        return analytics
    
    def backup_data(self, backup_dir: str = 'backups'):
        """Create backup of all data files"""
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        files_to_backup = [
            (self.customers_file, f'customers_{timestamp}.json'),
            (self.products_file, f'products_{timestamp}.json'),
            (self.defaults_file, f'defaults_{timestamp}.json')
        ]
        
        for source_file, backup_name in files_to_backup:
            if os.path.exists(source_file):
                backup_path = os.path.join(backup_dir, backup_name)
                with open(source_file, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                logger.info(f"Backed up {source_file} to {backup_path}")
    
    def validate_data_integrity(self) -> Dict[str, bool]:
        """Validate data integrity across all files"""
        results = {}
        
        # Validate customers
        try:
            customers = self.load_customers()
            results['customers_valid'] = all(
                'customer_id' in cdata and 'embedding_vector' in cdata
                for cdata in customers.values()
            )
        except Exception:
            results['customers_valid'] = False
        
        # Validate products
        try:
            products = self.load_products()
            results['products_valid'] = all(
                'product_id' in pdata and 'product_name' in pdata and 'embedding_vector' in pdata
                for pdata in products.values()
            )
        except Exception:
            results['products_valid'] = False
        
        # Validate defaults
        try:
            defaults = self.load_defaults()
            required_keys = ['popular_products', 'category_defaults', 'new_customer_recommendations']
            results['defaults_valid'] = all(key in defaults for key in required_keys)
        except Exception:
            results['defaults_valid'] = False
        
        return results
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all data"""
        customers = self.load_customers()
        products = self.load_products()
        defaults = self.load_defaults()
        
        return {
            'customers_count': len(customers),
            'products_count': len(products),
            'popular_products_count': len(defaults.get('popular_products', [])),
            'categories_with_defaults': len(defaults.get('category_defaults', {})),
            'new_customer_recommendations_count': len(defaults.get('new_customer_recommendations', [])),
            'data_integrity': self.validate_data_integrity()
        }