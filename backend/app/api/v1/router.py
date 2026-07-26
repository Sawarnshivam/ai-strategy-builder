"""Aggregates all v1 API routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    auth,
    backtests,
    health,
    market_data,
    optimize,
    strategies,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(strategies.router)
api_router.include_router(ai.router)
api_router.include_router(market_data.router)
api_router.include_router(backtests.router)
api_router.include_router(optimize.router)