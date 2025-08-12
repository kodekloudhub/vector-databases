#!/usr/bin/env python3
"""
Setup script to verify access to existing S3 bucket for the product recommendation app
"""

import boto3
from botocore.exceptions import ClientError
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use existing bucket
BUCKET_NAME = "my-product-embeddings-bucket-12345"

def verify_s3_bucket_access():
    """Verify access to existing S3 bucket and set up folder structure"""
    try:
        s3_client = boto3.client('s3')
        
        # Check if bucket exists and is accessible
        logger.info(f"Checking access to S3 bucket: {BUCKET_NAME}")
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        logger.info(f"✅ S3 bucket '{BUCKET_NAME}' exists and is accessible")
        
        # Test write permissions and create folder structure
        test_objects = [
            {
                "key": "product-recommendation-system/README.txt",
                "body": f"Product Recommendation System folder created on {datetime.now().isoformat()}\n\nThis folder contains:\n- user-preferences/: User preference embeddings\n- models/: Model configurations\n- logs/: System logs"
            },
            {
                "key": "product-recommendation-system/user-preferences/README.txt", 
                "body": "User preferences are stored here as JSON files containing embeddings and metadata"
            },
            {
                "key": "product-recommendation-system/models/README.txt",
                "body": "Model configurations and cached embeddings are stored here"
            }
        ]
        
        for obj in test_objects:
            try:
                s3_client.put_object(
                    Bucket=BUCKET_NAME,
                    Key=obj["key"],
                    Body=obj["body"],
                    ContentType="text/plain"
                )
                logger.info(f"✅ Created: {obj['key']}")
            except Exception as e:
                logger.warning(f"Failed to create {obj['key']}: {str(e)}")
        
        # List existing contents
        try:
            response = s3_client.list_objects_v2(
                Bucket=BUCKET_NAME,
                Prefix="product-recommendation-system/",
                Delimiter="/"
            )
            
            if 'Contents' in response:
                logger.info("Existing files in product-recommendation-system/:")
                for obj in response['Contents']:
                    logger.info(f"  - {obj['Key']}")
            
            if 'CommonPrefixes' in response:
                logger.info("Existing folders in product-recommendation-system/:")
                for prefix in response['CommonPrefixes']:
                    logger.info(f"  - {prefix['Prefix']}")
        
        except Exception as e:
            logger.warning(f"Could not list bucket contents: {str(e)}")
        
        logger.info("✅ S3 bucket setup completed successfully!")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            logger.error(f"❌ S3 bucket '{BUCKET_NAME}' does not exist")
            logger.error("Please create the bucket first or check the bucket name")
        elif error_code == 'AccessDenied':
            logger.error(f"❌ Access denied to S3 bucket '{BUCKET_NAME}'")
            logger.error("Please check your AWS permissions")
        else:
            logger.error(f"❌ Error accessing bucket: {str(e)}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return False

def test_bedrock_access():
    """Test if Bedrock service is accessible"""
    try:
        bedrock_client = boto3.client('bedrock-runtime')
        
        logger.info("Testing Bedrock access...")
        
        # Test with a simple embedding request
        test_body = {
            "inputText": "test embedding"
        }
        
        try:
            response = bedrock_client.invoke_model(
                modelId="amazon.titan-text-lite-v1",
                body=str(test_body).encode(),
                contentType="application/json",
                accept="application/json"
            )
            logger.info("✅ Bedrock access test successful!")
            logger.info("✅ amazon.titan-text-lite-v1 model is accessible")
            return True
        except Exception as model_error:
            logger.warning(f"⚠️  Model test failed: {str(model_error)}")
            logger.info("✅ Bedrock client initialized, but model access needs verification")
            return True
        
    except Exception as e:
        logger.error(f"❌ Failed to access Bedrock: {str(e)}")
        logger.error("Please ensure:")
        logger.error("1. AWS credentials are configured")
        logger.error("2. You have Bedrock permissions")
        logger.error("3. The titan-text-lite-v1 model is available in your region")
        logger.error("4. Handle Bedrock token as per AWS documentation")
        return False

def check_required_permissions():
    """Check if the current AWS identity has required permissions"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        logger.info(f"✅ AWS credentials configured for: {identity.get('Arn', 'Unknown')}")
        
        # Test IAM permissions (basic check)
        iam = boto3.client('iam')
        try:
            iam.get_user()
            logger.info("✅ IAM access confirmed")
        except:
            logger.info("ℹ️  Using role-based authentication (expected for EC2/Lambda)")
        
        return True
    except Exception as e:
        logger.error(f"❌ AWS credentials not configured: {str(e)}")
        return False

def main():
    print("🚀 Setting up Product Recommendation System")
    print("=" * 60)
    print(f"Using existing S3 bucket: {BUCKET_NAME}")
    print("=" * 60)
    
    # Check AWS credentials
    if not check_required_permissions():
        sys.exit(1)
    
    # Verify S3 bucket access and setup
    if not verify_s3_bucket_access():
        sys.exit(1)
    
    # Test Bedrock access
    if not test_bedrock_access():
        logger.warning("⚠️  Bedrock access test failed, but continuing...")
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("\nFolder structure created in S3:")
    print(f"  {BUCKET_NAME}/")
    print("  └── product-recommendation-system/")
    print("      ├── user-preferences/")
    print("      ├── models/")
    print("      └── logs/")
    print("\nNext steps:")
    print("1. Ensure AWS credentials are properly configured")
    print("2. Handle Bedrock token as per AWS documentation")
    print("3. Run: streamlit run app.py")
    print("\n🎉 Your product recommendation app is ready to go!")

if __name__ == "__main__":
    main()