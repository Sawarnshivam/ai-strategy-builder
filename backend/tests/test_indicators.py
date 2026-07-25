"""Unit tests for indicator calculations against known values."""

import numpy as np
import pandas as pd

from app.ai.strategy_spec import IndicatorType
from app.backtesting.indicators import compute_indicator


def _frame(closes: list[float]) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=len(closes), freq="1h", tz="UTC", name="timestamp")
    close = pd.Series(closes, index=index)
    return pd.DataFrame(
        {
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": pd.Series(1000.0, index=index),
        }
    )


def test_sma_matches_manual_mean() -> None:
    """A 3-period SMA equals the rolling arithmetic mean."""
    frame = _frame([1, 2, 3, 4, 5])
    result = compute_indicator(IndicatorType.SMA, frame, {"period": 3})

    assert result.iloc[2] == 2.0
    assert result.iloc[4] == 4.0


def test_ema_first_value_equals_first_close() -> None:
    """With adjust=False, the EMA seeds on the first close."""
    frame = _frame([10, 20, 30])
    result = compute_indicator(IndicatorType.EMA, frame, {"period": 2})

    assert result.iloc[0] == 10.0
    assert result.iloc[-1] > result.iloc[0]


def test_rsi_all_gains_approaches_100() -> None:
    """A monotonically rising series drives RSI toward 100."""
    frame = _frame(list(range(1, 30)))
    result = compute_indicator(IndicatorType.RSI, frame, {"period": 14})

    assert result.iloc[-1] > 95.0


def test_rsi_bounds() -> None:
    """RSI stays within [0, 100] on noisy input."""
    rng = np.random.default_rng(0)
    frame = _frame(list(100 + rng.normal(0, 5, 100).cumsum()))
    result = compute_indicator(IndicatorType.RSI, frame, {"period": 14})

    assert result.min() >= 0.0
    assert result.max() <= 100.0