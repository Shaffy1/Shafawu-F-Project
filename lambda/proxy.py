import json
import boto3
import os
import uuid

def lambda_handler(event, context):
    # CORS headers for all responses
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        path = event['path']
        method = event['httpMethod']
        
        if path == '/new_post' and method == 'POST':
            return handle_new_post(event, headers)
        elif path == '/get-post' and method == 'GET':
            return handle_get_post(event, headers)
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def handle_new_post(event, headers):
    body = json.loads(event['body'])
    record_id = str(uuid.uuid4())
    
    # Save to DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('content_posts')
    table.put_item(Item={
        'id': record_id,
        'text': body['text'],
        'voice': body['voice'],
        'status': 'processing'
    })
    
    # Trigger conversion
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName='content-convert-to-audio',
        InvocationType='Event',
        Payload=json.dumps({
            'Records': [{'Sns': {'Message': record_id}}]
        })
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(record_id)
    }

def handle_get_post(event, headers):
    post_id = event['queryStringParameters']['postId']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('content_posts')
    
    if post_id == '*':
        items = table.scan()['Items']
    else:
        response = table.get_item(Key={'id': post_id})
        items = [response['Item']] if 'Item' in response else []
    
    # Add URLs for completed items
    for item in items:
        if item.get('status') == 'completed':
            item['url'] = f"https://audio-storage-bucket-unique-2025.s3.us-east-1.amazonaws.com/{item['id']}.mp3"
        else:
            item['url'] = None
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(items)
    }