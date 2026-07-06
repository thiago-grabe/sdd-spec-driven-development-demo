# Spec-Driven Development — Demo

A worked example of **Spec-Driven Development (SDD)**: directing an AI coding agent with artifacts
precise enough that it *can't guess wrong*. The running example is **The Summarization API** — a
single `POST /summarize` endpoint that wraps **exactly one** OpenAI call. It is deliberately ordinary
(the most common production LLM pattern: a service in front of a model) yet ambiguity-sensitive at
every boundary, which makes it a sharp teaching case.

> Companion to the *Level Up with Experts* webinar **"Spec-Driven Development with AI Agents."** The
> two models in play are independent: **Claude Code is the coding agent** that writes the specs and
> the code; **the API it builds calls an OpenAI model (`gpt-5.5`) at runtime.**

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

The specification stack is complete and the **Tasks** section (`spec.md` §6) is ready to implement
task-by-task. No application code has been written yet — by design, this repo demonstrates the part
*before* the agent starts typing.
