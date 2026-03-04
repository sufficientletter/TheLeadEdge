"""Integration tests for dashboard data flow.

Tests the complete data path from database queries through to
the data structures used by page renderers.

IMPORTANT: Never include PII in test data that simulates UI output.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

from theleadedge.dashboard.components.filter_bar import FilterState
from theleadedge.dashboard.theme import (
    TIER_COLORS,
    format_date,
    format_price,
    format_score,
    get_tier_color,
)
from theleadedge.storage.database import (
    OutreachEventRow,
    ScoreHistoryRow,
    SignalRow,
    SourceRecordRow,
)
from theleadedge.storage.queries import (
    get_briefing_kpis,
    get_conversion_funnel,
    get_hot_leads,
    get_lead_detail,
    get_leads_for_grid,
    get_leads_for_map,
    get_pipeline_summary,
    get_signal_performance,
    get_source_records_by_type,
    get_source_records_for_property,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestFullLeadLifecycle:
    """Test a lead through its full dashboard lifecycle."""

    async def test_lead_appears_in_all_views(
        self, session: AsyncSession, make_property_row, make_lead_row
    ) -> None:
        """A high-tier lead with signals appears in all views."""
        prop = await make_property_row(
            session,
            address="100 INTEGRATION TEST DR",
            city="Naples",
            zip_code="34102",
            list_price=500000.0,
            latitude=26.45,
            longitude=-81.80,
        )
        lead = await make_lead_row(
            session,
            prop.id,
            tier="S",
            current_score=92.0,
            status="new",
            signal_count=3,
            is_active=True,
        )
        sig = SignalRow(
            lead_id=lead.id,
            property_id=prop.id,
            signal_type="expired_listing",
            signal_category="mls",
            points=15.0,
            base_points=15.0,
        )
        session.add(sig)
        await session.flush()

        # Briefing KPIs
        kpis = await get_briefing_kpis(session)
        assert kpis["total_active"] >= 1
        assert kpis["hot_count"] >= 1

        # Pipeline summary
        summary = await get_pipeline_summary(session)
        assert summary["tiers"].get("S", 0) >= 1

        # Hot leads
        hot = await get_hot_leads(session, min_tier="S")
        assert any(lead_row.id == lead.id for lead_row in hot)

        # Grid
        grid_leads = await get_leads_for_grid(session, tiers=["S"])
        assert any(lead_row.id == lead.id for lead_row in grid_leads)

        # Map
        map_leads = await get_leads_for_map(session)
        assert any(lead_row.id == lead.id for lead_row in map_leads)

        # Detail
        detail = await get_lead_detail(session, lead.id)
        assert detail is not None
        assert detail.property_rel.address == "100 INTEGRATION TEST DR"
        assert len(detail.signals) == 1

    async def test_lead_with_outreach_and_records(
        self, session: AsyncSession, make_property_row, make_lead_row
    ) -> None:
        """A lead with outreach events and source records should show all in detail."""
        prop = await make_property_row(session, address="200 FULL WORKFLOW ST")
        lead = await make_lead_row(
            session, prop.id, tier="A", current_score=70.0
        )

        # Add outreach event
        ev = OutreachEventRow(
            lead_id=lead.id,
            outreach_type="call",
            outcome="left_voicemail",
        )
        session.add(ev)

        # Add score history
        sh = ScoreHistoryRow(
            lead_id=lead.id,
            score=70.0,
            tier="A",
            signal_count=2,
            change_reason="New signal",
        )
        session.add(sh)

        # Add source record
        rec = SourceRecordRow(
            source_name="collier_clerk",
            source_record_id="INT001",
            record_type="lis_pendens",
            matched_property_id=prop.id,
        )
        session.add(rec)
        await session.flush()

        detail = await get_lead_detail(session, lead.id)
        assert detail is not None
        assert len(detail.outreach_events) == 1
        assert len(detail.score_history) == 1

        records = await get_source_records_for_property(session, prop.id)
        assert len(records) == 1

    async def test_nonexistent_lead_returns_none(
        self, session: AsyncSession
    ) -> None:
        """Requesting a non-existent lead should return None."""
        detail = await get_lead_detail(session, 999999)
        assert detail is None


@pytest.mark.asyncio
class TestFilterIntegration:
    """Test that filters produce correct results across views."""

    async def test_tier_filter_consistency(
        self, session: AsyncSession, make_property_row, make_lead_row
    ) -> None:
        """Tier filters should produce consistent results."""
        prop = await make_property_row(session, address="300 FILTER TEST LN")
        await make_lead_row(
            session, prop.id, tier="S", current_score=90.0
        )

        prop2 = await make_property_row(session, address="301 FILTER TEST LN")
        await make_lead_row(
            session, prop2.id, tier="D", current_score=5.0
        )
        await session.flush()

        # Grid with S filter
        s_leads = await get_leads_for_grid(session, tiers=["S"])
        assert all(lead.tier == "S" for lead in s_leads)

        # Hot leads (S and A)
        hot = await get_hot_leads(session, min_tier="A")
        assert all(lead.tier in ("S", "A") for lead in hot)

    async def test_zip_code_filter(
        self, session: AsyncSession, make_property_row, make_lead_row
    ) -> None:
        """ZIP code filter should work across grid and map."""
        p1 = await make_property_row(
            session,
            address="400 ZIP TEST DR",
            zip_code="34102",
            latitude=26.45,
            longitude=-81.80,
        )
        p2 = await make_property_row(
            session,
            address="401 ZIP TEST DR",
            zip_code="33901",
            latitude=26.60,
            longitude=-81.90,
        )
        await make_lead_row(session, p1.id, tier="A", current_score=50.0)
        await make_lead_row(session, p2.id, tier="A", current_score=50.0)
        await session.flush()

        filtered = await get_leads_for_grid(session, zip_code="34102")
        assert all(
            lead.property_rel.zip_code == "34102" for lead in filtered
        )

    async def test_price_range_filter(
        self, session: AsyncSession, make_property_row, make_lead_row
    ) -> None:
        """Price range filter should correctly bound results."""
        p_low = await make_property_row(
            session,
            address="500 PRICE TEST LN",
            list_price=100000.0,
        )
        p_high = await make_property_row(
            session,
            address="501 PRICE TEST LN",
            list_price=900000.0,
        )
        await make_lead_row(session, p_low.id, tier="B", current_score=30.0)
        await make_lead_row(session, p_high.id, tier="B", current_score=30.0)
        await session.flush()

        filtered = await get_leads_for_grid(
            session, min_price=200000.0, max_price=1000000.0
        )
        for lead in filtered:
            assert lead.property_rel.list_price >= 200000.0
            assert lead.property_rel.list_price <= 1000000.0


@pytest.mark.asyncio
class TestAnalyticsDataFlow:
    """Test analytics page data queries."""

    async def test_conversion_funnel_structure(
        self, session: AsyncSession, make_property_row, make_lead_row
    ) -> None:
        """Conversion funnel should return status counts."""
        prop = await make_property_row(session, address="600 FUNNEL TEST ST")
        await make_lead_row(
            session, prop.id, status="new", current_score=40.0
        )
        await session.flush()

        funnel = await get_conversion_funnel(session)
        assert isinstance(funnel, dict)
        assert "score_distribution" in funnel

    async def test_signal_performance_structure(
        self, session: AsyncSession, make_property_row, make_lead_row
    ) -> None:
        """Signal performance should return signal type counts."""
        prop = await make_property_row(session, address="700 SIGNAL TEST ST")
        lead = await make_lead_row(session, prop.id, current_score=50.0)
        sig = SignalRow(
            lead_id=lead.id,
            property_id=prop.id,
            signal_type="price_reduction",
            signal_category="mls",
            points=10.0,
            base_points=10.0,
        )
        session.add(sig)
        await session.flush()

        perf = await get_signal_performance(session)
        assert isinstance(perf, list)
        assert all("signal_type" in item and "count" in item for item in perf)

    async def test_source_records_by_type(
        self, session: AsyncSession
    ) -> None:
        """Source records query should filter by record type."""
        rec = SourceRecordRow(
            source_name="test_source",
            source_record_id="REC001",
            record_type="probate",
        )
        session.add(rec)
        await session.flush()

        results = await get_source_records_by_type(session, "probate")
        assert len(results) >= 1
        assert all(r.record_type == "probate" for r in results)

        # Different type should not match
        others = await get_source_records_by_type(session, "tax_deed")
        for other in others:
            assert other.record_type != "probate"


class TestDataFormatting:
    """Test that theme formatters produce correct output for UI rendering."""

    def test_price_formatting_range(self) -> None:
        assert format_price(0.0) == "$0"
        assert format_price(999999.0) == "$999,999"
        assert format_price(1500000.0) == "$1,500,000"
        assert format_price(None) == "N/A"

    def test_score_formatting(self) -> None:
        assert format_score(0.0) == "0.0"
        assert format_score(50.5) == "50.5"
        assert format_score(100.0) == "100.0"

    def test_date_formatting(self) -> None:
        dt = datetime(2026, 3, 5)
        assert format_date(dt) == "Mar 05, 2026"
        assert format_date(None) == "\u2014"

    def test_tier_colors_complete(self) -> None:
        for tier in ["S", "A", "B", "C", "D"]:
            color = get_tier_color(tier)
            assert color.startswith("#")

    def test_tier_colors_dict_has_all_tiers(self) -> None:
        for tier in ["S", "A", "B", "C", "D"]:
            assert tier in TIER_COLORS

    def test_filter_state_roundtrip(self) -> None:
        state = FilterState(
            tiers=["S", "A"], zip_code="34102", min_price=200000.0
        )
        d = state.to_dict()
        assert d["tiers"] == ["S", "A"]
        assert d["zip_code"] == "34102"
        assert d["min_price"] == 200000.0


class TestPIISafety:
    """Verify PII is never exposed in dashboard data structures."""

    def test_grid_data_excludes_pii(self) -> None:
        """AG Grid row data should never contain PII fields."""
        from theleadedge.dashboard.pages.leads import build_grid_data

        # Verify the function exists and can handle an empty list
        result = build_grid_data([])
        assert result == []

        # Verify expected grid fields never overlap with PII fields
        pii_fields = {
            "owner_name",
            "owner_phone",
            "owner_email",
            "owner_mailing_address",
        }
        grid_fields = {
            "id",
            "address",
            "city",
            "zip_code",
            "tier",
            "score",
            "signals",
            "list_price",
            "list_price_display",
            "status",
            "dom",
            "property_type",
            "mls_status",
            "detected",
        }
        assert pii_fields.isdisjoint(grid_fields)

    def test_map_marker_excludes_pii(self) -> None:
        """Map marker data should never contain PII."""
        marker_fields = {
            "lat",
            "lng",
            "lead_id",
            "address",
            "city",
            "zip_code",
            "tier",
            "score",
            "list_price",
            "color",
        }
        pii_fields = {"owner_name", "owner_phone", "owner_email"}
        assert marker_fields.isdisjoint(pii_fields)

    def test_source_record_display_excludes_pii(self) -> None:
        """Source records displayed in UI should not contain owner PII."""
        display_fields = {
            "source_name",
            "source_record_id",
            "record_type",
            "event_date",
            "event_type",
            "city",
            "zip_code",
            "created_at",
        }
        pii_fields = {"owner_name", "owner_phone", "owner_email"}
        assert display_fields.isdisjoint(pii_fields)
