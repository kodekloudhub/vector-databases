"""
Amazon Bedrock client for embeddings and text generation
"""

import json
import time
import logging
from typing import List, Dict, Optional, Any
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import numpy as np

from config import (
    BEDROCK_CONFIG, 
    EMBEDDING_MODEL_ID, 
    TEXT_MODEL_ID,
    get_bedrock_config
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockClient:
    """Client for interacting with Amazon Bedrock services"""
    
    def __init__(self):
        """Initialize Bedrock client"""
        try:
            self.bedrock_runtime = boto3.client(
                'bedrock-runtime',
                **get_bedrock_config()
            )
            self.embedding_model_id = EMBEDDING_MODEL_ID
            self.text_model_id = TEXT_MODEL_ID
            self.max_retries = BEDROCK_CONFIG['max_retries']
            self.retry_delay = BEDROCK_CONFIG['retry_delay']
            self.timeout = BEDROCK_CONFIG['timeout']
            
            logger.info("Bedrock client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (ClientError, BotoCoreError) as e:
                if attempt == self.max_retries - 1:
                    raise e
                
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                time.sleep(wait_time)
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for given text using Titan Embeddings
        
        Args:
            text (str): Input text to embed
            
        Returns:
            List[float]: Embedding vector or None if failed
        """
        try:
            # Prepare the request body
            body = json.dumps({
                'inputText': text
            })
            
            # Make the API call with retry logic
            response = self._retry_with_backoff(
                self.bedrock_runtime.invoke_model,
                modelId=self.embedding_model_id,
                body=body,
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')
            
            if embedding:
                logger.debug(f"Generated embedding of dimension {len(embedding)}")
                return embedding
            else:
                logger.error("No embedding found in response")
                return None
                
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    def generate_customer_embedding(self, customer_profile: Dict[str, Any]) -> Optional[List[float]]:
        """
        Generate embedding for customer profile
        
        Args:
            customer_profile (Dict): Customer profile data
            
        Returns:
            List[float]: Customer embedding vector
        """
        try:
            # Create a descriptive text from customer profile
            profile_text = self._format_customer_profile(customer_profile)
            return self.generate_embedding(profile_text)
            
        except Exception as e:
            logger.error(f"Error generating customer embedding: {str(e)}")
            return None
    
    def generate_product_embedding(self, product_data: Dict[str, Any]) -> Optional[List[float]]:
        """
        Generate embedding for product
        
        Args:
            product_data (Dict): Product data
            
        Returns:
            List[float]: Product embedding vector
        """
        try:
            # Create a descriptive text from product data
            product_text = self._format_product_description(product_data)
            return self.generate_embedding(product_text)
            
        except Exception as e:
            logger.error(f"Error generating product embedding: {str(e)}")
            return None
    
    def generate_explanation(self, customer_profile: Dict[str, Any], 
                           recommendations: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate explanation for recommendations using Claude
        
        Args:
            customer_profile (Dict): Customer profile
            recommendations (List[Dict]): List of recommended products
            
        Returns:
            str: Natural language explanation
        """
        try:
            # Create prompt for explanation
            prompt = self._create_explanation_prompt(customer_profile, recommendations)
            
            # Prepare the request body for Claude
            body = json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 500,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            })
            
            # Make the API call
            response = self._retry_with_backoff(
                self.bedrock_runtime.invoke_model,
                modelId=self.text_model_id,
                body=body,
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            explanation = response_body.get('content', [{}])[0].get('text', '')
            
            if explanation:
                logger.debug("Generated recommendation explanation")
                return explanation.strip()
            else:
                logger.error("No explanation found in response")
                return None
                
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return None
    
    def _format_customer_profile(self, profile: Dict[str, Any]) -> str:
        """Format customer profile into descriptive text"""
        age = profile.get('age', 'unknown')
        gender = profile.get('gender', 'unknown')
        location = profile.get('location', 'unknown')
        preferences = ', '.join(profile.get('preferences', []))
        price_sensitivity = profile.get('price_sensitivity', 0.5)
        
        price_desc = "budget-conscious" if price_sensitivity > 0.7 else \
                    "premium-oriented" if price_sensitivity < 0.3 else "value-conscious"
        
        return f"""
        Customer Profile:
        Age: {age} years old
        Gender: {gender}
        Location: {location}
        Interests: {preferences}
        Shopping Style: {price_desc}
        Lifestyle: {profile.get('lifestyle', 'General consumer')}
        """
    
    def _format_product_description(self, product: Dict[str, Any]) -> str:
        """Format product data into descriptive text"""
        name = product.get('product_name', product.get('name', 'Unknown Product'))
        category = product.get('category', 'General')
        subcategory = product.get('subcategory', '')
        price = product.get('price', 0)
        brand = product.get('brand', 'Generic')
        description = product.get('description', '')
        features = product.get('features', [])
        
        features_text = ', '.join(features) if features else 'Standard features'
        
        return f"""
        Product: {name}
        Category: {category} - {subcategory}
        Brand: {brand}
        Price: ${price}
        Description: {description}
        Features: {features_text}
        """
    
    def _create_explanation_prompt(self, customer_profile: Dict[str, Any], 
                                 recommendations: List[Dict[str, Any]]) -> str:
        """Create prompt for recommendation explanation"""
        customer_text = self._format_customer_profile(customer_profile)
        
        products_text = "\n".join([
            f"- {rec.get('product_name', 'Unknown')} (Similarity: {rec.get('similarity_score', 0):.2f})"
            for rec in recommendations[:3]  # Top 3 for explanation
        ])
        
        return f"""
        You are a helpful shopping assistant. Explain why these products were recommended for this customer.
        
        {customer_text}
        
        Recommended Products:
        {products_text}
        
        Please provide a brief, friendly explanation (2-3 sentences) of why these products match the customer's profile and preferences. Focus on the connection between their interests, demographics, and the recommended items.
        """
    
    def test_connection(self) -> bool:
        """Test Bedrock connection"""
        try:
            test_embedding = self.generate_embedding("Test connection")
            if test_embedding and len(test_embedding) > 0:
                logger.info("Bedrock connection test successful")
                return True
            else:
                logger.error("Bedrock connection test failed - no embedding returned")
                return False
                
        except Exception as e:
            logger.error(f"Bedrock connection test failed: {str(e)}")
            return False

# Utility functions
def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        a = np.array(vec1)
        b = np.array(vec2)
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot_product / (norm_a * norm_b))
        
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {str(e)}")
        return 0.0

def batch_generate_embeddings(bedrock_client: BedrockClient, 
                            texts: List[str], 
                            batch_size: int = 10) -> List[Optional[List[float]]]:
    """Generate embeddings for multiple texts in batches"""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        for text in batch:
            embedding = bedrock_client.generate_embedding(text)
            embeddings.append(embedding)
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
    
    return embeddings