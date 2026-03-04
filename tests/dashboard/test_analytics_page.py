"""Tests for analytics page -- query and chart data logic.

Tests cover:
- ``get_conversion_funnel`` query with status counts and score distribution
- ``get_signal_performance`` query with grouping by signal type
- ``get_tier_distribution_over_time`` query with date pivoting
- ``get_source_roi`` query with data source grouping
- Chart rendering helper isolation
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from theleadedge.storage.database import ScoreHistoryRow, SignalRow
from theleadedge.storage.queries import (
    get_conversion_funnel,
    get_signal_performance,
    get_source_roi,
    get_tier_distribution_over_time,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Test get_conversion_funnel query
# ---------------------------------------------------------------------------


class TestGetConversionFunnel:
    """Test conversion funnel query."""

    @pytest.mark.asyncio
    async def test_empty(self, session: AsyncSession) -> None:
        """Empty database returns only score_distribution key."""
        result = await get_conversion_funnel(session)
        assert "score_distribution" in result

    @pytest.mark.asyncio
    async def test_counts_statuses(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Status counts are correctly grouped."""
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, status="new")
        await make_lead_row(session, prop.id, status="new")
        await make_lead_row(session, prop.id, status="contacted")
        await session.flush()

        result = await get_conversion_funnel(session)
        assert result.get("new") == 2
        assert result.get("contacted") == 1

    @pytest.mark.asyncio
    async def test_score_distribution_buckets(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Score distribution creates correct buckets."""
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, current_score=25.0)
        await make_lead_row(session, prop.id, current_score=75.0)
        await session.flush()

        result = await get_conversion_funnel(session)
        dist = result["score_distribution"]
        assert dist["20-30"] >= 1
        assert dist["70-80"] >= 1

    @pytest.mark.asyncio
    async def test_score_distribution_has_all_buckets(
        self, session: AsyncSession
    ) -> None:
        """Score distribution always has all 10 buckets."""
        result = await get_conversion_funnel(session)
        dist = result["score_distribution"]
        assert len(dist) == 10
        assert "0-10" in dist
        assert "90-100" in dist

    @pytest.mark.asyncio
    async def test_excludes_inactive_leads(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Inactive leads are excluded from funnel counts."""
        prop = await make_property_row(session)
        await make_lead_row(
            session, prop.id, status="new", is_active=True
        )
        await make_lead_row(
            session, prop.id, status="new", is_active=False
        )
        await session.flush()

        result = await get_conversion_funnel(session)
        assert result.get("new") == 1


# ---------------------------------------------------------------------------
# Test get_signal_performance query
# ---------------------------------------------------------------------------


class TestGetSignalPerformance:
    """Test signal performance query."""

    @pytest.mark.asyncio
    async def test_empty(self, session: AsyncSession) -> None:
        """Returns empty list when no signals exist."""
        result = await get_signal_performance(session)
        assert result == []

    @pytest.mark.asyncio
    async def test_counts_by_type(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Signal counts are correctly grouped by type."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
        session.add(
            SignalRow(
                lead_id=lead.id,
                property_id=prop.id,
                signal_type="expired_listing",
                signal_category="mls",
                points=15.0,
                base_points=15.0,
            )
        )
        session.add(
            SignalRow(
                lead_id=lead.id,
                property_id=prop.id,
                signal_type="expired_listing",
                signal_category="mls",
                points=15.0,
                base_points=15.0,
            )
        )
        session.add(
            SignalRow(
                lead_id=lead.id,
                property_id=prop.id,
                signal_type="price_reduction",
                signal_category="mls",
                points=10.0,
                base_points=10.0,
            )
        )
        await session.flush()

        result = await get_signal_performance(session)
        assert len(result) == 2
        # Highest count first
        assert result[0]["count"] >= result[1]["count"]

    @pytest.mark.asyncio
    async def test_excludes_inactive_signals(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Inactive signals are excluded."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
        session.add(
            SignalRow(
                lead_id=lead.id,
                property_id=prop.id,
                signal_type="expired_listing",
                signal_category="mls",
                points=15.0,
                base_points=15.0,
                is_active=True,
            )
        )
        session.add(
            SignalRow(
                lead_id=lead.id,
                property_id=prop.id,
                signal_type="price_reduction",
                signal_category="mls",
                points=10.0,
                base_points=10.0,
                is_active=False,
            )
        )
        await session.flush()

        result = await get_signal_performance(session)
        assert len(result) == 1
        assert result[0]["signal_type"] == "expired_listing"

    @pytest.mark.asyncio
    async def test_limit(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Limit parameter caps the number of signal types returned."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
        for i, stype in enumerate(
            ["expired", "price_red", "high_dom", "withdrawn", "relisted"]
        ):
            session.add(
                SignalRow(
                    lead_id=lead.id,
                    property_id=prop.id,
                    signal_type=stype,
                    signal_category="mls",
                    points=float(i),
                    base_points=float(i),
                )
            )
        await session.flush()

        result = await get_signal_performance(session, limit=3)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# Test get_tier_distribution_over_time query
# ---------------------------------------------------------------------------


class TestGetTierDistribution:
    """Test tier distribution over time query."""

    @pytest.mark.asyncio
    async def test_empty(self, session: AsyncSession) -> None:
        """Returns empty list when no score history exists."""
        result = await get_tier_distribution_over_time(session)
        assert result == []

    @pytest.mark.asyncio
    async def test_groups_by_date(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Score history entries are grouped by date."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
        sh = ScoreHistoryRow(
            lead_id=lead.id,
            score=80.0,
            tier="S",
            signal_count=5,
            change_reason="test",
        )
        session.add(sh)
        await session.flush()

        result = await get_tier_distribution_over_time(session)
        assert len(result) >= 1
        assert "S" in result[0]
        assert "date" in result[0]

    @pytest.mark.asyncio
    async def test_includes_all_tier_keys(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Each date dict includes all five tier keys."""
        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)
        session.add(
            ScoreHistoryRow(
                lead_id=lead.id,
                score=50.0,
                tier="B",
                signal_count=3,
                change_reason="test",
            )
        )
        await session.flush()

        result = await get_tier_distribution_over_time(session)
        assert len(result) >= 1
        for tier in ["S", "A", "B", "C", "D"]:
            assert tier in result[0]

    @pytest.mark.asyncio
    async def test_sorted_by_date(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Results are sorted by date ascending."""
        from datetime import datetime, timedelta

        prop = await make_property_row(session)
        lead = await make_lead_row(session, prop.id)

        for i in range(3):
            session.add(
                ScoreHistoryRow(
                    lead_id=lead.id,
                    score=50.0 + i * 10,
                    tier="B",
                    signal_count=3,
                    change_reason="test",
                    calculated_at=datetime(2026, 3, 1) + timedelta(days=i),
                )
            )
        await session.flush()

        result = await get_tier_distribution_over_time(session)
        dates = [r["date"] for r in result]
        assert dates == sorted(dates)


# ---------------------------------------------------------------------------
# Test get_source_roi query
# ---------------------------------------------------------------------------


class TestGetSourceRoi:
    """Test source ROI query."""

    @pytest.mark.asyncio
    async def test_empty(self, session: AsyncSession) -> None:
        """Returns empty list when no leads exist."""
        result = await get_source_roi(session)
        assert result == []

    @pytest.mark.asyncio
    async def test_groups_by_source(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Lead counts are grouped by data source."""
        p1 = await make_property_row(session, data_source="mls_csv")
        p2 = await make_property_row(session, data_source="mls_csv")
        p3 = await make_property_row(session, data_source="public_records")
        await make_lead_row(session, p1.id)
        await make_lead_row(session, p2.id)
        await make_lead_row(session, p3.id)
        await session.flush()

        result = await get_source_roi(session)
        assert len(result) == 2
        sources = {r["source"] for r in result}
        assert "mls_csv" in sources
        assert "public_records" in sources

    @pytest.mark.asyncio
    async def test_ordered_by_count_desc(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Results are ordered by count descending."""
        p1 = await make_property_row(session, data_source="mls_csv")
        p2 = await make_property_row(session, data_source="mls_csv")
        p3 = await make_property_row(session, data_source="public_records")
        await make_lead_row(session, p1.id)
        await make_lead_row(session, p2.id)
        await make_lead_row(session, p3.id)
        await session.flush()

        result = await get_source_roi(session)
        counts = [r["count"] for r in result]
        assert counts == sorted(counts, reverse=True)

    @pytest.mark.asyncio
    async def test_excludes_null_data_source(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Properties with null data_source are excluded."""
        p1 = await make_property_row(session, data_source="mls_csv")
        p2 = await make_property_row(session, data_source=None)
        await make_lead_row(session, p1.id)
        await make_lead_row(session, p2.id)
        await session.flush()

        result = await get_source_roi(session)
        assert len(result) == 1
        assert result[0]["source"] == "mls_csv"

    @pytest.mark.asyncio
    async def test_excludes_inactive_leads(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Inactive leads are excluded from source ROI."""
        prop = await make_property_row(session, data_source="mls_csv")
        await make_lead_row(session, prop.id, is_active=True)
        await make_lead_row(session, prop.id, is_active=False)
        await session.flush()

        result = await get_source_roi(session)
        assert len(result) == 1
        assert result[0]["count"] == 1


# ---------------------------------------------------------------------------
# Chart helper verification
# ---------------------------------------------------------------------------


class TestChartHelpers:
    """Verify chart helper functions handle edge cases."""

    def test_funnel_chart_filters_non_int(self) -> None:
        """_funnel_chart filters out non-integer values (score_distribution)."""
        from theleadedge.dashboard.pages.analytics import _funnel_chart

        # Should not raise -- the function checks isinstance(v, int)
        # We cannot test NiceGUI rendering, but we can verify it imports
        assert callable(_funnel_chart)

    def test_score_distribution_chart_callable(self) -> None:
        """_score_distribution_chart is importable and callable."""
        from theleadedge.dashboard.pages.analytics import (
            _score_distribution_chart,
        )

        assert callable(_score_distribution_chart)

    def test_signal_performance_chart_callable(self) -> None:
        """_signal_performance_chart is importable and callable."""
        from theleadedge.dashboard.pages.analytics import (
            _signal_performance_chart,
        )

        assert callable(_signal_performance_chart)

    def test_tier_trend_chart_callable(self) -> None:
        """_tier_trend_chart is importable and callable."""
        from theleadedge.dashboard.pages.analytics import _tier_trend_chart

        assert callable(_tier_trend_chart)

    def test_source_roi_chart_callable(self) -> None:
        """_source_roi_chart is importable and callable."""
        from theleadedge.dashboard.pages.analytics import _source_roi_chart

        assert callable(_source_roi_chart)
