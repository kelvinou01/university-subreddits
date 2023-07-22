from __future__ import annotations

import math
from datetime import date as Date
from datetime import datetime
from datetime import timedelta

from common import config
from common import logger
from common.models import SubredditMetrics
from common.storage_client import GoogleCloudStorageClient
from common.utils import get_object_key
from google.cloud import bigquery


def convert_subreddit_metric_to_bigquery_row_dict(
    subreddit_metric,
) -> dict:
    row_dict = dict(subreddit_metric)
    row_dict["date"] = str(row_dict["date"])

    for col, value in row_dict.items():
        if type(value) == float and math.isnan(value):
            row_dict[col] = None  # NaN not accepted by bigquery client
        elif type(value) == Date:
            row_dict[col] = str(value)
    return row_dict


def load_subreddit_metrics_into_bigquery(
    bigquery_client,
    subreddit_metrics,
    dataset_id,
    table_id,
) -> list[dict]:
    subreddit_metrics_dicts = [
        convert_subreddit_metric_to_bigquery_row_dict(
            metrics,
        )
        for metrics in subreddit_metrics
    ]
    table_ref = bigquery_client.dataset(dataset_id).table(table_id)
    errors = bigquery_client.insert_rows_json(
        table_ref,
        subreddit_metrics_dicts,
    )
    return errors


def main(date: Date) -> None:
    logger.info(f"Starting load task for {date}")

    exec_datetime = datetime.utcnow()
    logger.info(
        f"""Execution time (UTC): {exec_datetime.isoformat(sep=" ", timespec='seconds')}""",
    )

    bigquery_client = bigquery.Client()
    cloud_storage_client = GoogleCloudStorageClient()

    logger.info("Fetching metrics from google cloud storage")
    object_key = get_object_key(config.GCS_TRANSFORM_PREFIX, date)
    subreddit_metrics = cloud_storage_client.download(
        model_type=SubredditMetrics,
        bucket_name=config.GCS_BUCKET_NAME,
        object_key=object_key,
    )

    logger.info("Loading metrics to BigQuery")
    errors = load_subreddit_metrics_into_bigquery(
        bigquery_client=bigquery_client,
        subreddit_metrics=subreddit_metrics,
        dataset_id=config.BIGQUERY_DATASET_ID,
        table_id=config.BIGQUERY_TABLE_ID,
    )
    if len(errors) > 0:
        logger.critical(f"Load task encountered error(s): {errors}")
    else:
        logger.info("Load task done")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--date",
        help="Date to load posts to (DD/MM/YY)",
    )
    args = vars(parser.parse_args())

    if args.get("date"):
        input_dt = datetime.strptime(str(args.get("date")), "%d/%m/%Y")
    else:
        input_dt = datetime.now() - timedelta(days=1)
    input_date = input_dt.date()

    main(date=input_date)
