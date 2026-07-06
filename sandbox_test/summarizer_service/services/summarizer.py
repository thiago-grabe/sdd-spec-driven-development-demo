import openai

from summarizer_service.core.config import Settings
from summarizer_service.exceptions import SummarizerError

_SYSTEM_PROMPT_TEMPLATE = (
    "You are a concise summarizer. Summarize the following text in no more than "
    "{max_words} words. Return only the summary, nothing else."
)


async def summarize(
    text: str,
    max_words: int,
    client: openai.AsyncOpenAI,
    settings: Settings,
) -> tuple[str, str]:
    """Call the model once and return (summary, model_name). Raises SummarizerError on failure."""
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(max_words=max_words)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    attempts = 0
    last_exc: Exception | None = None
    while attempts <= settings.max_retries:
        try:
            completion = await client.chat.completions.create(
                model=settings.model,
                messages=messages,
                timeout=settings.timeout_s,
            )
            summary = completion.choices[0].message.content or ""
            return summary, completion.model
        except (openai.APIConnectionError, openai.APITimeoutError) as exc:
            last_exc = exc
            attempts += 1
        except openai.OpenAIError as exc:
            raise SummarizerError("Upstream model error") from exc
    raise SummarizerError("Upstream model unavailable after retry") from last_exc
