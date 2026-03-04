"""Unit tests for Phase 2 repositories and PropertyRepo extensions.

Tests the 4 new repositories (SourceRecordRepo, MatchQueueRepo,
MarketSnapshotRepo, FSBOListingRepo) and the new parcel-based methods
on PropertyRepo.

All tests use the async session fixture from conftest.py with per-test
rollback for isolation.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from theleadedge.storage.repositories import (
    FSBOListingRepo,
    MarketSnapshotRepo,
    MatchQueueRepo,
    PropertyRepo,
    SourceRecordRepo,
)

# ---------------------------------------------------------------------------
# SourceRecordRepo
# ---------------------------------------------------------------------------


class TestSourceRecordRepo:
    """Tests for SourceRecordRepo CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve(self, session) -> None:
        """Create a source record and retrieve it by source + id."""
        repo = SourceRecordRepo(session)

        row = await repo.create(
            source_name="collier_pa",
            source_record_id="PA-001",
            record_type="property_assessment",
            parcel_id="00123456789",
            street_address="100 SYNTHETIC DR",
            city="Naples",
            state="FL",
            zip_code="34102",
        )
        assert row.id is not None
        assert row.source_name == "collier_pa"
        assert row.source_record_id == "PA-001"

        fetched = await repo.get_by_source_and_id("collier_pa", "PA-001")
        assert fetched is not None
        assert fetched.id == row.id
        assert fetched.parcel_id == "00123456789"

    @pytest.mark.asyncio
    async def test_get_unmatched(self, session) -> None:
        """get_unmatched returns only records without a matched_property_id."""
        repo = SourceRecordRepo(session)

        # Create one matched and one unmatched
        await repo.create(
            source_name="lee_clerk",
            source_record_id="LP-001",
            record_type="lis_pendens",
            matched_property_id=None,
        )
        await repo.create(
            source_name="lee_clerk",
            source_record_id="LP-002",
            record_type="lis_pendens",
            matched_property_id=99,  # matched
        )

        unmatched = await repo.get_unmatched()
        assert len(unmatched) == 1
        assert unmatched[0].source_record_id == "LP-001"

    @pytest.mark.asyncio
    async def test_dedup_by_source_and_id(self, session) -> None:
        """get_by_source_and_id returns None for non-existent records."""
        repo = SourceRecordRepo(session)

        result = await repo.get_by_source_and_id("nonexistent", "FAKE-001")
        assert result is None

        # Create a record, then verify we can find it but not a different one
        await repo.create(
            source_name="collier_pa",
            source_record_id="PA-100",
            record_type="property_assessment",
        )
        found = await repo.get_by_source_and_id("collier_pa", "PA-100")
        assert found is not None

        not_found = await repo.get_by_source_and_id("collier_pa", "PA-999")
        assert not_found is None


# ---------------------------------------------------------------------------
# MatchQueueRepo
# ---------------------------------------------------------------------------


class TestMatchQueueRepo:
    """Tests for MatchQueueRepo CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_get_pending(self, session) -> None:
        """Create queue entries and retrieve pending ones."""
        # Need a source record first for the FK
        sr_repo = SourceRecordRepo(session)
        sr = await sr_repo.create(
            source_name="test",
            source_record_id="T-001",
            record_type="test",
        )

        repo = MatchQueueRepo(session)

        entry = await repo.create(
            source_record_id=sr.id,
            match_confidence=0.75,
            match_method="address_key",
            status="pending",
        )
        assert entry.id is not None
        assert entry.status == "pending"

        pending = await repo.get_pending()
        assert len(pending) >= 1
        assert any(e.id == entry.id for e in pending)

    @pytest.mark.asyncio
    async def test_update_status(self, session) -> None:
        """update_status changes status and sets reviewed_at."""
        sr_repo = SourceRecordRepo(session)
        sr = await sr_repo.create(
            source_name="test",
            source_record_id="T-002",
            record_type="test",
        )

        repo = MatchQueueRepo(session)
        entry = await repo.create(
            source_record_id=sr.id,
            match_confidence=0.50,
            status="pending",
        )

        review_time = datetime(2026, 3, 3, 12, 0, 0)
        await repo.update_status(entry.id, "approved", reviewed_at=review_time)

        # Verify it no longer appears in pending
        pending = await repo.get_pending()
        pending_ids = [e.id for e in pending]
        assert entry.id not in pending_ids


# ---------------------------------------------------------------------------
# MarketSnapshotRepo
# ---------------------------------------------------------------------------


class TestMarketSnapshotRepo:
    """Tests for MarketSnapshotRepo CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_get_latest(self, session) -> None:
        """Create snapshots and retrieve the latest by ZIP."""
        repo = MarketSnapshotRepo(session)

        # Insert two snapshots for the same ZIP with different period_end dates
        await repo.create(
            zip_code="34102",
            source="redfin",
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 31),
            median_sale_price=450000.0,
            median_dom=45,
        )
        newer = await repo.create(
            zip_code="34102",
            source="redfin",
            period_start=datetime(2026, 2, 1),
            period_end=datetime(2026, 2, 28),
            median_sale_price=465000.0,
            median_dom=42,
        )

        latest = await repo.get_latest_by_zip("34102")
        assert latest is not None
        assert latest.id == newer.id
        assert latest.median_sale_price == 465000.0

    @pytest.mark.asyncio
    async def test_get_latest_by_zip_returns_none(self, session) -> None:
        """get_latest_by_zip returns None when no data exists."""
        repo = MarketSnapshotRepo(session)
        result = await repo.get_latest_by_zip("99999")
        assert result is None


# ---------------------------------------------------------------------------
# FSBOListingRepo
# ---------------------------------------------------------------------------


class TestFSBOListingRepo:
    """Tests for FSBOListingRepo CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_get_by_url(self, session) -> None:
        """Create an FSBO listing and retrieve by source URL."""
        repo = FSBOListingRepo(session)

        row = await repo.create(
            source="craigslist",
            source_url="https://fortmyers.craigslist.org/reb/d/test/12345.html",
            title="3BR House in Cape Coral",
            street_address="200 SYNTHETIC LN",
            city="Cape Coral",
            state="FL",
            zip_code="33904",
            asking_price=299000.0,
        )
        assert row.id is not None

        fetched = await repo.get_by_source_url(
            "https://fortmyers.craigslist.org/reb/d/test/12345.html"
        )
        assert fetched is not None
        assert fetched.id == row.id
        assert fetched.asking_price == 299000.0

    @pytest.mark.asyncio
    async def test_get_recent(self, session) -> None:
        """get_recent returns listings ordered by created_at desc."""
        repo = FSBOListingRepo(session)

        for i in range(3):
            await repo.create(
                source="zillow",
                source_url=f"https://zillow.com/fsbo/{i}",
                title=f"FSBO listing {i}",
                city="Naples",
                state="FL",
                zip_code="34102",
            )

        recent = await repo.get_recent(limit=2)
        assert len(recent) == 2


# ---------------------------------------------------------------------------
# PropertyRepo parcel_id methods
# ---------------------------------------------------------------------------


class TestPropertyRepoParcelMethods:
    """Tests for PropertyRepo.get_by_parcel_id and upsert_by_parcel_id."""

    @pytest.mark.asyncio
    async def test_parcel_id_methods(self, session) -> None:
        """get_by_parcel_id and upsert_by_parcel_id work correctly."""
        repo = PropertyRepo(session)

        # Initially no property with this parcel
        result = await repo.get_by_parcel_id("99-88-77-001")
        assert result is None

        # upsert creates a new row
        row, is_new = await repo.upsert_by_parcel_id(
            "99-88-77-001",
            address="500 SYNTHETIC BLVD",
            city="Naples",
            state="FL",
            zip_code="34102",
            assessed_value=350000.0,
        )
        assert is_new is True
        assert row.parcel_id == "99-88-77-001"
        assert row.assessed_value == 350000.0

        # Now get_by_parcel_id finds it
        found = await repo.get_by_parcel_id("99-88-77-001")
        assert found is not None
        assert found.id == row.id

        # upsert again updates the existing row
        updated, is_new_2 = await repo.upsert_by_parcel_id(
            "99-88-77-001",
            assessed_value=375000.0,
        )
        assert is_new_2 is False
        assert updated.id == row.id
        assert updated.assessed_value == 375000.0
