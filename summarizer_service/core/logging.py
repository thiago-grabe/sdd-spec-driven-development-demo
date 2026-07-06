import logging

logger = logging.getLogger(__name__)


def log_request(
    *,
    request_id: str,
    input_length: int,
    status_code: int,
    latency_ms: float,
    model: str | None = None,
    error_class: str | None = None,
) -> None:
    extra = {
        "request_id": request_id,
        "input_length": input_length,
        "status_code": status_code,
        "latency_ms": latency_ms,
        "model": model,
        "error_class": error_class,
    }
    if status_code < 400:
        logger.info("request completed", extra=extra)
    elif status_code < 500:
        logger.warning("client error", extra=extra)
    else:
        logger.error("server error", extra=extra)
