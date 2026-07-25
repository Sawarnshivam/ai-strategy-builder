"""Diagnostic endpoint to preview generated OHLCV bars."""

from datetime import UTC, datetime, timedelta
from typing import cast

import pandas as pd
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_ohlcv_provider
from app.market_data.models import BarRequest
from app.market_data.provider import OHLCVProvider
from app.schemas.market_data import BarPreview, BarsResponse

router = APIRouter(prefix="/market-data", tags=["market-data"])

_PREVIEW_ROWS = 5


def _to_previews(frame: pd.DataFrame) -> list[BarPreview]:
    """Convert head+tail of a frame into API bar previews."""
    sample = pd.concat([frame.head(_PREVIEW_ROWS), frame.tail(_PREVIEW_ROWS)])
    sample = sample[~sample.index.duplicated(keep="first")]
    previews: list[BarPreview] = []
    for timestamp, row in sample.iterrows():
        ts = cast(pd.Timestamp, timestamp).to_pydatetime()
        previews.append(
            BarPreview(
                timestamp=ts,
                open=float(row.open),
                high=float(row.high),
                low=float(row.low),
                close=float(row.close),
                volume=float(row.volume),
            )
        )
    return previews


@router.get(
    "/preview",
    response_model=BarsResponse,
    summary="Preview generated OHLCV bars (diagnostic)",
)
def preview_bars(
    symbol: str = Query(default="BTC-USD", max_length=20),
    timeframe: str = Query(default="1h", max_length=10),
    days: int = Query(default=30, ge=1, le=365),
    provider: OHLCVProvider = Depends(get_ohlcv_provider),
) -> BarsResponse:
    """Generate and preview OHLCV bars for a symbol over the last N days."""
    end = datetime.now(UTC)
    start = end - timedelta(days=days)
    request = BarRequest(symbol=symbol, timeframe=timeframe, start=start, end=end)

    frame = provider.get_bars(request)
    return BarsResponse(
        symbol=symbol,
        timeframe=timeframe,
        count=len(frame),
        bars=_to_previews(frame),
    )