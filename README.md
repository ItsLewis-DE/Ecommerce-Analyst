# AWS Data Engineering & BI Pipeline (LocalStack)

> **Dự án xây dựng một hệ thống Data Pipeline end-to-end hoàn chỉnh: từ xử lý dữ liệu thô (Serverless Architecture), lưu trữ Data Lake, cho đến tự động hoá và trực quan hoá bằng Power BI thông qua DuckDB (Zero-Copy Architecture) hoàn toàn trên môi trường LocalStack.**

## 🌟 Tổng quan Dự án (Overview)
Dự án mô phỏng một hệ thống dữ liệu của nền tảng Thương mại điện tử (E-commerce). Hệ thống tự động thu thập dữ liệu giao dịch, làm sạch, biến đổi, tổng hợp thành Data Mart và cuối cùng là đẩy lên Dashboard trực quan.


## 🏗️ Kiến trúc Hệ thống (Architecture)

1. **Ingestion & Raw Storage (`raw-bucket`)**: Nơi tiếp nhận dữ liệu thô (CSV) từ hệ thống nguồn.
2. **Transformation (AWS Lambda)**: Các hàm Lambda (`*_trans`) tự động được kích hoạt (S3 Event Trigger) ngay khi có file mới. Chúng chịu trách nhiệm:
   - Validate Data Contract bằng **Pandera**.
   - Làm sạch, chuẩn hoá dữ liệu.
   - Chuyển đổi định dạng sang Parquet và lưu vào **Processed Storage (`process-bucket`)**.
3. **Analytics & Data Mart (`function_analys` Lambda)**: Một hàm Lambda độc lập sử dụng **DuckDB** làm Query Engine tốc độ cao. Hàm này join các bảng Parquet, tính toán các chỉ số kinh doanh cốt lõi (Conversion Funnel, Segmentation, Engagement...) và lưu kết quả ra **`mart-bucket`**.
4. **Automation (Amazon EventBridge)**: Hàm phân tích được tự động kích hoạt mỗi giờ (cron schedule) thông qua EventBridge để luôn đảm bảo dữ liệu Data Mart được cập nhật mới nhất.

## 📂 Cấu trúc Thư mục

- `data/`: Chứa các file dữ liệu mẫu dạng CSV (khách hàng, sản phẩm, tương tác,...).
- `localstack/`: Các script Bash tự động hoá khởi tạo hạ tầng AWS cục bộ:
  - `init_s3.sh`: Khởi tạo Data Lake (buckets).
  - `init_lambda.sh`: Cấu hình, đóng gói và deploy Lambda.
  - `init_eventbridge.sh`: Lên lịch tự động (Cron job) cho hàm phân tích.
  - `full_deploy.sh`: Script chạy toàn bộ quy trình CI/CD giả lập.
- `src/functions/`: Source code của các hàm Lambda Serverless.
- `scripts/load_to_s3.py`: Script trigger pipeline bằng cách upload data lên S3.
- `setup_pbi.py`: Script khởi tạo cơ sở dữ liệu kết nối giữa S3 và Power BI.

## 🚀 Hướng dẫn chạy dự án

### Bước 1: Khởi động LocalStack
Sử dụng Docker Compose để bật môi trường AWS cục bộ.
```bash
docker-compose up -d
```

### Bước 2: Triển khai Hạ tầng (Deploy)
Khởi tạo toàn bộ bucket, nén code Lambda, upload lên LocalStack và thiết lập EventBridge:
```bash
bash localstack/full_deploy.sh
```
*(Script này cũng sẽ tự động upload dữ liệu thô lên `raw-bucket` để kích hoạt chuỗi Lambda xử lý ban đầu).*

### Bước 3: Cấu hình kết nối Power BI
Tạo file cơ sở dữ liệu trung gian chứa các TABLE:
```bash
python setup_pbi.py
```

## 🛠️ Công nghệ sử dụng
- **AWS LocalStack**: S3, Lambda, IAM, EventBridge.
- **Python Data Stack**: Pandas, Pandera (Data Quality).
- **DuckDB**: Động cơ In-process OLAP cực nhanh cho Data Lake.
- **Power BI**: BI Dashboarding.
