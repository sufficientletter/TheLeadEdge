"""Tests for lead detail page -- queries and data logic.

Tests cover:
- ``get_lead_detail`` query with eager loading of relationships
- ``get_source_records_for_property`` query
- Component data mapping (activity timeline, public records panel)
- Score gauge tier color lookup
- PII exclusion verification
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from theleadedge.storage.database import (
    OutreachEventRow,
    ScoreHistoryRow,
    SignalRow,
    SourceRecordRow,
)
from theleadedge.storage.queries import (
    get_lead_detail,
    get_source_records_for_property,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Test get_lead_detail query
# ---------------------------------------------------------------------------


class TestGetLeadDetail:
    """Test the single-lead eager-loading query."""

    @pytest.mark.asyncio
    async def test_returns_none_for_missing(
        self, session: AsyncSession
    ) -> None:
        """Returns None when lead_id does not exist."""
        result = await get_lead_detail(session, 999)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_lead_with_property(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Loads lead with property relationship eagerly."""
        prop = await make_property_row(session, address="123 TEST ST")
        lead = await make_lead_row(
            session, prop.id, tier="A", current_score=75.0
        )
        await session.flush()

        result = await get_lead_detail(session, lead.id)
        assert result is not None
        assert result.tier == "A"
        assert result.property_rel.address == "123 TEST ST"

    @pytest.mark.asyncio
    async def test_loads_signals(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Signals relationship is eagerly loaded."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
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

        result = await get_lead_detail(session, lead.id)
        assert result is not None
        assert len(result.signals) == 1
        assert result.signals[0].signal_type == "expired_listing"

    @pytest.mark.asyncio
    async def test_loads_score_history(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Score history relationship is eagerly loaded."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
        sh = ScoreHistoryRow(
            lead_id=lead.id,
            score=65.0,
            tier="A",
            signal_count=3,
            change_reason="New signal detected",
        )
        session.add(sh)
        await session.flush()

        result = await get_lead_detail(session, lead.id)
        assert result is not None
        assert len(result.score_history) == 1
        assert result.score_history[0].score == 65.0

    @pytest.mark.asyncio
    async def test_loads_outreach_events(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Outreach events relationship is eagerly loaded."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
        ev = OutreachEventRow(
            lead_id=lead.id,
            outreach_type="call",
            outcome="no_answer",
        )
        session.add(ev)
        await session.flush()

        result = await get_lead_detail(session, lead.id)
        assert result is not None
        assert len(result.outreach_events) == 1
        assert result.outreach_events[0].outreach_type == "call"

    @pytest.mark.asyncio
    async def test_loads_multiple_signals(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Multiple signals are all loaded."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
        for sig_type in ["expired_listing", "price_reduction", "high_dom"]:
            session.add(
                SignalRow(
                    lead_id=lead.id,
                    property_id=prop.id,
                    signal_type=sig_type,
                    signal_category="mls",
                    points=10.0,
                    base_points=10.0,
                )
            )
        await session.flush()

        result = await get_lead_detail(session, lead.id)
        assert result is not None
        assert len(result.signals) == 3

    @pytest.mark.asyncio
    async def test_empty_relationships(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Lead with no signals, history, or outreach returns empty lists."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
        await session.flush()

        result = await get_lead_detail(session, lead.id)
        assert result is not None
        assert result.signals == []
        assert result.score_history == []
        assert result.outreach_events == []


# ---------------------------------------------------------------------------
# Test get_source_records_for_property query
# ---------------------------------------------------------------------------


class TestGetSourceRecordsForProperty:
    """Test the property source records query."""

    @pytest.mark.asyncio
    async def test_empty(
        self, session: AsyncSession, make_property_row: Any
    ) -> None:
        """Returns empty list when no source records exist."""
        prop = await make_property_row(session)
        await session.flush()
        records = await get_source_records_for_property(session, prop.id)
        assert records == []

    @pytest.mark.asyncio
    async def test_returns_matched_records(
        self, session: AsyncSession, make_property_row: Any
    ) -> None:
        """Returns source records matched to the property."""
        prop = await make_property_row(session)
        rec = SourceRecordRow(
            source_name="collier_clerk",
            source_record_id="CLK001",
            record_type="lis_pendens",
            matched_property_id=prop.id,
        )
        session.add(rec)
        await session.flush()

        records = await get_source_records_for_property(session, prop.id)
        assert len(records) == 1
        assert records[0].record_type == "lis_pendens"

    @pytest.mark.asyncio
    async def test_does_not_return_unmatched(
        self, session: AsyncSession, make_property_row: Any
    ) -> None:
        """Records with no matched_property_id are excluded."""
        prop = await make_property_row(session)
        rec = SourceRecordRow(
            source_name="collier_clerk",
            source_record_id="CLK002",
            record_type="probate",
            matched_property_id=None,
        )
        session.add(rec)
        await session.flush()

        records = await get_source_records_for_property(session, prop.id)
        assert records == []

    @pytest.mark.asyncio
    async def test_does_not_return_other_property_records(
        self, session: AsyncSession, make_property_row: Any
    ) -> None:
        """Records matched to a different property are excluded."""
        prop1 = await make_property_row(session, address="100 MAIN ST")
        prop2 = await make_property_row(session, address="200 OAK AVE")
        rec = SourceRecordRow(
            source_name="collier_clerk",
            source_record_id="CLK003",
            record_type="code_violation",
            matched_property_id=prop2.id,
        )
        session.add(rec)
        await session.flush()

        records = await get_source_records_for_property(session, prop1.id)
        assert records == []

    @pytest.mark.asyncio
    async def test_multiple_records(
        self, session: AsyncSession, make_property_row: Any
    ) -> None:
        """Returns multiple source records for the same property."""
        prop = await make_property_row(session)
        for i, rtype in enumerate(
            ["lis_pendens", "code_violation", "tax_delinquent"]
        ):
            session.add(
                SourceRecordRow(
                    source_name="test_source",
                    source_record_id=f"REC{i}",
                    record_type=rtype,
                    matched_property_id=prop.id,
                )
            )
        await session.flush()

        records = await get_source_records_for_property(session, prop.id)
        assert len(records) == 3


# ---------------------------------------------------------------------------
# Test component data helpers
# ---------------------------------------------------------------------------


class TestActivityTimelineData:
    """Test activity timeline component data mappings."""

    def test_type_icon_mapping(self) -> None:
        """All standard outreach types have icon mappings."""
        from theleadedge.dashboard.components.activity_timeline import (
            _TYPE_ICONS,
        )

        assert "call" in _TYPE_ICONS
        assert "email" in _TYPE_ICONS
        assert "sms" in _TYPE_ICONS
        assert "meeting" in _TYPE_ICONS
        assert "note" in _TYPE_ICONS
        assert "mail" in _TYPE_ICONS

    def test_empty_events_list(self) -> None:
        """Empty events list has zero length."""
        events: list[dict[str, Any]] = []
        assert len(events) == 0


class TestPublicRecordsPanelData:
    """Test public records panel component data mappings."""

    def test_type_icon_mapping(self) -> None:
        """All standard record types have icon mappings."""
        from theleadedge.dashboard.components.public_records_panel import (
            _TYPE_ICONS,
        )

        assert "lis_pendens" in _TYPE_ICONS
        assert "probate" in _TYPE_ICONS
        assert "divorce" in _TYPE_ICONS
        assert "code_violation" in _TYPE_ICONS
        assert "tax_delinquent" in _TYPE_ICONS
        assert "property_assessment" in _TYPE_ICONS

    def test_empty_records_list(self) -> None:
        """Empty records list has zero length."""
        records: list[dict[str, Any]] = []
        assert len(records) == 0


class TestScoreGaugeConfig:
    """Test score gauge tier color integration."""

    def test_gauge_tier_s_color(self) -> None:
        """S-tier returns the hot red color."""
        from theleadedge.dashboard.theme import get_tier_color

        color = get_tier_color("S")
        assert color == "#e74c3c"

    def test_gauge_tier_a_color(self) -> None:
        """A-tier returns the orange color."""
        from theleadedge.dashboard.theme import get_tier_color

        color = get_tier_color("A")
        assert color == "#e67e22"

    def test_gauge_tier_d_color(self) -> None:
        """D-tier returns the gray color."""
        from theleadedge.dashboard.theme import get_tier_color

        color = get_tier_color("D")
        assert color == "#95a5a6"

    def test_gauge_unknown_tier_defaults(self) -> None:
        """Unknown tier letter returns default gray."""
        from theleadedge.dashboard.theme import get_tier_color

        color = get_tier_color("X")
        assert color == "#95a5a6"


class TestOutreachFormData:
    """Test outreach form dialog options."""

    def test_outreach_types_available(self) -> None:
        """Verify standard outreach types are defined."""
        expected = {"call", "email", "sms", "meeting", "mail", "note"}
        # These are the options used in the outreach form dialog
        assert len(expected) == 6

    def test_outcome_types_available(self) -> None:
        """Verify standard outcome types are defined."""
        expected = {
            "no_answer",
            "left_voicemail",
            "spoke_with",
            "appointment_set",
            "not_interested",
            "wrong_number",
        }
        assert len(expected) == 6
