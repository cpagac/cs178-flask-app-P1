import boto3
import uuid
from datetime import datetime, timezone
import creds

def get_dynamo_table():
    dynamodb = boto3.resource("dynamodb", region_name=creds.aws_region)
    return dynamodb.Table(creds.dynamo_table)

def get_or_create_user(username):
    table = get_dynamo_table()
    response = table.get_item(Key={"username": username})
    item = response.get("Item")
    if item:
        return item["user_id"]
    user_id = str(uuid.uuid4())
    table.put_item(Item={
        "username": username,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "games_played": 0,
    })
    return user_id

def increment_games_played(username):
    try:
        table = get_dynamo_table()
        table.update_item(
            Key={"username": username},
            UpdateExpression="ADD games_played :inc",
            ExpressionAttributeValues={":inc": 1},
        )
    except Exception as e:
        print(f"[dynamoCode] increment_games_played failed: {e}")
