from __future__ import annotations
import logging

import math
from datetime import date as Date
from datetime import datetime
from datetime import timedelta

from common import config
from common import logger
from common.bigquery_client import BigQueryClient
from common.bigquery_client import BigQueryInsertError
from common.models import SubredditMetrics
from common.storage_client import GoogleCloudStorageClient
from common.utils import get_object_key


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
        dataset_id=dataset_id,
        table_id=table_id,
        row_dicts=subreddit_metrics_dicts,
    )


def main(date: Date) -> None:
    logger.info("Starting load task")

    exec_datetime = datetime.utcnow()
    logger.info(
        f"""Execution time (UTC): {exec_datetime.isoformat(sep=" ", timespec='seconds')}""",
    )

    bigquery_client = BigQueryClient()
    cloud_storage_client = GoogleCloudStorageClient()

    logger.info("Fetching metrics from google cloud storage")
    object_key = get_object_key(config.GCS_TRANSFORM_PREFIX, date)
    subreddit_metrics = cloud_storage_client.download(
        model_type=SubredditMetrics,
        bucket_name=config.GCS_BUCKET_NAME,
        object_key=object_key,
    )

    logger.info("Loading metrics to BigQuery")
    try:
        load_subreddit_metrics_into_bigquery(
            bigquery_client=bigquery_client,
            subreddit_metrics_list=subreddit_metrics,
            dataset_id=config.BIGQUERY_DATASET_ID,
            table_id=config.BIGQUERY_TABLE_ID,
        )
        logger.info("Load task done")
    except BigQueryInsertError as e:
        logger.critical(f"Load task encountered error(s): {e}")


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
    elif config.DATE_TO_PROCESS is not None:
        input_dt = datetime.strptime(config.DATE_TO_PROCESS, "%d/%m/%Y")
    else:
        input_dt = datetime.now() - timedelta(days=1)
    input_date = input_dt.date()

    formatter = logging.Formatter(f"%(asctime)s - load({input_date}) - %(levelname)s — %(message)s")
    for handler in logger.handlers:
        handler.setFormatter(formatter)
    main(date=input_date)
