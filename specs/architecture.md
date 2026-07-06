# architecture.md — Summarization Service

---

## Request flow

```
Client
  → RequestID Middleware  (assign uuid, set X-Request-ID on response)
  → POST /summarize route (Pydantic validate → 10k guard → call summarizer → build response)
      → services/summarizer.py  (one OpenAI call, 30s timeout, ≤1 retry)
      → api/errors.py           (map exceptions → 413 / 422 / 502 ErrorResponse)
      → core/logging.py         (metadata only — never logs user text)
```

**Decision flow:** Pydantic invalid → 422 · text > 10k → 413 · model error → 502 · ok → 200.

---

## Module map

| Module | Responsibility |
|--------|---------------|
| `main.py` | `create_app()`, `RequestIDMiddleware`, register exception handlers, mount router |
| `api/routes.py` | `POST /summarize` — validate → 413 guard → call → build `SummarizeResponse` |
| `api/errors.py` | Exception handlers: `PayloadTooLargeError` → 413, `SummarizerError` → 502, `RequestValidationError` → 422 |
| `services/summarizer.py` | Single OpenAI call, 30s timeout, ≤1 retry on `APIConnectionError`/`APITimeoutError` |
| `models/schemas.py` | `SummarizeRequest`, `SummarizeResponse`, `ErrorResponse` |
| `core/config.py` | `Settings` (pydantic-settings): `openai_api_key`, `model`, `timeout_s`, `max_input_chars`, `max_retries` |
| `core/logging.py` | `log_request(request_id, input_length, status_code, latency_ms, model, error_class)` — no user text |
| `exceptions.py` | `PayloadTooLargeError`, `SummarizerError` |

---

## Key constraints

- The OpenAI client is a **FastAPI dependency** (`get_openai_client`) so tests swap it for a mock via `app.dependency_overrides`.
- `request_id` lives on `request.state` — set by middleware, read by route and error handlers.
- `OPENAI_API_KEY` stored as `SecretStr` — only unwrapped at the call site.
