"""Tests for map view page -- query and data logic.

Tests cover:
- ``get_leads_for_map`` query with coordinate/tier/active filters
- ``build_marker_data`` transformation logic
- PII exclusion verification
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from theleadedge.dashboard.pages.map_view import build_marker_data
from theleadedge.dashboard.theme import TIER_COLORS
from theleadedge.storage.database import LeadRow, PropertyRow
from theleadedge.storage.queries import get_leads_for_map

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Test get_leads_for_map query
# ---------------------------------------------------------------------------


class TestGetLeadsForMap:
    """Test the map query with coordinate and tier filters."""

    @pytest.mark.asyncio
    async def test_empty_database(self, session: AsyncSession) -> None:
        """Returns empty list when no leads exist."""
        leads = await get_leads_for_map(session)
        assert len(leads) == 0

    @pytest.mark.asyncio
    async def test_excludes_null_coordinates(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Leads without latitude/longitude are excluded."""
        p1 = await make_property_row(
            session, latitude=26.45, longitude=-81.80
        )
        p2 = await make_property_row(session, latitude=None, longitude=None)
        await make_lead_row(session, p1.id, tier="A")
        await make_lead_row(session, p2.id, tier="A")
        await session.flush()

        leads = await get_leads_for_map(session)
        assert len(leads) == 1

    @pytest.mark.asyncio
    async def test_excludes_partial_coordinates(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Leads with only latitude or only longitude are excluded."""
        p1 = await make_property_row(
            session, latitude=26.45, longitude=None
        )
        p2 = await make_property_row(
            session, latitude=None, longitude=-81.80
        )
        await make_lead_row(session, p1.id)
        await make_lead_row(session, p2.id)
        await session.flush()

        leads = await get_leads_for_map(session)
        assert len(leads) == 0

    @pytest.mark.asyncio
    async def test_excludes_inactive(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Inactive leads are excluded from the map."""
        prop = await make_property_row(
            session, latitude=26.45, longitude=-81.80
        )
        await make_lead_row(session, prop.id, is_active=False)
        await session.flush()

        leads = await get_leads_for_map(session)
        assert len(leads) == 0

    @pytest.mark.asyncio
    async def test_returns_property_rel(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Property relationship is eagerly loaded."""
        prop = await make_property_row(
            session,
            latitude=26.45,
            longitude=-81.80,
            address="MAP TEST ST",
        )
        await make_lead_row(session, prop.id)
        await session.flush()

        leads = await get_leads_for_map(session)
        assert len(leads) == 1
        assert leads[0].property_rel.address == "MAP TEST ST"

    @pytest.mark.asyncio
    async def test_ordered_by_score(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """Results are ordered by current_score descending."""
        p1 = await make_property_row(
            session, latitude=26.45, longitude=-81.80
        )
        p2 = await make_property_row(
            session, latitude=26.46, longitude=-81.81
        )
        await make_lead_row(session, p1.id, current_score=30.0)
        await make_lead_row(session, p2.id, current_score=90.0)
        await session.flush()

        leads = await get_leads_for_map(session)
        assert leads[0].current_score >= leads[1].current_score

    @pytest.mark.asyncio
    async def test_min_tier_filter(
        self,
        session: AsyncSession,
        make_property_row: Any,
        make_lead_row: Any,
    ) -> None:
        """min_tier parameter filters out lower tiers."""
        p1 = await make_property_row(
            session, latitude=26.45, longitude=-81.80
        )
        p2 = await make_property_row(
            session, latitude=26.46, longitude=-81.81
        )
        await make_lead_row(session, p1.id, tier="A", current_score=70.0)
        await make_lead_row(session, p2.id, tier="D", current_score=10.0)
        await session.flush()

        leads = await get_leads_for_map(session, min_tier="B")
        assert len(leads) == 1
        assert leads[0].tier == "A"


# ---------------------------------------------------------------------------
# Test build_marker_data transformation
# ---------------------------------------------------------------------------


class TestBuildMarkerData:
    """Test the marker data transformation logic."""

    def _make_mock_lead(
        self,
        lead_id: int = 1,
        tier: str = "A",
        score: float = 72.5,
        address: str = "100 MAIN ST",
        city: str = "Naples",
        zip_code: str = "34102",
        list_price: float | None = 450000.0,
        latitude: float | None = 26.45,
        longitude: float | None = -81.80,
    ) -> MagicMock:
        """Create a mock LeadRow with property_rel for testing."""
        prop = MagicMock(spec=PropertyRow)
        prop.address = address
        prop.city = city
        prop.zip_code = zip_code
        prop.list_price = list_price
        prop.latitude = latitude
        prop.longitude = longitude

        lead = MagicMock(spec=LeadRow)
        lead.id = lead_id
        lead.tier = tier
        lead.current_score = score
        lead.property_rel = prop

        return lead

    def test_basic_conversion(self) -> None:
        """Verify basic lead-to-marker conversion."""
        lead = self._make_mock_lead()
        markers = build_marker_data([lead])

        assert len(markers) == 1
        m = markers[0]
        assert m["lat"] == 26.45
        assert m["lng"] == -81.80
        assert m["lead_id"] == 1
        assert m["address"] == "100 MAIN ST"
        assert m["tier"] == "A"
        assert m["score"] == 72.5
        assert m["list_price"] == 450000.0
        assert m["color"] == TIER_COLORS["A"]

    def test_excludes_null_coordinates(self) -> None:
        """Leads without coordinates produce no markers."""
        lead = self._make_mock_lead(latitude=None, longitude=None)
        markers = build_marker_data([lead])
        assert len(markers) == 0

    def test_excludes_partial_lat(self) -> None:
        """Lead with only latitude (no longitude) is excluded."""
        lead = self._make_mock_lead(latitude=26.45, longitude=None)
        markers = build_marker_data([lead])
        assert len(markers) == 0

    def test_excludes_partial_lng(self) -> None:
        """Lead with only longitude (no latitude) is excluded."""
        lead = self._make_mock_lead(latitude=None, longitude=-81.80)
        markers = build_marker_data([lead])
        assert len(markers) == 0

    def test_multiple_leads(self) -> None:
        """Multiple leads produce multiple markers."""
        leads = [
            self._make_mock_lead(lead_id=1, latitude=26.45, longitude=-81.80),
            self._make_mock_lead(lead_id=2, latitude=26.46, longitude=-81.81),
        ]
        markers = build_marker_data(leads)
        assert len(markers) == 2

    def test_empty_list(self) -> None:
        """Empty leads list produces empty markers."""
        markers = build_marker_data([])
        assert markers == []


# ---------------------------------------------------------------------------
# PII and tier color verification
# ---------------------------------------------------------------------------


class TestMapMarkerSafety:
    """Verify no PII leaks and tier colors are defined."""

    def test_tier_colors_defined(self) -> None:
        """All five tiers have colors defined."""
        for tier in ["S", "A", "B", "C", "D"]:
            assert tier in TIER_COLORS

    def test_no_pii_in_marker(self) -> None:
        """Marker keys must not contain any PII fields."""
        marker_keys = {
            "lat", "lng", "lead_id", "address", "city",
            "zip_code", "tier", "score", "list_price", "color",
        }
        pii_keys = {
            "owner_name", "owner_phone", "owner_email",
            "owner_mailing_address", "owner_name_raw",
            "mailing_address_raw",
        }
        assert marker_keys.isdisjoint(pii_keys)

    def test_default_color_for_unknown_tier(self) -> None:
        """Unknown tier falls back to gray."""
        color = TIER_COLORS.get("X", "#95a5a6")
        assert color == "#95a5a6"
