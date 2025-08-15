#!/usr/bin/env python3
"""
Demo setup script for S3 Car Manual Search System.
This script helps users set up the demo environment and test the system.
"""

import sys
import os
import subprocess
from pathlib import Path
import logging

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from src.search_service import SearchService
from config import S3_BUCKET_NAME, AWS_REGION

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible."""
    logger.info("Checking Python version...")
    
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'sentence_transformers',
        'boto3',
        'numpy',
        'pandas',
        'scikit-learn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"✗ {package} is missing")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with: pip install -r requirements.txt")
        return False
    
    logger.info("✓ All dependencies are installed")
    return True

def check_aws_configuration():
    """Check AWS configuration."""
    logger.info("Checking AWS configuration...")
    
    try:
        search_service = SearchService()
        connection_status = search_service.s3_service.check_connection()
        
        if connection_status['connected']:
            logger.info("✓ AWS connection successful")
            logger.info(f"  Bucket: {S3_BUCKET_NAME}")
            logger.info(f"  Region: {AWS_REGION}")
            logger.info(f"  Bucket exists: {connection_status['bucket_exists']}")
            logger.info(f"  Can read: {connection_status['can_read']}")
            logger.info(f"  Can write: {connection_status['can_write']}")
            return True
        else:
            logger.error("✗ AWS connection failed")
            logger.error(f"  Error: {connection_status.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"✗ AWS configuration error: {e}")
        return False

def setup_sample_data():
    """Set up sample data and embeddings."""
    logger.info("Setting up sample data...")
    
    try:
        # Run the upload script
        script_path = Path(__file__).parent.parent / "cli" / "upload_manual.py"
        
        logger.info("Running data upload script...")
        result = subprocess.run([
            sys.executable, str(script_path), "--info"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Sample data setup completed")
            logger.info(result.stdout)
            return True
        else:
            logger.error("✗ Sample data setup failed")
            logger.error(result.stderr)
            return False
            
    except Exception as e:
        logger.error(f"Error setting up sample data: {e}")
        return False

def test_search_functionality():
    """Test basic search functionality."""
    logger.info("Testing search functionality...")
    
    try:
        search_service = SearchService()
        
        # Test a simple search
        test_query = "oil change"
        results = search_service.search(test_query, top_k=3)
        
        if results:
            logger.info(f"✓ Search test passed - found {len(results)} results for '{test_query}'")
            for i, result in enumerate(results[:2], 1):
                title = result['metadata']['title']
                score = result['similarity_score']
                logger.info(f"  {i}. {title} (Score: {score:.3f})")
            return True
        else:
            logger.warning("✗ Search test failed - no results found")
            return False
            
    except Exception as e:
        logger.error(f"Error testing search: {e}")
        return False

def run_streamlit_app():
    """Launch the Streamlit application."""
    logger.info("Launching Streamlit application...")
    
    try:
        app_path = Path(__file__).parent.parent / "streamlit_app.py"
        
        logger.info("Starting Streamlit server...")
        logger.info("The application will open in your browser at http://localhost:8501")
        logger.info("Press Ctrl+C to stop the server")
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path)
        ])
        
    except KeyboardInterrupt:
        logger.info("Streamlit server stopped")
    except Exception as e:
        logger.error(f"Error running Streamlit: {e}")

def print_usage_instructions():
    """Print usage instructions."""
    logger.info("=== Usage Instructions ===")
    logger.info("")
    logger.info("1. Manual Setup:")
    logger.info("   python cli/upload_manual.py          # Upload data to S3")
    logger.info("   streamlit run streamlit_app.py       # Run the app")
    logger.info("")
    logger.info("2. Search Examples:")
    logger.info("   - 'oil change procedure'")
    logger.info("   - 'brake noise when stopping'")
    logger.info("   - 'engine won't start'")
    logger.info("   - 'AC not cooling'")
    logger.info("")
    logger.info("3. Browse by Category:")
    logger.info("   - Engine, Brakes, Electrical")
    logger.info("   - Transmission, Suspension, AC/Heating")
    logger.info("")
    logger.info("4. CLI Tools:")
    logger.info("   python cli/upload_manual.py --help   # See all options")
    logger.info("   python cli/upload_manual.py --test   # Test search")
    logger.info("   python cli/upload_manual.py --info   # System info")

def main():
    """Main setup function."""
    logger.info("=== S3 Car Manual Search - Demo Setup ===")
    logger.info("")
    
    # Check prerequisites
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("AWS Configuration", check_aws_configuration),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        logger.info(f"--- {check_name} ---")
        if not check_func():
            all_passed = False
        logger.info("")
    
    if not all_passed:
        logger.error("Some checks failed. Please fix the issues before proceeding.")
        print_usage_instructions()
        return False
    
    logger.info("✓ All prerequisite checks passed!")
    logger.info("")
    
    # Ask user what to do
    print("What would you like to do?")
    print("1. Set up sample data and test search")
    print("2. Launch Streamlit application")
    print("3. Show usage instructions")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            logger.info("--- Setting up sample data ---")
            if setup_sample_data():
                logger.info("--- Testing search functionality ---")
                test_search_functionality()
        
        elif choice == "2":
            run_streamlit_app()
        
        elif choice == "3":
            print_usage_instructions()
        
        elif choice == "4":
            logger.info("Goodbye!")
        
        else:
            logger.warning("Invalid choice. Showing usage instructions.")
            print_usage_instructions()
    
    except KeyboardInterrupt:
        logger.info("\nSetup interrupted by user")
    except Exception as e:
        logger.error(f"Setup error: {e}")
    
    return True

if __name__ == "__main__":
    main()