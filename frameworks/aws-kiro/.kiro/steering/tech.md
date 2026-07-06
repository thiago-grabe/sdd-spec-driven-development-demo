---
inclusion: always
---

# Technology

## Stack
- **Language:** Python 3.12 — modern syntax (`X | None`, built-in generics, `match` where it clarifies).
- **Web framework:** FastAPI.
- **Validation / models:** Pydantic v2. No bare `dict` crosses an API boundary — every request and
  response body is a typed model.
- **LLM provider (runtime):** the official OpenAI Python SDK (`openai`). The app calls an OpenAI model
  (`gpt-5.5`). This is independent of Kiro, which is the coding agent that writes the code.
- **ASGI server:** `uvicorn` for local runs.
- **Package & env manager:** `uv`.

## Constraints (technical)
- **Exactly one model call per request**, with at most one bounded retry on a transient network error.
- **30-second timeout** on the model call.
- **10,000-character hard input cap**, enforced *before* any model call.
- **Secrets from the environment only** — `OPENAI_API_KEY` is read from an env var, never hard-coded,
  returned, or logged.
- **Stateless** — no session, no persisted request/response data.

## Testing
- The model client is **always mocked** in tests — the suite never makes a live network call.
- Every acceptance criterion has at least one test.
- A dedicated privacy test seeds a marker into the input and asserts it appears in **no** log record
  and **no** error body.

## Definition of done
Type hints everywhere · `ruff check` and `ruff format` clean · every acceptance criterion covered by
a passing test · OpenAPI schema matches the contract · no secret or user text reachable in logs or
responses · spec and code agree (no drift).
