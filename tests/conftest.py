

from datetime import datetime
import pandas as pd
import pytest

from common.models import RedditPost, SubredditMetrics
from collections import defaultdict


def get_date(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y").date()


@pytest.fixture
def id_to_submission():
    return {
        1: {
            "id": "1",
            "title": "cute cat",
            "body": "tis a cute cat",
            "subreddit_display_name": "cats",
            "upvote_ratio": 0.70,
            "ups": 7,
            "downs": 3,
            "total_awards_received": 5,
            "num_comments": 6,
            "created_utc": 1601728690,  # 3rd Oct 2020
            "extracted_utc": 1690115890.5,
        },
        2: {
            "id": "2",
            "title": "fluffy cat",
            "body": "tis a fluffy cat",
            "subreddit_display_name": "cats",
            "upvote_ratio": 0.60,
            "ups": 6,
            "downs": 0,
            "total_awards_received": 3,
            "num_comments": 4,
            "created_utc": 1601815090,  # 4th Oct 2020
            "extracted_utc": 1690119890.5,
        },
        3: {
            "id": "3",
            "title": "cute dog",
            "body": "tis a cute dog",
            "subreddit_display_name": "dogs",
            "upvote_ratio": 0.80,
            "ups": 8,
            "downs": 0,
            "total_awards_received": 3,
            "num_comments": 6,
            "created_utc": 1601901490,  # 5th Oct 2020
            "extracted_utc": 1690125890.5,
        },
        4: {
            "id": "4",
            "title": "good boy",
            "body": "isn't he a good boy?",
            "subreddit_display_name": "dogs",
            "upvote_ratio": 0.70,
            "ups": 140,
            "downs": 60,
            "total_awards_received": 5,
            "num_comments": 3,
            "created_utc": 1601901491,  # 5th Oct 2020
            "extracted_utc": 1690125895.5,
        },
    }

@pytest.fixture
def id_to_reddit_post():
    return {
        1: RedditPost(
            post_id="1",
            title="cute cat",
            body="tis a cute cat",
            subreddit="cats",
            upvote_ratio=0.70,
            upvotes=7,
            downvotes_estimated=3,
            awards=5,
            created_utc=1601728690,
            extracted_utc=1690115890.5,
            comment_count=6,
            date=get_date("03/10/2020"),
        ),
        2: RedditPost(
            post_id="2",
            title="fluffy cat",
            body="tis a fluffy cat",
            subreddit="cats",
            upvote_ratio=0.60,
            upvotes=6,
            downvotes_estimated=4,
            awards=3,
            created_utc=1601815090,
            extracted_utc=1690119890.5,
            comment_count=4,
            date=get_date("04/10/2020"),
        ),
        3: RedditPost(
            post_id="3",
            title="cute dog",
            body="tis a cute dog",
            subreddit="dogs",
            upvote_ratio=0.80,
            upvotes=8,
            downvotes_estimated=2,
            awards=3,
            created_utc=1601901490,
            extracted_utc=1690125890.5,
            comment_count=6,
            date=get_date("05/10/2020"),
        ),
        4: RedditPost(
            post_id="4",
            title="good boy",
            body="isn't he a good boy?",
            subreddit="dogs",
            upvote_ratio=0.70,
            upvotes=140,
            downvotes_estimated=60,
            awards=5,
            created_utc=1601901491,
            extracted_utc=1690125895.5,
            comment_count=3,
            date=get_date("05/10/2020"),
        ),
    }


@pytest.fixture
def date_to_submissions(id_to_submission):
    return {
        get_date("03/10/2020"): [id_to_submission[1]],
        get_date("04/10/2020"): [id_to_submission[2]],
        get_date("05/10/2020"): [id_to_submission[3], id_to_submission[4]],
    }


@pytest.fixture(params=[get_date("03/10/2020"), get_date("04/10/2020"), get_date("05/10/2020")])
def date(request):
    return request.param


@pytest.fixture
def submissions(id_to_submission):
    subs = sorted(
        id_to_submission.values(),
        key=lambda sub: sub["created_utc"],
        reverse=True
    )
    return subs


@pytest.fixture
def date_to_reddit_posts(id_to_reddit_post):
    return {
        get_date("03/10/2020"): [id_to_reddit_post[1]],
        get_date("04/10/2020"): [id_to_reddit_post[2]],
        get_date("05/10/2020"): [id_to_reddit_post[3], id_to_reddit_post[4]],
    }


@pytest.fixture
def reddit_posts(id_to_reddit_post):
    return sorted(
        id_to_reddit_post.values(),
        key=lambda post: post.created_utc,
        reverse=True
    )


@pytest.fixture(params=[["cats", "dogs"], ["cats"]])
def subreddits(request):
    return request.param


@pytest.fixture
def subreddit_to_posts(reddit_posts):
    sub_to_posts = defaultdict(list)
    for reddit_post in reddit_posts:
        subreddit = reddit_post.subreddit
        sub_to_posts[subreddit].append(reddit_post)
    return sub_to_posts


@pytest.fixture
def subreddit_metrics_list():
    return [
        SubredditMetrics(
            date=get_date("03/10/2020"),
            subreddit="cats",
            upvotes=7,
            downvotes=5,
            upvote_ratio=0.70,
            posts=1,
            transformed_utc=1690115891.5,
            sentiment_score=0.7,
            topics=["cute", "cats"],
        ),
        SubredditMetrics(
            date=get_date("04/10/2020"),
            subreddit="cats",
            upvotes=6,
            downvotes=4,
            upvote_ratio=0.60,
            posts=1,
            transformed_utc=1690119891.5,
            sentiment_score=0.65,
            topics=["cute", "fluffy"],
        ),
        SubredditMetrics(
            date=get_date("05/10/2020"),
            subreddit="cats",
            upvotes=0,
            downvotes=0,
            upvote_ratio=float("Nan"),
            posts=0,
            transformed_utc=1690125896.4,
            sentiment_score=float("NaN"),
            topics=[],
        ),
        SubredditMetrics(
            date=get_date("03/10/2020"),
            subreddit="dogs",
            upvotes=0,
            downvotes=0,
            upvote_ratio=float("NaN"),
            posts=0,
            transformed_utc=1690115891.5,
            sentiment_score=float("NaN"),
            topics=[],
        ),
        SubredditMetrics(
            date=get_date("04/10/2020"),
            subreddit="dogs",
            upvotes=0,
            downvotes=0,
            upvote_ratio=float("NaN"),
            posts=0,
            transformed_utc=1690119891.5,
            sentiment_score=float("NaN"),
            topics=[],
        ),
        SubredditMetrics(
            date=get_date("05/10/2020"),
            subreddit="dogs",
            upvotes=148,
            downvotes=62,
            upvote_ratio=0.7047619,
            posts=2,
            transformed_utc=1690125896.5,
            sentiment_score=0.68,
            topics=["cute", "dogs", "good boy"],
        ),
    ]


@pytest.fixture
def subreddit_metrics_bigquery_dicts():
    return [
        {
            "date": "2020-10-03",
            "subreddit": "cats",
            "upvotes": 7,
            "downvotes": 5,
            "upvote_ratio": 0.70,
            "posts": 1,
            "transformed_utc": 1690115891.5,
            "sentiment_score": 0.7,
            "topics": ["cute", "cats"],
        }, {
            "date": "2020-10-04",
            "subreddit": "cats",
            "upvotes": 6,
            "downvotes": 4,
            "upvote_ratio": 0.60,
            "posts": 1,
            "transformed_utc": 1690119891.5,
            "sentiment_score": 0.65,
            "topics": ["cute", "fluffy"],
        }, {
            "date": "2020-10-05",
            "subreddit": "cats",
            "upvotes": 0,
            "downvotes": 0,
            "upvote_ratio": None,
            "posts": 0,
            "transformed_utc": 1690125896.4,
            "sentiment_score": None,
            "topics": [],
        }, {
            "date": "2020-10-03",
            "subreddit": "dogs",
            "upvotes": 0,
            "downvotes": 0,
            "upvote_ratio": None,
            "posts": 0,
            "transformed_utc": 1690115891.5,
            "sentiment_score": None,
            "topics": [],
        }, {
            "date": "2020-10-04",
            "subreddit": "dogs",
            "upvotes": 0,
            "downvotes": 0,
            "upvote_ratio": None,
            "posts": 0,
            "transformed_utc": 1690119891.5,
            "sentiment_score": None,
            "topics": [],
        }, {
            "date": "2020-10-05",
            "subreddit": "dogs",
            "upvotes": 148,
            "downvotes": 62,
            "upvote_ratio": 0.7047619,
            "posts": 2,
            "transformed_utc": 1690125896.5,
            "sentiment_score": 0.68,
            "topics": ["cute", "dogs", "good boy"],
        },
    ]


@pytest.fixture
def reddit_posts_df(reddit_posts):
    post_dicts = (post.__dict__ for post in reddit_posts)
    return pd.DataFrame.from_records(post_dicts)


@pytest.fixture
def dataset_ids():
    return ["reddit-dataset", "backup-dataset"]


@pytest.fixture
def table_ids():
    return ["reddit-posts", "subreddit-metrics"]


@pytest.fixture(params=["reddit-bucket", "backup-bucket"])
def bucket_name(request):
    return request.param


@pytest.fixture(params=["object-1", "object-2"])
def object_key(request):
    return request.param


@pytest.fixture
def text_to_sentiment_score():
    return {
        "cute cat": 0.65,
        "fluffy cat": -0.4,  # For testing purposes
        "cute dog": 0.7,
        "good boy": 0.75,
        "": None,
    }

