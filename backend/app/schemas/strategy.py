"""Pydantic contracts for the Strategy resource."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_NAME_LENGTH = 120


class StrategyBase(BaseModel):
    """Fields shared by create and read representations."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=MAX_NAME_LENGTH,
        examples=["BTC Momentum RSI+EMA"],
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Long when RSI < 30 and price is above the 200 EMA."],
    )
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        examples=["Create a momentum strategy for BTC using RSI and EMA."],
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"rsi_period": 14, "ema_period": 200}],
    )

    @field_validator("name", "prompt")
    @classmethod
    def _strip_and_require(cls, value: str) -> str:
        """Reject values that are only whitespace and normalise padding."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("description")
    @classmethod
    def _strip_optional(cls, value: str | None) -> str | None:
        """Normalise an optional description, collapsing blanks to None."""
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class StrategyCreate(StrategyBase):
    """Payload accepted when creating a strategy."""


class StrategyUpdate(BaseModel):
    """Partial update payload — only supplied fields are applied."""

    name: str | None = Field(default=None, min_length=1, max_length=MAX_NAME_LENGTH)
    description: str | None = Field(default=None, max_length=2000)
    prompt: str | None = Field(default=None, min_length=1, max_length=8000)
    parameters: dict[str, Any] | None = None

    @field_validator("name", "prompt")
    @classmethod
    def _strip_and_require(cls, value: str | None) -> str | None:
        """Reject whitespace-only overrides."""
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class StrategyRead(StrategyBase):
    """Representation returned to API clients."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class StrategyListResponse(BaseModel):
    """Paginated envelope for strategy collections."""

    items: list[StrategyRead]
    total: int = Field(..., description="Total rows matching the filter, ignoring pagination.")
    limit: int
    offset: int