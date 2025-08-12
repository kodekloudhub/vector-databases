#!/usr/bin/env python3
"""
Synthetic Data Generator for Vector Recommendation Engine POC

This script generates synthetic customer and product data with embeddings
and populates the DynamoDB tables.

Usage:
    python generate_synthetic_data.py --environment dev --region us-east-1
"""

import argparse
import boto3
import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    """Generate synthetic customer and product data with embeddings"""
    
    def __init__(self, environment: str = 'dev', region: str = 'us-east-1'):
        self.environment = environment
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        
        # Table names
        self.customer_table_name = f'CustomerEmbeddings-{environment}'
        self.product_table_name = f'ProductEmbeddings-{environment}'
        
        # Get table references
        self.customer_table = self.dynamodb.Table(self.customer_table_name)
        self.product_table = self.dynamodb.Table(self.product_table_name)
        
        # Data configuration
        self.num_customers = 1000
        self.num_products = 2000
        self.embedding_dimensions = 10
        
        # Product categories and their characteristics
        self.categories = {
            'Electronics': {
                'subcategories': ['Audio', 'Computers', 'Mobile', 'Gaming', 'Cameras'],
                'price_range': (50, 2000),
                'age_preference': (18, 50),
                'gender_neutral': True
            },
            'Clothing': {
                'subcategories': ['Men', 'Women', 'Kids', 'Shoes', 'Accessories'],
                'price_range': (20, 300),
                'age_preference': (16, 60),
                'gender_neutral': False
            },
            'Home & Garden': {
                'subcategories': ['Furniture', 'Kitchen', 'Decor', 'Tools', 'Garden'],
                'price_range': (15, 800),
                'age_preference': (25, 65),
                'gender_neutral': True
            },
            'Sports': {
                'subcategories': ['Fitness', 'Outdoor', 'Team Sports', 'Water Sports', 'Winter Sports'],
                'price_range': (25, 500),
                'age_preference': (16, 45),
                'gender_neutral': True
            },
            'Books': {
                'subcategories': ['Fiction', 'Non-Fiction', 'Educational', 'Children', 'Comics'],
                'price_range': (10, 50),
                'age_preference': (12, 70),
                'gender_neutral': True
            }
        }
        
        # Sample product names by category
        self.product_names = {
            'Electronics': [
                'Wireless Bluetooth Headphones', 'Smart Watch', 'Laptop Computer', 
                'Gaming Mouse', 'Digital Camera', 'Smartphone', 'Tablet', 'Speaker',
                'Keyboard', 'Monitor', 'Webcam', 'Power Bank', 'USB Cable', 'Router'
            ],
            'Clothing': [
                'Cotton T-Shirt', 'Jeans', 'Running Shoes', 'Dress', 'Jacket',
                'Sweater', 'Shorts', 'Sneakers', 'Hat', 'Scarf', 'Belt', 'Socks'
            ],
            'Home & Garden': [
                'Coffee Maker', 'Dining Table', 'Bed Sheets', 'Garden Hose',
                'Tool Set', 'Lamp', 'Cushion', 'Plant Pot', 'Kitchen Knife', 'Vacuum'
            ],
            'Sports': [
                'Yoga Mat', 'Dumbbells', 'Tennis Racket', 'Basketball', 'Bicycle',
                'Swimming Goggles', 'Running Shoes', 'Fitness Tracker', 'Water Bottle'
            ],
            'Books': [
                'Mystery Novel', 'Cookbook', 'Programming Guide', 'Children Story',
                'History Book', 'Science Fiction', 'Biography', 'Self-Help Book'
            ]
        }
        
        # Customer demographics
        self.locations = ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain']
        self.genders = ['M', 'F']
    
    def generate_customer_embedding(self, age: int, gender: str, preferences: List[str], 
                                  price_sensitivity: float) -> List[float]:
        """Generate a 10-dimensional customer embedding vector"""
        
        # Normalize age (0-1 scale, where 0=18, 1=65)
        age_normalized = max(0, min(1, (age - 18) / (65 - 18)))
        
        # Gender preference (0=M, 1=F)
        gender_pref = 1.0 if gender == 'F' else 0.0
        
        # Price sensitivity (already 0-1)
        price_sens = price_sensitivity
        
        # Category preferences (5 dimensions for 5 categories)
        category_prefs = [0.0] * 5
        category_list = list(self.categories.keys())
        
        for pref in preferences:
            if pref in category_list:
                idx = category_list.index(pref)
                category_prefs[idx] = random.uniform(0.7, 1.0)
        
        # Fill remaining categories with lower preferences
        for i, val in enumerate(category_prefs):
            if val == 0.0:
                category_prefs[i] = random.uniform(0.0, 0.3)
        
        # Brand loyalty factor
        brand_loyalty = random.uniform(0.0, 1.0)
        
        # Seasonal preference
        seasonal_pref = random.uniform(0.0, 1.0)
        
        # Combine all features
        embedding = [age_normalized, gender_pref, price_sens] + category_prefs + [brand_loyalty, seasonal_pref]
        
        # Add some noise for realism
        embedding = [max(0, min(1, x + random.gauss(0, 0.05))) for x in embedding]
        
        return embedding
    
    def generate_product_embedding(self, category: str, subcategory: str, price: float,
                                 target_age_range: tuple, target_gender: str) -> List[float]:
        """Generate a 10-dimensional product embedding vector"""
        
        # Target age group (normalized)
        avg_age = sum(target_age_range) / 2
        age_normalized = max(0, min(1, (avg_age - 18) / (65 - 18)))
        
        # Gender target (0=M, 1=F, 0.5=Unisex)
        if target_gender == 'M':
            gender_target = 0.0
        elif target_gender == 'F':
            gender_target = 1.0
        else:
            gender_target = 0.5
        
        # Price tier (normalized within category)
        cat_info = self.categories[category]
        min_price, max_price = cat_info['price_range']
        price_normalized = max(0, min(1, (price - min_price) / (max_price - min_price)))
        
        # Category encoding (5 dimensions)
        category_encoding = [0.0] * 5
        category_list = list(self.categories.keys())
        if category in category_list:
            idx = category_list.index(category)
            category_encoding[idx] = 1.0
        
        # Brand prestige score (random for synthetic data)
        brand_prestige = random.uniform(0.0, 1.0)
        
        # Seasonal relevance
        seasonal_relevance = random.uniform(0.0, 1.0)
        
        # Combine all features
        embedding = [age_normalized, gender_target, price_normalized] + category_encoding + [brand_prestige, seasonal_relevance]
        
        # Add some noise for realism
        embedding = [max(0, min(1, x + random.gauss(0, 0.03))) for x in embedding]
        
        return embedding
    
    def generate_customers(self) -> List[Dict]:
        """Generate synthetic customer data"""
        customers = []
        
        logger.info(f"Generating {self.num_customers} customers...")
        
        for i in range(1, self.num_customers + 1):
            customer_id = f"CUST_{i:03d}"
            
            # Generate demographics
            age = random.randint(18, 65)
            gender = random.choice(self.genders)
            location = random.choice(self.locations)
            
            # Generate preferences (1-3 categories)
            num_prefs = random.randint(1, 3)
            preferences = random.sample(list(self.categories.keys()), num_prefs)
            
            # Generate price sensitivity (0=budget, 1=premium)
            price_sensitivity = random.uniform(0.0, 1.0)
            
            # Generate signup date (within last 2 years)
            signup_date = datetime.now() - timedelta(days=random.randint(1, 730))
            
            # Generate embedding
            embedding = self.generate_customer_embedding(age, gender, preferences, price_sensitivity)
            
            customer = {
                'customer_id': customer_id,
                'embedding_vector': embedding,
                'customer_metadata': {
                    'age': age,
                    'gender': gender,
                    'location': location,
                    'preferences': preferences,
                    'price_sensitivity': price_sensitivity,
                    'signup_date': signup_date.isoformat()
                },
                'last_updated': datetime.now().isoformat()
            }
            
            customers.append(customer)
        
        logger.info(f"Generated {len(customers)} customers")
        return customers
    
    def generate_products(self) -> List[Dict]:
        """Generate synthetic product data"""
        products = []
        
        logger.info(f"Generating {self.num_products} products...")
        
        product_counter = 1
        
        for category, cat_info in self.categories.items():
            # Calculate products per category
            products_per_category = self.num_products // len(self.categories)
            
            for _ in range(products_per_category):
                product_id = f"PROD_{product_counter:03d}"
                product_counter += 1
                
                # Generate product details
                subcategory = random.choice(cat_info['subcategories'])
                base_name = random.choice(self.product_names[category])
                product_name = f"{base_name} - {subcategory}"
                
                # Generate price within category range
                min_price, max_price = cat_info['price_range']
                price = round(random.uniform(min_price, max_price), 2)
                
                # Generate target demographics
                age_min, age_max = cat_info['age_preference']
                target_age_range = (age_min, age_max)
                
                if cat_info['gender_neutral']:
                    target_gender = 'Unisex'
                else:
                    target_gender = random.choice(['M', 'F', 'Unisex'])
                
                # Generate other attributes
                brand = f"Brand{random.randint(1, 20)}"
                rating = round(random.uniform(3.0, 5.0), 1)
                in_stock = random.choice([True, True, True, False])  # 75% in stock
                
                # Generate embedding
                embedding = self.generate_product_embedding(
                    category, subcategory, price, target_age_range, target_gender
                )
                
                product = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'embedding_vector': embedding,
                    'product_metadata': {
                        'category': category,
                        'subcategory': subcategory,
                        'price': price,
                        'brand': brand,
                        'rating': rating,
                        'in_stock': in_stock,
                        'target_age_range': target_age_range,
                        'target_gender': target_gender
                    },
                    'last_updated': datetime.now().isoformat()
                }
                
                products.append(product)
        
        # Fill remaining slots if needed
        while len(products) < self.num_products:
            category = random.choice(list(self.categories.keys()))
            cat_info = self.categories[category]
            
            product_id = f"PROD_{product_counter:03d}"
            product_counter += 1
            
            subcategory = random.choice(cat_info['subcategories'])
            base_name = random.choice(self.product_names[category])
            product_name = f"{base_name} - {subcategory}"
            
            min_price, max_price = cat_info['price_range']
            price = round(random.uniform(min_price, max_price), 2)
            
            age_min, age_max = cat_info['age_preference']
            target_age_range = (age_min, age_max)
            
            if cat_info['gender_neutral']:
                target_gender = 'Unisex'
            else:
                target_gender = random.choice(['M', 'F', 'Unisex'])
            
            brand = f"Brand{random.randint(1, 20)}"
            rating = round(random.uniform(3.0, 5.0), 1)
            in_stock = random.choice([True, True, True, False])
            
            embedding = self.generate_product_embedding(
                category, subcategory, price, target_age_range, target_gender
            )
            
            product = {
                'product_id': product_id,
                'product_name': product_name,
                'embedding_vector': embedding,
                'product_metadata': {
                    'category': category,
                    'subcategory': subcategory,
                    'price': price,
                    'brand': brand,
                    'rating': rating,
                    'in_stock': in_stock,
                    'target_age_range': target_age_range,
                    'target_gender': target_gender
                },
                'last_updated': datetime.now().isoformat()
            }
            
            products.append(product)
        
        logger.info(f"Generated {len(products)} products")
        return products
    
    def batch_write_customers(self, customers: List[Dict]):
        """Write customers to DynamoDB in batches"""
        logger.info("Writing customers to DynamoDB...")
        
        batch_size = 25  # DynamoDB batch write limit
        
        for i in range(0, len(customers), batch_size):
            batch = customers[i:i + batch_size]
            
            with self.customer_table.batch_writer() as batch_writer:
                for customer in batch:
                    batch_writer.put_item(Item=customer)
            
            logger.info(f"Written {min(i + batch_size, len(customers))}/{len(customers)} customers")
        
        logger.info("✅ All customers written to DynamoDB")
    
    def batch_write_products(self, products: List[Dict]):
        """Write products to DynamoDB in batches"""
        logger.info("Writing products to DynamoDB...")
        
        batch_size = 25  # DynamoDB batch write limit
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            
            with self.product_table.batch_writer() as batch_writer:
                for product in batch:
                    batch_writer.put_item(Item=product)
            
            logger.info(f"Written {min(i + batch_size, len(products))}/{len(products)} products")
        
        logger.info("✅ All products written to DynamoDB")
    
    def generate_and_populate(self):
        """Generate synthetic data and populate DynamoDB tables"""
        logger.info("🚀 Starting synthetic data generation...")
        
        try:
            # Check if tables exist
            logger.info("Checking DynamoDB tables...")
            self.customer_table.load()
            self.product_table.load()
            logger.info("✅ DynamoDB tables found")
            
            # Generate data
            customers = self.generate_customers()
            products = self.generate_products()
            
            # Populate tables
            self.batch_write_customers(customers)
            self.batch_write_products(products)
            
            logger.info("🎉 Synthetic data generation completed successfully!")
            logger.info(f"Generated and stored:")
            logger.info(f"  - {len(customers)} customers")
            logger.info(f"  - {len(products)} products")
            
        except Exception as e:
            logger.error(f"❌ Error during data generation: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic data for Vector Recommendation Engine')
    parser.add_argument('--environment', '-e', default='dev', help='Environment (dev, staging, prod)')
    parser.add_argument('--region', '-r', default='us-east-1', help='AWS region')
    parser.add_argument('--customers', '-c', type=int, default=1000, help='Number of customers to generate')
    parser.add_argument('--products', '-p', type=int, default=2000, help='Number of products to generate')
    
    args = parser.parse_args()
    
    # Create generator
    generator = SyntheticDataGenerator(args.environment, args.region)
    generator.num_customers = args.customers
    generator.num_products = args.products
    
    # Generate and populate data
    generator.generate_and_populate()

if __name__ == "__main__":
    main()