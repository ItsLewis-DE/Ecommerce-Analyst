echo "=================================="
echo "Khởi chạy venv"
echo "=================================="
source .venv/bin/bash
bash localstack/init_s3.sh && \
bash localstack/init_lambda.sh && \
bash localstack/init_eventbridge.sh && \
python3 scripts/load_to_s3.py
