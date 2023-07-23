
import math
from datetime import date as Date
from itertools import product

from load import parse_subreddit_metrics_to_bigquery_row_dict, load_subreddit_metrics_into_bigquery
from fakes import FakeBigQueryClient


def test_parse_subreddit_metric_to_bigquery_row_dict(subreddit_metrics_list):
    for subreddit_metrics in subreddit_metrics_list:
        bq_row_dict = parse_subreddit_metrics_to_bigquery_row_dict(subreddit_metrics)
        for value in bq_row_dict.values():
            if type(value) is float:
                assert not math.isnan(value)
            assert type(value) is not Date


def test_load_subreddit_metrics_into_bigquery(
    subreddit_metrics_list,
    subreddit_metrics_bigquery_dicts,
    dataset_ids,
    table_ids
    ):
    fake_bigquery_client = FakeBigQueryClient()

    for dataset_id, table_id in product(dataset_ids, table_ids):
        load_subreddit_metrics_into_bigquery(
            bigquery_client=fake_bigquery_client,
            subreddit_metrics_list=subreddit_metrics_list,
            dataset_id=dataset_id,
            table_id=table_id,
        )
        stored_data = fake_bigquery_client.dataset_to_table[dataset_id][table_id]
        assert stored_data == subreddit_metrics_bigquery_dicts
