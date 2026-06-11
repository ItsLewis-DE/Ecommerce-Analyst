#!/bin/bash
export AWS_PAGER=""

echo "===================================="
echo "Tạo Lambda Layer cho thư viện"
echo "===================================="

echo "Đang chuẩn bị thư viện (awswrangler & pandera)..."
# Dọn dẹp thư mục cũ nếu chạy lại script nhiều lần
rm -rf python/ my_data_layer.zip 
mkdir -p python/

wget https://github.com/aws/aws-sdk-pandas/releases/download/3.7.3/awswrangler-layer-3.7.3-py3.12.zip -O awswrangler.zip
unzip -qo awswrangler.zip
rm awswrangler.zip

pip install --upgrade pandera -t python/ > /dev/null

echo "===================================="
echo "Khởi tạo các function cho Lambda qua S3"
echo "===================================="

# Ngăn AWS CLI sử dụng multipart upload cho file ZIP dưới 100MB
aws configure set default.s3.multipart_threshold 100MB


FUNCTIONS=(
    "users_trans"
    "products_trans"
    "sessions_trans"
    "interactions_trans"
    "purchases_trans"
    "reviews_trans"
)

for FUNC in "${FUNCTIONS[@]}"; do
    echo "------------------------------------"
    echo "Đang tạo file zip Code cho hàm $FUNC..."
    
    rm -f code_$FUNC.zip
    
    # 1. Copy file handler.py của hàm vào chung thư mục chứa thư viện (thư mục python/)
    cp src/functions/$FUNC/handler.py python/handler.py
    
    # 2. Đi vào thư mục python/ và nén TẤT CẢ (thư viện + handler) thành 1 file ZIP duy nhất
    cd python
    zip -rq ../code_$FUNC.zip .
    cd ..
    
    echo "Đang upload zip của $FUNC lên S3..."
    awslocal s3 cp code_$FUNC.zip s3://lambda-deploy-bucket/code_$FUNC.zip
    
    echo "Đang khởi tạo hàm $FUNC trên LocalStack..."
    awslocal lambda delete-function --function-name $FUNC 2>/dev/null
    
    # 3. Tạo function mới (bỏ tham số --layers và sửa đường dẫn --handler)
    awslocal lambda create-function \
        --function-name $FUNC \
        --runtime python3.12 \
        --handler handler.lambda_handler \
        --role arn:aws:iam::000000000000:role/LambdaRole \
        --code S3Bucket=lambda-deploy-bucket,S3Key=code_$FUNC.zip \
        --timeout 300 \
        --memory-size 1024
done


echo "===================================="
echo "Khởi tạo thành công ${#FUNCTIONS[@]} hàm Lambda với Layer dùng chung!"