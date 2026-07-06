# spec.md — Summarization API

Inherits [`constitution.md`](./constitution.md). Architecture diagrams in [`architecture.md`](./architecture.md).

---

## 1. Goal

`POST /summarize` takes a text block and an optional `max_words`, calls **one** OpenAI model, and returns a JSON summary. Clients get summarization over HTTP without embedding model logic or API keys.

---

## 2. Requirements

| #  | Behavior | Acceptance criterion | Test |
|----|----------|----------------------|------|
| R1 | Happy path | Valid body → **200** + `SummarizeResponse` | `test_happy_path_200` |
| R2 | Empty input | Empty or whitespace-only `text` → **422**, no model call | `test_empty_text_422_no_call` |
| R3 | Oversize input | `text` > 10,000 chars → **413**, no model call | `test_oversize_413_no_call` |
| R4 | Upstream failure | Model error/timeout → **502** + `ErrorResponse`, no stack trace leaked | `test_upstream_failure_502` |
| R5 | Request ID | Every response has `request_id` in body and `X-Request-ID` header | `test_request_id_on_every_response` |
| R6 | Word count | `word_count` = number of whitespace-separated words in `summary` | `test_word_count_matches_summary` |
| R7 | Privacy | Input text never appears in logs or error responses | `test_input_text_never_logged` |
| R8 | Length hint | `max_words` is passed to the model as a soft target in the system prompt | `test_max_words_passed_to_model` |
| R9 | One call | Exactly one OpenAI call per request (≤1 retry on transient network error counts as one logical call) | `test_exactly_one_call` |

---

## 3. Interface

### Request / Response models

```python
class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1)            # 10k cap → 413 in route, not max_length here
    max_words: int | None = Field(default=150, ge=1, le=1_000)

class SummarizeResponse(BaseModel):
    summary: str
    word_count: int
    model: str
    request_id: str

class ErrorResponse(BaseModel):
    error: str
    request_id: str
```

### Endpoint

`POST /summarize` — status codes: `200` success · `413` text > 10k · `422` empty/whitespace · `502` upstream error. Every response includes `X-Request-ID` header.

### Model call

```python
client.chat.completions.create(
    model="gpt-5.5",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},   # includes max_words
        {"role": "user", "content": text},
    ],
    timeout=30,
)
```

---

## 4. Constraints & Out of Scope

**Constraints:** one model call per request · ≤1 retry on transient error · 10k char hard cap · 30s timeout · key from env · stateless.

**Out of scope (v1):** auth · streaming · caching · extra endpoints · database · rate limiting · web UI.
