from __future__ import annotations

import json
from abc import ABC
from abc import abstractmethod

from common import logger
from google.api_core.exceptions import BadRequest
from google.cloud import bigquery


class BigQueryInsertError(Exception):
    pass


class AbstractBigQueryClient(ABC):
    """
    Abstract wrapper class for the Google BigQuery Client.
    """

    @abstractmethod
    def insert_rows(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        row_dicts: list[dict],
        enforce_unique_on: list[str],
    ) -> None:
        pass


class BigQueryClient(AbstractBigQueryClient):
    """
    Wrapper class for the Google BigQuery Client.
    Provides an idempotent insert_rows method that will insert non-duplicate rows,
    and update duplicate rows.
    """

    def __init__(self):
        self.bigquery_client = bigquery.Client()

    def _update_rows(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        row_dicts: list[dict],
        key_columns: list[str],
    ) -> None:
        for row_dict in row_dicts:
            where_statements = [
                f"{col} = '{row_dict[col]}'" if type(row_dict[col]) == str else f"{col} = {row_dict[col]}"
                for col in key_columns
            ]
            where_statement = " AND ".join(where_statements)

            set_statements = [
                f"{col} = '{row_dict[col]}'" if type(row_dict[col]) == str else f"{col} = {row_dict[col]}"
                for col in row_dict
            ]
            set_statement = ", ".join(set_statements)

            query = f"""
                UPDATE `{project_id}.{dataset_id}.{table_id}`
                SET {set_statement}
                WHERE {where_statement};
            """
            job = self.bigquery_client.query(query)
            try:
                job.result()
            except BadRequest as e:
                row_identifier = tuple(row_dict[col] for col in key_columns)
                logger.warning(f"_update_rows encountered an error for row {row_identifier}: {e}")

    def _get_non_duplicate_rows(
        self,
        row_dicts: list[dict],
        duplicate_row_dicts: list[dict],
        key_columns: list[str],
    ) -> list[dict]:

        duplicate_set = {tuple(row_dict[col] for col in key_columns) for row_dict in duplicate_row_dicts}
        non_duplicate_rows_dicts = []
        for row_dict in row_dicts:
            values_to_check = tuple(row_dict[col] for col in key_columns)
            if values_to_check not in duplicate_set:
                non_duplicate_rows_dicts.append(row_dict)
        return non_duplicate_rows_dicts

    def _get_duplicate_rows(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        row_dicts: list[dict],
        key_columns: list[str],
    ) -> list[dict]:
        col_to_values: dict[str, list] = {col: [] for col in key_columns}
        for row_dict in row_dicts:
            for col in key_columns:
                col_to_values[col].append(row_dict[col])
        col_to_values_string: dict[str, str] = {
            col: ", ".join(f"'{value}'" if type(value) == str else str(value) for value in values)
            for col, values in col_to_values.items()
        }

        where_statements = [f"{col} IN ({values})" for col, values in col_to_values_string.items()]
        where_statement = " AND ".join(where_statements)
        query = f"""
            SELECT *
            FROM `{project_id}.{dataset_id}.{table_id}`
            WHERE {where_statement};
        """
        query_results_iter = self.bigquery_client.query(query).result()
        duplicate_row_dicts = [dict(row) for row in query_results_iter]
        return json.loads(json.dumps(duplicate_row_dicts, default=str))

    def _insert_rows(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        row_dicts: list[dict],
    ) -> None:
        table_ref = self.bigquery_client.dataset(dataset_id).table(table_id)
        errors = self.bigquery_client.insert_rows_json(
            table_ref,
            row_dicts,
        )
        if errors:
            raise BigQueryInsertError(errors)

    def insert_rows(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        row_dicts: list[dict],
        enforce_unique_on: list[str],
    ) -> None:
        duplicate_row_dicts = self._get_duplicate_rows(
            project_id=project_id,
            dataset_id=dataset_id,
            table_id=table_id,
            row_dicts=row_dicts,
            key_columns=enforce_unique_on,
        )
        non_duplicate_row_dicts = self._get_non_duplicate_rows(
            row_dicts=row_dicts,
            duplicate_row_dicts=duplicate_row_dicts,
            key_columns=enforce_unique_on,
        )
        if len(duplicate_row_dicts) + len(non_duplicate_row_dicts) > len(row_dicts):
            logger.warning("Pre-existing duplicate rows were found. Consider running a deduplication script.")

        if duplicate_row_dicts:
            self._update_rows(
                project_id=project_id,
                dataset_id=dataset_id,
                table_id=table_id,
                row_dicts=duplicate_row_dicts,
                key_columns=enforce_unique_on,
            )
        if non_duplicate_row_dicts:
            self._insert_rows(
                project_id=project_id,
                dataset_id=dataset_id,
                table_id=table_id,
                row_dicts=non_duplicate_row_dicts,
            )
