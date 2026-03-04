"""Tests for RecordMapper cascading address matching.

Validates the four-stage cascade (parcel ID, normalized address, address key,
fuzzy) and edge cases like missing fields, empty database, and unit-number
stripping.

All tests use the async session fixture from conftest.py with per-test
rollback for isolation.

IMPORTANT: All addresses in tests are synthetic -- never use real PII.
"""

from __future__ import annotations

import pytest

from theleadedge.models.source_record import SourceRecord
from theleadedge.pipelines.match import RecordMapper
from theleadedge.storage.database import PropertyRow
from theleadedge.utils.address import normalize_address


def _make_source_record(**overrides: object) -> SourceRecord:
    """Build a SourceRecord with sensible defaults and optional overrides."""
    defaults: dict[str, object] = {
        "source_name": "test_source",
        "source_record_id": "TST-001",
        "record_type": "test",
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
    address_normalized: str | None = None,
) -> PropertyRow:
    """Insert a PropertyRow into the test database and return it."""
    from sqlalchemy.ext.asyncio import AsyncSession

    assert isinstance(session, AsyncSession)

    if address_normalized is None:
        address_normalized = normalize_address(address, city, state, zip_code)

    row = PropertyRow(
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        parcel_id=parcel_id,
        address_normalized=address_normalized,
    )
    session.add(row)
    await session.flush()
    return row


class TestRecordMapperParcelId:
    """Tests for parcel ID exact matching (cascade step 1)."""

    @pytest.mark.asyncio
    async def test_match_by_parcel_id_exact(self, session) -> None:
        """Property with matching parcel_id returns confidence 1.0."""
        prop = await _insert_property(
            session, parcel_id="12-34-56-001"
        )

        record = _make_source_record(parcel_id="12-34-56-001")
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.property_id == prop.id
        assert result.method == "parcel_id"
        assert result.confidence == 1.0
        assert result.property_row is not None
        assert result.property_row.id == prop.id


class TestRecordMapperNormalizedAddress:
    """Tests for normalized address exact matching (cascade step 2)."""

    @pytest.mark.asyncio
    async def test_match_by_normalized_address(self, session) -> None:
        """Property with matching normalized address returns confidence 0.95."""
        prop = await _insert_property(
            session,
            address="200 PALM AVE",
            city="Naples",
            zip_code="34102",
        )

        record = _make_source_record(
            street_address="200 PALM AVE",
            city="Naples",
            zip_code="34102",
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.property_id == prop.id
        assert result.method == "address_normalized"
        assert result.confidence == 0.95


class TestRecordMapperAddressKey:
    """Tests for address key matching (cascade step 3)."""

    @pytest.mark.asyncio
    async def test_match_by_address_key(self, session) -> None:
        """Address key match returns confidence 0.85."""
        # Create property with a known address
        prop = await _insert_property(
            session,
            address="300 OAK DR",
            city="Naples",
            zip_code="34103",
        )

        # Source record has slightly different address form but same key
        record = _make_source_record(
            street_address="300 OAK DRIVE",
            city="Naples",
            zip_code="34103",
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.property_id == prop.id
        assert result.method in ("address_normalized", "address_key")
        assert result.confidence >= 0.85

    @pytest.mark.asyncio
    async def test_address_key_match_ignores_unit_numbers(
        self, session
    ) -> None:
        """Address key strips units: '100 MAIN ST APT 1' matches '100 MAIN ST'."""
        prop = await _insert_property(
            session,
            address="100 MAIN ST",
            city="Naples",
            zip_code="34102",
        )

        record = _make_source_record(
            street_address="100 MAIN ST APT 1",
            city="Naples",
            zip_code="34102",
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.property_id == prop.id
        assert result.method in ("address_key", "fuzzy")
        assert result.confidence >= 0.70


class TestRecordMapperFuzzy:
    """Tests for fuzzy address matching (cascade step 4)."""

    @pytest.mark.asyncio
    async def test_match_by_fuzzy(self, session) -> None:
        """Slightly different address in same ZIP produces fuzzy match >= 0.70."""
        prop = await _insert_property(
            session,
            address="450 COCONUT PALM DR",
            city="Naples",
            zip_code="34104",
        )

        # Slightly different -- "DRIVE" instead of "DR", same meaning
        record = _make_source_record(
            street_address="450 COCONUT PALM DRIVE",
            city="Naples",
            zip_code="34104",
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.property_id == prop.id
        # Could match via address_normalized or address_key or fuzzy
        assert result.confidence >= 0.70

    @pytest.mark.asyncio
    async def test_fuzzy_requires_exact_zip(self, session) -> None:
        """Different ZIP code prevents fuzzy match."""
        await _insert_property(
            session,
            address="500 ROYAL PALM BLVD",
            city="Naples",
            zip_code="34102",
        )

        record = _make_source_record(
            street_address="500 ROYAL PALM BLVD",
            city="Fort Myers",
            zip_code="33901",  # Different ZIP
            parcel_id=None,
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        # Should not match because ZIP is different
        assert result.method == "none"
        assert result.confidence == 0.0
        assert result.property_id is None

    @pytest.mark.asyncio
    async def test_fuzzy_rejects_low_ratio(self, session) -> None:
        """Very different address in same ZIP does not produce a match."""
        await _insert_property(
            session,
            address="600 COCONUT PALM DR",
            city="Naples",
            zip_code="34105",
        )

        record = _make_source_record(
            street_address="9999 TOTALLY DIFFERENT RD",
            city="Naples",
            zip_code="34105",
            parcel_id=None,
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.confidence < 0.60  # Should be very low or 0.0
        if result.method != "none":
            # If by some chance it matched, confidence must be below threshold
            assert result.confidence < 0.70


class TestRecordMapperCascade:
    """Tests for cascade ordering and edge cases."""

    @pytest.mark.asyncio
    async def test_cascade_prefers_parcel_over_address(self, session) -> None:
        """When both parcel_id and address match, parcel_id wins (1.0 > 0.95)."""
        prop = await _insert_property(
            session,
            address="700 PINE LN",
            city="Naples",
            zip_code="34102",
            parcel_id="77-88-99-001",
        )

        record = _make_source_record(
            street_address="700 PINE LN",
            city="Naples",
            zip_code="34102",
            parcel_id="77-88-99-001",
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.property_id == prop.id
        assert result.method == "parcel_id"
        assert result.confidence == 1.0

    @pytest.mark.asyncio
    async def test_match_with_none_parcel_skips_parcel_step(
        self, session
    ) -> None:
        """SourceRecord without parcel_id skips to address match."""
        prop = await _insert_property(
            session,
            address="800 MAPLE CT",
            city="Naples",
            zip_code="34102",
        )

        record = _make_source_record(
            street_address="800 MAPLE CT",
            city="Naples",
            zip_code="34102",
            parcel_id=None,
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.property_id == prop.id
        assert result.method != "parcel_id"
        assert result.confidence >= 0.85

    @pytest.mark.asyncio
    async def test_match_handles_missing_address_fields(
        self, session
    ) -> None:
        """SourceRecord with no street_address skips address steps gracefully."""
        record = _make_source_record(
            street_address=None,
            city=None,
            zip_code=None,
            parcel_id=None,
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.method == "none"
        assert result.confidence == 0.0
        assert result.property_id is None

    @pytest.mark.asyncio
    async def test_match_handles_empty_database(self, session) -> None:
        """Empty database returns no match for any record."""
        record = _make_source_record(
            street_address="999 NONEXISTENT DR",
            city="Naples",
            zip_code="34102",
            parcel_id="00-00-00-000",
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.method == "none"
        assert result.confidence == 0.0
        assert result.property_id is None

    @pytest.mark.asyncio
    async def test_no_match_returns_none(self, session) -> None:
        """SourceRecord with no matching property returns confidence 0.0."""
        await _insert_property(
            session,
            address="111 FIRST ST",
            city="Naples",
            zip_code="34102",
        )

        record = _make_source_record(
            street_address="222 SECOND AVE",
            city="Fort Myers",
            zip_code="33901",
            parcel_id=None,
        )
        mapper = RecordMapper(session)
        result = await mapper.match(record)

        assert result.property_id is None
        assert result.method == "none"
        assert result.confidence == 0.0
        assert result.property_row is None
