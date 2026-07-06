# Requirements Document

## Introduction

The Summarization API is a single HTTP endpoint, `POST /summarize`, that accepts a block of text and
returns a concise summary produced by **exactly one** OpenAI model call, as JSON. It is the simplest
shape of the most common production LLM pattern: a service in front of a model. Any client can obtain
a summary over HTTP without embedding model logic, prompts, or API keys of its own. The service is
stateless, makes at most one model call per request, rejects bad input before spending a model call,
and must never persist or log the caller's text.

## Requirements

### Requirement 1: Summarize valid text

**User Story:** As an API client, I want to submit a block of text and receive a concise summary as
JSON, so that I can summarize content without embedding model logic or credentials of my own.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /summarize with a non-empty `text` field THEN the system SHALL return HTTP 200 with a JSON body containing `summary`, `word_count`, `model`, and `request_id`.
2. WHEN the system returns a summary THEN the system SHALL set `word_count` to the number of whitespace-separated words in `summary`.
3. WHERE the request includes a `max_words` value the system SHALL pass it to the model as a soft target length.
4. WHEN a valid request is processed successfully THEN the system SHALL make exactly one call to the OpenAI client, where at most one bounded retry on a transient network error counts as part of the same logical call.

### Requirement 2: Reject invalid input without calling the model

**User Story:** As an operator, I want malformed or oversized requests rejected before any model call,
so that the service never spends money or latency on input it should not process.

#### Acceptance Criteria

1. IF the `text` field is empty or contains only whitespace THEN the system SHALL return HTTP 422 and SHALL NOT call the OpenAI client.
2. IF the `text` field is longer than 10,000 characters THEN the system SHALL return HTTP 413 and SHALL NOT call the OpenAI client.
3. WHEN the system rejects input for validation reasons THEN the system SHALL return a JSON body containing `error` and `request_id`.

### Requirement 3: Handle upstream model failures safely

**User Story:** As an API client, I want upstream failures reported as clean errors, so that a failure
never looks like a success and never exposes internal details.

#### Acceptance Criteria

1. IF the OpenAI call errors or exceeds the 30-second timeout THEN the system SHALL return HTTP 502 with a JSON body containing `error` and `request_id`.
2. WHEN the system returns a 502 THEN the system SHALL NOT include a stack trace, the provider's raw error, or the caller's text in the response.
3. IF a transient network error occurs on the model call THEN the system SHALL retry at most once before returning 502.

### Requirement 4: Make every response traceable

**User Story:** As an operator, I want every response correlated to a request id, so that I can trace
a call through the logs without ever seeing the user's text.

#### Acceptance Criteria

1. WHEN the system returns any response, whether success or error, THEN the system SHALL include a `request_id` in the body.
2. WHEN the system returns any response THEN the system SHALL set the `X-Request-ID` response header to the same value.

### Requirement 5: Protect user text and secrets

**User Story:** As a data owner, I want the caller's text and the API key kept out of all logs and
responses, so that using the service can never cause a privacy or credential incident.

#### Acceptance Criteria

1. WHILE processing any request the system SHALL keep the caller's text out of all logs, traces, and error messages, logging metadata only (request id, length, status, latency, model name).
2. the system SHALL read `OPENAI_API_KEY` from an environment variable and SHALL NOT hard-code it, return it, or write it to a log.
3. WHEN an uncertainty exists about whether a value is safe to log or return THEN the system SHALL NOT log or return it.

### Requirement 6: Operate within cost and latency guardrails

**User Story:** As an operator, I want strict per-request limits, so that a single request cannot run
up an unbounded bill or hang indefinitely.

#### Acceptance Criteria

1. the system SHALL make at most one model call per request (plus at most one bounded retry).
2. the system SHALL apply a 30-second timeout to the model call.
3. the system SHALL remain stateless, persisting no request or response data between calls.
