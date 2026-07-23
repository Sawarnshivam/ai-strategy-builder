"""Queries scoped to the Strategy aggregate."""

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select

from app.models.strategy import Strategy
from app.repositories.base_repository import BaseRepository


class StrategyRepository(BaseRepository[Strategy]):
    """Read and write access for strategies."""

    model = Strategy

    def _base_query(self, search: str | None) -> Select[tuple[Strategy]]:
        """Build the shared SELECT used by both listing and counting."""
        stmt = select(Strategy)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Strategy.name.ilike(pattern),
                    Strategy.description.ilike(pattern),
                )
            )
        return stmt

    def list(
        self,
        *,
        limit: int,
        offset: int,
        search: str | None = None,
    ) -> Sequence[Strategy]:
        """Return a page of strategies, newest first."""
        stmt = (
            self._base_query(search)
            .order_by(Strategy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self._db.execute(stmt).scalars().all()

    def count_matching(self, search: str | None = None) -> int:
        """Return how many strategies match the filter, ignoring pagination."""
        stmt = select(func.count()).select_from(self._base_query(search).subquery())
        return self._db.execute(stmt).scalar_one()

    def get_by_name(self, name: str) -> Strategy | None:
        """Return a strategy by its exact name, or None."""
        stmt = select(Strategy).where(Strategy.name == name)
        return self._db.execute(stmt).scalars().first()