# Feature Specification: Summarization API

**Feature Branch**: `001-summarization-api`
**Created**: 2026-06-22
**Status**: Draft
**Input**: User description: "A single POST /summarize endpoint that turns a block of text into a concise summary from one model call, returned as JSON, with explicit behavior on empty/oversize input and model failure, and a strict no-logging-of-user-text rule."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Summarize a valid block of text (Priority: P1)

A client application sends a block of text and receives back a concise summary as JSON, so it can
show summaries to its users without embedding any model logic, prompts, or credentials of its own.

**Why this priority**: This is the entire reason the service exists; without it there is no product.
It is the minimal, independently shippable slice.

**Independent Test**: POST a valid block of text and confirm a 200 response whose body contains a
non-empty summary, a word count, the model identifier, and a request identifier.

**Acceptance Scenarios**:
1. **Given** a request with a non-empty block of text, **When** the client calls the endpoint,
   **Then** the response is 200 and contains a summary, a word count, a model name, and a request id.
2. **Given** a request that also specifies a desired maximum length, **When** the client calls the
   endpoint, **Then** the summary respects that length as a soft target.

### User Story 2 - Get a clear, safe error when something is wrong (Priority: P2)

A client receives a predictable, typed error (never a stack trace or an HTML page) when its input is
invalid or the upstream model is unavailable, so it can react programmatically.

**Why this priority**: A service that only handles the happy path is not production-usable; callers
must be able to distinguish their fault from ours and never see leaked internals.

**Independent Test**: Send empty text, oversize text, and simulate an upstream failure; confirm each
returns the documented status code with a typed error body carrying a request id.

**Acceptance Scenarios**:
1. **Given** empty or whitespace-only text, **When** the client calls the endpoint, **Then** the
   response is 422 and no model call is made.
2. **Given** text longer than the maximum allowed size, **When** the client calls the endpoint,
   **Then** the response is 413 and no model call is made.
3. **Given** the upstream model errors or times out, **When** the client calls the endpoint,
   **Then** the response is 502 with a typed error body and no leaked internals.

### User Story 3 - Trust that private text stays private (Priority: P1)

An operator can run this service knowing that the text users submit never appears in logs, traces,
or error output, so the service is safe to deploy against sensitive content.

**Why this priority**: A privacy leak is an incident, not a bug. This is a release blocker and is
treated with the same priority as the happy path.

**Independent Test**: Submit text containing a unique marker, exercise success and failure paths,
and confirm the marker appears in no log record and no response body.

**Acceptance Scenarios**:
1. **Given** any request, **When** it is processed, **Then** the submitted text appears in no log
   record, trace, or error message.
2. **Given** any response, success or error, **When** it is returned, **Then** it carries a request
   id, also surfaced as a response header.

### Edge Cases

- Text exactly at the maximum size boundary is accepted; one character over is rejected (413).
- A transient network blip on the single model call is retried at most once before failing as 502.
- A desired maximum length outside the allowed range is rejected as invalid input.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a request containing a block of text and an optional desired maximum
  summary length, and return a concise summary of that text.
- **FR-002**: System MUST return the summary as structured data containing the summary, a word count
  of the summary, the model identifier used, and a request identifier.
- **FR-003**: System MUST reject empty or whitespace-only text as invalid input and MUST NOT invoke
  the model in that case.
- **FR-004**: System MUST reject text larger than the maximum allowed size with a distinct
  "payload too large" outcome and MUST NOT invoke the model in that case.
- **FR-005**: System MUST return a typed error outcome when the upstream model fails or times out,
  without exposing provider internals, stack traces, or the submitted text.
- **FR-006**: System MUST attach a request identifier to every response, success or error, and also
  expose it as a response header.
- **FR-007**: System MUST ensure the reported word count equals the number of words in the returned
  summary.
- **FR-008**: When a desired maximum length is provided, System MUST treat it as a soft target the
  summary respects.
- **FR-009**: A successful request MUST result in exactly one logical model invocation (a single
  bounded retry on a transient network error counts as part of that one invocation).
- **FR-010**: System MUST NOT record the submitted text in any log, trace, error message, or stored
  artifact. Logging MUST be limited to metadata.
- **FR-011**: System MUST read provider credentials only from the environment and MUST NOT
  hard-code, return, or log them.

### Key Entities *(include if feature involves data)*

- **Summarize Request**: the input — the block of text to summarize and an optional desired maximum
  summary length.
- **Summarize Response**: the success output — the summary, its word count, the model identifier,
  and the request identifier.
- **Error**: the failure output — a human-safe error message and the request identifier.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A valid request returns a usable summary in a single response with no client-side
  post-processing required.
- **SC-002**: 100% of invalid-input requests (empty/whitespace, oversize) are rejected before any
  model invocation.
- **SC-003**: 100% of upstream failures are returned as the typed error outcome; 0% expose provider
  internals or the submitted text.
- **SC-004**: In an audit of captured logs across success and failure paths, the submitted text
  appears 0 times.
- **SC-005**: Every response — success or error — carries a request identifier.

## Assumptions

- The service runs on a trusted network in v1; caller authentication is out of scope.
- One summarization model is used; callers do not choose the model.
- The maximum input size and the model timeout are operational tunables, fixed for v1.
- Out of scope for v1: authentication, streaming, caching, persistence, rate limiting, and any UI.
