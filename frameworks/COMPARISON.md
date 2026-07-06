# SDD frameworks compared — six ways to specify one system

## About this document

This is part of a **demo repository for Spec-Driven Development (SDD)** — building software by writing
artifacts precise enough that an AI coding agent can't guess wrong, rather than prompting ad-hoc. To
make the frameworks genuinely comparable, the demo specifies **one small system six different ways**,
one per SDD tool, on identical requirements. This file is the guided tour of those six — read it to
understand the landscape and to choose a framework for your own work.

The system in question is **the Summarization API**: a single endpoint, `POST /summarize`, that
returns a concise summary from exactly one OpenAI call (full contract in
[`../specs/spec.md`](../specs/spec.md)). Because every folder builds the *same* thing, every
difference below is a fact about the **tool**, not the problem.

This document compares the *tools*, not the feature: their philosophy, artifacts, workflow, and
trade-offs — so you can pick by how much rigor the work actually needs.

> New here? Read [`README.md`](./README.md) for the demo's purpose and the folder map, or
> [`../specs/`](../specs/) for the SDD method with no framework on top.

> **TL;DR.** They sit on one spectrum, sorted by how tightly the spec stays bound to the code.
> **Rules & context files** are the lightest (standing conventions, no per-feature spec). **Spec Kit,
> Kiro, OpenSpec, and BMAD** are full spec → plan → tasks workflows that differ in shape: Spec Kit is
> agent-agnostic and constitution-first; Kiro bakes it into an IDE with EARS requirements; OpenSpec is
> change-oriented for brownfield; BMAD assigns each phase to a different agent persona. **Tessl** is the
> radical end — the spec is the product and code is regenerated from it. No single winner: pick by
> whether you want the spec to *scaffold* the code or to *become* it.

---

## 1. At a glance

| | Rules & Context | Spec Kit | AWS Kiro | OpenSpec | BMAD | Tessl |
|---|---|---|---|---|---|---|
| **Category** | Standing context | Structured workflow | Agentic IDE | Change workflow | Multi-agent | Spec-as-source |
| **Spec ↔ code binding** | Loose (conventions) | Spec scaffolds code | Spec scaffolds code | Spec scaffolds code | Spec scaffolds code | Spec *is* the source |
| **Unit of work** | A rule file | A feature (`NNN-…/`) | A feature (`specs/<name>/`) | A change proposal | A story file | A logical code unit |
| **Constitution layer** | The rules themselves | `memory/constitution.md` | `steering/*.md` | `config.yaml` rules | `core-config.yaml` + docs | `tessl.json` + tiles |
| **Requirements style** | Prose bullets | `FR-###` + user stories | EARS (`WHEN…SHALL`) | `SHALL` + GIVEN/WHEN/THEN | FR/NFR + AC | Prose + `[@test]` links |
| **Greenfield / brownfield** | Either | Greenfield-leaning | Greenfield-leaning | **Brownfield-first** | Greenfield-leaning | Either |
| **Agent** | Any | Any (Copilot/Claude/Gemini) | Kiro IDE | Any | Any | Any (via MCP) |
| **Home** | Cursor / Claude / repo root | `.specify/` + `specs/` | `.kiro/` | `openspec/` | `docs/` + `_bmad/` | `*.spec.md` + `tessl.json` |
| **License / cost** | Free | Free / OSS | Paid beyond free tier | Free (MIT) | Free / OSS | Commercial; was beta |
| **Weight** | Lightest | Medium–heavy | Medium (IDE-integrated) | Light–medium | Heavy (orchestration) | Ambitious / least settled |

---

## 2. Philosophy — the one idea behind each

- **Rules & Context Files.** *Stop the agent re-guessing your conventions.* Standing instructions
  (Cursor `.cursor/rules/*.mdc`, `CLAUDE.md`, `AGENTS.md`) apply on every request. The lightest
  on-ramp — adjacent to SDD, not a replacement for specify/plan/tasks.
- **GitHub Spec Kit.** *Bolt a disciplined workflow onto the agent you already use.* A versioned
  **constitution** of immutable principles, then `spec → plan → tasks → implement` with checkpoints
  and validation checklists GitHub calls "unit tests for English." The de facto open-source standard.
- **AWS Kiro.** *Make the workflow the IDE.* Three approved-in-sequence documents — `requirements.md`
  in **EARS** notation, `design.md`, `tasks.md` — plus steering files and agent hooks, all native to
  the editor. Testable acceptance criteria by construction.
- **OpenSpec.** *Manage change, not just creation.* A strict state machine — **proposal → apply →
  archive** — that separates `specs/` (what's true now) from `changes/` (what's proposed). Purpose-built
  for codebases that already exist.
- **BMAD-METHOD.** *Turn a nebulous idea into a system with a team of agents.* Analyst → PM →
  Architect → PO → SM → Dev → QA, each a persona with its own role, producing a PRD, an architecture
  doc, and self-contained **story files** that carry context between fresh dev sessions.
- **Tessl.** *Bet that the spec is the product.* You maintain the spec; code and aligned tests are
  continuously regenerated to match. The radical end — humans own specs, AI owns code.

---

## 3. Artifacts & the granularity ladder

The frameworks differ mostly in **how finely they slice the work** and **where the "rules" live**.

| Framework | Rules live in | Feature spec | Plan / design | Task list |
|-----------|---------------|--------------|---------------|-----------|
| Rules & Context | the rule files | *(none — bring your own)* | *(none)* | *(none)* |
| Spec Kit | `memory/constitution.md` | `spec.md` (FR-###, user stories) | `plan.md`, `data-model.md`, `contracts/` | `tasks.md` (T001, `[P]`, `[US#]`) |
| AWS Kiro | `steering/*.md` | `requirements.md` (EARS) | `design.md` | `tasks.md` (`- [ ]` + `_Requirements:_`) |
| OpenSpec | `config.yaml` | `specs/<cap>/spec.md` (live) + delta | `changes/<name>/design.md` | `changes/<name>/tasks.md` |
| BMAD | `core-config.yaml` + docs | `docs/prd.md` (FR/NFR, epics) | `docs/architecture.md` | `docs/stories/*.md` (per story) |
| Tessl | `tessl.json` + tiles | `*.spec.md` (one per unit) | *(inline in the spec)* | *(derived by the agent)* |

**Reading the ladder:** the middle four all produce the classic trio (rules → spec → plan → tasks),
but slice differently — Spec Kit and Kiro per *feature*, OpenSpec per *change*, BMAD per *story*. Rules
& Context sit below the trio (conventions only); Tessl collapses it (the spec is the durable artifact,
the rest is regenerated).

---

## 4. Workflow & commands

| Framework | Drive it with | The loop |
|-----------|---------------|----------|
| Rules & Context | Edit `.mdc` / `CLAUDE.md`; agent auto-loads them | *(no loop — always-on context)* |
| Spec Kit | Slash commands in your agent | `/speckit.constitution → specify → clarify → plan → checklist → analyze → tasks → implement` |
| AWS Kiro | Kiro IDE (Spec sessions) | `requirements → design → tasks`, each **approved** before the next; Autopilot or Supervised execution |
| OpenSpec | `/opsx:*` commands + CLI | `propose → apply → verify → archive` (archive merges the delta into the live spec) |
| BMAD | Agent personas (`@pm`, `@architect`, `@sm`, `@dev`, `@qa`) | Planning (PRD + architecture, sharded) → dev cycle (SM drafts story → Dev implements → QA reviews) |
| Tessl | Prompt the agent; `spec-verification` skill | Write/evolve spec → generate code + tests → detect drift → regenerate |

All of them are the same five moves underneath — **constitution → specify → plan → tasks → implement &
verify** — with three quality gates (Clarify, Checklist, Analyze). The tools differ in ceremony, not in
the loop.

---

## 5. Benefits & disadvantages

### Rules & Context Files
- **Benefits:** zero-ceremony, works with any agent, instant day-one guardrails, composes with every
  framework below as the "constitution" layer.
- **Disadvantages:** not a per-feature spec — no plan/tasks/verification; easy to let it stand in for
  real specification and then watch the agent guess the *feature*. Standing context, not a contract.

### GitHub Spec Kit
- **Benefits:** agent- and IDE-agnostic; the versioned constitution + Constitution Check gate is
  genuinely rigorous; strong phase separation and traceability; the de facto OSS standard.
- **Disadvantages:** it's a process, not magic — you steer; specs can get long; the ceremony can feel
  heavy for a one-file change.

### AWS Kiro
- **Benefits:** integrated end to end; EARS makes acceptance criteria testable by construction;
  approval gates between phases; steering + hooks keep standards enforced automatically.
- **Disadvantages:** opinionated and tied to its own IDE; paid beyond a small free tier;
  greenfield-leaning.

### OpenSpec
- **Benefits:** the `specs/` vs `changes/` split is the cleanest model for evolving an existing system;
  lightweight; strict validation (every behavior needs a GIVEN/WHEN/THEN scenario); MIT / free.
- **Disadvantages:** deliberately light on big upfront design — change-oriented, not full greenfield
  planning; the delta/archive discipline is a learning curve.

### BMAD-METHOD
- **Benefits:** takes a vague idea all the way to a system; role separation catches gaps a single pass
  misses; story files carry context so fresh dev sessions start clean.
- **Disadvantages:** coordination overhead can outweigh the structure on small or fast-moving work;
  the most moving parts; V4 vs v6 layout churn.

### Tessl
- **Benefits:** the spec truly becomes the durable asset; drift detection built in; if the bet pays
  off, you maintain intent and regenerate implementation.
- **Disadvantages:** the most ambitious and least settled; commercial and was in beta; betting your
  workflow on regeneration is a real cultural shift.

---

## 6. How each handles the four ambiguity traps

The deck's four "blank → bug" traps, and where each framework forces you to fill them:

| Trap | Rules & Context | Spec Kit | Kiro | OpenSpec | BMAD | Tessl |
|------|-----------------|----------|------|----------|------|-------|
| **Goal creep** ("API" → platform) | A convention bullet | `spec.md` scope + user stories | `requirements.md` intro + stories | proposal `## Why/What` | PRD Goals + epics | spec `## Out of scope` |
| **"Handle errors gracefully"** | A rule ("never swallow") | `FR-###` + success criteria | EARS `IF…THEN…SHALL` | `SHALL` + scenario | AC (Given/When/Then) | requirement + `[@test]` |
| **Loose data contract** | Prose contract in `AGENTS.md` | `contracts/openapi.yaml` | `design.md` Data Models | scenario shapes | architecture Data Models | interface block in spec |
| **Silent guardrails** (log text, key) | A dedicated privacy rule | constitution NON-NEGOTIABLE | steering `tech.md` + hook | `config.yaml` rules | architecture Coding Standards | requirement + drift check |

Every framework *can* close every trap — the difference is how loudly it forces the question. Rules &
Context rely on you remembering; the workflow tools give the blank a named home you can't skip.

---

## 7. Choosing one

- **Any project, day one, any agent** → **Rules & Context Files.** Add them first regardless of what
  else you adopt; they're the constitution layer under everything.
- **You want the discipline but keep your agent/IDE** → **GitHub Spec Kit.** The safe default and the
  open-source standard.
- **You'll adopt an integrated IDE and love testable EARS criteria** → **AWS Kiro.** Best when you're
  greenfield and want one tool.
- **You're changing a system that already exists** → **OpenSpec.** The `specs/` vs `changes/` model is
  built for brownfield.
- **A nebulous idea that needs to become a whole system** → **BMAD.** Worth the orchestration overhead
  when scope is large and fuzzy; overkill for a one-endpoint change.
- **You're betting the spec is the product** → **Tessl.** The forward bet: maintain intent, regenerate
  code.

> The whole point survives the tool choice: **a spec precise enough the agent can't guess wrong, a
> plan before it touches a file, and verification against the spec you wrote.** Pick the lightest tool
> that forces those three on the work in front of you.
