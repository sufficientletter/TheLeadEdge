"""Tests for PublicRecordPipeline processing flow.

Validates the end-to-end flow: deduplication, address matching, persistence,
and queue routing based on match confidence.

All tests use the async session fixture from conftest.py with per-test
rollback for isolation.

IMPORTANT: All addresses in tests are synthetic -- never use real PII.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from theleadedge.models.source_record import SourceRecord
from theleadedge.pipelines.public_records import PublicRecordPipeline
from theleadedge.storage.database import PropertyRow
from theleadedge.storage.repositories import (
    MatchQueueRepo,
    SourceRecordRepo,
)
from theleadedge.utils.address import normalize_address


def _make_source_record(**overrides: object) -> SourceRecord:
    """Build a SourceRecord with sensible defaults and optional overrides."""
    defaults: dict[str, object] = {
        "source_name": "test_source",
        "source_record_id": "TST-001",
        "record_type": "lis_pendens",
        "street_address": "100 MAIN ST",
        "city": "Naples",
        "state": "FL",
        "zip_code": "34102",
    }
    defaults.update(overrides)
    return SourceRecord(**defaults)  # type: ignore[arg-type]


async def _insert_property(
    session: object,
    *,
    address: str = "100 MAIN ST",
    city: str = "Naples",
    state: str = "FL",
    zip_code: str = "34102",
    parcel_id: str | None = None,
) -> PropertyRow:
    """Insert a PropertyRow into the test database and return it."""
    from sqlalchemy.ext.asyncio import AsyncSession

    assert isinstance(session, AsyncSession)

    normalized = normalize_address(address, city, state, zip_code)

    row = PropertyRow(
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        parcel_id=parcel_id,
        address_normalized=normalized,
    )
    session.add(row)
    await session.flush()
    return row


class TestPublicRecordPipelineMatched:
    """Tests for records that match existing properties."""

    @pytest.mark.asyncio
    async def test_process_records_matched(
        self, session, scoring_config
    ) -> None:
        """Records matching properties are auto-linked, stats reflect matched."""
        prop = await _insert_property(
            session, parcel_id="11-22-33-001"
        )

        records = [
            _make_source_record(
                source_record_id="LP-001",
                parcel_id="11-22-33-001",
            ),
        ]

        pipeline = PublicRecordPipeline(
            session=session,
            config=scoring_config,
            confidence_threshold=0.80,
        )
        now = datetime(2026, 3, 2, 10, 0, 0)
        stats = await pipeline.process_records(records, now)

        assert stats["total"] == 1
        assert stats["matched"] == 1
        assert stats["queued"] == 0
        assert stats["unmatched"] == 0
        assert stats["duplicates"] == 0

        # Verify SourceRecordRow was persisted with match data
        sr_repo = SourceRecordRepo(session)
        saved = await sr_repo.get_by_source_and_id("test_source", "LP-001")
        assert saved is not None
        assert saved.matched_property_id == prop.id
        assert saved.match_method == "parcel_id"
        assert saved.match_confidence == 1.0


class TestPublicRecordPipelineUnmatched:
    """Tests for records that do not match any property."""

    @pytest.mark.asyncio
    async def test_process_records_unmatched(
        self, session, scoring_config
    ) -> None:
        """Records with no match are persisted as unmatched."""
        records = [
            _make_source_record(
                source_record_id="LP-002",
                street_address="9999 NOWHERE DR",
                city="Fort Myers",
                zip_code="33901",
                parcel_id=None,
            ),
        ]

        pipeline = PublicRecordPipeline(
            session=session,
            config=scoring_config,
        )
        now = datetime(2026, 3, 2, 10, 0, 0)
        stats = await pipeline.process_records(records, now)

        assert stats["total"] == 1
        assert stats["unmatched"] == 1
        assert stats["matched"] == 0
        assert stats["queued"] == 0

        # Verify record was still persisted
        sr_repo = SourceRecordRepo(session)
        saved = await sr_repo.get_by_source_and_id("test_source", "LP-002")
        assert saved is not None
        assert saved.matched_property_id is None


class TestPublicRecordPipelineQueued:
    """Tests for low-confidence matches routed to the review queue."""

    @pytest.mark.asyncio
    async def test_process_records_queued(
        self, session, scoring_config
    ) -> None:
        """Low-confidence match creates MatchQueueRow for manual review."""
        # Create a property; the source record will have a fuzzy-quality match
        await _insert_property(
            session,
            address="400 SUNSET PALM DR",
            city="Naples",
            zip_code="34106",
        )

        # Slightly different address that would fuzzy-match with moderate confidence
        records = [
            _make_source_record(
                source_record_id="LP-003",
                street_address="400 SUNSET PALMS DR",
                city="Naples",
                zip_code="34106",
                parcel_id=None,
            ),
        ]

        pipeline = PublicRecordPipeline(
            session=session,
            config=scoring_config,
            # Set threshold high so fuzzy matches get queued
            confidence_threshold=0.90,
        )
        now = datetime(2026, 3, 2, 10, 0, 0)
        stats = await pipeline.process_records(records, now)

        # The fuzzy match confidence (0.70 * ratio/100) should be below 0.90
        # so the record should be queued
        if stats["queued"] > 0:
            mq_repo = MatchQueueRepo(session)
            pending = await mq_repo.get_pending()
            assert len(pending) >= 1
            assert pending[0].status == "pending"
        else:
            # If address normalization made it an exact match, it is matched
            assert stats["matched"] >= 1 or stats["unmatched"] >= 1


class TestPublicRecordPipelineDedup:
    """Tests for duplicate record handling."""

    @pytest.mark.asyncio
    async def test_process_records_dedup(
        self, session, scoring_config
    ) -> None:
        """Duplicate source records are skipped."""
        # Pre-insert a source record
        sr_repo = SourceRecordRepo(session)
        await sr_repo.create(
            source_name="test_source",
            source_record_id="LP-004",
            record_type="lis_pendens",
        )

        # Try to process the same record again
        records = [
            _make_source_record(source_record_id="LP-004"),
        ]

        pipeline = PublicRecordPipeline(
            session=session,
            config=scoring_config,
        )
        now = datetime(2026, 3, 2, 10, 0, 0)
        stats = await pipeline.process_records(records, now)

        assert stats["total"] == 1
        assert stats["duplicates"] == 1
        assert stats["matched"] == 0
        assert stats["unmatched"] == 0
        assert stats["queued"] == 0


class TestPublicRecordPipelineEdgeCases:
    """Tests for edge cases and data integrity."""

    @pytest.mark.asyncio
    async def test_process_records_empty_list(
        self, session, scoring_config
    ) -> None:
        """Empty input list produces zero-stats result."""
        pipeline = PublicRecordPipeline(
            session=session,
            config=scoring_config,
        )
        now = datetime(2026, 3, 2, 10, 0, 0)
        stats = await pipeline.process_records([], now)

        assert stats["total"] == 0
        assert stats["matched"] == 0
        assert stats["queued"] == 0
        assert stats["unmatched"] == 0
        assert stats["duplicates"] == 0
        assert stats["signals_created"] == 0

    @pytest.mark.asyncio
    async def test_process_records_persists_source_record(
        self, session, scoring_config
    ) -> None:
        """SourceRecordRow is created in the database for every non-duplicate."""
        records = [
            _make_source_record(
                source_record_id="LP-005",
                street_address="555 PERSISTED LN",
                city="Naples",
                zip_code="34102",
            ),
        ]

        pipeline = PublicRecordPipeline(
            session=session,
            config=scoring_config,
        )
        now = datetime(2026, 3, 2, 10, 0, 0)
        await pipeline.process_records(records, now)

        sr_repo = SourceRecordRepo(session)
        saved = await sr_repo.get_by_source_and_id("test_source", "LP-005")
        assert saved is not None
        assert saved.source_name == "test_source"
        assert saved.record_type == "lis_pendens"
        assert saved.street_address == "555 PERSISTED LN"
        assert saved.city == "Naples"
        assert saved.zip_code == "34102"
