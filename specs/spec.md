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

---

## 5. Plan

### 5.1 File layout

```
summarizer_service/
├── main.py                   # create_app(), RequestIDMiddleware, register exception handlers, mount router
├── exceptions.py             # PayloadTooLargeError, SummarizerError
├── api/
│   ├── __init__.py
│   ├── routes.py             # POST /summarize — validate → 413/422 guard → call → build SummarizeResponse
│   └── errors.py             # Exception handlers: PayloadTooLargeError→413, SummarizerError→502, RequestValidationError→422
├── services/
│   ├── __init__.py
│   └── summarizer.py         # Single OpenAI call, 30s timeout, ≤1 retry on transient errors
├── models/
│   ├── __init__.py
│   └── schemas.py            # SummarizeRequest, SummarizeResponse, ErrorResponse
├── core/
│   ├── __init__.py
│   ├── config.py             # Settings (pydantic-settings): openai_api_key, model, timeout_s, max_input_chars, max_retries
│   └── logging.py            # log_request() — metadata only, never user text
└── tests/
    ├── __init__.py
    ├── conftest.py           # app fixture, mock client swap via app.dependency_overrides
    └── test_api.py           # all R1–R9 test functions
```

### 5.2 Dependency injection

`get_openai_client` lives in `main.py`. It is declared as a FastAPI dependency and returns an `AsyncOpenAI` instance built from `Settings.openai_api_key.get_secret_value()`.

In tests, `conftest.py` overrides it at fixture setup time (pseudocode):

```
# conftest.py
@fixture
def app():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=<fake_completion>)
    app.dependency_overrides[get_openai_client] = lambda: mock_client
    yield app
    app.dependency_overrides.clear()
```

No live network call is ever made because the real `get_openai_client` is never invoked inside tests.

### 5.3 Request-ID middleware (R5)

`RequestIDMiddleware` is defined in `main.py` and registered before the router. On each incoming request it:

1. Generates a `uuid4()` string.
2. Writes it to `request.state.request_id`.
3. Calls the next handler.
4. Adds `X-Request-ID: <uuid>` to the outgoing response.

The route handler (`api/routes.py`) reads `request.state.request_id` and places it in `SummarizeResponse.request_id`. Error handlers (`api/errors.py`) do the same for `ErrorResponse.request_id`, so every response — success or error — carries the same ID in both body and header (R5).

### 5.4 Error handling

Handlers are registered in `main.py` inside `create_app()`.

| Exception class | Raised by | HTTP status | Response model |
|-----------------|-----------|-------------|----------------|
| `RequestValidationError` | Pydantic / route whitespace guard | 422 | `ErrorResponse` |
| `PayloadTooLargeError` | route (`len(text) > max_input_chars`) | 413 | `ErrorResponse` |
| `SummarizerError` | `services/summarizer.py` | 502 | `ErrorResponse` |

All three handlers populate `ErrorResponse.request_id` from `request.state.request_id`. No stack trace or upstream error message is forwarded to the client (R4).

**Implementation note:** `SummarizeRequest.text` carries `min_length=1`, which catches truly empty strings. Whitespace-only strings (e.g. `"   "`) pass Pydantic and must be rejected by an explicit strip-and-check in the route, returning 422. This is consistent with the comment in `§3` ("10k cap → 413 in route, not max_length here") — the route owns both guards.

### 5.5 Summarizer service (R8, R9)

Function signature (pseudocode):

```
async summarize(text: str, max_words: int, client: AsyncOpenAI) -> str
```

Execution path:

1. Builds `SYSTEM_PROMPT` containing `"…in at most {max_words} words…"` (R8).
2. Calls `client.chat.completions.create(model=settings.model, messages=[system, user], timeout=30)` (30 s timeout).
3. On `APIConnectionError` or `APITimeoutError`: retries once. A second failure raises `SummarizerError` (≤1 retry satisfies the "one logical call" in R9).
4. On any other `OpenAIError`: raises `SummarizerError` immediately with no retry.
5. Returns `response.choices[0].message.content`.

The route builds `SummarizeResponse`: `word_count = len(summary.split())` (R6), `model` from settings, `request_id` from `request.state`.

### 5.6 Settings

Defined in `core/config.py` via `pydantic-settings` (`BaseSettings`). Env var names are the uppercase equivalents of field names.

| Field | Type | Default | Env var |
|-------|------|---------|---------|
| `openai_api_key` | `SecretStr` | *(required)* | `OPENAI_API_KEY` |
| `model` | `str` | `"gpt-5.5"` | `MODEL` |
| `timeout_s` | `int` | `30` | `TIMEOUT_S` |
| `max_input_chars` | `int` | `10_000` | `MAX_INPUT_CHARS` |
| `max_retries` | `int` | `1` | `MAX_RETRIES` |

`openai_api_key` uses `SecretStr` so it is never serialised or printed. The raw value is unwrapped only at the `get_openai_client` call site via `.get_secret_value()`.

### 5.7 Logging (R7)

`core/logging.py` exposes `log_request(...)`. It records exactly these fields:

| Field | Type | Notes |
|-------|------|-------|
| `request_id` | `str` | UUID set by middleware |
| `input_length` | `int` | `len(text)` — character count, never the text itself |
| `status_code` | `int` | Final HTTP status |
| `latency_ms` | `float` | Wall-clock duration for the full route |
| `model` | `str` | Model identifier from settings |
| `error_class` | `str \| None` | Exception class name on failure, else `None` |

User text never appears in any log record (R7). The privacy test (`test_input_text_never_logged`) seeds a unique sentinel string in `text`, captures all log output via `caplog`, and asserts the sentinel is absent from every log record and from the response body.

### 5.8 Test coverage

All tests live in `tests/test_api.py` and share the `app` fixture from `conftest.py`.

| Req | Test function | File | Mock used |
|-----|---------------|------|-----------|
| R1 | `test_happy_path_200` | `test_api.py` | `AsyncMock` returning a valid completion object |
| R2 | `test_empty_text_422_no_call` | `test_api.py` | `AsyncMock` — asserts `.create` never called |
| R3 | `test_oversize_413_no_call` | `test_api.py` | `AsyncMock` — asserts `.create` never called |
| R4 | `test_upstream_failure_502` | `test_api.py` | `AsyncMock` raising `OpenAIError` |
| R5 | `test_request_id_on_every_response` | `test_api.py` | `AsyncMock` — checks body and `X-Request-ID` header for each status code |
| R6 | `test_word_count_matches_summary` | `test_api.py` | `AsyncMock` returning a known fixed summary string |
| R7 | `test_input_text_never_logged` | `test_api.py` | `AsyncMock` + `caplog` (pytest log capture) |
| R8 | `test_max_words_passed_to_model` | `test_api.py` | `AsyncMock` — asserts system prompt contains the `max_words` value |
| R9 | `test_exactly_one_call` | `test_api.py` | `AsyncMock` — asserts `.create` called exactly once |

---

## 6. Tasks

### T1: Scaffold project layout

| Field | Value |
|-------|-------|
| Files | `pyproject.toml`, `.env.example`, `summarizer_service/__init__.py`, `summarizer_service/api/__init__.py`, `summarizer_service/services/__init__.py`, `summarizer_service/models/__init__.py`, `summarizer_service/core/__init__.py`, `summarizer_service/tests/__init__.py` |
| Satisfies | scaffold |
| Done when | `uv sync` exits 0; all `__init__.py` files exist; `ruff check` passes on the empty package |
| Test | n/a |

Create `pyproject.toml` declaring Python ≥ 3.12 and runtime dependencies (`fastapi`, `uvicorn[standard]`, `openai`, `pydantic-settings`) plus dev dependencies (`pytest`, `pytest-asyncio`, `httpx`, `ruff`). Add `.env.example` with a single `OPENAI_API_KEY=sk-...` placeholder. Create every `__init__.py` listed in §5.1 to establish the package hierarchy.

---

### T2: Define Pydantic models

| Field | Value |
|-------|-------|
| Files | `summarizer_service/models/schemas.py` |
| Satisfies | R1, R6 (structural basis) |
| Done when | all three model classes import cleanly; `ruff check` passes |
| Test | n/a (exercised by T10b and T10d) |

Implement `SummarizeRequest` (`text: str`, `min_length=1`; `max_words: int | None`, default 150, bounds 1–1000), `SummarizeResponse` (`summary`, `word_count`, `model`, `request_id`), and `ErrorResponse` (`error`, `request_id`) using Pydantic v2. No custom validators beyond field constraints — whitespace-only `text` is caught in the route (§5.4 implementation note).

---

### T3: Define custom exceptions

| Field | Value |
|-------|-------|
| Files | `summarizer_service/exceptions.py` |
| Satisfies | scaffold (consumed by T6, T7, T8) |
| Done when | both classes importable; no imports from any project module; `ruff check` passes |
| Test | n/a |

Create `PayloadTooLargeError(Exception)` and `SummarizerError(Exception)` as plain subclasses with no extra attributes or methods. All HTTP status-code mapping happens in the handlers registered in T7 — these classes are only raised and caught, never inspected for content.

---

### T4: Implement Settings and OpenAI dependency

| Field | Value |
|-------|-------|
| Files | `summarizer_service/core/config.py` |
| Satisfies | scaffold (consumed by T6, T8, T9, T10a) |
| Done when | `Settings()` resolves all fields from env; `openai_api_key` is `SecretStr`; `get_openai_client()` returns an `AsyncOpenAI` instance; `ruff check` passes |
| Test | n/a |

Define `Settings(BaseSettings)` with the five fields from §5.6. Also define `get_openai_client() -> AsyncOpenAI` in this file — **not in `main.py`** as §5.2 stated. Placing it here avoids a circular import: `main.py` imports `api/routes.py` to mount the router, and `api/routes.py` must import `get_openai_client` for `Depends()`; if that function lived in `main.py` the import would be circular. Unwrap `SecretStr` via `.get_secret_value()` only at the call site inside `get_openai_client`.

---

### T5: Implement metadata-only logger

| Field | Value |
|-------|-------|
| Files | `summarizer_service/core/logging.py` |
| Satisfies | R7 (privacy guarantee; integration test in T10d) |
| Done when | `log_request(...)` emits a log record with all six metadata fields; `text` is not a parameter; `ruff check` passes |
| Test | `test_input_text_never_logged` (written in T10d) |

Implement `log_request(request_id, input_length, status_code, latency_ms, model, error_class=None)` using Python's standard `logging` module. Log at INFO when `status_code < 400`, WARNING otherwise. The parameter list must not include `text` or any user content — only `input_length` (integer character count) represents the input. This is the only function in this module.

---

### T6: Implement summarizer service

| Field | Value |
|-------|-------|
| Files | `summarizer_service/services/summarizer.py` |
| Satisfies | R8, R9 |
| Done when | `test_max_words_passed_to_model` and `test_exactly_one_call` pass |
| Test | `test_max_words_passed_to_model`, `test_exactly_one_call` |

Implement `async summarize(text: str, max_words: int, client: AsyncOpenAI) -> str`. Build `SYSTEM_PROMPT` embedding `max_words` as a soft target (R8). Call `client.chat.completions.create` with `timeout=30`. On `APIConnectionError` or `APITimeoutError` retry once; a second failure raises `SummarizerError`. Any other `OpenAIError` raises `SummarizerError` immediately with no retry (R9 — ≤1 retry counts as one logical call). Return `choices[0].message.content`.

---

### T7: Implement exception handlers

| Field | Value |
|-------|-------|
| Files | `summarizer_service/api/errors.py` |
| Satisfies | R2, R3, R4 (handler logic; integration tests in T10d) |
| Done when | each handler returns the correct HTTP status and an `ErrorResponse` body with `request_id` populated; `ruff check` passes |
| Test | `test_empty_text_422_no_call`, `test_oversize_413_no_call`, `test_upstream_failure_502` (written in T10d) |

Define three async handler functions: `handle_validation_error` → 422, `handle_payload_too_large` → 413, `handle_summarizer_error` → 502. Each reads `request.state.request_id` for the response body. The `error` field must contain a static human-readable message — no upstream detail, no stack trace (R4). Handlers are imported and registered in T9.

---

### T8: Implement POST /summarize route

| Field | Value |
|-------|-------|
| Files | `summarizer_service/api/routes.py` |
| Satisfies | R1, R2, R3, R5, R6 |
| Done when | route returns 200 `SummarizeResponse` on valid input; raises `PayloadTooLargeError` when `len(text) > max_input_chars`; raises 422 on whitespace-only `text`; `word_count == len(summary.split())`; `request_id` matches the middleware-assigned value |
| Test | `test_happy_path_200`, `test_word_count_matches_summary`, `test_request_id_on_every_response` |

Create `router = APIRouter()`. Inject `client: AsyncOpenAI = Depends(get_openai_client)` imported from `core/config.py`. Guards in order: if `len(text) > settings.max_input_chars` raise `PayloadTooLargeError`; if `text.strip() == ""` raise `HTTPException(status_code=422)`. Call `await summarize(text, max_words, client)`, then build `SummarizeResponse` with `word_count = len(summary.split())`, `model` from settings, and `request_id` from `request.state.request_id`. Call `log_request(...)` before returning.

---

### T9: Assemble application in main.py

| Field | Value |
|-------|-------|
| Files | `summarizer_service/main.py` |
| Satisfies | R5 (middleware), scaffold |
| Done when | `create_app()` returns a `FastAPI` instance; `uvicorn summarizer_service.main:app` starts without error; `X-Request-ID` header appears on all responses |
| Test | `test_request_id_on_every_response` (integration, in T10d) |

Implement `create_app()`: instantiate `FastAPI`, add `RequestIDMiddleware` (generates `uuid4()`, writes to `request.state.request_id`, appends `X-Request-ID` header to the response), register the three handlers from `api/errors.py`, and include `router` from `api/routes.py`. Expose `app = create_app()` at module level for uvicorn. `get_openai_client` is defined in `core/config.py` and is not re-exported from here.

---

### T10a: Create shared test fixtures

| Field | Value |
|-------|-------|
| Files | `summarizer_service/tests/conftest.py` |
| Satisfies | scaffold (enables T10b–T10d) |
| Done when | `client` fixture returns an `AsyncClient` backed by the app with the real `get_openai_client` overridden; `mock_openai` fixture exposes the `AsyncMock`; `ruff check` passes |
| Test | n/a |

Define two fixtures: `mock_openai` (an `AsyncMock` on `chat.completions.create` returning a minimal completion object) and `client` (an `httpx.AsyncClient` wrapping the app with `app.dependency_overrides[get_openai_client] = lambda: mock_openai`). Import `get_openai_client` from `core/config.py`. Clear `dependency_overrides` after each test.

---

### T10b: Test schema word-count constraint (R6)

| Field | Value |
|-------|-------|
| Files | `summarizer_service/tests/test_schemas.py` |
| Satisfies | R6 |
| Done when | `test_word_count_matches_summary` passes |
| Test | `test_word_count_matches_summary` |

Test that `SummarizeResponse.word_count` equals `len(summary.split())` for a range of inputs (single word, multi-word, leading/trailing whitespace). This is a pure unit test — no HTTP client and no mock needed.

---

### T10c: Test summarizer service (R8, R9)

| Field | Value |
|-------|-------|
| Files | `summarizer_service/tests/test_summarizer.py` |
| Satisfies | R8, R9 |
| Done when | `test_max_words_passed_to_model` and `test_exactly_one_call` pass |
| Test | `test_max_words_passed_to_model`, `test_exactly_one_call` |

Call `summarize()` directly (not via HTTP) using an `AsyncMock` client from `conftest.py`. For R8: assert that the `messages[0]["content"]` (system prompt) contains the `max_words` value. For R9: assert `create` was called exactly once on a clean request and at most twice (initial + one retry) when the first call raises `APIConnectionError`. Use `pytest-asyncio` for async execution.

---

### T10d: Integration tests for the route (R1–R5, R7)

| Field | Value |
|-------|-------|
| Files | `summarizer_service/tests/test_summarize_route.py` |
| Satisfies | R1, R2, R3, R4, R5, R7 |
| Done when | all six test functions pass; `caplog` privacy test shows sentinel absent from every log record and the response body; `ruff check` passes |
| Test | `test_happy_path_200`, `test_empty_text_422_no_call`, `test_oversize_413_no_call`, `test_upstream_failure_502`, `test_request_id_on_every_response`, `test_input_text_never_logged` |

Six tests via `httpx.AsyncClient` (from `conftest.py`). R1: valid body → 200 `SummarizeResponse`. R2: empty/whitespace text → 422, `mock_openai.create` not called. R3: text > 10 000 chars → 413, `mock_openai.create` not called. R4: `mock_openai.create` raises `OpenAIError` → 502 `ErrorResponse` with no stack trace. R5: every response carries matching `request_id` in body and `X-Request-ID` header. R7: seed a unique sentinel string in `text`, capture logs via `caplog`, assert sentinel is absent from all log records and from the response body.
