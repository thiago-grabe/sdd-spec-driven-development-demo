## Context

Greenfield single-endpoint service. The only external dependency is the OpenAI API. The design must
make the one model call mockable so CI never touches the network, and must guarantee the user's text
cannot leak into logs or error output.

## Goals / Non-Goals

**Goals:**
- Exactly one model call per successful request; reject invalid input before any call.
- Typed, stable request/response/error contracts and status codes.
- Metadata-only logging; submitted text never logged.

**Non-Goals:**
- Authentication, streaming, caching, persistence, rate limiting, multiple models, or a UI.

## Decisions

- **Layered package**: `api/` (routes + error mapping), `services/summarizer.py` (the one call),
  `models/schemas.py` (Pydantic), `core/` (config + metadata-only logging). The model call is
  isolated so tests inject a mock client via a FastAPI dependency.
- **10k cap as a route-level 413**, not a Pydantic `max_length` (which would wrongly surface as 422).
- **Request-id middleware** stamps every response body and the `X-Request-ID` header.
- **Bounded resilience**: 30s timeout, at most one retry on a transient network error, then 502.

## Risks / Trade-offs

- Model non-determinism → tests assert contract and behavior (schema-valid, status codes, privacy),
  not exact summary wording; the live model is treated as a flaky dependency (timeout + 1 retry).
- A 10k hard cap may reject legitimately long inputs → acceptable for v1; revisit if needed.
