"""Unit tests for the SourceRecord Pydantic model.

Validates construction, defaults, validation, and from_attributes mode.
"""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from tests.factories import SourceRecordFactory
from theleadedge.models.source_record import SourceRecord


class TestSourceRecordConstruction:
    """Tests for SourceRecord model construction and defaults."""

    def test_construction_with_defaults(self) -> None:
        """Minimal construction with only required fields."""
        record = SourceRecord(
            source_name="collier_pa",
            source_record_id="PAR-001",
            record_type="property_assessment",
        )
        assert record.source_name == "collier_pa"
        assert record.source_record_id == "PAR-001"
        assert record.record_type == "property_assessment"
        assert record.state == "FL"
        assert record.parcel_id is None
        assert record.street_address is None
        assert record.city is None
        assert record.zip_code is None
        assert record.event_date is None
        assert record.event_type is None
        assert record.owner_name is None
        assert record.mailing_address is None
        assert record.matched_property_id is None
        assert record.match_method is None
        assert record.match_confidence is None

    def test_construction_with_all_fields(self) -> None:
        """Construction with every field populated."""
        record = SourceRecord(
            source_name="lee_clerk",
            source_record_id="LP-2026-00123",
            record_type="lis_pendens",
            parcel_id="20-44-25-01-00001.0000",
            street_address="1234 PALM BEACH BLVD",
            city="Fort Myers",
            state="FL",
            zip_code="33916",
            event_date=date(2026, 2, 15),
            event_type="foreclosure_filing",
            raw_data={"case_number": "26-CA-001234", "filed_by": "BANK"},
            owner_name="SYNTHETIC OWNER",
            mailing_address="PO BOX 999 FORT MYERS FL 33901",
            matched_property_id=42,
            match_method="parcel_id",
            match_confidence=1.0,
        )
        assert record.source_name == "lee_clerk"
        assert record.parcel_id == "20-44-25-01-00001.0000"
        assert record.event_date == date(2026, 2, 15)
        assert record.event_type == "foreclosure_filing"
        assert record.raw_data["case_number"] == "26-CA-001234"
        assert record.matched_property_id == 42
        assert record.match_method == "parcel_id"
        assert record.match_confidence == 1.0

    def test_validation_rejects_empty_source_name(self) -> None:
        """source_name is a required str field -- missing raises ValidationError."""
        with pytest.raises(ValidationError):
            SourceRecord(
                source_record_id="X-001",
                record_type="tax_delinquent",
            )  # type: ignore[call-arg]

    def test_from_attributes(self) -> None:
        """Model can be constructed from an object with matching attributes."""

        class FakeRow:
            source_name = "collier_pa"
            source_record_id = "PA-999"
            record_type = "property_assessment"
            parcel_id = "12345"
            street_address = "100 TEST DR"
            city = "Naples"
            state = "FL"
            zip_code = "34102"
            event_date = None
            event_type = None
            raw_data = {}
            owner_name = None
            mailing_address = None
            matched_property_id = None
            match_method = None
            match_confidence = None

        record = SourceRecord.model_validate(FakeRow(), from_attributes=True)
        assert record.source_name == "collier_pa"
        assert record.parcel_id == "12345"

    def test_raw_data_default_empty_dict(self) -> None:
        """raw_data defaults to an empty dict, not None."""
        record = SourceRecord(
            source_name="test_source",
            source_record_id="T-001",
            record_type="test",
        )
        assert record.raw_data == {}
        assert isinstance(record.raw_data, dict)

    def test_matching_fields_initially_none(self) -> None:
        """Match fields start as None before RecordMapper runs."""
        record = SourceRecordFactory.build()
        assert record.matched_property_id is None
        assert record.match_method is None
        assert record.match_confidence is None
