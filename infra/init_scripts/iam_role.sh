echo 'Gan Role cho ham lambda'

s3_get_policy='{
    "Version":"2012-10-17",
    "Statement": [
        {
            "Effect":"Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::job-raw-bucket",
                "arn:aws:s3:::job-raw-bucket/*"
            ]
        }
    ]
}'

arn=$(awslocal iam get-role --role-name LambdaS3LoadRole --query 'Role.Arn' --output text 2>/dev/null)
if [ -z "$arn" ]; then
    echo 'Role chua ton tai. Dang khoi tao....'
    arn=$(awslocal iam create-role --role-name LambdaS3LoadRole \
        --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
        --query 'Role.Arn' \
        --output text
        )
else 
    echo "Role da khoi tao. Se su dung role cu!"
fi 
    
echo 'Tao thanh cong arn'

awslocal iam put-role-policy --role-name LambdaS3LoadRole \
    --policy-name S3GetPolicy \
    --policy-document "$s3_get_policy"

echo 'Dang nen file'

zip -j function.zip src/lambda_functions/process_data/app.py

echo 'Nen file thanh cong!'

awslocal lambda delete-function --function-name transform-function 2>/dev/null

awslocal lambda create-function \
    --function-name transform-function \
    --runtime python3.12 \
    --handler app.lambda_transfer \
    --role $arn \
    --zip-file fileb://function.zip \
    --environment "Variables={NAME_BUCKET_RAW=job-raw-bucket,KEY=latest_data.json}"
