# QuickShift

A two-sided marketplace connecting businesses with hourly workers — plus an AI staffing agent that lets a business fill a shift just by describing what they need in plain English.

> "I need 3 experienced bartenders for a fast-paced upscale restaurant this Saturday night" → the agent resolves the date, builds a semantic search, blends it with the business's own culture/vibe, ranks candidates, and can post the shift — all in one turn.

## Highlights

- **AI staffing agent** — OpenAI function-calling agent (`search_workers`, `post_shift`) with streaming responses over SSE, conversational history, and natural-language date/time resolution ("tomorrow night", "midnight" → next-day rollover).
- **Semantic worker search** — `pgvector` embeddings (`text-embedding-3-small`) over worker profiles, blended 60/40 with the business's own culture embedding so results reflect *fit*, not just keyword match. Metro-area clustering (e.g. a San Francisco search also surfaces Oakland/Berkeley) layered on top of SQL filters before the vector rank.
- **Redis caching** — embeddings cached by content hash (24h TTL), search results cached by query fingerprint (5m TTL), with cache invalidation on worker writes so results never go stale.
- **Agent observability** — every agent turn is persisted with latency, input/output token counts, tool calls and arguments, and error traces — queryable via a `/agent/conversations` endpoint.
- **Auth & marketplace core** — JWT-based auth for businesses and workers, shift CRUD (post/pause/edit/delete), and a match pipeline (interested → accepted/declined).

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI (async), SQLAlchemy 2.0, PostgreSQL + pgvector, Redis |
| AI | OpenAI (chat completions + embeddings), custom tool-calling agent loop |
| Frontend | React 18, React Router, Sass, Vite |
| Infra | Docker Compose, Gunicorn + Uvicorn workers |

## Architecture

```
React (Vite) ── REST/SSE ──▶ FastAPI
                               ├── auth (JWT)
                               ├── shifts / matches
                               └── agent ─┬─ OpenAI (function calling + streaming)
                                          ├─ search_workers ─▶ pgvector similarity + SQL filters
                                          └─ post_shift     ─▶ Postgres
                               Redis: embedding cache · search-result cache
```

## Running locally

```bash
docker compose up
```

- Frontend → `localhost:5173`
- API → `localhost:8000`
- Postgres (pgvector) and Redis spin up with health checks; the backend waits on both before seeding the schema.

## Project layout

```
backend/app/
  agent/        tool-calling agent loop (streaming, logging, retries)
  llm/          LLM provider abstraction (OpenAI implementation)
  tools/        agent tools — search_workers, post_shift
  api/          auth, shifts, matches, agent routers
  models/       SQLAlchemy models (incl. pgvector columns)
  utils/        embeddings, Redis cache helpers, config

frontend/src/
  pages/        landing, auth, business dashboard, worker feed, matches
  components/   shared UI (cards, dialogs, toasts)
  services/     API + auth clients
```
