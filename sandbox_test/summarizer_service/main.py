import time
from uuid import uuid4

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from summarizer_service.api.errors import (
    handle_payload_too_large,
    handle_summarizer_error,
    handle_validation_error,
)
from summarizer_service.api.routes import router
from summarizer_service.exceptions import PayloadTooLargeError, SummarizerError


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assigns a UUID request_id to every request and echoes it as X-Request-ID (R5, I5)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.request_id = str(uuid4())
        request.state.start_time = time.monotonic()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response


def create_app() -> FastAPI:
    """Factory function — test isolation: each test creates its own app instance."""
    app = FastAPI(title="Summarizer Service")
    app.add_middleware(RequestIDMiddleware)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(PayloadTooLargeError, handle_payload_too_large)
    app.add_exception_handler(SummarizerError, handle_summarizer_error)
    app.include_router(router)
    return app


app = create_app()
