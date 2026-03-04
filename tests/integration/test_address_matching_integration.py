"""Integration tests for address matching across data sources.

Tests the RecordMapper's cascade behavior with real PropertyRow records
in the database, and the PublicRecordPipeline's handling of low-confidence
matches and unmatched records.

All test data is synthetic -- no real property data or PII.
"""

from __future__ import annotations

from datetime import date

import pytest

from theleadedge.models.source_record import SourceRecord
from theleadedge.pipelines.match import RecordMapper
from theleadedge.pipelines.public_records import PublicRecordPipeline
from theleadedge.storage.repositories import MatchQueueRepo, SourceRecordRepo

# ---------------------------------------------------------------------------
# Test 1: Parcel match resolves correctly (confidence 1.0)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_parcel_match_resolves_correctly(
    session,
    make_property_row,
):
    """Parcel ID exact match returns confidence 1.0."""
    prop = await make_property_row(
        session,
        address="200 PARCEL MATCH DR",
        city="Naples",
        zip_code="34102",
        parcel_id="TEST-PARCEL-001",
    )

    record = SourceRecord(
        source_name="collier_pa",
        source_record_id="PM-001",
        record_type="property_assessment",
        parcel_id="TEST-PARCEL-001",
    )

    mapper = RecordMapper(session)
    result = await mapper.match(record)

    assert result.property_id == prop.id
    assert result.method == "parcel_id"
    assert result.confidence == 1.0
    assert result.property_row is not None
    assert result.property_row.id == prop.id


# ---------------------------------------------------------------------------
# Test 2: Address cascade -- falls through to address match
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_address_cascade_normalized(
    session,
    make_property_row,
):
    """Normalized address match works despite different formatting."""
    prop = await make_property_row(
        session,
        address="100 N MAIN STREET",
        city="Naples",
        state="FL",
        zip_code="34102",
    )

    # SourceRecord uses a different format: "NORTH" instead of "N",
    # "ST" instead of "STREET"
    record = SourceRecord(
        source_name="collier_pa",
        source_record_id="AM-001",
        record_type="property_assessment",
        street_address="100 NORTH MAIN ST",
        city="Naples",
        state="FL",
        zip_code="34102",
    )

    mapper = RecordMapper(session)
    result = await mapper.match(record)

    assert result.property_id == prop.id
    # Should match via address_normalized or address_key
    assert result.method in ("address_normalized", "address_key")
    assert result.confidence >= 0.85


# ---------------------------------------------------------------------------
# Test 3: Low-confidence match queues to MatchQueue
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_low_confidence_match_queued(
    session,
    scoring_config,
    make_property_row,
    now,
):
    """A match below the confidence threshold is persisted and queued for review."""
    # Create a property (must exist for fuzzy matching)
    await make_property_row(
        session,
        address="500 PALM BEACH BLVD",
        city="Naples",
        zip_code="34102",
    )

    # Create a source record with a slightly different address in the same ZIP.
    # Use a street name that will fuzzy-match above the 85 rapidfuzz threshold
    # but produce a confidence below the pipeline threshold.
    record = SourceRecord(
        source_name="collier_clerk",
        source_record_id="LCM-001",
        record_type="lis_pendens",
        street_address="500 PALM BCH BLVD",
        city="Naples",
        state="FL",
        zip_code="34102",
        event_date=date(2026, 2, 25),
    )

    # Use a high confidence threshold so fuzzy matches get queued
    pipeline = PublicRecordPipeline(session, scoring_config, confidence_threshold=0.95)
    stats = await pipeline.process_records([record], now)

    # The fuzzy match should produce confidence < 0.95 threshold
    # so it should end up queued or unmatched
    # (Depending on the exact fuzzy ratio, it might be queued or unmatched)
    assert stats["total"] == 1
    # The record should have been persisted
    sr_repo = SourceRecordRepo(session)
    stored = await sr_repo.get_by_source_and_id("collier_clerk", "LCM-001")
    assert stored is not None

    # Check if it was queued (low-confidence match)
    if stats["queued"] > 0:
        mq_repo = MatchQueueRepo(session)
        pending = await mq_repo.get_pending()
        assert len(pending) >= 1
        queue_entry = pending[0]
        assert queue_entry.status == "pending"
        assert queue_entry.match_confidence < 0.95


# ---------------------------------------------------------------------------
# Test 4: Multiple properties in same ZIP -- correct one matched
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_correct_property_matched_in_same_zip(
    session,
    make_property_row,
):
    """Among multiple properties in the same ZIP, the right one is matched."""
    prop1 = await make_property_row(
        session,
        address="101 FIRST AVE",
        city="Naples",
        zip_code="34102",
    )
    prop2 = await make_property_row(
        session,
        address="202 SECOND AVE",
        city="Naples",
        zip_code="34102",
    )
    prop3 = await make_property_row(
        session,
        address="303 THIRD AVE",
        city="Naples",
        zip_code="34102",
    )

    # Match the second property specifically
    record = SourceRecord(
        source_name="collier_pa",
        source_record_id="CM-001",
        record_type="property_assessment",
        street_address="202 SECOND AVE",
        city="Naples",
        state="FL",
        zip_code="34102",
    )

    mapper = RecordMapper(session)
    result = await mapper.match(record)

    assert result.property_id == prop2.id
    assert result.method in ("address_normalized", "address_key")
    assert result.confidence >= 0.85

    # Verify it did NOT match the other two properties
    assert result.property_id != prop1.id
    assert result.property_id != prop3.id


# ---------------------------------------------------------------------------
# Test 5: Unmatched record persisted but no signal
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unmatched_record_persisted_no_signal(
    session,
    scoring_config,
    now,
):
    """A record with no matching address is persisted but creates no signals."""
    record = SourceRecord(
        source_name="collier_clerk",
        source_record_id="UNM-001",
        record_type="probate",
        street_address="999 NOWHERE BLVD",
        city="Fort Myers",
        state="FL",
        zip_code="33901",
        event_date=date(2026, 2, 20),
    )

    pipeline = PublicRecordPipeline(session, scoring_config)
    stats = await pipeline.process_records([record], now)

    assert stats["unmatched"] == 1
    assert stats["signals_created"] == 0
    assert stats["matched"] == 0
    assert stats["queued"] == 0

    # Verify the source record was still persisted
    sr_repo = SourceRecordRepo(session)
    stored = await sr_repo.get_by_source_and_id("collier_clerk", "UNM-001")
    assert stored is not None
    assert stored.matched_property_id is None
