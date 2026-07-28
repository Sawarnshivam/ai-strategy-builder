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