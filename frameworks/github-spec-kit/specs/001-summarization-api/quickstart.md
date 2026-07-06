# Quickstart: Summarization API

Run and verify the feature locally. This script demonstrates each acceptance scenario.

## Run

```bash
uv sync
export OPENAI_API_KEY=sk-...           # never commit this
uv run uvicorn summarizer_service.main:app --reload
# OpenAPI docs at http://localhost:8000/docs
```

## Verify the acceptance scenarios

```bash
# US1 — happy path → 200 with summary, word_count, model, request_id
curl -sS -i -X POST localhost:8000/summarize \
  -H 'content-type: application/json' \
  -d '{"text":"Long article text here ...","max_words":50}'

# US2 — empty input → 422, no model call
curl -sS -i -X POST localhost:8000/summarize \
  -H 'content-type: application/json' -d '{"text":"   "}'

# US2 — oversize input → 413, no model call
python -c "import json,sys; sys.stdout.write(json.dumps({'text':'x'*10001}))" | \
  curl -sS -i -X POST localhost:8000/summarize -H 'content-type: application/json' -d @-

# US3 — every response carries X-Request-ID (check the header in each response above)
```

## Run the test suite (no live model calls)

```bash
uv run pytest          # the OpenAI client is mocked in conftest.py
uv run ruff check . && uv run ruff format --check .
```

## Done when

- All curl checks return the documented status codes; every response has `X-Request-ID`.
- `pytest` is green offline; ruff is clean.
- The generated OpenAPI (`/openapi.json`) matches `contracts/openapi.yaml`.
- A grep of captured logs for any submitted text finds nothing (privacy).
