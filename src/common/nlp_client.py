from __future__ import annotations

import json
from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import Union

import requests
from google.api_core.exceptions import InvalidArgument
from google.cloud import language_v1


class InferenceRateLimitException(Exception):
    pass


class InferenceException(Exception):
    pass


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


class HuggingFaceNLPClient(AbstractNLPClient):
    def __init__(self, model: str, api_token: str) -> None:
        self.api_token = api_token
        self.inference_url = f"https://api-inference.huggingface.co/models/{model}"

    def _parse_huggingface_response_into_float(self, response: list[dict]) -> float:
        scores = {
            "NEU": None,
            "POS": None,
            "NEG": None,
        }

        if any(type(res) == str for res in response):
            raise InferenceException(f"HuggingFace returned an exception: {response}")

        for res in response:
            label = res["label"]
            if label in scores:
                scores[label] = res["score"]
            else:
                raise InferenceException(f"Invalid label for HuggingFace response: {res}")

        if any(score is None for score in scores.values()):
            raise InferenceException(f"Response returned from HuggingFace has a missing score: {response}")

        neu_score, pos_score, neg_score = scores.values()
        integrated_sentiment_score = (pos_score - neg_score) / (1 - neu_score)  # type: ignore
        return integrated_sentiment_score

    def _parse_huggingface_responses_into_floats(self, responses: list[list[dict]]) -> list[Optional[float]]:
        return [self._parse_huggingface_response_into_float(response) for response in responses]

    def _request_for_sentiments(self, texts: list[str]) -> list[list[dict]]:
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            url=self.inference_url,
            headers=headers,
            data=json.dumps(texts).encode("utf-8"),
        )
        if response.status_code == 429:
            raise InferenceRateLimitException()
        return response.json()

    def compute_sentiment_scores(self, texts: list[str]) -> list[Optional[float]]:
        responses = self._request_for_sentiments(texts)
        sentiment_scores = self._parse_huggingface_responses_into_floats(responses)
        return sentiment_scores
