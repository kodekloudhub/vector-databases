import streamlit as st
import boto3
import json
import numpy as np
from datetime import datetime
import pickle
import hashlib
import logging
import uuid
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AWS Configuration
BUCKET_NAME = "my-product-embeddings-bucket-12345"
BEDROCK_MODEL_ID = "amazon.titan-text-lite-v1"

# Alternative model IDs to try if the primary one fails
ALTERNATIVE_MODEL_IDS = [
    "amazon.titan-embed-text-v1",
    "amazon.titan-embed-text-v2", 
    "amazon.titan-text-lite-v1"
]

# Initialize AWS clients
@st.cache_resource
def init_aws_clients():
    try:
        logger.info("Initializing AWS clients...")
        
        # Get current AWS region
        session = boto3.Session()
        current_region = session.region_name or 'us-east-1'
        logger.info(f"Using AWS region: {current_region}")
        
        s3_client = boto3.client('s3', region_name=current_region)
        bedrock_client = boto3.client('bedrock-runtime', region_name=current_region)
        
        logger.info("AWS clients initialized successfully")
        return s3_client, bedrock_client, current_region
    except Exception as e:
        logger.error(f"Failed to initialize AWS clients: {str(e)}")
        st.error(f"Failed to initialize AWS clients: {str(e)}")
        return None, None, None

# Sample products - expanded to 10 items
PRODUCTS = [
    "Wireless Bluetooth Headphones",
    "Smart Fitness Tracker",
    "Portable Phone Charger",
    "Ergonomic Laptop Stand",
    "Premium Coffee Beans",
    "Wireless Mouse",
    "USB-C Hub",
    "Blue Light Blocking Glasses",
    "Desk Organizer",
    "Portable Bluetooth Speaker"
]

def verify_s3_bucket_access(s3_client):
    """Verify access to existing S3 bucket"""
    try:
        logger.info(f"Verifying access to existing S3 bucket '{BUCKET_NAME}'...")
        
        # Check if bucket exists and is accessible
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        logger.info(f"Successfully verified access to S3 bucket '{BUCKET_NAME}'")
        
        # Test write permissions by trying to create a test object
        test_key = "product-recommendation-system/test-access.txt"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=test_key,
            Body="Test access for product recommendation system",
            ContentType="text/plain"
        )
        logger.info("Write permissions verified")
        
        # Clean up test object
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=test_key)
        logger.info("Test cleanup completed")
        
        st.success(f"✅ S3 bucket '{BUCKET_NAME}' is ready!")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            error_msg = f"❌ S3 bucket '{BUCKET_NAME}' does not exist"
        elif error_code == 'AccessDenied':
            error_msg = f"❌ Access denied to S3 bucket '{BUCKET_NAME}'. Check your permissions."
        else:
            error_msg = f"❌ Error accessing bucket: {str(e)}"
        
        logger.error(error_msg)
        st.error(error_msg)
        return False
        
    except Exception as e:
        error_msg = f"❌ Unexpected error accessing bucket: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return False

def get_text_embedding(bedrock_client, text, model_id=None):
    """Generate embedding using Amazon Titan"""
    if model_id is None:
        model_id = BEDROCK_MODEL_ID
        
    try:
        logger.info(f"Generating embedding for text: {text[:50]}... using model: {model_id}")
        
        # Correct format for Titan Text models
        body = json.dumps({
            "inputText": text
        })
        
        logger.info(f"Sending request to Bedrock with model: {model_id}")
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=body,
            contentType="application/json",
            accept="application/json"
        )
        
        # Read the response
        response_body = json.loads(response['body'].read())
        logger.info(f"Bedrock response keys: {list(response_body.keys())}")
        
        # Try different possible response formats
        embedding = None
        if 'embedding' in response_body:
            embedding = response_body['embedding']
        elif 'embeddings' in response_body:
            # Handle array of embeddings
            if isinstance(response_body['embeddings'], list) and len(response_body['embeddings']) > 0:
                embedding = response_body['embeddings'][0]
            else:
                embedding = response_body['embeddings']
        elif 'results' in response_body and len(response_body['results']) > 0:
            if 'embedding' in response_body['results'][0]:
                embedding = response_body['results'][0]['embedding']
        
        if embedding and len(embedding) > 0:
            logger.info(f"Successfully generated embedding with {len(embedding)} dimensions using {model_id}")
            return embedding
        else:
            logger.error(f"No valid embedding found in response. Full response: {response_body}")
            
            # Try alternative models if the primary one failed
            if model_id == BEDROCK_MODEL_ID:
                logger.info("Trying alternative models...")
                for alt_model in ALTERNATIVE_MODEL_IDS:
                    if alt_model != model_id:
                        logger.info(f"Trying alternative model: {alt_model}")
                        result = get_text_embedding(bedrock_client, text, alt_model)
                        if result:
                            logger.info(f"Success with alternative model: {alt_model}")
                            return result
            
            # If all models failed, show error
            if 'message' in response_body:
                st.error(f"Bedrock error: {response_body['message']}")
            else:
                st.error(f"No embedding generated. Response: {response_body}")
            return None
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        logger.error(f"Bedrock ClientError with model {model_id}: {error_code} - {error_message}")
        
        # Try alternative models for certain errors
        if model_id == BEDROCK_MODEL_ID and error_code in ['ValidationException', 'ResourceNotFoundException']:
            logger.info(f"Model {model_id} failed with {error_code}, trying alternatives...")
            for alt_model in ALTERNATIVE_MODEL_IDS:
                if alt_model != model_id:
                    logger.info(f"Trying alternative model: {alt_model}")
                    result = get_text_embedding(bedrock_client, text, alt_model)
                    if result:
                        logger.info(f"Success with alternative model: {alt_model}")
                        return result
        
        # Show appropriate error message
        if error_code == 'ValidationException':
            error_msg = f"Model validation error: {error_message}. The model '{model_id}' may not be available in your region."
        elif error_code == 'AccessDeniedException':
            error_msg = f"Access denied: {error_message}. Check your Bedrock permissions for model '{model_id}'."
        elif error_code == 'ResourceNotFoundException':
            error_msg = f"Model not found: {error_message}. The model '{model_id}' may not exist or be available in your region."
        elif error_code == 'ThrottlingException':
            error_msg = f"Request throttled: {error_message}. Please try again in a moment."
        else:
            error_msg = f"Bedrock API error ({error_code}): {error_message}"
        
        logger.error(error_msg)
        st.error(error_msg)
        return None
        
    except Exception as e:
        error_msg = f"Failed to generate embedding with model {model_id}: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return None

def save_user_preferences(s3_client, bedrock_client, user_id, selected_products):
    """Save user preferences as embeddings to S3"""
    if not selected_products:
        logger.warning("No products selected, skipping save")
        return
    
    try:
        logger.info(f"Saving preferences for user {user_id}: {selected_products}")
        
        # Create a combined text from selected products
        preference_text = " ".join(selected_products)
        logger.info(f"Combined preference text: {preference_text}")
        
        # Generate embedding
        embedding = get_text_embedding(bedrock_client, preference_text)
        
        if embedding:
            # Prepare user data
            user_data = {
                "user_id": user_id,
                "selected_products": selected_products,
                "embedding": embedding,
                "timestamp": datetime.now().isoformat(),
                "preference_text": preference_text
            }
            
            # Save to S3 with organized folder structure
            key = f"product-recommendation-system/user-preferences/{user_id}/{user_id}_preferences.json"
            logger.info(f"Saving to S3 with key: {key}")
            
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=json.dumps(user_data, indent=2),
                ContentType="application/json"
            )
            
            success_msg = f"Saved preferences for user: {user_id}"
            logger.info(success_msg)
            st.success(success_msg)
        else:
            logger.error("Failed to generate embedding, cannot save preferences")
        
    except ClientError as e:
        error_msg = f"S3 error saving preferences: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
    except Exception as e:
        error_msg = f"Failed to save preferences: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)

def load_user_preferences(s3_client, user_id):
    """Load user preferences from S3"""
    try:
        key = f"product-recommendation-system/user-preferences/{user_id}/{user_id}_preferences.json"
        logger.info(f"Loading preferences for user {user_id} from S3 key: {key}")
        
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
        user_data = json.loads(response['Body'].read())
        
        logger.info(f"Successfully loaded preferences for user {user_id}")
        logger.info(f"Previous selections: {user_data.get('selected_products', [])}")
        
        return user_data
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            logger.info(f"No previous preferences found for user {user_id}")
            return None
        elif error_code == 'NoSuchBucket':
            logger.error(f"S3 bucket {BUCKET_NAME} does not exist")
            st.error(f"S3 bucket {BUCKET_NAME} does not exist. Please run setup first.")
            return None
        else:
            error_msg = f"S3 error loading preferences: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
            return None
    except Exception as e:
        error_msg = f"Failed to load preferences: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return None

def calculate_similarity(embedding1, embedding2):
    """Calculate cosine similarity between two embeddings"""
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            logger.warning("Zero norm detected in similarity calculation")
            return 0
        
        similarity = dot_product / (norm1 * norm2)
        logger.debug(f"Calculated similarity: {similarity:.4f}")
        return similarity
    except Exception as e:
        error_msg = f"Error calculating similarity: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return 0

def get_recommendations(bedrock_client, user_embedding):
    """Generate product recommendations based on user embedding"""
    try:
        logger.info("Generating product recommendations...")
        recommendations = []
        
        for product in PRODUCTS:
            logger.info(f"Processing product: {product}")
            product_embedding = get_text_embedding(bedrock_client, product)
            
            if product_embedding:
                similarity = calculate_similarity(user_embedding, product_embedding)
                recommendations.append((product, similarity))
                logger.info(f"Product: {product}, Similarity: {similarity:.4f}")
            else:
                logger.warning(f"Failed to get embedding for product: {product}")
        
        # Sort by similarity score (descending)
        recommendations.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        return recommendations
    
    except Exception as e:
        error_msg = f"Failed to generate recommendations: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return []

def test_bedrock_connection(bedrock_client):
    """Test Bedrock connection with a simple embedding request"""
    try:
        logger.info("Testing Bedrock connection...")
        test_text = "hello world"
        embedding = get_text_embedding(bedrock_client, test_text)
        
        if embedding:
            logger.info("✅ Bedrock connection test successful!")
            st.success("✅ Bedrock connection verified!")
            return True
        else:
            logger.error("❌ Bedrock connection test failed - no embedding returned")
            st.error("❌ Bedrock connection test failed - no embedding returned")
            return False
    except Exception as e:
        logger.error(f"❌ Bedrock connection test failed: {str(e)}")
        st.error(f"❌ Bedrock connection test failed: {str(e)}")
        return False
    """Generate a unique user ID from username"""
    user_id = hashlib.md5(username.encode()).hexdigest()[:12]
    logger.info(f"Generated user ID for '{username}': {user_id}")
    return user_id

def main():
    st.title("🛍️ Product Recommendation System")
    st.write("Powered by AWS Bedrock and S3")
    
    # Add debug info in sidebar
    with st.sidebar:
        st.header("Debug Info")
        st.write(f"Bucket: {BUCKET_NAME}")
        st.write(f"Model: {BEDROCK_MODEL_ID}")
        
        if st.button("Test Bedrock Connection"):
            test_bedrock_connection(bedrock_client)
            
        st.write("---")
        st.subheader("Manual Embedding Test")
        test_text = st.text_input("Test text:", value="hello world")
        if st.button("Generate Test Embedding"):
            with st.spinner("Testing..."):
                embedding = get_text_embedding(bedrock_client, test_text)
                if embedding:
                    st.success(f"✅ Success! Generated {len(embedding)}-dimensional embedding")
                    st.write(f"First 5 values: {embedding[:5]}")
                else:
                    st.error("❌ Failed to generate embedding")
        
        if st.button("Show Logs"):
            st.info("Check console for detailed logs")
    
    logger.info("Starting Product Recommendation System")
    
    # Initialize AWS clients
    s3_client, bedrock_client, region = init_aws_clients()
    
    if not s3_client or not bedrock_client:
        logger.error("Failed to initialize AWS clients")
        st.error("Failed to initialize AWS clients. Please check your credentials.")
        return
    
    # Verify S3 bucket access
    if not verify_s3_bucket_access(s3_client):
        logger.error("Failed to access S3 bucket")
        st.error("Cannot proceed without S3 bucket access. Please check your AWS permissions.")
        return
    
    # User authentication (simple)
    with st.sidebar:
        st.header("User Management")
        
        # Show different content based on login status
        if not st.session_state.get('logged_in', False):
            # Show login form only when not logged in
            username = st.text_input("Username", value="demo_user")
            
            if st.button("Login", type="primary"):
                logger.info(f"User login attempt: {username}")
                st.session_state.logged_in = True
                st.session_state.user_id = generate_user_id(username)
                st.session_state.username = username
                logger.info(f"User {username} logged in successfully")
                st.rerun()
        else:
            # Show user info and logout when logged in
            st.success(f"Logged in as: **{st.session_state.username}**")
            st.write(f"User ID: `{st.session_state.user_id}`")
            
            if st.button("Logout", type="secondary"):
                logger.info(f"User logout: {st.session_state.get('username', 'Unknown')}")
                if 'selected_products' in st.session_state and st.session_state.selected_products:
                    logger.info("Saving preferences on logout")
                    save_user_preferences(
                        s3_client, 
                        bedrock_client, 
                        st.session_state.user_id,
                        st.session_state.selected_products
                    )
                st.session_state.clear()
                logger.info("User logged out and session cleared")
                st.rerun()
    
    # Check if user is logged in
    if not st.session_state.get('logged_in', False):
        st.warning("Please login to continue")
        return
    
    logger.info(f"User {st.session_state.username} is logged in")
    st.success(f"Welcome back, {st.session_state.username}! 👋")
    
    # Load existing user preferences
    user_data = load_user_preferences(s3_client, st.session_state.user_id)
    
    # Initialize session state
    if 'selected_products' not in st.session_state:
        st.session_state.selected_products = []
        logger.info("Initialized empty product selection")
    
    # Create main layout with columns
    if user_data and 'embedding' in user_data:
        # Two column layout: Products on left, Recommendations on right
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Product Selection Section
            st.header("🛒 Browse All Products")
            st.write("Click on products you're interested in:")
            
            # Display products in a grid (2 columns within the left column)
            product_col1, product_col2 = st.columns(2)
            
            for i, product in enumerate(PRODUCTS):
                with product_col1 if i % 2 == 0 else product_col2:
                    is_selected = product in st.session_state.selected_products
                    button_text = f"✅ {product}" if is_selected else product
                    
                    if st.button(button_text, key=f"product_{i}", 
                                type="primary" if is_selected else "secondary"):
                        if product in st.session_state.selected_products:
                            st.session_state.selected_products.remove(product)
                            logger.info(f"User deselected product: {product}")
                            st.success(f"Removed {product}")
                        else:
                            st.session_state.selected_products.append(product)
                            logger.info(f"User selected product: {product}")
                            st.success(f"Added {product}")
                        st.rerun()
        
        with col2:
            # Recommendations Section
            logger.info("Showing personalized recommendations for returning user")
            st.header("🎯 Recommended for You")
            st.write(f"**Based on your previous selections:**")
            for prev_product in user_data['selected_products']:
                st.write(f"• {prev_product}")
            
            st.write("---")
            
            with st.spinner("Generating personalized recommendations..."):
                recommendations = get_recommendations(bedrock_client, user_data['embedding'])
            
            if recommendations:
                logger.info(f"Displaying {len(recommendations)} recommendations")
                st.write("**Top Recommendations:**")
                
                for i, (product, similarity) in enumerate(recommendations[:5]):
                    with st.container():
                        st.write(f"**{i+1}. {product}**")
                        st.write(f"Match Score: {similarity:.2f}")
                        if st.button(f"Select", key=f"rec_{i}", type="secondary", use_container_width=True):
                            if product not in st.session_state.selected_products:
                                st.session_state.selected_products.append(product)
                                logger.info(f"User selected recommended product: {product}")
                                st.success(f"Added {product}!")
                                st.rerun()
                            else:
                                st.info(f"Already selected!")
                        st.write("")  # Add spacing
            else:
                logger.warning("No recommendations generated")
                st.error("Unable to generate recommendations at this time.")
    
    else:
        # First time user - single column layout
        logger.info("No previous preferences found for user - showing first-time experience")
        st.info("👋 Welcome! This appears to be your first visit. Browse and select products you're interested in below.")
        
        # Product Selection Section
        st.header("🛒 Browse All Products")
        st.write("Click on products you're interested in:")
        
        # Display products in a 3-column grid for better space utilization
        col1, col2, col3 = st.columns(3)
        
        for i, product in enumerate(PRODUCTS):
            with col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3:
                is_selected = product in st.session_state.selected_products
                button_text = f"✅ {product}" if is_selected else product
                
                if st.button(button_text, key=f"product_{i}", 
                            type="primary" if is_selected else "secondary",
                            use_container_width=True):
                    if product in st.session_state.selected_products:
                        st.session_state.selected_products.remove(product)
                        logger.info(f"User deselected product: {product}")
                        st.success(f"Removed {product}")
                    else:
                        st.session_state.selected_products.append(product)
                        logger.info(f"User selected product: {product}")
                        st.success(f"Added {product}")
                    st.rerun()
    
    # Show current selections (always at the bottom)
    if st.session_state.selected_products:
        st.write("---")
        st.header("📋 Your Current Selections")
        
        # Display selections in a nice format
        selection_cols = st.columns(3)
        for i, product in enumerate(st.session_state.selected_products):
            with selection_cols[i % 3]:
                st.write(f"• {product}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save My Preferences Now", type="primary"):
                logger.info("Manual save triggered by user")
                save_user_preferences(
                    s3_client, 
                    bedrock_client, 
                    st.session_state.user_id,
                    st.session_state.selected_products
                )
        
        with col2:
            if st.button("🗑️ Clear All Selections", type="secondary"):
                logger.info("User cleared all selections")
                st.session_state.selected_products = []
                st.rerun()

if __name__ == "__main__":
    main()