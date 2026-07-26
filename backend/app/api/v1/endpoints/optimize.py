"""Endpoint to run a parameter-sweep optimization."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_optimizer_service
from app.models.user import User
from app.schemas.optimize import SweepRequest, SweepResponse
from app.services.optimizer_service import OptimizerService

router = APIRouter(prefix="/optimize", tags=["optimize"])


@router.post(
    "/sweep",
    response_model=SweepResponse,
    summary="Sweep one indicator parameter across a range",
)
def run_sweep(
    body: SweepRequest,
    service: OptimizerService = Depends(get_optimizer_service),
    _user: User = Depends(get_current_user),
) -> SweepResponse:
    """Grid-search a single parameter and return configurations ranked by metric."""
    return service.sweep(body)