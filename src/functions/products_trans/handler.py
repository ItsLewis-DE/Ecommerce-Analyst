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
        
        "date_added": Column(str, nullable=True) # Chuỗi ngày tháng
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

    if file_name == 'products':
        try:
            #1. Đọc dữ liệu từ s3
            dfs_iterator = wr.s3.read_csv(path=s3_path_in,chunksize=10000)

            chunk_idx = 0
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
                chunk_df.drop(columns=['product_description'],inplace=True)

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
                wr.s3.to_parquet(
                    df=chunk_df,
                    path = s3_path_out,
                    dataset=True,
                    mode = 'overwrite'
                )
            logger.info("Đã xử lí xong toàn bộ các file!")
        except Exception as e:
            logger.error(f'Có lỗi xãy ra trong khi xử lí dữ liệu!')
            raise        