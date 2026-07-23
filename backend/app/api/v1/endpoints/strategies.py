"""CRUD endpoints for trading strategies."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_strategy_service
from app.schemas.strategy import (
    StrategyCreate,
    StrategyListResponse,
    StrategyRead,
    StrategyUpdate,
)
from app.services.strategy_service import StrategyService

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.post(
    "",
    response_model=StrategyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a strategy",
)
def create_strategy(
    payload: StrategyCreate,
    service: StrategyService = Depends(get_strategy_service),
) -> StrategyRead:
    """Create a strategy from a natural-language prompt and optional parameters."""
    strategy = service.create(payload)
    return StrategyRead.model_validate(strategy)


@router.get(
    "",
    response_model=StrategyListResponse,
    summary="List strategies",
)
def list_strategies(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, max_length=120),
    service: StrategyService = Depends(get_strategy_service),
) -> StrategyListResponse:
    """Return a paginated list of strategies, optionally filtered by text."""
    items, total = service.list(limit=limit, offset=offset, search=search)
    return StrategyListResponse(
        items=[StrategyRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{strategy_id}",
    response_model=StrategyRead,
    summary="Get a strategy",
)
def get_strategy(
    strategy_id: UUID,
    service: StrategyService = Depends(get_strategy_service),
) -> StrategyRead:
    """Return a single strategy by id."""
    return StrategyRead.model_validate(service.get(strategy_id))


@router.patch(
    "/{strategy_id}",
    response_model=StrategyRead,
    summary="Update a strategy",
)
def update_strategy(
    strategy_id: UUID,
    payload: StrategyUpdate,
    service: StrategyService = Depends(get_strategy_service),
) -> StrategyRead:
    """Partially update a strategy. Omitted fields are left untouched."""
    return StrategyRead.model_validate(service.update(strategy_id, payload))


@router.delete(
    "/{strategy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a strategy",
)
def delete_strategy(
    strategy_id: UUID,
    service: StrategyService = Depends(get_strategy_service),
) -> None:
    """Permanently delete a strategy."""
    service.delete(strategy_id)