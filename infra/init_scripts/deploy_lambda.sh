#!/bin/bash
echo '======================================='
echo 'Deploy Lambda Function'
echo '======================================='

# Ensure we are at project root
cd "$(dirname "$0")/../.." || exit

echo 'Packaging function...'
zip -j function.zip src/lambda_functions/process_data/app.py

echo 'Package created successfully!'

# Get Role ARN
arn=$(awslocal iam get-role --role-name LambdaS3LoadRole --query 'Role.Arn' --output text)

echo 'Deploying Lambda...'
# Check if function exists
if awslocal lambda get-function --function-name transform-function > /dev/null 2>&1; then
    echo 'Updating existing function code...'
    awslocal lambda update-function-code \
        --function-name transform-function \
        --zip-file fileb://function.zip > /dev/null
else
    echo 'Creating new function...'
    awslocal lambda create-function \
        --function-name transform-function \
        --runtime python3.12 \
        --handler app.lambda_transfer \
        --role "$arn" \
        --zip-file fileb://function.zip \
        --environment "Variables={NAME_BUCKET_RAW=job-raw-bucket,NAME_BUCKET_PROCESSED=job-processed-bucket,KEY=latest_data.json}" > /dev/null
fi

echo 'Deployment complete!'