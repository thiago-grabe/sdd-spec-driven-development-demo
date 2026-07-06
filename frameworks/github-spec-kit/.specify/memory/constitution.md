<!--
SYNC IMPACT REPORT
Version change: (none) → 1.0.0
Modified principles: initial ratification
Added sections: Core Principles (I–V), Security & Privacy Constraints, Development Workflow, Governance
Templates requiring updates: ✅ spec-template.md ✅ plan-template.md ✅ tasks-template.md (consistent)
Follow-up TODOs: none
-->

# Summarization API Constitution

## Core Principles

### I. Spec-First, Code-Last
Every feature begins as a specification. No production code is written until `spec.md` (the what
and why), `plan.md` (the how), and `tasks.md` (the ordered units) exist and the Constitution Check
in `plan.md` passes. The specification is the source of truth; the chat is disposable. When the
implementation contradicts the spec, the spec is fixed first — then the code.

### II. Test-Backed Behavior (NON-NEGOTIABLE)
Every functional requirement carries at least one automated test, and the model provider is **always
mocked** in tests — the suite makes no live network calls and is deterministic, free, and runnable
offline in CI. "It looks right" is never sufficient; a green test that maps to an acceptance
criterion is.

### III. Contract Stability
Request, response, and error shapes are explicit and versioned. The generated OpenAPI schema MUST
match the contract in `contracts/`. A field that moves or a status code that changes is a breaking
change, not a tweak — callers depend on the shape.

### IV. Privacy by Default (NON-NEGOTIABLE)
User-supplied content is never logged, traced, returned in errors, or persisted. Logging is
metadata-only (request id, lengths, status, latency, model name). Secrets come only from the
environment and are never hard-coded, returned, or logged. On any uncertainty about whether
something is safe to emit, fail closed.

### V. Minimal Scope, Explicit Boundaries
Build exactly what the spec names and nothing more. Anything not required is out of scope and is
written down as such. Silence is not permission to add auth, caching, persistence, or extra
endpoints. New dependencies and patterns must be justified against this principle.

## Security & Privacy Constraints

- `OPENAI_API_KEY` (and any secret) is read from the environment only.
- The user's text never appears in logs, traces, error messages, analytics, or responses.
- Upstream provider errors are mapped to a typed error shape; raw bodies and stack traces never
  reach the client.
- The service is stateless: no sessions, no stored request/response data.

## Development Workflow

The five SDD stages run in order with three quality gates between them:
`/speckit.constitution` → `/speckit.specify` → `/speckit.clarify` → `/speckit.plan` →
`/speckit.checklist` → `/speckit.analyze` → `/speckit.tasks` → `/speckit.implement`.

- **Clarify** before planning: no `[NEEDS CLARIFICATION]` markers survive into `plan.md`.
- **Checklist** after specifying: the requirements checklist is the "unit tests for English" gate.
- **Analyze** before implementing: `spec.md`, `plan.md`, and `tasks.md` must be mutually consistent
  and every requirement must trace to a task. Violations of a `MUST` principle are CRITICAL and
  block implementation.

## Governance

This constitution supersedes feature specs where they conflict, unless a spec explicitly names the
principle it overrides and records the justification in its `plan.md` Complexity Tracking table.
Amendments require a version bump (semantic), an entry in the Sync Impact Report above, and a
re-check of the dependent templates. All PRs and reviews verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2026-06-22 | **Last Amended**: 2026-06-22
