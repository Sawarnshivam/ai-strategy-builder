"""Tests for metric computations against hand-computed values."""

import pandas as pd

from app.backtesting.metrics import _max_drawdown_pct, compute_metrics


def _series(values: list[float]) -> pd.Series:
    index = pd.date_range("2024-01-01", periods=len(values), freq="1d", tz="UTC")
    return pd.Series(values, index=index)


def test_max_drawdown_simple() -> None:
    """A drop from a peak of 120 down to 80 is a 33.33% drawdown."""
    equity = _series([100, 120, 80, 90])

    assert round(_max_drawdown_pct(equity), 2) == 33.33


def test_total_return_and_trade_stats() -> None:
    """Total return and win rate follow directly from the inputs."""
    equity = _series([100, 110])
    returns = _series([0.0, 0.1])
    position = _series([1.0, 1.0])
    trades = [5.0, -2.0, 3.0]

    metrics = compute_metrics(equity, returns, trades, position, "1d")

    assert metrics.total_return_pct == 10.0
    assert metrics.num_trades == 3
    assert round(metrics.win_rate_pct, 2) == round(2 / 3 * 100, 2)
    assert metrics.exposure_pct == 100.0