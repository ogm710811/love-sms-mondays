# Love SMS Mondays

A serverless application that sends love messages or inspirational quotes via SMS every Monday morning.

## Overview

Love SMS Mondays is a simple yet thoughtful AWS serverless application that:

1. Fetches a random quote or phrase from a public API
2. Stores it in a DynamoDB table for future reference
3. Sends it as an SMS message to a configured phone number
4. Runs automatically every Monday at 7:00 AM (configurable)

If the API call fails, the application will fall back to either:
1. A previously stored quote from DynamoDB
2. A hardcoded fallback message

## Features

- **Reliability**: Multiple fallback mechanisms ensure a message is always sent
- **Flexibility**: Works with various quote APIs (see Supported APIs below)
- **Persistence**: Stores quotes in DynamoDB for future reference and fallback
- **Scheduling**: Configurable timing using EventBridge Scheduler
- **Security**: Optional API key support via AWS Parameter Store
- **CI/CD**: Includes Jenkins pipeline for automated deployment
- **Testing**: Comprehensive test suite using pytest and moto

## Supported Quote APIs

The application works with various quote APIs out of the box, including:

1. **Quotable API** (default): https://api.quotable.io/random
2. **ZenQuotes API**: https://zenquotes.io/api/random

The application can be easily adapted to work with other APIs by adjusting the response parsing in the `fetch_phrase` function.

## Architecture

The application uses several AWS services:
- **AWS Lambda**: Runs the core application logic
- **Amazon DynamoDB**: Stores fetched phrases for future use
- **Amazon SNS**: Sends SMS messages
- **AWS Systems Manager Parameter Store**: Optionally stores API keys
- **Amazon EventBridge Scheduler**: Triggers the Lambda function on schedule

## Prerequisites

- AWS Account
- Python 3.12
- AWS CLI configured with appropriate permissions
- Pipenv for dependency management
- A phone number that can receive SMS messages

## Setup and Deployment

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/love-sms-mondays.git
   cd love-sms-mondays
   ```

2. Install dependencies:
   ```
   pipenv install --dev
   ```

3. Run tests:
   ```
   pipenv run pytest
   ```

### AWS Deployment

The project uses AWS CloudFormation/SAM for deployment. You'll need:

1. An S3 bucket to store the Lambda deployment package
2. The following parameters:
   - PhoneNumber: E.164 format phone number (e.g., +19045551234)
   - TimeZone: Your local timezone (default: America/New_York)
   - ArtifactBucket: S3 bucket name for Lambda code
   - ArtifactKey: S3 key for Lambda code
   - ApiUrl: URL for the quotes API (default: https://api.quotable.io/random)
   - ApiKeyParameterName: (Optional) SSM Parameter name for API key

Deploy using CloudFormation:
```
# First, package the Lambda function
# Generate requirements.txt from Pipfile
pipenv requirements > requirements.txt
# Install dependencies to a package directory
pip install -r requirements.txt -t ./package
cd package && zip -r ../love-sms.zip . && cd ..
zip -g love-sms.zip app.py

# Upload to S3
aws s3 cp love-sms.zip s3://your-artifact-bucket/builds/love-sms.zip

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name love-sms-mondays \
  --parameter-overrides \
    PhoneNumber=+19045551234 \
    ArtifactBucket=your-artifact-bucket \
    ArtifactKey=builds/love-sms.zip \
  --capabilities CAPABILITY_IAM
```

## Configuration

The application can be configured through CloudFormation parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| PhoneNumber | E.164 phone number to receive SMS | Required |
| TimeZone | Timezone for the scheduler | America/New_York |
| CronAt7amMonday | Cron expression for scheduling | cron(0 7 ? * MON *) |
| ApiUrl | URL for the quotes API | https://api.quotable.io/random |
| ApiKeyParameterName | SSM Parameter name for API key | "" (empty) |

## Testing

The project uses pytest for testing. Tests mock AWS services using moto.

Run tests with:
```
pipenv run pytest
```

## CI/CD

The project includes a Jenkinsfile for CI/CD pipeline configuration. The pipeline:
1. Builds the Lambda package
2. Uploads the artifact to S3
3. Deploys to AWS using CloudFormation
4. Performs a smoke test by invoking the Lambda function once

The Jenkinsfile expects the following environment variables/credentials:
- `WIFE_PHONE_E164`: Jenkins credential for the recipient's phone number
- `ARTIFACT_BUCKET`: S3 bucket for storing Lambda deployment packages
- AWS credentials configured in the Jenkins environment

Note: While the project uses Pipenv for local development, the CI/CD pipeline expects a requirements.txt file. You can generate this file from Pipfile using `pipenv requirements > requirements.txt`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and follow the existing code style.

## Troubleshooting

### SMS Messages Not Being Sent

1. **Check AWS SNS Permissions**: Ensure the Lambda function has proper permissions to send SMS via SNS.
2. **Verify Phone Number Format**: The phone number must be in E.164 format (e.g., +19045551234).
3. **Check CloudWatch Logs**: Review the Lambda function logs for error messages.
4. **SMS Spending Limit**: AWS has a default spending limit for SMS. Check your AWS SNS console to ensure you haven't reached the limit.

### API Integration Issues

1. **API Endpoint Availability**: Verify the API endpoint is accessible by testing it directly.
2. **API Key Configuration**: If using an API key, ensure it's correctly stored in SSM Parameter Store.
3. **Response Format Changes**: If the API provider changes their response format, you may need to update the `fetch_phrase` function.

### Deployment Issues

1. **S3 Bucket Access**: Ensure your deployment has proper access to the S3 bucket specified in `ArtifactBucket`.
2. **CloudFormation Permissions**: Verify that your AWS user/role has sufficient permissions to create all resources in the template.
3. **Lambda Package Size**: If your dependencies grow too large, you might hit Lambda package size limits. Consider using Lambda Layers for large dependencies.
