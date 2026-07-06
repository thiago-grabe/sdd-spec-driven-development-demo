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
├── main.py                # create_app(), RequestIDMiddleware, register exception handlers, mount router
├── exceptions.py          # PayloadTooLargeError, SummarizerError
├── api/
│   ├── __init__.py
│   ├── routes.py          # POST /summarize — validate → 413 guard → call summarizer → build SummarizeResponse
│   ├── dependencies.py    # get_openai_client() FastAPI dependency  ⚑ see flag below
│   └── errors.py          # exception_handler functions for 413 / 422 / 502
├── services/
│   ├── __init__.py
│   └── summarizer.py      # summarize(), single OpenAI call, 30s timeout, ≤1 retry
├── models/
│   ├── __init__.py
│   └── schemas.py         # SummarizeRequest, SummarizeResponse, ErrorResponse
└── core/
    ├── __init__.py
    ├── config.py          # Settings (pydantic-settings): API key, model, timeouts, limits
    └── logging.py         # log_request() — metadata only, never user text

tests/
├── conftest.py            # app fixture, mock AsyncOpenAI client via dependency_overrides
└── test_routes.py         # one test function per R1–R9
```

> **Flag — module map gap:** `architecture.md` states the OpenAI client is "a FastAPI dependency (`get_openai_client`)" but the module map does not list the file where it lives. This plan places it in `api/dependencies.py` (standard FastAPI convention). No contradiction with the existing map; the file simply needs to be added.

---

### 5.2 Dependency injection

`get_openai_client()` lives in `api/dependencies.py`. It reads `Settings().openai_api_key.get_secret_value()` and returns a configured `AsyncOpenAI` instance. The route declares it as a parameter:

```
# api/routes.py
async def post_summarize(..., client: AsyncOpenAI = Depends(get_openai_client)):
```

In `tests/conftest.py` a fixture replaces the real client before any test runs:

```
# conftest.py (pseudocode)
@pytest.fixture
def app():
    from summarizer_service.main import create_app
    from summarizer_service.api.dependencies import get_openai_client

    mock_client = AsyncMock(spec=AsyncOpenAI)
    application = create_app()
    application.dependency_overrides[get_openai_client] = lambda: mock_client
    yield application, mock_client
    application.dependency_overrides.clear()
```

No `monkeypatch` or global patching is ever needed — the override is scoped to the test's `app` instance.

---

### 5.3 Request-ID middleware (R5)

`RequestIDMiddleware` is registered in `main.py` before the router. For every incoming request it:

1. Generates `request_id = str(uuid.uuid4())`.
2. Stores it on `request.state.request_id`.
3. Calls `await call_next(request)` to get the response.
4. Sets `response.headers["X-Request-ID"] = request_id` before returning.

The route reads `request.state.request_id` and passes it to both `SummarizeResponse` and `ErrorResponse`, satisfying the body-field requirement. Error handlers in `api/errors.py` also read `request.state.request_id` from the `Request` object FastAPI passes to them.

---

### 5.4 Error handling

| Exception | HTTP status | Response model | Where raised |
|-----------|-------------|----------------|--------------|
| `RequestValidationError` (Pydantic/FastAPI) | 422 | `ErrorResponse` | Automatically on invalid/missing fields (R2) |
| `PayloadTooLargeError` | 413 | `ErrorResponse` | `api/routes.py` — explicit guard when `len(text) > settings.max_input_chars` (R3) |
| `SummarizerError` | 502 | `ErrorResponse` | `services/summarizer.py` — wraps any unrecoverable OpenAI error (R4) |

All three handler functions are defined in `api/errors.py` and registered in `main.py`:

```
# main.py (pseudocode)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(PayloadTooLargeError, payload_too_large_handler)
app.add_exception_handler(SummarizerError, summarizer_error_handler)
```

Each handler builds an `ErrorResponse(error=<safe message>, request_id=request.state.request_id)` — no stack trace, no upstream error text is forwarded.

---

### 5.5 Summarizer service (R8, R9)

Function signature (pseudocode):

```
async def summarize(
    text: str,
    max_words: int,
    client: AsyncOpenAI,
    settings: Settings,
) -> str
```

**Single OpenAI call:**

```
response = await client.chat.completions.create(
    model=settings.model,
    messages=[
        {"role": "system", "content": f"Summarize the text in at most {max_words} words."},
        {"role": "user",   "content": text},
    ],
    timeout=settings.timeout_s,   # 30 s
)
return response.choices[0].message.content
```

**Retry logic (R9 — ≤1 retry on transient errors):**

- On `APIConnectionError` or `APITimeoutError` on the first attempt, retry exactly once.
- Any failure on the second attempt, or any non-transient `OpenAIError`, raises `SummarizerError`.
- This counts as one logical call; the mock in `test_exactly_one_call` asserts `call_count == 1` for the happy path.

`max_words` goes directly into the system prompt string (R8), so the model receives the word-count constraint as a soft target.

---

### 5.6 Settings

Defined in `core/config.py` using `pydantic-settings`:

| Field | Type | Default | Env var |
|-------|------|---------|---------|
| `openai_api_key` | `SecretStr` | *(required)* | `OPENAI_API_KEY` |
| `model` | `str` | `"gpt-5.5"` | `MODEL` |
| `timeout_s` | `int` | `30` | `TIMEOUT_S` |
| `max_input_chars` | `int` | `10_000` | `MAX_INPUT_CHARS` |
| `max_retries` | `int` | `1` | `MAX_RETRIES` |

`openai_api_key` is a `SecretStr`; its value is only unwrapped via `.get_secret_value()` at the call site inside `get_openai_client()`. It is never logged, returned, or passed as a plain string anywhere else.

---

### 5.7 Logging (R7)

`log_request()` in `core/logging.py` emits a single structured log record per request containing exactly these fields:

| Field | Type | Notes |
|-------|------|-------|
| `request_id` | `str` | UUID from `request.state` |
| `input_length` | `int` | `len(text)` — the character count, not the text |
| `status_code` | `int` | Final HTTP status |
| `latency_ms` | `float` | Wall-clock time for the request |
| `model` | `str` | Model name from `Settings` |
| `error_class` | `str \| None` | Exception class name only; `None` on success |

User text never appears in any log record — only its length does. `error_class` stores the class name (e.g. `"SummarizerError"`), not the exception message, to prevent upstream error strings from leaking user content.

---

### 5.8 Test coverage

| Req | Test function | File | Mock used |
|-----|--------------|------|-----------|
| R1 | `test_happy_path_200` | `tests/test_routes.py` | `AsyncOpenAI` mock returning a valid completion object |
| R2 | `test_empty_text_422_no_call` | `tests/test_routes.py` | `AsyncOpenAI` mock; `assert mock.chat.completions.create.call_count == 0` |
| R3 | `test_oversize_413_no_call` | `tests/test_routes.py` | `AsyncOpenAI` mock; `assert mock.chat.completions.create.call_count == 0` |
| R4 | `test_upstream_failure_502` | `tests/test_routes.py` | `AsyncOpenAI` mock configured to raise `SummarizerError` |
| R5 | `test_request_id_on_every_response` | `tests/test_routes.py` | `AsyncOpenAI` mock; checks body `request_id` and `X-Request-ID` header match |
| R6 | `test_word_count_matches_summary` | `tests/test_routes.py` | `AsyncOpenAI` mock returning a known fixed summary string |
| R7 | `test_input_text_never_logged` | `tests/test_routes.py` | `AsyncOpenAI` mock + `caplog` fixture; seeds unique sentinel in input, asserts absent from all log records and response body |
| R8 | `test_max_words_passed_to_model` | `tests/test_routes.py` | `AsyncOpenAI` mock; inspects `call_args` to confirm system prompt contains the requested `max_words` value |
| R9 | `test_exactly_one_call` | `tests/test_routes.py` | `AsyncOpenAI` mock; asserts `call_count == 1` on the happy path |

---

## 6. Tasks

### T1: Scaffold the package structure

| Field | Value |
|-------|-------|
| Files | `pyproject.toml`, `.env.example`, `summarizer_service/__init__.py`, `summarizer_service/api/__init__.py`, `summarizer_service/services/__init__.py`, `summarizer_service/models/__init__.py`, `summarizer_service/core/__init__.py`, `tests/__init__.py` |
| Satisfies | scaffold |
| Done when | `uv sync` exits 0 and `python -m pytest --collect-only` runs without import errors |
| Test | n/a |

Create `pyproject.toml` declaring the `summarizer_service` package and its dependencies: `fastapi`, `uvicorn`, `openai`, `pydantic`, `pydantic-settings`. Add `pytest`, `pytest-asyncio`, and `httpx` as dev dependencies. Create `.env.example` with `OPENAI_API_KEY=`, `MODEL=gpt-5.5`, `TIMEOUT_S=30`, `MAX_INPUT_CHARS=10000`, `MAX_RETRIES=1`. All `__init__.py` files are empty. No hard-coded keys anywhere.

---

### T2: Define the three Pydantic models

| Field | Value |
|-------|-------|
| Files | `summarizer_service/models/schemas.py` |
| Satisfies | scaffold (used by R1–R5, R7) |
| Done when | `from summarizer_service.models.schemas import SummarizeRequest, SummarizeResponse, ErrorResponse` exits 0 and field constraints match §3 |
| Test | n/a |

Implement `SummarizeRequest` (`text: str = Field(min_length=1)`, `max_words: int | None = Field(default=150, ge=1, le=1000)`), `SummarizeResponse` (`summary`, `word_count`, `model`, `request_id`), and `ErrorResponse` (`error`, `request_id`) exactly as specified in §3. No imports from other internal modules — only `pydantic`. The 10 000-char cap is enforced in the route (T8), not here.

---

### T3: Define the custom exceptions

| Field | Value |
|-------|-------|
| Files | `summarizer_service/exceptions.py` |
| Satisfies | scaffold (used by R3, R4) |
| Done when | `from summarizer_service.exceptions import PayloadTooLargeError, SummarizerError` exits 0 |
| Test | n/a |

Create `PayloadTooLargeError` and `SummarizerError` as plain `Exception` subclasses with no additional fields. No imports from any other internal module. These are raised in the route (T8) and service (T6) and caught by the handlers (T7).

---

### T4: Implement Settings

| Field | Value |
|-------|-------|
| Files | `summarizer_service/core/config.py` |
| Satisfies | scaffold (used by T6, T8) |
| Done when | `Settings()` instantiates from environment variables and `openai_api_key` is a `SecretStr` |
| Test | n/a |

Use `pydantic-settings` to define `Settings` with the five fields from §5.6: `openai_api_key: SecretStr`, `model: str = "gpt-5.5"`, `timeout_s: int = 30`, `max_input_chars: int = 10_000`, `max_retries: int = 1`. The env var names follow the field names in upper-case. `openai_api_key` must never be accessed as a plain string outside `get_openai_client()` (T8).

---

### T5: Implement metadata-only logging

| Field | Value |
|-------|-------|
| Files | `summarizer_service/core/logging.py` |
| Satisfies | R7 (privacy) |
| Done when | `log_request()` accepts the six metadata fields from §5.7 and emits a structured log record containing none of the user-supplied text |
| Test | `test_input_text_never_logged` (indirectly; direct check in T10d) |

Implement `log_request(request_id, input_length, status_code, latency_ms, model, error_class)` using Python's `logging` module. Log a single JSON-compatible dict with exactly those six keys. The signature accepts only scalars — no `text` parameter exists, making it structurally impossible to log user input. No imports from `services/` or `api/`.

---

### T6: Implement the summarizer service

| Field | Value |
|-------|-------|
| Files | `summarizer_service/services/summarizer.py` |
| Satisfies | R8, R9 |
| Done when | `test_max_words_passed_to_model` and `test_exactly_one_call` pass |
| Test | `test_max_words_passed_to_model`, `test_exactly_one_call` |

Implement `async def summarize(text, max_words, client, settings)` as described in §5.5. The system prompt must contain `max_words` verbatim. On `APIConnectionError` or `APITimeoutError` retry exactly once; on second failure or any other `OpenAIError` raise `SummarizerError`. This is the only place an OpenAI call is made. Imports: `exceptions.py` (T3), `core/config.py` (T4), and the `openai` SDK — nothing else internal.

---

### T7: Implement the exception handlers

| Field | Value |
|-------|-------|
| Files | `summarizer_service/api/errors.py` |
| Satisfies | R2, R3, R4 |
| Done when | Each handler returns the correct HTTP status code and an `ErrorResponse` body with `request_id` set |
| Test | `test_empty_text_422_no_call`, `test_oversize_413_no_call`, `test_upstream_failure_502` (run in T10d) |

Write three async handler functions: `validation_error_handler` (422 for `RequestValidationError`), `payload_too_large_handler` (413 for `PayloadTooLargeError`), `summarizer_error_handler` (502 for `SummarizerError`). Each reads `request.state.request_id` and returns a `JSONResponse` wrapping `ErrorResponse`. No stack trace or upstream error message is forwarded to the client. Imports: `models/schemas.py` (T2), `exceptions.py` (T3).

---

### T8: Implement the POST /summarize route and client dependency

| Field | Value |
|-------|-------|
| Files | `summarizer_service/api/routes.py`, `summarizer_service/api/dependencies.py` |
| Satisfies | R1, R2, R3, R5, R6, R8, R9 |
| Done when | `POST /summarize` returns 200 + `SummarizeResponse` on a valid request (confirmed by `test_happy_path_200`) |
| Test | `test_happy_path_200` (and indirectly all other route tests) |

In `api/dependencies.py` define `get_openai_client() -> AsyncOpenAI` that reads `Settings().openai_api_key.get_secret_value()` and constructs the client — this is the only place the secret is unwrapped. In `api/routes.py` implement the route: validate input, guard `len(text) > settings.max_input_chars` → raise `PayloadTooLargeError`, call `summarize()`, compute `word_count = len(summary.split())` (R6), return `SummarizeResponse` with `request_id` from `request.state.request_id` (R5). Imports: T2, T3, T4, T5, T6, T7 — all created before this task.

---

### T9: Wire up the application

| Field | Value |
|-------|-------|
| Files | `summarizer_service/main.py` |
| Satisfies | R5 (middleware), scaffold |
| Done when | `create_app()` returns a FastAPI instance that starts with `uvicorn summarizer_service.main:app` |
| Test | `test_request_id_on_every_response` (run in T10d) |

Implement `create_app()` that: (1) instantiates `FastAPI`, (2) adds `RequestIDMiddleware` — generates `uuid4`, stores on `request.state.request_id`, sets `X-Request-ID` on the response, (3) registers the three exception handlers from `api/errors.py` via `app.add_exception_handler()`, (4) includes the router from `api/routes.py`. Expose `app = create_app()` at module level for uvicorn. Imports: T3, T7, T8.

---

### T10a: Write the shared test fixtures

| Field | Value |
|-------|-------|
| Files | `tests/conftest.py` |
| Satisfies | scaffold (used by T10b–T10d) |
| Done when | `pytest --collect-only` discovers tests in all three test files without fixture errors |
| Test | n/a |

Define an `app` fixture that calls `create_app()`, swaps `get_openai_client` for a `lambda: mock_client` via `app.dependency_overrides`, and yields `(TestClient(app), mock_client)`. The override is cleared in teardown. Define a `mock_client` fixture as `AsyncMock(spec=AsyncOpenAI)` with a sensible default return value. No live network calls must be possible from any test using these fixtures.

---

### T10b: Test word-count correctness

| Field | Value |
|-------|-------|
| Files | `tests/test_schemas.py` |
| Satisfies | R6 |
| Done when | `pytest tests/test_schemas.py` passes |
| Test | `test_word_count_matches_summary` |

Configure the mock to return a fixed summary string with a known word count. POST to `/summarize`, assert `response.json()["word_count"] == len(summary.split())`. The test is deterministic because the summary string is controlled by the mock.

---

### T10c: Test the summarizer service in isolation

| Field | Value |
|-------|-------|
| Files | `tests/test_summarizer.py` |
| Satisfies | R8, R9 |
| Done when | `pytest tests/test_summarizer.py` passes |
| Test | `test_max_words_passed_to_model`, `test_exactly_one_call` |

Call `summarize()` directly (bypassing HTTP). For R8: assert the `system` message in `mock_client.chat.completions.create.call_args` contains the requested `max_words` value. For R9: assert `call_count == 1` after a successful call. Use `AsyncMock` for the client; no `app` or HTTP client needed in this file.

---

### T10d: Test the HTTP route (acceptance tests)

| Field | Value |
|-------|-------|
| Files | `tests/test_summarize_route.py` |
| Satisfies | R1, R2, R3, R4, R5, R7 |
| Done when | `pytest tests/test_summarize_route.py` passes — all nine named test functions green |
| Test | `test_happy_path_200`, `test_empty_text_422_no_call`, `test_oversize_413_no_call`, `test_upstream_failure_502`, `test_request_id_on_every_response`, `test_input_text_never_logged` |

Cover R1 (200 + valid body), R2 (empty text → 422, mock not called), R3 (10 001-char text → 413, mock not called), R4 (mock raises `SummarizerError` → 502, no stack trace in body), R5 (body `request_id` equals `X-Request-ID` header across multiple requests). For R7 (`test_input_text_never_logged`): seed a unique sentinel string in `text`, capture log output with `pytest`'s `caplog` fixture, assert the sentinel never appears in any log record or in the response body — this is the mandatory privacy test from the constitution.
