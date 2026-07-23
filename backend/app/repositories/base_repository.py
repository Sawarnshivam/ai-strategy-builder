"""Generic persistence helpers shared by every repository."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Thin, typed data-access wrapper around a single ORM model.

    Repositories never commit. They flush so identity and server-side defaults
    are populated, leaving transaction boundaries to the calling service.
    """

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self._db = db

    @property
    def db(self) -> Session:
        """Expose the underlying session for services that manage transactions."""
        return self._db

    def get(self, entity_id: UUID) -> ModelT | None:
        """Return an entity by primary key, or None when it does not exist."""
        return self._db.get(self.model, entity_id)

    def count(self) -> int:
        """Return the total number of rows for this model."""
        stmt = select(func.count()).select_from(self.model)
        return self._db.execute(stmt).scalar_one()

    def add(self, entity: ModelT) -> ModelT:
        """Stage a new entity and flush so server-side defaults are available."""
        self._db.add(entity)
        self._db.flush()
        self._db.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        """Stage an entity for deletion."""
        self._db.delete(entity)
        self._db.flush()