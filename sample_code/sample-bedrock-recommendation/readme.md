# Product Recommendation System

A Streamlit application that provides personalized product recommendations using AWS Bedrock (Amazon Titan) and stores user preferences as embeddings in your existing S3 bucket `my-product-embeddings-bucket-12345`.

## Features

- **Product Selection**: Browse and select from 10 different products
- **User Authentication**: Simple username-based login system with persistent login state
- **Personalized Recommendations**: AI-powered recommendations using Amazon Titan embeddings
- **Persistent Storage**: User preferences stored as embeddings in AWS S3
- **Real-time Updates**: Recommendations update based on user interaction history
- **Organized Storage**: Uses structured folders within your existing S3 bucket
- **Intuitive Layout**: Recommendations shown on the right side for returning users

## Architecture

- **Frontend**: Streamlit web application
- **AI Model**: Amazon Titan Text Lite v1 for generating embeddings
- **Storage**: AWS S3 for persistent user preference storage
- **Recommendation Engine**: Cosine similarity matching between user preferences and product embeddings

## Prerequisites

- Python 3.8 or higher
- AWS Account with appropriate permissions
- AWS CLI configured or AWS credentials set up
- Access to AWS Bedrock service
- Access to Amazon Titan Text Lite v1 model

## Installation

1. **Clone or download the application files**

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up AWS credentials** (choose one method):
   - AWS CLI: `aws configure`
   - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - IAM roles (if running on EC2)
   - AWS credentials file

4. **Configure Bedrock access**:
   - Handle Bedrock token as per AWS documentation
   - Ensure access to `amazon.titan-text-lite-v1` model in your region

5. **Verify S3 bucket access** by running the setup script:
   ```bash
   python setup_aws.py
   ```
   This will verify access to your existing bucket `my-product-embeddings-bucket-12345` and set up the required folder structure.

## AWS Permissions Required

Your AWS credentials need the following permissions:

### S3 Permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:HeadBucket",
                "s3:PutBucketVersioning"
            ],
            "Resource": [
                "arn:aws:s3:::my-product-embeddings-bucket-12345",
                "arn:aws:s3:::my-product-embeddings-bucket-12345/*"
            ]
        }
    ]
}
```

### Bedrock Permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/amazon.titan-text-lite-v1"
        }
    ]
}
```

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Login**: Enter a username in the sidebar and click "Login"

3. **First-time users**: Browse and click on products you're interested in

4. **Returning users**: View personalized recommendations based on your previous selections

5. **Logout**: Click "Logout" to save your preferences to S3

## How It Works

### First Visit:
1. User logs in with a username
2. User browses and selects products in a 3-column grid layout
3. Upon logout, selected products are combined into text
4. Text is converted to embeddings using Amazon Titan
5. Embeddings are stored in S3 with user ID

### Subsequent Visits:
1. User logs in (login button is hidden, showing user info instead)
2. System retrieves user's embedding from S3
3. **Left side**: Product browsing in 2-column grid
4. **Right side**: Personalized recommendations with match scores
5. System generates embeddings for all available products
6. Cosine similarity is calculated between user preferences and products
7. Top 5 recommendations are displayed with "Select" buttons

## File Structure

```
├── app.py              # Main Streamlit application
├── setup_aws.py        # AWS setup script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## S3 Folder Structure

The application organizes data within your existing bucket using the following structure:

```
my-product-embeddings-bucket-12345/
└── product-recommendation-system/
    ├── user-preferences/
    │   └── {user_id}/
    │       └── {user_id}_preferences.json
    ├── models/
    │   └── (cached model data)
    └── logs/
        └── (system logs)
```

## Configuration

The application uses the following settings:

- **S3 Bucket**: `my-product-embeddings-bucket-12345` (your existing bucket)
- **Bedrock Model**: `amazon.titan-text-lite-v1`
- **AWS Region**: Uses your default AWS region
- **User Data Path**: `product-recommendation-system/user-preferences/{user_id}/`

## Sample Products

The application includes 10 sample products:
- Wireless Bluetooth Headphones
- Smart Fitness Tracker
- Portable Phone Charger
- Ergonomic Laptop Stand
- Premium Coffee Beans
- Wireless Mouse
- USB-C Hub
- Blue Light Blocking Glasses
- Desk Organizer
- Portable Bluetooth Speaker

## Troubleshooting

### Common Issues:

1. **AWS Credentials Error**:
   - Ensure AWS credentials are properly configured
   - Check that credentials have required permissions

2. **Bedrock Access Error**:
   - Verify you have access to the Bedrock service
   - Ensure the `amazon.titan-text-lite-v1` model is available in your region
   - Handle Bedrock token as per AWS documentation

3. **S3 Access Error**:
   - Verify the bucket `my-product-embeddings-bucket-12345` exists
   - Check S3 permissions for the bucket
   - Ensure you have read/write access to the bucket

4. **Model Invocation Error**:
   - Verify model ID is correct
   - Check that you have `bedrock:InvokeModel` permission
   - Ensure you're in a supported region

## Security Notes

- User IDs are generated using MD5 hashing of usernames
- No sensitive data is stored in embeddings
- All AWS operations use your configured credentials
- S3 bucket versioning is enabled for data protection

## Extending the Application

You can extend this application by:

- Adding more products to the `PRODUCTS` list
- Implementing more sophisticated user authentication
- Adding product categories and filtering
- Implementing collaborative filtering
- Adding product images and descriptions
- Creating admin panels for product management

## Cost Considerations

- **Bedrock**: Charged per token for embedding generation
- **S3**: Minimal storage costs for JSON files
- **Data Transfer**: Standard AWS data transfer rates apply

Monitor your AWS billing dashboard for actual costs.

## Support

For AWS-specific issues, refer to:
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

## License

This project is for demonstration purposes. Please ensure compliance with AWS terms of service and applicable licenses for all dependencies.