import logging

logger = logging.getLogger("summarizer_service")


def log_request(
    *,
    request_id: str,
    input_length: int,
    status_code: int,
    latency_ms: float,
    model: str | None = None,
    error_class: str | None = None,
) -> None:
    """Log request metadata. Never logs user-supplied text content."""
    parts = [
        f"request_id={request_id}",
        f"input_length={input_length}",
        f"status_code={status_code}",
        f"latency_ms={latency_ms:.1f}",
    ]
    if model:
        parts.append(f"model={model}")
    if error_class:
        parts.append(f"error_class={error_class}")
    msg = " ".join(parts)
    if status_code >= 500:
        logger.error(msg)
    elif status_code >= 400:
        logger.warning(msg)
    else:
        logger.info(msg)
