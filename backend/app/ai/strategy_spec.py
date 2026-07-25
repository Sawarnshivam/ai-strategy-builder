"""The structured strategy specification the LLM produces and the backtester consumes.

This is the pivot of the whole system: natural language collapses into these
typed fields, and everything downstream (code generation, backtesting) reads
them instead of prose. Constraints here are the guardrails that keep a plausible
-sounding but nonsensical LLM response from reaching the engine.
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Direction(StrEnum):
    """Which side(s) the strategy is allowed to trade."""

    LONG = "long"
    SHORT = "short"
    BOTH = "both"


class IndicatorType(StrEnum):
    """Technical indicators the engine knows how to compute.

    Kept as a closed set so the LLM cannot invent an indicator the backtester
    has no implementation for. Extend deliberately as the engine grows.
    """

    SMA = "sma"
    EMA = "ema"
    RSI = "rsi"
    MACD = "macd"
    ATR = "atr"
    BBANDS = "bbands"
    ADX = "adx"
    VWAP = "vwap"


class Comparator(StrEnum):
    """How an indicator value is compared in a rule."""

    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"


class IndicatorSpec(BaseModel):
    """A single configured indicator instance."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        min_length=1,
        max_length=40,
        description="Unique handle a rule can reference, e.g. 'ema_fast'.",
        examples=["ema_fast"],
    )
    type: IndicatorType
    params: dict[str, float] = Field(
        default_factory=dict,
        description="Indicator parameters such as {'period': 14}.",
        examples=[{"period": 14}],
    )


class RuleSpec(BaseModel):
    """One boolean condition combining an indicator with a threshold or another indicator."""

    model_config = ConfigDict(extra="forbid")

    left: str = Field(
        ...,
        min_length=1,
        description="Name of the indicator on the left-hand side, or 'price'.",
        examples=["rsi"],
    )
    comparator: Comparator
    right: str = Field(
        ...,
        min_length=1,
        description="A numeric literal (e.g. '30') or another indicator name.",
        examples=["30"],
    )


class RiskSpec(BaseModel):
    """Position sizing and protective exits."""

    model_config = ConfigDict(extra="forbid")

    position_size_pct: float = Field(
        default=100.0,
        gt=0,
        le=100,
        description="Percent of available capital to deploy per position.",
    )
    stop_loss_pct: float | None = Field(
        default=None,
        gt=0,
        le=100,
        description="Stop distance as a percent of entry price, if any.",
    )
    take_profit_pct: float | None = Field(
        default=None,
        gt=0,
        description="Profit target as a percent of entry price, if any.",
    )


class StrategySpec(BaseModel):
    """A complete, executable strategy description filled in by the LLM."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=120, examples=["BTC Momentum RSI+EMA"])
    symbol: str = Field(..., min_length=1, max_length=20, examples=["BTC-USD"])
    timeframe: str = Field(..., min_length=1, max_length=10, examples=["1h", "1d"])
    direction: Direction = Direction.LONG
    indicators: list[IndicatorSpec] = Field(..., min_length=1, max_length=10)
    entry_rules: list[RuleSpec] = Field(..., min_length=1, max_length=10)
    exit_rules: list[RuleSpec] = Field(default_factory=list, max_length=10)
    risk: RiskSpec = Field(default_factory=RiskSpec)
    rationale: str = Field(
        default="",
        max_length=2000,
        description="Short plain-language explanation of the strategy's thesis.",
    )

    @model_validator(mode="after")
    def _rules_reference_known_indicators(self) -> "StrategySpec":
        """Every rule operand must be a defined indicator, 'price', or a number.

        This is the check that catches the LLM referencing an indicator it forgot
        to declare — the single most common way a plausible spec is actually broken.
        """
        known = {ind.name for ind in self.indicators} | {"price"}

        def _is_valid_operand(operand: str) -> bool:
            if operand in known:
                return True
            try:
                float(operand)
            except ValueError:
                return False
            return True

        for rule in [*self.entry_rules, *self.exit_rules]:
            for operand in (rule.left, rule.right):
                if not _is_valid_operand(operand):
                    raise ValueError(
                        f"Rule operand {operand!r} is neither a declared indicator, "
                        f"'price', nor a number."
                    )
        return self