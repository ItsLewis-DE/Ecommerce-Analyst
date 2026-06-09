import boto3 
import json
import urllib.parse
import awswrangler as wr
import pandera as pa
from pandera import Column,DataFrameSchema,Check
import os,logging
from pathlib import Path
import pandas as pd 

product_schema = DataFrameSchema(

    {
        # Kiểm tra ID phải đúng chuẩn format UUID (chữ, số, dấu gạch ngang)
        "product_id": Column(str, Check.str_matches(r'^[0-9a-fA-F\-]+$'), nullable=False),
        
        "product_name": Column(str, nullable=True),
        "product_description": Column(str, nullable=True),
        "category": Column(str, nullable=True),
        "subcategory": Column(str, nullable=True),
        "brand": Column(str, nullable=True),
        
        # Giá tiền (price) phải >= 0. Cột này có thể rỗng (nullable=True)
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
   
    elif file_name == 'products':
        try:
            df = wr.s3.read_csv(ppath=f's3://{BUCKET_RAW}/{file_name}.csv')
        except Exception as e:
            logger.error(f'Có lỗi xãy ra: {e}')
            raise
        df['cateogry'] = df['category'].str.title()
        df['subcategory'] = df['subcategory'].str.title()
        df['brand'] = df['brand'].str.title()
        df['product_description'] = df['product_description'].replace('\n','').strim()

        df['price'] = pd.to_numeric(df['price'],errors='coerce')
        df['rating_avg'] = pd.to_numeric(df['rating_avg']).fillna(0)
        df['review_count'] = pd.to_numeric(df['review_count'])
        df['stock_quantity'] = pd.to_numeric(df['stock_quantity'])

        #enrich data
        conditions = [
            (df['stock_quantity'] ==0),
            (df['stock_quantity']<10),
            (df['stock_quantity'] >=10)
        ]
        choices = ['Out of Stock','Low Stock','In stock']
        df['stock_status'] = np.select(conditions,choices,default='Không xác định')
        df['date_added'] = pd.to_datetime(df['date_added'])
        df['month'] = df['date_added'].dt.month
        df['year'] = df['date_added'].dt.year 