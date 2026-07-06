## Why

Client applications need summaries of text but should not each embed model logic, prompts, or
provider credentials. A single shared HTTP endpoint that wraps one model call removes that
duplication and centralizes the privacy and error-handling guarantees. There is no `summarization`
capability today; this change introduces it.

## What Changes

- Add a `POST /summarize` endpoint that returns a concise summary of submitted text from one model
  call.
- Define explicit behavior for empty/whitespace input (422), oversize input (413), and upstream
  model failure (502).
- Guarantee that the submitted text is never logged and that every response carries a request id.

## Capabilities

### New Capabilities
- `summarization`: accept a block of text over HTTP and return a concise, single-model-call summary
  as JSON, with explicit validation, error, privacy, and request-identity behavior.

### Modified Capabilities
<!-- none — this is a greenfield capability -->

## Impact

- New service package (FastAPI app, schemas, the summarizer, error handling, request-id middleware).
- New dependency on the OpenAI SDK; `OPENAI_API_KEY` required in the environment.
- New test suite that mocks the model client (no live network calls in CI).

---
