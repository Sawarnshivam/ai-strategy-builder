"""Queries scoped to the BacktestRun aggregate."""

from collections.abc import Sequence

from sqlalchemy import func, select

from app.models.backtest_run import BacktestRun
from app.repositories.base_repository import BaseRepository


class BacktestRepository(BaseRepository[BacktestRun]):
    """Read and write access for backtest runs."""

    model = BacktestRun

    def list(self, *, limit: int, offset: int) -> Sequence[BacktestRun]:
        """Return a page of runs, newest first."""
        stmt = (
            select(BacktestRun)
            .order_by(BacktestRun.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self._db.execute(stmt).scalars().all()

    def count(self) -> int:
        """Return the total number of runs."""
        stmt = select(func.count()).select_from(BacktestRun)
        return self._db.execute(stmt).scalar_one()