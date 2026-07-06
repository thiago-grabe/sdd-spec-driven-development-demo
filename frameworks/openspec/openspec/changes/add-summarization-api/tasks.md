## 1. Scaffolding & configuration

- [ ] 1.1 Create the `summarizer_service` package (api / services / models / core) per design.md
- [ ] 1.2 Add dependencies (FastAPI, Pydantic v2, openai, uvicorn, pytest, ruff) via uv
- [ ] 1.3 Implement `core/config.py` (Settings: key, model, timeout=30, cap=10000, retries=1 from env)
- [ ] 1.4 Implement `core/logging.py` (metadata-only; cannot emit user text)

## 2. Contracts

- [ ] 2.1 Implement `SummarizeRequest` (text min length 1; max_words 1–1000 default 150)
- [ ] 2.2 Implement `SummarizeResponse` (summary, word_count, model, request_id)
- [ ] 2.3 Implement `ErrorResponse` (error, request_id)

## 3. The one model call

- [ ] 3.1 Implement `services/summarizer.py`: exactly one chat.completions.create call, 30s timeout
- [ ] 3.2 Add at most one bounded retry on transient network error
- [ ] 3.3 Fold `max_words` into the system prompt as a soft target
- [ ] 3.4 Raise `SummarizerError` (text-free) on failure

## 4. Route, errors, and identity

- [ ] 4.1 Implement `POST /summarize`: validate → 413 guard before any call → call → compute
      word_count → build response
- [ ] 4.2 Implement error mapping: validation→422, PayloadTooLargeError→413, SummarizerError→502
- [ ] 4.3 Implement request-id middleware (body + `X-Request-ID` header on every response)

## 5. Tests (model client mocked)

- [ ] 5.1 Happy path → 200, schema-valid, word_count matches
- [ ] 5.2 Empty/whitespace → 422, no model call; oversize → 413, no model call
- [ ] 5.3 Upstream failure → 502, typed body, no leak
- [ ] 5.4 Privacy: seeded marker absent from all logs and response bodies
- [ ] 5.5 Exactly one model call per success; X-Request-ID on every response
