"""Builds the configured OHLCV provider (synthetic, wrapped in a cache)."""

from app.core.config import Settings
from app.core.logging import get_logger
from app.market_data.cached_provider import CachedOHLCVProvider
from app.market_data.provider import OHLCVProvider
from app.market_data.synthetic_provider import SyntheticOHLCVProvider

logger = get_logger(__name__)


def build_ohlcv_provider(settings: Settings) -> OHLCVProvider:
    """Return a cache-wrapped synthetic provider.

    A real market source can be slotted in here later; for now the synthetic
    source keeps backtests deterministic and offline.
    """
    base = SyntheticOHLCVProvider(seed=settings.market_data_synthetic_seed)
    logger.info("Market data provider: synthetic (seed=%s)", settings.market_data_synthetic_seed)
    return CachedOHLCVProvider(base, settings.market_data_cache_dir)