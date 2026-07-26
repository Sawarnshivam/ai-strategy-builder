"""ORM model registry — import every model so Alembic autogenerate sees it."""

from app.models.backtest_run import BacktestRun
from app.models.strategy import Strategy
from app.models.user import User

__all__ = ["BacktestRun", "Strategy", "User"]