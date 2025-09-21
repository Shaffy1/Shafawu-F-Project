import boto3
import os
from boto3.dynamodb.conditions import Key
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DB_TABLE_NAME'])

BUCKET_NAME = os.environ["BUCKET_NAME"]
REGION = boto3.session.Session().region_name  # ✅ detect automatically

def lambda_handler(event, context):
    postId = event.get("queryStringParameters", {}).get("postId", "")

    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    if not postId:
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": json.dumps({"error": "Missing or empty postId"})
        }

    try:
        if postId == "*":
            items = table.scan()["Items"]
        else:
            items = table.query(
                KeyConditionExpression=Key('id').eq(postId)
            )["Items"]

        for item in items:
            if item.get("status") == "COMPLETED":
                item["url"] = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{item['id']}.mp3"
            else:
                item["url"] = None

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps(items)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)})
        }