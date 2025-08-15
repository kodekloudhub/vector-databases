import boto3
import json
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
import io
from config import (
    AWS_REGION, S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    S3_EMBEDDINGS_PATH, S3_DATA_PATH, S3_METADATA_FILE, 
    S3_EMBEDDINGS_FILE, S3_MANUAL_DATA_FILE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3VectorService:
    """
    Service for storing and retrieving embeddings and manual data from AWS S3.
    """
    
    def __init__(self, bucket_name: str = S3_BUCKET_NAME):
        """
        Initialize the S3 vector service.
        
        Args:
            bucket_name: Name of the S3 bucket to use
        """
        self.bucket_name = bucket_name
        self.s3_client = None
        self._initialize_s3_client()
    
    def _initialize_s3_client(self):
        """Initialize the S3 client with credentials."""
        try:
            # Try to create S3 client with explicit credentials if provided
            if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_REGION
                )
            else:
                # Use default credential chain (AWS CLI, IAM roles, etc.)
                self.s3_client = boto3.client('s3', region_name=AWS_REGION)
            
            logger.info(f"S3 client initialized for region: {AWS_REGION}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure AWS credentials.")
            raise
        except Exception as e:
            logger.error(f"Error initializing S3 client: {e}")
            raise
    
    def create_bucket_if_not_exists(self) -> bool:
        """
        Create S3 bucket if it doesn't exist.
        
        Returns:
            True if bucket exists or was created successfully
        """
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} already exists")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    if AWS_REGION == 'us-east-1':
                        # us-east-1 doesn't need LocationConstraint
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                        )
                    
                    logger.info(f"Created bucket: {self.bucket_name}")
                    return True
                    
                except ClientError as create_error:
                    logger.error(f"Error creating bucket: {create_error}")
                    return False
            else:
                logger.error(f"Error checking bucket: {e}")
                return False
    
    def upload_embeddings(self, embeddings: np.ndarray, key: str = S3_EMBEDDINGS_FILE) -> bool:
        """
        Upload embeddings array to S3.
        
        Args:
            embeddings: Numpy array of embeddings
            key: S3 key for the embeddings file
            
        Returns:
            True if upload successful
        """
        try:
            # Convert numpy array to bytes
            buffer = io.BytesIO()
            np.save(buffer, embeddings)
            buffer.seek(0)
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                buffer, 
                self.bucket_name, 
                key,
                ExtraArgs={'ContentType': 'application/octet-stream'}
            )
            
            logger.info(f"Uploaded embeddings to s3://{self.bucket_name}/{key}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading embeddings: {e}")
            return False
    
    def download_embeddings(self, key: str = S3_EMBEDDINGS_FILE) -> Optional[np.ndarray]:
        """
        Download embeddings array from S3.
        
        Args:
            key: S3 key for the embeddings file
            
        Returns:
            Numpy array of embeddings or None if error
        """
        try:
            # Download from S3
            buffer = io.BytesIO()
            self.s3_client.download_fileobj(self.bucket_name, key, buffer)
            buffer.seek(0)
            
            # Load numpy array
            embeddings = np.load(buffer)
            logger.info(f"Downloaded embeddings from s3://{self.bucket_name}/{key}, shape: {embeddings.shape}")
            return embeddings
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Embeddings file not found: {key}")
            else:
                logger.error(f"Error downloading embeddings: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            return None
    
    def upload_json_data(self, data: Dict[str, Any], key: str) -> bool:
        """
        Upload JSON data to S3.
        
        Args:
            data: Dictionary to upload as JSON
            key: S3 key for the JSON file
            
        Returns:
            True if upload successful
        """
        try:
            json_string = json.dumps(data, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_string,
                ContentType='application/json'
            )
            
            logger.info(f"Uploaded JSON data to s3://{self.bucket_name}/{key}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading JSON data: {e}")
            return False
    
    def download_json_data(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Download JSON data from S3.
        
        Args:
            key: S3 key for the JSON file
            
        Returns:
            Dictionary with JSON data or None if error
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            json_string = response['Body'].read().decode('utf-8')
            data = json.loads(json_string)
            
            logger.info(f"Downloaded JSON data from s3://{self.bucket_name}/{key}")
            return data
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"JSON file not found: {key}")
            else:
                logger.error(f"Error downloading JSON data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing JSON data: {e}")
            return None
    
    def upload_manual_data(self, manual_sections: List[Dict[str, Any]]) -> bool:
        """
        Upload car manual sections to S3.
        
        Args:
            manual_sections: List of manual sections
            
        Returns:
            True if upload successful
        """
        data = {"sections": manual_sections}
        return self.upload_json_data(data, S3_MANUAL_DATA_FILE)
    
    def download_manual_data(self) -> Optional[List[Dict[str, Any]]]:
        """
        Download car manual sections from S3.
        
        Returns:
            List of manual sections or None if error
        """
        data = self.download_json_data(S3_MANUAL_DATA_FILE)
        if data:
            return data.get('sections', [])
        return None
    
    def upload_metadata(self, metadata: List[Dict[str, Any]]) -> bool:
        """
        Upload section metadata to S3.
        
        Args:
            metadata: List of section metadata
            
        Returns:
            True if upload successful
        """
        data = {"metadata": metadata}
        return self.upload_json_data(data, S3_METADATA_FILE)
    
    def download_metadata(self) -> Optional[List[Dict[str, Any]]]:
        """
        Download section metadata from S3.
        
        Returns:
            List of section metadata or None if error
        """
        data = self.download_json_data(S3_METADATA_FILE)
        if data:
            return data.get('metadata', [])
        return None
    
    def list_bucket_contents(self, prefix: str = "") -> List[str]:
        """
        List contents of the S3 bucket.
        
        Args:
            prefix: Prefix to filter objects
            
        Returns:
            List of object keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            objects = []
            if 'Contents' in response:
                objects = [obj['Key'] for obj in response['Contents']]
            
            logger.info(f"Found {len(objects)} objects with prefix '{prefix}'")
            return objects
            
        except Exception as e:
            logger.error(f"Error listing bucket contents: {e}")
            return []
    
    def delete_object(self, key: str) -> bool:
        """
        Delete an object from S3.
        
        Args:
            key: S3 key of the object to delete
            
        Returns:
            True if deletion successful
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted object: s3://{self.bucket_name}/{key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting object: {e}")
            return False
    
    def check_connection(self) -> Dict[str, Any]:
        """
        Check S3 connection and bucket access.
        
        Returns:
            Dictionary with connection status
        """
        status = {
            "connected": False,
            "bucket_exists": False,
            "can_read": False,
            "can_write": False,
            "error": None
        }
        
        try:
            # Test basic connection
            self.s3_client.list_buckets()
            status["connected"] = True
            
            # Test bucket access
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                status["bucket_exists"] = True
                
                # Test read access
                try:
                    self.s3_client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
                    status["can_read"] = True
                except Exception:
                    pass
                
                # Test write access
                try:
                    test_key = "test_connection.txt"
                    self.s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=test_key,
                        Body="test"
                    )
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=test_key)
                    status["can_write"] = True
                except Exception:
                    pass
                    
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    status["error"] = "Bucket does not exist"
                else:
                    status["error"] = f"Bucket access error: {e}"
            
        except Exception as e:
            status["error"] = f"Connection error: {e}"
        
        return status

if __name__ == "__main__":
    # Test the S3 vector service
    s3_service = S3VectorService()
    
    # Check connection
    connection_status = s3_service.check_connection()
    print(f"Connection status: {connection_status}")
    
    if connection_status["connected"]:
        # Test bucket creation
        bucket_created = s3_service.create_bucket_if_not_exists()
        print(f"Bucket ready: {bucket_created}")
        
        # Test uploading dummy data
        test_data = {"test": "data"}
        upload_success = s3_service.upload_json_data(test_data, "test/test.json")
        print(f"Upload test: {upload_success}")
        
        if upload_success:
            # Test downloading
            downloaded_data = s3_service.download_json_data("test/test.json")
            print(f"Download test: {downloaded_data}")
            
            # Clean up
            s3_service.delete_object("test/test.json")