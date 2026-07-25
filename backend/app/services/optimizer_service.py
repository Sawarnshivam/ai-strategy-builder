"""Grid-search over a single indicator parameter.

Fetches bars once and reuses them for every parameter value, so all runs are
compared on identical data. Each run clones the spec, overrides one indicator
parameter, backtests, and records the metrics. Results are ranked by the chosen
metric — drawdown ascending (less is better), everything else descending.
"""

from datetime import UTC, datetime, timedelta

import pandas as pd

from app.ai.strategy_spec import StrategySpec
from app.backtesting.backtester import Backtester
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.market_data.models import BarRequest
from app.market_data.provider import OHLCVProvider
from app.schemas.backtest import MetricsSchema
from app.schemas.optimize import SweepPoint, SweepRequest, SweepResponse
from app.services.backtest_service import DEFAULT_LOOKBACK_DAYS, LOOKBACK_DAYS

logger = get_logger(__name__)

# Metrics where a smaller value is better rank higher when ascending.
_ASCENDING_METRICS = frozenset({"max_drawdown_pct"})


class OptimizerService:
    """Runs a parameter sweep and ranks the configurations."""

    def __init__(self, provider: OHLCVProvider) -> None:
        self._provider = provider

    def sweep(self, request: SweepRequest) -> SweepResponse:
        """Execute the grid search and return ranked results."""
        self._require_indicator_param(request)
        ohlcv = self._fetch_bars(request.spec)
        values = self._frange(request.start, request.stop, request.step)

        backtester = Backtester(initial_capital=request.initial_capital)
        points: list[SweepPoint] = []
        for value in values:
            candidate = self._with_param(request, value)
            result = backtester.run(candidate, ohlcv)
            points.append(
                SweepPoint(
                    value=value,
                    metrics=MetricsSchema.model_validate(
                        result.metrics, from_attributes=True
                    ),
                    final_equity=result.final_equity,
                )
            )

        ranked = self._rank(points, request.rank_by)
        logger.info(
            "Swept %s.%s over %d values; best %s at %s",
            request.indicator_name,
            request.param,
            len(ranked),
            request.rank_by,
            ranked[0].value,
        )
        return SweepResponse(
            indicator_name=request.indicator_name,
            param=request.param,
            rank_by=request.rank_by,
            best_value=ranked[0].value,
            points=ranked,
        )

    @staticmethod
    def _require_indicator_param(request: SweepRequest) -> None:
        """Ensure the named indicator and param exist in the spec."""
        for indicator in request.spec.indicators:
            if indicator.name == request.indicator_name:
                return
        raise ValidationError(
            f"Indicator {request.indicator_name!r} is not declared in the spec."
        )

    def _fetch_bars(self, spec: StrategySpec) -> pd.DataFrame:
        """Pull one window of bars, reused across the whole sweep."""
        days = LOOKBACK_DAYS.get(spec.timeframe, DEFAULT_LOOKBACK_DAYS)
        end = datetime.now(UTC)
        start = end - timedelta(days=days)
        return self._provider.get_bars(
            BarRequest(symbol=spec.symbol, timeframe=spec.timeframe, start=start, end=end)
        )

    @staticmethod
    def _with_param(request: SweepRequest, value: float) -> StrategySpec:
        """Return a deep copy of the spec with one indicator param overridden."""
        clone = request.spec.model_copy(deep=True)
        for indicator in clone.indicators:
            if indicator.name == request.indicator_name:
                indicator.params[request.param] = value
        return clone

    @staticmethod
    def _frange(start: float, stop: float, step: float) -> list[float]:
        """Inclusive float range, rounded to avoid FP drift."""
        values: list[float] = []
        current = start
        while current <= stop + 1e-9:
            values.append(round(current, 6))
            current += step
        return values

    @staticmethod
    def _rank(points: list[SweepPoint], rank_by: str) -> list[SweepPoint]:
        """Sort points best-first by the chosen metric."""
        ascending = rank_by in _ASCENDING_METRICS
        return sorted(
            points,
            key=lambda p: getattr(p.metrics, rank_by),
            reverse=not ascending,
        )