"""Value objects describing a market-data request and the OHLCV contract.

The OHLCV DataFrame shape is fixed here so every provider and every consumer
agrees on columns, index, and dtypes. A shared constant beats each module
re-deriving the schema and drifting.
"""

from dataclasses import dataclass
from datetime import datetime

# The canonical column set every provider must return, in this order.
OHLCV_COLUMNS = ("open", "high", "low", "close", "volume")

# Supported bar sizes mapped to their pandas frequency alias.
TIMEFRAME_TO_FREQ = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "1h": "1h",
    "4h": "4h",
    "1d": "1D",
}


@dataclass(frozen=True, slots=True)
class BarRequest:
    """A request for a window of OHLCV bars.

    start/end are timezone-aware UTC datetimes; timeframe is one of
    TIMEFRAME_TO_FREQ's keys. Frozen so it can be used as a cache key component.
    """

    symbol: str
    timeframe: str
    start: datetime
    end: datetime

    def cache_key(self) -> str:
        """A filesystem-safe key uniquely identifying this request."""
        safe_symbol = self.symbol.replace("/", "-").replace(":", "-")
        start_stamp = self.start.strftime("%Y%m%dT%H%M%S")
        end_stamp = self.end.strftime("%Y%m%dT%H%M%S")
        return f"{safe_symbol}_{self.timeframe}_{start_stamp}_{end_stamp}"