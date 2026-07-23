"""Shared FastAPI dependencies (composition root for the API layer)."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.strategy_repository import StrategyRepository
from app.services.strategy_service import StrategyService


def get_strategy_repository(db: Session = Depends(get_db)) -> StrategyRepository:
    """Provide a request-scoped strategy repository."""
    return StrategyRepository(db)


def get_strategy_service(
    repository: StrategyRepository = Depends(get_strategy_repository),
) -> StrategyService:
    """Provide a request-scoped strategy service."""
    return StrategyService(repository)