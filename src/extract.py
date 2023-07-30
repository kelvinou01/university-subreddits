from __future__ import annotations

from datetime import date as Date
from datetime import datetime
from datetime import timedelta
from typing import List

from common import config
from common import logger
from common.models import RedditPost
from common.reddit_client import AbstractRedditClient
from common.reddit_client import RedditClient
from common.storage_client import GoogleCloudStorageClient
from common.utils import estimate_downvotes
from common.utils import get_object_key
from fastapi import FastAPI
from fastapi import HTTPException


def convert_submission_to_reddit_post(submission: dict) -> RedditPost:
    """
    Converts a dictionary representing a PRAW submission object to a RedditPost object
    """

    # Reddit API doesn't send the number of downvotes, so it is estimated.
    downvotes_estimated = estimate_downvotes(
        upvotes=submission["ups"],
        upvote_ratio=submission["upvote_ratio"],
    )
    post_dt = datetime.utcfromtimestamp(submission.get("created_utc", 0.0))

    reddit_post = RedditPost(
        post_id=submission["id"],
        title=submission["title"],
        body=submission["body"],
        subreddit=submission.get("subreddit_display_name", ""),
        upvote_ratio=submission.get("upvote_ratio", 0.0),
        upvotes=submission.get("ups", 0),
        downvotes_estimated=downvotes_estimated,
        awards=submission.get("total_awards_received", 0),
        comment_count=submission.get("num_comments", 0.0),
        created_utc=submission.get("created_utc", 0.0),
        extracted_utc=submission.get("extracted_utc", 0.0),
        date=post_dt.date(),
    )
    return reddit_post


def fetch_posts_from_reddit(
    reddit_client: AbstractRedditClient,
    date: Date,
    subreddits: list[str],
) -> List[RedditPost]:
    new_submissions = []
    for subreddit in subreddits:
        submissions = reddit_client.fetch_submissions_made_on_date(
            subreddit=subreddit,
            date=date,
        )
        new_submissions.extend(submissions)

    return [convert_submission_to_reddit_post(submission) for submission in new_submissions]


def main(date: Date) -> None:
    logger.info("Starting extract task")

    exec_datetime = datetime.utcnow()
    logger.info(
        f"""Execution time (UTC): {exec_datetime.isoformat(sep=" ", timespec='seconds')}""",
    )

    logger.info("Connecting to Reddit API")
    reddit_client = RedditClient(
        reddit_client_id=config.REDDIT_CLIENT_ID,
        reddit_client_secret=config.REDDIT_CLIENT_SECRET,
        reddit_user_agent=config.REDDIT_USER_AGENT,
    )
    google_storage_client = GoogleCloudStorageClient()

    logger.info("Fetching posts made from reddit")
    new_posts = fetch_posts_from_reddit(
        reddit_client=reddit_client,
        date=date,
        subreddits=config.SUBREDDITS,
    )
    logger.info("Storing posts to google cloud storage")
    object_key = get_object_key(date)
    google_storage_client.upload(
        objects=new_posts,
        bucket_name=config.GCS_RAW_BUCKET_NAME,
        object_key=object_key,
    )

    logger.info("Extract task done")


def parse_and_check_date(input_date: str) -> Date:
    date = datetime.strptime(input_date, "%d/%m/%Y").date()

    today = datetime.now().date()
    more_than_a_month_ago = (today - date).days > 30
    if more_than_a_month_ago:
        raise ValueError(
            "Use extract_backfill.py to extract posts made more than a month ago.",
        )

    return date


app = FastAPI()


@app.get("/")
def handle_event(date: str = None):
    if date:
        try:
            date_to_extract = parse_and_check_date(date)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        date_to_extract = datetime.today() - timedelta(days=1)
        date_to_extract = date_to_extract.date()

    extract(date=date_to_extract)
