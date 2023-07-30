from __future__ import annotations

import os

REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
REDDIT_USER_AGENT = "UniversitySubreddits"

SUBREDDITS = os.environ["SUBREDDITS"].split(",")

GCS_RAW_BUCKET_NAME = "university-subreddits-raw"
GCS_TRANSFORMED_BUCKET_NAME = "university-subreddits-transformed"

BIGQUERY_PROJECT_ID = "university-subreddits"
BIGQUERY_DATASET_ID = "subreddit_metrics"
BIGQUERY_TABLE_ID = "subreddit_metrics"

DATE_TO_PROCESS = os.environ.get("DATE_TO_PROCESS", None)
