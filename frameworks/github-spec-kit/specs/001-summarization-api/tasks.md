# Tasks: Summarization API

**Input**: Design documents from `/specs/001-summarization-api/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3)

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Create the `src/summarizer_service/` package structure per plan.md
- [ ] T002 Initialize the project with FastAPI, Pydantic v2, openai, uvicorn, pytest (via `uv`)
- [ ] T003 [P] Configure ruff (lint + format) and pytest in `pyproject.toml`

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No user-story work can begin until this phase is complete.

- [ ] T004 Implement `core/config.py` — `Settings` reads key, model, timeout=30, cap=10000,
      retries=1 from the environment
- [ ] T005 [P] Implement `core/logging.py` — metadata-only logger (request id, length, status,
      latency, model); structurally incapable of emitting user text
- [ ] T006 [P] Implement `exceptions.py` — `PayloadTooLargeError`, `SummarizerError` (text-free)
- [ ] T007 Implement request-id middleware in `main.py` — assign a uuid, set `X-Request-ID` on every
      response (FR-006)

## Phase 3: User Story 1 - Summarize a valid block of text (Priority: P1) 🎯 MVP

**Goal**: A valid request returns a 200 with a usable summary payload.
**Independent Test**: POST valid text → 200 with summary, word_count, model, request_id.

### Tests for User Story 1
- [ ] T008 [P] [US1] Unit test for `SummarizeRequest` defaults and `word_count` helper in
      tests/unit/test_schemas.py (FR-002, FR-007)
- [ ] T009 [P] [US1] Unit test for the one-call summarizer (mocked client) in
      tests/unit/test_summarizer.py (FR-009, FR-008)
- [ ] T010 [P] [US1] Integration test for the happy path in tests/integration/test_summarize_route.py
      (FR-001, FR-002, FR-007)

### Implementation for User Story 1
- [ ] T011 [P] [US1] Implement `models/schemas.py` — `SummarizeRequest`, `SummarizeResponse`,
      `ErrorResponse` (FR-001, FR-002)
- [ ] T012 [US1] Implement `services/summarizer.py` — exactly one `chat.completions.create` call,
      30s timeout, ≤1 bounded retry, `max_words` folded into the system prompt (FR-008, FR-009)
- [ ] T013 [US1] Implement `api/routes.py` happy path — call service, compute `word_count`, build
      `SummarizeResponse` (FR-002, FR-007)

**Checkpoint**: User Story 1 is fully functional and independently testable.

## Phase 4: User Story 3 - Trust that private text stays private (Priority: P1)

**Goal**: User text never appears in logs, traces, or error output.
**Independent Test**: seed a marker in `text`, run success + failure paths, assert marker absent.

- [ ] T014 [US3] Privacy test: seed a unique marker, capture all logs + bodies, assert it appears
      nowhere (FR-010); confirm key is never logged/returned (FR-011)
- [ ] T015 [US3] Audit `core/logging.py` and `api/errors.py` against the test; fix any leak

**Checkpoint**: Privacy guarantee demonstrable, independent of the error work below.

## Phase 5: User Story 2 - Clear, safe errors (Priority: P2)

**Goal**: Invalid input and upstream failure produce documented, typed, leak-free outcomes.
**Independent Test**: empty → 422 (no call); oversize → 413 (no call); upstream fail → 502.

- [ ] T016 [P] [US2] Integration test: empty/whitespace → 422 and no model call (FR-003)
- [ ] T017 [P] [US2] Integration test: oversize text → 413 and no model call (FR-004)
- [ ] T018 [P] [US2] Integration test: simulated upstream failure → 502, typed body, no leak (FR-005)
- [ ] T019 [US2] Implement the 10k route guard in `api/routes.py` raising `PayloadTooLargeError`
      before any model call (FR-004)
- [ ] T020 [US2] Implement `api/errors.py` — map validation→422, `PayloadTooLargeError`→413,
      `SummarizerError`→502, each returning `ErrorResponse(error, request_id)` (FR-003, FR-005)

**Checkpoint**: All three error scenarios pass; happy path still green.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T021 Wire `main.py` `create_app()` + `__main__.py`; verify `uvicorn` run and `/docs`
- [ ] T022 [P] Verify generated OpenAPI matches `contracts/openapi.yaml` (Principle III)
- [ ] T023 [P] Run quickstart.md end-to-end; run ruff + full suite; confirm Definition of Done

## Dependencies & Execution Order

- Setup (T001–T003) → Foundational (T004–T007) → US1 (T008–T013) → US3 (T014–T015) →
  US2 (T016–T020) → Polish (T021–T023).
- US1 is the MVP and can ship before US2. US3 depends only on Foundational logging + any path.
- `[P]` tasks within a phase touch different files and may run concurrently.

## Implementation Strategy

- **MVP First**: deliver US1 (happy path) end-to-end, then layer US3 (privacy) and US2 (errors).
- **Incremental Delivery**: each user story is independently testable at its checkpoint.
- **Verify each task** against its FR before moving on; if implementation contradicts the spec, fix
  the spec first (Principle I).
