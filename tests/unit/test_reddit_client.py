import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from prawcore.exceptions import Forbidden

from common.reddit_client import RedditClient

@pytest.fixture
def reddit_client():
    return RedditClient(
        reddit_client_id="YOUR_CLIENT_ID",
        reddit_client_secret="YOUR_CLIENT_SECRET",
        reddit_user_agent="YOUR_USER_AGENT",
    )

@pytest.fixture
def subreddit_mock(reddit_client):
    reddit_client.reddit_client.subreddit = MagicMock()
    return reddit_client.reddit_client.subreddit.return_value

@pytest.fixture
def post_data():
    date = datetime(2023, 7, 28)

    post1 = MagicMock()
    post1.id = "post1"
    post1.title = "Test Post 1"
    post1.selftext = "This is test post 1."
    post1.subreddit.display_name = "test_subreddit"
    post1.upvote_ratio = 0.75
    post1.ups = 10
    post1.downs = 2
    post1.total_awards_received = 1
    post1.num_comments = 5
    post1.created_utc = date.timestamp()

    post2 = MagicMock()
    post2.id = "post2"
    post2.title = "Test Post 2"
    post2.selftext = "This is test post 2."
    post2.subreddit.display_name = "test_subreddit"
    post2.upvote_ratio = 0.80
    post2.ups = 15
    post2.downs = 3
    post2.total_awards_received = 2
    post2.num_comments = 8
    post2.created_utc = (date + timedelta(days=1)).timestamp()
    return [post1, post2]

@pytest.fixture
def subreddit_new_mock(subreddit_mock, post_data):
    subreddit_mock.new = MagicMock(return_value=post_data)
    return subreddit_mock.new

def test_remove_submissions_not_on_date(reddit_client):
    date = datetime(2021, 10, 4).date()
    submissions = [
        {"created_utc": 1633393174},
        {"created_utc": 1633306774},
        {"created_utc": 1633220374},
    ]
    expected_submissions = [{"created_utc": 1633306774}]
    result = reddit_client._remove_submissions_not_on_date(submissions, date)
    assert result == expected_submissions

def test_fetch_submissions_made_on_date(reddit_client, subreddit_new_mock):
    date = datetime(2023, 7, 28).date()
    subreddit_new_mock.side_effect = lambda *args, **kwargs: reddit_client._remove_submissions_not_on_date(post_data, date)
    result = reddit_client.fetch_submissions_made_on_date("test_subreddit", date)
    assert len(result) == 1
    assert result[0]["id"] == "post1"
    assert result[0]["title"] == "Test Post 1"

def test_fetch_submissions_made_on_date_forbidden_error(reddit_client, subreddit_new_mock):
    subreddit_new_mock.side_effect = Forbidden
    result = reddit_client.fetch_submissions_made_on_date("test_subreddit", datetime(2023, 7, 28))
    assert result == []

def test_fetch_submissions_made_on_date_no_posts(reddit_client, subreddit_new_mock):
    subreddit_new_mock.return_value = []
    result = reddit_client.fetch_submissions_made_on_date("test_subreddit", datetime(2023, 7, 28))
    assert result == []
