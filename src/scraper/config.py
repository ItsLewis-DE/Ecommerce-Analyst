import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# AWS Settings
AWS_ENDPOINT_URL = os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566')
BUCKET_NAME_RAW = os.getenv('NAME_BUCKET_RAW', 'job-raw-bucket')

# Scraper Settings
def load_json(filename: str) -> dict:
    file_path = BASE_DIR / filename
    if not file_path.exists():
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

COOKIES = load_json('cookies.json')
HEADERS = load_json('headers.json')
