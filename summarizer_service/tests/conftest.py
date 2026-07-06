from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from summarizer_service.core.config import Settings, get_openai_client, get_settings
from summarizer_service.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(openai_api_key="sk-test")


@pytest.fixture
def mock_openai_client():
    message = MagicMock()
    message.content = "This is a test summary."
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]

    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=completion)
    return client


@pytest.fixture
async def async_client(mock_openai_client, test_settings):
    app = create_app()
    app.dependency_overrides[get_openai_client] = lambda: mock_openai_client
    app.dependency_overrides[get_settings] = lambda: test_settings
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
