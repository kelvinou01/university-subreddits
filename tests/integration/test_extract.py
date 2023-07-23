
from common import config
from common.utils import get_object_key
from extract import fetch_posts_from_reddit
from fakes import FakeCloudStorageClient, FakeRedditClient


def test_extract(date, subreddits, date_to_reddit_posts, date_to_submissions):
    submissions = date_to_submissions[date]
    fake_reddit_client = FakeRedditClient(submissions=submissions)
    fake_google_storage_client = FakeCloudStorageClient()

    new_posts = fetch_posts_from_reddit(
        reddit_client=fake_reddit_client,
        date=date,
        subreddits=subreddits,
    )
    object_key = get_object_key(
        prefix="extract-prefix",
        date=date,
    )
    fake_google_storage_client.upload(
        objects=new_posts,
        bucket_name=config.GCS_BUCKET_NAME,
        object_key=object_key,
    )

    buckets_uploaded = len(fake_google_storage_client.buckets)
    assert buckets_uploaded == 1

    correct_posts = [post for post in date_to_reddit_posts[date] if post.subreddit in subreddits]
    stored_posts = fake_google_storage_client.buckets[config.GCS_BUCKET_NAME][object_key]

    correct_posts.sort(key=lambda post: post.post_id)
    stored_posts.sort(key=lambda post: post.post_id)
    assert correct_posts == stored_posts
