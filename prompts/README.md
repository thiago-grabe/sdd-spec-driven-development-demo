# Prompts — SDD Pipeline

Three prompts, one per stage. Run them in order. Approve between each step.

```
specs/ ──▶ [01-generate-plan.md] ──▶ spec.md §5 ──(approve)──▶
        ──▶ [02-generate-tasks.md] ──▶ spec.md §6 ──(approve)──▶
        ──▶ [03-implement.md] ──▶ code + green tests
```

---

## How to use

1. **Prompt 01** — paste into a new agent session. The agent reads the three spec files and appends `## 5. Plan` to `spec.md`. Review it, correct anything wrong, approve.

2. **Prompt 02** — new session. The agent checks that every R1–R9 criterion maps to a task, then appends `## 6. Tasks`. Review the dependency order and traceability, approve.

3. **Prompt 03** — new session. The agent implements one task per reply and stops for review. After T10d, run the full suite:
   ```bash
   uv run pytest tests/ -v
   uv run ruff check .
   uv run ruff format --check .
   ```

---

## R → Task traceability

| Req | Task |
|-----|------|
| R1 | T8, T10d |
| R2 | T2, T10d |
| R3 | T8, T3, T10d |
| R4 | T6, T7, T10d |
| R5 | T9, T10d |
| R6 | T8, T10b |
| R7 | T5, T10d |
| R8 | T6, T10c |
| R9 | T6, T10c |
