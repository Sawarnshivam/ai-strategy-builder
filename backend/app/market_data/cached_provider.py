"""A caching decorator that wraps any OHLCVProvider with on-disk Parquet storage.

Repeated backtests over the same window shouldn't recompute or refetch bars.
This wraps a delegate provider, serving from disk on a hit and populating the
cache on a miss. It is provider-agnostic — it caches synthetic or real bars alike.
"""

from pathlib import Path

import pandas as pd

from app.core.logging import get_logger
from app.market_data.models import BarRequest
from app.market_data.provider import OHLCVProvider
from app.market_data.validation import validate_ohlcv

logger = get_logger(__name__)


class CachedOHLCVProvider:
    """Wraps a provider with a filesystem Parquet cache keyed by BarRequest."""

    def __init__(self, delegate: OHLCVProvider, cache_dir: str | Path) -> None:
        self._delegate = delegate
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, request: BarRequest) -> Path:
        return self._cache_dir / f"{request.cache_key()}.parquet"

    def get_bars(self, request: BarRequest) -> pd.DataFrame:
        """Return cached bars if present, otherwise fetch, validate, and store."""
        path = self._path_for(request)

        if path.exists():
            logger.debug("Market data cache hit: %s", path.name)
            frame = pd.read_parquet(path)
            return validate_ohlcv(frame)

        logger.debug("Market data cache miss: %s", path.name)
        frame = self._delegate.get_bars(request)
        frame.to_parquet(path)
        return frame