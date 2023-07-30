from __future__ import annotations

import os

REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
REDDIT_USER_AGENT = "UniversitySubreddits"

SUBREDDITS = os.environ["SUBREDDITS"].split(",")

GCS_BUCKET_NAME = "university-subreddits-etl"
GCS_EXTRACT_PREFIX = "reddit-posts"
GCS_TRANSFORM_PREFIX = "subreddit-metrics"

BIGQUERY_DATASET_ID = "subreddit_metrics"
BIGQUERY_TABLE_ID = "subreddit_metrics"

DATE_TO_PROCESS = os.environ.get("DATE_TO_PROCESS", None)
