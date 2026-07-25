"""Validation tests for the StrategySpec domain model."""

import pytest
from pydantic import ValidationError

from app.ai.strategy_spec import StrategySpec


def _base_payload() -> dict:
    return {
        "name": "Test",
        "symbol": "BTC-USD",
        "timeframe": "1h",
        "indicators": [{"name": "rsi", "type": "rsi", "params": {"period": 14}}],
        "entry_rules": [{"left": "rsi", "comparator": "less_than", "right": "30"}],
    }


def test_valid_spec_parses() -> None:
    """A well-formed payload validates and applies defaults."""
    spec = StrategySpec.model_validate(_base_payload())

    assert spec.direction.value == "long"
    assert spec.risk.position_size_pct == 100.0
    assert spec.exit_rules == []


def test_rule_referencing_unknown_indicator_is_rejected() -> None:
    """A rule pointing at an undeclared indicator fails validation."""
    payload = _base_payload()
    payload["entry_rules"] = [
        {"left": "macd", "comparator": "greater_than", "right": "0"}
    ]

    with pytest.raises(ValidationError, match="neither a declared indicator"):
        StrategySpec.model_validate(payload)


def test_unknown_indicator_type_is_rejected() -> None:
    """Only enum indicator types are accepted."""
    payload = _base_payload()
    payload["indicators"] = [{"name": "x", "type": "supertrend", "params": {}}]

    with pytest.raises(ValidationError):
        StrategySpec.model_validate(payload)


def test_extra_fields_are_forbidden() -> None:
    """Unexpected keys are rejected so malformed LLM output can't slip through."""
    payload = _base_payload()
    payload["leverage"] = 10

    with pytest.raises(ValidationError):
        StrategySpec.model_validate(payload)