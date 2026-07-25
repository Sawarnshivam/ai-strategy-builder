"""The OHLCVProvider protocol every price source implements."""

from typing import Protocol, runtime_checkable

import pandas as pd

from app.market_data.models import BarRequest


@runtime_checkable
class OHLCVProvider(Protocol):
    """Provider-agnostic interface for fetching OHLCV bars.

    Implementations return a DataFrame indexed by a UTC DatetimeIndex named
    'timestamp', with exactly the OHLCV_COLUMNS as float columns (volume too).
    """

    def get_bars(self, request: BarRequest) -> pd.DataFrame:
        """Return OHLCV bars for the request as a validated DataFrame."""
        ...