"""Tests for the lead pipeline page -- query and data logic.

Tests cover:
- ``get_leads_for_grid`` query with various filter combinations
- ``build_grid_data`` transformation logic
- PII exclusion verification (grid data is client-side JSON)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from theleadedge.dashboard.pages.leads import build_grid_data
from theleadedge.storage.database import LeadRow, PropertyRow
from theleadedge.storage.queries import get_leads_for_grid

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Test get_leads_for_grid query
# ---------------------------------------------------------------------------


class TestGetLeadsForGrid:
    """Test the leads grid query with various filters."""

    @pytest.mark.asyncio
    async def test_empty_database(self, session: AsyncSession) -> None:
        """Returns empty list when no leads exist."""
        leads = await get_leads_for_grid(session)
        assert len(leads) == 0

    @pytest.mark.asyncio
    async def test_returns_active_leads_only(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Only active leads are returned; inactive leads are excluded."""
        prop = await make_property_row(session, list_price=300000.0)
        await make_lead_row(
            session, prop.id, is_active=True, tier="A", current_score=70.0
        )
        await make_lead_row(
            session, prop.id, is_active=False, tier="B", current_score=50.0
        )
        await session.flush()

        leads = await get_leads_for_grid(session)
        assert len(leads) == 1
        assert leads[0].tier == "A"

    @pytest.mark.asyncio
    async def test_filter_by_tier(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Tier filter returns only matching tiers."""
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, tier="S", current_score=90.0)
        await make_lead_row(session, prop.id, tier="A", current_score=70.0)
        await make_lead_row(session, prop.id, tier="D", current_score=10.0)
        await session.flush()

        leads = await get_leads_for_grid(session, tiers=["S", "A"])
        assert len(leads) == 2
        assert all(lead.tier in ("S", "A") for lead in leads)

    @pytest.mark.asyncio
    async def test_filter_by_status(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Status filter returns only matching statuses."""
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, status="new")
        await make_lead_row(session, prop.id, status="contacted")
        await make_lead_row(session, prop.id, status="closed")
        await session.flush()

        leads = await get_leads_for_grid(session, statuses=["new"])
        assert len(leads) == 1
        assert leads[0].status == "new"

    @pytest.mark.asyncio
    async def test_filter_by_zip_code(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """ZIP code filter returns only leads for the matching ZIP."""
        p1 = await make_property_row(session, zip_code="34102")
        p2 = await make_property_row(session, zip_code="33901")
        await make_lead_row(session, p1.id)
        await make_lead_row(session, p2.id)
        await session.flush()

        leads = await get_leads_for_grid(session, zip_code="34102")
        assert len(leads) == 1
        assert leads[0].property_rel.zip_code == "34102"

    @pytest.mark.asyncio
    async def test_filter_by_price_range(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Price range filter returns only leads within min/max bounds."""
        p1 = await make_property_row(session, list_price=200000.0)
        p2 = await make_property_row(session, list_price=500000.0)
        p3 = await make_property_row(session, list_price=800000.0)
        await make_lead_row(session, p1.id)
        await make_lead_row(session, p2.id)
        await make_lead_row(session, p3.id)
        await session.flush()

        leads = await get_leads_for_grid(
            session, min_price=300000.0, max_price=600000.0
        )
        assert len(leads) == 1
        assert leads[0].property_rel.list_price == 500000.0

    @pytest.mark.asyncio
    async def test_filter_min_price_only(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Min price filter without max returns all leads at or above min."""
        p1 = await make_property_row(session, list_price=100000.0)
        p2 = await make_property_row(session, list_price=500000.0)
        await make_lead_row(session, p1.id)
        await make_lead_row(session, p2.id)
        await session.flush()

        leads = await get_leads_for_grid(session, min_price=300000.0)
        assert len(leads) == 1
        assert leads[0].property_rel.list_price == 500000.0

    @pytest.mark.asyncio
    async def test_filter_max_price_only(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Max price filter without min returns all leads at or below max."""
        p1 = await make_property_row(session, list_price=100000.0)
        p2 = await make_property_row(session, list_price=500000.0)
        await make_lead_row(session, p1.id)
        await make_lead_row(session, p2.id)
        await session.flush()

        leads = await get_leads_for_grid(session, max_price=300000.0)
        assert len(leads) == 1
        assert leads[0].property_rel.list_price == 100000.0

    @pytest.mark.asyncio
    async def test_ordered_by_score_desc(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Results are ordered by current_score descending."""
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, current_score=30.0)
        await make_lead_row(session, prop.id, current_score=90.0)
        await make_lead_row(session, prop.id, current_score=60.0)
        await session.flush()

        leads = await get_leads_for_grid(session)
        scores = [lead.current_score for lead in leads]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_limit_parameter(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Limit parameter caps the number of results."""
        prop = await make_property_row(session)
        for i in range(10):
            await make_lead_row(session, prop.id, current_score=float(i))
        await session.flush()

        leads = await get_leads_for_grid(session, limit=5)
        assert len(leads) == 5

    @pytest.mark.asyncio
    async def test_has_property_rel_loaded(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Property relationship is eagerly loaded (no lazy-load needed)."""
        prop = await make_property_row(session, address="123 TEST ST")
        await make_lead_row(session, prop.id)
        await session.flush()

        leads = await get_leads_for_grid(session)
        assert len(leads) == 1
        assert leads[0].property_rel is not None
        assert leads[0].property_rel.address == "123 TEST ST"

    @pytest.mark.asyncio
    async def test_combined_filters(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Multiple filters applied together (ANDed)."""
        p1 = await make_property_row(
            session, zip_code="34102", list_price=400000.0
        )
        p2 = await make_property_row(
            session, zip_code="34102", list_price=200000.0
        )
        p3 = await make_property_row(
            session, zip_code="33901", list_price=400000.0
        )
        await make_lead_row(session, p1.id, tier="S", status="new")
        await make_lead_row(session, p2.id, tier="S", status="new")
        await make_lead_row(session, p3.id, tier="S", status="new")
        await session.flush()

        leads = await get_leads_for_grid(
            session,
            tiers=["S"],
            zip_code="34102",
            min_price=300000.0,
        )
        assert len(leads) == 1
        assert leads[0].property_rel.zip_code == "34102"
        assert leads[0].property_rel.list_price == 400000.0

    @pytest.mark.asyncio
    async def test_empty_tiers_list_returns_all(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Empty tiers list means no tier filter is applied."""
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, tier="D")
        await session.flush()

        leads = await get_leads_for_grid(session, tiers=[])
        assert len(leads) == 1

    @pytest.mark.asyncio
    async def test_empty_statuses_list_returns_all(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Empty statuses list means no status filter is applied."""
        prop = await make_property_row(session)
        await make_lead_row(session, prop.id, status="closed")
        await session.flush()

        leads = await get_leads_for_grid(session, statuses=[])
        assert len(leads) == 1

    @pytest.mark.asyncio
    async def test_no_matching_results(
        self, session: AsyncSession, make_property_row: Any, make_lead_row: Any
    ) -> None:
        """Returns empty list when filters match nothing."""
        prop = await make_property_row(session, zip_code="34102")
        await make_lead_row(session, prop.id)
        await session.flush()

        leads = await get_leads_for_grid(session, zip_code="99999")
        assert len(leads) == 0


# ---------------------------------------------------------------------------
# Test build_grid_data transformation
# ---------------------------------------------------------------------------


class TestBuildGridData:
    """Test the grid data transformation logic."""

    def _make_mock_lead(
        self,
        lead_id: int = 1,
        tier: str = "A",
        score: float = 72.5,
        signal_count: int = 3,
        status: str = "new",
        address: str = "100 MAIN ST",
        city: str = "Naples",
        zip_code: str = "34102",
        list_price: float | None = 450000.0,
        dom: int | None = 45,
        property_type: str | None = "Single Family",
        standard_status: str | None = "Active",
        detected_at: Any = None,
    ) -> MagicMock:
        """Create a mock LeadRow with property_rel for testing."""
        prop = MagicMock(spec=PropertyRow)
        prop.address = address
        prop.city = city
        prop.zip_code = zip_code
        prop.list_price = list_price
        prop.days_on_market = dom
        prop.property_type = property_type
        prop.standard_status = standard_status

        lead = MagicMock(spec=LeadRow)
        lead.id = lead_id
        lead.tier = tier
        lead.current_score = score
        lead.signal_count = signal_count
        lead.status = status
        lead.detected_at = detected_at
        lead.property_rel = prop

        return lead

    def test_basic_conversion(self) -> None:
        """Verify basic lead-to-grid-row conversion."""
        lead = self._make_mock_lead()
        rows = build_grid_data([lead])

        assert len(rows) == 1
        row = rows[0]
        assert row["id"] == 1
        assert row["tier"] == "A"
        assert row["score"] == 72.5
        assert row["address"] == "100 MAIN ST"
        assert row["city"] == "Naples"
        assert row["zip_code"] == "34102"
        assert row["signals"] == 3
        assert row["status"] == "new"

    def test_price_formatting(self) -> None:
        """List price is formatted as USD string."""
        lead = self._make_mock_lead(list_price=1234567.0)
        rows = build_grid_data([lead])
        assert rows[0]["list_price_display"] == "$1,234,567"

    def test_none_price(self) -> None:
        """None list price displays as N/A."""
        lead = self._make_mock_lead(list_price=None)
        rows = build_grid_data([lead])
        assert rows[0]["list_price_display"] == "N/A"

    def test_none_property_type_shows_dash(self) -> None:
        """None property_type displays as em-dash."""
        lead = self._make_mock_lead(property_type=None)
        rows = build_grid_data([lead])
        assert rows[0]["property_type"] == "\u2014"

    def test_none_standard_status_shows_dash(self) -> None:
        """None standard_status displays as em-dash."""
        lead = self._make_mock_lead(standard_status=None)
        rows = build_grid_data([lead])
        assert rows[0]["mls_status"] == "\u2014"

    def test_none_detected_at_shows_dash(self) -> None:
        """None detected_at displays as em-dash."""
        lead = self._make_mock_lead(detected_at=None)
        rows = build_grid_data([lead])
        assert rows[0]["detected"] == "\u2014"

    def test_detected_at_formatted(self) -> None:
        """Detected date is formatted with format_date."""
        from datetime import datetime

        dt = datetime(2026, 3, 4, 10, 0, 0)
        lead = self._make_mock_lead(detected_at=dt)
        rows = build_grid_data([lead])
        assert rows[0]["detected"] == "Mar 04, 2026"

    def test_score_rounded(self) -> None:
        """Score is rounded to one decimal place."""
        lead = self._make_mock_lead(score=72.456)
        rows = build_grid_data([lead])
        assert rows[0]["score"] == 72.5

    def test_no_pii_in_grid_data(self) -> None:
        """Verify PII fields are never included in grid row data."""
        pii_fields = {
            "owner_name",
            "owner_phone",
            "owner_email",
            "owner_mailing_address",
            "owner_name_raw",
            "mailing_address_raw",
        }
        lead = self._make_mock_lead()
        rows = build_grid_data([lead])

        for row in rows:
            present_pii = pii_fields.intersection(row.keys())
            assert len(present_pii) == 0, (
                f"PII fields found in grid data: {present_pii}"
            )

    def test_grid_row_expected_keys(self) -> None:
        """Verify grid rows contain exactly the expected keys."""
        expected_keys = {
            "id",
            "address",
            "city",
            "zip_code",
            "tier",
            "score",
            "signals",
            "list_price",
            "list_price_display",
            "dom",
            "property_type",
            "mls_status",
            "status",
            "detected",
        }
        lead = self._make_mock_lead()
        rows = build_grid_data([lead])
        assert set(rows[0].keys()) == expected_keys

    def test_multiple_leads(self) -> None:
        """Multiple leads produce multiple grid rows."""
        leads = [
            self._make_mock_lead(lead_id=1, tier="S", score=90.0),
            self._make_mock_lead(lead_id=2, tier="A", score=70.0),
            self._make_mock_lead(lead_id=3, tier="B", score=50.0),
        ]
        rows = build_grid_data(leads)
        assert len(rows) == 3
        assert [r["tier"] for r in rows] == ["S", "A", "B"]

    def test_empty_list(self) -> None:
        """Empty leads list produces empty grid data."""
        rows = build_grid_data([])
        assert rows == []

    def test_raw_list_price_preserved(self) -> None:
        """Raw numeric list_price is preserved for sorting."""
        lead = self._make_mock_lead(list_price=350000.0)
        rows = build_grid_data([lead])
        assert rows[0]["list_price"] == 350000.0

    def test_dom_preserved_as_int(self) -> None:
        """Days on market preserved as integer."""
        lead = self._make_mock_lead(dom=120)
        rows = build_grid_data([lead])
        assert rows[0]["dom"] == 120

    def test_dom_none(self) -> None:
        """None DOM is preserved as None."""
        lead = self._make_mock_lead(dom=None)
        rows = build_grid_data([lead])
        assert rows[0]["dom"] is None
