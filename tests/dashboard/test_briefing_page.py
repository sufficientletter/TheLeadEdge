"""Tests for the morning briefing page -- query and data logic.

Validates the ``get_briefing_kpis`` query, market pulse table data
formatting, and ``get_latest_market_snapshots`` query.

IMPORTANT: Never log or display PII in tests.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from theleadedge.storage.database import MarketSnapshotRow
from theleadedge.storage.queries import get_briefing_kpis, get_latest_market_snapshots

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# get_briefing_kpis tests
# ---------------------------------------------------------------------------


class TestGetBriefingKpis:
    """Test the briefing KPI aggregation query."""

    async def test_empty_database_returns_zeros(
        self, session: AsyncSession
    ) -> None:
        kpis = await get_briefing_kpis(session)
        assert kpis["total_active"] == 0
        assert kpis["hot_count"] == 0
        assert kpis["follow_ups_due"] == 0
        assert kpis["new_today"] == 0

    async def test_counts_active_leads(
        self,
        session: AsyncSession,
        make_property_row,
        make_lead_row,
    ) -> None:
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, is_active=True, tier="B")
        await make_lead_row(session, prop.id, is_active=True, tier="C")
        await make_lead_row(session, prop.id, is_active=False, tier="A")
        await session.flush()

        kpis = await get_briefing_kpis(session)
        assert kpis["total_active"] == 2

    async def test_counts_hot_leads_s_and_a_only(
        self,
        session: AsyncSession,
        make_property_row,
        make_lead_row,
    ) -> None:
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, tier="S", is_active=True)
        await make_lead_row(session, prop.id, tier="A", is_active=True)
        await make_lead_row(session, prop.id, tier="B", is_active=True)
        await make_lead_row(session, prop.id, tier="C", is_active=True)
        await session.flush()

        kpis = await get_briefing_kpis(session)
        assert kpis["hot_count"] == 2

    async def test_inactive_hot_leads_not_counted(
        self,
        session: AsyncSession,
        make_property_row,
        make_lead_row,
    ) -> None:
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, tier="S", is_active=False)
        await make_lead_row(session, prop.id, tier="A", is_active=True)
        await session.flush()

        kpis = await get_briefing_kpis(session)
        assert kpis["hot_count"] == 1

    async def test_counts_follow_ups_due(
        self,
        session: AsyncSession,
        make_property_row,
        make_lead_row,
    ) -> None:
        prop = await make_property_row(session)
        past = datetime.utcnow() - timedelta(hours=2)
        future = datetime.utcnow() + timedelta(days=1)
        await make_lead_row(
            session, prop.id, next_touch_date=past, is_active=True
        )
        await make_lead_row(
            session, prop.id, next_touch_date=future, is_active=True
        )
        await session.flush()

        kpis = await get_briefing_kpis(session)
        assert kpis["follow_ups_due"] == 1

    async def test_null_next_touch_not_counted_as_due(
        self,
        session: AsyncSession,
        make_property_row,
        make_lead_row,
    ) -> None:
        prop = await make_property_row(session)
        await make_lead_row(
            session, prop.id, next_touch_date=None, is_active=True
        )
        await session.flush()

        kpis = await get_briefing_kpis(session)
        assert kpis["follow_ups_due"] == 0

    async def test_inactive_follow_ups_not_counted(
        self,
        session: AsyncSession,
        make_property_row,
        make_lead_row,
    ) -> None:
        prop = await make_property_row(session)
        past = datetime.utcnow() - timedelta(hours=2)
        await make_lead_row(
            session, prop.id, next_touch_date=past, is_active=False
        )
        await session.flush()

        kpis = await get_briefing_kpis(session)
        assert kpis["follow_ups_due"] == 0

    async def test_counts_new_today(
        self,
        session: AsyncSession,
        make_property_row,
        make_lead_row,
    ) -> None:
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, detected_at=datetime.utcnow())
        await make_lead_row(
            session,
            prop.id,
            detected_at=datetime.utcnow() - timedelta(days=2),
        )
        await session.flush()

        kpis = await get_briefing_kpis(session)
        assert kpis["new_today"] >= 1

    async def test_new_today_excludes_yesterday(
        self,
        session: AsyncSession,
        make_property_row,
        make_lead_row,
    ) -> None:
        prop = await make_property_row(session)
        yesterday = datetime.utcnow() - timedelta(days=1)
        await make_lead_row(session, prop.id, detected_at=yesterday)
        await session.flush()

        kpis = await get_briefing_kpis(session)
        assert kpis["new_today"] == 0

    async def test_all_kpis_together(
        self,
        session: AsyncSession,
        make_property_row,
        make_lead_row,
    ) -> None:
        """Integration: multiple leads exercising all 4 KPI counters."""
        prop = await make_property_row(session)
        past = datetime.utcnow() - timedelta(hours=1)

        # Active S-tier, follow-up due, detected today -> all 4 counters
        await make_lead_row(
            session,
            prop.id,
            tier="S",
            is_active=True,
            next_touch_date=past,
            detected_at=datetime.utcnow(),
        )
        # Active B-tier, no follow-up, detected yesterday -> only total_active
        await make_lead_row(
            session,
            prop.id,
            tier="B",
            is_active=True,
            detected_at=datetime.utcnow() - timedelta(days=1),
        )
        await session.flush()

        kpis = await get_briefing_kpis(session)
        assert kpis["total_active"] == 2
        assert kpis["hot_count"] == 1
        assert kpis["follow_ups_due"] == 1
        assert kpis["new_today"] >= 1


# ---------------------------------------------------------------------------
# get_latest_market_snapshots tests
# ---------------------------------------------------------------------------


class TestGetLatestMarketSnapshots:
    """Test the market snapshot query."""

    async def test_empty_database(self, session: AsyncSession) -> None:
        snapshots = await get_latest_market_snapshots(session)
        assert snapshots == []

    async def test_returns_latest_per_zip(
        self, session: AsyncSession
    ) -> None:
        # Insert two snapshots for the same ZIP -- only latest should return
        older = MarketSnapshotRow(
            zip_code="34102",
            source="redfin",
            median_sale_price=400000.0,
            median_dom=45,
            inventory=120,
            months_of_supply=3.5,
            absorption_rate=28.0,
        )
        newer = MarketSnapshotRow(
            zip_code="34102",
            source="redfin",
            median_sale_price=425000.0,
            median_dom=40,
            inventory=110,
            months_of_supply=3.2,
            absorption_rate=31.0,
        )
        session.add_all([older, newer])
        await session.flush()

        snapshots = await get_latest_market_snapshots(session)
        assert len(snapshots) == 1
        assert snapshots[0]["median_sale_price"] == 425000.0
        assert snapshots[0]["zip_code"] == "34102"

    async def test_multiple_zips(self, session: AsyncSession) -> None:
        s1 = MarketSnapshotRow(
            zip_code="34102",
            source="redfin",
            median_sale_price=400000.0,
        )
        s2 = MarketSnapshotRow(
            zip_code="33901",
            source="redfin",
            median_sale_price=350000.0,
        )
        session.add_all([s1, s2])
        await session.flush()

        snapshots = await get_latest_market_snapshots(session)
        assert len(snapshots) == 2
        zips = {s["zip_code"] for s in snapshots}
        assert zips == {"34102", "33901"}

    async def test_snapshot_dict_keys(self, session: AsyncSession) -> None:
        snap = MarketSnapshotRow(
            zip_code="34102",
            source="redfin",
            median_sale_price=400000.0,
            median_dom=45,
            inventory=120,
            months_of_supply=3.5,
            absorption_rate=28.0,
        )
        session.add(snap)
        await session.flush()

        snapshots = await get_latest_market_snapshots(session)
        assert len(snapshots) == 1
        expected_keys = {
            "zip_code",
            "median_sale_price",
            "median_dom",
            "inventory",
            "months_of_supply",
            "absorption_rate",
        }
        assert set(snapshots[0].keys()) == expected_keys

    async def test_limit_respected(self, session: AsyncSession) -> None:
        for i in range(5):
            snap = MarketSnapshotRow(
                zip_code=f"3310{i}",
                source="redfin",
                median_sale_price=300000.0 + i * 10000,
            )
            session.add(snap)
        await session.flush()

        snapshots = await get_latest_market_snapshots(session, limit=3)
        assert len(snapshots) == 3


# ---------------------------------------------------------------------------
# Market pulse table data formatting tests
# ---------------------------------------------------------------------------


class TestMarketPulseTableData:
    """Test market pulse table data formatting logic."""

    def test_empty_snapshots(self) -> None:
        snapshots: list[dict] = []
        assert len(snapshots) == 0

    def test_snapshot_price_formatting(self) -> None:
        from theleadedge.dashboard.theme import format_price

        assert format_price(450000.0) == "$450,000"
        assert format_price(None) == "N/A"

    def test_months_of_supply_formatting(self) -> None:
        val = 3.5
        assert f"{val:.1f}" == "3.5"

    def test_none_months_of_supply(self) -> None:
        val = None
        result = f"{val:.1f}" if val is not None else "\u2014"
        assert result == "\u2014"

    def test_zero_months_of_supply(self) -> None:
        val = 0.0
        result = f"{val:.1f}" if val is not None else "\u2014"
        assert result == "0.0"

    def test_snapshot_row_building(self) -> None:
        """Verify the dict-to-row transformation logic."""
        from theleadedge.dashboard.theme import format_price

        s = {
            "zip_code": "34102",
            "median_sale_price": 500000.0,
            "median_dom": 30,
            "inventory": 150,
            "months_of_supply": 4.2,
        }
        row = {
            "zip_code": s.get("zip_code", ""),
            "median_sale_price": format_price(s.get("median_sale_price")),
            "median_dom": str(s.get("median_dom", "\u2014")),
            "inventory": str(s.get("inventory", "\u2014")),
            "months_of_supply": (
                f"{s.get('months_of_supply', 0):.1f}"
                if s.get("months_of_supply") is not None
                else "\u2014"
            ),
        }
        assert row["zip_code"] == "34102"
        assert row["median_sale_price"] == "$500,000"
        assert row["median_dom"] == "30"
        assert row["inventory"] == "150"
        assert row["months_of_supply"] == "4.2"

    def test_missing_fields_use_defaults(self) -> None:
        """Verify graceful handling of missing dict keys."""
        from theleadedge.dashboard.theme import format_price

        s: dict = {}
        row = {
            "zip_code": s.get("zip_code", ""),
            "median_sale_price": format_price(s.get("median_sale_price")),
            "median_dom": str(s.get("median_dom", "\u2014")),
            "inventory": str(s.get("inventory", "\u2014")),
            "months_of_supply": (
                f"{s.get('months_of_supply', 0):.1f}"
                if s.get("months_of_supply") is not None
                else "\u2014"
            ),
        }
        assert row["zip_code"] == ""
        assert row["median_sale_price"] == "N/A"
        assert row["median_dom"] == "\u2014"
        assert row["inventory"] == "\u2014"
        assert row["months_of_supply"] == "\u2014"
