from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from summarizer_service.api.routes import get_openai_client
from summarizer_service.core.config import Settings, get_settings
from summarizer_service.main import create_app


@pytest.fixture
def mock_completion() -> MagicMock:
    completion = MagicMock()
    completion.choices[0].message.content = "This is a test summary."
    completion.model = "gpt-5.5"
    return completion


@pytest.fixture
def mock_openai_client(mock_completion: MagicMock) -> MagicMock:
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=mock_completion)
    return client


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        openai_api_key="sk-test-dummy-key-for-testing",
        model="gpt-5.5",
        timeout_s=30,
        max_input_chars=10_000,
        max_retries=1,
    )


@pytest_asyncio.fixture
async def async_client(mock_openai_client: MagicMock, test_settings: Settings) -> AsyncClient:
    app = create_app()
    app.dependency_overrides[get_openai_client] = lambda: mock_openai_client
    app.dependency_overrides[get_settings] = lambda: test_settings
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, mock_openai_client
