---
paths:
  - "src/summarizer_service/api/**/*.py"
  - "src/summarizer_service/services/**/*.py"
  - "src/summarizer_service/core/logging.py"
---

# API & model-call privacy rules

Claude Code loads this rule only when working on files matching `paths:` above. Note the format
difference from Cursor: Claude Code uses a **quoted YAML array** here, whereas Cursor `.mdc` files use
an unquoted comma-separated `globs:` string.

- The caller's `text` must never be written to a log, a trace, or an error message. Log metadata only:
  request id, character length, status code, latency, model name.
- `OPENAI_API_KEY` is read from the environment and never hard-coded, returned in a response, or logged.
- Map upstream failures to a `502` with `ErrorResponse(error, request_id)` — no stack trace, no raw
  provider error, no user text.
- This is a release blocker: if you cannot guarantee the above for a change, stop and flag it.
