import json
import logging
from curl_cffi import requests
import boto3
from botocore.exceptions import ClientError
from .config import AWS_ENDPOINT_URL, BUCKET_NAME_RAW, COOKIES, HEADERS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def init_s3_client():
    return boto3.client(
        's3',
        endpoint_url=AWS_ENDPOINT_URL,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )

def fetch_jobs() -> list:
    all_jobs = []
    page = 1
    
    while page <= 10:
        data = {
            'page': page,
            'limit': 100,
            'city': 0,
            'salary': None,
            'exp': None,
            'category': None,
            'reRanking': '[]',
        }
        try:
            logging.info(f"Đang gửi request trang {page}...")
            response = requests.post(
                'https://www.topcv.vn/api-featured-jobs', 
                cookies=COOKIES, 
                headers=HEADERS, 
                json=data, 
                impersonate="chrome"
            )
            
            logging.info(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                res_json = response.json()
                jobs = res_json.get('jobs', [])
                all_jobs.extend(jobs)
                
                if not jobs:
                    logging.info("Đã hết dữ liệu ở page này!")
                    break
            elif response.status_code == 419:
                logging.warning("Lỗi 419 (Page Expired) - CSRF Token hoặc Session đã hết hạn. Cần cập nhật lại cookies.json/headers.json!")
                break
            else:
                logging.error(f"Lỗi {response.status_code}: {response.text[:200]}")
                break

        except Exception as e:
            logging.error(f"Lỗi hệ thống khi gọi API: {e}")
            break
            
        page += 1

    return all_jobs

def upload_to_s3(s3_client, jobs: list):
    try:
        logging.info(f"Tổng số jobs lấy được: {len(jobs)}")
        logging.info("Đang upload lên S3...")
        
        # Save locally as well just in case
        with open('output.json', 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
            
        s3_client.put_object(
            Bucket=BUCKET_NAME_RAW,
            Key='latest_data.json',
            Body=json.dumps(jobs, ensure_ascii=False, indent=2).encode('utf-8')
        )
        logging.info("Đã upload thành công lên S3!")
    except ClientError as e:
        logging.error(f"Lỗi khi upload lên S3: {e}")

def main():
    s3_client = init_s3_client()
    jobs = fetch_jobs()
    if jobs:
        upload_to_s3(s3_client, jobs)
    else:
        logging.warning("Không có dữ liệu nào được lấy!")

if __name__ == "__main__":
    main()
