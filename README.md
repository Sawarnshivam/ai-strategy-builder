# AI Strategy Builder

Describe a trading strategy in plain language, get a structured spec, backtest it on
deterministic data, and optimise its parameters — all in a dark, terminal-style workspace.

## Stack

- **Backend** — FastAPI, SQLAlchemy 2.0, Alembic, Postgres, pandas/numpy backtester,
  Anthropic SDK (with a fake client for key-less runs), JWT auth.
- **Frontend** — Next.js (App Router), TypeScript, Tailwind v4, Zustand, Recharts.

## Prerequisites

- Python 3.12, Node 22, Docker (for Postgres).

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate.bat        # Windows
pip install -r requirements-dev.txt
docker compose -f ..\docker-compose.yml up -d postgres
alembic upgrade head
uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs. Without an `ANTHROPIC_API_KEY` the app uses a
fake LLM client — spec-mode backtests and sweeps work fully; natural-language generation
needs a real key in `backend/.env`.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

App at http://localhost:3000. Sign up, then describe or paste a strategy spec.

## Checks

```bash
# backend
cd backend && ruff check . && mypy app && pytest

# frontend
cd frontend && npm run lint && npm run build
```

CI runs all of the above on every push and pull request.

## Deployment

The whole stack runs as three containers (Postgres, backend, frontend) via
`docker-compose.prod.yml`. It is host-agnostic — anywhere Docker runs.

1. Copy the env template and fill in real secrets:

```bash
   cp .env.prod.example .env.prod
   # set a strong POSTGRES_PASSWORD and a long random JWT_SECRET
```

2. Build and start:

```bash
   docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

   The backend runs migrations automatically on start, then serves on :8000.
   The frontend serves on :3000.

3. Open http://localhost:3000, sign up, and use it.

To deploy on a remote host, copy the repo (or pull it) onto a Docker-capable
server, set `CORS_ORIGINS` and `NEXT_PUBLIC_API_BASE_URL` to the server's public
URLs in `.env.prod`, and run the same compose command. Put a reverse proxy
(Caddy, nginx, Traefik) in front for TLS.

Stop with `docker compose -f docker-compose.prod.yml down` (add `-v` to wipe the
database volume).