import json
import boto3
import uuid
import os

def handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        path = event['path']
        method = event['httpMethod']
        
        if path == '/new_post' and method == 'POST':
            return create_post(event, headers)
        elif path == '/get_post' and method == 'GET':
            return get_post(event, headers)
        else:
            return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Not found'})}
            
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}

def create_post(event, headers):
    body = json.loads(event['body'])
    post_id = str(uuid.uuid4())
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
    # Save to DynamoDB
    table.put_item(Item={
        'id': post_id,
        'text': body['text'],
        'voice': body['voice'],
        'status': 'processing'
    })
    
    # Generate audio with Polly
    try:
        polly = boto3.client('polly')
        s3 = boto3.client('s3')
        
        response = polly.synthesize_speech(
            Text=body['text'],
            OutputFormat='mp3',
            VoiceId=body['voice']
        )
        
        # Save to S3
        s3.put_object(
            Bucket=os.environ['AUDIO_BUCKET'],
            Key=f"{post_id}.mp3",
            Body=response['AudioStream'].read(),
            ContentType='audio/mpeg',
            ACL='public-read'
        )
        
        # Update status
        table.update_item(
            Key={'id': post_id},
            UpdateExpression='SET #status = :status, #url = :url',
            ExpressionAttributeNames={'#status': 'status', '#url': 'url'},
            ExpressionAttributeValues={
                ':status': 'completed',
                ':url': f"https://{os.environ['AUDIO_BUCKET']}.s3.amazonaws.com/{post_id}.mp3"
            }
        )
        
    except Exception as e:
        print(f"Error processing audio: {e}")
    
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps(post_id)}

def get_post(event, headers):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
    post_id = event['queryStringParameters']['postId']
    
    if post_id == '*':
        items = table.scan()['Items']
    else:
        response = table.get_item(Key={'id': post_id})
        items = [response['Item']] if 'Item' in response else []
    
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps(items)}