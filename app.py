import os, json, random, hashlib, logging
import boto3, botocore
import requests
from datetime import datetime, timezone

log = logging.getLogger()
log.setLevel(logging.INFO)

sns = boto3.client("sns")
dynamodb = boto3.resource("dynamodb")
ssm = boto3.client("ssm")

def _get_api_key(api_key_param):
    if not api_key_param:
        return None
    resp = ssm.get_parameter(Name=api_key_param, WithDecryption=False)
    return resp["Parameter"]["Value"]

def fetch_phrase(api_key_param, api_url):
    """
    Fetches a phrase and its author from a public API using the provided API key and URL.

    This function sends an HTTP GET request to the given API URL with the required API key
    as an authorization header. The function expects a specific response structure from
    the API, which should either be a JSON object or a list containing the text of the
    phrase and its author's information. The function normalizes the structure of the
    response to extract the text and author, handling various common formats.

    :param api_key_param: The parameter containing the API key used to authorize the
                          API request.
    :type api_key_param: str
    :param api_url: The URL of the API endpoint to fetch the phrase from.
    :type api_url: str
    :return: A tuple containing the phrase's text and its author's name, both strings.
    :rtype: tuple
    :raises ValueError: If the API response does not contain the phrase's text.
    :raises requests.exceptions.RequestException: If an HTTP request-related error occurs.
    """
    headers = {}
    key = _get_api_key(api_key_param)
    if key:
        # Adjust this header to match your public APIs auth schemeN
        headers["X-API-KEY"] = key

    r = requests.get(api_url, headers=headers, timeout=5)
    r.raise_for_status()
    data = r.json()

    # Normalize common shapes:
    # Quotable: {"content": "...", "author": "..."}    https://api.quotable.io/random
    # ZenQuotes: [{"q": "...", "a": "..."}]            https://zenquotes.io/api/random
    if isinstance(data, list) and data:
        data = data[0]

    text = data.get("content") or data.get("q") or data.get("text")
    author = data.get("author") or data.get("a") or data.get("by") or ""

    if not text:
        raise ValueError(f"API response missing text: {data}")

    return text.strip(), author.strip()

def save_phrase(table_name, text, author, source="api"):
    """
    Saves a phrase into a DynamoDB table.

    This function attempts to save a new phrase into a specified DynamoDB
    table. It assigns a unique ID to the phrase based on the provided text.
    If the phrase already exists in the table (based on its ID), it will not
    overwrite the existing entry. If the save operation is successful, a
    log entry is created to indicate the success.

    :param table_name: The name of the DynamoDB table where the phrase should
                       be stored.
    :type table_name: str
    :param text: The textual content of the phrase to save.
    :type text: str
    :param author: The author of the phrase being saved.
    :type author: str
    :param source: The source of the phrase. Defaults to "api".
    :type source: str, optional
    :return: None
    """
    pid = hashlib.sha256(text.encode("utf-8")).hexdigest()
    item = {
        "id": pid,
        "text": text,
        "author": author,
        "source": source,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    try:
        dynamodb.Table(table_name).put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(id)"  # dedupe
        )
        log.info("Saved new phrase %s", pid)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise
        log.info("Phrase already exists, not overwriting")

def pick_random_from_dynamo(table):
    """
    Pick a random item from an AWS DynamoDB table and return specific attributes.

    This function retrieves up to 100 items from the provided DynamoDB table using
    a scan operation. It selects a random item from the scanned results and
    returns its "text" and "author" attributes. The function may be inefficient
    for tables containing a large number of items, as the scan operation retrieves
    items sequentially.

    :param table: DynamoDB table object that provides access to the table.
    :type table: boto3.resources.factory.dynamodb.Table
    :return: A tuple containing the "text" attribute of the randomly selected item
        and its corresponding "author" attribute, if present. If the "author" attribute
        is not available, an empty string is returned as its value. If no items are
        retrieved, None is returned.
    :rtype: Optional[Tuple[str, str]]
    """
    # Cheap & simple for small tables. For large tables, use better sampling.
    resp = table.scan(ProjectionExpression="#id, #t, #a",
                      ExpressionAttributeNames={"#id":"id", "#t":"text", "#a":"author"},
                      Limit=100)
    items = resp.get("Items", [])
    if not items:
        return None
    choice = random.choice(items)
    return choice["text"], choice.get("author","")

FALLBACKS = [
    "Good morning, my love ❤️",
    "You make Mondays better. 😘",
    "New week, same love. Have a great day!",
]

def handler(event, context):
    phone = os.environ["PHONE_NUMBER"]                # E.164 e.g. +19045551234
    table_name = os.environ["PHRASES_TABLE"]          # CFN-provided table
    api_url = os.environ.get("API_URL", "https://api.quotable.io/random")
    api_key_param = os.environ.get("API_KEY_PARAM", "")  # Optional SSM param name

    try:
        text, author = fetch_phrase(api_key_param, api_url)
        save_phrase(table_name, text, author)
        msg = f"{text} — {author}" if author else text
    except Exception as e:
        log.warning("Fetch failed (%s). Falling back.", e)
        table = dynamodb.Table(table_name)
        picked = pick_random_from_dynamo(table)
        if picked:
            t, a = picked
            msg = f"{t} — {a}" if a else t
        else:
            msg = random.choice(FALLBACKS)

    sns.publish(PhoneNumber=phone, Message=msg)
    return {"statusCode": 200, "body": json.dumps({"sent": msg[:160]})}
