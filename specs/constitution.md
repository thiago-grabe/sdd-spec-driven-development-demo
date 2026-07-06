# constitution.md — Project Rules

Every spec in this repo inherits these rules. Don't copy them — just reference this file.

---

## Stack

- **Python 3.12** · **FastAPI** · **Pydantic v2** · **OpenAI SDK** · `uvicorn` · `uv`
- Type hints on every function. Lint/format with `ruff` (must pass before done).
- Layers: `HTTP → domain → core`. No reverse imports. External clients injected as FastAPI dependencies (so tests can mock without patching globals).

## Security (non-negotiable)

- `OPENAI_API_KEY` from env only — never hard-coded, logged, or returned.
- **Never log user input.** Log metadata only: `request_id`, `input_length`, `status_code`, `latency_ms`, `model`.
- Never leak upstream errors to the client — map them to a typed `ErrorResponse`.
- When in doubt, don't log it.

## Testing

- The OpenAI client is **always mocked** in tests. No live network calls ever.
- Every acceptance criterion has at least one test.
- One dedicated privacy test: seeds a unique string in the input, asserts it never appears in any log record or response body.

## Definition of Done

- [ ] Every acceptance criterion has a passing test.
- [ ] `ruff check` and `ruff format` are clean.
- [ ] No user input in logs or responses (privacy test passes).
- [ ] OpenAPI schema matches the spec's interface contract.
- [ ] Spec still matches the code (no drift).

## The SDD loop

```
Specify (what+why) → Plan (how, agent proposes) → Tasks → Implement → Verify
```

No code until Specify + Plan are done and approved. Tasks are ordered by dependency. Verify against the requirements table — not against vibes.
