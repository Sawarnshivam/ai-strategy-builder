"""Pydantic schemas for parameter-sweep optimization."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.ai.strategy_spec import StrategySpec
from app.schemas.backtest import MetricsSchema

# Metrics a sweep can rank by. Drawdown ranks ascending; the rest descending.
RANKABLE_METRICS = (
    "total_return_pct",
    "annualized_return_pct",
    "sharpe_ratio",
    "win_rate_pct",
    "max_drawdown_pct",
)


class SweepRequest(BaseModel):
    """Request to sweep one indicator parameter across a numeric range."""

    spec: StrategySpec
    indicator_name: str = Field(
        ...,
        min_length=1,
        description="The `name` of the indicator in the spec to sweep.",
        examples=["sma"],
    )
    param: str = Field(
        ...,
        min_length=1,
        description="The parameter key on that indicator to vary.",
        examples=["period"],
    )
    start: float = Field(..., description="First value in the sweep (inclusive).")
    stop: float = Field(..., description="Last value in the sweep (inclusive).")
    step: float = Field(..., gt=0, description="Increment between values.")
    rank_by: str = Field(default="sharpe_ratio", examples=["sharpe_ratio"])
    initial_capital: float = Field(default=10_000.0, gt=0)

    @model_validator(mode="after")
    def _validate(self) -> "SweepRequest":
        """Guard the range size and the rank metric."""
        if self.stop < self.start:
            raise ValueError("'stop' must be >= 'start'.")
        if self.rank_by not in RANKABLE_METRICS:
            raise ValueError(f"rank_by must be one of {RANKABLE_METRICS}.")
        count = int((self.stop - self.start) / self.step) + 1
        if count > 100:
            raise ValueError("Sweep would exceed 100 runs; widen the step.")
        return self


class SweepPoint(BaseModel):
    """One configuration's result within a sweep."""

    model_config = ConfigDict(from_attributes=True)

    value: float
    metrics: MetricsSchema
    final_equity: float


class SweepResponse(BaseModel):
    """The full sweep result, ranked best-first by the chosen metric."""

    indicator_name: str
    param: str
    rank_by: str
    best_value: float
    points: list[SweepPoint]