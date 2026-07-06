# Summarization API — Rules & Context Files version

The same Summarization API expressed as **rules & context files** — the lightest rung on the
spec-driven-development spectrum. These are standing conventions that steer *any* agent on *every*
request: **Cursor rules** (`.cursor/rules/*.mdc`), **Claude Code** (`CLAUDE.md` + `.claude/rules/`),
and the cross-tool **`AGENTS.md`** standard.

> **This is adjacent to SDD, not the whole of it.** Rules encode the reusable "constitution" layer —
> stack, conventions, guardrails, the behavior contract. They do **not** replace a per-feature
> `spec → plan → tasks` flow. Reach for them as day-one guardrails on any project, and pair them with
> one of the fuller frameworks when a feature needs real specification.

## What's here

```text
AGENTS.md                              # tool-agnostic shared guidance (the cross-tool standard)
CLAUDE.md                              # Claude Code: imports @AGENTS.md + Claude-specific notes
.claude/
└── rules/
    └── api-privacy.md                 # path-scoped rule (quoted YAML `paths:` array)
.cursor/
└── rules/
    ├── always.mdc                     # Always            (alwaysApply: true)
    ├── python-fastapi.mdc             # Auto Attached     (globs + alwaysApply: false)
    ├── openai-model-call.mdc          # Agent Requested   (description + alwaysApply: false)
    └── release-checklist.mdc          # Manual            (@-mentioned only)
```

## The four Cursor rule types

Cursor rules are Markdown-with-frontmatter (`.mdc`). Three frontmatter fields — `description`,
`globs`, `alwaysApply` — combine into four activation patterns:

| Type | Front-matter | When it loads |
|------|--------------|---------------|
| **Always** | `alwaysApply: true` | Every request. |
| **Auto Attached** | `globs:` set, `alwaysApply: false` | When a file matching the globs is referenced. |
| **Agent Requested** | `description:` set, no `globs`, `alwaysApply: false` | The agent reads the description and decides. |
| **Manual** | none of the above | Only when `@`-mentioned in chat. |

> `globs:` is an **unquoted, comma-separated** list (`src/**/*.py, tests/**/*.py`) — not a YAML array.
> Cursor also reads `AGENTS.md`, but ignores plain `.md` rule files; rules must be `.mdc`.

## How Claude Code models this

- Claude Code reads **`CLAUDE.md`**, not `AGENTS.md` — so `CLAUDE.md` here starts with `@AGENTS.md` to
  import the shared guidance, then adds Claude-specific notes. Keep it under ~200 lines.
- **`.claude/rules/*.md`** are path-scoped, like Cursor's Auto Attached rules, but the front-matter
  uses a **quoted YAML `paths:` array** with brace expansion — a common authenticity mistake is to mix
  this up with Cursor's comma syntax.
- Precedence (broad → specific, all concatenated): managed policy → `~/.claude/CLAUDE.md` (user) →
  `./CLAUDE.md` (project) → `./CLAUDE.local.md` (local, gitignored). Subdirectory `CLAUDE.md` files
  load on demand.

## The catch (from the deck)

Rules are **standing context, not a per-feature spec** — they don't do specify / plan / tasks. And
"plan mode" is ephemeral: the plan is discarded, the code is the asset. Use rules to stop the agent
re-guessing your conventions on every request; use a spec to stop it guessing the *feature*.
