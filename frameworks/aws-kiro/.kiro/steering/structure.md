---
inclusion: always
---

# Structure

## Project layout
```
src/summarizer_service/
├── main.py              # create_app(): middleware, exception handlers, router
├── exceptions.py        # PayloadTooLargeError, SummarizerError
├── core/
│   ├── config.py        # Settings from env (key, model, timeout, cap, retries)
│   └── logging.py       # metadata-only logging (never user text)
├── models/
│   └── schemas.py       # SummarizeRequest / SummarizeResponse / ErrorResponse
├── services/
│   └── summarizer.py    # the ONE OpenAI call (30s timeout, <=1 retry)
└── api/
    ├── routes.py        # POST /summarize (validate -> 413 guard -> call -> build)
    └── errors.py        # 413 / 422 / 502 -> ErrorResponse
tests/
├── conftest.py          # mocked OpenAI client + TestClient (no live calls)
├── unit/                # test_schemas.py, test_summarizer.py
└── integration/         # test_summarize_route.py
```

## Naming & organization conventions
- **One responsibility per module.** Model definitions, the model-call wrapper, and the HTTP layer
  live in separate files so each can be tested in isolation.
- **Dependencies point inward:** `api/` → `services/` → `core/`. Never the reverse.
- **Dependency injection over monkey-patching.** The OpenAI client is injected via a FastAPI
  dependency so tests swap it for a mock without patching globals.
- **Typed errors, mapped at the boundary.** Domain failures are named exception types translated to
  status codes in `api/errors.py` — never `except Exception: pass`, never a leaked upstream trace.
- **Kebab-case** for spec folders under `.kiro/specs/`; **snake_case** for Python modules.
