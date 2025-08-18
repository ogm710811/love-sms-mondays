import os
import sys
import pytest
import boto3
from pathlib import Path
from moto import mock_aws

# Add the project root directory to Python's module search path
root_dir = Path(__file__).parent.parent  # This gets the parent directory of the tests directory
sys.path.insert(0, str(root_dir))

@pytest.fixture(autouse=True)
def aws_credentials(monkeypatch):
    """Fake AWS creds for all tests."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-2")
