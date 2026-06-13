import duckdb

# Tạo (hoặc mở) một file database vật lý thay vì memory
conn = duckdb.connect('powerbi_data.duckdb')

# Cài đặt extension và cấu hình LocalStack S3
conn.execute("""
    INSTALL httpfs;
    LOAD httpfs;
    SET s3_endpoint='localhost:4566';
    SET s3_access_key_id='test';
    SET s3_secret_access_key='test';
    SET s3_region='us-east-1';
    SET s3_use_ssl=false;   
    SET s3_url_style='path';
""")

# Tạo các View (Nó không tải dữ liệu về máy mà chỉ trỏ link lên S3)
print("Đang tạo các Views từ LocalStack S3...")

# 1. category_views
conn.execute("CREATE OR REPLACE TABLE category_views AS SELECT * FROM read_parquet('s3://mart-bucket/category_views.parquet');")
print("- Đã tạo view: category_views")

# 2. conversion_funnel
conn.execute("CREATE OR REPLACE TABLE conversion_funnel AS SELECT * FROM read_parquet('s3://mart-bucket/conversion_funnel.parquet');")
print("- Đã tạo view: conversion_funnel")

# 3. customer_segmentation 
conn.execute("CREATE OR REPLACE TABLE customer_segmentation AS SELECT * FROM read_parquet('s3://mart-bucket/customer_segmentation.parquet');")
print("- Đã tạo view: customer_segmentation")

# 4. poor_products_high_views
conn.execute("CREATE OR REPLACE TABLE poor_products_high_views AS SELECT * FROM read_parquet('s3://mart-bucket/poor_products_high_views.parquet');")
print("- Đã tạo view: poor_products_high_views")

# 5. device_engagement
conn.execute("CREATE OR REPLACE TABLE device_engagement AS SELECT * FROM read_parquet('s3://mart-bucket/device_engagement.parquet');")
print("- Đã tạo view: device_engagement")

print("\nHoàn tất! Cấu trúc views đã được tạo trong 'powerbi_data.duckdb'.")
conn.close()
