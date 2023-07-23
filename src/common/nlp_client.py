from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Union

from google.api_core.exceptions import InvalidArgument
from google.cloud import language_v1


class AbstractNLPClient(ABC):
    @abstractmethod
    def compute_sentiment_scores(self, texts: list[str]) -> list[Union[float, None]]:
        pass


class GoogleNLPClient(AbstractNLPClient):
    def __init__(self) -> None:
        self.language_client = language_v1.LanguageServiceClient()

    def _compute_sentiment_score(self, text: str) -> Union[float, None]:
        type_ = language_v1.Document.Type.PLAIN_TEXT
        document = {"type_": type_, "content": text}
        try:
            response = self.language_client.analyze_sentiment(
                request={"document": document},
            )
        except InvalidArgument:  # Text is in a different language
            return None
        sentiment = response.document_sentiment
        return sentiment.score

    def compute_sentiment_scores(self, texts: list[str]) -> list[Union[float, None]]:
        return [self._compute_sentiment_score(text) for text in texts]
