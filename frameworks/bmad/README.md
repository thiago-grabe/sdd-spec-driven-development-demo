# Summarization API — BMAD-METHOD version

The same Summarization API specified with **[BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)**
conventions (the "Breakthrough Method of Agile AI-Driven Development").

## What's here

```text
core-config.yaml           # tells the agents where artifacts live + the dev-load-always files
docs/
├── prd.md                 # PM (John) — Goals, FR/NFR, Technical Assumptions, Epics & Stories
├── architecture.md        # Architect (Winston) — tech stack, data models, source tree, standards
└── stories/
    ├── 1.1.project-scaffold.md   # SM (Bob) — drafted story, ready for the Dev agent
    └── 1.2.summarize-endpoint.md
```

## How BMAD models this

BMAD is **agent-team + document-driven**, not slash-command driven. Two phases:

1. **Planning** (big-context web/IDE): the **Analyst** → **PM** → **Architect** produce a PRD and
   an Architecture doc; the **PO** validates them with a master checklist and **shards** them into
   `docs/prd/` and `docs/architecture/`.
2. **Development cycle** (fresh IDE context per story): the **Scrum Master** drafts a self-contained
   **story file** (the unit of work — note the rich `Dev Notes`, `Tasks/Subtasks`, `Dev Agent
   Record`, and `QA Results` sections); the **Dev** agent implements it; the **QA** agent reviews.
   Status flows `Draft → Approved → InProgress → Review → Done`.

The story file is BMAD's distinctive artifact: it carries *just enough* architecture context inline
so each dev session starts fresh without re-reading the whole repo ("context-engineered
development"). Story 1.1 is shown as `Approved`; Story 1.2 as `Draft`.

## Reproduce with the real CLI

```bash
npx bmad-method install        # creates bmad-core/ (V4) or _bmad/ (v6+) + agent files
# then, with the agents:
@pm *create-prd                # John writes docs/prd.md
@architect *create-backend-architecture   # Winston writes docs/architecture.md
@po  *shard-prd                # Sarah shards docs into docs/prd/ and docs/architecture/
@sm  *draft                    # Bob drafts docs/stories/1.1...  (repeat per story)
@dev *develop-story            # James implements;  @qa *review  to review
```

> This example targets **V4** layout (`bmad-core/`, named personas Mary/John/Winston/Bob/James/
> Sarah/Quinn, `docs/stories/{epic}.{story}.{slug}.md`), which most documentation describes. v6+
> renames to `_bmad/` + skills, consolidates QA/SM into the Dev persona (Amelia), and outputs to
> `_bmad-output/`; the planning artifacts and story content map across both.
