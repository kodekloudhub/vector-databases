# S3 Car Manual Search System

A simple Streamlit application that demonstrates AWS S3 Vector storage capabilities for searching car manual information. Mechanics can quickly search and get the top 5 most relevant repair procedures.

## 🎯 Overview

This system allows mechanics to:
- Search car manual information using natural language queries
- Get top 5 most relevant repair procedures
- Access detailed step-by-step instructions
- Browse by category (Engine, Brakes, Electrical, etc.)

## 🏗️ Architecture

- **Local Embeddings**: Uses sentence-transformers for cost-effective processing
- **S3 Vector Storage**: Stores embeddings and manual data in AWS S3
- **Streamlit Interface**: Simple web interface for search and results
- **CLI Tools**: Command-line utilities for data management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- AWS Account with S3 access
- AWS CLI configured

### Installation

```bash
# Navigate to the project directory
cd s3-car-manual-search

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure
# OR set environment variables:
# export AWS_ACCESS_KEY_ID=your_key
# export AWS_SECRET_ACCESS_KEY=your_secret
# export AWS_REGION=us-east-1
```

### Setup

```bash
# 1. Copy environment variables template
cp .env.example .env

# 2. Edit .env file with your AWS credentials
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_REGION=us-east-1
# S3_BUCKET_NAME=car-manual-vectors

# 3. Upload car manual data to S3
python cli/upload_manual.py

# 4. Run the Streamlit app
streamlit run streamlit_app.py
```

### Quick Demo Setup

```bash
# Run the interactive setup script
python scripts/setup_demo.py
```

### Usage

1. Open your browser to `http://localhost:8501`
2. Choose from three search modes:
   - **🔍 Text Search**: Enter queries like "oil change", "brake noise"
   - **📂 Browse by Category**: Explore by system (Engine, Brakes, etc.)
   - **📋 View All Sections**: See complete manual overview
3. View the top 5 most relevant results with similarity scores
4. Expand results to see detailed procedures and keywords

## 📁 Project Structure

```
s3-car-manual-search/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.py                         # Configuration settings
├── streamlit_app.py                  # Main search interface
├── src/
│   ├── manual_processor.py          # Process car manual sections
│   ├── embedding_service.py         # Local embedding generation
│   ├── s3_vector_service.py         # S3 operations
│   └── search_service.py            # Search and ranking
├── data/
│   └── car_manual_sections.json     # Dummy car manual data
├── cli/
│   └── upload_manual.py             # CLI to upload data to S3
└── scripts/
    ├── setup_demo.py                # Setup demo environment
    └── cleanup_aws.py               # AWS resource cleanup script
```

## 🔧 Configuration

Edit `config.py` to customize:
- S3 bucket name
- AWS region
- Embedding model
- Number of search results

## 🛠️ Sample Queries

### Engine System
- "How to change engine oil?"
- "Spark plug replacement procedure"
- "Engine overheating diagnosis"
- "Air filter replacement"
- "Timing belt replacement"

### Brake System
- "Brake pad replacement"
- "Brake noise when stopping"
- "Brake fluid bleeding procedure"
- "Brake rotor resurfacing"

### Electrical System
- "Battery testing and replacement"
- "Alternator not charging"
- "Starter motor problems"
- "Headlight bulb replacement"
- "Fuse replacement"

### Other Systems
- "Transmission fluid change"
- "AC not cooling properly"
- "Power steering fluid check"
- "Tire rotation procedure"

## 📊 Features

### Search Capabilities
- **Vector Search**: Semantic similarity using sentence-transformers
- **Keyword Fallback**: Traditional keyword search when needed
- **Category Browse**: Filter by automotive system
- **Relevance Scoring**: Similarity scores for each result

### User Interface
- **Interactive Web App**: Clean Streamlit interface
- **Multiple Search Modes**: Text search, category browse, overview
- **Expandable Results**: Detailed procedures with keywords
- **System Status**: Real-time connection and data status

### Technical Features
- **Local Embeddings**: Cost-effective sentence-transformers
- **S3 Vector Storage**: Scalable cloud storage for embeddings
- **Fallback Mechanisms**: Graceful degradation when S3 unavailable
- **CLI Tools**: Command-line utilities for data management

## 🆘 Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   ```bash
   # Check AWS configuration
   aws configure list
   
   # Or set environment variables
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_REGION=us-east-1
   ```

2. **S3 Permissions Error**
   - Ensure your AWS user has S3 read/write permissions
   - Check if the bucket name is unique globally
   - Verify the region is correct

3. **Dependencies Missing**
   ```bash
   pip install -r requirements.txt
   ```

4. **Model Download Issues**
   - First run downloads ~90MB embedding model
   - Ensure stable internet connection
   - Model is cached locally after first download

5. **Streamlit Issues**
   ```bash
   # Clear Streamlit cache
   streamlit cache clear
   
   # Run with specific port
   streamlit run streamlit_app.py --server.port 8502
   ```

### Debug Commands

```bash
# Check system status
python cli/upload_manual.py --info

# Test search functionality
python cli/upload_manual.py --test

# Check prerequisites
python cli/upload_manual.py --check

# Run interactive setup
python scripts/setup_demo.py

# Clean up AWS resources when done
python scripts/cleanup_aws.py
```

## 🧹 Cleanup

When you're finished with the demo, you can clean up all AWS resources:

```bash
# Interactive cleanup (recommended)
python scripts/cleanup_aws.py

# List what will be deleted
python scripts/cleanup_aws.py --list

# Delete objects but keep bucket
python scripts/cleanup_aws.py --objects-only

# Force cleanup without prompts
python scripts/cleanup_aws.py --force

# Dry run (show what would be deleted)
python scripts/cleanup_aws.py --dry-run
```

**What gets cleaned up:**
- S3 bucket and all objects (embeddings, manual data, metadata)
- Local cache files
- All demo data

**Note:** Cleanup is permanent and cannot be undone!

---

*Built with ❤️ using AWS S3, sentence-transformers, and Streamlit*