"""ORM model recording a single backtest execution and its results."""

import uuid
from typing import Any

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class BacktestRun(Base, TimestampMixin):
    """A persisted backtest: the spec that ran, its metrics, and the equity curve.

    Stored self-contained (spec + metrics + curve as JSONB) so a run can be
    re-read and re-rendered without recomputation. Optionally linked to a saved
    Strategy, but a run can also be ad-hoc with no parent strategy.
    """

    __tablename__ = "backtest_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    strategy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    spec: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    equity_curve: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    initial_capital: Mapped[float] = mapped_column(Float, nullable=False)
    final_equity: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self) -> str:
        """Return a debug representation of the run."""
        return f"<BacktestRun id={self.id} symbol={self.symbol!r}>"