from __future__ import annotations

from datetime import date as Date
from datetime import datetime
from datetime import timedelta
import logging
from statistics import mean

import pandas as pd
from common import config
from common import logger
from common.models import RedditPost
from common.models import SubredditMetrics
from common.nlp_client import AbstractNLPClient
from common.nlp_client import GoogleNLPClient
from common.storage_client import AbstractGoogleCloudStorageClient
from common.storage_client import GoogleCloudStorageClient
from common.utils import get_object_key


def fetch_reddit_posts_dataframe_from_gcs(
    google_storage_client: AbstractGoogleCloudStorageClient,
    bucket_name: str,
    object_key: str,
) -> pd.DataFrame:
    reddit_posts = google_storage_client.download(
        model_type=RedditPost,
        bucket_name=bucket_name,
        object_key=object_key,
    )
    return pd.DataFrame([post.__dict__ for post in reddit_posts])


def compute_sentiment_score(
    google_nlp_client: AbstractNLPClient,
    reddit_posts: pd.DataFrame,
) -> float:
    scores_of_each_post = google_nlp_client.compute_sentiment_scores(
        reddit_posts.title,
    )
    scores_of_each_post = [score for score in scores_of_each_post if score is not None]
    return mean(scores_of_each_post)


# TODO
def compute_common_topics(
    reddit_posts: pd.DataFrame,
) -> list[str]:
    return ["sample-topic"]


def calculate_subreddit_metrics(
    google_nlp_client: AbstractNLPClient,
    reddit_posts_df: pd.DataFrame,
) -> pd.DataFrame:
    groupby_subreddit = reddit_posts_df.groupby(["subreddit"])
    grouped_df = groupby_subreddit[
        [
            "upvotes",
            "downvotes_estimated",
        ]
    ].agg("sum")
    subreddit_to_df = dict(tuple(groupby_subreddit))

    subreddit_to_sentiment_scores = {
        subreddit[0]: compute_sentiment_score(google_nlp_client, df) for subreddit, df in subreddit_to_df.items()
    }
    grouped_df["sentiment_score"] = subreddit_to_sentiment_scores

    subreddit_to_topics = {
        subreddit[0]: compute_common_topics(
            df,
        )
        for subreddit, df in subreddit_to_df.items()
    }
    grouped_df["topics"] = subreddit_to_topics

    grouped_votes = grouped_df.upvotes + grouped_df.downvotes_estimated
    grouped_df["upvote_ratio"] = grouped_df.upvotes / grouped_votes

    grouped_df["posts"] = groupby_subreddit.size()
    return grouped_df.reset_index()


def get_subreddit_metrics_list_from_metrics_df(
    metrics_df: pd.DataFrame,
    date: Date,
) -> list[SubredditMetrics]:
    subreddit_metrics = []
    for _, row in metrics_df.iterrows():
        metrics = SubredditMetrics(
            date=date,
            subreddit=row.subreddit,
            upvotes=row.upvotes,
            downvotes=row.downvotes_estimated,
            upvote_ratio=row.upvote_ratio,
            posts=row.posts,
            sentiment_score=row.sentiment_score,
            topics=row.topics,
            transformed_utc=datetime.utcnow().timestamp(),
        )
        subreddit_metrics.append(metrics)
    return subreddit_metrics


def store_metrics_list_to_gcs(
    google_storage_client: AbstractGoogleCloudStorageClient,
    metrics_list: list[SubredditMetrics],
    date: Date,
) -> None:
    object_key = get_object_key(
        config.GCS_TRANSFORM_PREFIX,
        date,
    )
    google_storage_client.upload(
        objects=metrics_list,
        bucket_name=config.GCS_BUCKET_NAME,
        object_key=object_key,
    )


def main(date: Date) -> None:
    logger.info("Starting transform task")

    exec_datetime = datetime.utcnow()
    logger.info(
        f"""Execution time (UTC): {exec_datetime.isoformat(sep=" ", timespec='seconds')}""",
    )

    google_storage_client = GoogleCloudStorageClient()
    google_nlp_client = GoogleNLPClient()
    object_key = get_object_key(config.GCS_EXTRACT_PREFIX, date)

    logger.info("Fetching reddit posts from Google Cloud Storage")
    reddit_posts_df = fetch_reddit_posts_dataframe_from_gcs(
        google_storage_client=google_storage_client,
        bucket_name=config.GCS_BUCKET_NAME,
        object_key=object_key,
    )

    logger.info("Calculating subreddit metrics")
    metrics_df = calculate_subreddit_metrics(
        google_nlp_client=google_nlp_client,
        reddit_posts_df=reddit_posts_df,
    )
    logger.info(
        "Converting metrics DataFrame to list of SubredditMetrics objects",
    )
    metrics_list = get_subreddit_metrics_list_from_metrics_df(
        metrics_df=metrics_df,
        date=date,
    )
    logger.info("Storing metrics to Google Cloud Storage")
    store_metrics_list_to_gcs(
        google_storage_client=google_storage_client,
        metrics_list=metrics_list,
        date=date,
    )

    logger.info("Transform task done")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--date",
        help="Date to transform posts from (DD/MM/YYYY)",
    )
    args = vars(parser.parse_args())

    if args.get("date"):
        input_dt = datetime.strptime(str(args.get("date")), "%d/%m/%Y")
    elif config.DATE_TO_PROCESS is not None:
        input_dt = datetime.strptime(config.DATE_TO_PROCESS, "%d/%m/%Y")
    else:
        input_dt = datetime.now() - timedelta(days=1)
    input_date = input_dt.date()

    formatter = logging.Formatter(f"%(asctime)s - transform({input_date}) - %(levelname)s — %(message)s")
    for handler in logger.handlers:
        handler.setFormatter(formatter)
    main(date=input_date)
