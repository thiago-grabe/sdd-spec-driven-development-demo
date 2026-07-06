# Summarization Service Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Let any client obtain a concise summary of a block of text over HTTP without embedding model
  logic, prompts, or credentials of its own.
- Ship a single, production-shaped endpoint that wraps exactly one model call, with explicit,
  predictable behavior on every input and failure path.
- Guarantee that user-submitted text is never logged, traced, returned, or persisted.

### Background Context

A service in front of a model is the most common production LLM pattern. Teams repeatedly re-build
it ad hoc, each time re-deciding the response shape, the error codes, the input limits, and the
logging policy — and getting at least one of them wrong (a leaked stack trace, a 200 hiding a
failure, user text in the logs). This PRD specifies that endpoint once, completely, so the build is
boring and correct. The example is deliberately small (one endpoint, one model call) to keep the
whole spec inside one planning session.

### Change Log

| Date       | Version | Description                       | Author        |
|------------|---------|-----------------------------------|---------------|
| 2026-06-22 | 0.1     | Initial PRD for the summarization service | John (PM) |

## Requirements

### Functional

- **FR1**: The service accepts `POST /summarize` with a block of `text` and an optional `max_words`
  and returns a concise summary of that text.
- **FR2**: A successful response is JSON containing `summary`, `word_count`, `model`, and
  `request_id`.
- **FR3**: Empty or whitespace-only `text` is rejected with `422` and no model call is made.
- **FR4**: `text` longer than 10,000 characters is rejected with `413` and no model call is made.
- **FR5**: A model error or timeout returns `502` with a typed `{error, request_id}` body and no
  leaked provider internals or stack trace.
- **FR6**: Every response (success or error) carries `request_id`, also exposed as the
  `X-Request-ID` header.
- **FR7**: `word_count` equals the number of whitespace-separated words in `summary`.
- **FR8**: When `max_words` is provided it is passed to the model as a soft target.
- **FR9**: A successful request triggers exactly one logical model call (≤1 bounded retry on a
  transient network error counts as part of it).

### Non Functional

- **NFR1**: The submitted text MUST NOT appear in any log, trace, error message, or stored artifact;
  logging is metadata-only (request id, lengths, status, latency, model).
- **NFR2**: `OPENAI_API_KEY` is read from the environment only; never hard-coded, returned, or
  logged.
- **NFR3**: The model call uses a 30-second timeout.
- **NFR4**: The service is stateless — no database, no cache, no sessions.
- **NFR5**: Tests MUST mock the model client; CI makes no live model calls and is deterministic.
- **NFR6**: The generated OpenAPI schema matches the documented request/response/error contract.

## Technical Assumptions

### Repository Structure
Single repository, single service (`src/summarizer_service/`).

### Service Architecture
A monolithic FastAPI service with a layered split: `api/` (routes + error mapping),
`services/summarizer.py` (the one model call), `models/schemas.py` (Pydantic v2), `core/` (config +
metadata-only logging). The model client is injected so it can be mocked.

### Testing Requirements
Unit + integration tests with `pytest`; the OpenAI client is mocked. A dedicated privacy test
asserts a seeded marker never appears in logs or response bodies.

### Additional Technical Assumptions and Requests
- Python 3.12, FastAPI, Pydantic v2, openai SDK, uvicorn, `uv` package manager.
- Out of scope for v1: authentication, streaming, caching, persistence, rate limiting, multiple
  models, and any UI. v1 assumes a trusted network.

## Epic List

- **Epic 1 — Summarization Endpoint (MVP)**: stand up the service and deliver `POST /summarize`
  end-to-end — happy path, input validation, the single model call, safe error handling, privacy,
  and request identity — with a mocked-model test suite.

## Epic 1 Summarization Endpoint

**Goal**: Deliver a deployable `POST /summarize` that satisfies every functional and non-functional
requirement above, proven by a deterministic test suite that never calls the live model.

### Story 1.1 Project scaffold and configuration

As a developer,
I want a typed, tested, lint-clean service skeleton with environment-driven configuration,
so that every later story has a consistent place to add behavior and CI can run offline.

#### Acceptance Criteria

1. **Given** a clean checkout, **When** I run the install and test commands, **Then** dependencies
   install via `uv`, `ruff` passes, and `pytest` collects zero tests without error.
2. **Given** the environment provides configuration, **When** the app starts, **Then** settings
   (key, model, timeout=30, cap=10000, retries=1) load from environment variables with documented
   defaults and no secret is logged.
3. **Given** any code path, **When** it logs, **Then** the logger emits metadata only and is
   structurally unable to emit the submitted text.

### Story 1.2 Summarize endpoint end-to-end

As a client application,
I want to POST text and receive a concise summary as JSON, with predictable errors,
so that I can show summaries to my users without embedding any model logic or credentials.

#### Acceptance Criteria

1. **Given** non-empty `text`, **When** I call `POST /summarize`, **Then** I receive `200` with
   `summary`, `word_count`, `model`, and `request_id`, and `word_count` matches the summary. (FR1,
   FR2, FR7)
2. **Given** empty or whitespace-only `text`, **When** I call the endpoint, **Then** I receive `422`
   and no model call is made. (FR3)
3. **Given** `text` over 10,000 characters, **When** I call the endpoint, **Then** I receive `413`
   and no model call is made. (FR4)
4. **Given** the model errors or times out, **When** I call the endpoint, **Then** I receive `502`
   with `{error, request_id}` and no leaked internals. (FR5)
5. **Given** any response, **When** it returns, **Then** it carries `request_id` and the
   `X-Request-ID` header. (FR6)
6. **Given** `max_words` is provided, **When** the summary is produced, **Then** it is passed to the
   model as a soft target and a successful request makes exactly one model call. (FR8, FR9)
7. **Given** a request whose `text` contains a unique marker, **When** it is processed on any path,
   **Then** the marker appears in no log record and no response body. (NFR1)

## Checklist Results Report

PO master checklist run by Sarah (PO): PRD and Architecture are consistent; all FRs are covered by
Epic 1 stories; NFRs are reflected in story acceptance criteria and the architecture's coding
standards. Status: **APPROVED — ready to shard**.

## Next Steps

### Architect Prompt
Read this PRD and produce `docs/architecture.md` for a stateless FastAPI service implementing
`POST /summarize` with one mocked-injectable model call, metadata-only logging, and the
413/422/502 error mapping. Define coding standards, tech stack, and source tree for sharding.

### Scrum Master Prompt
After sharding, draft Story 1.1 then Story 1.2 from `docs/prd/` and `docs/architecture/`, pulling
only the context each story needs.
