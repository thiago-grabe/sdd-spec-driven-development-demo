# Summarization API — Tessl version

The same Summarization API specified with **[Tessl](https://tessl.io)** spec-driven-development
conventions.

## What's here

```text
tessl.json                 # project manifest: the SDD tile + library usage-spec tiles
specs/
└── summarize.spec.md      # one spec per logical unit; targets[] map it to the code it governs
```

## How Tessl models this

- **One `.spec.md` per logical unit of functionality.** Its `targets:` frontmatter lists the
  implementation file(s) the spec governs — the spec is the durable artifact, the code is a
  regenerable one.
- Requirements are plain prose with an **inline `` `[@test] path` `` link** next to each, binding a
  behavior to the test that proves it. Tessl's `spec-verification` skill uses these links to detect
  **spec drift** (code that diverged from its spec).
- Library knowledge comes from **Registry tiles** (`tessl/pypi-fastapi`, `tessl/pypi-openai`) listed
  in `tessl.json`, so the agent uses accurate, version-pinned API docs instead of guessing.

## Reproduce with the real CLI

```bash
curl -fsSL https://get.tessl.io | sh
tessl login
tessl init --agent claude
tessl install tessl-labs/spec-driven-development
# then prompt your agent: "use spec-driven development to build the summarize endpoint"
# verify drift later with the spec-verification skill; tessl build (Framework) can regenerate code
```

> Note: the `@generate`/`@use` code-generation directives belong to the (closed-beta) Tessl
> *Framework*. This example uses the generally-available **skills-based** SDD workflow, whose
> confirmed format is `name`/`description`/`targets` frontmatter + inline `[@test]` links.
