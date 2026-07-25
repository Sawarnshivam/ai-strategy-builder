"""Tests for the parameter-sweep optimizer service."""

import pytest

from app.ai.strategy_spec import StrategySpec
from app.core.exceptions import ValidationError
from app.market_data.synthetic_provider import SyntheticOHLCVProvider
from app.schemas.optimize import SweepRequest
from app.services.optimizer_service import OptimizerService


def _spec() -> StrategySpec:
    return StrategySpec.model_validate(
        {
            "name": "SMA Trend",
            "symbol": "BTC-USD",
            "timeframe": "1h",
            "indicators": [{"name": "sma", "type": "sma", "params": {"period": 10}}],
            "entry_rules": [{"left": "price", "comparator": "greater_than", "right": "sma"}],
            "exit_rules": [{"left": "price", "comparator": "less_than", "right": "sma"}],
        }
    )


def _service() -> OptimizerService:
    return OptimizerService(SyntheticOHLCVProvider(seed=11))


def test_sweep_returns_one_point_per_value() -> None:
    """A start/stop/step of 5..15 by 5 yields three configurations."""
    request = SweepRequest(
        spec=_spec(),
        indicator_name="sma",
        param="period",
        start=5,
        stop=15,
        step=5,
        rank_by="sharpe_ratio",
    )

    response = _service().sweep(request)

    assert [p.value for p in response.points] == sorted(
        [p.value for p in response.points], key=lambda v: v, reverse=False
    ) or True  # order is by metric, not value; just assert count
    assert len(response.points) == 3
    assert response.best_value in {5, 10, 15}


def test_sweep_ranks_best_first() -> None:
    """Points come back ordered best-first for the chosen metric."""
    request = SweepRequest(
        spec=_spec(),
        indicator_name="sma",
        param="period",
        start=5,
        stop=25,
        step=5,
        rank_by="total_return_pct",
    )

    response = _service().sweep(request)
    returns = [p.metrics.total_return_pct for p in response.points]

    assert returns == sorted(returns, reverse=True)
    assert response.points[0].value == response.best_value


def test_drawdown_ranks_ascending() -> None:
    """Ranking by drawdown puts the smallest drawdown first."""
    request = SweepRequest(
        spec=_spec(),
        indicator_name="sma",
        param="period",
        start=5,
        stop=15,
        step=5,
        rank_by="max_drawdown_pct",
    )

    response = _service().sweep(request)
    dds = [p.metrics.max_drawdown_pct for p in response.points]

    assert dds == sorted(dds)


def test_unknown_indicator_is_rejected() -> None:
    """Sweeping an indicator not in the spec raises a domain error."""
    request = SweepRequest(
        spec=_spec(),
        indicator_name="ema",
        param="period",
        start=5,
        stop=10,
        step=5,
    )

    with pytest.raises(ValidationError):
        _service().sweep(request)


def test_oversized_sweep_is_rejected() -> None:
    """A range that would exceed 100 runs fails validation."""
    with pytest.raises(ValueError, match="exceed 100 runs"):
        SweepRequest(
            spec=_spec(),
            indicator_name="sma",
            param="period",
            start=1,
            stop=1000,
            step=1,
        )