# Implementation Plan: Summarization API

**Branch**: `001-summarization-api` | **Date**: 2026-06-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-summarization-api/spec.md`

## Summary

A single `POST /summarize` HTTP endpoint wraps exactly one OpenAI chat-completion call. Pydantic v2
validates input (empty/whitespace → 422); a route guard rejects oversize text (>10,000 chars → 413)
before any model call; the model call runs with a 30s timeout and at most one bounded retry; upstream
failures map to a typed 502. Every response carries a request id (header `X-Request-ID`). Logging is
metadata-only; the user's text is never logged. Tests mock the model client so CI makes no live
calls.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Pydantic v2, openai (official SDK), uvicorn
**Storage**: N/A (stateless — no DB, no cache)
**Testing**: pytest, httpx TestClient; the OpenAI client is mocked (no live calls)
**Target Platform**: Linux container, run locally under uvicorn for the demo
**Project Type**: web-service (single backend service)
**Performance Goals**: one model call per request; 30s model timeout; p99 dominated by model latency
**Constraints**: 10,000-char hard input cap; ≤1 bounded retry; key from env; never log user text
**Scale/Scope**: one endpoint, three models, stateless — scale horizontally by running more replicas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Status |
|-----------|-------|--------|
| I. Spec-First, Code-Last | spec.md complete, no `[NEEDS CLARIFICATION]` remain | ✅ PASS |
| II. Test-Backed Behavior | every FR maps to a test; model client mocked | ✅ PASS |
| III. Contract Stability | request/response/error shapes + status codes fixed in `contracts/` | ✅ PASS |
| IV. Privacy by Default | metadata-only logging; key from env; typed errors | ✅ PASS |
| V. Minimal Scope | one endpoint; auth/cache/DB/streaming explicitly out of scope | ✅ PASS |

**Initial Constitution Check: PASS** — no violations, `Complexity Tracking` left empty.
**Post-Design Re-check: PASS** — design adds no project, pattern, or dependency beyond the above.

## Project Structure

### Documentation (this feature)

```text
specs/001-summarization-api/
├── plan.md              # this file
├── spec.md              # the what & why
├── research.md          # Phase 0 output (decisions below; trivial here)
├── data-model.md        # Phase 1 output — the three entities
├── quickstart.md        # Phase 1 output — run & verify locally
├── contracts/           # Phase 1 output
│   └── openapi.yaml     # the HTTP contract
├── checklists/
│   └── requirements.md  # spec-quality gate (unit tests for English)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/summarizer_service/
├── __init__.py
├── __main__.py          # python -m summarizer_service
├── main.py              # create_app(): request-id middleware, error handlers, router
├── exceptions.py        # PayloadTooLargeError, SummarizerError
├── core/
│   ├── config.py        # Settings from env (key, model, timeout, cap, retries)
│   └── logging.py       # metadata-only logger (never user text)
├── models/
│   └── schemas.py       # SummarizeRequest / SummarizeResponse / ErrorResponse
├── services/
│   └── summarizer.py    # the ONE OpenAI call (+ ≤1 retry, 30s timeout)
└── api/
    ├── routes.py        # POST /summarize (validate → 413 guard → call → build)
    └── errors.py        # 413 / 422 / 502 → ErrorResponse

tests/
├── conftest.py          # mocked OpenAI client + TestClient
├── unit/
│   ├── test_schemas.py
│   └── test_summarizer.py
└── integration/
    └── test_summarize_route.py
```

**Structure Decision**: Option 1 (single project). The service is one backend with no frontend and
no shared library, so a single `src/` package with a layered split (api / services / models / core)
is the simplest structure that still isolates the model call for mocking.

## Phase 0: Research (research.md)

The stack is fixed by the constitution and the technical context, so research is minimal:

- **Decision**: Use Chat Completions (`client.chat.completions.create`) — stable, familiar response
  shape. **Rationale**: simplest single-call surface. **Alternatives**: Responses API (more surface
  than needed for one call).
- **Decision**: Enforce the 10k cap as a route-level 413, not a Pydantic `max_length`.
  **Rationale**: `max_length` would surface oversize input as 422, the wrong status for FR-004.
- **Decision**: Inject the OpenAI client via a FastAPI dependency. **Rationale**: tests swap a mock
  without monkey-patching globals (Principle II).

## Phase 1: Design (data-model.md, contracts/, quickstart.md)

- `data-model.md` defines the three entities and their field-level rules.
- `contracts/openapi.yaml` pins the endpoint, the request/response/error schemas, and the status
  codes (200/413/422/502) — the artifact the generated OpenAPI must match (Principle III).
- `quickstart.md` is the run-and-verify script that demonstrates each acceptance scenario locally.

## Complexity Tracking

*No constitution violations — this table is intentionally empty.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| — | — | — |
