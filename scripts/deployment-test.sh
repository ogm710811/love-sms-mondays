#!/bin/bash
# Simple test script to verify Lambda deployment

# Get the function name from CloudFormation outputs
FUNCTION_NAME=$(aws cloudformation describe-stacks \
  --stack-name love-sms-mondays \
  --query "Stacks[0].Outputs[?OutputKey=='LambdaName'].OutputValue" \
  --output text)

if [ -z "$FUNCTION_NAME" ]; then
  echo "Error: Could not retrieve Lambda function name from CloudFormation"
  exit 1
fi

# Test Lambda with dry-run mode (no SMS sent)
echo "Testing Lambda function ${FUNCTION_NAME}..."
aws lambda invoke \
  --function-name "$FUNCTION_NAME" \
  --cli-binary-format raw-in-base64-out \
  --payload '{"test": true, "dry_run": true}' \
  response.json

# Check for errors in response
if grep -q "errorMessage" response.json; then
  echo "Lambda invocation test failed:"
  cat response.json
  exit 1
else
  echo "Lambda invocation test succeeded"
  cat response.json
fi