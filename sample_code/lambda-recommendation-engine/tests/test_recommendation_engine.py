#!/usr/bin/env python3
"""
Test script for Vector Recommendation Engine POC

This script tests the recommendation engine functionality including:
- API endpoint testing
- Lambda function testing
- Data validation
- Performance testing

Usage:
    python test_recommendation_engine.py --api-url https://api-url/recommend --environment dev
"""

import argparse
import requests
import json
import time
import statistics
import boto3
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommendationEngineTest:
    """Test suite for the Vector Recommendation Engine"""
    
    def __init__(self, api_url: str = None, environment: str = 'dev', region: str = 'us-east-1'):
        self.api_url = api_url
        self.environment = environment
        self.region = region
        
        # Initialize AWS clients for direct testing
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        
        # Table names
        self.customer_table_name = f'CustomerEmbeddings-{environment}'
        self.product_table_name = f'ProductEmbeddings-{environment}'
        
        # Lambda function name
        self.function_name = f'vector-recommendation-{environment}'
        
        # Test results
        self.test_results = {
            'api_tests': [],
            'lambda_tests': [],
            'performance_tests': [],
            'data_validation_tests': []
        }
    
    def test_api_endpoint(self, customer_ids: List[str]) -> Dict:
        """Test the API Gateway endpoint"""
        logger.info("🧪 Testing API Gateway endpoint...")
        
        if not self.api_url:
            logger.warning("⚠️ API URL not provided, skipping API tests")
            return {'status': 'skipped', 'reason': 'No API URL provided'}
        
        results = []
        
        for customer_id in customer_ids:
            try:
                # Test valid request
                payload = {'customer_id': customer_id}
                headers = {'Content-Type': 'application/json'}
                
                start_time = time.time()
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                test_result = {
                    'customer_id': customer_id,
                    'status_code': response.status_code,
                    'response_time_ms': round(response_time, 2),
                    'success': response.status_code == 200
                }
                
                if response.status_code == 200:
                    data = response.json()
                    test_result['recommendations_count'] = len(data.get('recommendations', []))
                    test_result['processing_time_ms'] = data.get('processing_time_ms', 0)
                    
                    # Validate response structure
                    if self._validate_response_structure(data):
                        test_result['valid_structure'] = True
                    else:
                        test_result['valid_structure'] = False
                        test_result['success'] = False
                else:
                    test_result['error'] = response.text
                
                results.append(test_result)
                logger.info(f"✅ Customer {customer_id}: {response.status_code} ({response_time:.2f}ms)")
                
            except Exception as e:
                test_result = {
                    'customer_id': customer_id,
                    'success': False,
                    'error': str(e)
                }
                results.append(test_result)
                logger.error(f"❌ Customer {customer_id}: {str(e)}")
        
        self.test_results['api_tests'] = results
        return {'status': 'completed', 'results': results}
    
    def test_lambda_function(self, customer_ids: List[str]) -> Dict:
        """Test the Lambda function directly"""
        logger.info("🧪 Testing Lambda function directly...")
        
        results = []
        
        for customer_id in customer_ids:
            try:
                # Create test event
                event = {
                    'body': json.dumps({'customer_id': customer_id})
                }
                
                start_time = time.time()
                response = self.lambda_client.invoke(
                    FunctionName=self.function_name,
                    Payload=json.dumps(event)
                )
                response_time = (time.time() - start_time) * 1000
                
                # Parse response
                payload = json.loads(response['Payload'].read())
                
                test_result = {
                    'customer_id': customer_id,
                    'status_code': payload.get('statusCode', 500),
                    'response_time_ms': round(response_time, 2),
                    'success': payload.get('statusCode') == 200
                }
                
                if payload.get('statusCode') == 200:
                    body = json.loads(payload.get('body', '{}'))
                    test_result['recommendations_count'] = len(body.get('recommendations', []))
                    test_result['processing_time_ms'] = body.get('processing_time_ms', 0)
                    
                    # Validate response structure
                    if self._validate_response_structure(body):
                        test_result['valid_structure'] = True
                    else:
                        test_result['valid_structure'] = False
                        test_result['success'] = False
                else:
                    test_result['error'] = payload.get('body', 'Unknown error')
                
                results.append(test_result)
                logger.info(f"✅ Customer {customer_id}: {payload.get('statusCode')} ({response_time:.2f}ms)")
                
            except Exception as e:
                test_result = {
                    'customer_id': customer_id,
                    'success': False,
                    'error': str(e)
                }
                results.append(test_result)
                logger.error(f"❌ Customer {customer_id}: {str(e)}")
        
        self.test_results['lambda_tests'] = results
        return {'status': 'completed', 'results': results}
    
    def test_performance(self, customer_id: str, num_requests: int = 10) -> Dict:
        """Test performance with multiple requests"""
        logger.info(f"🧪 Testing performance with {num_requests} requests...")
        
        if not self.api_url:
            logger.warning("⚠️ API URL not provided, skipping performance tests")
            return {'status': 'skipped', 'reason': 'No API URL provided'}
        
        response_times = []
        processing_times = []
        success_count = 0
        
        for i in range(num_requests):
            try:
                payload = {'customer_id': customer_id}
                headers = {'Content-Type': 'application/json'}
                
                start_time = time.time()
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
                response_time = (time.time() - start_time) * 1000
                
                response_times.append(response_time)
                
                if response.status_code == 200:
                    success_count += 1
                    data = response.json()
                    processing_times.append(data.get('processing_time_ms', 0))
                
                logger.info(f"Request {i+1}/{num_requests}: {response.status_code} ({response_time:.2f}ms)")
                
            except Exception as e:
                logger.error(f"Request {i+1}/{num_requests} failed: {str(e)}")
        
        # Calculate statistics
        if response_times:
            performance_stats = {
                'total_requests': num_requests,
                'successful_requests': success_count,
                'success_rate': (success_count / num_requests) * 100,
                'response_time_stats': {
                    'min_ms': min(response_times),
                    'max_ms': max(response_times),
                    'avg_ms': statistics.mean(response_times),
                    'median_ms': statistics.median(response_times)
                }
            }
            
            if processing_times:
                performance_stats['processing_time_stats'] = {
                    'min_ms': min(processing_times),
                    'max_ms': max(processing_times),
                    'avg_ms': statistics.mean(processing_times),
                    'median_ms': statistics.median(processing_times)
                }
        else:
            performance_stats = {
                'total_requests': num_requests,
                'successful_requests': 0,
                'success_rate': 0,
                'error': 'No successful requests'
            }
        
        self.test_results['performance_tests'] = performance_stats
        return {'status': 'completed', 'results': performance_stats}
    
    def test_data_validation(self) -> Dict:
        """Validate data in DynamoDB tables"""
        logger.info("🧪 Validating data in DynamoDB tables...")
        
        results = {
            'customer_table': {},
            'product_table': {}
        }
        
        try:
            # Test customer table
            customer_table = self.dynamodb.Table(self.customer_table_name)
            customer_response = customer_table.scan(Limit=10)
            
            customer_count = customer_response['Count']
            results['customer_table']['sample_count'] = customer_count
            results['customer_table']['valid_structure'] = True
            
            # Validate customer structure
            for item in customer_response['Items']:
                if not self._validate_customer_item(item):
                    results['customer_table']['valid_structure'] = False
                    break
            
            logger.info(f"✅ Customer table: {customer_count} items sampled")
            
        except Exception as e:
            results['customer_table']['error'] = str(e)
            logger.error(f"❌ Customer table validation failed: {str(e)}")
        
        try:
            # Test product table
            product_table = self.dynamodb.Table(self.product_table_name)
            product_response = product_table.scan(Limit=10)
            
            product_count = product_response['Count']
            results['product_table']['sample_count'] = product_count
            results['product_table']['valid_structure'] = True
            
            # Validate product structure
            for item in product_response['Items']:
                if not self._validate_product_item(item):
                    results['product_table']['valid_structure'] = False
                    break
            
            logger.info(f"✅ Product table: {product_count} items sampled")
            
        except Exception as e:
            results['product_table']['error'] = str(e)
            logger.error(f"❌ Product table validation failed: {str(e)}")
        
        self.test_results['data_validation_tests'] = results
        return {'status': 'completed', 'results': results}
    
    def test_error_scenarios(self) -> Dict:
        """Test error handling scenarios"""
        logger.info("🧪 Testing error scenarios...")
        
        if not self.api_url:
            logger.warning("⚠️ API URL not provided, skipping error scenario tests")
            return {'status': 'skipped', 'reason': 'No API URL provided'}
        
        error_tests = [
            {
                'name': 'Missing customer_id',
                'payload': {},
                'expected_status': 400
            },
            {
                'name': 'Invalid customer_id',
                'payload': {'customer_id': ''},
                'expected_status': 400
            },
            {
                'name': 'Non-existent customer',
                'payload': {'customer_id': 'CUST_999999'},
                'expected_status': 404
            },
            {
                'name': 'Invalid JSON',
                'payload': 'invalid json',
                'expected_status': 400
            }
        ]
        
        results = []
        
        for test in error_tests:
            try:
                headers = {'Content-Type': 'application/json'}
                
                if isinstance(test['payload'], str):
                    # Send invalid JSON
                    response = requests.post(self.api_url, data=test['payload'], headers=headers, timeout=30)
                else:
                    response = requests.post(self.api_url, json=test['payload'], headers=headers, timeout=30)
                
                test_result = {
                    'test_name': test['name'],
                    'expected_status': test['expected_status'],
                    'actual_status': response.status_code,
                    'success': response.status_code == test['expected_status']
                }
                
                results.append(test_result)
                
                if test_result['success']:
                    logger.info(f"✅ {test['name']}: Expected {test['expected_status']}, got {response.status_code}")
                else:
                    logger.error(f"❌ {test['name']}: Expected {test['expected_status']}, got {response.status_code}")
                
            except Exception as e:
                test_result = {
                    'test_name': test['name'],
                    'success': False,
                    'error': str(e)
                }
                results.append(test_result)
                logger.error(f"❌ {test['name']}: {str(e)}")
        
        return {'status': 'completed', 'results': results}
    
    def _validate_response_structure(self, data: Dict) -> bool:
        """Validate the structure of API response"""
        required_fields = ['customer_id', 'recommendations', 'processing_time_ms']
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate recommendations structure
        recommendations = data.get('recommendations', [])
        if not isinstance(recommendations, list):
            return False
        
        for rec in recommendations:
            if not isinstance(rec, dict):
                return False
            if 'product_id' not in rec or 'product_name' not in rec or 'similarity_score' not in rec:
                return False
        
        return True
    
    def _validate_customer_item(self, item: Dict) -> bool:
        """Validate customer item structure"""
        required_fields = ['customer_id', 'embedding_vector', 'customer_metadata']
        
        for field in required_fields:
            if field not in item:
                return False
        
        # Validate embedding vector
        embedding = item.get('embedding_vector', [])
        if not isinstance(embedding, list) or len(embedding) != 10:
            return False
        
        return True
    
    def _validate_product_item(self, item: Dict) -> bool:
        """Validate product item structure"""
        required_fields = ['product_id', 'product_name', 'embedding_vector', 'product_metadata']
        
        for field in required_fields:
            if field not in item:
                return False
        
        # Validate embedding vector
        embedding = item.get('embedding_vector', [])
        if not isinstance(embedding, list) or len(embedding) != 10:
            return False
        
        return True
    
    def run_all_tests(self) -> Dict:
        """Run all test suites"""
        logger.info("🚀 Starting comprehensive test suite...")
        
        # Test customer IDs (assuming these exist in the data)
        test_customer_ids = ['CUST_001', 'CUST_002', 'CUST_003', 'CUST_004', 'CUST_005']
        
        # Run tests
        api_results = self.test_api_endpoint(test_customer_ids)
        lambda_results = self.test_lambda_function(test_customer_ids)
        performance_results = self.test_performance('CUST_001', 5)
        data_validation_results = self.test_data_validation()
        error_results = self.test_error_scenarios()
        
        # Generate summary
        summary = {
            'api_tests': api_results,
            'lambda_tests': lambda_results,
            'performance_tests': performance_results,
            'data_validation_tests': data_validation_results,
            'error_scenario_tests': error_results,
            'overall_success': self._calculate_overall_success()
        }
        
        logger.info("🎉 Test suite completed!")
        return summary
    
    def _calculate_overall_success(self) -> bool:
        """Calculate overall test success"""
        # Check API tests
        api_success = all(test.get('success', False) for test in self.test_results.get('api_tests', []))
        
        # Check Lambda tests
        lambda_success = all(test.get('success', False) for test in self.test_results.get('lambda_tests', []))
        
        # Check performance (success rate > 80%)
        perf_tests = self.test_results.get('performance_tests', {})
        perf_success = perf_tests.get('success_rate', 0) > 80
        
        # Check data validation
        data_tests = self.test_results.get('data_validation_tests', {})
        data_success = (
            data_tests.get('customer_table', {}).get('valid_structure', False) and
            data_tests.get('product_table', {}).get('valid_structure', False)
        )
        
        return api_success and lambda_success and perf_success and data_success
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("🧪 VECTOR RECOMMENDATION ENGINE TEST SUMMARY")
        print("="*60)
        
        # API Tests
        api_tests = self.test_results.get('api_tests', [])
        if api_tests:
            successful_api = sum(1 for test in api_tests if test.get('success', False))
            print(f"📡 API Tests: {successful_api}/{len(api_tests)} passed")
        
        # Lambda Tests
        lambda_tests = self.test_results.get('lambda_tests', [])
        if lambda_tests:
            successful_lambda = sum(1 for test in lambda_tests if test.get('success', False))
            print(f"⚡ Lambda Tests: {successful_lambda}/{len(lambda_tests)} passed")
        
        # Performance Tests
        perf_tests = self.test_results.get('performance_tests', {})
        if perf_tests:
            success_rate = perf_tests.get('success_rate', 0)
            avg_response = perf_tests.get('response_time_stats', {}).get('avg_ms', 0)
            print(f"🚀 Performance: {success_rate:.1f}% success rate, {avg_response:.1f}ms avg response")
        
        # Data Validation
        data_tests = self.test_results.get('data_validation_tests', {})
        if data_tests:
            customer_valid = data_tests.get('customer_table', {}).get('valid_structure', False)
            product_valid = data_tests.get('product_table', {}).get('valid_structure', False)
            print(f"📊 Data Validation: Customer table {'✅' if customer_valid else '❌'}, Product table {'✅' if product_valid else '❌'}")
        
        overall_success = self._calculate_overall_success()
        print(f"\n🎯 Overall Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Test Vector Recommendation Engine')
    parser.add_argument('--api-url', help='API Gateway endpoint URL')
    parser.add_argument('--environment', '-e', default='dev', help='Environment (dev, staging, prod)')
    parser.add_argument('--region', '-r', default='us-east-1', help='AWS region')
    parser.add_argument('--performance-requests', '-p', type=int, default=5, help='Number of requests for performance testing')
    
    args = parser.parse_args()
    
    # Create test instance
    tester = RecommendationEngineTest(args.api_url, args.environment, args.region)
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Print summary
    tester.print_summary()
    
    # Save results to file
    with open(f'test_results_{args.environment}.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Test results saved to test_results_{args.environment}.json")

if __name__ == "__main__":
    main()