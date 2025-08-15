#!/usr/bin/env python3
"""
CLI tool to upload car manual data to S3 and generate embeddings.
This script initializes the search system by processing manual sections,
generating embeddings, and uploading everything to S3.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from src.search_service import SearchService
from src.manual_processor import ManualProcessor
from src.embedding_service import EmbeddingService
from src.s3_vector_service import S3VectorService
from config import LOCAL_MANUAL_FILE, S3_BUCKET_NAME

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_prerequisites():
    """Check if all prerequisites are met before uploading."""
    logger.info("Checking prerequisites...")
    
    # Check if manual data file exists
    if not os.path.exists(LOCAL_MANUAL_FILE):
        logger.error(f"Manual data file not found: {LOCAL_MANUAL_FILE}")
        return False
    
    # Test S3 connection
    s3_service = S3VectorService()
    connection_status = s3_service.check_connection()
    
    if not connection_status["connected"]:
        logger.error(f"S3 connection failed: {connection_status.get('error', 'Unknown error')}")
        logger.error("Please check your AWS credentials and configuration")
        return False
    
    logger.info("✓ Prerequisites check passed")
    return True

def upload_manual_data(force_regenerate=False):
    """
    Upload manual data to S3 with embeddings.
    
    Args:
        force_regenerate: If True, regenerate embeddings even if they exist
    """
    try:
        logger.info("Starting manual data upload process...")
        
        # Initialize search service
        search_service = SearchService()
        
        # Check if data already exists in S3
        if not force_regenerate:
            logger.info("Checking if data already exists in S3...")
            embeddings = search_service.s3_service.download_embeddings()
            metadata = search_service.s3_service.download_metadata()
            manual_data = search_service.s3_service.download_manual_data()
            
            if embeddings is not None and metadata is not None and manual_data is not None:
                logger.info("Data already exists in S3. Use --force to regenerate.")
                logger.info(f"Found {len(manual_data)} sections with embeddings shape: {embeddings.shape}")
                return True
        
        # Initialize data (this will generate embeddings and upload to S3)
        logger.info("Initializing search service data...")
        success = search_service.initialize_data()
        
        if success:
            logger.info("✓ Manual data uploaded successfully!")
            
            # Verify upload
            status = search_service.get_system_status()
            logger.info(f"System status: {status}")
            
            return True
        else:
            logger.error("✗ Failed to upload manual data")
            return False
            
    except Exception as e:
        logger.error(f"Error uploading manual data: {e}")
        return False

def test_search_functionality():
    """Test the search functionality after upload."""
    try:
        logger.info("Testing search functionality...")
        
        search_service = SearchService()
        
        # Test queries
        test_queries = [
            "oil change",
            "brake noise",
            "engine won't start",
            "battery dead",
            "AC not cooling"
        ]
        
        for query in test_queries:
            logger.info(f"Testing query: '{query}'")
            results = search_service.search(query, top_k=3)
            
            if results:
                logger.info(f"  Found {len(results)} results:")
                for i, result in enumerate(results[:2], 1):
                    title = result['metadata']['title']
                    score = result['similarity_score']
                    logger.info(f"    {i}. {title} (Score: {score:.3f})")
            else:
                logger.warning(f"  No results found for '{query}'")
        
        logger.info("✓ Search functionality test completed")
        return True
        
    except Exception as e:
        logger.error(f"Error testing search functionality: {e}")
        return False

def show_system_info():
    """Display system information and statistics."""
    try:
        logger.info("Gathering system information...")
        
        # Manual processor info
        processor = ManualProcessor()
        sections = processor.load_manual_data()
        
        logger.info(f"Manual Data:")
        logger.info(f"  Total sections: {len(sections)}")
        logger.info(f"  Categories: {processor.get_categories()}")
        logger.info(f"  Category counts: {processor.get_section_count_by_category()}")
        
        # Embedding service info
        embedding_service = EmbeddingService()
        model_info = embedding_service.get_model_info()
        
        logger.info(f"Embedding Model:")
        logger.info(f"  Model: {model_info.get('model_name', 'Unknown')}")
        logger.info(f"  Dimension: {model_info.get('embedding_dimension', 'Unknown')}")
        logger.info(f"  Device: {model_info.get('device', 'Unknown')}")
        
        # S3 service info
        s3_service = S3VectorService()
        connection_status = s3_service.check_connection()
        
        logger.info(f"S3 Configuration:")
        logger.info(f"  Bucket: {S3_BUCKET_NAME}")
        logger.info(f"  Connected: {connection_status['connected']}")
        logger.info(f"  Bucket exists: {connection_status['bucket_exists']}")
        logger.info(f"  Can read: {connection_status['can_read']}")
        logger.info(f"  Can write: {connection_status['can_write']}")
        
        if connection_status['connected']:
            objects = s3_service.list_bucket_contents()
            logger.info(f"  Objects in bucket: {len(objects)}")
            for obj in objects:
                logger.info(f"    - {obj}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error gathering system info: {e}")
        return False

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Upload car manual data to S3 with embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/upload_manual.py                    # Upload data (skip if exists)
  python cli/upload_manual.py --force            # Force regenerate embeddings
  python cli/upload_manual.py --test             # Test search after upload
  python cli/upload_manual.py --info             # Show system information
  python cli/upload_manual.py --check            # Check prerequisites only
        """
    )
    
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Force regenerate embeddings even if they exist in S3'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test search functionality after upload'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show system information and statistics'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check prerequisites only (no upload)'
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
    
    logger.info("=== S3 Car Manual Search - Data Upload Tool ===")
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("Prerequisites check failed. Exiting.")
        sys.exit(1)
    
    # Handle different modes
    success = True
    
    if args.info:
        success = show_system_info()
    elif args.check:
        logger.info("Prerequisites check completed successfully")
    else:
        # Upload data
        success = upload_manual_data(force_regenerate=args.force)
        
        # Test if requested
        if success and args.test:
            success = test_search_functionality()
    
    if success:
        logger.info("✓ Operation completed successfully")
        sys.exit(0)
    else:
        logger.error("✗ Operation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()