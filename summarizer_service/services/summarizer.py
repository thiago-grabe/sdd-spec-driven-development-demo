from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, OpenAIError

from summarizer_service.core.config import Settings
from summarizer_service.exceptions import SummarizerError


async def summarize(
    text: str,
    max_words: int,
    client: AsyncOpenAI,
    settings: Settings,
) -> tuple[str, str]:
    messages = [
        {
            "role": "system",
            "content": f"Summarize the text in at most {max_words} words.",
        },
        {"role": "user", "content": text},
    ]

    last_exc: Exception | None = None
    for attempt in range(settings.max_retries + 1):
        try:
            response = await client.chat.completions.create(
                model=settings.model,
                messages=messages,
                timeout=settings.timeout_s,
            )
            summary = response.choices[0].message.content or ""
            return summary, settings.model
        except (APIConnectionError, APITimeoutError) as exc:
            last_exc = exc
            if attempt < settings.max_retries:
                continue
            raise SummarizerError("Upstream connection error") from exc
        except OpenAIError as exc:
            raise SummarizerError("Upstream model error") from exc

    raise SummarizerError("Upstream error") from last_exc
