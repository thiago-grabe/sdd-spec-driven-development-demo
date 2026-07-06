# Prompt 02 — Write the Task List (spec.md §6)

> Run this after `01-generate-plan.md` has been executed and the Plan has been approved.

Read these files first:
- `specs/constitution.md`
- `specs/spec.md` (including the approved §5 Plan)
- `specs/architecture.md`

---

## Before writing tasks, check

- Every R1–R9 criterion maps to at least one task.
- No task imports from a module created by a later task.
- Module names match `architecture.md`.
- No constitutional rule is violated (no hard-coded keys, no live calls in tests, no user text in logs).

If anything fails, fix it before proceeding.

---

## What to produce

Append `## 6. Tasks` to `specs/spec.md`. Each task uses this format:

```
### T<N>: <imperative title>

| Field | Value |
|-------|-------|
| Files | files created or modified |
| Satisfies | R-number(s) or "scaffold" |
| Done when | exact testable condition |
| Test | function name or "n/a" |

2–4 sentences: what to build, key constraints, how to verify.
```

---

## Required tasks (in this order)

| Task | Creates | Plan section |
|------|---------|-------------|
| T1 | `pyproject.toml`, `.env.example`, package `__init__` files | §5.1 |
| T2 | `models/schemas.py` — the three Pydantic models | §5.1 |
| T3 | `exceptions.py` — `PayloadTooLargeError`, `SummarizerError` | §5.4 |
| T4 | `core/config.py` — `Settings` | §5.6 |
| T5 | `core/logging.py` — metadata-only `log_request()` | §5.7 |
| T6 | `services/summarizer.py` — one call, timeout, retry | §5.5 |
| T7 | `api/errors.py` — exception handlers for 413/422/502 | §5.4 |
| T8 | `api/routes.py` — `POST /summarize` route | §5.2, §5.3 |
| T9 | `main.py` — `create_app()`, middleware, handler registration | §5.3 |
| T10a | `tests/conftest.py` — shared fixtures | §5.8 |
| T10b | `tests/test_schemas.py` — R6 | §5.8 |
| T10c | `tests/test_summarizer.py` — R8, R9 | §5.8 |
| T10d | `tests/test_summarize_route.py` — R1–R5, R7 | §5.8 |

After appending the task list to `spec.md`, **stop**. Don't implement yet.
