import time

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from summarizer_service.core.logging import log_request
from summarizer_service.exceptions import PayloadTooLargeError, SummarizerError
from summarizer_service.models.schemas import ErrorResponse


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "")
    start_time = getattr(request.state, "start_time", time.monotonic())
    log_request(
        request_id=request_id,
        input_length=0,
        status_code=422,
        latency_ms=(time.monotonic() - start_time) * 1000,
        error_class=type(exc).__name__,
    )
    body = ErrorResponse(error="Invalid request", request_id=request_id)
    return JSONResponse(status_code=422, content=body.model_dump())


async def payload_too_large_handler(
    request: Request, exc: PayloadTooLargeError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "")
    start_time = getattr(request.state, "start_time", time.monotonic())
    log_request(
        request_id=request_id,
        input_length=0,
        status_code=413,
        latency_ms=(time.monotonic() - start_time) * 1000,
        error_class=type(exc).__name__,
    )
    body = ErrorResponse(error="Payload too large", request_id=request_id)
    return JSONResponse(status_code=413, content=body.model_dump())


async def summarizer_error_handler(
    request: Request, exc: SummarizerError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "")
    start_time = getattr(request.state, "start_time", time.monotonic())
    log_request(
        request_id=request_id,
        input_length=0,
        status_code=502,
        latency_ms=(time.monotonic() - start_time) * 1000,
        error_class=type(exc).__name__,
    )
    body = ErrorResponse(error="Upstream error", request_id=request_id)
    return JSONResponse(status_code=502, content=body.model_dump())
