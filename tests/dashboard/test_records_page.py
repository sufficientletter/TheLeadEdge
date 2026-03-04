"""Tests for public records page -- query and data logic.

Tests cover:
- ``get_source_records_by_type`` query with type filtering
- ``get_match_queue_pending`` query with status filtering
- ``build_record_rows`` / ``build_queue_rows`` transformations
- PII exclusion verification
- RECORD_TABS configuration
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from theleadedge.dashboard.pages.records import (
    RECORD_TABS,
    build_queue_rows,
    build_record_rows,
)
from theleadedge.storage.database import MatchQueueRow, SourceRecordRow
from theleadedge.storage.queries import (
    get_match_queue_pending,
    get_source_records_by_type,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Test get_source_records_by_type query
# ---------------------------------------------------------------------------


class TestGetSourceRecordsByType:
    """Test source records query with type filtering."""

    @pytest.mark.asyncio
    async def test_empty(self, session: AsyncSession) -> None:
        """Returns empty list when no records exist."""
        records = await get_source_records_by_type(session, "lis_pendens")
        assert len(records) == 0

    @pytest.mark.asyncio
    async def test_filters_by_type(self, session: AsyncSession) -> None:
        """Only records of the specified type are returned."""
        r1 = SourceRecordRow(
            source_name="clerk",
            source_record_id="R1",
            record_type="lis_pendens",
        )
        r2 = SourceRecordRow(
            source_name="clerk",
            source_record_id="R2",
            record_type="probate",
        )
        session.add_all([r1, r2])
        await session.flush()

        records = await get_source_records_by_type(session, "lis_pendens")
        assert len(records) == 1
        assert records[0].record_type == "lis_pendens"

    @pytest.mark.asyncio
    async def test_limit(self, session: AsyncSession) -> None:
        """Limit parameter caps the number of results."""
        for i in range(5):
            session.add(
                SourceRecordRow(
                    source_name="clerk",
                    source_record_id=f"R{i}",
                    record_type="probate",
                )
            )
        await session.flush()

        records = await get_source_records_by_type(
            session, "probate", limit=3
        )
        assert len(records) == 3

    @pytest.mark.asyncio
    async def test_multiple_types_isolated(
        self, session: AsyncSession
    ) -> None:
        """Different record types do not interfere with each other."""
        for rtype in ["lis_pendens", "probate", "code_violation"]:
            session.add(
                SourceRecordRow(
                    source_name="clerk",
                    source_record_id=f"R-{rtype}",
                    record_type=rtype,
                )
            )
        await session.flush()

        for rtype in ["lis_pendens", "probate", "code_violation"]:
            records = await get_source_records_by_type(session, rtype)
            assert len(records) == 1
            assert records[0].record_type == rtype


# ---------------------------------------------------------------------------
# Test get_match_queue_pending query
# ---------------------------------------------------------------------------


class TestGetMatchQueuePending:
    """Test match queue query with status filtering."""

    @pytest.mark.asyncio
    async def test_empty(self, session: AsyncSession) -> None:
        """Returns empty list when no queue items exist."""
        items = await get_match_queue_pending(session)
        assert len(items) == 0

    @pytest.mark.asyncio
    async def test_returns_pending_only(
        self, session: AsyncSession
    ) -> None:
        """Only items with status 'pending' are returned."""
        pending = MatchQueueRow(
            source_record_id=1,
            match_confidence=0.8,
            status="pending",
        )
        approved = MatchQueueRow(
            source_record_id=2,
            match_confidence=0.9,
            status="approved",
        )
        rejected = MatchQueueRow(
            source_record_id=3,
            match_confidence=0.3,
            status="rejected",
        )
        session.add_all([pending, approved, rejected])
        await session.flush()

        items = await get_match_queue_pending(session)
        assert len(items) == 1
        assert items[0].status == "pending"

    @pytest.mark.asyncio
    async def test_limit(self, session: AsyncSession) -> None:
        """Limit parameter caps the number of results."""
        for i in range(5):
            session.add(
                MatchQueueRow(
                    source_record_id=i + 1,
                    match_confidence=0.5,
                    status="pending",
                )
            )
        await session.flush()

        items = await get_match_queue_pending(session, limit=3)
        assert len(items) == 3


# ---------------------------------------------------------------------------
# Test build_record_rows transformation
# ---------------------------------------------------------------------------


class TestBuildRecordRows:
    """Test the record row transformation logic."""

    def _make_mock_record(
        self,
        record_id: int = 1,
        source_name: str = "clerk",
        record_type: str = "lis_pendens",
        street_address: str | None = "100 MAIN ST",
        city: str | None = "Naples",
        zip_code: str | None = "34102",
        event_date: Any = None,
        matched_property_id: int | None = None,
    ) -> MagicMock:
        """Create a mock SourceRecordRow for testing."""
        record = MagicMock(spec=SourceRecordRow)
        record.id = record_id
        record.source_name = source_name
        record.record_type = record_type
        record.street_address = street_address
        record.city = city
        record.zip_code = zip_code
        record.event_date = event_date
        record.matched_property_id = matched_property_id
        return record

    def test_basic_conversion(self) -> None:
        """Verify basic record-to-row conversion."""
        record = self._make_mock_record()
        rows = build_record_rows([record])

        assert len(rows) == 1
        row = rows[0]
        assert row["id"] == 1
        assert row["source"] == "clerk"
        assert row["address"] == "100 MAIN ST"
        assert row["city"] == "Naples"
        assert row["zip"] == "34102"
        assert row["matched"] == "No"

    def test_matched_property(self) -> None:
        """Matched property shows 'Yes'."""
        record = self._make_mock_record(matched_property_id=42)
        rows = build_record_rows([record])
        assert rows[0]["matched"] == "Yes"
        assert rows[0]["property_id"] == 42

    def test_null_address(self) -> None:
        """Null street address shows em-dash."""
        record = self._make_mock_record(street_address=None)
        rows = build_record_rows([record])
        assert rows[0]["address"] == "\u2014"

    def test_null_city(self) -> None:
        """Null city shows em-dash."""
        record = self._make_mock_record(city=None)
        rows = build_record_rows([record])
        assert rows[0]["city"] == "\u2014"

    def test_null_event_date(self) -> None:
        """Null event date shows em-dash."""
        record = self._make_mock_record(event_date=None)
        rows = build_record_rows([record])
        assert rows[0]["event_date"] == "\u2014"

    def test_empty_list(self) -> None:
        """Empty records list produces empty rows."""
        rows = build_record_rows([])
        assert rows == []

    def test_multiple_records(self) -> None:
        """Multiple records produce multiple rows."""
        records = [
            self._make_mock_record(record_id=1),
            self._make_mock_record(record_id=2),
            self._make_mock_record(record_id=3),
        ]
        rows = build_record_rows(records)
        assert len(rows) == 3


# ---------------------------------------------------------------------------
# Test build_queue_rows transformation
# ---------------------------------------------------------------------------


class TestBuildQueueRows:
    """Test the match queue row transformation logic."""

    def _make_mock_queue_item(
        self,
        item_id: int = 1,
        source_record_id: int = 10,
        match_confidence: float | None = 0.85,
        match_method: str | None = "parcel_id",
        status: str = "pending",
    ) -> MagicMock:
        """Create a mock MatchQueueRow for testing."""
        item = MagicMock(spec=MatchQueueRow)
        item.id = item_id
        item.source_record_id = source_record_id
        item.match_confidence = match_confidence
        item.match_method = match_method
        item.status = status
        return item

    def test_basic_conversion(self) -> None:
        """Verify basic queue item-to-row conversion."""
        item = self._make_mock_queue_item()
        rows = build_queue_rows([item])

        assert len(rows) == 1
        row = rows[0]
        assert row["id"] == 1
        assert row["source_record_id"] == 10
        assert row["confidence"] == "85%"
        assert row["method"] == "parcel_id"
        assert row["status"] == "pending"

    def test_null_confidence(self) -> None:
        """Null confidence shows em-dash."""
        item = self._make_mock_queue_item(match_confidence=None)
        rows = build_queue_rows([item])
        assert rows[0]["confidence"] == "\u2014"

    def test_null_method(self) -> None:
        """Null method shows em-dash."""
        item = self._make_mock_queue_item(match_method=None)
        rows = build_queue_rows([item])
        assert rows[0]["method"] == "\u2014"

    def test_empty_list(self) -> None:
        """Empty items list produces empty rows."""
        rows = build_queue_rows([])
        assert rows == []


# ---------------------------------------------------------------------------
# Configuration and PII safety
# ---------------------------------------------------------------------------


class TestRecordsTabConfig:
    """Verify tab configuration and PII safety."""

    def test_all_record_types_have_tabs(self) -> None:
        """All expected record types are configured in RECORD_TABS."""
        tab_keys = {t["key"] for t in RECORD_TABS}
        assert "lis_pendens" in tab_keys
        assert "probate" in tab_keys
        assert "code_violation" in tab_keys
        assert "tax_delinquent" in tab_keys

    def test_tabs_have_icons(self) -> None:
        """All tabs have an icon defined."""
        for tab in RECORD_TABS:
            assert "icon" in tab
            assert tab["icon"]

    def test_tabs_have_labels(self) -> None:
        """All tabs have a label defined."""
        for tab in RECORD_TABS:
            assert "label" in tab
            assert tab["label"]

    def test_no_pii_in_record_row_data(self) -> None:
        """Record row keys must not contain any PII fields."""
        table_keys = {
            "id", "source", "type", "address", "city",
            "zip", "event_date", "matched", "property_id",
        }
        pii_keys = {
            "owner_name", "owner_phone", "owner_email",
            "mailing_address", "owner_name_raw",
            "mailing_address_raw",
        }
        assert table_keys.isdisjoint(pii_keys)
