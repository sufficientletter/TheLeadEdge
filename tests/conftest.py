"""Shared pytest fixtures for TheLeadEdge test suite.

Provides:
- In-memory SQLite engine and async sessions (per-test isolation)
- Test Settings with FL defaults
- Scoring configuration loaded from real YAML
- Fixed timestamps for deterministic tests
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from theleadedge.config import Settings
from theleadedge.scoring.config_loader import ScoringConfig, load_scoring_config
from theleadedge.storage.database import Base


@pytest_asyncio.fixture(loop_scope="session")
async def engine():
    """In-memory SQLite engine for tests."""
    eng = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    """Async session for a single test.  Rolls back after test."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess
        await sess.rollback()


@pytest.fixture
def settings() -> Settings:
    """Test settings with FL defaults."""
    return Settings(
        app_env="test",
        log_level="DEBUG",
        state="FL",
        database_url="sqlite+aiosqlite://",
    )


@pytest.fixture
def scoring_config() -> ScoringConfig:
    """Load real scoring config from YAML."""
    config_path = Path(__file__).parent.parent / "config" / "scoring_weights.yaml"
    return load_scoring_config(config_path)


@pytest.fixture
def now() -> datetime:
    """Fixed timestamp for deterministic tests."""
    return datetime(2026, 3, 2, 10, 0, 0)


@pytest.fixture
def yesterday(now) -> datetime:
    """One day before the fixed timestamp."""
    return now - timedelta(days=1)


@pytest.fixture
def one_week_ago(now) -> datetime:
    """Seven days before the fixed timestamp."""
    return now - timedelta(days=7)


@pytest.fixture
def one_month_ago(now) -> datetime:
    """Thirty days before the fixed timestamp."""
    return now - timedelta(days=30)


@pytest.fixture
def three_months_ago(now) -> datetime:
    """Ninety days before the fixed timestamp."""
    return now - timedelta(days=90)
