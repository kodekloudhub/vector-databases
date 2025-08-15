# Bedrock-Streamlit Recommendation System

A local AI-powered recommendation system using Amazon Bedrock for embeddings and Streamlit for the web interface.

## 🎯 Overview

This system provides personalized product recommendations by:
- Using **Amazon Titan Embeddings G1 - Text** for generating customer and product embeddings
- Leveraging **Claude 3 Haiku** for natural language explanations
- Storing data locally in JSON files (no cloud infrastructure required)
- Providing an interactive **Streamlit** web interface
- Supporting both existing customers (20 pre-computed) and new customers (real-time)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit UI   │───▶│ Recommendation  │───▶│  Bedrock APIs   │
│                 │    │    Engine       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │  Data Manager   │              │
         │              │                 │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local JSON    │    │   Cosine        │    │   Titan         │
│   Storage       │    │   Similarity    │    │   Embeddings    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
bedrock-streamlit-recommendation/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── config.py                          # Configuration settings
├── streamlit_app.py                   # Main Streamlit application
├── recommendation_engine.py           # Core recommendation logic
├── bedrock_client.py                  # Bedrock API integration
├── data_manager.py                    # Local data management
├── data/
│   ├── customers.json                 # 20 customer embeddings
│   ├── products.json                  # Product catalog with embeddings
│   └── defaults.json                  # Default recommendations
├── assets/
│   ├── product_images/                # Product images
│   └── logos/                         # Brand logos
├── utils/
│   ├── embedding_generator.py         # Embedding utilities
│   ├── similarity_calculator.py       # Similarity calculations
│   └── explanation_generator.py       # Recommendation explanations
├── scripts/
│   ├── generate_initial_data.py       # Generate 20 customers + products
│   ├── update_embeddings.py           # Refresh embeddings
│   └── test_bedrock_connection.py     # Test Bedrock connectivity
└── tests/
    ├── test_recommendations.py        # Unit tests
    ├── test_bedrock_integration.py    # Bedrock API tests
    └── test_streamlit_app.py          # UI tests
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS CLI configured or environment variables set

### 2. Installation

```bash
# Clone the repository and navigate to the Bedrock system
cd bedrock-streamlit-recommendation

# Install dependencies
pip install -r requirements.txt
```

### 3. AWS Configuration

Set up your AWS credentials and region:

```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# Option 2: AWS CLI
aws configure
```

### 4. Generate Initial Data

```bash
# Generate 20 customer profiles and product catalog
python scripts/generate_initial_data.py

# Generate with Bedrock embeddings (requires AWS access)
python scripts/generate_initial_data.py --embeddings
```

### 5. Run the Application

```bash
# Start the Streamlit app
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

## 🛠️ Configuration

### Environment Variables

```bash
# Required
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# Optional
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
TEXT_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
MAX_RECOMMENDATIONS=5
SIMILARITY_THRESHOLD=0.3
```

### AWS Permissions

Your AWS user/role needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1",
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            ]
        }
    ]
}
```

## 🎮 Using the Application

### For Existing Customers

1. Select **"Existing Customer"** in the sidebar
2. Choose from 20 pre-computed customer profiles
3. View instant recommendations based on stored embeddings
4. Get detailed explanations for each recommendation

### For New Customers

1. Select **"New Customer"** in the sidebar
2. Fill out the customer profile form:
   - Personal details (name, age, gender, location)
   - Preferences (product categories)
   - Price sensitivity
   - Lifestyle information
3. Get real-time recommendations powered by Bedrock
4. Optionally save the profile for future use

### Features

- **Smart Recommendations**: AI-powered product matching
- **Detailed Explanations**: Understand why products were recommended
- **Fallback System**: Popular recommendations when similarity is low
- **Analytics Dashboard**: Customer and product insights
- **Product Details**: Comprehensive product information
- **System Status**: Monitor Bedrock connection and data integrity

## 📊 Data Model

### Customer Profile

```json
{
  "customer_id": "CUST_001",
  "embedding_vector": [0.1, 0.2, ...],
  "customer_metadata": {
    "name": "Ahmed Al Mansouri",
    "age": 32,
    "gender": "M",
    "location": "Dubai",
    "preferences": ["Electronics", "Home & Garden"],
    "price_sensitivity": 0.3,
    "lifestyle": "Tech Executive",
    "occupation": "Software Engineer"
  }
}
```

### Product Data

```json
{
  "product_id": "PROD_001",
  "product_name": "iPhone 15 Pro Max",
  "embedding_vector": [0.3, 0.7, ...],
  "category": "Electronics",
  "subcategory": "Mobile",
  "price": 1199.99,
  "brand": "Apple",
  "description": "Latest iPhone with titanium design",
  "features": ["A17 Pro chip", "48MP camera"],
  "rating": 4.8,
  "in_stock": true
}
```

## 🧪 Testing

### Test Bedrock Connection

```bash
python scripts/test_bedrock_connection.py
```

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=.
```

### Manual Testing

1. **Test Existing Customer Flow**:
   - Select an existing customer
   - Verify recommendations appear
   - Check explanation quality

2. **Test New Customer Flow**:
   - Create a new customer profile
   - Verify real-time embedding generation
   - Test fallback scenarios

3. **Test Error Handling**:
   - Disconnect from internet
   - Verify fallback recommendations work
   - Check error messages are user-friendly

## 📈 Performance

### Expected Response Times

- **Existing Customers**: < 1 second (local data)
- **New Customers**: < 10 seconds (including Bedrock calls)
- **Fallback Recommendations**: < 500ms

### Optimization Tips

1. **Enable Caching**: Set `CACHE_EMBEDDINGS=true` in config
2. **Batch Processing**: Generate embeddings in batches for better throughput
3. **Local Storage**: Keep frequently accessed data in memory
4. **Error Handling**: Implement graceful degradation

## 💰 Cost Estimation

### AWS Bedrock Costs (Monthly)

- **Titan Embeddings**: ~$0.0001 per 1K tokens
- **Claude 3 Haiku**: ~$0.00025 per 1K input tokens
- **Estimated Cost**: $5-15 for moderate usage (50 new customers/day)

### Cost Optimization

1. **Cache Embeddings**: Avoid regenerating for existing customers
2. **Batch Requests**: Process multiple items together
3. **Smart Fallbacks**: Use defaults when appropriate
4. **Monitor Usage**: Track API calls and costs

## 🔧 Troubleshooting

### Common Issues

1. **Bedrock Connection Failed**
   - Check AWS credentials
   - Verify region supports Bedrock
   - Ensure proper IAM permissions

2. **No Recommendations Generated**
   - Check if data files exist
   - Verify embeddings are generated
   - Test with fallback recommendations

3. **Slow Performance**
   - Enable caching in config
   - Check internet connection
   - Monitor Bedrock API limits

4. **Streamlit Errors**
   - Check Python version (3.8+)
   - Verify all dependencies installed
   - Clear Streamlit cache

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Deployment

### Local Development

```bash
streamlit run streamlit_app.py --server.port 8501
```

### Production Deployment

1. **Docker Container**:
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "streamlit_app.py"]
```

2. **Cloud Deployment**:
   - AWS EC2 with Streamlit
   - Heroku with buildpack
   - Google Cloud Run

## 📚 API Reference

### RecommendationEngine

```python
from recommendation_engine import RecommendationEngine

engine = RecommendationEngine()

# Get recommendations for existing customer
recommendations = engine.get_recommendations_for_existing_customer("CUST_001")

# Get recommendations for new customer
profile = {"age": 30, "preferences": ["Electronics"]}
recommendations = engine.get_recommendations_for_new_customer(profile)
```

### BedrockClient

```python
from bedrock_client import BedrockClient

client = BedrockClient()

# Generate embedding
embedding = client.generate_embedding("Product description")

# Generate explanation
explanation = client.generate_explanation(customer_profile, recommendations)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Test Bedrock connectivity
4. Verify data integrity

---

*Built with ❤️ using Amazon Bedrock, Streamlit, and AI*