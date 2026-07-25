"""Aggregates all v1 API routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import ai, backtests, health, market_data, strategies

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(strategies.router)
api_router.include_router(ai.router)
api_router.include_router(market_data.router)
api_router.include_router(backtests.router)