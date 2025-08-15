import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'car-manual-vectors')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# S3 Paths
S3_EMBEDDINGS_PATH = 'embeddings/'
S3_DATA_PATH = 'data/'
S3_METADATA_FILE = 'embeddings/metadata.json'
S3_EMBEDDINGS_FILE = 'embeddings/sections_embeddings.npy'
S3_MANUAL_DATA_FILE = 'data/manual_sections.json'

# Embedding Configuration
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
EMBEDDING_DIMENSION = 384

# Search Configuration
MAX_SEARCH_RESULTS = 5
SIMILARITY_THRESHOLD = 0.3

# Local Data Paths
LOCAL_DATA_DIR = 'data'
LOCAL_MANUAL_FILE = 'data/car_manual_sections.json'

# Streamlit Configuration
APP_TITLE = "🔧 Car Manual Search System"
APP_DESCRIPTION = "Search car repair procedures and get top 5 relevant results"

# Categories for car manual sections
MANUAL_CATEGORIES = [
    'Engine',
    'Brakes', 
    'Electrical',
    'Transmission',
    'Suspension',
    'AC/Heating',
    'Fuel System',
    'Exhaust',
    'Cooling System',
    'Steering'
]

# Common mechanic search terms for testing
SAMPLE_QUERIES = [
    "How to change oil?",
    "Brake noise when stopping",
    "Engine won't start",
    "AC not cooling",
    "Transmission slipping",
    "Battery dead",
    "Spark plug replacement",
    "Brake pad replacement",
    "Alternator problems",
    "Coolant leak"
]