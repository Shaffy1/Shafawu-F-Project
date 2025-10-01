import boto3
import os
import uuid
import json

def lambda_handler(event, context):
    print("Received event:", event)

    body = json.loads(event.get("body", "{}"))

    recordId = str(uuid.uuid4())
    voice = body["voice"]
    text = body["text"]

    print('Generating new DynamoDB record, with ID: ' + recordId)
    print('Input Text: ' + text)
    print('Selected voice: ' + voice)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])
    table.put_item(
        Item={
            'id': recordId,
            'text': text,
            'voice': voice,
            'status': 'processing'
        }
    )

    # Publish to SNS
    client = boto3.client('sns')
    client.publish(
        TopicArn=os.environ['SNS_TOPIC'],
        Message=recordId
    )
    
    # Also directly invoke convert function as backup
    lambda_client = boto3.client('lambda')
    try:
        lambda_client.invoke(
            FunctionName='content-convert-to-audio',
            InvocationType='Event',
            Payload=json.dumps({
                'Records': [{
                    'Sns': {
                        'Message': recordId
                    }
                }]
            })
        )
        print(f"Direct Lambda invocation sent for {recordId}")
    except Exception as e:
        print(f"Direct Lambda invocation failed: {e}")

    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Credentials": "false"
    }

    return {
        "statusCode": 200,
        "headers": cors_headers,
        "body": json.dumps(recordId)
    }