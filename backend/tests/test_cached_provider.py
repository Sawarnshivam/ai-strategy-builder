"""Tests for the on-disk caching provider wrapper."""

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from app.market_data.cached_provider import CachedOHLCVProvider
from app.market_data.models import BarRequest
from app.market_data.synthetic_provider import SyntheticOHLCVProvider


class _CountingProvider:
    """Wraps synthetic generation and counts how often it is invoked."""

    def __init__(self) -> None:
        self._inner = SyntheticOHLCVProvider(seed=1)
        self.calls = 0

    def get_bars(self, request: BarRequest) -> pd.DataFrame:
        self.calls += 1
        return self._inner.get_bars(request)


def _request() -> BarRequest:
    return BarRequest(
        symbol="BTC-USD",
        timeframe="1h",
        start=datetime(2024, 5, 27, tzinfo=UTC),
        end=datetime(2024, 6, 1, tzinfo=UTC),
    )


def test_second_call_is_served_from_cache(tmp_path: Path) -> None:
    """A repeated request hits disk, not the delegate."""
    counting = _CountingProvider()
    cached = CachedOHLCVProvider(counting, tmp_path)
    request = _request()

    first = cached.get_bars(request)
    second = cached.get_bars(request)

    assert counting.calls == 1
    assert first.equals(second)


def test_cache_file_is_written(tmp_path: Path) -> None:
    """The cache persists a parquet file keyed by the request."""
    cached = CachedOHLCVProvider(SyntheticOHLCVProvider(seed=1), tmp_path)
    request = _request()

    cached.get_bars(request)

    expected = tmp_path / f"{request.cache_key()}.parquet"
    assert expected.exists()