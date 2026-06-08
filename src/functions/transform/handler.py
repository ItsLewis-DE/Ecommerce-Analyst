import boto3 
import json
import urllib.parse
import awswrangler as wr

session = boto3.Session()
s3_client = session.client('s3')
BUCKET_RAW = os.getenv('BUCKET_RAW','raw-bucket')
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def lambda_handler(event,context):
    s3_record = event['Records'][0]
    event_name = s3_record['eventName']
    print(f"Đang xử lí: {event}")

    file_key = urlib.parse.unquote_plus(s3_record['s3']['object']['key'])
    file_name = Path(file_key).stem
    if file_name == 'interactions':
        try:
            df = wr.s3.read_csv(path=f's3://{BUCKET_RAW}/{file_name}.csv')
        except Exception as e:
            logger.info(f"There is an error: {e}")
        df['timestamp'] =pd.to_datetime(df['timestamp'])
        df['year'] = df['timestamp'].dt.year
        df['month'] = df['timestamp'].dt.month
        df['timestamp'] = df['timestamp'].dt.strftime("%Y-%m-%d %H-%M-%S")
        df = df.dropna(axis=0,how='any',subset=['user_id','product_id','session_id'])
        df['dwell_time_ms'] = df['dwell_time_ms'].fillna(0).abs()
        df = df.drop_duplicates()

        df['interaction_type'] = df['interaction_type'].str.lower().str.strip()