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
        path = event.get('path', '')
        method = event['httpMethod']
        
        print(f"Received request: {method} {path}")
        print(f"Event: {json.dumps(event)}")
        
        if path == '/new_post' and method == 'POST':
            return create_post(event, headers)
        elif path == '/get-post' and method == 'GET':
            return get_post(event, headers)
        else:
            return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': f'Path {path} not found'})}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}

def create_post(event, headers):
    try:
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
        
        # Generate audio with Polly immediately
        polly = boto3.client('polly')
        s3 = boto3.client('s3')
        
        print(f"Generating speech for text: {body['text']} with voice: {body['voice']}")
        
        response = polly.synthesize_speech(
            Text=body['text'],
            OutputFormat='mp3',
            VoiceId=body['voice']
        )
        
        # Read audio stream
        audio_data = response['AudioStream'].read()
        print(f"Generated audio data size: {len(audio_data)} bytes")
        
        # Save to S3 with public access
        s3.put_object(
            Bucket=os.environ['AUDIO_BUCKET'],
            Key=f"{post_id}.mp3",
            Body=audio_data,
            ContentType='audio/mpeg',
            ACL='public-read'
        )
        
        audio_url = f"https://{os.environ['AUDIO_BUCKET']}.s3.amazonaws.com/{post_id}.mp3"
        print(f"Audio saved to: {audio_url}")
        
        # Update status to completed
        table.update_item(
            Key={'id': post_id},
            UpdateExpression='SET #status = :status, #url = :url',
            ExpressionAttributeNames={'#status': 'status', '#url': 'url'},
            ExpressionAttributeValues={
                ':status': 'completed',
                ':url': audio_url
            }
        )
        
        print(f"Successfully processed post {post_id}")
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps(post_id)}
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}

def get_post(event, headers):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
        
        query_params = event.get('queryStringParameters') or {}
        post_id = query_params.get('postId', '*')
        
        if post_id == '*':
            items = table.scan()['Items']
        else:
            response = table.get_item(Key={'id': post_id})
            items = [response['Item']] if 'Item' in response else []
        
        # Ensure all items have required fields
        for item in items:
            if 'url' not in item:
                item['url'] = None
            if 'status' not in item:
                item['status'] = 'unknown'
                
        print(f"Retrieved {len(items)} items for postId: {post_id}")
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps(items)}
        
    except Exception as e:
        print(f"Error retrieving post: {str(e)}")
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}