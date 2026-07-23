"""Domain-level exceptions that are transport-agnostic.

Services raise these; the API layer translates them into HTTP responses.
Keeping them free of FastAPI imports lets the domain stay testable in isolation.
"""


class AppError(Exception):
    """Base class for all recoverable application errors."""

    status_code: int = 500
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(AppError):
    """Raised when a requested entity does not exist."""

    status_code = 404
    default_message = "Resource not found."


class ConflictError(AppError):
    """Raised when an operation violates a uniqueness or state constraint."""

    status_code = 409
    default_message = "Resource conflict."


class ValidationError(AppError):
    """Raised when input passes schema validation but breaks a business rule."""

    status_code = 422
    default_message = "Invalid request."