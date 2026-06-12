#!/bin/bash
export AWS_PAGER=""

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
    
    # Định nghĩa tên thư mục tạm cho chuẩn xác
    PACKAGE_DIR="${FUNC}_package"
    rm -rf $PACKAGE_DIR
    
    # Cài đặt thư viện vào thư mục tạm
    pip install -r src/functions/${FUNC}/requirements.txt -t $PACKAGE_DIR

    # Copy file code chính vào thư mục tạm
    cp src/functions/${FUNC}/handler.py $PACKAGE_DIR

    # Quan trọng: CD vào trong thư mục tạm để nén, 
    # đảm bảo code nằm ở root của file zip (không bị lồng trong thư mục con)
    pushd $PACKAGE_DIR > /dev/null
    zip -r ../${FUNC}.zip . > /dev/null
    popd > /dev/null
     
    echo "Đang upload zip của $FUNC lên S3..."
    awslocal s3 cp ${FUNC}.zip s3://lambda-deploy-bucket/${FUNC}.zip
    
    echo "Đang khởi tạo hàm $FUNC trên LocalStack..."
    awslocal lambda delete-function --function-name $FUNC 2>/dev/null
    
    # Tạo function mới
    awslocal lambda create-function \
        --function-name $FUNC \
        --runtime python3.12 \
        --handler handler.lambda_handler \
        --role arn:aws:iam::000000000000:role/LambdaRole \
        --code S3Bucket=lambda-deploy-bucket,S3Key=${FUNC}.zip \
        --timeout 300 \
        --memory-size 8192
        
    # Xoá file zip và thư mục build tạm ngay trong vòng lặp cho sạch sẽ
    rm ${FUNC}.zip
    rm -rf $PACKAGE_DIR
done

echo "Áp dụng config cho bucket"
awslocal s3api put-bucket-notification-configuration \
    --bucket raw-bucket \
    --notification-configuration file://notification.json

echo "===================================="
# Sửa lại câu báo cáo vì cách này là đóng gói độc lập, không dùng Layer
echo "Khởi tạo thành công ${#FUNCTIONS[@]} hàm Lambda với các packages được đóng gói độc lập!"