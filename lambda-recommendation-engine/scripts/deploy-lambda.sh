#!/bin/bash

# Deploy Lambda function and API Gateway for Vector Recommendation Engine POC
# Usage: ./deploy-lambda.sh [environment] [region]

set -e

# Default values
ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
STACK_NAME="vector-recommendation-lambda-${ENVIRONMENT}"
S3_BUCKET="vector-recommendation-deployments-${ENVIRONMENT}-${REGION}"

echo "🚀 Deploying Vector Recommendation Engine Lambda Function"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Stack Name: ${STACK_NAME}"
echo "S3 Bucket: ${S3_BUCKET}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI is not installed. Please install it first."
    echo "Installation guide: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

# Check if user is authenticated
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI and SAM CLI configured and authenticated"

# Create S3 bucket for deployments if it doesn't exist
echo "📦 Checking/Creating S3 bucket for deployments..."
if ! aws s3 ls "s3://${S3_BUCKET}" 2>/dev/null; then
    echo "Creating S3 bucket: ${S3_BUCKET}"
    if [ "${REGION}" = "us-east-1" ]; then
        aws s3 mb "s3://${S3_BUCKET}" --region "${REGION}"
    else
        aws s3 mb "s3://${S3_BUCKET}" --region "${REGION}" --create-bucket-configuration LocationConstraint="${REGION}"
    fi
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "${S3_BUCKET}" \
        --versioning-configuration Status=Enabled
    
    echo "✅ S3 bucket created successfully"
else
    echo "✅ S3 bucket already exists"
fi

# Build the SAM application
echo "🔨 Building SAM application..."
sam build --use-container

if [ $? -ne 0 ]; then
    echo "❌ SAM build failed!"
    exit 1
fi

echo "✅ SAM build completed successfully"

# Deploy the SAM application
echo "🚀 Deploying SAM application..."
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name "${STACK_NAME}" \
    --s3-bucket "${S3_BUCKET}" \
    --parameter-overrides Environment="${ENVIRONMENT}" \
    --capabilities CAPABILITY_IAM \
    --region "${REGION}" \
    --no-fail-on-empty-changeset \
    --no-confirm-changeset

if [ $? -eq 0 ]; then
    echo "✅ Lambda function and API Gateway deployed successfully!"
    
    # Get stack outputs
    echo ""
    echo "📋 Stack Outputs:"
    aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
    
    # Get API endpoint
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[?OutputKey==`RecommendationApiUrl`].OutputValue' \
        --output text)
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "API Endpoint: ${API_URL}"
    echo ""
    echo "Test the API with:"
    echo "curl -X POST ${API_URL} \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"customer_id\": \"CUST_001\"}'"
    
else
    echo "❌ Deployment failed!"
    exit 1
fi