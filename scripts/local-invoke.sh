#!/bin/bash

# Set environment variables for local testing
export PHONE_NUMBER="+1XXXXXXXXXX"  # Use a test number
export PHRASES_TABLE="love-phrases"
export API_URL="https://api.quotable.io/random"
export DRY_RUN=true  # Prevent actual SMS sending

# Invoke the Lambda function locally
pipenv run python -c "import sys; sys.path.append('src'); import app; app.handler({'test': True, 'dry_run': True}, {})"
