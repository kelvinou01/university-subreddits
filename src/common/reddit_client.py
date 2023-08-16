from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import date as Date
from datetime import datetime

from common import logger
from praw import Reddit
from prawcore.exceptions import Forbidden


class AbstractRedditClient(ABC):
    """
    Wrapper class for the PRAW client to access the Reddit API.
    """

    @abstractmethod
    def fetch_submissions_made_on_date(self, subreddit: str, date: Date) -> list[dict]:
        pass


class RedditClient(AbstractRedditClient):
    def __init__(
        self,
        reddit_client_id: str,
        reddit_client_secret: str,
        reddit_user_agent: str,
    ):
        self.reddit_client = Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent,
        )

    def _remove_submissions_not_on_date(
        self,
        submissions: list[dict],
        date: Date,
    ) -> list[dict]:
        """Removes submissions not made on date"""
        return [
            submission for submission in submissions
            if datetime.utcfromtimestamp(submission["created_utc"]).date() == date
        ]


    def fetch_submissions_made_on_date(self, subreddit: str, date: Date) -> list[dict]:
        posts_made_on_date = []
        last_post_id = None
        try:
            while True:
                post_generator = self.reddit_client.subreddit(subreddit).new(
                    limit=100,
                    params={"after": last_post_id},
                )
                posts = [
                    {
                        "id": post.id,
                        "title": post.title,
                        "body": post.selftext,
                        "subreddit_display_name": post.subreddit.display_name,
                        "upvote_ratio": post.upvote_ratio,
                        "ups": post.ups,
                        "downs": post.downs,
                        "total_awards_received": post.total_awards_received,
                        "num_comments": post.num_comments,
                        "created_utc": post.created_utc,
                        "extracted_utc": datetime.utcnow().timestamp(),
                    }
                    for post in post_generator
                ]
                if len(posts) == 0:
                    break
                posts_made_on_date += posts

                last_post = posts[-1]
                last_post_created_datetime = datetime.utcfromtimestamp(
                    last_post["created_utc"],
                )
                should_fetch_more = last_post_created_datetime.date() >= date
                if should_fetch_more:
                    last_post_id = f"t3_{last_post['id']}"
                else:
                    break
        except Forbidden:
            logger.error(
                f"Couldn't fetch posts due to Forbidden error from subreddit: {subreddit}",
            )
            return []

        posts_made_on_date = self._remove_submissions_not_on_date(
            posts_made_on_date,
            date,
        )
        print(len(posts_made_on_date))
        return posts_made_on_date
