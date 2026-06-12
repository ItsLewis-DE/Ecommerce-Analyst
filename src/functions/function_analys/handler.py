import duckdb
import os

S3_ENDPOINT=os.getenv('S3_ENDPOINT','localhost:4566')
REGION=os.getenv('REGION','us-east-1')
BUCKET_LOAD=os.getenv('BUCKET_LOAD','process-bucket')
BUCKET_TO=os.getenv('BUCKET_TO','mart-bucket')

conn = duckdb.connect(database=':memory:')
conn.execute("INSTALL httpfs;")
conn.execute("LOAD httpfs;")

conn.execute(f"""
    SET s3_endpoint='{S3_ENDPOINT}';
    SET s3_access_key_id='test';
    SET s3_secret_access_key='test';
    SET s3_region='{REGION}';
    SET s3_use_ssl=false;   
    SET s3_url_style='path';
"""
)
#SET s3_use_ssl=false: Chuyển về http vì localhost chỉ lắng nghe trên cổng http
#Set s3_url_stype='path': để hệ thống DNS k cần phân giải
def lambda_handler(event,context):

    sql_query_1 = f"""
        SELECT 
            p.category,
            COUNT(*) as total_views
        FROM read_parquet('s3://{BUCKET_LOAD}/interactions/*.parquet') AS i
        JOIN read_parquet('s3://{BUCKET_LOAD}/products/*.parquet') AS p
            ON i.product_id = p.product_id
        WHERE i.interaction_type = 'view'
        GROUP BY p.category, i.interaction_type
        ORDER BY total_views DESC
        LIMIT 10;
    """
    print("Đang truy cấn trực tiếp vào S3....")

    sql_query_2 = f"""
WITH view_events AS (
    -- Bước 1: Lấy danh sách các sản phẩm được khách hàng XEM trong mỗi session
    SELECT DISTINCT session_id, product_id
    FROM read_parquet('s3://{BUCKET_LOAD}/interactions/*.parquet')
    WHERE interaction_type = 'view'
),

cart_events AS (
    -- Bước 2: Lấy danh sách các sản phẩm được BỎ VÀO GIỎ HÀNG
    SELECT DISTINCT session_id, product_id
    FROM read_parquet('s3://{BUCKET_LOAD}/interactions/*.parquet')
    WHERE interaction_type = 'add_to_cart' 
),
remove_wishlist_events As (
    -- Bước 3: Lấy danh sách các sản phẩm bị bỏ ra khỏi giỏ
    SELECT DISTINCT session_id, product_id
    FROM read_parquet('s3://{BUCKET_LOAD}/interactions/*.parquet')
    WHERE interaction_type = 'remove_from_wishlist' 
),
add_wishlist_events AS(
    -- Bước 3: Lấy danh sách các sản phẩm bị bỏ ra khỏi giỏ
    SELECT DISTINCT session_id, product_id
    FROM read_parquet('s3://{BUCKET_LOAD}/interactions/*.parquet')
    WHERE interaction_type = 'add_to_wishlist'
),
click_events AS(
    -- Bước 3: Lấy danh sách các sản phẩm bị bỏ ra khỏi giỏ
    SELECT DISTINCT session_id, product_id
    FROM read_parquet('s3://{BUCKET_LOAD}/interactions/*.parquet')
    WHERE interaction_type = 'click'
)

SELECT 
    -- 1. Phần trăm khách hàng bỏ vào giỏ hàng sau khi xem sản phẩm
    ROUND(COUNT(c.session_id) * 100.0 / COUNT(v.session_id), 2) AS view_to_cart_percentage,
    
    -- 2. Phần trăm khách hàng bỏ sản phẩm ra khỏi mục yêu thích sau khi xem sản phẩm
    ROUND(COUNT(rw.session_id) * 100.0 / COUNT(v.session_id), 2) AS view_to_remove_wishlist_percentage,
    
    -- 3. Phần trăm khách hàng cho vào sản phẩm yêu thích sau khi xem sản phẩm
    ROUND(COUNT(aw.session_id) * 100.0 / COUNT(v.session_id), 2) AS view_to_add_wishlist_percentage,
    
    -- 4. Phần trăm khách hàng click sau khi xem sản phẩm
    ROUND(COUNT(cl.session_id) * 100.0 / COUNT(v.session_id), 2) AS view_to_click_percentage


FROM view_events v
LEFT JOIN cart_events c 
    ON v.session_id = c.session_id AND v.product_id = c.product_id
LEFT JOIN remove_wishlist_events rw
    ON v.session_id = rw.session_id AND v.product_id = rw.product_id
LEFT JOIN add_wishlist_events aw
    ON v.session_id = aw.session_id AND v.product_id = aw.product_id
LEFT JOIN click_events cl
    ON v.session_id = cl.session_id AND v.product_id = cl.product_id
    """
    sql_query_3 = f"""
        SELECT 
        u.city, 
        u.loyalty_tier, 
        SUM(p.total_amount) AS total_revenue,
        COUNT(DISTINCT u.user_id) AS unique_buyers
        FROM read_parquet('s3://{BUCKET_LOAD}/purchases/*.parquet') AS p
        JOIN read_parquet('s3://{BUCKET_LOAD}/users/*.parquet') AS u 
            ON p.user_id = u.user_id
        GROUP BY u.city, u.loyalty_tier
        ORDER BY city,loyalty_tier
        LIMIT 10;
    """

    sql_query_4 = f"""
        SELECT 
        prd.product_name,
        prd.category,
        prd.rating_avg,
        COUNT(i.interaction_id) AS total_views
        FROM read_parquet('s3://{BUCKET_LOAD}/interactions/*.parquet') AS i
        JOIN read_parquet('s3://{BUCKET_LOAD}/products/*.parquet') AS prd 
            ON i.product_id = prd.product_id
        WHERE i.interaction_type = 'view' 
        AND prd.rating_avg < 3.0   -- Rating thấp
        GROUP BY prd.product_name, prd.category, prd.rating_avg
        HAVING COUNT(i.interaction_id) > 100  -- Chỉ lấy các SP có nhiều người xem
        ORDER BY total_views DESC
        LIMIT 10;

    """
    sql_query_5 = f"""
        SELECT 
            s.device_type,
            AVG(i.dwell_time_ms) / 1000 AS avg_dwell_time_seconds,
            COUNT(i.interaction_id) AS total_interactions
        FROM read_parquet('s3://{BUCKET_LOAD}/sessions/*.parquet') AS s
        JOIN read_parquet('s3://{BUCKET_LOAD}/interactions/*.parquet') AS i 
            ON s.session_id = i.session_id
        WHERE i.dwell_time_ms IS NOT NULL
        GROUP BY s.device_type
        ORDER BY avg_dwell_time_seconds DESC;
    """
    queries = [
        ("category_views", sql_query_1),
        ("conversion_funnel", sql_query_2),
        ("customer_segmentation", sql_query_3),
        ("poor_products_high_views", sql_query_4),
        ("device_engagement", sql_query_5)
    ]

    for name, query in queries:
        s3_path = f"s3://{BUCKET_TO}/{name}.parquet"
        print(f"Đang tính toán và lưu {name} lên {s3_path}...")
        # Xóa dấu chấm phẩy ở cuối query để đưa vào trong ngoặc tròn COPY ()
        clean_query = query.strip().rstrip(';')
        conn.execute(f"COPY ({clean_query}) TO '{s3_path}' (FORMAT PARQUET);")
        
    print("Hoàn tất đẩy toàn bộ Data Mart lên S3!")

if __name__ == '__main__':
    lambda_handler({}, None)
