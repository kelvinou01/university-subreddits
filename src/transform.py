from __future__ import annotations

import copy
from datetime import date as Date
from datetime import datetime
from statistics import mean
from typing import Set

import pandas as pd
from common import config
from common import logger
from common.middleware import LoggingMiddleware
from common.models import RedditPost
from common.models import SubredditMetrics
from common.nlp_client import AbstractNLPClient
from common.nlp_client import HuggingFaceNLPClient
from common.storage_client import AbstractBlobStorageClient
from common.storage_client import GoogleCloudStorageClient
from common.utils import get_date
from common.utils import get_object_key
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response


def fetch_reddit_posts_dataframe_from_cloud(
    storage_client: AbstractBlobStorageClient,
    bucket_name: str,
    object_key: str,
) -> pd.DataFrame:
    reddit_posts = storage_client.download(
        model_type=RedditPost,
        bucket_name=bucket_name,
        object_key=object_key,
    )
    return pd.DataFrame([post.__dict__ for post in reddit_posts])


def compute_sentiment_score(
    nlp_client: AbstractNLPClient,
    reddit_posts: pd.DataFrame,
) -> float:
    scores_of_each_post = nlp_client.compute_sentiment_scores(
        list(reddit_posts.title),
    )
    scores_of_each_post = [score for score in scores_of_each_post if score is not None]
    return mean(scores_of_each_post)


# TODO
def compute_common_topics(
    reddit_posts: pd.DataFrame,
) -> list[str]:
    return ["sample-topic"]


def calculate_subreddit_metrics(
    nlp_client: AbstractNLPClient,
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
        subreddit[0]: compute_sentiment_score(nlp_client, df) for subreddit, df in subreddit_to_df.items()
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
    all_subreddits: Set[str],
) -> list[SubredditMetrics]:
    subreddits_with_no_posts = copy.deepcopy(all_subreddits)
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
        subreddits_with_no_posts.remove(row.subreddit)

    for subreddit in subreddits_with_no_posts:
        metrics = SubredditMetrics(
            date=date,
            subreddit=subreddit,
            upvotes=0,
            downvotes=0,
            upvote_ratio=1,
            posts=0,
            sentiment_score=0,
            topics=[],
            transformed_utc=datetime.utcnow().timestamp(),
        )
        subreddit_metrics.append(metrics)
    return subreddit_metrics


def store_metrics_list_to_gcs(
    storage_client: AbstractBlobStorageClient,
    metrics_list: list[SubredditMetrics],
    date: Date,
) -> None:
    object_key = get_object_key(date)
    storage_client.upload(
        objects=metrics_list,
        bucket_name=config.GCS_TRANSFORMED_BUCKET_NAME,
        object_key=object_key,
    )


def transform(date: Date) -> None:
    logger.info(f"Starting transform task for {date}")

    exec_datetime = datetime.utcnow()
    logger.info(
        f"""Execution time (UTC): {exec_datetime.isoformat(sep=" ", timespec='seconds')}""",
    )

    google_storage_client = GoogleCloudStorageClient()
    huggingface_nlp_client = HuggingFaceNLPClient(
        model=config.HUGGINGFACE_MODEL,
        api_token=config.HUGGINGFACE_TOKEN,
    )
    object_key = get_object_key(date)

    logger.info("Fetching reddit posts from Google Cloud Storage")
    reddit_posts_df = fetch_reddit_posts_dataframe_from_cloud(
        storage_client=google_storage_client,
        bucket_name=config.GCS_RAW_BUCKET_NAME,
        object_key=object_key,
    )

    logger.info("Calculating subreddit metrics")
    metrics_df = calculate_subreddit_metrics(
        nlp_client=huggingface_nlp_client,
        reddit_posts_df=reddit_posts_df,
    )

    logger.info(
        "Converting metrics DataFrame to list of SubredditMetrics objects",
    )
    metrics_list = get_subreddit_metrics_list_from_metrics_df(
        metrics_df=metrics_df,
        date=date,
        all_subreddits=set(config.SUBREDDITS),
    )
    logger.info("Storing metrics to Google Cloud Storage")
    store_metrics_list_to_gcs(
        storage_client=google_storage_client,
        metrics_list=metrics_list,
        date=date,
    )

    logger.info("Transform task done")


app = FastAPI()


@app.middleware("http")
async def add_logging_prefix(request: Request, call_next) -> Response:
    middleware = LoggingMiddleware(call_next, "transform")
    response = await middleware(request)
    return response


@app.post("/")
async def handle_event(request: Request):
    event = await request.json()
    object_name = event["message"]["attributes"]["objectId"]
    date_to_transform = get_date(object_name)
    transform(date=date_to_transform)
    return Response(status_code=200)
