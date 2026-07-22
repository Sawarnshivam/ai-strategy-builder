"""Health check endpoints used for liveness and readiness probes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.health import DatabaseHealthResponse, HealthResponse

router = APIRouter(tags=["system"])
logger = get_logger(__name__)

APP_VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse, summary="Service health check")
def health_check() -> HealthResponse:
    """Return basic service metadata to confirm the API is reachable."""
    settings: Settings = get_settings()
    logger.debug("Health check requested")
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment,
        version=APP_VERSION,
    )


@router.get(
    "/health/db",
    response_model=DatabaseHealthResponse,
    summary="Database readiness check",
)
def database_health_check(db: Session = Depends(get_db)) -> DatabaseHealthResponse:
    """Verify the API can reach Postgres by issuing a trivial query."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.error("Database health check failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unreachable",
        ) from exc
    return DatabaseHealthResponse(status="ok", database="reachable")