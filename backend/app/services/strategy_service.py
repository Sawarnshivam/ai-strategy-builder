"""Business logic for creating and managing trading strategies."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.strategy import Strategy
from app.repositories.strategy_repository import StrategyRepository
from app.schemas.strategy import StrategyCreate, StrategyUpdate

logger = get_logger(__name__)


class StrategyService:
    """Coordinates strategy use-cases and owns the transaction boundary."""

    def __init__(self, repository: StrategyRepository) -> None:
        self._repo = repository

    def create(self, payload: StrategyCreate) -> Strategy:
        """Persist a new strategy, rejecting duplicate names."""
        if self._repo.get_by_name(payload.name) is not None:
            raise ConflictError(f"A strategy named {payload.name!r} already exists.")

        strategy = Strategy(
            name=payload.name,
            description=payload.description,
            prompt=payload.prompt,
            parameters=payload.parameters,
        )
        try:
            self._repo.add(strategy)
            self._repo.db.commit()
        except IntegrityError as exc:
            self._repo.db.rollback()
            logger.warning("Strategy creation conflict: %s", exc.orig)
            raise ConflictError(f"A strategy named {payload.name!r} already exists.") from exc

        self._repo.db.refresh(strategy)
        logger.info("Created strategy %s (%s)", strategy.id, strategy.name)
        return strategy

    def get(self, strategy_id: UUID) -> Strategy:
        """Return a strategy or raise NotFoundError."""
        strategy = self._repo.get(strategy_id)
        if strategy is None:
            raise NotFoundError(f"Strategy {strategy_id} not found.")
        return strategy

    def list(
        self,
        *,
        limit: int,
        offset: int,
        search: str | None = None,
    ) -> tuple[list[Strategy], int]:
        """Return a page of strategies plus the total matching count."""
        items = list(self._repo.list(limit=limit, offset=offset, search=search))
        total = self._repo.count_matching(search)
        return items, total

    def update(self, strategy_id: UUID, payload: StrategyUpdate) -> Strategy:
        """Apply a partial update to an existing strategy."""
        strategy = self.get(strategy_id)
        changes = payload.model_dump(exclude_unset=True)

        new_name = changes.get("name")
        if new_name and new_name != strategy.name:
            existing = self._repo.get_by_name(new_name)
            if existing is not None and existing.id != strategy.id:
                raise ConflictError(f"A strategy named {new_name!r} already exists.")

        for field, value in changes.items():
            setattr(strategy, field, value)

        try:
            self._repo.db.commit()
        except IntegrityError as exc:
            self._repo.db.rollback()
            logger.warning("Strategy update conflict: %s", exc.orig)
            raise ConflictError("Strategy name must be unique.") from exc

        self._repo.db.refresh(strategy)
        logger.info("Updated strategy %s (fields=%s)", strategy.id, sorted(changes))
        return strategy

    def delete(self, strategy_id: UUID) -> None:
        """Delete a strategy, raising NotFoundError when it is missing."""
        strategy = self.get(strategy_id)
        self._repo.delete(strategy)
        self._repo.db.commit()
        logger.info("Deleted strategy %s", strategy_id)