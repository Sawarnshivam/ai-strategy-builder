"""Aggregates all v1 API routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, strategies

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(strategies.router)