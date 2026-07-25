"""The backtest simulator: StrategySpec + OHLCV bars -> equity curve and metrics.

The simulation is intentionally simple and fully vectorised where it can be:
positions are derived from entry/exit signals, shifted one bar to avoid
look-ahead, and equity compounds bar-to-bar returns while in a position. Round
-trip trade P&L is collected for win-rate reporting.
"""

import numpy as np
import pandas as pd

from app.ai.strategy_spec import Direction, StrategySpec
from app.backtesting.metrics import compute_metrics
from app.backtesting.models import BacktestResult
from app.backtesting.signals import build_indicator_frame, evaluate_rules
from app.core.exceptions import ValidationError

DEFAULT_INITIAL_CAPITAL = 10_000.0


class Backtester:
    """Runs a single strategy over a single OHLCV series."""

    def __init__(self, initial_capital: float = DEFAULT_INITIAL_CAPITAL) -> None:
        if initial_capital <= 0:
            raise ValidationError("Initial capital must be positive.")
        self._initial_capital = initial_capital

    def run(self, spec: StrategySpec, ohlcv: pd.DataFrame) -> BacktestResult:
        """Execute the backtest and return equity, returns, trades and metrics."""
        if ohlcv.empty:
            raise ValidationError("Cannot backtest on an empty price series.")

        indicators = build_indicator_frame(spec, ohlcv)
        entries = evaluate_rules(spec.entry_rules, ohlcv, indicators)
        exits = evaluate_rules(spec.exit_rules, ohlcv, indicators)

        position = self._build_positions(entries, exits, spec.direction)
        # Shift to trade on the *next* bar after a signal — no look-ahead.
        executed = position.shift(1).fillna(0.0)

        size = spec.risk.position_size_pct / 100.0
        bar_returns = ohlcv["close"].pct_change().fillna(0.0)
        strategy_returns = executed * bar_returns * size

        equity = self._initial_capital * (1.0 + strategy_returns).cumprod()
        trades = self._extract_trades(executed, bar_returns, size)

        metrics = compute_metrics(equity, strategy_returns, trades, executed, spec.timeframe)
        return BacktestResult(
            equity_curve=equity,
            returns=strategy_returns,
            trades=trades,
            metrics=metrics,
            initial_capital=self._initial_capital,
            final_equity=float(equity.iloc[-1]),
        )

    @staticmethod
    def _build_positions(
        entries: pd.Series,
        exits: pd.Series,
        direction: Direction,
    ) -> pd.Series:
        """Walk entry/exit signals into a stateful 0/±1 position series.

        A position opens on an entry signal and closes on an exit signal,
        holding in between. Long strategies take +1; short-only take -1.
        """
        target = -1.0 if direction is Direction.SHORT else 1.0
        values = np.zeros(len(entries))
        holding = False
        entry_arr = entries.to_numpy()
        exit_arr = exits.to_numpy()

        for i in range(len(entry_arr)):
            if holding:
                if exit_arr[i]:
                    holding = False
                else:
                    values[i] = target
            elif entry_arr[i]:
                holding = True
                values[i] = target

        return pd.Series(values, index=entries.index)

    @staticmethod
    def _extract_trades(
        executed: pd.Series,
        bar_returns: pd.Series,
        size: float,
    ) -> list[float]:
        """Collect per-round-trip P&L percentages from executed positions."""
        trades: list[float] = []
        in_trade = False
        cum = 1.0
        pos = executed.to_numpy()
        rets = bar_returns.to_numpy()

        for i in range(len(pos)):
            if pos[i] != 0.0:
                if not in_trade:
                    in_trade = True
                    cum = 1.0
                cum *= 1.0 + pos[i] * rets[i] * size
            elif in_trade:
                in_trade = False
                trades.append((cum - 1.0) * 100.0)

        if in_trade:
            trades.append((cum - 1.0) * 100.0)
        return trades