
pre-commit:
	pre-commit run --all-files

test: pre-commit
	cd tests && export REDDIT_CLIENT_ID="" REDDIT_CLIENT_SECRET="" SUBREDDITS="" HUGGINGFACE_TOKEN="" GCS_RAW_BUCKET_NAME="" GCS_TRANSFORMED_BUCKET_NAME="" BIGQUERY_DATASET_ID="" BIGQUERY_TABLE_ID="" && python3 -m pytest -v

first-time-setup:
	gcloud artifacts repositories create etl-images --location=asia-southeast1 --repository-format=docker
	cd terraform && terraform init
