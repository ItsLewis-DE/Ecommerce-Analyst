#!/bin/bash 
export AWS_PAGER=""

echo "=========================="
echo "Đang cấu hình eventbridge cho DuckDB Lambda"
echo "=========================="

awslocal events put-rule \
    --name "duckdb-analytics-schedule" \
    --schedule-expression "cron(0 * * * ? *)" \
    --state "ENABLED"

echo "Đang cấp quyền cho EventBridge để gọi hàm Lambda"

awslocal lambda add-permission \
    --function-name function_analys \
    --statement-id EventBridgeInvoke \
    --action "lambda:InvokeFunction" \
    --principal events.amazonaws.com \
    --source-arn "arn:aws:events:us-east-1:000000000000:rule/duckdb-analytics-schedule" 2>/dev/null || true

awslocal events put-targets \
    --rule "duckdb-analytics-schedule" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:000000000000:function:function_analys"
    
echo "Cấu hình EventBridge hoàn tất!"