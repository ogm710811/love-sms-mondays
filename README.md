# Love SMS Mondays

A serverless application that sends a love message or inspirational quote via SMS every Monday morning to brighten someone's day.

## Overview

Love SMS Mondays is an AWS Lambda-based application that:

1. Fetches an inspirational quote from a public API
2. Saves the quote to a DynamoDB table
3. Sends the quote as an SMS message to a configured phone number
4. Runs automatically every Monday at 7 AM (configurable timezone)

If the API fetch fails, the application falls back to previously stored quotes or default love messages.

## Architecture

The application uses several AWS services:

- **AWS Lambda**: Runs the Python code that fetches quotes and sends messages
- **Amazon DynamoDB**: Stores fetched quotes for future use
- **Amazon SNS**: Sends SMS messages to the configured phone number
- **AWS EventBridge Scheduler**: Triggers the Lambda function on a schedule
- **AWS Systems Manager Parameter Store**: (Optional) Stores API keys securely

## Prerequisites

- AWS Account
- Python 3.12
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate permissions
- [Pipenv](https://pipenv.pypa.io/en/latest/) (for dependency management)
- [Git](https://git-scm.com/) (for version control)

For CI/CD with GitHub Actions:
- GitHub repository with Actions enabled
- AWS IAM role with appropriate permissions for OIDC authentication

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd love-sms-mondays
   ```

2. Install dependencies:
   ```
   pipenv install --dev
   ```

3. Deploy to AWS:

   ### Option 1: Using GitHub Actions (Recommended)

   Push your changes to the main branch, and the GitHub Actions workflow will automatically:
   - Run linting and tests
   - Validate the CloudFormation template
   - Build and deploy the application to AWS

   See `.github/workflows/deploy.yml` for the complete workflow configuration.

   ### Option 2: Manual Deployment

   ```
   # Generate requirements.txt from Pipfile
   pipenv requirements > requirements.txt

   # Create a deployment package (zip file)
   mkdir -p dist
   cp src/app.py requirements.txt dist/
   cd dist && zip -r ../love-sms.zip .

   # Upload the Lambda code to an S3 bucket
   aws s3 cp love-sms.zip s3://<your-bucket>/<path>/love-sms.zip

   # Deploy the CloudFormation stack
   aws cloudformation deploy \
     --template-file template.yaml \
     --stack-name love-sms-mondays \
     --parameter-overrides \
       PhoneNumber=+1XXXXXXXXXX \
       ArtifactBucket=<your-bucket> \
       ArtifactKey=<path>/love-sms.zip \
       TimeZone=America/New_York \
     --capabilities CAPABILITY_IAM
   ```

## Configuration Parameters

The CloudFormation template accepts the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| PhoneNumber | E.164 phone number (e.g., +19045551234) | (Required) |
| TimeZone | Timezone for the scheduler | America/New_York |
| CronAt7amMonday | Cron expression for the scheduler | cron(0 7 ? * MON *) |
| ArtifactBucket | S3 bucket where GitHub Actions uploads the Lambda zip | (Required) |
| ArtifactKey | S3 key for the Lambda zip | (Required) |
| ApiUrl | Public API endpoint for quotes | https://api.quotable.io/random |
| ApiKeyParameterName | (Optional) SSM Parameter name for API key | "" |
| EnvSuffix | Suffix for PR-specific deployments | "" |

## Supported Quote APIs

The application is designed to work with various quote APIs, with built-in support for:

- [Quotable](https://api.quotable.io/random)
- [ZenQuotes](https://zenquotes.io/api/random)

You can configure other APIs by setting the `ApiUrl` parameter and adjusting the response parsing in the code if needed.

## Project Structure

The project is organized as follows:

- `src/` - Contains the application source code
  - `app.py` - Main Lambda function code
- `tests/` - Contains test files
- `scripts/` - Contains utility scripts
  - `local-invoke.sh` - Script for testing the Lambda function locally
  - `deployment-test.sh` - Script for testing a deployed Lambda function
- `.github/workflows/` - Contains GitHub Actions workflow definitions
  - `deploy.yml` - CI/CD workflow for testing and deploying the application

## Development

### Local Testing

Run tests with pytest:
```
pipenv run pytest
```

You can also use the provided script to test the Lambda function locally:
```
# On Linux/Mac
chmod +x scripts/local-invoke.sh
./scripts/local-invoke.sh

# On Windows (using Git Bash or similar)
bash scripts/local-invoke.sh

# Note: The script adds the src/ directory to the Python path to import app.py
```

### Deployment Testing

After deploying the application, you can test it using:
```
# On Linux/Mac
chmod +x scripts/deployment-test.sh
./scripts/deployment-test.sh

# On Windows (using Git Bash or similar)
bash scripts/deployment-test.sh
```

### Code Quality

The project uses flake8 for linting. You can run it with:
```
pipenv run flake8
```

### Adding Custom Fallback Messages

You can modify the `FALLBACKS` list in `src/app.py` to add your own custom fallback messages that will be used if both the API and DynamoDB fallbacks fail.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
