# Spec-Driven Development — Demo

A worked example of **Spec-Driven Development (SDD)**: directing an AI coding agent with artifacts
precise enough that it *can't guess wrong*. The running example is **The Summarization API** — a
single `POST /summarize` endpoint that wraps **exactly one** OpenAI call. It is deliberately ordinary
(the most common production LLM pattern: a service in front of a model) yet ambiguity-sensitive at
every boundary, which makes it a sharp teaching case.

> Companion to the *Level Up with Experts* webinar **"Spec-Driven Development with AI Agents."** The
> two models in play are independent: **Claude Code is the coding agent** that writes the specs and
> the code; **the API it builds calls an OpenAI model (`gpt-5.5`) at runtime.**

## Quick start

```bash
# 1. Install dependencies
uv sync --extra dev

# 2. Set your OpenAI key
cp .env.example .env
# edit .env and set OPENAI_API_KEY=sk-...

# 3. Run the server
uv run uvicorn summarizer_service.main:app --reload

# 4. Call the endpoint
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Spec-Driven Development (SDD) is a software engineering discipline that inverts the typical AI-assisted workflow. Instead of prompting an agent to write code directly, the developer first produces a precise specification: a requirements table with numbered acceptance criteria, an interface contract defining exact request and response shapes, a constraints section listing what is explicitly out of scope, and an architecture document mapping every module to its responsibility. Only once these artifacts are approved does the agent proceed — first to a plan that traces each requirement to a file and a function, then to an ordered task list where each task has a testable done-when condition, and finally to implementation. The result is that the agent cannot guess wrong: every boundary condition is named, every edge case has a test, and every deviation from the spec is immediately visible. SDD also produces a living audit trail — the spec, plan, and tasks remain in the repository and serve as the ground truth against which future changes are verified.",
    "max_words": 60
  }'
```

The response looks like:

```json
{
  "summary": "A concise summary of your text.",
  "word_count": 7,
  "model": "gpt-5.5",
  "request_id": "3f2a1b4c-..."
}
```

Every response also carries an `X-Request-ID` header matching the `request_id` in the body.

## Running the tests

```bash
uv run pytest summarizer_service/tests/ -v
```

All 15 tests should pass. No live OpenAI call is ever made — the client is mocked via FastAPI's
`dependency_overrides`.

```bash
# Lint and format check
uv run ruff check .
uv run ruff format --check .
```

## API reference

### `POST /summarize`

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `text` | `string` | required | 1–10,000 characters; whitespace-only rejected |
| `max_words` | `integer` | `150` | Soft target passed to the model; range 1–1,000 |

**Status codes**

| Code | Meaning |
|------|---------|
| `200` | Summary returned |
| `413` | `text` exceeds 10,000 characters |
| `422` | Empty, whitespace-only, or otherwise invalid body |
| `502` | OpenAI call failed or timed out |

Every non-200 response body is `{"error": "<message>", "request_id": "<uuid>"}`.

### Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | yes | — | Injected as `SecretStr`; never logged |
| `MODEL` | no | `gpt-5.5` | OpenAI model name |
| `TIMEOUT_S` | no | `30` | Per-request timeout in seconds |
| `MAX_INPUT_CHARS` | no | `10000` | Hard cap on `text` length |
| `MAX_RETRIES` | no | `1` | Retries on transient network errors |

---

## The core idea

> Building software with AI agents isn't about writing code anymore. It's about writing a
> specification precise enough that the agent can't guess wrong, planning before the agent touches a
> file, and verifying the output against the spec you wrote — not against what you hoped it would do.

## The artifacts (read in this order)

| File | Role | SDD stage |
|------|------|-----------|
| [`specs/constitution.md`](./specs/constitution.md) | The **building code** — standing rules every spec inherits: stack, conventions, security & privacy, testing policy, definition of done, and the SDD loop + pre-flight checklist. Written once, reused. | 01 · Constitution |
| [`specs/spec.md`](./specs/spec.md) | The **one feature spec** in six sections: Context & Goal · Requirements & Acceptance Criteria · Interface & Data Contracts · Constraints/Guardrails/Out-of-Scope · **Plan** · **Tasks**. | 02 Specify · 03 Plan · 04 Tasks |
| [`specs/architecture.md`](./specs/architecture.md) | Component, sequence, decision-flow, and topology diagrams + the module map and invariants. Companion design detail the Plan points at. | supports 03 Plan |

Plan and Tasks live **inside** `spec.md` — one spec file, not three. The constitution is the only
*separate* standing file.

## The same project in six SDD frameworks

The [`frameworks/`](./frameworks/) directory specifies this **same** Summarization API six
different ways — one per point on the webinar's spectrum — so you can compare conventions on identical
requirements. Ordered lightest-touch → spec-as-source:

| Folder | Framework | Distinctive idea |
|--------|-----------|------------------|
| [`frameworks/rules-and-context/`](./frameworks/rules-and-context/) | **Rules & Context Files** | Standing conventions that steer any agent — Cursor rules, `CLAUDE.md`, `AGENTS.md` |
| [`frameworks/github-spec-kit/`](./frameworks/github-spec-kit/) | **GitHub Spec Kit** | Versioned constitution + phase gates; spec/plan/tasks split |
| [`frameworks/aws-kiro/`](./frameworks/aws-kiro/) | **AWS Kiro** | EARS requirements → design → tasks, built into the IDE; steering files + hooks |
| [`frameworks/openspec/`](./frameworks/openspec/) | **OpenSpec** | `specs/` (truth) vs `changes/` (proposals) + archive; brownfield-first |
| [`frameworks/bmad/`](./frameworks/bmad/) | **BMAD-METHOD** | Agile AI agent team → PRD, architecture, story files |
| [`frameworks/tessl/`](./frameworks/tessl/) | **Tessl** | Spec is the source of truth; code regenerable; library-spec registry |

📄 [`frameworks/COMPARISON.md`](./frameworks/COMPARISON.md) — full comparison: philosophy, artifacts,
workflow, benefits, disadvantages, and how to choose · 📁 [`frameworks/README.md`](./frameworks/README.md)
— the index.

## The SDD loop

```
Constitution ─▶ Specify ─▶ Plan ─▶ Tasks ─▶ Implement & Verify ─▶ (loop back)
                   │          │        │
               Clarify    (approve)  Analyze     ◀── three quality gates
```

- **Clarify** — resolve every ambiguity before planning.
- **Checklist** — validate the spec is complete (the pre-flight checklist in the constitution §8).
- **Analyze** — confirm constitution, spec, plan, and tasks are consistent before any code is
  written. Every acceptance criterion (R1–R9) traces to a task and a test.

The agent never touches code until Constitution, Specify, and Plan are complete and approved.

## Status

Implementation complete. The full spec (§1–§6) and all application code live in this repo.
15 tests pass, covering every acceptance criterion R1–R9. No live OpenAI calls in the test suite.
