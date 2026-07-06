# Data Model: Summarization API

Phase 1 output. Three entities cross the API boundary; none is persisted (the service is stateless).

## SummarizeRequest (input)

| Field       | Type          | Rules                                                      | Maps to |
|-------------|---------------|-----------------------------------------------------------|---------|
| `text`      | string        | Required; min length 1 (empty/whitespace → 422). The 10,000-char cap is enforced in the route as 413, **not** as a schema `max_length`. | FR-001, FR-003, FR-004 |
| `max_words` | integer\|null | Optional; default 150; range 1–1000. Soft target only.    | FR-008 |

## SummarizeResponse (success output)

| Field        | Type    | Rules                                              | Maps to |
|--------------|---------|---------------------------------------------------|---------|
| `summary`    | string  | The model's concise summary.                      | FR-001 |
| `word_count` | integer | Whitespace-separated word count of `summary`.     | FR-007 |
| `model`      | string  | Identifier of the model used (e.g. `gpt-5.5`).    | FR-002 |
| `request_id` | string  | Per-request id; also the `X-Request-ID` header.   | FR-006 |

## ErrorResponse (failure output)

| Field        | Type   | Rules                                                       | Maps to |
|--------------|--------|------------------------------------------------------------|---------|
| `error`      | string | Human-safe message. Never contains provider internals, stack traces, or the submitted text. | FR-005, FR-010 |
| `request_id` | string | Per-request id; also the `X-Request-ID` header.            | FR-006 |

## Validation & status-code rules

- Empty/whitespace `text` → **422** (schema), no model call (FR-003).
- `len(text) > 10000` → **413** (route guard before any call) (FR-004).
- Upstream model error/timeout → **502** with `ErrorResponse`, no leak (FR-005).
- Valid request → **200** with `SummarizeResponse` (FR-001/002).
- Exactly one model invocation per success; ≤1 bounded retry on transient network error (FR-009).
