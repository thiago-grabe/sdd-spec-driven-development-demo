# Spec-Driven Development Frameworks — A Comparison

Four ways to specify and build the **same** service — the Summarization API (`POST /summarize`, one
OpenAI call, with 422/413/502 behavior, request ids, and a strict no-logging-of-user-text rule).
Each framework's faithful artifacts live in this directory:

- [`github-spec-kit/`](./github-spec-kit/) · [`tessl/`](./tessl/) · [`openspec/`](./openspec/) · [`bmad/`](./bmad/)

The plain-Markdown reference version (the method by hand, no tooling) lives in the repo's top-level
[`specs/`](../specs/).

> **TL;DR.** **Spec Kit** = GitHub's heavyweight, gated, constitution-anchored workflow. **OpenSpec**
> = a lightweight, Git-native *specs-vs-changes* ledger that excels on brownfield codebases.
> **Tessl** = the most radical — specs as the durable source of truth with code as a *regenerable*
> artifact, plus a registry of versioned library specs. **BMAD** = not a spec tool per se but an
> *agile AI agent team* (PM/Architect/SM/Dev/QA) that produces PRDs, architecture docs, and richly
> contextualized stories.

---

## 1. At a glance

| | **GitHub Spec Kit** | **Tessl** | **OpenSpec** | **BMAD-METHOD** |
|---|---|---|---|---|
| **One-liner** | Constitution-gated spec→plan→tasks→implement toolkit | Specs as source of truth; code regenerable; library-spec registry | Specs-vs-changes ledger, brownfield-first | Agile AI agent team producing PRD + architecture + stories |
| **Vendor / origin** | GitHub (open source) | Tessl (Guy Podjarny, ex-Snyk) | Fission-AI (open source) | bmad-code-org (open source) |
| **Install** | `uv tool install specify-cli` | `curl get.tessl.io \| sh` | `npm i -g @fission-ai/openspec` | `npx bmad-method install` |
| **Primary artifact** | `spec.md` + `plan.md` + `tasks.md` | `*.spec.md` (per code unit) | capability `spec.md` + change deltas | `prd.md` + `architecture.md` + story files |
| **Unit of work** | A feature folder (`specs/NNN-*/`) | A logical code unit (one spec → its files) | A *change* (proposal → archive) | A *story* (within an epic) |
| **Maps spec→code?** | No (spec is upstream of code) | **Yes** (`targets:` frontmatter, regeneration) | No (specs describe capabilities) | No (stories guide the dev agent) |
| **Process style** | Phase-gated, prescriptive | Spec-centric, regeneration loop | Fluid, iterative, no mandatory gates | Two-phase agile (plan → story cycle) |
| **Driving mechanism** | Slash commands (`/speckit.*`) | Skills/rules + MCP registry | Slash commands (`/opsx:*`) + CLI | Agent personas (`@pm`, `@dev`, `*draft`) |
| **Constitution / rules** | First-class `constitution.md` (versioned, gated) | `rules/` steering files in the tile | `config.yaml` context + rules | `architecture/coding-standards.md` |
| **State / history model** | Git + feature folders | Spec files + drift detection | **Specs (truth) vs changes (proposals) + archive** | Story status + sprint tracking |
| **Best for** | Teams wanting rigor & governance | Teams treating specs as the real source | Brownfield incremental change | End-to-end greenfield product builds |
| **Maturity (2026)** | High, fast-moving, large ecosystem | Newer; skills GA, code-gen Framework in beta | Mature, lightweight, Radar-listed | Mature, large community, V4→v6 churn |

---

## 2. Philosophy — what each one actually believes

### GitHub Spec Kit — *"specifications are executable; the constitution is law"*
Spec Kit treats the spec as the primary artifact and code as its "last-mile" expression. Its
distinctive move is the **constitution**: versioned, non-negotiable project principles that every
plan is checked against at explicit **gates** (Constitution Check before Phase 0, re-check after
Phase 1). The `spec.md` is deliberately **non-technical** — written for stakeholders, no frameworks
or status codes — and all implementation shape is pushed down into `plan.md`/`data-model.md`/
`contracts/`. Three quality gates (Clarify, Checklist, Analyze) sit between stages.

### Tessl — *"the spec is the source of truth; code is disposable"*
Tessl is the only one of the four that inverts the spec↔code relationship for real. A `*.spec.md`
*owns* the files listed in its `targets:`; implementation is generated and can be **regenerated**
after a model upgrade or dependency change without losing intent. It adds two unique ideas: **spec
drift detection** (flagging when code diverged from its spec) and a **registry of versioned library
"usage specs"** (`tessl/pypi-fastapi`, etc.) so the agent uses accurate, pinned API docs instead of
hallucinating. Tests are bound to requirements via inline `` `[@test]` `` links.

### OpenSpec — *"agree on the change before you build it"*
OpenSpec's core is the **specs vs. changes** split. `openspec/specs/` is the established truth;
`openspec/changes/` holds proposals as self-contained folders that never touch the live specs until
**archived** (which merges the delta in). Its principles are explicitly *fluid, iterative, easy,
brownfield-first* — no mandatory phase gates. The format is strict where it matters: every
requirement needs ≥1 `#### Scenario:` in GIVEN/WHEN/THEN, validated by `openspec validate --strict`.

### BMAD-METHOD — *"agents are an agile team, not an autopilot"*
BMAD isn't really a "spec format" — it's a **role-playing agent team** running an agile process.
A **Planning** phase (Analyst → PM → Architect → PO) produces a PRD and Architecture doc; a
**Development cycle** has the Scrum Master shard those into epics and draft self-contained **story
files**, which Dev implements and QA reviews. The story file is the key artifact: it embeds *just
enough* architecture context inline so each fresh agent session has what it needs without re-reading
the repo ("context-engineered development").

---

## 3. Artifacts & file structure (as built here)

| Framework | Key paths in this repo |
|---|---|
| **Spec Kit** | `.specify/memory/constitution.md`; `specs/001-summarization-api/{spec,plan,tasks,data-model,quickstart}.md`, `contracts/openapi.yaml`, `checklists/requirements.md` |
| **Tessl** | `tessl.json`; `specs/summarize.spec.md` (frontmatter `name`/`description`/`targets` + inline `[@test]`) |
| **OpenSpec** | `openspec/config.yaml`; `openspec/specs/summarization/spec.md` (live); `openspec/changes/add-summarization-api/{proposal,design,tasks}.md` + delta `specs/summarization/spec.md` |
| **BMAD** | `core-config.yaml`; `docs/{prd,architecture}.md`; `docs/stories/1.1.*.md`, `docs/stories/1.2.*.md` |

**Granularity ladder** (how big is "one spec"?): Tessl (one code unit) → Spec Kit / OpenSpec
(one feature/capability) → BMAD (one product, decomposed into epics → stories).

---

## 4. Workflow & commands

| Stage | Spec Kit | Tessl | OpenSpec | BMAD |
|---|---|---|---|---|
| Set rules | `/speckit.constitution` | install SDD tile (`rules/`) | edit `config.yaml` | Architect coding-standards |
| Specify | `/speckit.specify` | author `*.spec.md` | `/opsx:propose` (delta) | `@pm *create-prd` |
| Clarify | `/speckit.clarify` | `requirement-gathering` skill | in-proposal Q&A | PO checklist |
| Plan | `/speckit.plan` | (spec *is* the plan) | `design.md` | `@architect *create-architecture` |
| Decompose | `/speckit.tasks` | (implicit) | `tasks.md` | `@po *shard` → `@sm *draft` |
| Quality gate | `/speckit.checklist`, `/speckit.analyze` | `spec-verification` (drift) | `openspec validate --strict`, `/opsx:verify` | PO master checklist, QA review |
| Implement | `/speckit.implement` | `tessl build` / agent | `/opsx:apply` | `@dev *develop-story` |
| Land | (merge PR) | regenerate / verify | `openspec archive` | story → Done |

---

## 5. Benefits & disadvantages

### GitHub Spec Kit
**Benefits**
- Strongest **governance**: a versioned constitution plus hard Constitution-Check gates; ideal where
  consistency across many features/teams matters.
- Clean **separation of what vs how** — `spec.md` stays stakeholder-readable; tech detail is isolated.
- Rich, dependency-ordered `tasks.md` (phases, `[P]` parallel, `[US#]` story tags) enabling MVP-first
  delivery; large ecosystem (extensions, presets) and broad agent support.
- Backed by GitHub; strong momentum and docs.

**Disadvantages**
- **Heaviest** of the four: many files per feature (`spec`, `plan`, `research`, `data-model`,
  `quickstart`, `contracts/`, `checklists/`, `tasks`) — overkill for a tiny change.
- Prescriptive/phase-gated; can feel like ceremony on small teams.
- Greenfield-leaning; no first-class model of "change vs current truth" like OpenSpec.
- Fast-moving and young — templates and commands shift between releases.

### Tessl
**Benefits**
- The only framework that makes **specs the durable source and code regenerable** — code can be
  rebuilt from spec after a model/dep upgrade without losing intent.
- **Spec drift detection** keeps spec and code honest over time (the chronic SDD failure mode).
- **Registry of versioned library specs** reduces API hallucination — a genuinely different lever.
- Lightweight spec format (frontmatter + prose + inline `[@test]`); one spec per code unit maps
  cleanly to files and tests.

**Disadvantages**
- **Least mature / least open**: the code-generation **Framework** (`@generate`, `tessl build`) is in
  closed beta and not in public docs; only the skills-based workflow is GA. Some conventions here are
  inferred from examples, not documentation.
- Vendor platform + registry dependency (login, hosted registry) — more lock-in than plain Markdown.
- Regeneration is non-deterministic; teams uncomfortable with "disposable implementation" will resist.
- Smallest community and example base of the four.

### OpenSpec
**Benefits**
- **Brownfield-first** and **lightweight** — plain Markdown, no servers/keys; the easiest to adopt
  incrementally on an existing codebase.
- The **specs-vs-changes** model is its superpower: proposals are reviewable in isolation and merged
  into the living truth on archive, building an organic spec library and an audit trail of *why*.
- Strict, machine-checkable format (`validate --strict`: every requirement needs a scenario;
  exactly-four-hashtag scenarios) catches structural gaps cheaply.
- Multiple parallel changes coexist without conflict; great fit for normal PR-based teamflow.

**Disadvantages**
- Provides structure, **not governance** — no first-class versioned constitution (rules live in
  `config.yaml`); less opinionated about *what good looks like*.
- The delta syntax (`ADDED`/`MODIFIED`/`REMOVED`, full-block copies for MODIFIED) has sharp edges —
  silent failures if you use the wrong heading depth.
- No spec→code binding or drift detection; the spec can still rot if discipline lapses.
- Recent breaking changes (e.g. `project.md` → `config.yaml`, skills-based agent files) mean older
  tutorials mislead.

### BMAD-METHOD
**Benefits**
- The most complete **end-to-end product workflow**: research → PRD → architecture → sharded stories
  → dev → QA, with explicit roles and checklists.
- **Context engineering** is its standout idea — self-contained story files keep each agent session
  focused and avoid context overflow on large builds.
- Strong for **greenfield products** and for teams that want an agile cadence (epics, stories,
  sprints, retrospectives) rather than just a spec format.
- Large, active community; web-bundle option lets the planning phase run in any chat UI.

**Disadvantages**
- **Heaviest process and most concepts** (a whole agent roster, templates, workflows, checklists) —
  large overhead for a single endpoint; this example needs only one epic.
- It's an **agile method**, not a spec contract — weaker on machine-checkable spec validation than
  OpenSpec or on contract artifacts than Spec Kit.
- Significant **V4 → v6 churn**: directory layout (`bmad-core/` → `_bmad/`), persona roster (QA/SM
  folded into a Dev persona), and story template all changed — version confusion is common.
- Document-and-persona driven; less "drop into an existing repo and go" than OpenSpec.

---

## 6. How they handle the same hard requirements

The Summarization API has four ambiguity traps. How each framework pins them down:

| Requirement | Spec Kit | Tessl | OpenSpec | BMAD |
|---|---|---|---|---|
| Empty input → **422, no model call** | FR-003 + acceptance scenario; status in `data-model.md`/contract | prose req + `[@test]` link | `### Requirement: Reject Invalid Input` + `#### Scenario` | FR3 + story 1.2 AC #2 |
| Model failure → **502, no leak** | FR-005 + SC-003 | prose req + `[@test]` | `### Requirement: Handle Upstream Failure Safely` | FR5 + AC #4 |
| **Never log user text** | Principle IV + FR-010 + SC-004 | privacy req + `[@test]` | `### Requirement: Never Log User Text` (+ scenario w/ marker) | NFR1 + AC #7 |
| Exactly **one** model call | FR-009 | prose req + `[@test]` | `### Requirement: Single Bounded Model Invocation` | FR9 + AC #6 |

All four can express every requirement; they differ in **where** it lives (a versioned principle vs a
test-linked line vs a validated scenario vs a story AC) and in **how machine-checkable** it is.

---

## 7. Choosing one

- **Want governance and consistency across many features/teams?** → **Spec Kit**. The constitution +
  gates are the differentiator.
- **Adding to an existing codebase, change by change, PR by PR?** → **OpenSpec**. Lightweight,
  brownfield-first, with the cleanest "proposal vs truth" model and machine validation.
- **Believe the spec should outlive the code and want regeneration + drift detection + accurate
  library specs?** → **Tessl**. Most forward-looking; accept it's the least mature/most vendor-bound.
- **Building a product greenfield and want an agile agent team (PRD → architecture → stories)?** →
  **BMAD**. Best end-to-end workflow; heaviest ceremony.

They're **not mutually exclusive**. Common combinations: a Spec-Kit/OpenSpec constitution-style rule
set + OpenSpec change tracking; BMAD for planning + Spec Kit/OpenSpec for per-feature specs; Tessl's
library registry alongside any of them. The discipline underneath is identical and is what actually
matters — *name it, plan it, verify it* — captured framework-free in [`../specs/`](../specs/).

---

*Conventions in this document were verified against each project's public documentation and source in
2026. These tools move fast — especially Tessl (Framework in beta) and BMAD (V4→v6). Treat the
hand-authored files here as faithful, diffable illustrations and re-run the real CLIs (see each
folder's README) for the current canonical output.*
