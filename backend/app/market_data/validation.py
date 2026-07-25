"""Shared validation enforcing the OHLCV DataFrame contract.

Every provider runs its output through this before returning, so a consumer can
trust the shape without re-checking. Bad data fails here, close to its source,
instead of surfacing as a confusing error deep in the backtester.
"""

import pandas as pd

from app.core.exceptions import MarketDataError
from app.market_data.models import OHLCV_COLUMNS


def validate_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    """Assert the OHLCV contract and return the frame unchanged.

    Checks column set, index type, monotonicity, and the high/low invariant.
    Raises MarketDataError on any violation.
    """
    if list(frame.columns) != list(OHLCV_COLUMNS):
        raise MarketDataError(
            f"OHLCV columns must be {OHLCV_COLUMNS}, got {tuple(frame.columns)}."
        )

    if not isinstance(frame.index, pd.DatetimeIndex):
        raise MarketDataError("OHLCV frame must have a DatetimeIndex.")

    if frame.index.name != "timestamp":
        raise MarketDataError("OHLCV index must be named 'timestamp'.")

    if not frame.index.is_monotonic_increasing:
        raise MarketDataError("OHLCV timestamps must be sorted ascending.")

    if frame.index.has_duplicates:
        raise MarketDataError("OHLCV timestamps must be unique.")

    if frame.empty:
        raise MarketDataError("OHLCV frame is empty for the requested window.")

    high_ok = (frame["high"] >= frame["low"]).all()
    if not bool(high_ok):
        raise MarketDataError("OHLCV invariant violated: some high < low.")

    return frame