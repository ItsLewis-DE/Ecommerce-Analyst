#!/bin/bash
echo '======================================='
echo 'Create Bucket In S3'
echo '======================================='

awslocal s3 mb s3://job-raw-bucket

awslocal s3 mb s3://job-processed-bucket

echo 'Listing bucket'

awslocal s3 ls

echo 'Done'