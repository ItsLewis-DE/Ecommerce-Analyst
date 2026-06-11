!/bin/bash
export AWS_PAGER=""


#!/bin/bash
echo '============================================='
echo 'Đang khởi tạo IAM role'
echo '============================================='

TRUST_POLICY='{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}'

echo " Đang tạo role cho Lambda đọc dữ liệu"

awslocal iam create-role \
    --role-name LambdaRole \
    --assume-role-policy-document "$TRUST_POLICY"

PERMISION_READ_POLICY='{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AccessS3",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::raw-bucket",
                "arn:aws:s3:::raw-bucket/*"
            ]
        },
        {
            "Sid": "LambdaCloudWatchLogsAccess",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}'

echo "Đang tạo policy"

ARN_READ=$(awslocal iam create-policy \
    --policy-name read-s3-policy \
    --policy-document "$PERMISION_READ_POLICY" \
    --query 'Policy.Arn' \
    --output text
)

echo "Đang gán policy cho Role Lambda đọc dữ liệu"

awslocal iam attach-role-policy \
        --role-name LambdaRole \
        --policy-arn "$ARN_READ"

PERMISION_TRANSFORM_POLICY='{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AccessS3",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::process-bucket",
                "arn:aws:s3:::process-bucket/*"
            ]
        },
        {
            "Sid": "LambdaCloudWatchLogsAccess",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}'

echo "Tạo policy cho Lambda transform"

ARN_TRANSFORM=$(awslocal iam create-policy \
    --policy-name transform-s3-policy \
    --policy-document "$PERMISION_TRANSFORM_POLICY" \
    --query 'Policy.Arn' \
    --output text
)

echo "Gán policy vào Role của Lambda transform"

awslocal iam attach-role-policy \
        --role-name LambdaRole \
        --policy-arn "$ARN_TRANSFORM"


echo "Kiểm tra đã khởi tạo Role thành công chưa"

awslocal iam list-roles --query 'Roles[*].RoleName' --output table

echo "============================"
echo "Khởi tạo Role thành công"
echo "============================"