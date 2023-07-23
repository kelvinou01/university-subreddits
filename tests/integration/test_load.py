from __future__ import annotations

from common import config
from common.models import SubredditMetrics
from common.utils import get_object_key
from fakes import FakeBigQueryClient
from fakes import FakeCloudStorageClient
from load import load_subreddit_metrics_into_bigquery


def test_load(date, subreddit_metrics_list, subreddit_metrics_bigquery_rows):
    fake_bigquery_client = FakeBigQueryClient()
    fake_storage_client = FakeCloudStorageClient()

    object_key = get_object_key(config.GCS_TRANSFORM_PREFIX, date)
    fake_storage_client.upload(
        objects=subreddit_metrics_list,
        bucket_name=config.GCS_BUCKET_NAME,
        object_key=object_key,
    )

    subreddit_metrics = fake_storage_client.download(
        model_type=SubredditMetrics,
        bucket_name=config.GCS_BUCKET_NAME,
        object_key=object_key,
    )

    load_subreddit_metrics_into_bigquery(
        bigquery_client=fake_bigquery_client,
        subreddit_metrics_list=subreddit_metrics,
        dataset_id=config.BIGQUERY_DATASET_ID,
        table_id=config.BIGQUERY_TABLE_ID,
    )

    dataset_tables = fake_bigquery_client.dataset_to_table[config.BIGQUERY_DATASET_ID]
    num_tables = len(dataset_tables)
    assert num_tables == 1

    table_contents = dataset_tables[config.BIGQUERY_TABLE_ID]
    assert table_contents == subreddit_metrics_bigquery_rows
