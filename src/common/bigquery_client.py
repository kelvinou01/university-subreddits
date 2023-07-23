from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from google.cloud import bigquery


class BigQueryInsertError(Exception):
    pass


class AbstractBigQueryClient(ABC):
    """
    Wrapper class for the Google BigQuery Client
    """

    @abstractmethod
    def insert_rows(
        self,
        dataset_id: int,
        table_id: int,
        row_dicts: list[dict],
    ) -> None:
        pass


class BigQueryClient(AbstractBigQueryClient):
    def __init__(self):
        self.bigquery_client = bigquery.Client()

    def insert_rows(
        self,
        dataset_id: int,
        table_id: int,
        row_dicts: list[dict],
    ) -> None:
        table_ref = self.bigquery_client.dataset(dataset_id).table(table_id)
        errors = self.bigquery_client.insert_rows_json(
            table_ref,
            row_dicts,
        )
        if errors:
            raise BigQueryInsertError(errors)
