# spec.md — Summarization API (`POST /summarize`)

> **Single source of truth.** This file is the complete specification for the Summarization Service.
> It owns the stack, the conventions, the security and privacy posture, the testing policy, the
> definition of "done", and the per-feature interface and plan. There is no separate `constitution.md`,
> `plan.md`, or `tasks.md` — the **Plan** and **Tasks** sections live here.

---

## 1. Context & Goal

A single HTTP endpoint, **`POST /summarize`**, takes a block of text (and an optional `max_words`)
and returns a concise summary produced by **one** OpenAI model call, as JSON. It is the simplest
shape of the most common production LLM pattern: *a service in front of a model.* Any client can
get a summary over HTTP without embedding model logic, prompts, or API keys of its own.

Keep the surface to exactly one endpoint; non-goals are listed in §6.

## 2. Stack & Conventions

### 2.1 Stack & runtime
- **Language:** Python 3.12 (modern syntax — `X | None`, built-in generics, `match` where it helps).
- **Web framework:** FastAPI.
- **Validation / models:** Pydantic v2 (`BaseModel`, `Field`, validators). All request and response
  bodies are typed Pydantic models — **no bare `dict`s cross the API boundary**.
- **LLM provider (runtime):** the official OpenAI Python SDK (`openai`). The application calls an
  **OpenAI** model at runtime; this is independent of whatever coding agent authored the code.
- **ASGI server:** `uvicorn` for local runs.
- **Package manager:** `uv` (per workspace convention).

### 2.2 Code conventions
- **Type hints everywhere.** Every function signature is fully annotated. Public functions carry a
  docstring stating *intent*, not implementation.
- **Lint/format clean.** Code must pass `ruff check` and `ruff format` with no warnings before it is
  considered done. Prefer small, single-responsibility functions.
- **Separation of layers.** Keep model definitions, the model-call wrapper, and the HTTP/route layer
  in separate modules so each can be tested in isolation (see §7 project structure).
- **No dead code, no commented-out blocks, no stray `TODO`s in shipped code.**
- **Errors are typed and explicit.** Never swallow an exception and return a success; surface
  failures as the status codes defined in §4.

## 3. Security & Privacy (non-negotiable)

These rules are absolute. A violation is a release blocker, not a code review nit.

- **Secrets come from the environment.** API keys and other secrets are read from environment
  variables (e.g. `OPENAI_API_KEY`). They are **never** hard-coded, written to disk, returned in a
  response, or written to logs.
- **Never log raw user text.** The user-supplied content being summarized must never appear in
  logs, traces, error messages, or analytics. Log **metadata only** — request id, length/byte
  counts, status code, latency, and the model name.
- **Never leak upstream errors.** Provider stack traces, raw error bodies, and prompts must not
  appear in client responses. Map them to the typed `ErrorResponse` defined in §5.
- **Fail closed.** On any uncertainty about whether something is safe to log or return, do not log
  or return it.

## 4. Requirements & Acceptance Criteria

Each criterion is written so it can be turned directly into a test ("unit tests for English").

| #  | Behavior          | Acceptance criterion |
|----|-------------------|----------------------|
| R1 | Happy path        | A valid body returns **200** with JSON that validates against `SummarizeResponse`. |
| R2 | Empty input       | `text` that is empty or whitespace-only returns **422** and makes **no model call**. |
| R3 | Oversize input    | `text` longer than **10,000** characters returns **413** and makes **no model call**. |
| R4 | Upstream failure  | If the model errors or times out, return **502** with a body that validates against `ErrorResponse`. **Never leak a stack trace or the provider's raw error.** |
| R5 | Request id        | **Every** response (success or error) carries a `request_id`, also returned as `X-Request-ID`. |
| R6 | Word count        | On success, `word_count` equals the number of whitespace-separated words in `summary`. |
| R7 | Privacy           | The input text never appears in logs, traces, or error messages (asserted by test). |
| R8 | Length hint       | When `max_words` is provided, it is passed to the model as a target and respected as a soft limit. |
| R9 | One call          | A successful request triggers **exactly one** call to the OpenAI client (≤1 bounded retry on transient network error counts as part of the same logical call). |

## 5. Interface & Data Contracts

### Models (Pydantic v2)

```python
class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1)            # 10k cap is a route-level 413 (see below), not max_length
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

> The schema enforces only *non-empty* text (empty/whitespace → 422). The 10,000-character cap is
> enforced in the route as a **413**; a `max_length` on the model would instead surface oversize
> input as a 422, which is the wrong status for R3.

### Endpoint

- `POST /summarize`
- Request body → `SummarizeRequest`
- `200` → `SummarizeResponse`
- `413` → text over the 10k cap (explicit route guard; **no** model call)
- `422` → empty/whitespace input (Pydantic validation; **no** model call)
- `502` → `ErrorResponse` on any upstream model error/timeout

### Status codes (summary)

`200` success · `413` text > 10k chars · `422` empty/whitespace · `502` model error/timeout.

### The one model call

Exactly one OpenAI call per request, via Chat Completions:

```python
completion = client.chat.completions.create(
    model="gpt-5.5",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ],
    timeout=30,
)
summary = completion.choices[0].message.content
```

The client is constructed as `OpenAI()` and reads `OPENAI_API_KEY` from the environment.

## 6. Constraints, Guardrails & Out of Scope

### Constraints & guardrails
- **One model call per request**, with **at most one** bounded retry on a transient network error.
- **Hard input cap** of 10,000 characters, enforced *before* any model call.
- **30-second** timeout on the model call.
- **`OPENAI_API_KEY` from an environment variable** — never hard-coded, returned, or logged.
- **Never log the user's text** — metadata only (request id, length, status, latency, model).
- **Stateless** — no session and no stored request/response data.

### Out of scope (v1)
- No caller authentication (v1 assumes a trusted network).
- No streaming (no SSE/websockets).
- No caching.
- No caller-chosen model and no additional endpoints.
- No database / persistence.
- No rate limiter.
- No web UI.

## 7. Testing Policy

- **Unit tests mock the model client.** Tests must **never** make a live network call to OpenAI.
  The model client is mocked/stubbed so the suite is deterministic, free, and runnable in CI
  offline.
- **Every acceptance criterion in §4 has at least one test.** Tests assert on status codes,
  response shape, and the privacy rules (including that the input text is **absent** from captured
  logs).
- **One privacy-specific test** asserts that, given a marker string in `text`, that string does
  not appear in any captured log record or any error response body.
- **CI runs the full suite on every change** and must be green before merge.

## 8. Plan

*The "how," folded into this spec. The agent proposes this; you approve it before any code is written.*

### 8.1 Project structure (target tree)

A small but production-shaped Python service — `src/` layout, typed, tested, container- and CI-ready:

```text
summarization-service/
├── pyproject.toml                  # deps, build, ruff + pytest config
├── Makefile                        # install / run / test / lint / fmt
├── Dockerfile                      # slim runtime image
├── .env.example                    # OPENAI_API_KEY + tunables (never commit .env)
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml                  # ruff + pytest, NO live model calls
├── docs/
│   ├── spec.md                     # ← this file (the source of truth)
│   └── architecture.md             # request lifecycle + module map
├── src/
│   └── summarizer_service/
│       ├── __init__.py
│       ├── __main__.py             # python -m summarizer_service
│       ├── main.py                 # create_app(): middleware, handlers, router
│       ├── exceptions.py           # SummarizerError, PayloadTooLargeError
│       ├── core/
│       │   ├── config.py           # Settings from env (key, model, timeout, caps, retries)
│       │   └── logging.py          # metadata-only logging (never user text)
│       ├── models/
│       │   └── schemas.py          # SummarizeRequest / SummarizeResponse / ErrorResponse
│       ├── services/
│       │   └── summarizer.py       # the ONE OpenAI call (+ ≤1 retry, 30s timeout)
│       └── api/
│           ├── routes.py           # POST /summarize  (validate → 413 guard → call → build)
│           └── errors.py           # 413 / 422 / 502 → ErrorResponse
└── tests/
    ├── conftest.py                 # mocked OpenAI client + TestClient (no live calls)
    ├── unit/
    │   ├── test_schemas.py
    │   └── test_summarizer.py
    └── integration/
        └── test_summarize_route.py
```

> The three models live in `models/schemas.py`; the single model call is isolated in
> `services/summarizer.py` so it can be unit-tested with a mock; HTTP concerns (routing, status-code
> mapping, the per-request id) live in `api/`. That separation is exactly what lets the test suite
> mock the model client and run with no live calls.

### 8.2 Request flow

1. FastAPI validates the body against `SummarizeRequest` (empty/whitespace → **422** automatically).
2. The route enforces the 10k cap and returns **413** for oversize text — **before** any model call.
3. On valid input, `services/summarizer.py` makes exactly one model call (30s timeout, ≤1 retry).
4. On success, the route computes `word_count`, builds `SummarizeResponse` (echoing `model` and the
   per-request `request_id`).
5. On any model error/timeout, `api/errors.py` returns **502** `ErrorResponse(error, request_id)` —
   no stack trace and no user text.

### 8.3 Key decisions

- Use **Chat Completions** (`client.chat.completions.create`) for a familiar, stable response shape.
- The schema enforces only *non-empty* text; the **10k cap is a route-level 413** so oversize input
  is rejected with the right status.
- A request-id middleware stamps every request and response (header `X-Request-ID`); logging is
  **metadata-only** by policy (see §3).
- The OpenAI client is injected into the route via a FastAPI dependency so tests can swap it for a
  mock without monkey-patching.

## 9. Tasks

**TBD** 

## 10. Definition of Done

A feature is done when **all** of the following hold:

1. Every acceptance criterion in §4 is implemented and covered by a passing test.
2. The full test suite is green in CI, with **no live model calls**.
3. The generated OpenAPI schema matches the interface in §5 (model names, fields, status codes).
4. `ruff check` and `ruff format` report no issues.
5. No secret and no raw user text can appear in logs or responses (verified by a test — see §7).
