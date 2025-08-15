# Lambda-Based Vector Recommendation Engine

This is the original serverless recommendation engine that uses AWS Lambda, DynamoDB, and API Gateway to provide product recommendations based on vector similarity.

## 🎯 Overview

This system implements a vector-based recommendation engine that:
- Takes a `customer_id` as input
- Returns top 5 product recommendations using cosine similarity
- Uses AWS Lambda for serverless compute
- Stores embeddings in DynamoDB
- Provides a REST API via API Gateway

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│ API Gateway │───▶│   Lambda    │
└─────────────┘    └─────────────┘    └─────────────┘
                                               │
                                               ▼
                    ┌─────────────┐    ┌─────────────┐
                    │  DynamoDB   │◀───│   Cosine    │
                    │ Embeddings  │    │ Similarity  │
                    └─────────────┘    └─────────────┘
```

## 📁 Project Structure

```
lambda-recommendation-engine/
├── README.md                           # This file
├── vector-recommendation-engine-design.md  # Design document
├── lambda_function.py                  # Main Lambda function
├── requirements.txt                    # Python dependencies
├── template.yaml                       # SAM template
├── infrastructure/
│   └── dynamodb-tables.yaml          # DynamoDB CloudFormation template
├── scripts/
│   ├── deploy-tables.sh               # Deploy DynamoDB tables
│   ├── deploy-lambda.sh               # Deploy Lambda and API Gateway
│   └── generate_synthetic_data.py     # Generate sample data
└── tests/
    └── test_recommendation_engine.py  # Comprehensive test suite
```

## 🚀 Quick Start

### 1. Deploy Infrastructure
```bash
# Deploy DynamoDB tables
./scripts/deploy-tables.sh dev us-east-1

# Deploy Lambda function and API Gateway
./scripts/deploy-lambda.sh dev us-east-1
```

### 2. Generate Sample Data
```bash
# Install Python dependencies
pip install boto3 numpy

# Generate synthetic data
python scripts/generate_synthetic_data.py --environment dev --region us-east-1
```

### 3. Test the API
```bash
# Get the API endpoint from CloudFormation outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name vector-recommendation-lambda-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`RecommendationApiUrl`].OutputValue' \
  --output text)

# Test the recommendation endpoint
curl -X POST $API_URL \
  -H 'Content-Type: application/json' \
  -d '{"customer_id": "CUST_001"}'
```

## 📡 API Reference

### POST /recommend

Get product recommendations for a customer.

#### Request
```json
{
  "customer_id": "CUST_001"
}
```

#### Response (200 OK)
```json
{
  "customer_id": "CUST_001",
  "recommendations": [
    {
      "product_id": "PROD_123",
      "product_name": "Wireless Bluetooth Headphones",
      "similarity_score": 0.95
    }
  ],
  "processing_time_ms": 1250
}
```

## 🧪 Testing

```bash
# Run comprehensive tests
python tests/test_recommendation_engine.py \
  --api-url https://your-api-url/recommend \
  --environment dev \
  --region us-east-1
```

## 💰 Cost Estimation

### Monthly Costs (Development Environment)
- **Lambda**: ~$5-10 (10,000 requests/month)
- **DynamoDB**: ~$2-5 (on-demand pricing)
- **API Gateway**: ~$3-7 (request-based pricing)
- **Total**: ~$10-22/month

## 📊 Performance

### Target Metrics
- **Response Time**: < 2 seconds
- **Throughput**: 100+ requests/minute
- **Scale**: 1,000 customers, 2,000 products

For detailed design documentation, see [`vector-recommendation-engine-design.md`](vector-recommendation-engine-design.md).