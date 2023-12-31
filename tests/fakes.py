from __future__ import annotations

from collections import defaultdict
from datetime import date as Date
from datetime import datetime
from typing import Union

from common.bigquery_client import AbstractBigQueryClient
from common.models import AbstractModel
from common.nlp_client import AbstractNLPClient
from common.reddit_client import AbstractRedditClient
from common.storage_client import AbstractBlobStorageClient


class FakeBigQueryClient(AbstractBigQueryClient):
    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    def insert_rows(
        self,
        project_id: int,
        dataset_id: int,
        table_id: int,
        row_dicts: list[dict],
        enforce_unique_on: list[str],
    ) -> None:
        self.data[project_id][dataset_id][table_id] += row_dicts


class FakeNLPClient(AbstractNLPClient):
    def __init__(self, text_to_sentiment_score):
        self.text_to_sentiment_score = text_to_sentiment_score

    def compute_sentiment_scores(self, texts: list[str]) -> list[Union[float, None]]:
        return [self.text_to_sentiment_score[text] for text in texts]


class FakeRedditClient(AbstractRedditClient):
    def __init__(self, submissions):
        self.submissions = submissions

    def fetch_submissions_made_on_date(self, subreddit: str, date: Date) -> list[dict]:
        filtered_submissions = []
        for submission in self.submissions:
            created_date = datetime.utcfromtimestamp(submission["created_utc"]).date()
            if (submission["subreddit_display_name"] == subreddit) and (created_date == date):
                filtered_submissions.append(submission)
        return filtered_submissions


class FakeCloudStorageClient(AbstractBlobStorageClient):
    def __init__(self):
        self.buckets = defaultdict(dict)

    def upload(
        self,
        objects: list[AbstractModel],
        bucket_name: str,
        object_key: str,
    ) -> None:
        bucket_dict = self.buckets[bucket_name]
        bucket_dict[object_key] = objects

    def download(
        self,
        model_type: type[AbstractModel],
        bucket_name: str,
        object_key: str,
    ) -> list[AbstractModel]:
        bucket_dict = self.buckets[bucket_name]
        return bucket_dict[object_key]
