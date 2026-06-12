#!/bin/bash
export AWS_PAGER=""

echo "========================================="
echo "Dang khởi tạo các bucket cần thiết!"
echo "========================================="

awslocal s3 mb s3://raw-bucket

awslocal s3 mb s3://process-bucket

awslocal s3 mb s3://lambda-deploy-bucket


echo "========================================="
echo "Đã khởi tạo xong các bucket"
echo "========================================="