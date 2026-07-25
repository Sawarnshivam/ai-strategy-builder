"""Tests for the backtest orchestration service."""

import pytest
from sqlalchemy.orm import Session

from app.ai.fake_client import FakeLLMClient
from app.ai.spec_generator import SpecGenerator
from app.market_data.synthetic_provider import SyntheticOHLCVProvider
from app.repositories.backtest_repository import BacktestRepository
from app.services.backtest_service import BacktestService


@pytest.fixture()
def backtest_service(db_session: Session, valid_spec_json: str) -> BacktestService:
    """A backtest service wired to synthetic data and a scripted fake LLM."""
    provider = SyntheticOHLCVProvider(seed=7)
    generator = SpecGenerator(FakeLLMClient(reply=valid_spec_json))
    repository = BacktestRepository(db_session)
    return BacktestService(provider, generator, repository)


@pytest.mark.anyio
async def test_run_from_description_persists_run(backtest_service: BacktestService) -> None:
    """A description-driven backtest produces a stored run with metrics."""
    run = await backtest_service.run(
        description="momentum BTC using RSI and EMA",
        spec=None,
        strategy_id=None,
        initial_capital=10_000.0,
    )

    assert run.id is not None
    assert run.symbol == "BTC-USD"
    assert "total_return_pct" in run.metrics
    assert run.equity_curve["points"]


@pytest.mark.anyio
async def test_run_from_spec_skips_llm(db_session: Session, valid_spec_json: str) -> None:
    """A spec-driven run does not call the LLM at all."""
    from app.ai.strategy_spec import StrategySpec

    client = FakeLLMClient(reply="should not be used")
    service = BacktestService(
        SyntheticOHLCVProvider(seed=7),
        SpecGenerator(client),
        BacktestRepository(db_session),
    )
    spec = StrategySpec.model_validate_json(valid_spec_json)

    run = await service.run(
        description=None,
        spec=spec,
        strategy_id=None,
        initial_capital=5_000.0,
    )

    assert client.call_count == 0
    assert run.initial_capital == 5_000.0