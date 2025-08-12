"""
Core recommendation engine with cosine similarity and default fallbacks
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import random

from data_manager import DataManager
from bedrock_client import BedrockClient, cosine_similarity as bedrock_cosine_similarity
from config import MAX_RECOMMENDATIONS, SIMILARITY_THRESHOLD, DEFAULT_FALLBACK_COUNT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Core recommendation engine for the Bedrock-Streamlit system"""
    
    def __init__(self):
        """Initialize the recommendation engine"""
        self.data_manager = DataManager()
        self.bedrock_client = BedrockClient()
        
        # Cache for frequently accessed data
        self._customers_cache = None
        self._products_cache = None
        self._defaults_cache = None
        
        logger.info("Recommendation engine initialized")
    
    def _load_customers(self) -> Dict[str, Dict[str, Any]]:
        """Load customers with caching"""
        if self._customers_cache is None:
            self._customers_cache = self.data_manager.load_customers()
        return self._customers_cache
    
    def _load_products(self) -> Dict[str, Dict[str, Any]]:
        """Load products with caching"""
        if self._products_cache is None:
            self._products_cache = self.data_manager.load_products()
        return self._products_cache
    
    def _load_defaults(self) -> Dict[str, Any]:
        """Load defaults with caching"""
        if self._defaults_cache is None:
            self._defaults_cache = self.data_manager.load_defaults()
        return self._defaults_cache
    
    def refresh_cache(self):
        """Refresh all cached data"""
        self._customers_cache = None
        self._products_cache = None
        self._defaults_cache = None
        logger.info("Cache refreshed")
    
    def get_recommendations_for_existing_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Get recommendations for an existing customer
        
        Args:
            customer_id (str): Customer ID
            
        Returns:
            Dict containing recommendations and metadata
        """
        try:
            customers = self._load_customers()
            customer = customers.get(customer_id)
            
            if not customer:
                logger.warning(f"Customer {customer_id} not found")
                return self._get_default_recommendations("Customer not found")
            
            customer_embedding = customer.get('embedding_vector')
            if not customer_embedding:
                logger.warning(f"No embedding found for customer {customer_id}")
                return self._get_default_recommendations("No customer embedding")
            
            # Calculate recommendations
            recommendations = self._calculate_similarity_recommendations(
                customer_embedding, 
                customer.get('customer_metadata', {})
            )
            
            if not recommendations or len(recommendations) == 0:
                logger.warning(f"No recommendations found for customer {customer_id}")
                return self._get_default_recommendations("No similar products")
            
            # Generate explanation
            explanation = self._generate_explanation(
                customer.get('customer_metadata', {}), 
                recommendations
            )
            
            return {
                'customer_id': customer_id,
                'customer_type': 'existing',
                'recommendations': recommendations,
                'explanation': explanation,
                'processing_time_ms': 0,  # Will be calculated by caller
                'fallback_used': False
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations for {customer_id}: {str(e)}")
            return self._get_default_recommendations(f"Error: {str(e)}")
    
    def get_recommendations_for_new_customer(self, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommendations for a new customer profile
        
        Args:
            customer_profile (Dict): New customer profile data
            
        Returns:
            Dict containing recommendations and metadata
        """
        try:
            # Generate embedding for new customer
            customer_embedding = self.bedrock_client.generate_customer_embedding(customer_profile)
            
            if not customer_embedding:
                logger.warning("Failed to generate embedding for new customer")
                return self._get_default_recommendations("Failed to generate customer embedding")
            
            # Calculate recommendations
            recommendations = self._calculate_similarity_recommendations(
                customer_embedding, 
                customer_profile
            )
            
            # Check if similarity scores are good enough
            if not recommendations or self._should_use_fallback(recommendations):
                logger.info("Using fallback recommendations for new customer")
                return self._get_default_recommendations("Low similarity scores")
            
            # Generate explanation
            explanation = self._generate_explanation(customer_profile, recommendations)
            
            return {
                'customer_id': 'NEW_CUSTOMER',
                'customer_type': 'new',
                'recommendations': recommendations,
                'explanation': explanation,
                'processing_time_ms': 0,  # Will be calculated by caller
                'fallback_used': False
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations for new customer: {str(e)}")
            return self._get_default_recommendations(f"Error: {str(e)}")
    
    def _calculate_similarity_recommendations(self, customer_embedding: List[float], 
                                           customer_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate recommendations based on cosine similarity"""
        try:
            products = self._load_products()
            recommendations = []
            
            for product_id, product_data in products.items():
                # Skip out of stock products
                if not product_data.get('in_stock', True):
                    continue
                
                product_embedding = product_data.get('embedding_vector')
                if not product_embedding:
                    continue
                
                # Calculate similarity
                similarity = bedrock_cosine_similarity(customer_embedding, product_embedding)
                
                if similarity >= SIMILARITY_THRESHOLD:
                    recommendations.append({
                        'product_id': product_id,
                        'product_name': product_data.get('product_name', 'Unknown'),
                        'similarity_score': round(similarity, 4),
                        'category': product_data.get('category', 'Unknown'),
                        'subcategory': product_data.get('subcategory', ''),
                        'price': product_data.get('price', 0),
                        'brand': product_data.get('brand', 'Unknown'),
                        'rating': product_data.get('rating', 0),
                        'description': product_data.get('description', ''),
                        'features': product_data.get('features', [])
                    })
            
            # Sort by similarity score and return top recommendations
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            return recommendations[:MAX_RECOMMENDATIONS]
            
        except Exception as e:
            logger.error(f"Error calculating similarity recommendations: {str(e)}")
            return []
    
    def _should_use_fallback(self, recommendations: List[Dict[str, Any]]) -> bool:
        """Determine if fallback recommendations should be used"""
        if not recommendations:
            return True
        
        # Check if top recommendation has good similarity
        top_similarity = recommendations[0].get('similarity_score', 0)
        if top_similarity < SIMILARITY_THRESHOLD * 1.5:  # 1.5x threshold for fallback
            return True
        
        # Check if we have enough diverse recommendations
        categories = set(rec.get('category') for rec in recommendations)
        if len(categories) < 2 and len(recommendations) < 3:
            return True
        
        return False
    
    def _get_default_recommendations(self, reason: str = "Fallback") -> Dict[str, Any]:
        """Get default recommendations as fallback"""
        try:
            defaults = self._load_defaults()
            new_customer_recs = defaults.get('new_customer_recommendations', [])
            
            if not new_customer_recs:
                # Generate basic fallback from popular products
                popular_products = defaults.get('popular_products', [])
                new_customer_recs = popular_products[:DEFAULT_FALLBACK_COUNT]
            
            # Format recommendations
            recommendations = []
            products = self._load_products()
            
            for rec in new_customer_recs[:MAX_RECOMMENDATIONS]:
                product_id = rec.get('product_id')
                product_data = products.get(product_id, {})
                
                if product_data:
                    recommendations.append({
                        'product_id': product_id,
                        'product_name': product_data.get('product_name', rec.get('product_name', 'Unknown')),
                        'similarity_score': rec.get('similarity_score', 0.8),
                        'category': product_data.get('category', rec.get('category', 'Unknown')),
                        'subcategory': product_data.get('subcategory', ''),
                        'price': product_data.get('price', 0),
                        'brand': product_data.get('brand', 'Unknown'),
                        'rating': product_data.get('rating', 0),
                        'description': product_data.get('description', ''),
                        'features': product_data.get('features', []),
                        'reason': rec.get('reason', 'Popular choice')
                    })
            
            return {
                'customer_id': 'DEFAULT',
                'customer_type': 'fallback',
                'recommendations': recommendations,
                'explanation': f"Showing popular recommendations ({reason})",
                'processing_time_ms': 0,
                'fallback_used': True,
                'fallback_reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error getting default recommendations: {str(e)}")
            return {
                'customer_id': 'ERROR',
                'customer_type': 'error',
                'recommendations': [],
                'explanation': f"Unable to load recommendations: {str(e)}",
                'processing_time_ms': 0,
                'fallback_used': True,
                'fallback_reason': f"Error: {str(e)}"
            }
    
    def _generate_explanation(self, customer_profile: Dict[str, Any], 
                            recommendations: List[Dict[str, Any]]) -> str:
        """Generate explanation for recommendations"""
        try:
            explanation = self.bedrock_client.generate_explanation(
                customer_profile, 
                recommendations
            )
            
            if explanation:
                return explanation
            else:
                # Fallback explanation
                return self._generate_fallback_explanation(customer_profile, recommendations)
                
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return self._generate_fallback_explanation(customer_profile, recommendations)
    
    def _generate_fallback_explanation(self, customer_profile: Dict[str, Any], 
                                     recommendations: List[Dict[str, Any]]) -> str:
        """Generate a simple fallback explanation"""
        try:
            preferences = customer_profile.get('preferences', [])
            age = customer_profile.get('age', 'unknown')
            location = customer_profile.get('location', 'your area')
            
            if preferences:
                pref_text = ', '.join(preferences)
                return f"Based on your interest in {pref_text} and your profile, we've selected these highly-rated products that match your preferences. These items are popular among customers in {location} and have excellent reviews."
            else:
                return f"We've selected these popular, highly-rated products that are trending among customers in {location}. These items offer great value and quality."
                
        except Exception:
            return "These are our top recommended products based on customer preferences and ratings."
    
    def get_category_recommendations(self, category: str, limit: int = MAX_RECOMMENDATIONS) -> List[Dict[str, Any]]:
        """Get recommendations for a specific category"""
        try:
            products = self._load_products()
            category_products = []
            
            for product_id, product_data in products.items():
                if product_data.get('category') == category and product_data.get('in_stock', True):
                    category_products.append({
                        'product_id': product_id,
                        'product_name': product_data.get('product_name', 'Unknown'),
                        'similarity_score': product_data.get('rating', 0) / 5.0,  # Use rating as similarity
                        'category': category,
                        'subcategory': product_data.get('subcategory', ''),
                        'price': product_data.get('price', 0),
                        'brand': product_data.get('brand', 'Unknown'),
                        'rating': product_data.get('rating', 0),
                        'description': product_data.get('description', ''),
                        'features': product_data.get('features', [])
                    })
            
            # Sort by rating and return top items
            category_products.sort(key=lambda x: x['rating'], reverse=True)
            return category_products[:limit]
            
        except Exception as e:
            logger.error(f"Error getting category recommendations: {str(e)}")
            return []
    
    def get_similar_products(self, product_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get products similar to a given product"""
        try:
            products = self._load_products()
            target_product = products.get(product_id)
            
            if not target_product:
                return []
            
            target_embedding = target_product.get('embedding_vector')
            if not target_embedding:
                return []
            
            similar_products = []
            
            for pid, product_data in products.items():
                if pid == product_id:  # Skip the same product
                    continue
                
                if not product_data.get('in_stock', True):
                    continue
                
                product_embedding = product_data.get('embedding_vector')
                if not product_embedding:
                    continue
                
                similarity = bedrock_cosine_similarity(target_embedding, product_embedding)
                
                if similarity >= SIMILARITY_THRESHOLD:
                    similar_products.append({
                        'product_id': pid,
                        'product_name': product_data.get('product_name', 'Unknown'),
                        'similarity_score': round(similarity, 4),
                        'category': product_data.get('category', 'Unknown'),
                        'price': product_data.get('price', 0),
                        'rating': product_data.get('rating', 0)
                    })
            
            # Sort by similarity and return top items
            similar_products.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_products[:limit]
            
        except Exception as e:
            logger.error(f"Error getting similar products: {str(e)}")
            return []
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """Get analytics data for dashboard"""
        try:
            customer_analytics = self.data_manager.get_customer_analytics()
            product_analytics = self.data_manager.get_product_analytics()
            
            return {
                'customers': customer_analytics,
                'products': product_analytics,
                'system_health': {
                    'bedrock_connection': self.bedrock_client.test_connection(),
                    'data_integrity': self.data_manager.validate_data_integrity()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics data: {str(e)}")
            return {}
    
    def add_new_customer_to_system(self, customer_profile: Dict[str, Any]) -> str:
        """Add a new customer to the system with embedding"""
        try:
            # Generate customer ID
            customers = self._load_customers()
            customer_count = len(customers)
            customer_id = f"CUST_{customer_count + 1:03d}"
            
            # Generate embedding
            embedding = self.bedrock_client.generate_customer_embedding(customer_profile)
            
            if not embedding:
                raise Exception("Failed to generate customer embedding")
            
            # Create customer data
            customer_data = {
                'customer_id': customer_id,
                'embedding_vector': embedding,
                'customer_metadata': customer_profile
            }
            
            # Add to system
            self.data_manager.add_customer(customer_id, customer_data)
            
            # Refresh cache
            self.refresh_cache()
            
            logger.info(f"Added new customer {customer_id} to system")
            return customer_id
            
        except Exception as e:
            logger.error(f"Error adding new customer: {str(e)}")
            raise