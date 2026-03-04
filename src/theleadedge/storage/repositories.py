"""Repository layer for TheLeadEdge.

Each repository wraps a single ORM table and exposes async CRUD methods
using SQLAlchemy 2.0 ``select()`` statements (no legacy Query API).

Repositories receive an ``AsyncSession`` at construction time so callers
control transaction scope.  Never call ``session.commit()`` inside a
repository -- let ``get_session()`` handle that.

Usage::

    async with get_session() as session:
        prop_repo = PropertyRepo(session)
        row, created = await prop_repo.upsert_by_listing_key(
            "12345", address="123 Main St", ...
        )
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .database import (
    FSBOListingRow,
    LeadRow,
    MarketSnapshotRow,
    MatchQueueRow,
    OutreachEventRow,
    PriceHistoryRow,
    PropertyRow,
    ScoreHistoryRow,
    SignalRow,
    SourceRecordRow,
    SyncLogRow,
)

# ---------------------------------------------------------------------------
# PropertyRepo
# ---------------------------------------------------------------------------


class PropertyRepo:
    """CRUD operations on the ``properties`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: int) -> PropertyRow | None:
        """Fetch a property by primary key."""
        return await self.session.get(PropertyRow, id)

    async def get_by_listing_key(self, listing_key: str) -> PropertyRow | None:
        """Fetch a property by MLS listing key."""
        stmt = select(PropertyRow).where(
            PropertyRow.listing_key == listing_key
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_listing_id(self, listing_id: str) -> PropertyRow | None:
        """Fetch a property by MLS listing ID."""
        stmt = select(PropertyRow).where(
            PropertyRow.listing_id == listing_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_address_key(
        self, address_normalized: str
    ) -> PropertyRow | None:
        """Fetch a property by normalized address string."""
        stmt = select(PropertyRow).where(
            PropertyRow.address_normalized == address_normalized
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, **kwargs: Any) -> PropertyRow:
        """Insert a new property row."""
        row = PropertyRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def update(self, id: int, **kwargs: Any) -> PropertyRow | None:
        """Update a property by primary key.  Returns the updated row."""
        row = await self.get_by_id(id)
        if row is None:
            return None
        for key, value in kwargs.items():
            setattr(row, key, value)
        await self.session.flush()
        return row

    async def upsert_by_listing_key(
        self, listing_key: str, **kwargs: Any
    ) -> tuple[PropertyRow, bool]:
        """Insert or update a property keyed on listing_key.

        Returns
        -------
        tuple[PropertyRow, bool]
            The row and a boolean: ``True`` if newly created, ``False``
            if an existing row was updated.
        """
        existing = await self.get_by_listing_key(listing_key)
        if existing is not None:
            for key, value in kwargs.items():
                setattr(existing, key, value)
            await self.session.flush()
            return existing, False
        row = PropertyRow(listing_key=listing_key, **kwargs)
        self.session.add(row)
        await self.session.flush()
        return row, True

    async def get_by_parcel_id(self, parcel_id: str) -> PropertyRow | None:
        """Fetch a property by county parcel ID."""
        stmt = select(PropertyRow).where(PropertyRow.parcel_id == parcel_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_zip_code(self, zip_code: str) -> Sequence[PropertyRow]:
        """Return all properties in a ZIP code."""
        stmt = select(PropertyRow).where(PropertyRow.zip_code == zip_code)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def upsert_by_parcel_id(
        self, parcel_id: str, **kwargs: Any
    ) -> tuple[PropertyRow, bool]:
        """Insert or update a property keyed on parcel_id.

        Returns (row, is_new).
        """
        existing = await self.get_by_parcel_id(parcel_id)
        if existing is not None:
            for key, value in kwargs.items():
                setattr(existing, key, value)
            await self.session.flush()
            return existing, False
        row = PropertyRow(parcel_id=parcel_id, **kwargs)
        self.session.add(row)
        await self.session.flush()
        return row, True


# ---------------------------------------------------------------------------
# LeadRepo
# ---------------------------------------------------------------------------


class LeadRepo:
    """CRUD operations on the ``leads`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: int) -> LeadRow | None:
        """Fetch a lead by primary key."""
        return await self.session.get(LeadRow, id)

    async def get_by_property_id(self, property_id: int) -> LeadRow | None:
        """Fetch the lead for a given property (expects at most one)."""
        stmt = select(LeadRow).where(LeadRow.property_id == property_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active(self) -> Sequence[LeadRow]:
        """Return all active leads ordered by score descending."""
        stmt = (
            select(LeadRow)
            .where(LeadRow.is_active.is_(True))
            .order_by(desc(LeadRow.current_score))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_tier(self, tier: str) -> Sequence[LeadRow]:
        """Return active leads in a specific tier, ordered by score desc."""
        stmt = (
            select(LeadRow)
            .where(LeadRow.is_active.is_(True), LeadRow.tier == tier)
            .order_by(desc(LeadRow.current_score))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> LeadRow:
        """Insert a new lead row."""
        row = LeadRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def update_score(
        self,
        id: int,
        score: float,
        tier: str,
        signal_count: int,
    ) -> None:
        """Update scoring fields on a lead."""
        stmt = (
            update(LeadRow)
            .where(LeadRow.id == id)
            .values(
                previous_score=LeadRow.current_score,
                current_score=score,
                tier=tier,
                signal_count=signal_count,
                scored_at=datetime.utcnow(),
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()


# ---------------------------------------------------------------------------
# SignalRepo
# ---------------------------------------------------------------------------


class SignalRepo:
    """CRUD operations on the ``signals`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_lead_id(self, lead_id: int) -> Sequence[SignalRow]:
        """Return all signals for a lead (active and inactive)."""
        stmt = (
            select(SignalRow)
            .where(SignalRow.lead_id == lead_id)
            .order_by(desc(SignalRow.detected_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active_by_lead_id(
        self, lead_id: int
    ) -> Sequence[SignalRow]:
        """Return only active (non-expired) signals for a lead."""
        stmt = (
            select(SignalRow)
            .where(
                SignalRow.lead_id == lead_id,
                SignalRow.is_active.is_(True),
            )
            .order_by(desc(SignalRow.detected_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> SignalRow:
        """Insert a new signal row."""
        row = SignalRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def deactivate_expired(self, now: datetime) -> int:
        """Mark all signals past their ``expires_at`` as inactive.

        Returns the number of rows affected.
        """
        stmt = (
            update(SignalRow)
            .where(
                SignalRow.is_active.is_(True),
                SignalRow.expires_at.isnot(None),
                SignalRow.expires_at <= now,
            )
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# ScoreHistoryRepo
# ---------------------------------------------------------------------------


class ScoreHistoryRepo:
    """CRUD operations on the ``score_history`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> ScoreHistoryRow:
        """Insert a new score history entry."""
        row = ScoreHistoryRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_by_lead_id(
        self, lead_id: int, limit: int = 30
    ) -> Sequence[ScoreHistoryRow]:
        """Return recent score history for a lead, newest first."""
        stmt = (
            select(ScoreHistoryRow)
            .where(ScoreHistoryRow.lead_id == lead_id)
            .order_by(desc(ScoreHistoryRow.calculated_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ---------------------------------------------------------------------------
# OutreachEventRepo
# ---------------------------------------------------------------------------


class OutreachEventRepo:
    """CRUD operations on the ``outreach_events`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> OutreachEventRow:
        """Insert a new outreach event."""
        row = OutreachEventRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_by_lead_id(
        self, lead_id: int
    ) -> Sequence[OutreachEventRow]:
        """Return all outreach events for a lead, newest first."""
        stmt = (
            select(OutreachEventRow)
            .where(OutreachEventRow.lead_id == lead_id)
            .order_by(desc(OutreachEventRow.performed_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ---------------------------------------------------------------------------
# PriceHistoryRepo
# ---------------------------------------------------------------------------


class PriceHistoryRepo:
    """CRUD operations on the ``price_history`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> PriceHistoryRow:
        """Insert a new price history entry."""
        row = PriceHistoryRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_by_property_id(
        self, property_id: int
    ) -> Sequence[PriceHistoryRow]:
        """Return price history for a property, newest first."""
        stmt = (
            select(PriceHistoryRow)
            .where(PriceHistoryRow.property_id == property_id)
            .order_by(desc(PriceHistoryRow.changed_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ---------------------------------------------------------------------------
# SyncLogRepo
# ---------------------------------------------------------------------------


class SyncLogRepo:
    """CRUD operations on the ``sync_log`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> SyncLogRow:
        """Insert a new sync log entry."""
        row = SyncLogRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_latest_by_source(self, source: str) -> SyncLogRow | None:
        """Return the most recent sync log entry for a given source."""
        stmt = (
            select(SyncLogRow)
            .where(SyncLogRow.source == source)
            .order_by(desc(SyncLogRow.started_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()


# ---------------------------------------------------------------------------
# SourceRecordRepo
# ---------------------------------------------------------------------------


class SourceRecordRepo:
    """CRUD operations on the ``source_records`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> SourceRecordRow:
        """Insert a new source record row."""
        row = SourceRecordRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_by_source_and_id(
        self, source_name: str, source_record_id: str
    ) -> SourceRecordRow | None:
        """Fetch a source record by its source name and source-specific ID."""
        stmt = select(SourceRecordRow).where(
            SourceRecordRow.source_name == source_name,
            SourceRecordRow.source_record_id == source_record_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_unmatched(self) -> Sequence[SourceRecordRow]:
        """Return all source records not yet matched to a property."""
        stmt = (
            select(SourceRecordRow)
            .where(SourceRecordRow.matched_property_id.is_(None))
            .order_by(desc(SourceRecordRow.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ---------------------------------------------------------------------------
# MatchQueueRepo
# ---------------------------------------------------------------------------


class MatchQueueRepo:
    """CRUD operations on the ``match_queue`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> MatchQueueRow:
        """Insert a new match queue entry."""
        row = MatchQueueRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_pending(self) -> Sequence[MatchQueueRow]:
        """Return all pending match queue entries, highest confidence first."""
        stmt = (
            select(MatchQueueRow)
            .where(MatchQueueRow.status == "pending")
            .order_by(desc(MatchQueueRow.match_confidence))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status(
        self, id: int, status: str, reviewed_at: datetime | None = None
    ) -> None:
        """Update the status of a match queue entry."""
        stmt = (
            update(MatchQueueRow)
            .where(MatchQueueRow.id == id)
            .values(status=status, reviewed_at=reviewed_at)
        )
        await self.session.execute(stmt)
        await self.session.flush()


# ---------------------------------------------------------------------------
# MarketSnapshotRepo
# ---------------------------------------------------------------------------


class MarketSnapshotRepo:
    """CRUD operations on the ``market_snapshots`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> MarketSnapshotRow:
        """Insert a new market snapshot row."""
        row = MarketSnapshotRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_latest_by_zip(self, zip_code: str) -> MarketSnapshotRow | None:
        """Return the most recent market snapshot for a ZIP code."""
        stmt = (
            select(MarketSnapshotRow)
            .where(MarketSnapshotRow.zip_code == zip_code)
            .order_by(desc(MarketSnapshotRow.period_end))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_zip_and_source(
        self, zip_code: str, source: str
    ) -> Sequence[MarketSnapshotRow]:
        """Return all snapshots for a ZIP and source, newest first."""
        stmt = (
            select(MarketSnapshotRow)
            .where(
                MarketSnapshotRow.zip_code == zip_code,
                MarketSnapshotRow.source == source,
            )
            .order_by(desc(MarketSnapshotRow.period_end))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ---------------------------------------------------------------------------
# FSBOListingRepo
# ---------------------------------------------------------------------------


class FSBOListingRepo:
    """CRUD operations on the ``fsbo_listings`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs: Any) -> FSBOListingRow:
        """Insert a new FSBO listing row."""
        row = FSBOListingRow(**kwargs)
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_by_source_url(self, source_url: str) -> FSBOListingRow | None:
        """Fetch an FSBO listing by its source URL (deduplication key)."""
        stmt = select(FSBOListingRow).where(
            FSBOListingRow.source_url == source_url
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_recent(self, limit: int = 50) -> Sequence[FSBOListingRow]:
        """Return the most recent FSBO listings."""
        stmt = (
            select(FSBOListingRow)
            .order_by(desc(FSBOListingRow.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
