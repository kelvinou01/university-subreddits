from __future__ import annotations

import os

REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
REDDIT_USER_AGENT = "UniversitySubreddits"

SUBREDDITS = os.environ["SUBREDDITS"].split(",")

GCS_RAW_BUCKET_NAME = os.environ["GCS_RAW_BUCKET_NAME"]
GCS_TRANSFORMED_BUCKET_NAME = os.environ["GCS_TRANSFORMED_BUCKET_NAME"]

BIGQUERY_PROJECT_ID = "university-subreddits"
BIGQUERY_DATASET_ID = os.environ["BIGQUERY_DATASET_ID"]
BIGQUERY_TABLE_ID = os.environ["BIGQUERY_TABLE_ID"]

HUGGINGFACE_TOKEN = os.environ["HUGGINGFACE_TOKEN"]
HUGGINGFACE_MODEL = "finiteautomata/bertweet-base-sentiment-analysis"
