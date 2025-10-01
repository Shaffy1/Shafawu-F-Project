import boto3
import os
from boto3.dynamodb.conditions import Key
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DB_TABLE_NAME'])

BUCKET_NAME = os.environ["BUCKET_NAME"]
REGION = boto3.session.Session().region_name

def lambda_handler(event, context):
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Credentials": "false"
    }
    
    # Handle preflight OPTIONS request
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": ""
        }

    postId = event.get("queryStringParameters", {}).get("postId", "")

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
            # Check for both possible status values
            if item.get("status") in ["COMPLETED", "completed"]:
                item["url"] = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{item['id']}.mp3"
            else:
                item["url"] = None
                # If still processing, check if audio file exists in S3
                if item.get("status") in ["PROCESSING", "processing"]:
                    s3 = boto3.client('s3')
                    try:
                        s3.head_object(Bucket=BUCKET_NAME, Key=f"{item['id']}.mp3")
                        item["url"] = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{item['id']}.mp3"
                        item["status"] = "completed"
                    except:
                        pass

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