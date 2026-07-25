"""Pydantic schemas for the market-data diagnostic endpoint."""

from datetime import datetime

from pydantic import BaseModel, Field


class BarPreview(BaseModel):
    """A single OHLCV bar in API form."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class BarsResponse(BaseModel):
    """Response wrapping a small preview of generated bars."""

    symbol: str
    timeframe: str
    count: int
    bars: list[BarPreview] = Field(..., description="First and last few bars only.")