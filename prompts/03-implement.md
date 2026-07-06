# Prompt 03 — Implement the Summarization API

> Run this after the Plan (§5) and Tasks (§6) are in `spec.md` and approved.

Read these files first:
- `specs/constitution.md`
- `specs/spec.md` (all sections)
- `specs/architecture.md`

---

## Working rules

1. **One task per reply.** Implement T1, show the files, stop. Wait for approval. Then T2, and so on.
2. **Show complete files every time.** Never truncate with "…rest unchanged…".
3. **The spec is the source of truth.** Don't add fields, endpoints, auth, caching, or anything in the out-of-scope list.
4. **No live model calls in tests.** Every test touching the OpenAI client uses the mock from `conftest.py`.
5. **After each task, run:**
   ```bash
   uv run ruff check . && uv run ruff format --check .
   ```
   For test tasks, also run `uv run pytest tests/ -v` and confirm the target tests are green.

---

## Task header (use this format for each reply)

```
## T<N>: <title>
Satisfies: <R-numbers or scaffold>
Files: <list>
```

---

## Key implementation notes

**T1 — Scaffold**
`pyproject.toml` deps: `fastapi>=0.115`, `uvicorn[standard]>=0.30`, `openai>=1.30`, `pydantic-settings>=2.3`. Dev deps: `pytest>=8`, `pytest-asyncio>=0.23`, `httpx>=0.27`, `ruff>=0.4`, `anyio>=4`. Add `[tool.pytest.ini_options] asyncio_mode = "auto"` and `[tool.ruff.lint] select = ["E","F","I"]`.

**T2 — Schemas**
`SummarizeRequest` needs a `@field_validator("text")` that rejects whitespace-only strings — `min_length=1` alone passes `"   "` because it counts characters, not content. Reject if `v.strip()` is empty → `ValueError` → 422. (R2)

**T3 — Exceptions**
`PayloadTooLargeError` and `SummarizerError`. Neither carries user text or raw upstream messages.

**T4 — Settings**
`BaseSettings` fields: `openai_api_key: SecretStr`, `model: str = "gpt-5.5"`, `timeout_s: int = 30`, `max_input_chars: int = 10_000`, `max_retries: int = 1`. Use `@lru_cache` on `get_settings()`.

**T5 — Logger**
`log_request(*, request_id, input_length, status_code, latency_ms, model=None, error_class=None)`. Never a `text` parameter. Log at INFO/WARNING/ERROR by status range.

**T6 — Summarizer**
`async def summarize(text, max_words, client, settings) -> tuple[str, str]`. Embed `max_words` in the system prompt. One call. On `APIConnectionError` or `APITimeoutError`, retry once then raise `SummarizerError`. On any other `OpenAIError`, raise `SummarizerError` immediately. Return `(summary, model_name)`.

**T7 — Error handlers**
Three async handlers: `RequestValidationError` → 422, `PayloadTooLargeError` → 413, `SummarizerError` → 502. Every `ErrorResponse` includes `request_id` from `request.state`. Log metadata before returning.

**T8 — Route**
After Pydantic validates, check `len(body.text) > settings.max_input_chars` and raise `PayloadTooLargeError` (R3). Call `summarize()`. Set `word_count = len(summary.split())` (R6). `request_id` from `request.state`. The `X-Request-ID` header is set by middleware — don't set it here.

**T9 — App factory**
`RequestIDMiddleware`: sets `request.state.request_id = str(uuid4())` and `request.state.start_time = time.monotonic()` before dispatching; adds `X-Request-ID` to response after. Register the three exception handlers. Mount the router. Expose `app = create_app()`.

**T10a — Fixtures**
`mock_openai_client`: `MagicMock` with `chat.completions.create = AsyncMock(return_value=<completion mock>)`. `async_client`: `httpx.AsyncClient(ASGITransport(app))` with `get_openai_client` and `get_settings` overridden. `test_settings`: `Settings(openai_api_key="sk-test", ...)`.

**T10b — Schema tests (R6)**
`test_word_count_matches_summary`: parametrize with 3-4 summaries, assert `word_count == len(summary.split())`.

**T10c — Summarizer tests (R8, R9)**
- `test_max_words_passed_to_model`: assert the `max_words` value appears in the messages sent to the mock.
- `test_exactly_one_call`: assert `create.call_count == 1`.
- `test_retry_on_transient_error`: mock raises `APIConnectionError` first, then succeeds — assert `call_count == 2`.
- `test_raises_summarizer_error_after_retry`: both attempts fail → `SummarizerError` raised.

**T10d — Route tests (R1–R5, R7)**
- `test_happy_path_200`: valid body → 200, response has all four fields, `word_count` matches.
- `test_empty_text_422_no_call`: `"   "` → 422, mock not called.
- `test_oversize_413_no_call`: 10,001 chars → 413, mock not called.
- `test_upstream_failure_502`: mock raises `OpenAIError` → 502, raw error string not in response.
- `test_request_id_on_every_response`: check all four status codes — body has `request_id`, header has `X-Request-ID`, they match.
- `test_input_text_never_logged`: seed a unique marker in `text`, capture logs with `caplog`, assert marker absent from every log record and the response body.

---

## Final check (after T10d)

```bash
uv run pytest tests/ -v
uv run ruff check .
uv run ruff format --check .
```

All three must exit 0. Verify against the spec's requirements table (R1–R9) — every row needs a green test.
