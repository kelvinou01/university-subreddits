
from itertools import product

from common.reddit_client import RedditClient
from extract import convert_submission_to_reddit_post, fetch_posts_from_reddit
from fakes import FakeRedditClient


def test_remove_posts_not_on_date(date_to_submissions):
    reddit_client = RedditClient(
        reddit_client_id="client_id",
        reddit_client_secret="client_secret",
        reddit_user_agent="UserAgent",
    )
    for date, submissions in date_to_submissions.items():
        filtered_submissions = reddit_client._remove_submissions_not_on_date(
            submissions=submissions,
            date=date
        )
        assert filtered_submissions == submissions


def test_convert_submission_to_reddit_post(submissions, reddit_posts):
    for submission, reddit_post in zip(submissions, reddit_posts):
        assert convert_submission_to_reddit_post(submission) == reddit_post


def test_fetch_posts_from_reddit(submissions, date_to_reddit_posts, subreddit_to_posts):
    fake_reddit_client = FakeRedditClient(submissions)

    dates = date_to_reddit_posts.keys()
    subreddits = subreddit_to_posts.keys()
    for date, subreddit in product(dates, subreddits):
        correct_reddit_posts = [
            post for post in date_to_reddit_posts[date]
            if post in subreddit_to_posts[subreddit]
        ]
        fetched_reddit_posts = fetch_posts_from_reddit(
            reddit_client=fake_reddit_client,
            date=date,
            subreddits=[subreddit],
        )

        assert set(correct_reddit_posts) == set(fetched_reddit_posts)
