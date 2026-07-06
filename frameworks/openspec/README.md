# Summarization API — OpenSpec version

The same Summarization API specified with **[OpenSpec](https://github.com/Fission-AI/OpenSpec)**
conventions.

## What's here

```text
openspec/
├── config.yaml                              # project context + per-artifact rules
├── specs/
│   └── summarization/
│       └── spec.md                          # LIVE spec — the established source of truth
└── changes/
    └── add-summarization-api/
        ├── proposal.md                      # Why / What Changes / Capabilities / Impact
        ├── design.md                        # Context / Goals / Decisions / Risks
        ├── tasks.md                         # numbered groups of - [ ] checkboxes
        └── specs/
            └── summarization/
                └── spec.md                  # DELTA — `## ADDED Requirements`
```

## How OpenSpec models this

The defining idea is the split between **`specs/`** (what is *true and built* now) and
**`changes/`** (proposals not yet merged). You never edit a live spec directly:

1. **Propose** a change → write `proposal.md`, `design.md`, `tasks.md`, and a **delta spec** under
   `changes/<name>/specs/<capability>/spec.md` using `## ADDED / MODIFIED / REMOVED Requirements`.
2. **Review & implement** the tasks.
3. **Archive** (`openspec archive`) → the delta is merged into `specs/summarization/spec.md` and the
   change moves to `changes/archive/YYYY-MM-DD-add-summarization-api/`.

Requirements use RFC-2119 language (`SHALL`/`MUST`) and **every requirement has at least one
`#### Scenario:`** in GIVEN/WHEN/THEN form — scenarios use **exactly four hashtags**, which
`openspec validate --strict` enforces (three hashtags fail silently at archive time).

Both the delta (in `changes/`) and the merged result (in `specs/`) are included here so you can see
the full lifecycle; in a real repo the live spec is produced by the archive step.

## Reproduce with the real CLI

```bash
npm install -g @fission-ai/openspec@latest
openspec init
# inside your agent:
/opsx:propose add-summarization-api    # generates proposal, delta specs, design, tasks
/opsx:apply add-summarization-api      # implements tasks, ticks checkboxes
/opsx:verify add-summarization-api     # completeness / correctness / coherence
openspec validate --strict
openspec archive add-summarization-api # merges the delta into specs/summarization/spec.md
```
