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

product_schema = DataFrameSchema(
    {
        # Kiểm tra ID phải đúng chuẩn format UUID (chữ, số, dấu gạch ngang)
        "product_id": Column(str, Check.str_matches(r'^[0-9a-fA-F\-]+$'), nullable=False),
        
        "product_name": Column(str, nullable=True),
        "category": Column(str, nullable=True),
        "subcategory": Column(str, nullable=True),
        "brand": Column(str, nullable=True),
        "price": Column(float, Check.ge(0), nullable=True), 
        
        # Rating từ 0 đến 5
        "rating_avg": Column(float, Check.in_range(0.0, 5.0), nullable=True),
        
        "review_count": Column(float, Check.ge(0), nullable=True),
        "stock_quantity": Column(float, Check.ge(0), nullable=True),
        
        "date_added": Column(pa.DateTime, nullable=True) # Chuỗi ngày tháng
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

            chunk_df['category'] = chunk_df['category'].str.title()
            chunk_df['subcategory'] = chunk_df['subcategory'].str.title()
            chunk_df['brand'] = chunk_df['brand'].str.title()
            chunk_df.drop(columns=['product_description'],inplace=True, errors='ignore')

            chunk_df['price'] = pd.to_numeric(chunk_df['price'],errors='coerce')
            chunk_df['rating_avg'] = pd.to_numeric(chunk_df['rating_avg']).fillna(0)
            chunk_df['review_count'] = pd.to_numeric(chunk_df['review_count'])
            chunk_df['stock_quantity'] = pd.to_numeric(chunk_df['stock_quantity'])

            #enrich data
            conditions = [
                (chunk_df['stock_quantity'] ==0),
                (chunk_df['stock_quantity']<10),
                (chunk_df['stock_quantity'] >=10)
            ]
            choices = ['Out of Stock','Low Stock','In stock']
            chunk_df['stock_status'] = np.select(conditions,choices,default='Không xác định')
            chunk_df['date_added'] = pd.to_datetime(chunk_df['date_added'])
            chunk_df['month'] = chunk_df['date_added'].dt.month
            chunk_df['year'] = chunk_df['date_added'].dt.year 
            # -----------------------------------------------------
            # 3. VALIDATION (Kiểm tra dữ liệu qua Data Contract)
            # -----------------------------------------------------
            try:
                logger.info(f"Đang tiến hành validate dữ liệu của chunk thứ {chunk_idx}")
                chunk_df = product_schema.validate(chunk_df)
            except pandera.errors.SchemaError as exc:
                logger.error(f"Dữ liệu bị sai.Lỗi tại cột {exc.schema.name}")
                logger.error(f"CHi tiết lỗi {exc}")
                raise
            
            out_key = f"{file_name}/part_{chunk_idx}.parquet"
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