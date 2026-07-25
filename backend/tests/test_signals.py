"""Tests for rule evaluation into boolean signals."""

import pandas as pd

from app.ai.strategy_spec import StrategySpec
from app.backtesting.signals import build_indicator_frame, evaluate_rules


def _spec() -> StrategySpec:
    return StrategySpec.model_validate(
        {
            "name": "t",
            "symbol": "BTC-USD",
            "timeframe": "1h",
            "indicators": [{"name": "sma_fast", "type": "sma", "params": {"period": 2}}],
            "entry_rules": [{"left": "price", "comparator": "greater_than", "right": "sma_fast"}],
        }
    )


def _ohlcv(closes: list[float]) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=len(closes), freq="1h", tz="UTC", name="timestamp")
    close = pd.Series(closes, index=index)
    return pd.DataFrame(
        {"open": close, "high": close, "low": close, "close": close, "volume": close}
    )


def test_greater_than_produces_expected_signal() -> None:
    """price > sma_fast triggers where close exceeds its moving average."""
    spec = _spec()
    ohlcv = _ohlcv([10, 11, 12, 13])
    indicators = build_indicator_frame(spec, ohlcv)

    signal = evaluate_rules(spec.entry_rules, ohlcv, indicators)

    assert signal.dtype == bool
    assert signal.iloc[-1]  # rising series: price above its SMA


def test_empty_rules_yield_all_false() -> None:
    """No rules means a never-True signal (used for absent exit rules)."""
    spec = _spec()
    ohlcv = _ohlcv([10, 11, 12])
    indicators = build_indicator_frame(spec, ohlcv)

    signal = evaluate_rules([], ohlcv, indicators)

    assert not signal.any()


def test_numeric_operand_resolves() -> None:
    """A rule can compare an indicator to a numeric literal."""
    spec = StrategySpec.model_validate(
        {
            "name": "t",
            "symbol": "BTC-USD",
            "timeframe": "1h",
            "indicators": [{"name": "rsi", "type": "rsi", "params": {"period": 2}}],
            "entry_rules": [{"left": "rsi", "comparator": "less_than", "right": "50"}],
        }
    )
    ohlcv = _ohlcv([10, 9, 8, 7])
    indicators = build_indicator_frame(spec, ohlcv)

    signal = evaluate_rules(spec.entry_rules, ohlcv, indicators)

    assert signal.iloc[-1]  # falling series: RSI below 50