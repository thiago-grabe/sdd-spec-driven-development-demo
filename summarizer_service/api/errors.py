import time

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from summarizer_service.core.logging import log_request
from summarizer_service.exceptions import PayloadTooLargeError, SummarizerError
from summarizer_service.models.schemas import ErrorResponse


async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    start_time = getattr(request.state, "start_time", time.monotonic())
    log_request(
        request_id=request_id,
        input_length=0,
        status_code=422,
        latency_ms=(time.monotonic() - start_time) * 1000,
        error_class="RequestValidationError",
    )
    body = ErrorResponse(error="Invalid request", request_id=request_id)
    return JSONResponse(status_code=422, content=body.model_dump())


async def handle_payload_too_large(
    request: Request, exc: PayloadTooLargeError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    start_time = getattr(request.state, "start_time", time.monotonic())
    log_request(
        request_id=request_id,
        input_length=0,
        status_code=413,
        latency_ms=(time.monotonic() - start_time) * 1000,
        error_class="PayloadTooLargeError",
    )
    body = ErrorResponse(
        error="Input text exceeds maximum allowed length", request_id=request_id
    )
    return JSONResponse(status_code=413, content=body.model_dump())


async def handle_summarizer_error(
    request: Request, exc: SummarizerError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    start_time = getattr(request.state, "start_time", time.monotonic())
    log_request(
        request_id=request_id,
        input_length=0,
        status_code=502,
        latency_ms=(time.monotonic() - start_time) * 1000,
        error_class="SummarizerError",
    )
    body = ErrorResponse(
        error="Upstream summarization service failed", request_id=request_id
    )
    return JSONResponse(status_code=502, content=body.model_dump())
