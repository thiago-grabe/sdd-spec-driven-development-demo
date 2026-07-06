import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from summarizer_service.api.errors import (
    payload_too_large_handler,
    summarizer_error_handler,
    validation_error_handler,
)
from summarizer_service.api.routes import router
from summarizer_service.exceptions import PayloadTooLargeError, SummarizerError


class RequestIDMiddleware:
    def __init__(self, app: FastAPI) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http":
            request = Request(scope, receive)
            request.state.request_id = str(uuid4())
            request.state.start_time = time.monotonic()

            response_started = False
            request_id = request.state.request_id

            async def send_with_header(message) -> None:
                nonlocal response_started
                if message["type"] == "http.response.start" and not response_started:
                    response_started = True
                    headers = dict(message.get("headers", []))
                    headers[b"x-request-id"] = request_id.encode()
                    message = {**message, "headers": list(headers.items())}
                await send(message)

            await self.app(scope, receive, send_with_header)
        else:
            await self.app(scope, receive, send)


def create_app() -> FastAPI:
    application = FastAPI(title="Summarizer Service")

    application.add_exception_handler(RequestValidationError, validation_error_handler)
    application.add_exception_handler(PayloadTooLargeError, payload_too_large_handler)
    application.add_exception_handler(SummarizerError, summarizer_error_handler)

    application.include_router(router)
    application.add_middleware(RequestIDMiddleware)

    return application


app = create_app()
