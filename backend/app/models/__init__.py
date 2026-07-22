"""ORM model registry — import every model so Alembic autogenerate sees it."""

from app.models.strategy import Strategy

__all__ = ["Strategy"]