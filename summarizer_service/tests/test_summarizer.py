from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from openai import APIConnectionError

from summarizer_service.core.config import Settings
from summarizer_service.exceptions import SummarizerError
from summarizer_service.services.summarizer import summarize

_FAKE_REQUEST = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


def _make_completion(content: str = "A summary.") -> MagicMock:
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]
    return completion


@pytest.fixture
def settings() -> Settings:
    return Settings(openai_api_key="sk-test")


async def test_max_words_passed_to_model(settings: Settings) -> None:
    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=_make_completion())

    await summarize("Some text to summarize.", 50, client, settings)

    call_kwargs = client.chat.completions.create.call_args.kwargs
    system_content = call_kwargs["messages"][0]["content"]
    assert "50" in system_content


async def test_exactly_one_call(settings: Settings) -> None:
    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=_make_completion())

    await summarize("Some text.", 100, client, settings)

    assert client.chat.completions.create.call_count == 1


async def test_retry_on_transient_error(settings: Settings) -> None:
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=[
            APIConnectionError(request=_FAKE_REQUEST),
            _make_completion("Retry worked."),
        ]
    )

    summary, _ = await summarize("Some text.", 100, client, settings)

    assert client.chat.completions.create.call_count == 2
    assert summary == "Retry worked."


async def test_raises_summarizer_error_after_retry(settings: Settings) -> None:
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=[
            APIConnectionError(request=_FAKE_REQUEST),
            APIConnectionError(request=_FAKE_REQUEST),
        ]
    )

    with pytest.raises(SummarizerError):
        await summarize("Some text.", 100, client, settings)

    assert client.chat.completions.create.call_count == 2
