import boto3
import os
import json
import uuid

polly = boto3.client('polly')
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables set in Terraform
table_name = os.environ['DB_TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME']
region = os.environ.get('AWS_REGION', 'us-east-1')

table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    post_id = event['Records'][0]['Sns']['Message']
    print("Processing post_id:", post_id)

    # Fetch post from DynamoDB
    response = table.get_item(Key={'id': post_id})
    item = response.get('Item')
    if not item:
        print(f"No post found with id {post_id}")
        return {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"error": f"No post found with id {post_id}"})
        }

    text = item['text']
    voice = item.get('voice', 'Joanna')

    # Generate speech using Polly
    polly_response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=voice
    )

    # Save MP3 to S3
    s3_key = f"{post_id}.mp3"
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=polly_response['AudioStream'].read(),
        ContentType="audio/mpeg"
    )

    # Generate public S3 URL
    s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"

    # Update DynamoDB with status + URL
    table.update_item(
        Key={'id': post_id},
        UpdateExpression="SET #s = :s, #u = :u",
        ExpressionAttributeNames={
            "#s": "status",
            "#u": "url"
        },
        ExpressionAttributeValues={
            ":s": "completed",
            ":u": s3_url
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({"id": post_id, "url": s3_url})
    }