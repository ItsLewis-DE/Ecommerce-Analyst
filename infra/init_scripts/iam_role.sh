#!/bin/bash

# 1. Trust Policy
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

echo "Creating role: lambda-s3-role..."
awslocal iam create-role \
    --role-name lambda-s3-role \
    --assume-role-policy-document "$TRUST_POLICY"

# 2. Cleanse Policy
CLEANSE_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::yt-landing-bucket",
        "arn:aws:s3:::yt-landing-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::yt-cleansed-bucket",
        "arn:aws:s3:::yt-cleansed-bucket/*"
      ]
    }
  ]
}'

echo "Creating and attaching policy: lambda-policy..."
ARN=$(awslocal iam create-policy \
    --policy-name lambda-policy \
    --policy-document "$CLEANSE_POLICY" \
    --query 'Policy.Arn' --output text)

awslocal iam attach-role-policy \
    --role-name lambda-s3-role \
    --policy-arn "$ARN"

# 3. Transform Policy
TRANSFORM_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::yt-cleansed-bucket",
        "arn:aws:s3:::yt-cleansed-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::yt-analytics-bucket",
        "arn:aws:s3:::yt-analytics-bucket/*"
      ]
    }
  ]
}'

echo "Creating and attaching policy: lambda-transform-policy..."
ARN_TRANSFORM=$(awslocal iam create-policy \
    --policy-name lambda-transform-policy \
    --policy-document "$TRANSFORM_POLICY" \
    --query 'Policy.Arn' --output text)

awslocal iam attach-role-policy \
    --role-name lambda-s3-role \
    --policy-arn "$ARN_TRANSFORM"

# 4. Landing Write Policy (Đã bổ sung biến bị thiếu)
LANDING_WRITE_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::yt-landing-bucket",
        "arn:aws:s3:::yt-landing-bucket/*"
      ]
    }
  ]
}'

echo "Creating policy: s3-landing-write-policy..."
awslocal iam create-policy \
  --policy-name s3-landing-write-policy \
  --policy-document "$LANDING_WRITE_POLICY"

echo "List of IAM Roles:"
awslocal iam list-roles --query 'Roles[*].RoleName'

echo "List of IAM Users:"
awslocal iam list-users --query 'Users[*].UserName'

echo "List of Customer Managed Policies:"
awslocal iam list-policies --scope Local --query 'Policies[*].PolicyName'

echo "Attached Policies to lambda-s3-role:"
awslocal iam list-attached-role-policies --role-name lambda-s3-role --query 'AttachedPolicies[*].PolicyName'

echo "Attached Policies to clickhouse-user:"
awslocal iam list-attached-user-policies --user-name clickhouse-user --query 'AttachedPolicies[*].PolicyName'

echo "=========== IAM Setup Completed Successfully ==========="
