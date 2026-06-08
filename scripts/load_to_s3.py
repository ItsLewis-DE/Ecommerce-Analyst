import os
import boto3
import logging
from pathlib import Path
from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


BUCKET_RAW = os.getenv("BUCKET_RAW", "raw-bucket")

def upload_to_s3():
    logging.info(f"Bắt đầu upload các file từ {DATA_DIR} lên S3 bucket: {BUCKET_RAW}")
    
    s3_client = boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )
    
    csv_files = list(DATA_DIR.rglob("*.csv"))
    
    # glob trả về list rỗng [] nếu không thấy, chứ không trả về None
    if not csv_files:
        logging.warning("Không tìm thấy file .csv nào trong thư mục data!")
        return

    for file_path in csv_files:
        file_name = file_path.name 
        
        try:
            s3_client.upload_file(
                Filename=str(file_path), 
                Bucket=BUCKET_RAW, 
                Key=file_name
            )
            logging.info(f" Đã upload thành công: {file_name}")
            
        except ClientError as e:
            logging.error(f"Lỗi boto3 khi upload {file_name}: {e}")
        except Exception as e:
            logging.error(f"Lỗi hệ thống khi upload {file_name}: {e}")

if __name__ == "__main__":
    upload_to_s3()
