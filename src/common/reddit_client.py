
from abc import ABC, abstractmethod
from datetime import datetime
from datetime import date as Date

from praw import Reddit
from prawcore.exceptions import Forbidden

from common import logger


class AbstractRedditClient(ABC):
    """
    Wrapper class for the PRAW client to access the Reddit API.
    """

    @abstractmethod
    def fetch_posts_made_on_date(self, subreddit: str, date: Date) -> list[dict]:
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

    def _remove_posts_not_on_date(self, post_list, date):
        """Trims the post list from the front and back"""
        for start in range(len(post_list) - 1):
            created_datetime = datetime.utcfromtimestamp(post_list[start]["created_utc"])
            should_remove_post = created_datetime.date() > date
            if not should_remove_post:
                post_list = post_list[start:]
                break

        for end in range(len(post_list) - 1, -1, -1):
            created_datetime = datetime.utcfromtimestamp(post_list[end]["created_utc"])
            should_remove_post = created_datetime.date() < date
            if not should_remove_post:
                post_list = post_list[:end + 1]
                break

        return post_list

    def fetch_posts_made_on_date(self, subreddit: str, date: Date) -> list[dict]:
        posts_made_on_date = []
        last_post_id = None
        try:
            while True:
                post_generator = self.reddit_client.subreddit(subreddit).new(
                    limit=100,
                    params={"after": last_post_id}
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
                posts_made_on_date += posts

                last_post_created_datetime = datetime.utcfromtimestamp(posts[-1]["created_utc"])
                should_fetch_more = last_post_created_datetime.date() >= date
                if should_fetch_more:
                    last_post_id = f"t3_{posts[-1]['id']}"
                else:
                    break
        except Forbidden:
            logger.error(f"Couldn't fetch posts due to Forbidden error from subreddit: {subreddit}")
            return []

        posts_made_on_date = self._remove_posts_not_on_date(posts_made_on_date, date)
        return posts_made_on_date
