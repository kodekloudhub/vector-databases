"""
Generate initial data for the Bedrock-Streamlit recommendation system
Creates 20 diverse customer profiles and comprehensive product catalog
"""

import json
import random
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import UAE_LOCATIONS, PRODUCT_CATEGORIES
from data_manager import DataManager
from bedrock_client import BedrockClient

class InitialDataGenerator:
    """Generate initial customer and product data"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.bedrock_client = None  # Will initialize when needed
        
        # Customer profiles for diverse UAE demographics
        self.customer_templates = [
            {
                'name': 'Ahmed Al Mansouri',
                'age': 32,
                'gender': 'M',
                'location': 'Dubai',
                'preferences': ['Electronics', 'Home & Garden'],
                'price_sensitivity': 0.3,
                'lifestyle': 'Tech Executive',
                'occupation': 'Software Engineer'
            },
            {
                'name': 'Fatima Al Zahra',
                'age': 28,
                'gender': 'F',
                'location': 'Abu Dhabi',
                'preferences': ['Clothing', 'Electronics'],
                'price_sensitivity': 0.6,
                'lifestyle': 'Young Professional',
                'occupation': 'Marketing Manager'
            },
            {
                'name': 'Mohammed bin Rashid',
                'age': 45,
                'gender': 'M',
                'location': 'Sharjah',
                'preferences': ['Home & Garden', 'Electronics'],
                'price_sensitivity': 0.2,
                'lifestyle': 'Family Man',
                'occupation': 'Business Owner'
            },
            {
                'name': 'Aisha Al Qasimi',
                'age': 35,
                'gender': 'F',
                'location': 'Dubai',
                'preferences': ['Clothing', 'Home & Garden'],
                'price_sensitivity': 0.4,
                'lifestyle': 'Working Mother',
                'occupation': 'Doctor'
            },
            {
                'name': 'Omar Al Maktoum',
                'age': 26,
                'gender': 'M',
                'location': 'Dubai',
                'preferences': ['Electronics', 'Clothing'],
                'price_sensitivity': 0.7,
                'lifestyle': 'Student',
                'occupation': 'University Student'
            },
            {
                'name': 'Mariam Al Suwaidi',
                'age': 42,
                'gender': 'F',
                'location': 'Abu Dhabi',
                'preferences': ['Home & Garden', 'Clothing'],
                'price_sensitivity': 0.3,
                'lifestyle': 'Homemaker',
                'occupation': 'Interior Designer'
            },
            {
                'name': 'Khalid Al Nuaimi',
                'age': 38,
                'gender': 'M',
                'location': 'Ajman',
                'preferences': ['Electronics', 'Home & Garden'],
                'price_sensitivity': 0.5,
                'lifestyle': 'Engineer',
                'occupation': 'Civil Engineer'
            },
            {
                'name': 'Noura Al Shamsi',
                'age': 29,
                'gender': 'F',
                'location': 'Sharjah',
                'preferences': ['Clothing', 'Electronics'],
                'price_sensitivity': 0.6,
                'lifestyle': 'Creative Professional',
                'occupation': 'Graphic Designer'
            },
            {
                'name': 'Saeed Al Dhaheri',
                'age': 55,
                'gender': 'M',
                'location': 'Abu Dhabi',
                'preferences': ['Home & Garden'],
                'price_sensitivity': 0.2,
                'lifestyle': 'Senior Executive',
                'occupation': 'Bank Manager'
            },
            {
                'name': 'Hessa Al Mazrouei',
                'age': 31,
                'gender': 'F',
                'location': 'Dubai',
                'preferences': ['Clothing', 'Electronics'],
                'price_sensitivity': 0.4,
                'lifestyle': 'Entrepreneur',
                'occupation': 'Startup Founder'
            },
            {
                'name': 'Rashid Al Ketbi',
                'age': 24,
                'gender': 'M',
                'location': 'Ras Al Khaimah',
                'preferences': ['Electronics'],
                'price_sensitivity': 0.8,
                'lifestyle': 'Recent Graduate',
                'occupation': 'Junior Developer'
            },
            {
                'name': 'Shamma Al Hosani',
                'age': 33,
                'gender': 'F',
                'location': 'Dubai',
                'preferences': ['Home & Garden', 'Clothing'],
                'price_sensitivity': 0.3,
                'lifestyle': 'Luxury Shopper',
                'occupation': 'Lawyer'
            },
            {
                'name': 'Hamdan Al Falasi',
                'age': 40,
                'gender': 'M',
                'location': 'Dubai',
                'preferences': ['Electronics', 'Home & Garden'],
                'price_sensitivity': 0.2,
                'lifestyle': 'Tech Enthusiast',
                'occupation': 'IT Director'
            },
            {
                'name': 'Moza Al Kaabi',
                'age': 27,
                'gender': 'F',
                'location': 'Abu Dhabi',
                'preferences': ['Clothing'],
                'price_sensitivity': 0.7,
                'lifestyle': 'Fashion Conscious',
                'occupation': 'Teacher'
            },
            {
                'name': 'Sultan Al Ameri',
                'age': 48,
                'gender': 'M',
                'location': 'Fujairah',
                'preferences': ['Home & Garden', 'Electronics'],
                'price_sensitivity': 0.4,
                'lifestyle': 'Traditional Family',
                'occupation': 'Government Employee'
            },
            {
                'name': 'Latifa Al Blooshi',
                'age': 36,
                'gender': 'F',
                'location': 'Sharjah',
                'preferences': ['Clothing', 'Home & Garden'],
                'price_sensitivity': 0.5,
                'lifestyle': 'Working Professional',
                'occupation': 'Accountant'
            },
            {
                'name': 'Majid Al Mansoori',
                'age': 22,
                'gender': 'M',
                'location': 'Dubai',
                'preferences': ['Electronics'],
                'price_sensitivity': 0.9,
                'lifestyle': 'Budget Conscious',
                'occupation': 'Intern'
            },
            {
                'name': 'Amna Al Zaabi',
                'age': 44,
                'gender': 'F',
                'location': 'Abu Dhabi',
                'preferences': ['Home & Garden'],
                'price_sensitivity': 0.3,
                'lifestyle': 'Luxury Homemaker',
                'occupation': 'Housewife'
            },
            {
                'name': 'Zayed Al Nahyan',
                'age': 30,
                'gender': 'M',
                'location': 'Abu Dhabi',
                'preferences': ['Electronics', 'Clothing'],
                'price_sensitivity': 0.1,
                'lifestyle': 'High Earner',
                'occupation': 'Investment Banker'
            },
            {
                'name': 'Sheikha Al Qasimi',
                'age': 39,
                'gender': 'F',
                'location': 'Umm Al Quwain',
                'preferences': ['Clothing', 'Home & Garden'],
                'price_sensitivity': 0.4,
                'lifestyle': 'Cultural Enthusiast',
                'occupation': 'Museum Curator'
            }
        ]
        
        # Product catalog
        self.product_catalog = {
            'Electronics': [
                {
                    'name': 'iPhone 15 Pro Max',
                    'subcategory': 'Mobile',
                    'price': 1199.99,
                    'brand': 'Apple',
                    'description': 'Latest iPhone with titanium design and advanced camera system',
                    'features': ['A17 Pro chip', '48MP camera', 'Titanium build', '5G connectivity'],
                    'rating': 4.8
                },
                {
                    'name': 'Samsung Galaxy S24 Ultra',
                    'subcategory': 'Mobile',
                    'price': 1099.99,
                    'brand': 'Samsung',
                    'description': 'Premium Android smartphone with S Pen and AI features',
                    'features': ['200MP camera', 'S Pen included', 'AI photo editing', '5000mAh battery'],
                    'rating': 4.7
                },
                {
                    'name': 'MacBook Pro 14-inch M3',
                    'subcategory': 'Computers',
                    'price': 1999.99,
                    'brand': 'Apple',
                    'description': 'Professional laptop with M3 chip for creative professionals',
                    'features': ['M3 Pro chip', '18-hour battery', 'Liquid Retina XDR display', '16GB RAM'],
                    'rating': 4.9
                },
                {
                    'name': 'Dell XPS 13 Plus',
                    'subcategory': 'Computers',
                    'price': 1299.99,
                    'brand': 'Dell',
                    'description': 'Ultra-thin laptop with premium design and performance',
                    'features': ['Intel Core i7', '13.4-inch OLED', '16GB RAM', 'Thunderbolt 4'],
                    'rating': 4.6
                },
                {
                    'name': 'Sony WH-1000XM5',
                    'subcategory': 'Audio',
                    'price': 399.99,
                    'brand': 'Sony',
                    'description': 'Industry-leading noise canceling wireless headphones',
                    'features': ['30-hour battery', 'Adaptive noise canceling', 'Quick charge', 'Multipoint connection'],
                    'rating': 4.8
                },
                {
                    'name': 'AirPods Pro 2nd Gen',
                    'subcategory': 'Audio',
                    'price': 249.99,
                    'brand': 'Apple',
                    'description': 'Premium wireless earbuds with spatial audio',
                    'features': ['Active noise cancellation', 'Spatial audio', 'MagSafe charging', 'Transparency mode'],
                    'rating': 4.7
                },
                {
                    'name': 'PlayStation 5',
                    'subcategory': 'Gaming',
                    'price': 499.99,
                    'brand': 'Sony',
                    'description': 'Next-generation gaming console with 4K gaming',
                    'features': ['4K gaming', 'Ray tracing', 'DualSense controller', 'Ultra-fast SSD'],
                    'rating': 4.8
                },
                {
                    'name': 'Xbox Series X',
                    'subcategory': 'Gaming',
                    'price': 499.99,
                    'brand': 'Microsoft',
                    'description': 'Powerful gaming console with 4K and 120fps support',
                    'features': ['4K 120fps', 'Quick Resume', 'Smart Delivery', '1TB SSD'],
                    'rating': 4.7
                },
                {
                    'name': 'Canon EOS R6 Mark II',
                    'subcategory': 'Cameras',
                    'price': 2499.99,
                    'brand': 'Canon',
                    'description': 'Professional mirrorless camera for photography and video',
                    'features': ['24.2MP sensor', '4K 60p video', 'In-body stabilization', 'Dual card slots'],
                    'rating': 4.9
                },
                {
                    'name': 'Amazon Echo Dot 5th Gen',
                    'subcategory': 'Smart Home',
                    'price': 49.99,
                    'brand': 'Amazon',
                    'description': 'Smart speaker with Alexa voice assistant',
                    'features': ['Alexa built-in', 'Improved audio', 'Smart home hub', 'Temperature sensor'],
                    'rating': 4.5
                }
            ],
            'Clothing': [
                {
                    'name': 'Levi\'s 501 Original Jeans',
                    'subcategory': 'Men',
                    'price': 89.99,
                    'brand': 'Levi\'s',
                    'description': 'Classic straight-fit jeans with authentic styling',
                    'features': ['100% cotton', 'Button fly', 'Straight fit', 'Classic 5-pocket'],
                    'rating': 4.6
                },
                {
                    'name': 'Nike Air Force 1',
                    'subcategory': 'Shoes',
                    'price': 110.00,
                    'brand': 'Nike',
                    'description': 'Iconic basketball shoes with timeless style',
                    'features': ['Leather upper', 'Air-Sole unit', 'Rubber outsole', 'Classic design'],
                    'rating': 4.8
                },
                {
                    'name': 'Zara Blazer',
                    'subcategory': 'Women',
                    'price': 79.99,
                    'brand': 'Zara',
                    'description': 'Elegant blazer perfect for professional settings',
                    'features': ['Tailored fit', 'Lapel collar', 'Front pockets', 'Lined interior'],
                    'rating': 4.4
                },
                {
                    'name': 'Adidas Ultraboost 22',
                    'subcategory': 'Sportswear',
                    'price': 190.00,
                    'brand': 'Adidas',
                    'description': 'High-performance running shoes with energy return',
                    'features': ['Boost midsole', 'Primeknit upper', 'Continental rubber', 'Torsion system'],
                    'rating': 4.7
                },
                {
                    'name': 'H&M Cotton T-Shirt',
                    'subcategory': 'Men',
                    'price': 12.99,
                    'brand': 'H&M',
                    'description': 'Basic cotton t-shirt in various colors',
                    'features': ['100% cotton', 'Regular fit', 'Crew neck', 'Machine washable'],
                    'rating': 4.2
                },
                {
                    'name': 'Coach Leather Handbag',
                    'subcategory': 'Accessories',
                    'price': 350.00,
                    'brand': 'Coach',
                    'description': 'Luxury leather handbag with signature design',
                    'features': ['Genuine leather', 'Multiple compartments', 'Adjustable strap', 'Dust bag included'],
                    'rating': 4.8
                },
                {
                    'name': 'Uniqlo Heattech Innerwear',
                    'subcategory': 'Women',
                    'price': 19.90,
                    'brand': 'Uniqlo',
                    'description': 'Thermal innerwear for warmth and comfort',
                    'features': ['Heattech fabric', 'Moisture-wicking', 'Odor control', 'Stretch material'],
                    'rating': 4.5
                },
                {
                    'name': 'Ray-Ban Aviator Sunglasses',
                    'subcategory': 'Accessories',
                    'price': 154.00,
                    'brand': 'Ray-Ban',
                    'description': 'Classic aviator sunglasses with UV protection',
                    'features': ['UV protection', 'Metal frame', 'Gradient lenses', 'Adjustable nose pads'],
                    'rating': 4.7
                },
                {
                    'name': 'Gap Denim Jacket',
                    'subcategory': 'Men',
                    'price': 69.99,
                    'brand': 'Gap',
                    'description': 'Classic denim jacket for casual wear',
                    'features': ['100% cotton denim', 'Button closure', 'Chest pockets', 'Regular fit'],
                    'rating': 4.3
                },
                {
                    'name': 'Lululemon Align Leggings',
                    'subcategory': 'Sportswear',
                    'price': 128.00,
                    'brand': 'Lululemon',
                    'description': 'High-waisted leggings for yoga and everyday wear',
                    'features': ['Nulu fabric', 'High-rise', '4-way stretch', 'No-dig waistband'],
                    'rating': 4.8
                }
            ],
            'Home & Garden': [
                {
                    'name': 'IKEA MALM Bed Frame',
                    'subcategory': 'Furniture',
                    'price': 179.00,
                    'brand': 'IKEA',
                    'description': 'Modern bed frame with clean lines and storage',
                    'features': ['Veneer surface', 'Under-bed storage', 'Easy assembly', 'Multiple sizes'],
                    'rating': 4.4
                },
                {
                    'name': 'Dyson V15 Detect',
                    'subcategory': 'Kitchen',
                    'price': 749.99,
                    'brand': 'Dyson',
                    'description': 'Cordless vacuum with laser dust detection',
                    'features': ['Laser detection', '60-minute runtime', 'HEPA filtration', 'LCD screen'],
                    'rating': 4.7
                },
                {
                    'name': 'Philips Hue Smart Bulbs',
                    'subcategory': 'Smart Home',
                    'price': 49.99,
                    'brand': 'Philips',
                    'description': 'Smart LED bulbs with color changing capability',
                    'features': ['16 million colors', 'Voice control', 'App control', 'Energy efficient'],
                    'rating': 4.6
                },
                {
                    'name': 'KitchenAid Stand Mixer',
                    'subcategory': 'Kitchen',
                    'price': 379.99,
                    'brand': 'KitchenAid',
                    'description': 'Professional stand mixer for baking enthusiasts',
                    'features': ['5-quart bowl', '10 speeds', 'Tilt-head design', 'Multiple attachments'],
                    'rating': 4.8
                },
                {
                    'name': 'West Elm Mid-Century Sofa',
                    'subcategory': 'Furniture',
                    'price': 1299.00,
                    'brand': 'West Elm',
                    'description': 'Mid-century modern sofa with kiln-dried frame',
                    'features': ['Kiln-dried frame', 'Performance fabric', 'Deep seats', 'Multiple colors'],
                    'rating': 4.5
                },
                {
                    'name': 'Nespresso Vertuo Next',
                    'subcategory': 'Kitchen',
                    'price': 199.99,
                    'brand': 'Nespresso',
                    'description': 'Coffee machine with barcode technology',
                    'features': ['Barcode reading', 'Multiple cup sizes', 'Fast heating', 'Bluetooth connectivity'],
                    'rating': 4.4
                },
                {
                    'name': 'Monstera Deliciosa Plant',
                    'subcategory': 'Garden',
                    'price': 29.99,
                    'brand': 'Local Nursery',
                    'description': 'Popular indoor plant with split leaves',
                    'features': ['Air purifying', 'Low maintenance', 'Fast growing', 'Pet-friendly'],
                    'rating': 4.7
                },
                {
                    'name': 'Pottery Barn Throw Pillows',
                    'subcategory': 'Decor',
                    'price': 39.99,
                    'brand': 'Pottery Barn',
                    'description': 'Decorative throw pillows in various patterns',
                    'features': ['Down alternative fill', 'Removable cover', 'Multiple patterns', 'Machine washable'],
                    'rating': 4.3
                },
                {
                    'name': 'Black+Decker Drill Set',
                    'subcategory': 'Tools',
                    'price': 89.99,
                    'brand': 'Black+Decker',
                    'description': 'Cordless drill with comprehensive bit set',
                    'features': ['20V battery', '30 drill bits', 'LED light', 'Carrying case'],
                    'rating': 4.5
                },
                {
                    'name': 'Weber Genesis Gas Grill',
                    'subcategory': 'Garden',
                    'price': 899.99,
                    'brand': 'Weber',
                    'description': 'Premium gas grill for outdoor cooking',
                    'features': ['3 burners', 'Porcelain grates', 'Side tables', '10-year warranty'],
                    'rating': 4.8
                }
            ]
        }
    
    def generate_customers(self) -> Dict[str, Dict[str, Any]]:
        """Generate 20 diverse customer profiles"""
        customers = {}
        
        for i, template in enumerate(self.customer_templates):
            customer_id = f"CUST_{i+1:03d}"
            
            # Add some variation to the template
            customer_data = {
                'customer_id': customer_id,
                'embedding_vector': [],  # Will be generated later
                'customer_metadata': {
                    'name': template['name'],
                    'age': template['age'],
                    'gender': template['gender'],
                    'location': template['location'],
                    'preferences': template['preferences'],
                    'price_sensitivity': template['price_sensitivity'],
                    'lifestyle': template['lifestyle'],
                    'occupation': template['occupation'],
                    'signup_date': (datetime.now() - timedelta(days=random.randint(30, 730))).isoformat()
                },
                'last_updated': datetime.now().isoformat()
            }
            
            customers[customer_id] = customer_data
        
        return customers
    
    def generate_products(self) -> Dict[str, Dict[str, Any]]:
        """Generate comprehensive product catalog"""
        products = {}
        product_counter = 1
        
        for category, product_list in self.product_catalog.items():
            for product_info in product_list:
                product_id = f"PROD_{product_counter:03d}"
                product_counter += 1
                
                product_data = {
                    'product_id': product_id,
                    'product_name': product_info['name'],
                    'embedding_vector': [],  # Will be generated later
                    'category': category,
                    'subcategory': product_info['subcategory'],
                    'price': product_info['price'],
                    'brand': product_info['brand'],
                    'description': product_info['description'],
                    'features': product_info['features'],
                    'rating': product_info['rating'],
                    'in_stock': random.choice([True, True, True, False]),  # 75% in stock
                    'last_updated': datetime.now().isoformat()
                }
                
                products[product_id] = product_data
        
        return products
    
    def generate_defaults(self, products: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate default recommendations"""
        # Get top-rated products for popular recommendations
        product_list = list(products.values())
        product_list.sort(key=lambda x: x['rating'], reverse=True)
        
        popular_products = []
        for product in product_list[:10]:
            popular_products.append({
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'reason': f"Highly rated {product['category'].lower()} item",
                'category': product['category'],
                'rating': product['rating']
            })
        
        # Category defaults
        category_defaults = {}
        for category in PRODUCT_CATEGORIES.keys():
            category_products = [p for p in products.values() if p['category'] == category]
            category_products.sort(key=lambda x: x['rating'], reverse=True)
            category_defaults[category] = [p['product_id'] for p in category_products[:5]]
        
        # New customer recommendations (mix of popular and diverse)
        new_customer_recommendations = []
        for product in product_list[:5]:
            new_customer_recommendations.append({
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'reason': 'Popular choice for new customers',
                'similarity_score': 0.85,
                'category': product['category']
            })
        
        return {
            'popular_products': popular_products,
            'category_defaults': category_defaults,
            'new_customer_recommendations': new_customer_recommendations,
            'last_updated': datetime.now().isoformat()
        }
    
    def generate_all_data(self, generate_embeddings: bool = False):
        """Generate all initial data"""
        print("🚀 Starting initial data generation...")
        
        # Generate customers and products
        print("👥 Generating customer profiles...")
        customers = self.generate_customers()
        print(f"✅ Generated {len(customers)} customer profiles")
        
        print("🛍️ Generating product catalog...")
        products = self.generate_products()
        print(f"✅ Generated {len(products)} products")
        
        print("⭐ Generating default recommendations...")
        defaults = self.generate_defaults(products)
        print("✅ Generated default recommendations")
        
        # Save to files
        print("💾 Saving data to files...")
        self.data_manager.save_customers(customers)
        self.data_manager.save_products(products)
        self.data_manager.save_defaults(defaults)
        print("✅ Data saved successfully")
        
        # Generate embeddings if requested
        if generate_embeddings:
            print("🧠 Generating embeddings with Bedrock...")
            self._generate_embeddings(customers, products)
        
        print("🎉 Initial data generation completed!")
        
        # Print summary
        summary = self.data_manager.get_data_summary()
        print("\n📊 Data Summary:")
        print(f"  - Customers: {summary['customers_count']}")
        print(f"  - Products: {summary['products_count']}")
        print(f"  - Popular products: {summary['popular_products_count']}")
        print(f"  - Categories with defaults: {summary['categories_with_defaults']}")
    
    def _generate_embeddings(self, customers: Dict, products: Dict):
        """Generate embeddings using Bedrock (optional)"""
        try:
            self.bedrock_client = BedrockClient()
            
            # Test connection first
            if not self.bedrock_client.test_connection():
                print("⚠️ Bedrock connection failed, skipping embedding generation")
                return
            
            # Generate customer embeddings
            print("Generating customer embeddings...")
            for customer_id, customer_data in customers.items():
                embedding = self.bedrock_client.generate_customer_embedding(
                    customer_data['customer_metadata']
                )
                if embedding:
                    customer_data['embedding_vector'] = embedding
                    print(f"✅ Generated embedding for {customer_id}")
                else:
                    print(f"❌ Failed to generate embedding for {customer_id}")
            
            # Generate product embeddings
            print("Generating product embeddings...")
            for product_id, product_data in products.items():
                embedding = self.bedrock_client.generate_product_embedding(product_data)
                if embedding:
                    product_data['embedding_vector'] = embedding
                    print(f"✅ Generated embedding for {product_id}")
                else:
                    print(f"❌ Failed to generate embedding for {product_id}")
            
            # Save updated data
            self.data_manager.save_customers(customers)
            self.data_manager.save_products(products)
            print("✅ Embeddings generated and saved")
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {str(e)}")
            print("Continuing without embeddings...")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate initial data for Bedrock-Streamlit recommendation system')
    parser.add_argument('--embeddings', action='store_true', help='Generate embeddings using Bedrock')
    parser.add_argument('--force', action='store_true', help='Force regeneration even if data exists')
    
    args = parser.parse_args()
    
    generator = InitialDataGenerator()
    
    # Check if data already exists
    if not args.force:
        summary = generator.data_manager.get_data_summary()
        if summary['customers_count'] > 0 or summary['products_count'] > 0:
            response = input("Data already exists. Regenerate? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
    
    generator.generate_all_data(generate_embeddings=args.embeddings)

if __name__ == "__main__":
    main()