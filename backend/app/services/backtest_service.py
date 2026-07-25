"""Orchestrates spec resolution, data fetch, simulation and persistence."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

import pandas as pd

from app.ai.spec_generator import SpecGenerator
from app.ai.strategy_spec import StrategySpec
from app.backtesting.backtester import Backtester
from app.backtesting.models import BacktestResult
from app.core.logging import get_logger
from app.market_data.models import BarRequest
from app.market_data.provider import OHLCVProvider
from app.models.backtest_run import BacktestRun
from app.repositories.backtest_repository import BacktestRepository

logger = get_logger(__name__)

# How many days of history to pull per timeframe so backtests have enough bars.
LOOKBACK_DAYS = {
    "1m": 3,
    "5m": 10,
    "15m": 20,
    "1h": 120,
    "4h": 365,
    "1d": 1095,
}
DEFAULT_LOOKBACK_DAYS = 120

# Cap equity-curve points returned/stored so responses stay small.
MAX_CURVE_POINTS = 500


class BacktestService:
    """Turns a description or spec into a persisted, retrievable backtest run."""

    def __init__(
        self,
        provider: OHLCVProvider,
        spec_generator: SpecGenerator,
        repository: BacktestRepository,
    ) -> None:
        self._provider = provider
        self._spec_generator = spec_generator
        self._repo = repository

    async def run(
        self,
        *,
        description: str | None,
        spec: StrategySpec | None,
        strategy_id: uuid.UUID | None,
        initial_capital: float,
    ) -> BacktestRun:
        """Resolve a spec, fetch bars, simulate, and persist the run."""
        resolved = spec if spec is not None else await self._resolve_spec(description)

        ohlcv = self._fetch_bars(resolved)
        result = Backtester(initial_capital=initial_capital).run(resolved, ohlcv)

        run = self._persist(resolved, result, strategy_id)
        logger.info(
            "Backtest %s: return=%.2f%% trades=%d",
            run.id,
            result.metrics.total_return_pct,
            result.metrics.num_trades,
        )
        return run

    async def _resolve_spec(self, description: str | None) -> StrategySpec:
        """Generate a spec from a description via the LLM."""
        assert description is not None  # guaranteed by the request validator
        return await self._spec_generator.generate(description)

    def _fetch_bars(self, spec: StrategySpec) -> pd.DataFrame:
        """Pull an appropriate window of OHLCV bars for the spec."""
        days = LOOKBACK_DAYS.get(spec.timeframe, DEFAULT_LOOKBACK_DAYS)
        end = datetime.now(UTC)
        start = end - timedelta(days=days)
        request = BarRequest(
            symbol=spec.symbol,
            timeframe=spec.timeframe,
            start=start,
            end=end,
        )
        return self._provider.get_bars(request)

    def _persist(
        self,
        spec: StrategySpec,
        result: BacktestResult,
        strategy_id: uuid.UUID | None,
    ) -> BacktestRun:
        """Store the run with a downsampled equity curve."""
        curve = self._downsample_curve(result.equity_curve)
        run = BacktestRun(
            strategy_id=strategy_id,
            symbol=spec.symbol,
            timeframe=spec.timeframe,
            spec=spec.model_dump(mode="json"),
            metrics={
                "total_return_pct": result.metrics.total_return_pct,
                "annualized_return_pct": result.metrics.annualized_return_pct,
                "sharpe_ratio": result.metrics.sharpe_ratio,
                "max_drawdown_pct": result.metrics.max_drawdown_pct,
                "win_rate_pct": result.metrics.win_rate_pct,
                "num_trades": result.metrics.num_trades,
                "exposure_pct": result.metrics.exposure_pct,
            },
            equity_curve={"points": curve, "trades": result.trades},
            initial_capital=result.initial_capital,
            final_equity=result.final_equity,
        )
        self._repo.add(run)
        self._repo.db.commit()
        self._repo.db.refresh(run)
        return run

    @staticmethod
    def _downsample_curve(equity: "pd.Series") -> list[dict[str, float | str]]:
        """Reduce the equity curve to at most MAX_CURVE_POINTS points."""
        n = len(equity)
        step = max(1, n // MAX_CURVE_POINTS)
        sampled = equity.iloc[::step]
        points: list[dict[str, float | str]] = []
        for ts, value in sampled.items():
            timestamp = cast(pd.Timestamp, ts).isoformat()
            points.append({"timestamp": timestamp, "equity": float(value)})
        return points

    def get(self, run_id: uuid.UUID) -> BacktestRun | None:
        """Return a single run by id."""
        return self._repo.get(run_id)

    def list(self, *, limit: int, offset: int) -> tuple[list[BacktestRun], int]:
        """Return a page of runs plus the total count."""
        items = list(self._repo.list(limit=limit, offset=offset))
        return items, self._repo.count()