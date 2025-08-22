#!/bin/bash
# Simple test script to verify Lambda deployment

# Get the function name from CloudFormation
FUNCTION_NAME=$(aws cloudformation describe-stack-resource \
  --stack-name love-sms-mondays \
  --logical-resource-id LambdaFunction \
  --query 'StackResourceDetail.PhysicalResourceId' \
  --output text)

# Test Lambda with dry-run mode (no SMS sent)
echo "Testing Lambda function ${FUNCTION_NAME}..."
aws lambda invoke \
  --function-name "$FUNCTION_NAME" \
  --payload '{"test": true, "dry_run": true}' \
  response.json

# Display results
cat response.json