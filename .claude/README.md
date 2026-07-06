# The Same Project, Four SDD Frameworks

This directory specifies **one service — the Summarization API** (`POST /summarize`, exactly one
OpenAI call) **four different ways**, one per spec-driven-development framework, so you can compare
their conventions side by side on identical requirements.

| Folder | Framework | Distinctive idea |
|--------|-----------|------------------|
| [`github-spec-kit/`](./github-spec-kit/) | **GitHub Spec Kit** | Versioned `constitution.md` + phase gates; spec/plan/tasks split |
| [`tessl/`](./tessl/) | **Tessl** | Spec is the source of truth; code is regenerable; library-spec registry |
| [`openspec/`](./openspec/) | **OpenSpec** | `specs/` (truth) vs `changes/` (proposals) + archive; brownfield-first |
| [`bmad/`](./bmad/) | **BMAD-METHOD** | Agile AI agent team → PRD, architecture, and story files |

📄 **[COMPARISON.md](./COMPARISON.md)** — the full write-up: philosophy, artifacts, workflow,
benefits, disadvantages, and how to choose.

📘 **[TEACHING-GUIDE.md](./TEACHING-GUIDE.md)** — how to **read, create, and explain every file** in
each framework, with "say this out loud" lines, reading orders, and a demo choreography. Start here
if you're presenting.

The same requirements expressed **framework-free** (the method by hand, plain Markdown) live in the
repo's top-level [`../specs/`](../specs/) — start there for the underlying discipline, then read each
folder to see how a given tool encodes it.

> Every folder's files are **hand-authored to match the real framework's conventions** (verified
> against each project's docs/source in 2026) so the example is self-contained and diffable without
> installing four toolchains. Each folder's README shows how to reproduce it with the actual CLI.
