import time

from fastapi import APIRouter, Depends, Request
from openai import AsyncOpenAI

from summarizer_service.api.dependencies import get_openai_client
from summarizer_service.core.config import Settings, get_settings
from summarizer_service.core.logging import log_request
from summarizer_service.exceptions import PayloadTooLargeError
from summarizer_service.models.schemas import SummarizeRequest, SummarizeResponse
from summarizer_service.services.summarizer import summarize

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
async def post_summarize(
    request: Request,
    body: SummarizeRequest,
    client: AsyncOpenAI = Depends(get_openai_client),
    settings: Settings = Depends(get_settings),
) -> SummarizeResponse:
    if len(body.text) > settings.max_input_chars:
        raise PayloadTooLargeError("Input exceeds maximum allowed length")

    request_id: str = request.state.request_id
    start_time: float = request.state.start_time

    summary, model_name = await summarize(
        text=body.text,
        max_words=body.max_words or 150,
        client=client,
        settings=settings,
    )

    word_count = len(summary.split())

    log_request(
        request_id=request_id,
        input_length=len(body.text),
        status_code=200,
        latency_ms=(time.monotonic() - start_time) * 1000,
        model=model_name,
    )

    return SummarizeResponse(
        summary=summary,
        word_count=word_count,
        model=model_name,
        request_id=request_id,
    )
