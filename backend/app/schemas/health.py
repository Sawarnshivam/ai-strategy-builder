"""Pydantic schemas for the health endpoints."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response payload returned by the health check endpoint."""

    status: str = Field(..., examples=["ok"])
    app_name: str = Field(..., examples=["AI Backtest Platform"])
    environment: str = Field(..., examples=["development"])
    version: str = Field(..., examples=["0.1.0"])


class DatabaseHealthResponse(BaseModel):
    """Response payload for the database readiness check."""

    status: str = Field(..., examples=["ok"])
    database: str = Field(..., examples=["reachable"])