import os
from moto import mock_aws
import boto3, requests_mock
import logging
log = logging.getLogger(__name__)

@mock_aws
def test_handler_sends_message_and_saves_phrase():
    # Set environment variables
    os.environ["PHONE_NUMBER"] = "+15551230000"
    os.environ["PHRASES_TABLE"] = "love-phrases"
    os.environ["API_URL"] = "https://api.quotable.io/random"


    # Mock DynamoDB client
    ddb = boto3.client("dynamodb", region_name="us-east-1")
    ddb.create_table(
        TableName="love-phrases",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )

    from src.app import handler

    # Mock API response
    with requests_mock.Mocker() as mock_request:
        mock_request.get(
            "https://api.quotable.io/random",
            json={"author": "test", "content": "This is a test quote"}
        )

        # Call the handler
        event = {}  # Simulate a Lambda event (you can mock specifics here)
        result = handler(event, None)
        # Assertions/Validations
        # 1. Check if the handler ran successfully
        assert result

        # 2. Fetch the item from DynamoDB
        response = ddb.scan(TableName="love-phrases")
        items = response.get("Items", [])
        assert len(items) == 1  # The table should have one saved phrase
        log.info("Items: %s", items)

        # Check the saved content
        assert items[0]["author"]["S"] == "test"
        assert items[0]["text"]["S"] == "This is a test quote"

