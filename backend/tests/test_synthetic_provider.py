"""Tests for the deterministic synthetic OHLCV provider."""

from datetime import UTC, datetime

import pytest

from app.core.exceptions import MarketDataError
from app.market_data.models import OHLCV_COLUMNS, BarRequest
from app.market_data.synthetic_provider import SyntheticOHLCVProvider

_START = datetime(2024, 5, 27, tzinfo=UTC)
_END = datetime(2024, 6, 1, tzinfo=UTC)


def _request(symbol: str = "BTC-USD", timeframe: str = "1h") -> BarRequest:
    return BarRequest(symbol=symbol, timeframe=timeframe, start=_START, end=_END)


def test_output_matches_ohlcv_contract(synthetic_provider: SyntheticOHLCVProvider) -> None:
    """Generated frames have the right columns, index, and invariants."""
    frame = synthetic_provider.get_bars(_request())

    assert list(frame.columns) == list(OHLCV_COLUMNS)
    assert frame.index.name == "timestamp"
    assert frame.index.is_monotonic_increasing
    assert (frame["high"] >= frame["low"]).all()


def test_generation_is_deterministic(synthetic_provider: SyntheticOHLCVProvider) -> None:
    """The same request yields identical data across calls."""
    request = _request()

    first = synthetic_provider.get_bars(request)
    second = synthetic_provider.get_bars(request)

    assert first.equals(second)


def test_different_symbols_differ(synthetic_provider: SyntheticOHLCVProvider) -> None:
    """Distinct symbols produce distinct series."""
    btc = synthetic_provider.get_bars(_request(symbol="BTC-USD"))
    eth = synthetic_provider.get_bars(_request(symbol="ETH-USD"))

    assert not btc["close"].equals(eth["close"])


def test_unsupported_timeframe_raises(synthetic_provider: SyntheticOHLCVProvider) -> None:
    """An unknown timeframe is rejected."""
    with pytest.raises(MarketDataError, match="Unsupported timeframe"):
        synthetic_provider.get_bars(_request(timeframe="7s"))