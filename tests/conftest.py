from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from summarizer_service.api.dependencies import get_openai_client
from summarizer_service.core.config import Settings, get_settings
from summarizer_service.main import create_app


def _make_completion(text: str = "A short summary.", model: str = "gpt-5.5"):
    message = MagicMock()
    message.content = text
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]
    completion.model = model
    return completion


@pytest.fixture
def test_settings() -> Settings:
    return Settings(openai_api_key="sk-test", model="gpt-5.5")


@pytest.fixture
def mock_openai_client():
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(
        return_value=_make_completion("A short summary.")
    )
    return client


@pytest.fixture
async def app_client(mock_openai_client, test_settings):
    application = create_app()
    application.dependency_overrides[get_openai_client] = lambda: mock_openai_client
    application.dependency_overrides[get_settings] = lambda: test_settings
    transport = httpx.ASGITransport(app=application)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, mock_openai_client
    application.dependency_overrides.clear()
