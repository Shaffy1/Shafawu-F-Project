#!/bin/bash
# Get API URL from Terraform outputs
cd terraform
API_URL=$(terraform output -raw api_url)
echo "API URL: $API_URL"

# Update JavaScript file
cd ../website
sed -i "s|https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod|$API_URL|g" scripts.js

# Get website bucket and upload updated file
cd ../terraform
WEBSITE_BUCKET=$(terraform output -raw website_bucket)
echo "Website bucket: $WEBSITE_BUCKET"

# Upload updated JavaScript
aws s3 cp ../website/scripts.js s3://$WEBSITE_BUCKET/scripts.js --content-type "application/javascript"

echo "API URL updated and JavaScript file uploaded successfully!"