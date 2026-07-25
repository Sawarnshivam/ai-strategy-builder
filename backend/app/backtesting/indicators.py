"""Technical indicator calculations over an OHLCV frame.

Each function takes the OHLCV DataFrame plus parameters and returns a single
Series aligned to the frame's index. The registry maps IndicatorType to a
builder so the evaluator can compute whatever a spec declares without a big
if/elif ladder. Every indicator here corresponds to an IndicatorType enum value;
the two grow together, by design.
"""

from collections.abc import Callable

import numpy as np
import pandas as pd

from app.ai.strategy_spec import IndicatorType
from app.core.exceptions import ValidationError


def _period(params: dict[str, float], default: int) -> int:
    """Read an integer 'period' param, falling back to a sensible default."""
    return int(params.get("period", default))


def sma(frame: pd.DataFrame, params: dict[str, float]) -> pd.Series:
    """Simple moving average of close."""
    return frame["close"].rolling(window=_period(params, 20), min_periods=1).mean()


def ema(frame: pd.DataFrame, params: dict[str, float]) -> pd.Series:
    """Exponential moving average of close."""
    span = _period(params, 20)
    return frame["close"].ewm(span=span, adjust=False, min_periods=1).mean()


def rsi(frame: pd.DataFrame, params: dict[str, float]) -> pd.Series:
    """Relative strength index (Wilder's smoothing) of close."""
    period = _period(params, 14)
    delta = frame["close"].diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=1).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=1).mean()

    result = pd.Series(50.0, index=frame.index)
    both = (avg_gain + avg_loss) > 0
    rs = avg_gain[both] / avg_loss[both].replace(0.0, np.nan)
    result[both] = 100.0 - (100.0 / (1.0 + rs))
    # When there are gains but zero losses, RSI is 100.
    result[(avg_loss == 0.0) & (avg_gain > 0.0)] = 100.0
    return result.fillna(50.0)


def macd(frame: pd.DataFrame, params: dict[str, float]) -> pd.Series:
    """MACD line (fast EMA minus slow EMA) of close."""
    fast = int(params.get("fast", 12))
    slow = int(params.get("slow", 26))
    fast_ema = frame["close"].ewm(span=fast, adjust=False, min_periods=1).mean()
    slow_ema = frame["close"].ewm(span=slow, adjust=False, min_periods=1).mean()
    return fast_ema - slow_ema


def atr(frame: pd.DataFrame, params: dict[str, float]) -> pd.Series:
    """Average true range over high/low/close."""
    period = _period(params, 14)
    high, low, close = frame["high"], frame["low"], frame["close"]
    prev_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=1).mean()


def bbands(frame: pd.DataFrame, params: dict[str, float]) -> pd.Series:
    """Bollinger %B: position of close within its bands (0 = lower, 1 = upper)."""
    period = _period(params, 20)
    std_mult = float(params.get("std", 2.0))
    mid = frame["close"].rolling(window=period, min_periods=1).mean()
    std = frame["close"].rolling(window=period, min_periods=1).std(ddof=0).fillna(0.0)
    upper = mid + std_mult * std
    lower = mid - std_mult * std
    span = (upper - lower).replace(0.0, np.nan)
    return ((frame["close"] - lower) / span).fillna(0.5)


def adx(frame: pd.DataFrame, params: dict[str, float]) -> pd.Series:
    """Average directional index (trend strength, 0–100)."""
    period = _period(params, 14)
    high, low = frame["high"], frame["low"]
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    tr = atr(frame, {"period": period})
    plus_di = 100.0 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / tr.replace(0.0, np.nan)
    minus_di = 100.0 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / tr.replace(0.0, np.nan)
    dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0.0, np.nan)
    return dx.ewm(alpha=1 / period, adjust=False).mean().fillna(0.0)


def vwap(frame: pd.DataFrame, params: dict[str, float]) -> pd.Series:
    """Cumulative volume-weighted average price."""
    typical = (frame["high"] + frame["low"] + frame["close"]) / 3.0
    cum_vol = frame["volume"].cumsum().replace(0.0, np.nan)
    return (typical * frame["volume"]).cumsum() / cum_vol


IndicatorBuilder = Callable[[pd.DataFrame, dict[str, float]], pd.Series]

INDICATOR_REGISTRY: dict[IndicatorType, IndicatorBuilder] = {
    IndicatorType.SMA: sma,
    IndicatorType.EMA: ema,
    IndicatorType.RSI: rsi,
    IndicatorType.MACD: macd,
    IndicatorType.ATR: atr,
    IndicatorType.BBANDS: bbands,
    IndicatorType.ADX: adx,
    IndicatorType.VWAP: vwap,
}


def compute_indicator(
    indicator_type: IndicatorType,
    frame: pd.DataFrame,
    params: dict[str, float],
) -> pd.Series:
    """Compute a single indicator series by type using the registry."""
    builder = INDICATOR_REGISTRY.get(indicator_type)
    if builder is None:  # pragma: no cover - enum and registry are kept in sync
        raise ValidationError(f"No implementation for indicator {indicator_type!r}.")
    return builder(frame, params)