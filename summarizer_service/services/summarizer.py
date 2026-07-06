from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, OpenAIError

from summarizer_service.core.config import Settings
from summarizer_service.exceptions import SummarizerError

_SYSTEM_PROMPT = (
    "You are a summarization assistant. "
    "Summarize the following text in at most {max_words} words. "
    "Return only the summary, with no preamble."
)


async def summarize(
    text: str,
    max_words: int,
    client: AsyncOpenAI,
    settings: Settings,
) -> tuple[str, str]:
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT.format(max_words=max_words)},
        {"role": "user", "content": text},
    ]

    for attempt in range(settings.max_retries + 1):
        try:
            response = await client.chat.completions.create(
                model=settings.model,
                messages=messages,
                timeout=settings.timeout_s,
            )
            return response.choices[0].message.content, settings.model
        except (APIConnectionError, APITimeoutError):
            if attempt >= settings.max_retries:
                raise SummarizerError("Upstream service unavailable after retry")
        except OpenAIError as exc:
            raise SummarizerError("Upstream service error") from exc

    raise SummarizerError("Upstream service unavailable")
