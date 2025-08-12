# Dual AI Recommendation Systems

This repository contains two distinct AI-powered recommendation systems, each designed for different use cases and deployment scenarios.

## 🎯 Overview

### 🚀 Two Powerful Systems

1. **[Lambda-Based System](lambda-recommendation-engine/)** - Serverless cloud recommendation engine
2. **[Bedrock-Streamlit System](bedrock-streamlit-recommendation/)** - Local AI-powered recommendation app

Both systems provide personalized product recommendations but use different architectures and deployment models.

## 📊 System Comparison

| Feature | Lambda System | Bedrock-Streamlit System |
|---------|---------------|--------------------------|
| **Deployment** | AWS Cloud (Serverless) | Local Machine |
| **Interface** | REST API | Streamlit Web App |
| **Embeddings** | Pre-computed (DynamoDB) | Real-time (Bedrock Titan) |
| **Explanations** | Similarity scores only | Natural language (Claude) |
| **Scalability** | Auto-scaling | Single user |
| **Cost** | Pay-per-request | Pay-per-API-call |
| **Setup Complexity** | High (AWS infrastructure) | Medium (local setup) |
| **Data Storage** | DynamoDB | Local JSON files |
| **Customer Limit** | 1000+ | 20 pre-computed + unlimited new |

## 🏗️ Architecture Overview

### Lambda-Based System
```
Client → API Gateway → Lambda → DynamoDB → Cosine Similarity → Response
```

### Bedrock-Streamlit System
```
Streamlit UI → Recommendation Engine → Bedrock APIs → Local Storage → Response
```

## 🚀 Quick Start

### Choose Your System

#### For Production/Enterprise Use
👉 **Use the [Lambda-Based System](lambda-recommendation-engine/)**
- Scalable serverless architecture
- Production-ready with monitoring
- REST API for integration
- Handles thousands of customers

#### For Development/Prototyping
👉 **Use the [Bedrock-Streamlit System](bedrock-streamlit-recommendation/)**
- Interactive web interface
- Real-time AI explanations
- Easy local development
- Perfect for demos and testing

## 📁 Repository Structure

```
s3-vector-lambda/
├── README.md                                    # This file
├── project-plan.md                             # Implementation roadmap
├── bedrock-streamlit-recommendation-design.md  # Bedrock system design
├── lambda-recommendation-engine/               # Serverless system
│   ├── README.md                              # Lambda system docs
│   ├── lambda_function.py                     # Main Lambda function
│   ├── template.yaml                          # SAM template
│   ├── infrastructure/                        # CloudFormation templates
│   ├── scripts/                               # Deployment scripts
│   └── tests/                                 # Test suite
└── bedrock-streamlit-recommendation/          # Local AI system
    ├── README.md                              # Bedrock system docs
    ├── streamlit_app.py                       # Main Streamlit app
    ├── bedrock_client.py                      # Bedrock integration
    ├── recommendation_engine.py               # Core logic
    ├── data/                                  # Local data storage
    ├── scripts/                               # Utility scripts
    └── tests/                                 # Test suite
```

## 🛠️ Setup Instructions

### Lambda-Based System Setup

```bash
# Navigate to Lambda system
cd lambda-recommendation-engine

# Deploy infrastructure
./scripts/deploy-tables.sh dev us-east-1
./scripts/deploy-lambda.sh dev us-east-1

# Generate sample data
python scripts/generate_synthetic_data.py --environment dev
```

### Bedrock-Streamlit System Setup

```bash
# Navigate to Bedrock system
cd bedrock-streamlit-recommendation

# Install dependencies
pip install -r requirements.txt

# Set up AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1

# Generate initial data
python scripts/generate_initial_data.py --embeddings

# Run the app
streamlit run streamlit_app.py
```

## 🎮 Usage Examples

### Lambda System - API Calls

```bash
# Get recommendations via REST API
curl -X POST https://your-api-url/recommend \
  -H 'Content-Type: application/json' \
  -d '{"customer_id": "CUST_001"}'
```

### Bedrock System - Web Interface

1. Open browser to `http://localhost:8501`
2. Select existing customer or create new profile
3. View AI-generated recommendations with explanations
4. Explore analytics dashboard

## 🧪 Testing

### Test Lambda System
```bash
cd lambda-recommendation-engine
python tests/test_recommendation_engine.py --api-url https://your-api-url
```

### Test Bedrock System
```bash
cd bedrock-streamlit-recommendation
python scripts/test_bedrock_connection.py
pytest tests/
```

## 📊 Features Comparison

### Lambda System Features
- ✅ Serverless auto-scaling
- ✅ REST API integration
- ✅ DynamoDB storage
- ✅ CloudWatch monitoring
- ✅ Production-ready
- ✅ Cost-effective at scale
- ❌ No real-time explanations
- ❌ Complex setup

### Bedrock System Features
- ✅ Interactive web interface
- ✅ Real-time AI explanations
- ✅ Natural language processing
- ✅ Easy local development
- ✅ Analytics dashboard
- ✅ New customer support
- ❌ Single user limitation
- ❌ Requires AWS Bedrock access

## 💰 Cost Analysis

### Lambda System (Monthly)
- **Small Scale** (1K requests): ~$10-15
- **Medium Scale** (10K requests): ~$25-40
- **Large Scale** (100K requests): ~$100-200

### Bedrock System (Monthly)
- **Light Usage** (10 new customers/day): ~$5-10
- **Moderate Usage** (50 new customers/day): ~$15-25
- **Heavy Usage** (200 new customers/day): ~$50-100

## 🔧 Configuration

### Environment Variables

Both systems support these common variables:
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

System-specific variables are documented in each system's README.

## 📈 Performance Benchmarks

### Lambda System
- **Cold Start**: ~2-3 seconds
- **Warm Response**: ~200-500ms
- **Throughput**: 1000+ requests/minute
- **Availability**: 99.9%

### Bedrock System
- **Existing Customer**: <1 second
- **New Customer**: 5-10 seconds
- **Concurrent Users**: 1 (local)
- **Availability**: Depends on local setup

## 🛡️ Security Considerations

### Lambda System
- IAM roles and policies
- API Gateway authentication
- VPC configuration (optional)
- CloudTrail logging

### Bedrock System
- Local data storage
- AWS credentials management
- Streamlit security headers
- Network access controls

## 🚀 Deployment Options

### Lambda System Deployment
- **Development**: SAM local
- **Staging**: AWS CloudFormation
- **Production**: CI/CD pipeline

### Bedrock System Deployment
- **Local**: Direct Python execution
- **Docker**: Containerized deployment
- **Cloud**: EC2, Heroku, or Cloud Run

## 📚 Documentation

- **[Lambda System Docs](lambda-recommendation-engine/README.md)** - Complete serverless system guide
- **[Bedrock System Docs](bedrock-streamlit-recommendation/README.md)** - Local AI system guide
- **[Design Documents](bedrock-streamlit-recommendation-design.md)** - Technical specifications
- **[Project Plan](project-plan.md)** - Implementation roadmap

## 🤝 Contributing

1. Choose the system you want to contribute to
2. Read the specific system's README
3. Follow the setup instructions
4. Make your changes
5. Add tests
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

### Getting Help

1. **Check the specific system's README** for detailed instructions
2. **Run the test suites** to identify issues
3. **Review the troubleshooting sections** in each system's docs
4. **Check AWS service status** for cloud-related issues

### Common Issues

- **AWS Credentials**: Ensure proper AWS setup for both systems
- **Bedrock Access**: Verify Bedrock is available in your region
- **Dependencies**: Check Python version and package installations
- **Permissions**: Ensure proper IAM permissions for AWS services

---

## 🎯 Which System Should You Choose?

### Choose Lambda System If:
- Building a production application
- Need to handle many concurrent users
- Want serverless auto-scaling
- Require REST API integration
- Have AWS infrastructure expertise

### Choose Bedrock System If:
- Prototyping or demonstrating AI capabilities
- Want interactive web interface
- Need natural language explanations
- Developing locally
- Want to experiment with Bedrock models

Both systems demonstrate different approaches to AI-powered recommendations and can serve as learning resources or production starting points.

*Built with ❤️ using AWS Lambda, Amazon Bedrock, Streamlit, and AI*
