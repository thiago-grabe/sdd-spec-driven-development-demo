from openai import AsyncOpenAI

from summarizer_service.core.config import get_settings


def get_openai_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
