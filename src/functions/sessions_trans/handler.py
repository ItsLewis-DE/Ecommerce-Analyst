import boto3 
import json
import urllib.parse
import io
import pandera as pa
from pandera import Column,DataFrameSchema,Check
import os,logging
from pathlib import Path
import pandas as pd 
import numpy as np

session = boto3.Session()
s3_client = session.client('s3')

BUCKET_RAW = os.getenv('BUCKET_RAW','raw-bucket')
BUCKET_PROCESSED = os.getenv('BUCKET_PROCESSED','process-bucket')


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

sessions_schema = DataFrameSchema(
    {
        # Kiểm tra ID phải đúng chuẩn format UUID (chữ, số, dấu gạch ngang)
        "session_id": Column(str, Check.str_matches(r'^[0-9a-fA-F\-]+$'), nullable=False),
        "user_id": Column(str,Check.str_matches(r'^[0-9a-fA-F\-]+$'),nullable=False),
        "start_time": Column(pa.DateTime,nullable=False),
        "device_type": Column(str,nullable=True),
        "referrer_source": Column(str,nullable=True),
        "is_converted": Column(bool, nullable=True),
    },
    strict=False, 
    coerce=True   
)   

def lambda_handler(event,context):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    s3_record = event['Records'][0]
    event_name = s3_record['eventName']
    logger.info(f"Đang xử lí: {event}")

    file_key = urllib.parse.unquote_plus(s3_record['s3']['object']['key'])
    file_name = Path(file_key).stem

    bucket_in = s3_record['s3']['bucket']['name']
    try:
        #1. Đọc dữ liệu từ s3
        response = s3_client.get_object(Bucket=bucket_in, Key=file_key)
        dfs_iterator = pd.read_csv(response['Body'], chunksize=10000)

        chunk_idx = 0
        is_first_chunk = True
        #2. Đọc dữ liệu theo chunk
        for chunk_df in dfs_iterator:
            chunk_idx +=1
            logger.info(f"Đang xử lí chunk thứ {chunk_idx}")

            # -----------------------------------------------------
            #  Transformation
            # -----------------------------------------------------
            chunk_df['device_type'] = chunk_df['device_type'].str.title()
            chunk_df['referrer_source'] = chunk_df['referrer_source'].str.title()
            chunk_df['start_time'] = pd.to_datetime(chunk_df['start_time'],errors='coerce')
            chunk_df['year'] = chunk_df['start_time'].dt.year 
            chunk_df['month'] = chunk_df['start_time'].dt.month

            # -----------------------------------------------------
            # 3. VALIDATION (Kiểm tra dữ liệu qua Data Contract)
            # -----------------------------------------------------
            try:
                logger.info(f"Đang tiến hành validate dữ liệu của chunk thứ {chunk_idx}")
                chunk_df = sessions_schema.validate(chunk_df)
            except pa.errors.SchemaError as exc:
                logger.error(f"Dữ liệu bị sai.Lỗi tại cột {exc.schema.name}")
                logger.error(f"CHi tiết lỗi {exc}")
                raise
            
            out_key = f"{file_name}.parquet/part_{chunk_idx}.parquet"
            parquet_buffer = io.BytesIO()
            chunk_df.to_parquet(parquet_buffer, index=False)
            
            s3_client.put_object(
                Bucket=BUCKET_PROCESSED,
                Key=out_key,
                Body=parquet_buffer.getvalue()
            )
            is_first_chunk = False
        logger.info("Đã xử lí xong toàn bộ các file!")
    except Exception as e:
        logger.error(f'Có lỗi xãy ra trong khi xử lí dữ liệu!')
        raise        