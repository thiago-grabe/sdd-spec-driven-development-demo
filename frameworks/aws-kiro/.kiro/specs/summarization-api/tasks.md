# Implementation Plan

- [ ] 1. Set up project structure and configuration
  - Create the `src/summarizer_service/` tree (core, models, services, api) and the `tests/` tree
  - Add `pyproject.toml` (FastAPI, Pydantic v2, openai, uvicorn, pytest, ruff) and ruff config
  - Implement `core/config.py` with `Settings` reading key, model, timeout=30, cap=10000, retries=1
  - _Requirements: 6.2, 6.3, 5.2_

- [ ] 2. Implement metadata-only logging
  - Implement `core/logging.py` so it logs request id, length, status, latency, and model name only
  - Write a unit test asserting the formatter cannot emit a seeded marker string from the request
  - _Requirements: 5.1, 5.3_

- [ ] 3. Implement data models and validation
  - Write `models/schemas.py`: `SummarizeRequest` (text min_length 1; max_words default 150, 1..1000),
    `SummarizeResponse`, `ErrorResponse`
  - Write unit tests proving empty/whitespace text is rejected, defaults apply, and a helper computes
    `word_count` from a summary
  - _Requirements: 1.2, 2.1_

- [ ] 4. Implement custom exceptions
  - Write `exceptions.py`: `PayloadTooLargeError` and `SummarizerError`, each carrying a text-free message
  - _Requirements: 2.2, 3.1_

- [ ] 5. Implement the summarizer service (the one model call)
  - Write `services/summarizer.py` `summarize(client, text, max_words)`: exactly one
    `chat.completions.create(...)` with a 30s timeout, folding `max_words` into the system prompt
  - Retry at most once on a transient network error; raise `SummarizerError` on failure
  - Write unit tests (mocked client) for exactly one logical call, max_words reaching the model, and
    provider error → `SummarizerError` with no leaked trace
  - _Requirements: 1.3, 1.4, 3.1, 3.3, 6.1, 6.2_

- [ ] 6. Implement request-id middleware
  - Add middleware in `main.py` that assigns a uuid request id, exposes it to handlers, and sets the
    `X-Request-ID` header on every response
  - Write an integration test asserting the header is present on a 200 and on an error
  - _Requirements: 4.1, 4.2_

- [ ] 7. Implement the route
  - Write `api/routes.py` `POST /summarize`: rely on Pydantic for 422, enforce the 10k cap as a 413
    before any call, invoke the service, compute `word_count`, build `SummarizeResponse`
  - Write integration tests for the happy path, empty→422 (no call), oversize→413 (no call), and
    matching `word_count`
  - _Requirements: 1.1, 1.2, 2.1, 2.2_

- [ ] 8. Implement error handling
  - Write `api/errors.py`: map `PayloadTooLargeError`→413, validation→422, `SummarizerError`→502, each
    returning `ErrorResponse(error, request_id)` with no stack trace and no user text
  - Write an integration test proving 502 on upstream failure with a schema-valid body and no leaked internals
  - _Requirements: 2.3, 3.1, 3.2_

- [ ] 9. Add the privacy test
  - Seed a unique marker into `text`, exercise happy and failure paths, capture all log records and the
    error body, and assert the marker appears nowhere
  - _Requirements: 5.1, 5.3_

- [ ] 10. Assemble the app and wire CI
  - Wire `main.py` `create_app()` (middleware + handlers + router) and `__main__.py`
  - Configure CI to run `ruff check`, `ruff format --check`, and `pytest` with no network access
  - _Requirements: 1.1, 5.2_
