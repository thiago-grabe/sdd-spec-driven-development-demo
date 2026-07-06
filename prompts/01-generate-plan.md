# Prompt 01 — Write the Implementation Plan (spec.md §5)

Read these three files before you do anything:
- `specs/constitution.md`
- `specs/spec.md`
- `specs/architecture.md`

---

## What to produce

Write `## 5. Plan` and append it to `specs/spec.md`. Cover each section below. Reference requirement numbers (R1–R9) where relevant.

### 5.1 File layout

Show the full directory tree for `summarizer_service/` with one-line descriptions per file. Base it on the module map in `architecture.md`.

### 5.2 Dependency injection

How is the `AsyncOpenAI` client injected so tests never make a live call? Name the dependency function and where it lives. Show the mock swap pattern used in `conftest.py`.

### 5.3 Request-ID middleware

How is `request_id` assigned once per request and attached to every response body and `X-Request-ID` header? (R5)

### 5.4 Error handling

Map each exception class to its status code and response model (422 / 413 / 502). Where are the handlers registered?

### 5.5 Summarizer service

Describe the `summarize()` function signature, the single OpenAI call, 30s timeout, ≤1 retry on transient errors, and how `max_words` goes into the system prompt. (R8, R9)

### 5.6 Settings

List the `Settings` fields, their defaults, and env var names. Note that `openai_api_key` uses `SecretStr`.

### 5.7 Logging

List the metadata fields logged per request. Confirm user text is never one of them. (R7)

### 5.8 Test coverage

One row per R1–R9: test function name, file, mock used.

---

## Rules

- No Python code — pseudocode is fine if it helps.
- Don't contradict `architecture.md` — if you spot an inconsistency, flag it.
- Stay within the out-of-scope list in `spec.md §4`.
- After appending the Plan to `spec.md`, **stop**. Don't write tasks or code yet.
