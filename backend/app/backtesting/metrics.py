"""Computes summary metrics from an equity curve and trade list.

Kept separate from the simulator so the maths can be unit-tested against hand
-computed values without running a full simulation.
"""

import numpy as np
import pandas as pd

from app.backtesting.models import BacktestMetrics

# Bars per year per timeframe, for annualisation. Approximate; crypto trades 24/7.
BARS_PER_YEAR = {
    "1m": 525_600,
    "5m": 105_120,
    "15m": 35_040,
    "1h": 8_760,
    "4h": 2_190,
    "1d": 365,
}


def _sharpe(returns: pd.Series, periods_per_year: int) -> float:
    """Annualised Sharpe ratio, zero when there is no variation."""
    if returns.std(ddof=0) == 0 or len(returns) < 2:
        return 0.0
    mean = returns.mean()
    std = returns.std(ddof=0)
    return float((mean / std) * np.sqrt(periods_per_year))


def _max_drawdown_pct(equity: pd.Series) -> float:
    """Largest peak-to-trough decline as a positive percentage."""
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    return float(-drawdown.min() * 100.0)


def compute_metrics(
    equity: pd.Series,
    returns: pd.Series,
    trades: list[float],
    position: pd.Series,
    timeframe: str,
) -> BacktestMetrics:
    """Assemble summary metrics from the simulation outputs."""
    initial = float(equity.iloc[0])
    final = float(equity.iloc[-1])
    total_return = (final / initial - 1.0) * 100.0 if initial else 0.0

    periods_per_year = BARS_PER_YEAR.get(timeframe, 365)
    n = len(equity)
    years = n / periods_per_year if periods_per_year else 0.0
    if years > 0 and initial > 0 and final > 0:
        annualized = ((final / initial) ** (1.0 / years) - 1.0) * 100.0
    else:
        annualized = 0.0

    wins = sum(1 for pnl in trades if pnl > 0)
    win_rate = (wins / len(trades) * 100.0) if trades else 0.0
    exposure = float((position != 0).mean() * 100.0) if n else 0.0

    return BacktestMetrics(
        total_return_pct=round(total_return, 4),
        annualized_return_pct=round(annualized, 4),
        sharpe_ratio=round(_sharpe(returns, periods_per_year), 4),
        max_drawdown_pct=round(_max_drawdown_pct(equity), 4),
        win_rate_pct=round(win_rate, 4),
        num_trades=len(trades),
        exposure_pct=round(exposure, 4),
    )