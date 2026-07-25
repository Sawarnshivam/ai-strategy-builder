"""Result value objects returned by the backtester."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class BacktestMetrics:
    """Summary performance statistics for a completed backtest."""

    total_return_pct: float
    annualized_return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    win_rate_pct: float
    num_trades: int
    exposure_pct: float


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """The full output of a backtest run.

    equity_curve and returns are time series aligned to the input bars; trades
    lists per-round-trip P&L. Metrics summarise all three.
    """

    equity_curve: pd.Series
    returns: pd.Series
    trades: list[float]
    metrics: BacktestMetrics
    initial_capital: float
    final_equity: float