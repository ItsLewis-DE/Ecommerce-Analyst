.PHONY: install format lint test deploy-infra deploy-lambda run-scraper

install:
	pip install -e ".[dev]"

format:
	ruff format .
	ruff check --fix .

lint:
	ruff check .

deploy-infra:
	bash infra/init_scripts/s3_init.sh
	bash infra/init_scripts/iam_role.sh

deploy-lambda:
	bash infra/init_scripts/deploy_lambda.sh

run-scraper:
	python src/scraper/extract.py
