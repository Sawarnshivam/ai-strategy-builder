"""Unit tests for StrategyRepository queries."""

from sqlalchemy.orm import Session

from app.models.strategy import Strategy
from app.repositories.strategy_repository import StrategyRepository


def _make(db: Session, name: str, description: str | None = None) -> Strategy:
    """Insert a strategy directly for test setup."""
    strategy = Strategy(name=name, description=description, prompt="p", parameters={})
    db.add(strategy)
    db.flush()
    return strategy


def test_get_by_name_returns_match(db_session: Session) -> None:
    """An exact name lookup finds the stored row."""
    repo = StrategyRepository(db_session)
    _make(db_session, "BTC Momentum")

    assert repo.get_by_name("BTC Momentum") is not None
    assert repo.get_by_name("missing") is None


def test_list_applies_search_and_pagination(db_session: Session) -> None:
    """Search filters on name/description and pagination limits the page size."""
    repo = StrategyRepository(db_session)
    _make(db_session, "BTC Momentum", "uses rsi")
    _make(db_session, "ETH Reversion", "mean reversion")
    _make(db_session, "SOL Breakout", "donchian")

    matches = repo.list(limit=10, offset=0, search="reversion")
    assert len(matches) == 1
    assert matches[0].name == "ETH Reversion"

    assert len(repo.list(limit=2, offset=0)) == 2
    assert repo.count_matching() == 3