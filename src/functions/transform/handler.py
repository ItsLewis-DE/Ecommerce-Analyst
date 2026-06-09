import boto3 
import json
import urllib.parse
import awswrangler as wr

session = boto3.Session()
s3_client = session.client('s3')
BUCKET_RAW = os.getenv('BUCKET_RAW','raw-bucket')
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def lambda_handler(event,context):
    logger = logging.getLogger(__name__)
    s3_record = event['Records'][0]
    event_name = s3_record['eventName']
    logger.info(f"Đang xử lí: {event}")

    file_key = urlib.parse.unquote_plus(s3_record['s3']['object']['key'])
    file_name = Path(file_key).stem
    if file_name == 'interactions':
        try:
            df = wr.s3.read_csv(path=f's3://{BUCKET_RAW}/{file_name}.csv')
        except Exception as e:
            logger.error(f"Có lỗi xãy ra: {e}")
            raise
        df['timestamp'] =pd.to_datetime(df['timestamp'])
        df['year'] = df['timestamp'].dt.year
        df['month'] = df['timestamp'].dt.month
        df['timestamp'] = df['timestamp'].dt.strftime("%Y-%m-%d %H-%M-%S")
        df = df.dropna(axis=0,how='any',subset=['user_id','product_id','session_id'])
        df['dwell_time_ms'] = df['dwell_time_ms'].fillna(0).abs()
        df = df.drop_duplicates()

        df['interaction_type'] = df['interaction_type'].str.lower().str.strip()

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
        