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
    MatchQueueRow,
    PropertyRow,
    ScoreHistoryRow,
    SignalRow,
    SourceRecordRow,
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
# Lead Pipeline Grid (dashboard)
# ---------------------------------------------------------------------------


async def get_leads_for_grid(
    session: AsyncSession,
    *,
    tiers: list[str] | None = None,
    statuses: list[str] | None = None,
    zip_code: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 500,
) -> Sequence[LeadRow]:
    """Get leads for the AG Grid display with optional filters.

    Returns leads with ``property_rel`` and ``signals`` eagerly loaded.
    Filters are ANDed together.  ``None`` or empty list means no filter
    for that dimension.

    IMPORTANT: Results are used in AG Grid (client-side JSON).
    Never include PII fields in the data sent to the grid.

    Parameters
    ----------
    session:
        Active database session.
    tiers:
        Filter to these tier letters (e.g. ``["S", "A"]``).
    statuses:
        Filter to these lead statuses (e.g. ``["new", "contacted"]``).
    zip_code:
        Filter to a single ZIP code.
    min_price:
        Minimum list price (inclusive).
    max_price:
        Maximum list price (inclusive).
    limit:
        Maximum rows to return.  Default 500.

    Returns
    -------
    Sequence[LeadRow]
        Leads ordered by score descending, with property_rel loaded.
    """
    # Build the base query -- always filter to active leads
    stmt = (
        select(LeadRow)
        .where(LeadRow.is_active.is_(True))
        .options(
            selectinload(LeadRow.property_rel),
            selectinload(LeadRow.signals),
        )
    )

    # Apply optional filters
    if tiers:
        stmt = stmt.where(LeadRow.tier.in_(tiers))
    if statuses:
        stmt = stmt.where(LeadRow.status.in_(statuses))

    # Property-level filters require a join
    needs_join = any(f is not None for f in [zip_code, min_price, max_price])
    if needs_join:
        stmt = stmt.join(PropertyRow, LeadRow.property_id == PropertyRow.id)
        if zip_code:
            stmt = stmt.where(PropertyRow.zip_code == zip_code)
        if min_price is not None:
            stmt = stmt.where(PropertyRow.list_price >= min_price)
        if max_price is not None:
            stmt = stmt.where(PropertyRow.list_price <= max_price)

    stmt = stmt.order_by(desc(LeadRow.current_score)).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


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


# ---------------------------------------------------------------------------
# Briefing KPIs (morning briefing page)
# ---------------------------------------------------------------------------


async def get_briefing_kpis(session: AsyncSession) -> dict[str, Any]:
    """Compute KPI values for the morning briefing header.

    Returns
    -------
    dict
        ``{"total_active": int, "hot_count": int,
        "follow_ups_due": int, "new_today": int}``
    """
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Total active leads
    total_stmt = (
        select(func.count()).select_from(LeadRow).where(LeadRow.is_active.is_(True))
    )
    total_active = (await session.execute(total_stmt)).scalar() or 0

    # Hot leads (S + A tier)
    hot_stmt = (
        select(func.count())
        .select_from(LeadRow)
        .where(LeadRow.is_active.is_(True), LeadRow.tier.in_(["S", "A"]))
    )
    hot_count = (await session.execute(hot_stmt)).scalar() or 0

    # Follow-ups due (next_touch_date in the past)
    fu_stmt = (
        select(func.count())
        .select_from(LeadRow)
        .where(
            LeadRow.is_active.is_(True),
            LeadRow.next_touch_date.isnot(None),
            LeadRow.next_touch_date <= now,
        )
    )
    follow_ups_due = (await session.execute(fu_stmt)).scalar() or 0

    # New leads detected today
    new_stmt = (
        select(func.count())
        .select_from(LeadRow)
        .where(LeadRow.detected_at >= today_start)
    )
    new_today = (await session.execute(new_stmt)).scalar() or 0

    return {
        "total_active": total_active,
        "hot_count": hot_count,
        "follow_ups_due": follow_ups_due,
        "new_today": new_today,
    }


# ---------------------------------------------------------------------------
# Market Snapshots (briefing market pulse)
# ---------------------------------------------------------------------------


async def get_latest_market_snapshots(
    session: AsyncSession,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Return the latest market snapshot per ZIP code.

    Used by the morning briefing to show the market pulse table.

    Returns
    -------
    list[dict]
        Each dict has keys matching MarketSnapshotRow columns.
    """
    from .database import MarketSnapshotRow

    # Subquery to get the max id (latest) per ZIP code
    latest_ids_stmt = (
        select(func.max(MarketSnapshotRow.id))
        .group_by(MarketSnapshotRow.zip_code)
    )
    stmt = (
        select(MarketSnapshotRow)
        .where(MarketSnapshotRow.id.in_(latest_ids_stmt))
        .order_by(MarketSnapshotRow.zip_code)
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()

    return [
        {
            "zip_code": r.zip_code,
            "median_sale_price": r.median_sale_price,
            "median_dom": r.median_dom,
            "inventory": r.inventory,
            "months_of_supply": r.months_of_supply,
            "absorption_rate": r.absorption_rate,
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Lead Detail (single lead deep-dive)
# ---------------------------------------------------------------------------


async def get_lead_detail(
    session: AsyncSession,
    lead_id: int,
) -> LeadRow | None:
    """Get a single lead with all relationships eagerly loaded.

    Used by the lead detail page for the deep-dive view.
    Loads property, signals, score history, and outreach events
    in a single query with selectinload.

    Parameters
    ----------
    session:
        Active database session.
    lead_id:
        Primary key of the lead to load.

    Returns
    -------
    LeadRow or None
        The fully-loaded lead, or None if not found.
    """
    stmt = (
        select(LeadRow)
        .where(LeadRow.id == lead_id)
        .options(
            selectinload(LeadRow.property_rel),
            selectinload(LeadRow.signals),
            selectinload(LeadRow.score_history),
            selectinload(LeadRow.outreach_events),
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Source Records for Property (lead detail)
# ---------------------------------------------------------------------------


async def get_source_records_for_property(
    session: AsyncSession,
    property_id: int,
) -> list:
    """Get source records matched to a property.

    Used by the lead detail page to show public records
    associated with the property.

    Parameters
    ----------
    session:
        Active database session.
    property_id:
        Primary key of the property.

    Returns
    -------
    list[SourceRecordRow]
        Source records ordered by creation date descending.
    """
    stmt = (
        select(SourceRecordRow)
        .where(SourceRecordRow.matched_property_id == property_id)
        .order_by(desc(SourceRecordRow.created_at))
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Leads for Map (Batch 6)
# ---------------------------------------------------------------------------


async def get_leads_for_map(
    session: AsyncSession,
    min_tier: str = "D",
) -> Sequence[LeadRow]:
    """Get active leads with non-null coordinates for the map view.

    Returns leads with ``property_rel`` loaded, filtered to those
    having valid latitude and longitude.

    Parameters
    ----------
    session:
        Active database session.
    min_tier:
        Minimum tier threshold (inclusive).  Default ``"D"`` returns
        all tiers.

    Returns
    -------
    Sequence[LeadRow]
        Leads ordered by score descending, limited to 1000.
    """
    min_val = _TIER_VALUES.get(min_tier, 0)
    valid_tiers = [t for t, v in _TIER_VALUES.items() if v >= min_val]

    stmt = (
        select(LeadRow)
        .join(PropertyRow)
        .where(
            LeadRow.is_active.is_(True),
            LeadRow.tier.in_(valid_tiers),
            PropertyRow.latitude.isnot(None),
            PropertyRow.longitude.isnot(None),
        )
        .options(selectinload(LeadRow.property_rel))
        .order_by(desc(LeadRow.current_score))
        .limit(1000)
    )
    result = await session.execute(stmt)
    return result.scalars().unique().all()


# ---------------------------------------------------------------------------
# Source Records by Type (Batch 7)
# ---------------------------------------------------------------------------


async def get_source_records_by_type(
    session: AsyncSession,
    record_type: str,
    limit: int = 500,
) -> Sequence[SourceRecordRow]:
    """Get source records filtered by record type.

    IMPORTANT: Never return owner PII fields to the UI.

    Parameters
    ----------
    session:
        Active database session.
    record_type:
        Filter value (e.g. ``"lis_pendens"``, ``"probate"``).
    limit:
        Maximum rows to return.

    Returns
    -------
    Sequence[SourceRecordRow]
        Records ordered by created_at descending.
    """
    stmt = (
        select(SourceRecordRow)
        .where(SourceRecordRow.record_type == record_type)
        .order_by(desc(SourceRecordRow.created_at))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Match Queue Pending (Batch 7)
# ---------------------------------------------------------------------------


async def get_match_queue_pending(
    session: AsyncSession,
    limit: int = 100,
) -> Sequence[MatchQueueRow]:
    """Get pending items from the match queue.

    Parameters
    ----------
    session:
        Active database session.
    limit:
        Maximum rows to return.

    Returns
    -------
    Sequence[MatchQueueRow]
        Pending queue items ordered by created_at descending.
    """
    stmt = (
        select(MatchQueueRow)
        .where(MatchQueueRow.status == "pending")
        .order_by(desc(MatchQueueRow.created_at))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Conversion Funnel (Batch 8)
# ---------------------------------------------------------------------------


async def get_conversion_funnel(session: AsyncSession) -> dict[str, Any]:
    """Get conversion funnel counts by lead status.

    Returns a dict with status counts (e.g. ``{"new": 20, ...}``)
    and a nested ``"score_distribution"`` dict with bucket counts.

    Parameters
    ----------
    session:
        Active database session.

    Returns
    -------
    dict
        Status counts plus ``score_distribution`` bucket counts.
    """
    # Status counts
    status_stmt = (
        select(LeadRow.status, func.count())
        .where(LeadRow.is_active.is_(True))
        .group_by(LeadRow.status)
    )
    result = await session.execute(status_stmt)
    status_counts: dict[str, Any] = dict(result.all())

    # Score distribution (buckets of 10)
    score_dist: dict[str, int] = {}
    for bucket_start in range(0, 100, 10):
        bucket_end = bucket_start + 10
        label = f"{bucket_start}-{bucket_end}"
        stmt = (
            select(func.count())
            .select_from(LeadRow)
            .where(
                LeadRow.is_active.is_(True),
                LeadRow.current_score >= bucket_start,
                LeadRow.current_score < bucket_end,
            )
        )
        count = (await session.execute(stmt)).scalar() or 0
        score_dist[label] = count

    status_counts["score_distribution"] = score_dist
    return status_counts


# ---------------------------------------------------------------------------
# Signal Performance (Batch 8)
# ---------------------------------------------------------------------------


async def get_signal_performance(
    session: AsyncSession,
    limit: int = 15,
) -> list[dict[str, Any]]:
    """Get signal type counts for performance analysis.

    Parameters
    ----------
    session:
        Active database session.
    limit:
        Maximum number of signal types to return.

    Returns
    -------
    list[dict]
        Each dict has ``signal_type`` and ``count`` keys, ordered by
        count descending.
    """
    stmt = (
        select(SignalRow.signal_type, func.count().label("count"))
        .where(SignalRow.is_active.is_(True))
        .group_by(SignalRow.signal_type)
        .order_by(desc(func.count()))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [{"signal_type": row[0], "count": row[1]} for row in result.all()]


# ---------------------------------------------------------------------------
# Tier Distribution Over Time (Batch 8)
# ---------------------------------------------------------------------------


async def get_tier_distribution_over_time(
    session: AsyncSession,
    limit: int = 30,
) -> list[dict[str, Any]]:
    """Get daily tier distribution from score history.

    Parameters
    ----------
    session:
        Active database session.
    limit:
        Maximum number of dates to return.

    Returns
    -------
    list[dict]
        Each dict has ``date``, ``S``, ``A``, ``B``, ``C``, ``D`` keys.
        Sorted by date ascending, limited to most recent *limit* dates.
    """
    stmt = (
        select(
            func.date(ScoreHistoryRow.calculated_at).label("date"),
            ScoreHistoryRow.tier,
            func.count().label("count"),
        )
        .group_by(
            func.date(ScoreHistoryRow.calculated_at), ScoreHistoryRow.tier
        )
        .order_by(desc(func.date(ScoreHistoryRow.calculated_at)))
        .limit(limit * 5)  # 5 tiers per date
    )
    result = await session.execute(stmt)

    # Pivot into per-date dicts
    date_map: dict[str, dict[str, Any]] = {}
    for date_val, tier, count in result.all():
        date_str = str(date_val)
        if date_str not in date_map:
            date_map[date_str] = {
                "date": date_str,
                "S": 0,
                "A": 0,
                "B": 0,
                "C": 0,
                "D": 0,
            }
        date_map[date_str][tier] = count

    return sorted(date_map.values(), key=lambda d: d["date"])[-limit:]


# ---------------------------------------------------------------------------
# Source ROI (Batch 8)
# ---------------------------------------------------------------------------


async def get_source_roi(
    session: AsyncSession,
) -> list[dict[str, Any]]:
    """Get lead counts by data source for ROI analysis.

    Parameters
    ----------
    session:
        Active database session.

    Returns
    -------
    list[dict]
        Each dict has ``source`` and ``count`` keys, ordered by
        count descending.
    """
    stmt = (
        select(PropertyRow.data_source, func.count().label("count"))
        .join(LeadRow, PropertyRow.id == LeadRow.property_id)
        .where(
            LeadRow.is_active.is_(True),
            PropertyRow.data_source.isnot(None),
        )
        .group_by(PropertyRow.data_source)
        .order_by(desc(func.count()))
    )
    result = await session.execute(stmt)
    return [{"source": row[0], "count": row[1]} for row in result.all()]
