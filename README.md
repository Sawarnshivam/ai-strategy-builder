# AI Backtest Platform

Describe a trading strategy in natural language, have Claude translate it into
executable strategy logic, and backtest it with VectorBT.

## Stack
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** Next.js (App Router) + TypeScript
- **AI:** Anthropic Claude API
- **Backtesting:** VectorBT

## Local Development

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs