"""SQLAlchemy 2.0 async ORM tables, engine, and session factory.

Seven tables mirror the Pydantic models in ``theleadedge.models``:

* **properties** -- full property data (address, physical, pricing, MLS, owner)
* **leads** -- lead records with scoring, engagement, and CRM metadata
* **signals** -- detected motivation signals with scoring metadata
* **score_history** -- point-in-time score snapshots for trend analysis
* **outreach_events** -- contact attempts performed by the Realtor
* **price_history** -- price change tracking for price-reduction signals
* **sync_log** -- data-source sync audit trail

Design notes:

* Uses ``DeclarativeBase`` + ``mapped_column`` (SQLAlchemy 2.0 style).
* Async engine backed by ``aiosqlite`` for MVP, swappable to
  ``asyncpg`` for PostgreSQL in production.
* ``get_session()`` is an async context manager that commits on
  success and rolls back on exception.
* ``init_db()`` creates all tables (dev/test).  Production uses Alembic.
* Owner PII columns exist in ``PropertyRow`` but MUST NEVER be logged.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# ---------------------------------------------------------------------------
# Declarative Base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# ---------------------------------------------------------------------------
# PropertyRow
# ---------------------------------------------------------------------------


class PropertyRow(Base):
    """All property data -- mirrors PropertyBase + Valuation + MLS + Owner."""

    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    listing_key: Mapped[str | None] = mapped_column(String(50), index=True)
    listing_id: Mapped[str | None] = mapped_column(String(50), index=True)

    # Address
    address: Mapped[str] = mapped_column(String(200))
    address_normalized: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100), default="Naples")
    state: Mapped[str] = mapped_column(String(2), default="FL")
    zip_code: Mapped[str] = mapped_column(String(10))
    county: Mapped[str | None] = mapped_column(String(100))

    # Physical characteristics
    bedrooms: Mapped[int | None] = mapped_column(Integer)
    bathrooms: Mapped[int | None] = mapped_column(Integer)
    living_area: Mapped[float | None] = mapped_column(Float)
    lot_size_acres: Mapped[float | None] = mapped_column(Float)
    year_built: Mapped[int | None] = mapped_column(Integer)
    property_type: Mapped[str | None] = mapped_column(String(50))
    property_sub_type: Mapped[str | None] = mapped_column(String(50))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    # Pricing / valuation
    list_price: Mapped[float | None] = mapped_column(Float)
    original_list_price: Mapped[float | None] = mapped_column(Float)
    previous_list_price: Mapped[float | None] = mapped_column(Float)
    close_price: Mapped[float | None] = mapped_column(Float)
    list_price_low: Mapped[float | None] = mapped_column(Float)

    # MLS status
    standard_status: Mapped[str | None] = mapped_column(String(50))
    mls_status: Mapped[str | None] = mapped_column(String(50))
    days_on_market: Mapped[int | None] = mapped_column(Integer)
    cumulative_dom: Mapped[int | None] = mapped_column(Integer)

    # Dates (Date for date-only, DateTime for timestamps)
    listing_contract_date: Mapped[datetime | None] = mapped_column(Date)
    expiration_date: Mapped[datetime | None] = mapped_column(Date)
    on_market_date: Mapped[datetime | None] = mapped_column(Date)
    off_market_date: Mapped[datetime | None] = mapped_column(Date)
    pending_timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    withdrawn_date: Mapped[datetime | None] = mapped_column(Date)
    cancellation_date: Mapped[datetime | None] = mapped_column(Date)
    close_date: Mapped[datetime | None] = mapped_column(Date)
    price_change_timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    status_change_timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    modification_timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    original_entry_timestamp: Mapped[datetime | None] = mapped_column(DateTime)

    # Agent information
    list_agent_key: Mapped[str | None] = mapped_column(String(50))
    list_agent_mls_id: Mapped[str | None] = mapped_column(String(50))
    list_agent_full_name: Mapped[str | None] = mapped_column(String(200))
    list_office_mls_id: Mapped[str | None] = mapped_column(String(50))
    list_office_name: Mapped[str | None] = mapped_column(String(200))
    buyer_agent_key: Mapped[str | None] = mapped_column(String(50))

    # SWFLAMLS custom fields
    foreclosed_reo: Mapped[bool] = mapped_column(Boolean, default=False)
    potential_short_sale: Mapped[bool] = mapped_column(Boolean, default=False)
    gulf_access: Mapped[bool] = mapped_column(Boolean, default=False)

    # Owner PII -- NEVER log these values
    owner_name: Mapped[str | None] = mapped_column(String(200))
    owner_phone: Mapped[str | None] = mapped_column(String(20))
    owner_email: Mapped[str | None] = mapped_column(String(200))
    owner_mailing_address: Mapped[str | None] = mapped_column(String(300))
    is_absentee: Mapped[bool] = mapped_column(Boolean, default=False)
    is_corporate: Mapped[bool] = mapped_column(Boolean, default=False)

    # Public records enrichment (Phase 2)
    parcel_id: Mapped[str | None] = mapped_column(String(50), index=True)
    homestead_exempt: Mapped[bool] = mapped_column(Boolean, default=False)
    assessed_value: Mapped[float | None] = mapped_column(Float)
    assessed_value_previous: Mapped[float | None] = mapped_column(Float)
    last_sale_date: Mapped[datetime | None] = mapped_column(Date)
    last_sale_price: Mapped[float | None] = mapped_column(Float)
    property_use_code: Mapped[str | None] = mapped_column(String(20))
    owner_name_raw: Mapped[str | None] = mapped_column(String(300))
    mailing_address_raw: Mapped[str | None] = mapped_column(String(500))

    # Meta
    data_source: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    leads: Mapped[list[LeadRow]] = relationship(back_populates="property_rel")
    signals: Mapped[list[SignalRow]] = relationship(
        back_populates="property_rel"
    )
    price_history: Mapped[list[PriceHistoryRow]] = relationship(
        back_populates="property_rel"
    )


# ---------------------------------------------------------------------------
# LeadRow
# ---------------------------------------------------------------------------


class LeadRow(Base):
    """Lead record -- ties property to scoring, engagement, and CRM state."""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id"), index=True
    )

    status: Mapped[str] = mapped_column(String(20), default="new")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Scoring
    current_score: Mapped[float] = mapped_column(Float, default=0.0)
    previous_score: Mapped[float | None] = mapped_column(Float)
    tier: Mapped[str] = mapped_column(String(1), default="D")
    signal_count: Mapped[int] = mapped_column(Integer, default=0)
    priority_rank: Mapped[int | None] = mapped_column(Integer)

    # Engagement
    contacted_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_touch_at: Mapped[datetime | None] = mapped_column(DateTime)
    next_touch_date: Mapped[datetime | None] = mapped_column(DateTime)
    contact_attempts: Mapped[int] = mapped_column(Integer, default=0)

    # CRM
    crm_id: Mapped[str | None] = mapped_column(String(100))
    crm_synced_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    scored_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    property_rel: Mapped[PropertyRow] = relationship(back_populates="leads")
    signals: Mapped[list[SignalRow]] = relationship(back_populates="lead_rel")
    score_history: Mapped[list[ScoreHistoryRow]] = relationship(
        back_populates="lead_rel"
    )
    outreach_events: Mapped[list[OutreachEventRow]] = relationship(
        back_populates="lead_rel"
    )


# ---------------------------------------------------------------------------
# SignalRow
# ---------------------------------------------------------------------------


class SignalRow(Base):
    """Detected motivation signal with scoring metadata."""

    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id"), index=True
    )
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id"), index=True
    )

    signal_type: Mapped[str] = mapped_column(String(50))
    signal_category: Mapped[str] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(50))
    source_ref: Mapped[str | None] = mapped_column(String(100))
    event_date: Mapped[datetime | None] = mapped_column(Date)

    # Scoring metadata
    points: Mapped[float] = mapped_column(Float, default=0.0)
    base_points: Mapped[float] = mapped_column(Float, default=0.0)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    decay_type: Mapped[str] = mapped_column(String(20), default="linear")
    half_life_days: Mapped[float | None] = mapped_column(Float)

    # Lifecycle
    detected_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    lead_rel: Mapped[LeadRow] = relationship(back_populates="signals")
    property_rel: Mapped[PropertyRow] = relationship(
        back_populates="signals"
    )


# ---------------------------------------------------------------------------
# ScoreHistoryRow
# ---------------------------------------------------------------------------


class ScoreHistoryRow(Base):
    """Point-in-time score snapshot for trend tracking and calibration."""

    __tablename__ = "score_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id"), index=True
    )
    score: Mapped[float] = mapped_column(Float)
    tier: Mapped[str] = mapped_column(String(1))
    signal_count: Mapped[int] = mapped_column(Integer, default=0)
    change_reason: Mapped[str] = mapped_column(String(200))
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationship
    lead_rel: Mapped[LeadRow] = relationship(back_populates="score_history")


# ---------------------------------------------------------------------------
# OutreachEventRow
# ---------------------------------------------------------------------------


class OutreachEventRow(Base):
    """Record of a contact attempt by the Realtor."""

    __tablename__ = "outreach_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id"), index=True
    )
    outreach_type: Mapped[str] = mapped_column(String(30))
    outcome: Mapped[str | None] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    performed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    follow_up_date: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationship
    lead_rel: Mapped[LeadRow] = relationship(
        back_populates="outreach_events"
    )


# ---------------------------------------------------------------------------
# PriceHistoryRow
# ---------------------------------------------------------------------------


class PriceHistoryRow(Base):
    """Price change tracking for price-reduction signal detection."""

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id"), index=True
    )
    old_price: Mapped[float | None] = mapped_column(Float)
    new_price: Mapped[float] = mapped_column(Float)
    change_pct: Mapped[float | None] = mapped_column(Float)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    source: Mapped[str | None] = mapped_column(String(50))

    # Relationship
    property_rel: Mapped[PropertyRow] = relationship(
        back_populates="price_history"
    )


# ---------------------------------------------------------------------------
# SyncLogRow
# ---------------------------------------------------------------------------


class SyncLogRow(Base):
    """Audit trail for data-source sync jobs."""

    __tablename__ = "sync_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    job_type: Mapped[str] = mapped_column(String(30))
    success: Mapped[bool] = mapped_column(Boolean)
    records_fetched: Mapped[int] = mapped_column(Integer, default=0)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[str | None] = mapped_column(Text)  # JSON list of strings
    started_at: Mapped[datetime] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    duration_ms: Mapped[int | None] = mapped_column(Integer)


# ---------------------------------------------------------------------------
# SourceRecordRow
# ---------------------------------------------------------------------------


class SourceRecordRow(Base):
    """Persisted source record from external data connectors."""

    __tablename__ = "source_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[str] = mapped_column(String(50))
    source_record_id: Mapped[str] = mapped_column(String(100))
    record_type: Mapped[str] = mapped_column(String(50))

    parcel_id: Mapped[str | None] = mapped_column(String(50), index=True)
    street_address: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(2), default="FL")
    zip_code: Mapped[str | None] = mapped_column(String(10))

    event_date: Mapped[datetime | None] = mapped_column(Date)
    event_type: Mapped[str | None] = mapped_column(String(50))
    raw_data: Mapped[str | None] = mapped_column(Text)  # JSON

    owner_name: Mapped[str | None] = mapped_column(String(200))
    mailing_address: Mapped[str | None] = mapped_column(String(300))

    # Matching
    matched_property_id: Mapped[int | None] = mapped_column(
        ForeignKey("properties.id"), index=True
    )
    match_method: Mapped[str | None] = mapped_column(String(30))
    match_confidence: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


# ---------------------------------------------------------------------------
# MatchQueueRow
# ---------------------------------------------------------------------------


class MatchQueueRow(Base):
    """Low-confidence matches queued for manual review."""

    __tablename__ = "match_queue"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_record_id: Mapped[int] = mapped_column(
        ForeignKey("source_records.id"), index=True
    )
    suggested_property_id: Mapped[int | None] = mapped_column(
        ForeignKey("properties.id")
    )
    match_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    match_method: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, approved, rejected
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


# ---------------------------------------------------------------------------
# MarketSnapshotRow
# ---------------------------------------------------------------------------


class MarketSnapshotRow(Base):
    """Market data snapshot for a ZIP code (from Redfin, etc.)."""

    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    zip_code: Mapped[str] = mapped_column(String(10), index=True)
    source: Mapped[str] = mapped_column(String(50))  # "redfin"
    period_start: Mapped[datetime | None] = mapped_column(Date)
    period_end: Mapped[datetime | None] = mapped_column(Date)

    median_sale_price: Mapped[float | None] = mapped_column(Float)
    median_list_price: Mapped[float | None] = mapped_column(Float)
    median_dom: Mapped[int | None] = mapped_column(Integer)
    homes_sold: Mapped[int | None] = mapped_column(Integer)
    new_listings: Mapped[int | None] = mapped_column(Integer)
    inventory: Mapped[int | None] = mapped_column(Integer)
    months_of_supply: Mapped[float | None] = mapped_column(Float)
    absorption_rate: Mapped[float | None] = mapped_column(Float)
    sale_to_list_ratio: Mapped[float | None] = mapped_column(Float)
    price_drops_pct: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


# ---------------------------------------------------------------------------
# FSBOListingRow
# ---------------------------------------------------------------------------


class FSBOListingRow(Base):
    """FSBO listing detected from Craigslist, Zillow, etc."""

    __tablename__ = "fsbo_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))  # "craigslist", "zillow"
    source_url: Mapped[str | None] = mapped_column(String(500))
    title: Mapped[str | None] = mapped_column(String(300))

    street_address: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(2), default="FL")
    zip_code: Mapped[str | None] = mapped_column(String(10))

    asking_price: Mapped[float | None] = mapped_column(Float)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    matched_property_id: Mapped[int | None] = mapped_column(
        ForeignKey("properties.id"), index=True
    )
    posted_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


# ---------------------------------------------------------------------------
# Engine + Session Factory (module-level singletons)
# ---------------------------------------------------------------------------

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine(database_url: str | None = None) -> AsyncEngine:
    """Return the global async engine, creating it on first call.

    Parameters
    ----------
    database_url:
        SQLAlchemy async connection string.  Falls back to the
        ``DATABASE_URL`` env var, then to a local SQLite file.
    """
    global _engine  # noqa: PLW0603
    if _engine is None:
        url = database_url or os.environ.get(
            "DATABASE_URL", "sqlite+aiosqlite:///./theleadedge.db"
        )
        _engine = create_async_engine(url, echo=False)
    return _engine


def get_session_factory(
    engine: AsyncEngine | None = None,
) -> async_sessionmaker[AsyncSession]:
    """Return the global async session factory, creating it on first call."""
    global _session_factory  # noqa: PLW0603
    if _session_factory is None:
        eng = engine or get_engine()
        _session_factory = async_sessionmaker(eng, expire_on_commit=False)
    return _session_factory


@asynccontextmanager
async def get_session(
    engine: AsyncEngine | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields a session.

    Commits on clean exit, rolls back on exception.
    """
    factory = get_session_factory(engine)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db(engine: AsyncEngine | None = None) -> None:
    """Create all tables.  Use for development and testing.

    Production deployments should use Alembic migrations instead.
    """
    eng = engine or get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db(engine: AsyncEngine | None = None) -> None:
    """Drop all tables.  Use for testing teardown only."""
    eng = engine or get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def reset_engine() -> None:
    """Reset module-level singletons.  Useful between test runs."""
    global _engine, _session_factory  # noqa: PLW0603
    _engine = None
    _session_factory = None
