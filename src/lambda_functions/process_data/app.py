import json
import boto3
import os
import re
import logging
from typing import Any, Dict

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients outside of the handler for performance (execution environment reuse)
# For localstack, we need to handle endpoint_url if provided.
aws_endpoint = os.getenv('AWS_ENDPOINT_URL')
if aws_endpoint:
    s3_client = boto3.client('s3', endpoint_url=aws_endpoint)
else:
    s3_client = boto3.client('s3')

BUCKET_RAW = os.getenv('NAME_BUCKET_RAW', 'job-raw-bucket')
BUCKET_PROCESSED = os.getenv('NAME_BUCKET_PROCESSED', 'job-processed-bucket')
FILE_KEY = os.getenv('KEY', 'latest_data.json')

def clean_data(full_jobs: list) -> list:
    """
    Cleans and extracts specific fields from the raw job data.
    """
    data = []
    pattern = r'[\[\(\-\,\:]'
    for job in full_jobs:
        company = job.get('company', {})
        working_times = job.get('working_times')
        
        clean_job = {
            'job_id': job.get('id'),
            'job_name': re.split(pattern, str(job.get('title', '')))[0].strip(),
            'company_id': company.get('id'),
            'company_name': company.get('name'),
            'city': job.get('short_cities'),
            'salary': job.get('salary'),
            'working_times': working_times[0] if working_times else None,
            'type': job.get('type'),
            'experience': job.get('experience'),
            'address': job.get('address')
        }
        data.append(clean_job)
    return data

def lambda_transfer(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler to read raw jobs from S3, clean them, and save back to S3.
    """
    logger.info(f"Triggered lambda_transfer. Reading from {BUCKET_RAW}/{FILE_KEY}")
    
    try:
        # Get raw data
        response = s3_client.get_object(Bucket=BUCKET_RAW, Key=FILE_KEY)
        file_content = response['Body'].read().decode('utf-8')
        full_jobs = json.loads(file_content)
        
        logger.info(f"Successfully loaded {len(full_jobs)} jobs from {BUCKET_RAW}")
        
        # Clean data
        cleaned_data = clean_data(full_jobs)
        
        # Save processed data
        s3_client.put_object(
            Bucket=BUCKET_PROCESSED,
            Key=FILE_KEY,
            Body=json.dumps(cleaned_data, ensure_ascii=False, indent=2).encode('utf-8')
        )
        logger.info(f"Successfully saved {len(cleaned_data)} cleaned jobs to {BUCKET_PROCESSED}")
        
        return {
            "statusCode": 200,
            "message": "Processed and saved file successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "message": f"Internal Server Error: {str(e)}"
        }
