# Architecture — Summarization Service

> **One endpoint. One model call. Layered, stateless, mockable.**
> The diagrams below are the source of truth for component boundaries, the request lifecycle, and
> the status-code decision flow. See `spec.md` for behavior and contracts.

---

## 1. Component view

The main pieces of the service and how they talk to each other.
Solid arrows = a normal call. Dashed arrows = something used in the background (config, logs).

```mermaid
flowchart LR
  classDef ext fill:#fef3c7,stroke:#b45309,color:#1f2937
  classDef app fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a

  Client(["Client"]):::ext
  OpenAI[["OpenAI API"]]:::ext
  Env[("ENV<br/>OPENAI_API_KEY")]:::ext

  subgraph App["summarizer_service (FastAPI app)"]
    direction LR
    API["API route<br/>POST /summarize"]:::app
    Schemas["Schemas<br/>(Pydantic)"]:::app
    Service["Summarizer<br/>(the one call)"]:::app
    ErrHandler["Error handler<br/>413 · 422 · 502"]:::app
    Settings["Settings"]:::app
    Logger["Logger<br/><i>metadata only</i>"]:::app
  end

  Client -- "POST /summarize" --> API
  API -- "validate" --> Schemas
  API -- "call" --> Service
  Service -- "1 call · 30 s" --> OpenAI

  Service -. "errors" .-> ErrHandler
  API -. "errors" .-> ErrHandler
  ErrHandler -- "ErrorResponse" --> Client
  API -- "SummarizeResponse" --> Client

  Env -.-> Settings
  Settings -. "model · timeout · key" .-> Service
  Logger -. "every request" .-> API
  Logger -. "every error" .-> ErrHandler
```

| Component | Role |
|-----------|------|
| **Client** | Anyone that calls `POST /summarize`. External. |
| **API route** | Receives the request, runs the 10k guard, calls the service, builds the response. |
| **Schemas** | Pydantic models that validate input and shape output. |
| **Summarizer** | Makes the **single** OpenAI call (30 s timeout, ≤1 retry). |
| **Error handler** | Turns failures into clean `413 / 422 / 502` `ErrorResponse`s. |
| **Settings** | Reads `OPENAI_API_KEY`, model name, timeout from `.env`. |
| **Logger** | Writes **metadata only** (request id, length, status, latency). Never the user's text. |
| **OpenAI API** | External LLM provider. |

---

## 2. Request lifecycle (sequence)

```mermaid
sequenceDiagram
  autonumber
  actor C as Client
  participant MW as RequestID Middleware
  participant R as api/routes.py
  participant V as Pydantic (schemas)
  participant S as services/summarizer.py
  participant O as OpenAI SDK
  participant E as api/errors.py
  participant L as core/logging (metadata only)

  C->>MW: POST /summarize { text, max_words? }
  MW->>MW: assign request_id (uuid)
  MW->>R: forward request

  R->>V: validate SummarizeRequest
  alt empty / whitespace text
    V-->>E: ValidationError
    E-->>L: log(status=422, len=0, request_id)
    E-->>C: 422 ErrorResponse(request_id)
  else text length > 10_000
    R-->>E: raise PayloadTooLargeError
    E-->>L: log(status=413, len=N, request_id)
    E-->>C: 413 ErrorResponse(request_id)
  else valid
    R->>S: summarize(text, max_words)
    S->>O: chat.completions.create(model, msgs, timeout=30)
    alt success
      O-->>S: completion
      S-->>R: summary
      R->>L: log(status=200, latency, model, request_id)
      R-->>MW: SummarizeResponse(summary, word_count, model, request_id)
      MW-->>C: 200 + X-Request-ID
    else timeout / upstream error (≤1 retry, then fail)
      O--xS: error / timeout
      S-->>E: raise SummarizerError
      E->>L: log(status=502, err_class, request_id)
      E-->>C: 502 ErrorResponse(request_id)
    end
  end
```

---

## 3. Status-code decision flow

```mermaid
flowchart LR
  classDef ok fill:#dcfce7,stroke:#15803d,color:#14532d
  classDef warn fill:#fef9c3,stroke:#ca8a04,color:#713f12
  classDef err fill:#fee2e2,stroke:#b91c1c,color:#7f1d1d
  classDef gate fill:#e0e7ff,stroke:#4338ca,color:#312e81

  Req(["Incoming request"]) --> P{Pydantic<br/>valid?}:::gate
  P -- no --> R422["422<br/>empty / whitespace"]:::warn
  P -- yes --> L{len text<br/>≤ 10 000?}:::gate
  L -- no --> R413["413<br/>payload too large"]:::warn
  L -- yes --> Call{{"ONE OpenAI call<br/>30 s · ≤1 retry"}}:::gate
  Call -- error / timeout --> R502["502<br/>upstream failure"]:::err
  Call -- ok --> R200["200<br/>SummarizeResponse"]:::ok

  R422 & R413 -. "no model call" .-> NoCall(("$"))
  classDef hidden display:none
  class NoCall hidden
```

---

## 4. Module map

| Layer       | Module                  | Responsibility                                                  | Imports from                |
|-------------|-------------------------|-----------------------------------------------------------------|-----------------------------|
| App         | `main.py`               | `create_app()` · middleware · router registration               | `api/`, `core/`             |
| HTTP        | `api/routes.py`         | `POST /summarize` — validate → 413 guard → call → build         | `models/`, `services/`, `core/` |
| HTTP        | `api/errors.py`         | Map `PayloadTooLargeError` / `SummarizerError` / validation → 413 / 502 / 422 | `models/`, `exceptions`     |
| Domain      | `services/summarizer.py`| The single OpenAI call (timeout + ≤1 retry). Mockable.          | `core/config`, `openai`     |
| Contracts   | `models/schemas.py`     | `SummarizeRequest` / `SummarizeResponse` / `ErrorResponse`      | `pydantic`                  |
| Core        | `core/config.py`        | `Settings` from env (key, model, timeout, caps, retries)        | `os` / `pydantic-settings`  |
| Core        | `core/logging.py`       | Metadata-only logger. **Never the user's text.**                | `logging`                   |
| Cross       | `exceptions.py`         | `SummarizerError`, `PayloadTooLargeError`                       | —                           |

---

## 5. Runtime topology

```mermaid
flowchart LR
  classDef ext fill:#fef3c7,stroke:#b45309,color:#1f2937
  classDef host fill:#e0f2fe,stroke:#0369a1,color:#0c4a6e
  classDef proc fill:#dcfce7,stroke:#15803d,color:#14532d

  Caller(["Trusted client<br/>(internal network)"]):::ext
  subgraph Host["Container · slim Python 3.12 image"]
    direction TB
    UV["uvicorn :8000"]:::host
    App["FastAPI app<br/>summarizer_service"]:::proc
    UV --> App
  end
  OpenAI[["OpenAI API<br/>(HTTPS)"]]:::ext
  EnvBox[("Environment<br/>OPENAI_API_KEY · MODEL · TIMEOUT")]:::ext

  Caller -- "HTTP POST /summarize" --> UV
  App -- "1 call · 30 s · ≤1 retry" --> OpenAI
  EnvBox -. "injected at start" .-> App
```

**Stateless · no DB · no cache · no auth (v1).** Horizontal scaling is "run more containers."

---

## 6. Architectural invariants

| # | Invariant                                                   | Enforced by                       | Spec ref |
|---|-------------------------------------------------------------|-----------------------------------|----------|
| I1 | Exactly **one** OpenAI call per successful request          | `services/summarizer.py`          | R9, §6   |
| I2 | **No model call** for invalid input (422 / 413)             | `api/routes.py` (guard before call)| R2, R3   |
| I3 | **No raw user text** in logs, traces, or responses          | `core/logging.py` · `api/errors.py`| R7, §3   |
| I4 | Secrets only from env; never returned, never logged         | `core/config.py`                  | §3       |
| I5 | Every response carries `request_id` + `X-Request-ID` header | RequestID middleware in `main.py` | R5       |
| I6 | The model client is **injectable** (FastAPI dependency)     | `services/summarizer.py`          | §7 (tests) |
| I7 | Stateless — no session, no persistence                      | Whole app                         | §6       |
