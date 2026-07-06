from unittest.mock import AsyncMock, MagicMock

import openai
import pytest

from summarizer_service.core.config import Settings
from summarizer_service.exceptions import SummarizerError
from summarizer_service.services.summarizer import summarize


@pytest.fixture
def settings() -> Settings:
    return Settings(
        openai_api_key="sk-test",
        model="gpt-5.5",
        timeout_s=30,
        max_input_chars=10_000,
        max_retries=1,
    )


@pytest.fixture
def make_completion():
    def _make(content: str = "Summary text", model: str = "gpt-5.5") -> MagicMock:
        c = MagicMock()
        c.choices[0].message.content = content
        c.model = model
        return c

    return _make


@pytest.mark.asyncio
async def test_max_words_passed_to_model(settings: Settings, make_completion) -> None:
    """R8: max_words is embedded in the prompt sent to the model."""
    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=make_completion())
    await summarize("Some text to summarize", 75, client, settings)
    call_kwargs = client.chat.completions.create.call_args
    messages = call_kwargs.kwargs["messages"]
    all_content = " ".join(m["content"] for m in messages)
    assert "75" in all_content


@pytest.mark.asyncio
async def test_exactly_one_call(settings: Settings, make_completion) -> None:
    """R9: exactly one model call per successful request."""
    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=make_completion())
    await summarize("Some text", 150, client, settings)
    assert client.chat.completions.create.call_count == 1


@pytest.mark.asyncio
async def test_retry_on_transient_error(settings: Settings, make_completion) -> None:
    """R9 / spec §4.1: one retry allowed on a transient network error."""
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=[openai.APIConnectionError(request=MagicMock()), make_completion()]
    )
    summary, model = await summarize("Some text", 150, client, settings)
    assert summary == "Summary text"
    assert client.chat.completions.create.call_count == 2


@pytest.mark.asyncio
async def test_raises_summarizer_error_after_retry(settings: Settings) -> None:
    """R4: SummarizerError raised when all attempts fail."""
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=openai.APIConnectionError(request=MagicMock())
    )
    with pytest.raises(SummarizerError):
        await summarize("Some text", 150, client, settings)
