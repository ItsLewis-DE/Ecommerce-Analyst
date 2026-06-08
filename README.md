# Project AWS Data Pipeline

A production-ready data pipeline to scrape job data and process it using AWS S3 and Lambda.

## Project Structure

```
├── .env                  # Environment variables (AWS endpoints, Bucket names)
├── Makefile              # Helper commands for development and deployment
├── pyproject.toml        # Python dependencies and development tools
├── infra/                # Infrastructure bash scripts (LocalStack)
│   ├── init_scripts/
│   │   ├── s3_init.sh         # Initializes S3 buckets
│   │   ├── iam_role.sh        # Configures IAM role and policies
│   │   └── deploy_lambda.sh   # Packages and deploys Lambda function
├── src/                  # Source code
│   ├── scraper/          # Scraper module
│   │   ├── config.py     # Configuration loader
│   │   ├── extract.py    # Main scraper logic
│   │   ├── cookies.json  # Scraper cookies (Not tracked in git)
│   │   └── headers.json  # Scraper headers (Not tracked in git)
│   └── lambda_functions/ # AWS Lambda handlers
│       └── process_data/
│           └── app.py    # Data cleaning lambda function
```

## Setup & Installation

1. **Install Dependencies**
   It's recommended to use a virtual environment.
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   make install
   ```

2. **Environment Variables**
   Ensure you have a `.env` file at the root:
   ```env
   NAME_BUCKET_RAW=job-raw-bucket
   NAME_BUCKET_PROCESSED=job-processed-bucket
   AWS_ENDPOINT_URL=http://localhost:4566
   KEY=latest_data.json
   ```

3. **Scraper Config**
   Add `cookies.json` and `headers.json` inside `src/scraper/` with the appropriate authentication data from your browser to bypass Cloudflare.

## Usage

You can use the `Makefile` to interact with the project:

- `make run-scraper`: Runs the scraper and uploads data to the raw S3 bucket.
- `make deploy-infra`: Initializes LocalStack S3 buckets and IAM roles.
- `make deploy-lambda`: Packages and deploys the data processing lambda.
- `make format`: Runs `ruff` to auto-format code.
- `make lint`: Runs `ruff` to check code quality.
