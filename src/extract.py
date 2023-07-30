from __future__ import annotations

from datetime import date as Date
from datetime import datetime
from datetime import timedelta
import logging
from typing import List

from common import config
from common import logger
from common.models import RedditPost
from common.reddit_client import AbstractRedditClient
from common.reddit_client import RedditClient
from common.storage_client import GoogleCloudStorageClient
from common.utils import estimate_downvotes
from common.utils import get_object_key


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
    object_key = get_object_key(
        config.GCS_EXTRACT_PREFIX,
        date,
    )
    google_storage_client.upload(
        objects=new_posts,
        bucket_name=config.GCS_BUCKET_NAME,
        object_key=object_key,
    )

    logger.info("Extract task done")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--date",
        help="Date to extract posts from (DD/MM/YYYY)",
    )
    args = vars(parser.parse_args())

    if args.get("date"):
        input_dt = datetime.strptime(str(args.get("date")), "%d/%m/%Y")
    elif config.DATE_TO_PROCESS is not None:
        input_dt = datetime.strptime(config.DATE_TO_PROCESS, "%d/%m/%Y")
    else:
        input_dt = datetime.now() - timedelta(days=1)
    input_date = input_dt.date()

    today = datetime.now().date()
    more_than_a_month_ago = (today - input_date).days > 30
    if more_than_a_month_ago:
        raise ValueError(
            "Use extract_historical.py to extract posts made more than a month ago.",
        )

    formatter = logging.Formatter(f"%(asctime)s - extract({input_date}) - %(levelname)s — %(message)s")
    for handler in logger.handlers:
        handler.setFormatter(formatter)
    main(date=input_date)
