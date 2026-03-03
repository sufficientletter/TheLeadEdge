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
    LeadRow,
    OutreachEventRow,
    PriceHistoryRow,
    PropertyRow,
    ScoreHistoryRow,
    SignalRow,
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
