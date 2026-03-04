"""Shared pytest fixtures for TheLeadEdge test suite.

Provides:
- In-memory SQLite engine and async sessions (per-test isolation)
- Test Settings with FL defaults
- Scoring configuration loaded from real YAML
- Fixed timestamps for deterministic tests
- Phase 2 helper factories for PropertyRow, LeadRow, and SourceRecord
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from theleadedge.config import Settings
from theleadedge.models.source_record import SourceRecord
from theleadedge.scoring.config_loader import ScoringConfig, load_scoring_config
from theleadedge.storage.database import Base, LeadRow, PropertyRow
from theleadedge.utils.address import normalize_address


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


# ---------------------------------------------------------------------------
# Phase 2 Fixtures — SourceRecord, PropertyRow, LeadRow helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def source_record_factory():
    """Factory function for creating SourceRecord instances."""

    def _make(
        source_name: str = "collier_pa",
        source_record_id: str = "SR001",
        record_type: str = "property_assessment",
        parcel_id: str | None = None,
        street_address: str | None = None,
        city: str | None = "Naples",
        state: str = "FL",
        zip_code: str | None = "34102",
        event_date: Any = None,
        event_type: str | None = None,
        raw_data: dict[str, Any] | None = None,
        owner_name: str | None = None,
        mailing_address: str | None = None,
    ) -> SourceRecord:
        return SourceRecord(
            source_name=source_name,
            source_record_id=source_record_id,
            record_type=record_type,
            parcel_id=parcel_id,
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code,
            event_date=event_date,
            event_type=event_type,
            raw_data=raw_data or {},
            owner_name=owner_name,
            mailing_address=mailing_address,
        )

    return _make


@pytest.fixture
def make_property_row():
    """Helper to create a PropertyRow in the session."""

    async def _make(session: AsyncSession, **kwargs: Any) -> PropertyRow:
        defaults: dict[str, Any] = {
            "address": "100 MAIN ST",
            "city": "Naples",
            "state": "FL",
            "zip_code": "34102",
            "data_source": "mls_csv",
        }
        defaults.update(kwargs)

        # Auto-set address_normalized
        if "address_normalized" not in defaults:
            defaults["address_normalized"] = normalize_address(
                defaults["address"],
                defaults.get("city", ""),
                defaults.get("state", "FL"),
                defaults.get("zip_code", ""),
            )

        row = PropertyRow(**defaults)
        session.add(row)
        await session.flush()
        return row

    return _make


@pytest.fixture
def make_lead_row():
    """Helper to create a LeadRow in the session."""

    async def _make(
        session: AsyncSession, property_id: int, **kwargs: Any
    ) -> LeadRow:
        defaults: dict[str, Any] = {
            "property_id": property_id,
            "status": "new",
            "is_active": True,
            "current_score": 0.0,
            "tier": "D",
            "signal_count": 0,
        }
        defaults.update(kwargs)

        row = LeadRow(**defaults)
        session.add(row)
        await session.flush()
        return row

    return _make
