"""Translates domain exceptions into HTTP responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach application-wide exception handlers to the FastAPI app."""

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        """Return a consistent error envelope for known domain failures."""
        logger.info(
            "%s on %s %s: %s",
            type(exc).__name__,
            request.method,
            request.url.path,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": type(exc).__name__},
        )