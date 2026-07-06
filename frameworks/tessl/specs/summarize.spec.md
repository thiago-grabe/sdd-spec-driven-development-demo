---
name: Summarization Endpoint
description: POST /summarize — returns a concise summary of a block of text from one OpenAI call
targets:
  - ../src/summarizer_service/api/routes.py
  - ../src/summarizer_service/services/summarizer.py
  - ../src/summarizer_service/models/schemas.py
---

# Summarization Endpoint

`POST /summarize` accepts a block of text and an optional target length, makes **exactly one**
OpenAI chat-completion call, and returns a concise summary as JSON. The service is stateless and
never logs the submitted text.

```python
# models/schemas.py
class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1)
    max_words: int | None = Field(default=150, ge=1, le=1_000)

class SummarizeResponse(BaseModel):
    summary: str
    word_count: int
    model: str
    request_id: str

class ErrorResponse(BaseModel):
    error: str
    request_id: str

# services/summarizer.py
def summarize(client: OpenAI, text: str, max_words: int | None) -> str: ...

# api/routes.py
def post_summarize(request: SummarizeRequest) -> SummarizeResponse: ...
```

`[@test] ../tests/integration/test_summarize_route.py`

## Happy path

- A valid request returns `200` with a body that validates against `SummarizeResponse`
  `[@test] ../tests/integration/test_summarize_route.py`
- `word_count` equals the number of whitespace-separated words in `summary`
  `[@test] ../tests/unit/test_schemas.py`
- When `max_words` is provided it is passed to the model as a soft target
  `[@test] ../tests/unit/test_summarizer.py`

## Input validation

- Empty or whitespace-only `text` returns `422` and makes **no** model call
  `[@test] ../tests/integration/test_summarize_route.py`
- `text` longer than 10,000 characters returns `413` and makes **no** model call
  `[@test] ../tests/integration/test_summarize_route.py`
- `max_words` outside the range 1–1000 returns `422`
  `[@test] ../tests/unit/test_schemas.py`

## The one model call

- A successful request triggers **exactly one** call to `client.chat.completions.create`; a single
  bounded retry on a transient network error counts as part of that one call
  `[@test] ../tests/unit/test_summarizer.py`
- The model call uses a 30-second timeout
  `[@test] ../tests/unit/test_summarizer.py`
- On model error or timeout the endpoint returns `502` with an `ErrorResponse`; the provider's raw
  error and stack trace are never exposed
  `[@test] ../tests/integration/test_summarize_route.py`

## Privacy and secrets

- The submitted `text` appears in no log record, trace, or error body
  `[@test] ../tests/integration/test_summarize_route.py`
- `OPENAI_API_KEY` is read from the environment and is never hard-coded, returned, or logged
  `[@test] ../tests/unit/test_summarizer.py`

## Request identity

- Every response, success or error, carries a `request_id` and the `X-Request-ID` header
  `[@test] ../tests/integration/test_summarize_route.py`

## Out of scope

No authentication, streaming, caching, persistence, rate limiting, or UI. One endpoint, one model,
stateless.
