"""Shared FastAPI dependencies (composition root for the API layer)."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.client import LLMClient
from app.ai.factory import build_llm_client
from app.ai.spec_generator import SpecGenerator
from app.core.config import Settings, get_settings
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


def get_llm_client(settings: Settings = Depends(get_settings)) -> LLMClient:
    """Provide the configured LLM client (real or fake) for a request."""
    return build_llm_client(settings)

def get_spec_generator(
    client: LLMClient = Depends(get_llm_client),
) -> SpecGenerator:
    """Provide a spec generator wired to the configured LLM client."""
    return SpecGenerator(client)