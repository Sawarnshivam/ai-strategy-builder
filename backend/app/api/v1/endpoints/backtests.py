"""Endpoints to run and retrieve backtests."""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.ai.strategy_spec import StrategySpec
from app.api.deps import get_backtest_service, get_current_user
from app.core.exceptions import NotFoundError
from app.models.backtest_run import BacktestRun
from app.models.user import User
from app.schemas.backtest import (
    BacktestRequestBody,
    BacktestResultResponse,
    BacktestRunListResponse,
    BacktestRunSummary,
    EquityPoint,
    MetricsSchema,
)
from app.services.backtest_service import BacktestService

router = APIRouter(prefix="/backtests", tags=["backtests"])


def _to_result_response(run: BacktestRun) -> BacktestResultResponse:
    """Map a persisted run to the full result response schema."""
    curve = run.equity_curve.get("points", [])
    trades = run.equity_curve.get("trades", [])
    return BacktestResultResponse(
        id=run.id,
        symbol=run.symbol,
        timeframe=run.timeframe,
        spec=StrategySpec.model_validate(run.spec),
        metrics=MetricsSchema(**run.metrics),
        equity_curve=[EquityPoint(**point) for point in curve],
        trades=trades,
        initial_capital=run.initial_capital,
        final_equity=run.final_equity,
        created_at=run.created_at,
    )


@router.post(
    "",
    response_model=BacktestResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run a backtest from a description or spec",
)
async def run_backtest(
    body: BacktestRequestBody,
    service: BacktestService = Depends(get_backtest_service),
    _user: User = Depends(get_current_user),
) -> BacktestResultResponse:
    """Run and persist a backtest, returning equity curve, trades and metrics."""
    run = await service.run(
        description=body.description,
        spec=body.spec,
        strategy_id=body.strategy_id,
        initial_capital=body.initial_capital,
    )
    return _to_result_response(run)


@router.get(
    "",
    response_model=BacktestRunListResponse,
    summary="List backtest runs",
)
def list_backtests(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: BacktestService = Depends(get_backtest_service),
) -> BacktestRunListResponse:
    """Return a paginated list of past run summaries."""
    items, total = service.list(limit=limit, offset=offset)
    return BacktestRunListResponse(
        items=[BacktestRunSummary.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{run_id}",
    response_model=BacktestResultResponse,
    summary="Get a backtest run",
)
def get_backtest(
    run_id: uuid.UUID,
    service: BacktestService = Depends(get_backtest_service),
) -> BacktestResultResponse:
    """Return the full result of a single run."""
    run = service.get(run_id)
    if run is None:
        raise NotFoundError(f"Backtest run {run_id} not found.")
    return _to_result_response(run)