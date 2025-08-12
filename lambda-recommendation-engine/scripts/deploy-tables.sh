#!/bin/bash

# Deploy DynamoDB tables for Vector Recommendation Engine POC
# Usage: ./deploy-tables.sh [environment] [region]

set -e

# Default values
ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
STACK_NAME="vector-recommendation-dynamodb-${ENVIRONMENT}"

echo "🚀 Deploying DynamoDB tables for Vector Recommendation Engine"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Stack Name: ${STACK_NAME}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured and authenticated"

# Deploy CloudFormation stack
echo "📦 Deploying CloudFormation stack..."

aws cloudformation deploy \
    --template-file infrastructure/dynamodb-tables.yaml \
    --stack-name "${STACK_NAME}" \
    --parameter-overrides Environment="${ENVIRONMENT}" \
    --region "${REGION}" \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset

if [ $? -eq 0 ]; then
    echo "✅ DynamoDB tables deployed successfully!"
    
    # Get stack outputs
    echo ""
    echo "📋 Stack Outputs:"
    aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "Table names:"
    echo "  - CustomerEmbeddings-${ENVIRONMENT}"
    echo "  - ProductEmbeddings-${ENVIRONMENT}"
    
else
    echo "❌ Deployment failed!"
    exit 1
fi