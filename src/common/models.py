from __future__ import annotations

from datetime import date as Date
from typing import List

from pydantic import BaseModel


class AbstractModel(BaseModel):
    date: Date


class RedditPost(AbstractModel):
    post_id: str
    title: str
    body: str
    subreddit: str
    upvote_ratio: float
    upvotes: int
    downvotes_estimated: int
    awards: int
    created_utc: float
    extracted_utc: float
    comment_count: int = 0


class SubredditMetrics(AbstractModel):
    subreddit: str
    upvotes: int
    downvotes: int
    upvote_ratio: float
    posts: int
    transformed_utc: float
    sentiment_score: float
    topics: List[str]
