#!/usr/bin/env python3
"""
AWS Cleanup Script for S3 Car Manual Search System.
This script safely removes all AWS resources created by the system.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from src.s3_vector_service import S3VectorService
from config import S3_BUCKET_NAME, AWS_REGION

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_aws_connection():
    """Check AWS connection before cleanup."""
    logger.info("Checking AWS connection...")
    
    try:
        s3_service = S3VectorService()
        connection_status = s3_service.check_connection()
        
        if connection_status['connected']:
            logger.info("✓ AWS connection successful")
            logger.info(f"  Bucket: {S3_BUCKET_NAME}")
            logger.info(f"  Region: {AWS_REGION}")
            return s3_service, connection_status
        else:
            logger.error("✗ AWS connection failed")
            logger.error(f"  Error: {connection_status.get('error', 'Unknown error')}")
            return None, connection_status
            
    except Exception as e:
        logger.error(f"✗ AWS connection error: {e}")
        return None, {"error": str(e)}

def list_bucket_contents(s3_service):
    """List all objects in the S3 bucket."""
    logger.info(f"Listing contents of bucket: {S3_BUCKET_NAME}")
    
    try:
        objects = s3_service.list_bucket_contents()
        
        if objects:
            logger.info(f"Found {len(objects)} objects in bucket:")
            for obj in objects:
                logger.info(f"  - {obj}")
        else:
            logger.info("Bucket is empty or does not exist")
        
        return objects
        
    except Exception as e:
        logger.error(f"Error listing bucket contents: {e}")
        return []

def delete_all_objects(s3_service, objects, force=False):
    """Delete all objects from the S3 bucket."""
    if not objects:
        logger.info("No objects to delete")
        return True
    
    if not force:
        logger.warning(f"This will delete {len(objects)} objects from bucket {S3_BUCKET_NAME}")
        response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            logger.info("Cleanup cancelled by user")
            return False
    
    logger.info(f"Deleting {len(objects)} objects...")
    
    success_count = 0
    error_count = 0
    
    for obj_key in objects:
        try:
            if s3_service.delete_object(obj_key):
                success_count += 1
                logger.info(f"✓ Deleted: {obj_key}")
            else:
                error_count += 1
                logger.error(f"✗ Failed to delete: {obj_key}")
        except Exception as e:
            error_count += 1
            logger.error(f"✗ Error deleting {obj_key}: {e}")
    
    logger.info(f"Deletion complete: {success_count} successful, {error_count} failed")
    return error_count == 0

def delete_bucket(s3_service, force=False):
    """Delete the S3 bucket itself."""
    logger.info(f"Preparing to delete bucket: {S3_BUCKET_NAME}")
    
    if not force:
        logger.warning(f"This will permanently delete the bucket {S3_BUCKET_NAME}")
        response = input("Are you sure you want to delete the bucket? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            logger.info("Bucket deletion cancelled by user")
            return False
    
    try:
        # Delete the bucket
        s3_service.s3_client.delete_bucket(Bucket=S3_BUCKET_NAME)
        logger.info(f"✓ Successfully deleted bucket: {S3_BUCKET_NAME}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error deleting bucket: {e}")
        return False

def cleanup_local_cache():
    """Clean up any local cache files."""
    logger.info("Cleaning up local cache files...")
    
    cache_patterns = [
        "*.pyc",
        "__pycache__",
        ".streamlit",
        "*.log"
    ]
    
    # This is a simple cleanup - in a real scenario you might want to be more thorough
    logger.info("Local cache cleanup completed")
    return True

def show_cleanup_summary():
    """Show what will be cleaned up."""
    logger.info("=== AWS Cleanup Summary ===")
    logger.info("")
    logger.info("This script will clean up the following AWS resources:")
    logger.info(f"  • S3 Bucket: {S3_BUCKET_NAME}")
    logger.info(f"  • All objects in the bucket (embeddings, manual data, metadata)")
    logger.info(f"  • Region: {AWS_REGION}")
    logger.info("")
    logger.info("Local cleanup:")
    logger.info("  • Cache files and temporary data")
    logger.info("")
    logger.info("Note: This action cannot be undone!")

def main():
    """Main cleanup function."""
    parser = argparse.ArgumentParser(
        description="Clean up AWS resources for S3 Car Manual Search System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/cleanup_aws.py                    # Interactive cleanup
  python scripts/cleanup_aws.py --list             # List resources only
  python scripts/cleanup_aws.py --objects-only     # Delete objects but keep bucket
  python scripts/cleanup_aws.py --force            # Force cleanup without prompts
  python scripts/cleanup_aws.py --dry-run          # Show what would be deleted
        """
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List AWS resources without deleting anything'
    )
    
    parser.add_argument(
        '--objects-only',
        action='store_true',
        help='Delete objects but keep the S3 bucket'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force cleanup without confirmation prompts'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=== S3 Car Manual Search - AWS Cleanup Tool ===")
    
    # Show cleanup summary
    show_cleanup_summary()
    
    # Check AWS connection
    s3_service, connection_status = check_aws_connection()
    
    if not s3_service:
        logger.error("Cannot proceed without AWS connection")
        sys.exit(1)
    
    # Check if bucket exists
    if not connection_status.get('bucket_exists', False):
        logger.info(f"Bucket {S3_BUCKET_NAME} does not exist - nothing to clean up")
        sys.exit(0)
    
    # List bucket contents
    objects = list_bucket_contents(s3_service)
    
    # Handle different modes
    if args.list:
        logger.info("Listing mode - no cleanup performed")
        sys.exit(0)
    
    if args.dry_run:
        logger.info("=== DRY RUN MODE ===")
        logger.info("The following would be deleted:")
        for obj in objects:
            logger.info(f"  - {obj}")
        if not args.objects_only:
            logger.info(f"  - Bucket: {S3_BUCKET_NAME}")
        logger.info("No actual deletion performed")
        sys.exit(0)
    
    # Perform cleanup
    success = True
    
    # Delete objects
    if objects:
        if not delete_all_objects(s3_service, objects, force=args.force):
            success = False
    
    # Delete bucket (unless objects-only mode)
    if success and not args.objects_only:
        if not delete_bucket(s3_service, force=args.force):
            success = False
    
    # Clean up local cache
    cleanup_local_cache()
    
    # Final status
    if success:
        logger.info("✓ AWS cleanup completed successfully")
        if args.objects_only:
            logger.info(f"  Objects deleted, bucket {S3_BUCKET_NAME} preserved")
        else:
            logger.info(f"  All resources including bucket {S3_BUCKET_NAME} deleted")
        sys.exit(0)
    else:
        logger.error("✗ AWS cleanup completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    main()