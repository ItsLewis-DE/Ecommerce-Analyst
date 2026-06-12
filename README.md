# AWS Data Engineering Pipeline (LocalStack)

> **Mục đích của project này là để thử nghiệm các công cụ liên quan đến AWS Data Engineering, Serverless Architecture và Data Lake hoàn toàn trên môi trường Local.**

Dự án mô phỏng một hệ thống Data Pipeline cho nền tảng Thương mại điện tử (E-commerce), đi từ dữ liệu thô (CSV) đến dữ liệu chuẩn hoá (Parquet) và tạo ra các báo cáo phân tích (Data Mart).

## 🏗️ Kiến trúc Hệ thống (Architecture)
1. **Raw Storage (S3 - `raw-bucket`)**: Nơi chứa dữ liệu nguyên bản dạng CSV tải lên từ hệ thống.
2. **Data Transformation (AWS Lambda)**: Các hàm Lambda tự động được kích hoạt (S3 Event Trigger) khi có file CSV mới. Chúng đọc dữ liệu theo từng chunk, làm sạch, validate dữ liệu (sử dụng Pandera) và chuyển đổi sang định dạng Parquet.
3. **Processed Storage (S3 - `process-bucket`)**: Nơi lưu trữ dữ liệu đã qua xử lý, chia nhỏ thành nhiều phần (`part_X.parquet`) theo chuẩn Data Lake.
4. **Data Analytics & Data Mart (DuckDB + Lambda)**: Sử dụng **DuckDB** như một công cụ truy vấn (Query Engine) tốc độ cao để JOIN nhiều bảng dữ liệu trên S3, tính toán các metrics kinh doanh, và xuất kết quả ra bucket cuối cùng (`mart-bucket`).

## 📂 Cấu trúc Thư mục

- `data/`: Chứa các file dữ liệu mẫu CSV (`interactions.csv`, `products.csv`, `users.csv`,...).
- `localstack/`: Các script Bash để khởi tạo hạ tầng AWS cục bộ trên LocalStack.
  - `init_s3.sh`: Khởi tạo các buckets S3.
  - `init_lambda.sh`: Cấu hình, nén code và deploy các hàm Lambda.
  - `full_deploy.sh`: Script tổng hợp để chạy toàn bộ quá trình setup trong 1 lệnh.
- `scripts/load_to_s3.py`: Script upload file CSV từ local lên `raw-bucket` để kích hoạt chuỗi sự kiện.
- `src/functions/`: Source code của các hàm Lambda:
  - `*_trans/`: Các hàm xử lý dữ liệu đầu vào (interactions, products, users,...).
  - `function_analys/`: Hàm sử dụng DuckDB để tổng hợp dữ liệu ra các báo cáo kinh doanh.

## 🚀 Hướng dẫn chạy dự án

**Bước 1: Khởi động LocalStack**
Sử dụng Docker Compose để bật LocalStack.
```bash
docker-compose up -d
```

**Bước 2: Triển khai Hạ tầng (Deploy)**
Khởi tạo toàn bộ bucket, nén code Lambda và upload lên LocalStack:
```bash
bash localstack/full_deploy.sh
```

**Bước 3: Tải Dữ liệu lên S3 (Trigger Pipeline)**
Tải các file CSV lên `raw-bucket` để kích hoạt các hàm Lambda tự động xử lý. (Lệnh này đã được tích hợp sẵn ở cuối `full_deploy.sh` nếu bạn chạy kịch bản tự động).
```bash
python scripts/load_to_s3.py
```

**Bước 4: Xuất Báo cáo (Data Mart)**
Chạy script DuckDB để tổng hợp và tải các báo cáo (Conversion Funnel, Customer Segmentation,...) lên `mart-bucket`:
```bash
python src/functions/function_analys/handler.py
```
*Ghi chú: Lệnh phân tích này có thể được chuyển thành một Lambda và lên lịch tự động bằng EventBridge (Cron).*

## 🛠️ Công nghệ sử dụng
- **LocalStack**: Giả lập môi trường AWS (S3, Lambda, IAM, EventBridge).
- **Pandas & Pandera**: Xử lý dữ liệu và kiểm chứng Data Contract (Schema Validation).
- **DuckDB**: Động cơ In-process OLAP cực nhanh để query trực tiếp Data Lake.
- **uv**: Trình quản lý package Python cực nhanh.
