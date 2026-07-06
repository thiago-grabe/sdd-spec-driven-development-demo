import time

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from summarizer_service.core.logging import log_request
from summarizer_service.exceptions import PayloadTooLargeError, SummarizerError
from summarizer_service.models.schemas import ErrorResponse


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Map Pydantic validation errors (empty/whitespace text) to 422."""
    request_id = getattr(request.state, "request_id", "unknown")
    start = getattr(request.state, "start_time", time.monotonic())
    log_request(
        request_id=request_id,
        input_length=0,
        status_code=422,
        latency_ms=(time.monotonic() - start) * 1000,
        error_class=type(exc).__name__,
    )
    body = ErrorResponse(error="Invalid request", request_id=request_id)
    return JSONResponse(status_code=422, content=body.model_dump())


async def handle_payload_too_large(request: Request, exc: PayloadTooLargeError) -> JSONResponse:
    """Map PayloadTooLargeError to 413."""
    request_id = getattr(request.state, "request_id", "unknown")
    start = getattr(request.state, "start_time", time.monotonic())
    log_request(
        request_id=request_id,
        input_length=getattr(exc, "input_length", 0),
        status_code=413,
        latency_ms=(time.monotonic() - start) * 1000,
        error_class=type(exc).__name__,
    )
    body = ErrorResponse(error="Payload too large", request_id=request_id)
    return JSONResponse(status_code=413, content=body.model_dump())


async def handle_summarizer_error(request: Request, exc: SummarizerError) -> JSONResponse:
    """Map SummarizerError to 502. Never leaks the raw upstream error."""
    request_id = getattr(request.state, "request_id", "unknown")
    start = getattr(request.state, "start_time", time.monotonic())
    log_request(
        request_id=request_id,
        input_length=0,
        status_code=502,
        latency_ms=(time.monotonic() - start) * 1000,
        error_class=type(exc).__name__,
    )
    body = ErrorResponse(error="Upstream error", request_id=request_id)
    return JSONResponse(status_code=502, content=body.model_dump())
