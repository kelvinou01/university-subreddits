from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from common.models import AbstractModel
from common.utils import deserialize_single_json_to_objects
from common.utils import serialize_objects_to_single_json
from google.api_core.exceptions import NotFound
from google.cloud import storage


class AbstractBlobStorageClient(ABC):
    """
    Wrapper class for Cloud Blob Storage
    """

    @abstractmethod
    def upload(
        self,
        objects: list[AbstractModel],
        bucket_name: str,
        object_key: str,
    ) -> None:
        pass

    @abstractmethod
    def download(
        self,
        model_type: type[AbstractModel],
        bucket_name: str,
        object_key: str,
    ) -> list[AbstractModel]:
        pass


class GoogleCloudStorageClient(AbstractBlobStorageClient):
    def __init__(self):
        self.gcs_client = storage.Client()

    def upload(
        self,
        objects: list[AbstractModel],
        bucket_name: str,
        object_key: str,
    ) -> None:

        object_json_string = serialize_objects_to_single_json(objects)
        bucket = self.gcs_client.get_bucket(bucket_name)
        blob = bucket.blob(object_key)
        blob.upload_from_string(object_json_string)

    def download(
        self,
        model_type: type[AbstractModel],
        bucket_name: str,
        object_key: str,
    ) -> list[AbstractModel]:

        bucket = self.gcs_client.get_bucket(bucket_name)
        blob = bucket.get_blob(object_key)
        if blob is None:
            raise NotFound(f"Object {bucket_name}:{object_key} not found")
        json_string = blob.download_as_text()
        return deserialize_single_json_to_objects(json_string, model_type)
