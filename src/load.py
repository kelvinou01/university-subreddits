from __future__ import annotations

import math
from datetime import date as Date
from datetime import datetime

from common import config
from common import logger
from common.bigquery_client import BigQueryClient
from common.bigquery_client import BigQueryInsertError
from common.middleware import LoggingMiddleware
from common.models import SubredditMetrics
from common.storage_client import GoogleCloudStorageClient
from common.utils import get_date
from common.utils import get_object_key
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response


def parse_subreddit_metrics_to_bigquery_row_dict(
    subreddit_metrics: SubredditMetrics,
) -> dict:
    row_dict = dict(subreddit_metrics)
    row_dict["date"] = str(row_dict["date"])

    for col, value in row_dict.items():
        if type(value) == float and math.isnan(value):
            row_dict[col] = None  # NaN not accepted by bigquery client
        elif type(value) == Date:
            row_dict[col] = str(value)
    return row_dict


def load_subreddit_metrics_into_bigquery(
    bigquery_client: BigQueryClient,
    subreddit_metrics_list: list[SubredditMetrics],
    project_id: int,
    dataset_id: int,
    table_id: int,
) -> None:
    subreddit_metrics_dicts = [
        parse_subreddit_metrics_to_bigquery_row_dict(
            metrics,
        )
        for metrics in subreddit_metrics_list
    ]
    bigquery_client.insert_rows(
        project_id=project_id,
        dataset_id=dataset_id,
        table_id=table_id,
        row_dicts=subreddit_metrics_dicts,
        enforce_unique_on=["subreddit", "date"],
    )


def load(date: Date) -> None:
    logger.info(f"Starting load task for {date}")

    exec_datetime = datetime.utcnow()
    logger.info(
        f"""Execution time (UTC): {exec_datetime.isoformat(sep=" ", timespec='seconds')}""",
    )

    bigquery_client = BigQueryClient()
    cloud_storage_client = GoogleCloudStorageClient()

    logger.info("Fetching metrics from google cloud storage")
    object_key = get_object_key(date)
    subreddit_metrics = cloud_storage_client.download(
        model_type=SubredditMetrics,
        bucket_name=config.GCS_TRANSFORMED_BUCKET_NAME,
        object_key=object_key,
    )

    logger.info("Loading metrics to BigQuery")
    try:
        load_subreddit_metrics_into_bigquery(
            bigquery_client=bigquery_client,
            subreddit_metrics_list=subreddit_metrics,
            project_id=config.BIGQUERY_PROJECT_ID,
            dataset_id=config.BIGQUERY_DATASET_ID,
            table_id=config.BIGQUERY_TABLE_ID,
        )
        logger.info("Load task done")
    except BigQueryInsertError as e:
        logger.critical(f"Load task encountered error(s): {e}")


app = FastAPI()


@app.middleware("http")
async def add_logging_prefix(request: Request, call_next) -> Response:
    middleware = LoggingMiddleware(call_next, "load")
    response = await middleware(request)
    return response


@app.post("/")
async def handle_event(request: Request):
    event = await request.json()
    object_name = event["message"]["attributes"]["objectId"]
    date_to_load = get_date(object_name)
    load(date=date_to_load)
    return Response(status_code=200)
