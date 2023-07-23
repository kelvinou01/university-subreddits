from __future__ import annotations

from statistics import mean

from fakes import FakeCloudStorageClient
from fakes import FakeNLPClient
from pandas.testing import assert_frame_equal
from transform import compute_sentiment_score
from transform import fetch_reddit_posts_dataframe_from_gcs


def test_fetch_reddit_posts_dataframe_from_gcs(bucket_name, object_key, reddit_posts, reddit_posts_df):
    fake_storage_client = FakeCloudStorageClient()
    fake_storage_client.upload(
        objects=reddit_posts,
        bucket_name=bucket_name,
        object_key=object_key,
    )

    fetched_df = fetch_reddit_posts_dataframe_from_gcs(
        google_storage_client=fake_storage_client,
        bucket_name=bucket_name,
        object_key=object_key,
    )
    assert_frame_equal(reddit_posts_df, fetched_df)


def test_compute_sentiment_score(text_to_sentiment_score, reddit_posts_df):
    fake_nlp_client = FakeNLPClient(text_to_sentiment_score)
    computed_sentiment_score = compute_sentiment_score(
        google_nlp_client=fake_nlp_client,
        reddit_posts=reddit_posts_df,
    )
    actual_sentiment_score = mean(text_to_sentiment_score[text] for text in reddit_posts_df.title)
    assert computed_sentiment_score == actual_sentiment_score
