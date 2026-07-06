---
inclusion: always
---

# Product

## What we are building
A **Summarization API** — a single HTTP endpoint, `POST /summarize`, that takes a block of text
and returns a concise summary produced by **exactly one** OpenAI model call, as JSON. It is the
simplest shape of the most common production LLM pattern: *a service in front of a model.*

## Who it is for
Any client (another service, a script, a UI) that needs a summary over HTTP **without** embedding
model logic, prompts, or API keys of its own.

## Why it exists
Centralize the model call, the prompt, and the credentials behind one typed, testable contract so
callers stay thin and the model provider can change without touching them.

## What success looks like
- A valid request returns a schema-valid summary in one round trip.
- Bad input is rejected with the *right* status code **before** any model call is made.
- Upstream failures surface as clean errors — never a fake success, never a leaked stack trace.
- The caller's text never lands in a log, a trace, or an error body.

## Explicitly not building (v1)
No authentication, no streaming, no caching, no database, no rate limiter, no web UI, no
caller-chosen model, no additional endpoints. One endpoint, one model call, stateless.
