from __future__ import annotations

from common import config
from common.utils import get_object_key
from fakes import FakeCloudStorageClient
from fakes import FakeNLPClient
from transform import calculate_subreddit_metrics
from transform import fetch_reddit_posts_dataframe_from_cloud
from transform import get_subreddit_metrics_list_from_metrics_df
from transform import store_metrics_list_to_gcs


def test_transform(date, text_to_sentiment_score, date_to_reddit_posts):
    SUBREDDITS = ["cats", "dogs"]

    fake_storage_client = FakeCloudStorageClient()
    fake_nlp_client = FakeNLPClient(
        text_to_sentiment_score=text_to_sentiment_score,
    )
    reddit_post_obj_key = get_object_key(date)
    reddit_posts_to_upload = date_to_reddit_posts[date]
    fake_storage_client.upload(
        objects=reddit_posts_to_upload,
        bucket_name=config.GCS_RAW_BUCKET_NAME,
        object_key=reddit_post_obj_key,
    )

    reddit_posts_df = fetch_reddit_posts_dataframe_from_cloud(
        storage_client=fake_storage_client,
        bucket_name=config.GCS_RAW_BUCKET_NAME,
        object_key=reddit_post_obj_key,
    )

    metrics_df = calculate_subreddit_metrics(
        nlp_client=fake_nlp_client,
        reddit_posts_df=reddit_posts_df,
    )
    metrics_list = get_subreddit_metrics_list_from_metrics_df(
        metrics_df=metrics_df,
        date=date,
        all_subreddits=set(SUBREDDITS),
    )
    store_metrics_list_to_gcs(
        storage_client=fake_storage_client,
        metrics_list=metrics_list,
        date=date,
    )

    metrics_obj_key = get_object_key(date)
    stored_metrics = fake_storage_client.buckets[config.GCS_TRANSFORMED_BUCKET_NAME][metrics_obj_key]
    assert stored_metrics == metrics_list
