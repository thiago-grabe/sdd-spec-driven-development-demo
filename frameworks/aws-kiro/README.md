# Summarization API — AWS Kiro version

The same Summarization API (`POST /summarize`, one OpenAI call) specified with **[AWS
Kiro](https://kiro.dev)** conventions — the AI-native IDE with spec-driven development built into
its core.

## What's here

```text
.kiro/
├── steering/                     # standing project context (Kiro's "constitution" layer)
│   ├── product.md                # the why — purpose, users, success, out-of-scope
│   ├── tech.md                   # the stack, constraints, testing, definition of done
│   └── structure.md              # file layout + naming/organization conventions
├── specs/
│   └── summarization-api/        # one spec = one feature (kebab-case folder)
│       ├── requirements.md       # EARS user stories + acceptance criteria
│       ├── design.md             # Overview/Architecture/Components/Data Models/Errors/Testing
│       └── tasks.md              # "# Implementation Plan" — [ ] tasks + _Requirements:_ trailers
└── hooks/
    └── never-log-user-text.kiro.hook   # event-driven agent hook (fileEdited -> askAgent)
```

## How Kiro models this

Kiro splits SDD into **three documents produced in sequence, each approved before the next**:

1. **`requirements.md`** — user stories plus acceptance criteria written in **EARS** (Easy Approach
   to Requirements Syntax): `WHEN <trigger> THEN the system SHALL <response>`, `IF <condition> THEN
   the system SHALL <response>`, `WHILE <state> the system SHALL ...`, `WHERE <feature> the system
   SHALL ...`, and ubiquitous `the system SHALL ...`. Every criterion is testable by construction.
2. **`design.md`** — a fixed set of sections (Overview, Architecture with Mermaid, Components and
   Interfaces, Data Models, Error Handling, Testing Strategy).
3. **`tasks.md`** — titled `# Implementation Plan`, GitHub-style `- [ ]` checkboxes (max two levels),
   each closing with an italic `_Requirements: X.Y_` trailer that traces the task back to the
   acceptance criteria it satisfies.

**Steering files** (`.kiro/steering/*.md`) are the always-on context every spec inherits — the Kiro
analog of a constitution. Their `inclusion:` front-matter controls when they load: `always` (default),
`fileMatch` (with a `fileMatchPattern`), or `manual` (referenced in chat as `#file-name`).

**Agent hooks** (`.kiro/hooks/*.kiro.hook`) are event-driven automations: a `when` trigger (e.g.
`fileEdited` with glob `patterns`) fires a `then` action (`askAgent` with a prompt, or `runCommand`).
The hook here re-checks the privacy guardrail every time a source file is saved.

## Reproduce in the real IDE

```text
1. Install Kiro (kiro.dev) and open this folder.
2. Kiro auto-generates .kiro/steering/{product,tech,structure}.md — or run "Generate steering".
3. In the Kiro pane, click + under Specs (or pick Spec in chat) and describe the feature.
4. Approve each phase in turn: requirements.md -> design.md -> tasks.md.
5. Execute tasks from tasks.md (Autopilot for autonomous, Supervised for per-hunk review).
```

> These files were hand-authored to match Kiro's generated formats so the example is self-contained
> and diffable without running the IDE. EARS keywords are uppercase; `the system` is lowercase — that
> is Kiro's authentic rendering.
