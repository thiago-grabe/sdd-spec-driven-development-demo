import time

from fastapi import APIRouter, Depends, Request
from openai import AsyncOpenAI

from summarizer_service.core.config import Settings, get_settings
from summarizer_service.core.logging import log_request
from summarizer_service.exceptions import PayloadTooLargeError
from summarizer_service.models.schemas import SummarizeRequest, SummarizeResponse
from summarizer_service.services.summarizer import summarize

router = APIRouter()


def get_openai_client(settings: Settings = Depends(get_settings)) -> AsyncOpenAI:
    """FastAPI dependency — replaced in tests with a mock (invariant I6)."""
    return AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_endpoint(
    body: SummarizeRequest,
    request: Request,
    client: AsyncOpenAI = Depends(get_openai_client),
    settings: Settings = Depends(get_settings),
) -> SummarizeResponse:
    """POST /summarize — validate → 10k guard → one model call → response."""
    request_id: str = request.state.request_id
    start: float = request.state.start_time

    if len(body.text) > settings.max_input_chars:
        exc = PayloadTooLargeError("Input too large")
        exc.input_length = len(body.text)  # type: ignore[attr-defined]
        raise exc

    max_words = body.max_words if body.max_words is not None else 150
    summary_text, model_name = await summarize(body.text, max_words, client, settings)

    word_count = len(summary_text.split())
    log_request(
        request_id=request_id,
        input_length=len(body.text),
        status_code=200,
        latency_ms=(time.monotonic() - start) * 1000,
        model=model_name,
    )
    return SummarizeResponse(
        summary=summary_text,
        word_count=word_count,
        model=model_name,
        request_id=request_id,
    )
