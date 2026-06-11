import boto3 
import json
import urllib.parse
import awswrangler as wr
import pandera as pa
from pandera import Column,DataFrameSchema,Check
import os,logging
from pathlib import Path
import pandas as pd 

session = boto3.Session()
s3_client = session.client('s3')
BUCKET_RAW = os.getenv('BUCKET_RAW','raw-bucket')
BUCKET_PROCESSED = os.getenv('BUCKET_PROCESSED','process-bucket')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

interaction_schema = DataFrameSchema(
    {
        "interaction_id": Column(str, Check.str_matches(r'^[0-9a-fA-F\-]+$'), nullable=False),
        "user_id": Column(str, Check.str_matches(r'^[0-9a-fA-F\-]+$'), nullable=True),
        "product_id": Column(str, Check.str_matches(r'^[0-9a-fA-F\-]+$'), nullable=True),
        "session_id": Column(str, Check.str_matches(r'^[0-9a-fA-F\-]+$'), nullable=True),
        "interaction_type": Column(str, nullable=True),
        "timestamp": Column(str, nullable=True),
        "dwell_time_ms": Column(float, Check.ge(0), nullable=True),
    },
    strict=False, 
    coerce=True   
)
def lambda_handler(event,context):
    logger = logging.getLogger(__name__)
    s3_record = event['Records'][0]
    event_name = s3_record['eventName']
    logger.info(f"Đang xử lí: {event}")

    file_key = urllib.parse.unquote_plus(s3_record['s3']['object']['key'])
    file_name = Path(file_key).stem

    s3_path_in = f"s3://{s3_record['s3']['bucket']['name']}/{file_key}"
    s3_path_out = f's3://{BUCKET_PROCESSED}/{file_name}.parquet'
    try:
        #1. Đọc dữ liệu từ s3
        dfs_iterator = wr.s3.read_csv(path=s3_path_in,chunksize=10000)

        chunk_idx = 0
        is_first_chunk = True
        #2. Đọc dữ liệu theo chunk
        for chunk_df in dfs_iterator:
            chunk_idx +=1
            logger.info(f"Đang xử lí chunk thứ {chunk_idx}")

            # -----------------------------------------------------
            # 2. TRANSFORMATION (Xử lí dữ liệu)
            # -----------------------------------------------------

            chunk_df['time_stamp'] = pd.to_datetime(chunk_df['timestamp'],errors='coerce')
            chunk_df['year'] = chunk_df['time_stamp'].dt.year
            chunk_df['month'] = chunk_df['time_stamp'].dt.month
            chunk_df = chunk_df.dropna(axis=0,how='any',subset=['user_id','product_id','session_id'])
            chunk_df['dwell_time_ms'] = chunk_df['dwell_time_ms'].fillna(0).abs()
            chunk_df['interaction_type'] = chunk_df['interaction_type'].str.lower().str.strip()
            # -----------------------------------------------------
            # 3. VALIDATION (Kiểm tra dữ liệu qua Data Contract)
            # -----------------------------------------------------

            try:
                logger.info(f"Đang tiến hành validate dữ liệu của chunk thứ {chunk_idx}")
                chunk_df = interaction_schema.validate(chunk_df)
            except pandera.errors.SchemaError as exc:
                logger.error(f"Dữ liệu bị sai.Lỗi tại cột {exc.schema.name}")
                logger.error(f"CHi tiết lỗi {exc}")
                raise
            
            write_mode = 'overwrite' if is_first_chunk else 'append'
            wr.s3.to_parquet(
                df=chunk_df,
                path = s3_path_out,
                dataset=True,
                mode = write_mode
            )
            is_first_chunk = False
        logger.info("Đã xử lí xong toàn bộ các file!")
    except Exception as e:
        logger.error(f'Có lỗi xãy ra trong khi xử lí dữ liệu!')
        raise

