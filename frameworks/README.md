# Building one system, six SDD frameworks

## What this is

This directory is the heart of a **teaching demo for Spec-Driven Development (SDD)** — the practice of
directing an AI coding agent with written artifacts (a constitution, a spec, a plan, tasks) precise
enough that the agent *can't guess wrong*, instead of ad-hoc "vibe" prompting. It accompanies the
webinar **"Spec-Driven Development with AI Agents."**

The demo does one thing and does it six times: it takes a **single, deliberately small system** and
specifies it with **six different SDD frameworks**, so you can see — side by side, on identical
requirements — how each tool wants you to work, what files it produces, and where it forces you to
resolve ambiguity. It is a Rosetta stone for the SDD tool landscape.

> **Why compare on one tiny system?** Holding the *feature* constant is the whole point. When every
> folder builds the exact same thing, the only variable left is the **framework** — so the diffs
> between folders are pure signal about the tools, not noise about the problem.

## The system every folder builds

**The Summarization API** — a single HTTP endpoint, **`POST /summarize`**, that takes a block of text
and returns a concise summary from **exactly one** OpenAI call, as JSON. It's the most common
production LLM pattern (a service in front of a model), small enough to fully specify in one sitting,
yet ambiguity-sensitive at every edge: What's the response shape? What status code on empty input? On
a model timeout? Do you log the user's text? Every folder answers those *same* questions in its own
dialect. The identical behavior contract (`R1`–`R9`) lives in [`../specs/spec.md`](../specs/spec.md).

> **Note:** these folders contain the **specifications** for the system, not a running application —
> that is by design. The demo is about the part of the work that happens *before* the agent writes
> code. Each folder is the input you'd hand an agent to then generate the implementation.

## The six frameworks

Each folder specifies that same API using a different point on the SDD spectrum from the webinar —
same requirements, six dialects, so you can compare conventions on identical ground.

Ordered lightest-touch → spec-as-source (the deck's spectrum):

| Folder | Framework | Spectrum position | Distinctive idea |
|--------|-----------|-------------------|------------------|
| [`rules-and-context/`](./rules-and-context/) | **Rules & Context Files** | Lightest touch (adjacent to SDD) | Standing conventions that steer any agent — Cursor rules, `CLAUDE.md`, `AGENTS.md`. No per-feature spec. |
| [`github-spec-kit/`](./github-spec-kit/) | **GitHub Spec Kit** | Full workflow · agent-agnostic | Versioned constitution + phase gates; spec / plan / tasks split. The open-source standard. |
| [`aws-kiro/`](./aws-kiro/) | **AWS Kiro** | Full workflow · agentic IDE | Three docs — requirements (EARS) → design → tasks — built into the IDE, with steering files & hooks. |
| [`openspec/`](./openspec/) | **OpenSpec** | Full workflow · brownfield-first | `specs/` (truth) vs `changes/` (proposals) + archive; every behavior a GIVEN/WHEN/THEN scenario. |
| [`bmad/`](./bmad/) | **BMAD-METHOD** | Full workflow · multi-agent | An agile AI *team* — Analyst → PM → Architect → Dev → QA → PRD, architecture, story files. |
| [`tessl/`](./tessl/) | **Tessl** | Spec-as-source (radical end) | The spec is the maintained artifact; code is regenerated from it. |

> **Framework-free reference:** [`../specs/`](../specs/) shows the same method *by hand* — a
> constitution plus a six-section spec — with no tool on top. Read it first if you want the bare loop.

## How to read this demo

- **New to SDD?** Start at [`../specs/`](../specs/) — the same method by hand (a constitution + a
  six-section spec), with no tool on top. It's the loop everything here is a variation of.
- **Want the big picture of the tools?** Read [`COMPARISON.md`](./COMPARISON.md) — philosophy,
  artifacts, workflow, benefits, disadvantages, and how to choose.
- **Exploring one framework?** Open its folder and read its `README.md` first — it explains what each
  file is and how to reproduce it with the real CLI/IDE. Then read the spec files themselves.
- **Picking one for your own project?** Jump to §7 of `COMPARISON.md`.

Every folder is hand-authored to match its framework's real templates, so the examples are
self-contained and diffable **without installing any of the toolchains** — you can study the artifacts
directly. Each folder's `README.md` also shows the exact commands to generate the same thing with the
live tool.
