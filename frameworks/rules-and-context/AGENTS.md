# AGENTS.md

Tool-agnostic guidance for any AI coding agent working in this repo. Cursor, GitHub Copilot, Codex,
Gemini CLI, Zed, and others read `AGENTS.md` directly; Claude Code reads it via the `@AGENTS.md`
import in `CLAUDE.md`.

> **Note on scope.** Rules & context files are the *lightest* rung of spec-driven development — they
> encode standing conventions that steer the agent on every request. They are **adjacent to**, not a
> replacement for, a per-feature spec → plan → tasks flow. Think of this file as the reusable
> "constitution" layer; a real feature still needs its own specification.

## What we are building
A **Summarization API**: one endpoint, `POST /summarize`, that takes a block of text and returns a
concise summary from **exactly one** OpenAI model call, as JSON. A service in front of a model.

## Stack
- Python 3.12 · FastAPI · Pydantic v2 · the official `openai` SDK · `uvicorn` · `uv` · `pytest` · `ruff`.
- The app calls an OpenAI model (`gpt-5.5`) at runtime. The coding agent is a separate choice from
  the model the app ships on.

## Commands
- Install: `uv sync`
- Run: `uv run uvicorn summarizer_service.main:app --reload`
- Test: `uv run pytest`
- Lint/format: `uv run ruff check` and `uv run ruff format`

## Conventions
- Type hints on every function signature. No bare `dict` crosses an API boundary — use Pydantic models.
- One responsibility per module; dependencies point inward (`api/` → `services/` → `core/`).
- Inject external clients (the OpenAI client) via FastAPI dependencies so tests use a mock.
- Errors are typed and mapped to status codes at the HTTP boundary. Never `except Exception: pass`.

## Behavior contract (the part an agent most often guesses wrong)
- Valid body → **200** `{summary, word_count, model, request_id}`.
- Empty/whitespace `text` → **422**, **no** model call.
- `text` > 10,000 chars → **413**, **no** model call.
- Model error/timeout → **502** `{error, request_id}` — never a fake 200, never a leaked trace.
- `word_count` = whitespace-separated words in `summary`. Every response carries `request_id`.

## Non-negotiable guardrails
- **Never log the user's text** — metadata only (request id, length, status, latency, model).
- `OPENAI_API_KEY` comes from the environment — never hard-coded, returned, or logged.
- Exactly one model call per request (≤1 bounded retry), 30s timeout, stateless.

## Out of scope (v1)
No auth, no streaming, no caching, no database, no rate limiter, no UI, no extra endpoints.

## Testing
- The model client is **always mocked** — no live calls in CI.
- Every behavior above has a test; a privacy test proves the input text never appears in logs or errors.
