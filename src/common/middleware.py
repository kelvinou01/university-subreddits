import json
import logging
from typing import Callable
from fastapi import Request, Response
from datetime import date as Date, datetime

from common.utils import get_date, get_default_date_for_extract_call


class LoggingMiddleware:
    """
    For every call to extract/transform/load, prepend the date
    that is being processed to all logs.
    """
    def __init__(self, app: Callable, pipeline_stage: str):
        self.app = app
        self.pipeline_stage = pipeline_stage

    async def set_body(self, request: Request, body: bytes):
        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive

    async def get_body(self, request: Request) -> bytes:
        body = await request.body()
        await self.set_body(request, body)
        return body

    async def _get_date_to_proceess_for_extract(self, request) -> Date:
        if "date" in request.query_params:
            date_string = request.query_params["date"]
            return datetime.strptime(date_string, "%d/%m/%Y").date()
        else:
            return get_default_date_for_extract_call()

    async def _get_date_to_proceess_for_transform_or_load(self, request) -> Date:
        # Workaround for not being able to call request.body() multiple times
        # during the lifetime of a request.
        # https://github.com/tiangolo/fastapi/issues/394#issuecomment-883524819
        await self.set_body(request, await request.body())
        request_body = json.loads(await self.get_body(request))
        date_to_process = get_date(request_body["name"])
        return date_to_process

    async def _get_date_to_process(self, request: Request) -> Date:
        if request.method == "GET":
            return await self._get_date_to_proceess_for_extract(request)
        elif request.method == "POST":
            return await self._get_date_to_proceess_for_transform_or_load(request)
        else:
            raise ValueError(f"Invalid request method {request.method}")

    def _assign_format_to_all_handlers(self, format: str):
        logger = logging.getLogger()
        handlers = logger.handlers
        for handler in handlers:
            handler.setFormatter(logging.Formatter(format))

    async def __call__(self, request: Request) -> Response:
        date_to_process = await self._get_date_to_process(request)
        logging_format = f"%(asctime)s - %(levelname)s - {self.pipeline_stage}({date_to_process}) - %(message)s"
        self._assign_format_to_all_handlers(logging_format)
        response = await self.app(request)
        return response
