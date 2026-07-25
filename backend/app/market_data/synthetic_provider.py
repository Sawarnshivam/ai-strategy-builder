"""A deterministic synthetic OHLCV source for tests and offline development.

Generates a seeded geometric random walk, so the same BarRequest always yields
byte-identical bars. This is what makes backtests reproducible: no network, no
clock dependence, no run-to-run variation.
"""

import numpy as np
import pandas as pd

from app.core.exceptions import MarketDataError
from app.market_data.models import OHLCV_COLUMNS, TIMEFRAME_TO_FREQ, BarRequest
from app.market_data.validation import validate_ohlcv

_BASE_PRICE = 100.0
_DRIFT = 0.0002
_VOLATILITY = 0.01


class SyntheticOHLCVProvider:
    """Produces reproducible pseudo-market data from a fixed seed."""

    def __init__(self, seed: int = 42) -> None:
        self._seed = seed

    def _stable_offset(self, request: BarRequest) -> int:
        """Derive a per-symbol seed offset so different symbols differ but repeat."""
        return abs(hash(request.symbol)) % 10_000

    def get_bars(self, request: BarRequest) -> pd.DataFrame:
        """Generate a seeded random-walk OHLCV frame for the request."""
        freq = TIMEFRAME_TO_FREQ.get(request.timeframe)
        if freq is None:
            raise MarketDataError(f"Unsupported timeframe {request.timeframe!r}.")

        index = pd.date_range(
            start=request.start,
            end=request.end,
            freq=freq,
            tz="UTC",
            name="timestamp",
        )
        if len(index) == 0:
            raise MarketDataError("Requested window contains no bars.")

        rng = np.random.default_rng(self._seed + self._stable_offset(request))
        n = len(index)

        returns = rng.normal(loc=_DRIFT, scale=_VOLATILITY, size=n)
        close = _BASE_PRICE * np.exp(np.cumsum(returns))
        open_ = np.empty(n)
        open_[0] = _BASE_PRICE
        open_[1:] = close[:-1]

        intrabar = np.abs(rng.normal(loc=0.0, scale=_VOLATILITY, size=n)) * close
        high = np.maximum(open_, close) + intrabar
        low = np.minimum(open_, close) - intrabar
        volume = rng.uniform(1_000, 10_000, size=n)

        frame = pd.DataFrame(
            {
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            },
            index=index,
            columns=list(OHLCV_COLUMNS),
        )
        return validate_ohlcv(frame)