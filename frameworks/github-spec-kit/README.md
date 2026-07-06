# Summarization API — GitHub Spec Kit version

The same Summarization API (`POST /summarize`, one OpenAI call) specified with **[GitHub Spec
Kit](https://github.com/github/spec-kit)** conventions.

## What's here

```text
.specify/
└── memory/
    └── constitution.md          # project principles (the /speckit.constitution output)
specs/
└── 001-summarization-api/
    ├── spec.md                  # /speckit.specify — WHAT & WHY, no implementation detail
    ├── plan.md                  # /speckit.plan   — Technical Context, Constitution Check, structure
    ├── data-model.md            # /speckit.plan   — Phase 1 entities
    ├── quickstart.md            # /speckit.plan   — run & verify
    ├── contracts/openapi.yaml   # /speckit.plan   — the HTTP contract
    ├── checklists/requirements.md  # /speckit.checklist — spec-quality gate
    └── tasks.md                 # /speckit.tasks  — T001.. dependency-ordered, [P], [US#]
```

## How Spec Kit models this

- The **constitution** is immutable-ish project law in `.specify/memory/`, version-stamped, with a
  Sync Impact Report. Every plan runs a **Constitution Check** gate against it.
- `spec.md` is deliberately **non-technical**: user stories with priorities, `FR-###` requirements,
  technology-agnostic success criteria. No status codes, field types, or model names — those are
  pushed down into `plan.md` / `data-model.md` / `contracts/`.
- `tasks.md` groups work into **phases** (Setup → Foundational → per-User-Story → Polish) with
  `T###` ids, `[P]` parallel markers, and `[US#]` story tags, so an MVP (US1) can ship first.

## Reproduce with the real CLI

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init . --here --integration claude
# then, inside your agent:
/speckit.constitution   /speckit.specify   /speckit.clarify   /speckit.plan
/speckit.checklist      /speckit.analyze   /speckit.tasks      /speckit.implement
```

These files were hand-authored to match Spec Kit's templates so the example is self-contained and
diffable without running the toolchain.
