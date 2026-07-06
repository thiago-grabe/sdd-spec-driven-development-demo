# Summarization Service Architecture Document

## Introduction

This document defines the architecture for the Summarization Service described in `docs/prd.md`: a
stateless FastAPI service exposing `POST /summarize`, wrapping exactly one OpenAI call. It is the
technical source of truth for the development agents and is sharded into `docs/architecture/` for
story-by-story consumption.

## High Level Architecture

### Technical Summary
A single monolithic Python service. A request-id middleware stamps every request/response; the route
validates input (Pydantic → 422), guards the 10k cap (→ 413) before any call, invokes a single,
injectable summarizer (30s timeout, ≤1 retry), and maps upstream failure to 502. Logging is
metadata-only. No persistence.

### High Level Diagram

```text
Client → [RequestID MW] → POST /summarize (api/routes.py)
            ├─ invalid (Pydantic)        → 422  (api/errors.py)
            ├─ len(text) > 10000          → 413  (api/errors.py)
            └─ valid → services/summarizer.py → OpenAI (1 call, 30s, ≤1 retry)
                          ├─ error/timeout → 502 (api/errors.py)
                          └─ success       → 200  SummarizeResponse
```

## Tech Stack

| Category        | Technology      | Version | Purpose                          |
|-----------------|-----------------|---------|----------------------------------|
| Language        | Python          | 3.12    | Service implementation           |
| Web framework   | FastAPI         | latest  | HTTP routing, OpenAPI            |
| Validation      | Pydantic        | v2      | Typed request/response/error     |
| LLM SDK         | openai          | latest  | The one model call (runtime)     |
| ASGI server     | uvicorn         | latest  | Local + container runtime        |
| Testing         | pytest + httpx  | latest  | Unit + integration (mocked model)|
| Lint/format     | ruff            | latest  | Code quality gate                |
| Package manager | uv              | latest  | Deps + venv                      |

## Data Models

- **SummarizeRequest**: `text: str` (min length 1; 10k cap enforced as 413 in the route),
  `max_words: int | None = 150` (1–1000).
- **SummarizeResponse**: `summary`, `word_count`, `model`, `request_id`.
- **ErrorResponse**: `error`, `request_id`.

## API Specification

`POST /summarize` → `200` SummarizeResponse · `413` oversize · `422` empty/whitespace · `502`
upstream failure. Every response includes the `X-Request-ID` header. Full contract mirrors the PRD
FRs; the generated OpenAPI must match it (NFR6).

## Source Tree

```text
src/summarizer_service/
├── main.py              # create_app(): request-id middleware, error handlers, router
├── exceptions.py        # PayloadTooLargeError, SummarizerError
├── core/{config,logging}.py
├── models/schemas.py
├── services/summarizer.py
└── api/{routes,errors}.py
tests/{conftest.py, unit/, integration/}
```

## Coding Standards (sharded to docs/architecture/coding-standards.md)

- Full type hints; docstrings state intent. Small, single-responsibility functions.
- **Never log the user's text**; logging is metadata-only. Secrets from env only.
- Errors are typed and explicit; never swallow an exception and return success.
- The model client is injected via a FastAPI dependency so tests can mock it (no live calls in CI).
- `ruff check` and `ruff format` must pass before a story is Done.

## Test Strategy

Unit tests for schemas and the summarizer (mocked client); integration tests for each status-code
path via TestClient; one privacy test asserting a seeded marker never appears in logs or bodies.
