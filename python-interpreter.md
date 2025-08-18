# Setting Up Python Interpreter for Love SMS Mondays in IntelliJ IDEA Ultimate

This guide will help you set up the Python interpreter for the Love SMS Mondays project in IntelliJ IDEA Ultimate.

## Prerequisites

- IntelliJ IDEA Ultimate installed
- Python 3.11 installed on your system (the project uses Python 3.11 for AWS Lambda)
- Git repository cloned to your local machine

## Step 1: Open the Project

1. Launch IntelliJ IDEA Ultimate
2. Select "Open" or "Open Project" from the welcome screen
3. Navigate to the directory where you cloned the Love SMS Mondays repository
4. Select the project folder and click "OK"

## Step 2: Set Up a Virtual Environment

1. Open the Terminal in IntelliJ IDEA (View > Tool Windows > Terminal)
2. Navigate to your project root directory (if not already there)
3. Create a virtual environment:
   ```bash
   # For Windows
   python -m venv venv
   
   # For macOS/Linux
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   ```bash
   # For Windows
   venv\Scripts\activate
   
   # For macOS/Linux
   source venv/bin/activate
   ```

## Step 3: Configure the Python Interpreter in IntelliJ IDEA

1. Go to File > Settings (or IntelliJ IDEA > Preferences on macOS)
2. Navigate to Project: love-sms-mondays > Python Interpreter
3. Click the gear icon in the top-right corner and select "Add..."
4. Select "Virtualenv Environment" on the left panel
5. Choose "Existing environment"
6. Click the "..." button and navigate to your project's virtual environment:
   - For Windows: `<project_path>\venv\Scripts\python.exe`
   - For macOS/Linux: `<project_path>/venv/bin/python`
7. Click "OK" to confirm the interpreter selection
8. Click "Apply" and then "OK" to save the settings

## Step 4: Install Dependencies

1. Make sure your virtual environment is activated in the Terminal
2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. This will also install the production dependencies from requirements.txt

## Step 5: Configure Run/Debug Configurations

### For Running Tests

1. Go to Run > Edit Configurations
2. Click the "+" button and select "Python tests > pytest"
3. Name the configuration "Run Tests"
4. Set the target to "script path" and select the test file (e.g., tests/test_app.py)
5. Make sure the Python interpreter is set to your virtual environment
6. Click "Apply" and "OK"

### For Running the Application Locally

1. Go to Run > Edit Configurations
2. Click the "+" button and select "Python"
3. Name the configuration "Run App Locally"
4. Set the script path to "app.py"
5. Add the following environment variables:
   ```
   PHONE_NUMBER=+15551230000
   PHRASES_TABLE=love-phrases
   API_URL=https://api.quotable.io/random
   ```
6. Make sure the Python interpreter is set to your virtual environment
7. Click "Apply" and "OK"

## Step 6: Verify Setup

1. Run the tests to verify your setup:
   - Go to Run > Run 'Run Tests'
   - The tests should execute successfully

## Troubleshooting

- **Missing Dependencies**: If you encounter errors about missing packages, try reinstalling the requirements:
  ```bash
  pip install -r requirements-dev.txt
  ```

- **Python Version Mismatch**: Ensure you're using Python 3.11 for compatibility with the AWS Lambda runtime.

- **Virtual Environment Not Recognized**: Make sure the virtual environment is properly activated and the path is correctly set in the interpreter settings.

- **AWS Credentials**: For local testing with AWS services, ensure your AWS credentials are properly configured in your environment.