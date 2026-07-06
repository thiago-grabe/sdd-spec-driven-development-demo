@AGENTS.md

# CLAUDE.md

Claude Code reads `CLAUDE.md`, not `AGENTS.md`, so this file imports the shared guidance above with
`@AGENTS.md` (expanded into context at launch) and adds only Claude-specific notes. Keep this file
short — under ~200 lines — so adherence stays high; put path-scoped detail in `.claude/rules/`.

## Claude Code specifics
- Use **plan mode** before touching files under `src/summarizer_service/services/` — the single model
  call is the load-bearing part; propose the approach and get approval before editing.
- After changing any route or model, run `uv run pytest` and confirm the OpenAPI schema still matches
  the contract in `@AGENTS.md`.
- The privacy rule is a **release blocker**, not a nit: if a change could put user text or the API key
  in a log or response, stop and flag it.

## Memory & file locations (reference)
- Project memory: this file (`./CLAUDE.md`) or `./.claude/CLAUDE.md`, committed for the team.
- Personal, uncommitted overrides: `./CLAUDE.local.md` (gitignored).
- User-global across all projects: `~/.claude/CLAUDE.md`.
- Path-scoped rules: `.claude/rules/*.md` with a `paths:` front-matter array (see `.claude/rules/`).
- Add a memory mid-session by typing a line that starts with `#`, or run `/memory` to edit files.
