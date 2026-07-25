"""Pydantic schemas for backtest requests and results."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.ai.strategy_spec import StrategySpec


class BacktestRequestBody(BaseModel):
    """Request to run a backtest from either a description or a full spec.

    Exactly one of description/spec must be provided. A description is turned
    into a spec via the LLM; a spec runs directly.
    """

    description: str | None = Field(default=None, min_length=1, max_length=8000)
    spec: StrategySpec | None = None
    strategy_id: uuid.UUID | None = Field(
        default=None,
        description="Optional saved strategy to associate this run with.",
    )
    initial_capital: float = Field(default=10_000.0, gt=0)

    @model_validator(mode="after")
    def _exactly_one_source(self) -> "BacktestRequestBody":
        """Require exactly one of description or spec."""
        if (self.description is None) == (self.spec is None):
            raise ValueError("Provide exactly one of 'description' or 'spec'.")
        return self


class MetricsSchema(BaseModel):
    """Serialised backtest metrics."""

    total_return_pct: float
    annualized_return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    win_rate_pct: float
    num_trades: int
    exposure_pct: float


class EquityPoint(BaseModel):
    """A single (timestamp, equity) point on the curve."""

    timestamp: datetime
    equity: float


class BacktestResultResponse(BaseModel):
    """Full backtest result returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    symbol: str
    timeframe: str
    spec: StrategySpec
    metrics: MetricsSchema
    equity_curve: list[EquityPoint]
    trades: list[float]
    initial_capital: float
    final_equity: float
    created_at: datetime


class BacktestRunSummary(BaseModel):
    """Lightweight run listing (no equity curve or trades)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    strategy_id: uuid.UUID | None
    symbol: str
    timeframe: str
    metrics: MetricsSchema
    final_equity: float
    created_at: datetime


class BacktestRunListResponse(BaseModel):
    """Paginated list of run summaries."""

    items: list[BacktestRunSummary]
    total: int
    limit: int
    offset: int