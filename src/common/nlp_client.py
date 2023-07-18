

from abc import ABC, abstractmethod

from google.cloud import language_v1
from google.api_core.exceptions import InvalidArgument


class AbstractNLPClient(ABC):

    @abstractmethod
    def compute_sentiment_scores(texts: list[str]) -> list[float]:
        pass


class GoogleNLPClient(AbstractNLPClient):

    def __init__(self) -> None:
        self.language_client = language_v1.LanguageServiceClient()

    def _compute_sentiment_score(self, text: str) -> float:
        type_ = language_v1.Document.Type.PLAIN_TEXT
        document = {"type_": type_, "content": text}
        try:
            response = self.language_client.analyze_sentiment(request={"document": document})
        except InvalidArgument:
            return None
        sentiment = response.document_sentiment
        return sentiment.score

    def compute_sentiment_scores(self, texts: list[str]) -> list[float]:
        return [self._compute_sentiment_score(text) for text in texts]
