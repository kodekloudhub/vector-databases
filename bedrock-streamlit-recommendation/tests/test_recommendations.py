"""
Unit tests for the recommendation system
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation_engine import RecommendationEngine
from bedrock_client import BedrockClient, cosine_similarity
from data_manager import DataManager

class TestRecommendationEngine(unittest.TestCase):
    """Test cases for RecommendationEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = RecommendationEngine()
        
        # Mock data
        self.sample_customer = {
            'customer_id': 'CUST_001',
            'embedding_vector': [0.1, 0.2, 0.3, 0.4, 0.5],
            'customer_metadata': {
                'name': 'Test Customer',
                'age': 30,
                'gender': 'M',
                'location': 'Dubai',
                'preferences': ['Electronics']
            }
        }
        
        self.sample_product = {
            'product_id': 'PROD_001',
            'product_name': 'Test Product',
            'embedding_vector': [0.2, 0.3, 0.4, 0.5, 0.6],
            'category': 'Electronics',
            'price': 100.0,
            'rating': 4.5,
            'in_stock': True
        }
    
    @patch('recommendation_engine.DataManager')
    def test_load_customers_cache(self, mock_data_manager):
        """Test customer loading with caching"""
        mock_data_manager.return_value.load_customers.return_value = {'CUST_001': self.sample_customer}
        
        engine = RecommendationEngine()
        customers1 = engine._load_customers()
        customers2 = engine._load_customers()
        
        # Should only call load_customers once due to caching
        mock_data_manager.return_value.load_customers.assert_called_once()
        self.assertEqual(customers1, customers2)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        # Test identical vectors
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0, places=3)
        
        # Test orthogonal vectors
        vec3 = [0.0, 1.0, 0.0]
        similarity = cosine_similarity(vec1, vec3)
        self.assertAlmostEqual(similarity, 0.0, places=3)
        
        # Test zero vectors
        vec_zero = [0.0, 0.0, 0.0]
        similarity = cosine_similarity(vec1, vec_zero)
        self.assertEqual(similarity, 0.0)
    
    @patch('recommendation_engine.DataManager')
    def test_get_recommendations_existing_customer(self, mock_data_manager):
        """Test recommendations for existing customer"""
        # Mock data
        customers = {'CUST_001': self.sample_customer}
        products = {'PROD_001': self.sample_product}
        
        mock_data_manager.return_value.load_customers.return_value = customers
        mock_data_manager.return_value.load_products.return_value = products
        
        engine = RecommendationEngine()
        
        with patch.object(engine.bedrock_client, 'generate_explanation', return_value="Test explanation"):
            result = engine.get_recommendations_for_existing_customer('CUST_001')
        
        self.assertEqual(result['customer_id'], 'CUST_001')
        self.assertEqual(result['customer_type'], 'existing')
        self.assertFalse(result['fallback_used'])
        self.assertIsInstance(result['recommendations'], list)
    
    @patch('recommendation_engine.DataManager')
    def test_get_recommendations_customer_not_found(self, mock_data_manager):
        """Test recommendations when customer not found"""
        mock_data_manager.return_value.load_customers.return_value = {}
        mock_data_manager.return_value.load_defaults.return_value = {
            'new_customer_recommendations': []
        }
        
        engine = RecommendationEngine()
        result = engine.get_recommendations_for_existing_customer('NONEXISTENT')
        
        self.assertTrue(result['fallback_used'])
        self.assertEqual(result['customer_type'], 'fallback')
    
    @patch('recommendation_engine.DataManager')
    @patch('recommendation_engine.BedrockClient')
    def test_get_recommendations_new_customer(self, mock_bedrock, mock_data_manager):
        """Test recommendations for new customer"""
        # Mock Bedrock client
        mock_bedrock.return_value.generate_customer_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_bedrock.return_value.generate_explanation.return_value = "Test explanation"
        
        # Mock data
        products = {'PROD_001': self.sample_product}
        mock_data_manager.return_value.load_products.return_value = products
        
        engine = RecommendationEngine()
        
        customer_profile = {
            'name': 'New Customer',
            'age': 25,
            'preferences': ['Electronics']
        }
        
        result = engine.get_recommendations_for_new_customer(customer_profile)
        
        self.assertEqual(result['customer_type'], 'new')
        self.assertIsInstance(result['recommendations'], list)
    
    def test_should_use_fallback(self):
        """Test fallback decision logic"""
        engine = RecommendationEngine()
        
        # Empty recommendations should use fallback
        self.assertTrue(engine._should_use_fallback([]))
        
        # Low similarity should use fallback
        low_sim_recs = [{'similarity_score': 0.1, 'category': 'Electronics'}]
        self.assertTrue(engine._should_use_fallback(low_sim_recs))
        
        # Good similarity should not use fallback
        good_sim_recs = [
            {'similarity_score': 0.8, 'category': 'Electronics'},
            {'similarity_score': 0.7, 'category': 'Clothing'}
        ]
        self.assertFalse(engine._should_use_fallback(good_sim_recs))

class TestBedrockClient(unittest.TestCase):
    """Test cases for BedrockClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('bedrock_client.boto3.client'):
            self.client = BedrockClient()
    
    def test_format_customer_profile(self):
        """Test customer profile formatting"""
        profile = {
            'age': 30,
            'gender': 'M',
            'location': 'Dubai',
            'preferences': ['Electronics', 'Clothing'],
            'price_sensitivity': 0.3
        }
        
        formatted = self.client._format_customer_profile(profile)
        
        self.assertIn('30 years old', formatted)
        self.assertIn('Dubai', formatted)
        self.assertIn('Electronics, Clothing', formatted)
        self.assertIn('premium-oriented', formatted)
    
    def test_format_product_description(self):
        """Test product description formatting"""
        product = {
            'product_name': 'iPhone 15',
            'category': 'Electronics',
            'price': 999.99,
            'brand': 'Apple',
            'features': ['5G', 'Face ID']
        }
        
        formatted = self.client._format_product_description(product)
        
        self.assertIn('iPhone 15', formatted)
        self.assertIn('Electronics', formatted)
        self.assertIn('$999.99', formatted)
        self.assertIn('Apple', formatted)
        self.assertIn('5G, Face ID', formatted)

class TestDataManager(unittest.TestCase):
    """Test cases for DataManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('data_manager.os.makedirs'), \
             patch('data_manager.os.path.exists', return_value=True):
            self.data_manager = DataManager()
    
    @patch('data_manager.DataManager._load_json')
    def test_get_customer(self, mock_load_json):
        """Test getting specific customer"""
        mock_load_json.return_value = {
            'CUST_001': {'name': 'Test Customer'}
        }
        
        customer = self.data_manager.get_customer('CUST_001')
        self.assertEqual(customer['name'], 'Test Customer')
        
        # Test non-existent customer
        customer = self.data_manager.get_customer('NONEXISTENT')
        self.assertIsNone(customer)
    
    @patch('data_manager.DataManager._load_json')
    def test_get_products_by_category(self, mock_load_json):
        """Test filtering products by category"""
        mock_load_json.return_value = {
            'PROD_001': {'category': 'Electronics', 'name': 'Phone'},
            'PROD_002': {'category': 'Clothing', 'name': 'Shirt'},
            'PROD_003': {'category': 'Electronics', 'name': 'Laptop'}
        }
        
        electronics = self.data_manager.get_products_by_category('Electronics')
        self.assertEqual(len(electronics), 2)
        self.assertIn('PROD_001', electronics)
        self.assertIn('PROD_003', electronics)
    
    def test_validate_data_integrity(self):
        """Test data integrity validation"""
        with patch.object(self.data_manager, 'load_customers') as mock_customers, \
             patch.object(self.data_manager, 'load_products') as mock_products, \
             patch.object(self.data_manager, 'load_defaults') as mock_defaults:
            
            # Valid data
            mock_customers.return_value = {
                'CUST_001': {
                    'customer_id': 'CUST_001',
                    'embedding_vector': [0.1, 0.2]
                }
            }
            mock_products.return_value = {
                'PROD_001': {
                    'product_id': 'PROD_001',
                    'product_name': 'Test Product',
                    'embedding_vector': [0.1, 0.2]
                }
            }
            mock_defaults.return_value = {
                'popular_products': [],
                'category_defaults': {},
                'new_customer_recommendations': []
            }
            
            result = self.data_manager.validate_data_integrity()
            
            self.assertTrue(result['customers_valid'])
            self.assertTrue(result['products_valid'])
            self.assertTrue(result['defaults_valid'])

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestRecommendationEngine))
    test_suite.addTest(unittest.makeSuite(TestBedrockClient))
    test_suite.addTest(unittest.makeSuite(TestDataManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)