"""Named queries for TheLeadEdge briefing and dashboard.

These are read-only query functions used by the daily briefing email
generator and the NiceGUI dashboard.  Each function takes an
``AsyncSession`` and returns structured results.

All queries use SQLAlchemy 2.0 ``select()`` style.  Eager-loading via
``selectinload`` is applied where the caller needs related objects
(e.g., property data alongside leads).
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .database import (
    LeadRow,
    PropertyRow,
    ScoreHistoryRow,
    SignalRow,
    SyncLogRow,
)

# ---------------------------------------------------------------------------
# Tier ordering helper
# ---------------------------------------------------------------------------

_TIER_VALUES: dict[str, int] = {"S": 4, "A": 3, "B": 2, "C": 1, "D": 0}


# ---------------------------------------------------------------------------
# Hot Leads (daily briefing)
# ---------------------------------------------------------------------------


async def get_hot_leads(
    session: AsyncSession,
    min_tier: str = "B",
) -> Sequence[LeadRow]:
    """Get active leads at *min_tier* or above, ordered by score descending.

    Parameters
    ----------
    session:
        Active database session.
    min_tier:
        Minimum tier threshold (inclusive).  Default ``"B"`` returns
        S, A, and B-tier leads.

    Returns
    -------
    Sequence[LeadRow]
        Leads with ``property_rel`` eagerly loaded.
    """
    min_val = _TIER_VALUES.get(min_tier, 0)
    valid_tiers = [t for t, v in _TIER_VALUES.items() if v >= min_val]

    stmt = (
        select(LeadRow)
        .where(
            LeadRow.is_active.is_(True),
            LeadRow.tier.in_(valid_tiers),
        )
        .options(
            selectinload(LeadRow.property_rel),
            selectinload(LeadRow.signals),
        )
        .order_by(desc(LeadRow.current_score))
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Pipeline Summary (dashboard)
# ---------------------------------------------------------------------------


async def get_pipeline_summary(session: AsyncSession) -> dict[str, Any]:
    """Get aggregate counts by tier and status for the dashboard.

    Returns
    -------
    dict
        ``{"tiers": {"S": 3, "A": 12, ...}, "statuses": {"new": 20, ...},
        "total_active": 45}``
    """
    # Count by tier
    tier_stmt = (
        select(LeadRow.tier, func.count())
        .where(LeadRow.is_active.is_(True))
        .group_by(LeadRow.tier)
    )
    tier_result = await session.execute(tier_stmt)
    tier_counts: dict[str, int] = dict(tier_result.all())

    # Count by status
    status_stmt = (
        select(LeadRow.status, func.count())
        .where(LeadRow.is_active.is_(True))
        .group_by(LeadRow.status)
    )
    status_result = await session.execute(status_stmt)
    status_counts: dict[str, int] = dict(status_result.all())

    total = sum(tier_counts.values())

    return {
        "tiers": tier_counts,
        "statuses": status_counts,
        "total_active": total,
    }


# ---------------------------------------------------------------------------
# Tier Changes (briefing alerts)
# ---------------------------------------------------------------------------


async def get_tier_changes(
    session: AsyncSession,
    since: datetime,
) -> list[dict[str, Any]]:
    """Find leads whose tier changed since a given time.

    Compares the lead's current tier with the most recent
    ``ScoreHistoryRow`` entry recorded at or after *since*.  Returns
    only leads where the tier actually differs.

    Returns
    -------
    list[dict]
        Each dict has keys: ``lead``, ``old_tier``, ``new_tier``,
        ``old_score``, ``new_score``.
    """
    stmt = (
        select(LeadRow, ScoreHistoryRow)
        .join(ScoreHistoryRow, LeadRow.id == ScoreHistoryRow.lead_id)
        .where(
            LeadRow.is_active.is_(True),
            ScoreHistoryRow.calculated_at >= since,
        )
        .options(
            selectinload(LeadRow.property_rel),
            selectinload(LeadRow.signals),
        )
        .order_by(desc(ScoreHistoryRow.calculated_at))
    )
    result = await session.execute(stmt)
    rows = result.all()

    changes: list[dict[str, Any]] = []
    seen_leads: set[int] = set()
    for lead, history in rows:
        if lead.id not in seen_leads:
            if lead.tier != history.tier:
                changes.append(
                    {
                        "lead": lead,
                        "old_tier": history.tier,
                        "new_tier": lead.tier,
                        "old_score": history.score,
                        "new_score": lead.current_score,
                    }
                )
            seen_leads.add(lead.id)

    return changes


# ---------------------------------------------------------------------------
# Follow-Ups Due (task list)
# ---------------------------------------------------------------------------


async def get_follow_ups_due(
    session: AsyncSession,
    before: datetime | None = None,
) -> Sequence[LeadRow]:
    """Get leads with follow-up dates that have passed or are due now.

    Parameters
    ----------
    before:
        Cutoff datetime.  Defaults to ``datetime.utcnow()``.

    Returns
    -------
    Sequence[LeadRow]
        Leads ordered by ``next_touch_date`` ascending (most overdue first),
        with ``property_rel`` eagerly loaded.
    """
    cutoff = before or datetime.utcnow()
    stmt = (
        select(LeadRow)
        .where(
            LeadRow.is_active.is_(True),
            LeadRow.next_touch_date.isnot(None),
            LeadRow.next_touch_date <= cutoff,
        )
        .options(
            selectinload(LeadRow.property_rel),
            selectinload(LeadRow.signals),
        )
        .order_by(LeadRow.next_touch_date)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# New Signals (briefing)
# ---------------------------------------------------------------------------


async def get_new_signals_since(
    session: AsyncSession,
    since: datetime,
) -> Sequence[SignalRow]:
    """Return signals detected since a given datetime, newest first.

    Useful for the daily briefing's "new signals" section.
    """
    stmt = (
        select(SignalRow)
        .where(SignalRow.detected_at >= since)
        .order_by(desc(SignalRow.detected_at))
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Stale Leads (monitoring)
# ---------------------------------------------------------------------------


async def get_stale_leads(
    session: AsyncSession,
    stale_days: int = 14,
) -> Sequence[LeadRow]:
    """Return active leads not touched in *stale_days* or more.

    A lead is considered stale if it has no ``last_touch_at`` and was
    detected more than *stale_days* ago, or if ``last_touch_at`` is
    older than the threshold.
    """
    cutoff = datetime.utcnow()
    from datetime import timedelta

    threshold = cutoff - timedelta(days=stale_days)

    stmt = (
        select(LeadRow)
        .where(
            LeadRow.is_active.is_(True),
            LeadRow.tier.in_(["S", "A", "B"]),
            (
                (LeadRow.last_touch_at.is_(None) & (LeadRow.detected_at <= threshold))
                | (LeadRow.last_touch_at <= threshold)
            ),
        )
        .options(
            selectinload(LeadRow.property_rel),
            selectinload(LeadRow.signals),
        )
        .order_by(desc(LeadRow.current_score))
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Sync Health (data-health check)
# ---------------------------------------------------------------------------


async def get_recent_syncs(
    session: AsyncSession,
    limit: int = 10,
) -> Sequence[SyncLogRow]:
    """Return recent sync log entries for the data-health dashboard."""
    stmt = (
        select(SyncLogRow)
        .order_by(desc(SyncLogRow.started_at))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Property Search (dashboard)
# ---------------------------------------------------------------------------


async def search_properties(
    session: AsyncSession,
    *,
    zip_code: str | None = None,
    status: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 100,
) -> Sequence[PropertyRow]:
    """Search properties with optional filters."""
    stmt = select(PropertyRow)

    if zip_code is not None:
        stmt = stmt.where(PropertyRow.zip_code == zip_code)
    if status is not None:
        stmt = stmt.where(PropertyRow.standard_status == status)
    if min_price is not None:
        stmt = stmt.where(PropertyRow.list_price >= min_price)
    if max_price is not None:
        stmt = stmt.where(PropertyRow.list_price <= max_price)

    stmt = stmt.order_by(desc(PropertyRow.created_at)).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()
