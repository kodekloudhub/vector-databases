import json
import boto3
import numpy as np
import time
import logging
from typing import Dict, List, Tuple, Optional
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Environment variables for table names
CUSTOMER_EMBEDDINGS_TABLE = 'CustomerEmbeddings'
PRODUCT_EMBEDDINGS_TABLE = 'ProductEmbeddings'

class RecommendationEngine:
    """Vector-based recommendation engine using cosine similarity"""
    
    def __init__(self):
        self.customer_table = dynamodb.Table(CUSTOMER_EMBEDDINGS_TABLE)
        self.product_table = dynamodb.Table(PRODUCT_EMBEDDINGS_TABLE)
    
    def cosine_similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        Returns value between -1 and 1, where 1 means identical
        """
        try:
            # Convert to numpy arrays for efficient computation
            a = np.array(vector_a, dtype=float)
            b = np.array(vector_b, dtype=float)
            
            # Calculate dot product
            dot_product = np.dot(a, b)
            
            # Calculate norms
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            # Handle zero vectors
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    def get_customer_embedding(self, customer_id: str) -> Optional[List[float]]:
        """Fetch customer embedding vector from DynamoDB"""
        try:
            response = self.customer_table.get_item(
                Key={'customer_id': customer_id}
            )
            
            if 'Item' not in response:
                logger.warning(f"Customer {customer_id} not found")
                return None
            
            # Convert Decimal to float for numpy compatibility
            embedding = response['Item']['embedding_vector']
            return [float(x) for x in embedding]
            
        except Exception as e:
            logger.error(f"Error fetching customer embedding: {str(e)}")
            return None
    
    def get_all_product_embeddings(self) -> List[Dict]:
        """Fetch all product embeddings from DynamoDB"""
        try:
            products = []
            
            # Scan all products (for POC scale this is acceptable)
            response = self.product_table.scan()
            
            for item in response['Items']:
                # Convert Decimal to float for numpy compatibility
                embedding = [float(x) for x in item['embedding_vector']]
                
                products.append({
                    'product_id': item['product_id'],
                    'product_name': item['product_name'],
                    'embedding_vector': embedding,
                    'metadata': item.get('product_metadata', {})
                })
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = self.product_table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                
                for item in response['Items']:
                    embedding = [float(x) for x in item['embedding_vector']]
                    products.append({
                        'product_id': item['product_id'],
                        'product_name': item['product_name'],
                        'embedding_vector': embedding,
                        'metadata': item.get('product_metadata', {})
                    })
            
            logger.info(f"Fetched {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Error fetching product embeddings: {str(e)}")
            return []
    
    def calculate_recommendations(self, customer_embedding: List[float], 
                                products: List[Dict], top_k: int = 5) -> List[Dict]:
        """Calculate top-k product recommendations using cosine similarity"""
        try:
            recommendations = []
            
            for product in products:
                # Skip products that are out of stock
                if not product['metadata'].get('in_stock', True):
                    continue
                
                # Calculate similarity score
                similarity = self.cosine_similarity(
                    customer_embedding, 
                    product['embedding_vector']
                )
                
                recommendations.append({
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'similarity_score': round(similarity, 4)
                })
            
            # Sort by similarity score (descending) and return top-k
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            return recommendations[:top_k]
            
        except Exception as e:
            logger.error(f"Error calculating recommendations: {str(e)}")
            return []
    
    def get_recommendations(self, customer_id: str) -> Dict:
        """Main method to get recommendations for a customer"""
        start_time = time.time()
        
        try:
            # Step 1: Get customer embedding
            customer_embedding = self.get_customer_embedding(customer_id)
            if customer_embedding is None:
                return {
                    'statusCode': 404,
                    'body': {
                        'error': 'Customer not found',
                        'customer_id': customer_id,
                        'message': 'No embedding found for the provided customer ID'
                    }
                }
            
            # Step 2: Get all product embeddings
            products = self.get_all_product_embeddings()
            if not products:
                return {
                    'statusCode': 500,
                    'body': {
                        'error': 'No products available',
                        'message': 'Unable to fetch product catalog'
                    }
                }
            
            # Step 3: Calculate recommendations
            recommendations = self.calculate_recommendations(customer_embedding, products)
            
            # Step 4: Calculate processing time
            processing_time = round((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            # Step 5: Format response
            return {
                'statusCode': 200,
                'body': {
                    'customer_id': customer_id,
                    'recommendations': recommendations,
                    'processing_time_ms': processing_time
                }
            }
            
        except Exception as e:
            logger.error(f"Error in get_recommendations: {str(e)}")
            processing_time = round((time.time() - start_time) * 1000)
            
            return {
                'statusCode': 500,
                'body': {
                    'error': 'Internal server error',
                    'message': 'An error occurred while processing recommendations',
                    'processing_time_ms': processing_time
                }
            }

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    try:
        # Log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse the request body
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        # Validate required parameters
        if 'customer_id' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'Missing required parameter: customer_id'
                })
            }
        
        customer_id = body['customer_id']
        
        # Validate customer_id format
        if not isinstance(customer_id, str) or not customer_id.strip():
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'Invalid customer_id format'
                })
            }
        
        # Initialize recommendation engine and get recommendations
        engine = RecommendationEngine()
        result = engine.get_recommendations(customer_id.strip())
        
        # Return response with proper headers
        return {
            'statusCode': result['statusCode'],
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result['body'])
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Bad Request',
                'message': 'Invalid JSON format in request body'
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            })
        }

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'body': json.dumps({
            'customer_id': 'CUST_001'
        })
    }
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.function_name = 'test-function'
            self.memory_limit_in_mb = 512
            self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test-function'
            self.aws_request_id = 'test-request-id'
    
    context = MockContext()
    
    # Test the function
    result = lambda_handler(test_event, context)
    print(json.dumps(result, indent=2))