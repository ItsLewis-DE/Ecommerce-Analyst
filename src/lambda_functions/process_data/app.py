import json
import boto3
import os
import pandas as pd
s3_client = boto3.client('s3')
bucket_name = os.getenv('NAME_BUCKET_RAW','job-raw-bucket')
key = os.getenv('KEY','latest_data.json')
def lambda_transfer(event,context):
    response = s3_client.get_object(Bucket = bucket_name,Key=key)
    file_content = response['Body'].read().decode('utf-8')
    full_jobs = json.loads(file_content)
    data = []
    pattern = r'[\[\(\-\,\:]'
    for job in full_jobs:
        company=job['company']
        clean_job = {
            'job_id':job.get('id'),
            'job_name':re.split(pattern,job.get('title'))[0].strip(),
            'company_id':company['id'],
            'company_name':company['name'],
            'city':job.get('short_cities'),
            'salary':job.get('salary'),
            'working_times': job.get('working_times')[0],
            'type':job.get('type'),
            'experience':job.get('experience'),
            'address':job.get('address')
        }
        data.append(clean_job)
    s3_client.put_object(
        Bucket=
    )

