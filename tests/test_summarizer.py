from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import APIConnectionError, APITimeoutError

from summarizer_service.core.config import Settings
from summarizer_service.exceptions import SummarizerError
from summarizer_service.services.summarizer import summarize


def _make_client(return_text: str = "Summary text."):
    message = MagicMock()
    message.content = return_text
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]

    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=completion)
    return client


def _test_settings() -> Settings:
    return Settings(openai_api_key="sk-test", model="gpt-5.5")


async def test_max_words_passed_to_model() -> None:
    client = _make_client()
    settings = _test_settings()

    await summarize(
        text="Some text to summarize.", max_words=42, client=client, settings=settings
    )

    call_kwargs = client.chat.completions.create.call_args
    messages = call_kwargs.kwargs.get("messages") or call_kwargs.args[0]
    system_content = next(m["content"] for m in messages if m["role"] == "system")
    assert "42" in system_content


async def test_exactly_one_call() -> None:
    client = _make_client()
    settings = _test_settings()

    await summarize(text="Some text.", max_words=100, client=client, settings=settings)

    assert client.chat.completions.create.call_count == 1


async def test_retry_on_transient_error() -> None:
    message = MagicMock()
    message.content = "Retry success."
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]

    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=[APIConnectionError(request=MagicMock()), completion]
    )

    settings = _test_settings()
    summary, _ = await summarize(
        text="Some text.", max_words=100, client=client, settings=settings
    )

    assert client.chat.completions.create.call_count == 2
    assert summary == "Retry success."


async def test_raises_summarizer_error_after_retry() -> None:
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=[
            APITimeoutError(request=MagicMock()),
            APITimeoutError(request=MagicMock()),
        ]
    )

    settings = _test_settings()

    with pytest.raises(SummarizerError):
        await summarize(
            text="Some text.", max_words=100, client=client, settings=settings
        )

    assert client.chat.completions.create.call_count == 2
