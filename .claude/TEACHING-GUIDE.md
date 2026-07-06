# Teaching Guide — How to Read, Create, and Explain Every File

A presenter's companion to the four framework folders. For **each file** in each framework you get:

- **What it is** — its job in one line.
- **How to read it** — what to look at first, and what each part means.
- **How to create it** — the order to fill it in, and the rule that keeps it honest.
- **Say this out loud** — the sentence that lands it with a technical audience.

> Through-line for the whole talk: **name it, plan it, verify it.** Every file below is one of those
> three moves. When you explain a file, tell the room *which* move it is.

How to use this guide:
1. Skim **§0** for the one mental model that spans all four.
2. Teach **one** framework deeply (Spec Kit or OpenSpec are the easiest first), then use the
   **Rosetta stone (§6)** to show the others are the same idea in different clothing.
3. Use the **reading order** at the top of each section as your demo path — open files in that order.

---

## §0 — The shared mental model (teach this once)

Every spec-driven framework is the same five moves; the files are just where each move is written
down:

| Move | Question it answers | The "name it / plan it / verify it" bucket |
|------|---------------------|--------------------------------------------|
| **Constitution / Rules** | What's true on *every* task? | name it (once) |
| **Specify** | What & why for *this* feature? | name it |
| **Plan / Design** | How will we build it? | plan it |
| **Tasks / Stories** | In what small, ordered, checkable steps? | plan it |
| **Implement & Verify** | Did it actually meet the spec? | verify it |

The single sentence to repeat: *"A spec precise enough the agent can't guess wrong, a plan before it
touches a file, and verification against the spec — not against what you hoped."*

The four frameworks differ on **where** these live and **how strict** the format is — that's the
whole comparison. Keep [`COMPARISON.md`](./COMPARISON.md) open in the other tab.

---

## §1 — GitHub Spec Kit

**Folder:** [`github-spec-kit/`](./github-spec-kit/)
**One-liner to open with:** *"GitHub's take: a versioned constitution is law, and every plan is
checked against it at a gate before any code is written."*
**Reading order for a demo:** `constitution.md` → `spec.md` → `plan.md` → `data-model.md` →
`contracts/openapi.yaml` → `checklists/requirements.md` → `tasks.md` → (`quickstart.md` to verify).

### `.specify/memory/constitution.md`
- **What it is:** the project's non-negotiable principles — versioned, amended deliberately, obeyed
  on every feature.
- **How to read it:** start at the `## Core Principles` list (I–V). Note the two marked
  `(NON-NEGOTIABLE)` — those become CRITICAL gate failures. Scroll to the bottom: the
  `**Version** | **Ratified** | **Last Amended**` line and the HTML `SYNC IMPACT REPORT` comment at
  the very top are how Spec Kit tracks amendments.
- **How to create it:** name 3–7 principles (one bold title + a paragraph each), add any standing
  constraints (security/privacy), describe the workflow + gates, then a `## Governance` section that
  says "this supersedes specs unless explicitly overridden." Stamp a semantic version.
- **Say this out loud:** *"This is the building code. You don't re-argue 'never log user text' on
  every feature — you write it once, here, and every plan gets checked against it."*

### `specs/001-summarization-api/spec.md`
- **What it is:** the WHAT and WHY of one feature — deliberately **non-technical**.
- **How to read it:** notice there are **no status codes, field types, or framework names** in the
  prose. It's `## User Scenarios` (with **Priority: P1/P2** and Given/When/Then), `## Requirements`
  (`FR-001…` each independently testable), `## Success Criteria` (`SC-001…`, technology-agnostic),
  and `## Assumptions`. The folder is numbered `001-` (sequential feature id).
- **How to create it:** write the user stories first (priority-ordered, with acceptance scenarios),
  derive one `FR-###` per testable behavior, then measurable `SC-###`. If you can't say it without a
  framework name, it belongs in the plan, not here. Park unknowns as `[NEEDS CLARIFICATION: …]`
  (max 3) and resolve them in `/speckit.clarify`.
- **Say this out loud:** *"A stakeholder who's never seen our stack could read this and agree. The
  word 'FastAPI' appearing here would be a bug — that's a how, and how lives downstairs."*

### `specs/001-summarization-api/plan.md`
- **What it is:** the HOW — and the **gate**.
- **How to read it:** `## Technical Context` (now the stack appears: Python 3.12, FastAPI…), then the
  star of the file — `## Constitution Check`, a pass/fail table run *before* design and again after.
  `## Project Structure` shows the chosen source tree; `## Complexity Tracking` is **empty on
  purpose** — a filled row would mean "we knowingly violated a principle, here's why."
- **How to create it:** fill Technical Context, run each constitution principle as a row (PASS/FAIL),
  pick a structure option, and only write in Complexity Tracking if you must justify a violation.
- **Say this out loud:** *"This is the checkpoint. If the plan violates a constitution principle, the
  agent either fixes the approach or writes down the justification — it can't quietly proceed."*

### `specs/001-summarization-api/data-model.md`
- **What it is:** the field-level contract for the entities crossing the boundary.
- **How to read it:** three tables (Request / Response / Error) with a **Maps to** column tying each
  field back to an `FR-###`. The note "10k cap is a 413 route guard, **not** a `max_length`" is the
  teachable subtlety — wrong choice would make oversize input a 422.
- **How to create it:** one table per entity; every field gets type, rules, and the requirement it
  serves. If a field maps to no requirement, question it.
- **Say this out loud:** *"Every field traces to a requirement. No orphan fields, no orphan
  requirements — that traceability is what the Analyze gate checks."*

### `specs/001-summarization-api/contracts/openapi.yaml`
- **What it is:** the machine-readable HTTP contract — the thing the generated OpenAPI must match.
- **How to read it:** the `responses:` block enumerates `200/413/422/502`, each with the
  `X-Request-ID` header and a schema `$ref`. This is Principle III (Contract Stability) made
  concrete.
- **How to create it:** pin every status code the spec names and reference the same schemas as
  `data-model.md`. Treat a moved field or changed code as a breaking change.
- **Say this out loud:** *"This file is the promise to callers. 'Verify against the spec' literally
  means: does the running app's `/openapi.json` still equal this?"*

### `specs/001-summarization-api/checklists/requirements.md`
- **What it is:** the **Checklist** quality gate — "unit tests for English."
- **How to read it:** three groups (Content Quality / Requirement Completeness / Feature Readiness).
  Every box checks the **spec**, not the code — e.g. "No [NEEDS CLARIFICATION] markers remain."
- **How to create it:** auto-generated by `/speckit.specify`; you tick boxes to confirm the spec is
  complete *before* planning. A box you can't tick is a gap to fix now, cheaply.
- **Say this out loud:** *"These aren't tests of the software — they're tests of the writing. If you
  can't tick them, you're about to let the agent guess."*

### `specs/001-summarization-api/tasks.md`
- **What it is:** the plan decomposed into small, ordered, individually-verifiable units.
- **How to read it:** the `## Format` legend explains the codes: `T001` ids, `[P]` = parallel-safe
  (different files), `[US1]` = which user story. Phases run Setup → Foundational → per-User-Story →
  Polish, with **Checkpoints** where a story is independently shippable.
- **How to create it:** group by phase; one behavior per task; tag the story and add `[P]` only when
  the task touches different files with no dependency. Order so the MVP (US1) lands first.
- **Say this out loud:** *"Small, ordered, tagged. The agent does one, you verify it against its FR,
  then the next — instead of a big-bang you can't review."*

### `quickstart.md`
- **What it is:** the run-and-verify script — the **verify** move.
- **How to read it / create it:** `uv run uvicorn …`, then a `curl` per acceptance scenario, then
  `pytest` + `ruff`, then the "Done when" list. Each curl maps to a user story.
- **Say this out loud:** *"This is how we check it works — by reproducing every acceptance scenario,
  not by eyeballing the happy path."*

**Common mistakes to call out:** letting tech leak into `spec.md`; leaving Complexity Tracking
implicitly empty without saying why; writing tasks that touch the same file but marking them `[P]`.

---

## §2 — Tessl

**Folder:** [`tessl/`](./tessl/)
**One-liner to open with:** *"The radical one: the spec is the durable source of truth and the code
is a regenerable artifact. The spec owns the files."*
**Reading order for a demo:** `tessl.json` → `specs/summarize.spec.md` (top frontmatter → interface
block → requirement+`[@test]` lines).

### `tessl.json`
- **What it is:** the project manifest — which workflow tile and which **library usage-spec tiles**
  the project depends on.
- **How to read it:** `dependencies` pins the SDD workflow tile; `tiles` pins versioned specs for
  libraries (`tessl/pypi-fastapi`, `tessl/pypi-openai`) so the agent reads accurate API docs instead
  of hallucinating. The `describes` field links a tile to a package URL.
- **How to create it:** `tessl install <tile>` writes these entries; pin the library tiles your code
  calls.
- **Say this out loud:** *"This is the bit no other framework has — a registry of versioned, accurate
  library specs. The agent isn't guessing the OpenAI SDK's shape from stale training data; it's
  reading a pinned spec."*

### `specs/summarize.spec.md`
- **What it is:** the whole feature — Tessl's one spec **per logical code unit**.
- **How to read it, top to bottom:**
  - **Frontmatter** (`---`): `name`, `description`, and the load-bearing `targets:` — the relative
    paths to the implementation files this spec *owns*. "This spec governs these files."
  - **Interface code block:** a `python` block with the signatures (the models, `summarize(...)`,
    `post_summarize(...)`). It's the contract in code, not prose.
  - **Requirements:** plain English under `##` headings, and next to each line an **inline
    `` `[@test] ../tests/…` `` link** binding that behavior to the test that proves it.
- **How to create it:** write the frontmatter (point `targets:` at the files), drop the interface
  block, then write requirements as short prose lines — and add a `[@test]` link beside each one.
  Group related requirements under headings (Happy path / Validation / The one model call / Privacy).
- **Say this out loud:** *"Read the targets line: this spec owns these files. Read the `[@test]`
  links: every requirement is wired to its proof. When the code drifts from this, Tessl's
  spec-verification skill flags it — that's the chronic SDD failure mode solved."*

**Common mistakes to call out:** writing one giant spec for many code units (Tessl is one-per-unit);
forgetting the `[@test]` link (then there's nothing to verify drift against); confusing this
GA skills format with the closed-beta `@generate` Framework syntax.

---

## §3 — OpenSpec

**Folder:** [`openspec/`](./openspec/)
**One-liner to open with:** *"A Git-native ledger: `specs/` is what's TRUE now, `changes/` is what
you're PROPOSING. You never edit the truth directly — you propose a change and archive it in."*
**Reading order for a demo:** `config.yaml` → `changes/add-summarization-api/proposal.md` →
`design.md` → the **delta** `changes/.../specs/summarization/spec.md` → `tasks.md` → then the
**merged result** `specs/summarization/spec.md`.

### `openspec/config.yaml`
- **What it is:** project context + per-artifact rules, injected into every generation.
- **How to read it:** the `context:` block (stack, privacy, testing) is prepended to all AI
  instructions; the `rules:` block is scoped per artifact (e.g. spec rules: "SHALL/MUST, every
  requirement needs a scenario, four-hashtag scenarios").
- **How to create it:** put the standing facts in `context:` and the format laws in `rules:`. This is
  OpenSpec's lightweight stand-in for a constitution.
- **Say this out loud:** *"OpenSpec has no heavyweight constitution — its rules live here, and they
  get injected so the agent can't forget them."*

### `changes/add-summarization-api/proposal.md`
- **What it is:** the *why* of a change — the entry point of the propose→archive lifecycle.
- **How to read it:** it starts at `## Why` (no title line by convention), then `## What Changes`,
  then the load-bearing `## Capabilities` (New / Modified) — that section is the contract that says
  which delta spec files must exist — then `## Impact`.
- **How to create it:** state the motivation, list what changes, and under Capabilities name the
  capability in kebab-case (`summarization`); each new capability requires a matching delta spec.
  Keep it 1–2 pages; the *how* goes in design.
- **Say this out loud:** *"A change is a self-contained proposal. This file is the pitch — why, and
  which capabilities it touches. Reviewers approve this before anyone builds."*

### `changes/add-summarization-api/design.md`
- **What it is:** the technical decisions for the change (optional — only when there's real
  complexity).
- **How to read it / create it:** `## Context`, `## Goals / Non-Goals`, `## Decisions`,
  `## Risks / Trade-offs`. For a one-endpoint change it's short; for a cross-cutting one it's where
  contradictions surface early.
- **Say this out loud:** *"Design is where the 'how' lives, and it's optional — skip it for a trivial
  change, write it when a decision needs to be argued before code."*

### `changes/add-summarization-api/specs/summarization/spec.md` (the **delta**)
- **What it is:** the *change to the spec* — not a full rewrite, only what's changing.
- **How to read it:** the top-level headers are **delta operators**: `## ADDED Requirements`
  (also `MODIFIED` / `REMOVED` / `RENAMED`). Under them, `### Requirement: <name>` (RFC-2119
  SHALL/MUST) and **`#### Scenario:`** blocks with `- **WHEN** / - **THEN**` bullets. **Exactly four
  hashtags** on Scenario — three fails silently at archive.
- **How to create it:** for a new capability, everything goes under `## ADDED Requirements`; give each
  requirement at least one scenario (validation enforces this). For an edit, copy the **full**
  requirement block under `## MODIFIED Requirements` and change it.
- **Say this out loud:** *"Read the header: ADDED. This file doesn't restate the system — it states
  the diff. That's why two changes can be in flight at once without colliding."*

### `changes/add-summarization-api/tasks.md`
- **What it is:** the implementation checklist for the change.
- **How to read it / create it:** numbered groups (`## 1. …`) of `- [ ]` checkboxes. The `apply`
  step ticks these; tasks not in `- [ ]` form are invisible to tracking.
- **Say this out loud:** *"Plain checkboxes — but the tooling parses them, so format discipline isn't
  cosmetic."*

### `specs/summarization/spec.md` (the **live spec**)
- **What it is:** the established source of truth — the result of **archiving** the change (its delta
  merged in).
- **How to read it:** same `## Purpose` + `## Requirements` + `### Requirement:` + `#### Scenario:`
  structure as the delta, but with no `ADDED/MODIFIED` operators — it's settled truth. Compare it
  side-by-side with the delta to show the merge.
- **How to create it:** you don't hand-write this in practice — `openspec archive` generates it from
  the delta. (It's committed here so the lifecycle is visible end-to-end.)
- **Say this out loud:** *"Watch what archive does: the ADDED block in the change becomes plain
  requirements here. The proposal is the diff; this is the codebase's living spec after merge."*

**Common mistakes to call out:** three hashtags on a scenario (silent failure); a requirement with no
scenario (fails `--strict`); editing the live `specs/` file directly instead of via a change;
partial MODIFIED blocks (lose detail at archive).

---

## §4 — BMAD-METHOD

**Folder:** [`bmad/`](./bmad/)
**One-liner to open with:** *"Not a spec format — an agile AI *team*. Personas (PM, Architect, Scrum
Master, Dev, QA) produce a PRD, an architecture doc, and self-contained story files."*
**Reading order for a demo:** `core-config.yaml` → `docs/prd.md` → `docs/architecture.md` →
`docs/stories/1.1.*.md` → `docs/stories/1.2.*.md`.

### `core-config.yaml`
- **What it is:** the wiring — where artifacts live and which files the Dev agent always loads.
- **How to read it:** `prd`/`architecture` blocks (file paths + `sharded: true`), and the key one,
  `devLoadAlwaysFiles` (coding-standards, tech-stack, source-tree) — the always-in-context files for
  every dev session. `slashPrefix: BMad` sets the command prefix.
- **How to create it:** generated by `npx bmad-method install`; you tune paths and the
  always-load list.
- **Say this out loud:** *"This is how BMAD does context engineering — it guarantees the Dev agent
  always has the standards and the source tree in front of it, nothing more."*

### `docs/prd.md` (written by the PM persona)
- **What it is:** the product requirements — goals, requirements, epics, and stories.
- **How to read it:** `## Goals and Background Context`, then `## Requirements` split into
  **`### Functional`** (`FR1…`) and **`### Non Functional`** (`NFR1…`), `## Technical Assumptions`,
  the `## Epic List`, then each `## Epic N` containing `### Story N.M` with `#### Acceptance Criteria`
  in Given/When/Then. The `## Checklist Results Report` is the PO's sign-off.
- **How to create it:** goals → FR/NFR → technical assumptions → list epics → expand each epic into
  stories with acceptance criteria. Keep one MVP epic for a small build (we have exactly one).
- **Say this out loud:** *"Notice FR and NFR are separated, and every story has Given/When/Then
  acceptance criteria. This is the plan the whole team works from."*

### `docs/architecture.md` (written by the Architect persona)
- **What it is:** the technical source of truth — stack, data models, source tree, coding standards.
- **How to read it:** `## Tech Stack` table, `## Data Models`, `## Source Tree`, and
  `## Coding Standards` (this is what gets sharded into `devLoadAlwaysFiles`). The high-level diagram
  shows the same lifecycle as the other frameworks.
- **How to create it:** derive it from the PRD; make the coding standards explicit because the Dev
  agent loads them on every story.
- **Say this out loud:** *"The architecture doc isn't decoration — its coding-standards section is
  literally loaded into every dev session via core-config."*

### `docs/stories/1.1.project-scaffold.md` and `1.2.summarize-endpoint.md` (the SM drafts)
- **What it is:** BMAD's signature artifact — the **story file**, the unit of work, self-contained so
  a fresh agent session needs nothing else.
- **How to read it, section by section** (point at each):
  - `## Status` — the lifecycle flag (`Draft → Approved → InProgress → Review → Done`). 1.1 is
    `Approved`, 1.2 is `Draft`.
  - `## Story` — the As-a / I-want / so-that.
  - `## Acceptance Criteria` — numbered, each tagged back to an `FR`/`NFR`.
  - `## Tasks / Subtasks` — nested `- [ ]` checkboxes, each tagged `(AC: #)`.
  - `## Dev Notes` (+ `### Testing`) — architecture context *extracted for this story only*; the Dev
    agent reads this and does **not** go spelunking the whole repo.
  - `## Change Log`, `## Dev Agent Record` (Agent Model Used / File List / etc.), `## QA Results` —
    the **ownership** bands: SM writes the top, Dev fills its Record, QA fills its Results.
- **How to create it:** the SM drafts it from the sharded PRD + architecture, copying just-enough
  context into Dev Notes and tagging every task to an AC. Leave the Dev/QA sections as empty
  placeholders — those agents own them.
- **Say this out loud:** *"This is the magic of BMAD — the story carries its own context. A brand-new
  agent chat can implement story 1.2 with nothing but this file open, because the SM front-loaded the
  relevant architecture into Dev Notes. And notice the ownership: SM writes the ask, Dev writes the
  record, QA writes the verdict."*

**Common mistakes to call out:** confusing V4 (this folder: `bmad-core/`, personas Mary/John/Winston/
Bob/James/Sarah/Quinn, `docs/stories/{epic}.{story}.{slug}.md`) with v6 (`_bmad/`, QA+SM folded into
the Dev persona, `_bmad-output/`); a Dev agent editing the Acceptance Criteria (immutable after
approval); story Dev Notes that just say "see the architecture doc" (defeats context engineering).

---

## §5 — A 60-second demo choreography (any framework)

When you screen-share, narrate the **move**, not the syntax:

1. Open the **rules** file → *"Name-it-once: the standing law."*
2. Open the **spec/requirements** → *"Name-it: what & why, testably."* Point at one acceptance
   criterion.
3. Open the **plan/design** → *"Plan-it: the how, and the gate."* Point at the gate/decision.
4. Open the **tasks/story** → *"Plan-it: small, ordered, checkable."* Point at one task ↔ one AC.
5. Open the **verify** artifact (quickstart / `[@test]` link / scenario / QA Results) → *"Verify-it:
   against the spec, not the vibe."*

Then flip to the **same acceptance criterion** ("empty input → 422, no model call") in each framework
and show it's the same idea, differently encoded. That single criterion across four files is the most
persuasive 60 seconds in the talk.

---

## §6 — Rosetta stone (the same concept, four dialects)

| Concept | Spec Kit | Tessl | OpenSpec | BMAD |
|---|---|---|---|---|
| Standing rules | `.specify/memory/constitution.md` | `rules/` in the SDD tile | `config.yaml` (`context`+`rules`) | `architecture/coding-standards.md` + `core-config.yaml` |
| What & why | `spec.md` (`FR-###`, user stories) | `*.spec.md` requirement lines | `### Requirement:` + `#### Scenario:` | `prd.md` (`FR`/`NFR`, stories) |
| Interface/contract | `data-model.md` + `contracts/openapi.yaml` | interface code block + `targets:` | embedded in requirement scenarios | `architecture.md` Data Models / API |
| The how (plan) | `plan.md` (+ Constitution Check gate) | (the spec is the plan) | `design.md` | `architecture.md` |
| Ordered work | `tasks.md` (`T###`, `[P]`, `[US#]`) | (implicit) | `tasks.md` (`- [ ]`) | story `Tasks / Subtasks` |
| Verify | `quickstart.md`, Analyze gate | inline `[@test]` + drift check | `validate --strict`, `/opsx:verify` | `QA Results`, story status |
| "Done / merged" state | merged PR | regenerate / verified | `archive` → live `specs/` | story → `Done` |

**The teaching payoff:** read this table top to bottom for any column and you've described that
framework; read it left to right for any row and you've shown the audience that *the discipline is
universal — only the filing system changes.*

---

*Pair this guide with [`COMPARISON.md`](./COMPARISON.md) (why you'd pick each) and the framework-free
[`../specs/`](../specs/) (the method by hand). Conventions verified against each project's docs in
2026; re-check each folder's README for the current CLI commands.*
