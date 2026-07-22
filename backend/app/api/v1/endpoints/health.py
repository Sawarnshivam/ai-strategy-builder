"""Health check endpoint used for liveness probes and smoke tests."""

from fastapi import APIRouter

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.schemas.health import HealthResponse

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