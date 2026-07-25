"""Turns a StrategySpec's rules into a boolean entry/exit signal series.

Operands resolve to a Series: a declared indicator by name, the special 'price'
(close), or a numeric literal broadcast to a constant Series. Multiple rules in
a list are AND-combined. Crossover comparators look at the previous bar, so they
need the prior value — handled inside each comparator.
"""

import pandas as pd

from app.ai.strategy_spec import (
    Comparator,
    RuleSpec,
    StrategySpec,
)
from app.backtesting.indicators import compute_indicator
from app.core.exceptions import ValidationError


def build_indicator_frame(spec: StrategySpec, ohlcv: pd.DataFrame) -> pd.DataFrame:
    """Compute every declared indicator into a name-keyed DataFrame."""
    columns: dict[str, pd.Series] = {}
    for indicator in spec.indicators:
        columns[indicator.name] = compute_indicator(indicator.type, ohlcv, indicator.params)
    return pd.DataFrame(columns, index=ohlcv.index)


def _resolve_operand(
    operand: str,
    ohlcv: pd.DataFrame,
    indicators: pd.DataFrame,
) -> pd.Series:
    """Resolve an operand string to a Series (indicator, price, or constant)."""
    if operand == "price":
        return ohlcv["close"]
    if operand in indicators.columns:
        return indicators[operand]
    try:
        value = float(operand)
    except ValueError as exc:
        raise ValidationError(f"Unresolvable rule operand {operand!r}.") from exc
    return pd.Series(value, index=ohlcv.index)


def _apply_comparator(
    left: pd.Series,
    comparator: Comparator,
    right: pd.Series,
) -> pd.Series:
    """Evaluate one comparator into a boolean Series."""
    if comparator is Comparator.GREATER_THAN:
        return left > right
    if comparator is Comparator.LESS_THAN:
        return left < right
    if comparator is Comparator.CROSSES_ABOVE:
        return (left > right) & (left.shift(1) <= right.shift(1))
    if comparator is Comparator.CROSSES_BELOW:
        return (left < right) & (left.shift(1) >= right.shift(1))
    raise ValidationError(f"Unsupported comparator {comparator!r}.")  # pragma: no cover


def _evaluate_rule(
    rule: RuleSpec,
    ohlcv: pd.DataFrame,
    indicators: pd.DataFrame,
) -> pd.Series:
    """Evaluate a single rule into a boolean Series."""
    left = _resolve_operand(rule.left, ohlcv, indicators)
    right = _resolve_operand(rule.right, ohlcv, indicators)
    return _apply_comparator(left, rule.comparator, right)


def evaluate_rules(
    rules: list[RuleSpec],
    ohlcv: pd.DataFrame,
    indicators: pd.DataFrame,
) -> pd.Series:
    """AND-combine a list of rules into one boolean signal.

    An empty rule list yields an all-False signal, which the simulator reads as
    "never triggers" — the correct behaviour for absent exit rules.
    """
    if not rules:
        return pd.Series(False, index=ohlcv.index)

    combined = pd.Series(True, index=ohlcv.index)
    for rule in rules:
        combined &= _evaluate_rule(rule, ohlcv, indicators)
    return combined.fillna(False).astype(bool)


