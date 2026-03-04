"""Unit tests for the Code Violation connector.

Tests cover file reading, active/closed status filtering, SourceRecord
transformation, violation_type in raw_data, missing parcel fallback, and
health checks.

All test data is synthetic -- no real PII.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest

from theleadedge.sources.code_violations import (
    CodeViolationConnector,
)

# ---------------------------------------------------------------------------
# Shared config fixture (simulates clerk_fields.yaml code_violation section)
# ---------------------------------------------------------------------------

SAMPLE_CONFIG: dict[str, Any] = {
    "code_violation": {
        "parcel_id": ["PARCEL_ID", "PARCEL", "FOLIO"],
        "street_address": ["ADDRESS", "PROPERTY_ADDRESS", "VIOLATION_ADDRESS"],
        "city": ["CITY", "VIOLATION_CITY"],
        "zip_code": ["ZIP", "ZIP_CODE"],
        "event_date": ["VIOLATION_DATE", "INSPECTION_DATE", "ISSUED_DATE"],
        "violation_type": ["VIOLATION_TYPE", "VIOLATION_CODE", "CODE_SECTION"],
        "status": ["STATUS", "CASE_STATUS", "VIOLATION_STATUS"],
        "compliance_date": ["COMPLIANCE_DATE", "DUE_DATE"],
        "case_number": ["CASE_NUMBER", "CASE_NO", "VIOLATION_NO"],
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def active_violations_csv(tmp_path: Path) -> Path:
    """CSV with a mix of OPEN, CLOSED, and ACTIVE violations."""
    csv_path = tmp_path / "code_violation_2024.csv"
    csv_path.write_text(
        "PARCEL_ID,ADDRESS,CITY,ZIP,"
        "VIOLATION_DATE,VIOLATION_TYPE,STATUS,CASE_NUMBER\n"
        "12345,100 MAIN ST,NAPLES,34102,"
        "2024-01-15,OVERGROWN VEGETATION,OPEN,CV-2024-001\n"
        "67890,200 OAK AVE,NAPLES,34103,"
        "2024-02-20,UNPERMITTED STRUCTURE,CLOSED,CV-2024-002\n"
        "11111,300 ELM ST,NAPLES,34104,"
        "2024-03-10,JUNK VEHICLES,ACTIVE,CV-2024-003\n"
        "22222,400 PINE RD,NAPLES,34105,"
        "2024-04-05,NOISE COMPLAINT,RESOLVED,CV-2024-004\n",
        encoding="utf-8",
    )
    return csv_path


@pytest.fixture
def connector(tmp_path: Path) -> CodeViolationConnector:
    """Create a CodeViolationConnector."""
    return CodeViolationConnector(
        import_dir=tmp_path,
        config=SAMPLE_CONFIG,
        county="collier",
    )


# ---------------------------------------------------------------------------
# Test: transform produces SourceRecords
# ---------------------------------------------------------------------------


class TestTransformProducesRecords:
    """Tests for the complete transform pipeline."""

    def test_transform_produces_source_records(
        self, tmp_path: Path, active_violations_csv: Path
    ) -> None:
        """Active violations produce valid SourceRecord-compatible dicts."""
        conn = CodeViolationConnector(
            import_dir=tmp_path,
            config=SAMPLE_CONFIG,
        )

        raw = [{"file_path": active_violations_csv}]
        results = conn.transform(raw)

        # OPEN and ACTIVE should be kept; CLOSED and RESOLVED should be filtered
        assert len(results) == 2

        rec = results[0]
        assert rec["source_name"] == "code_violations"
        assert rec["record_type"] == "code_violation"
        assert rec["parcel_id"] == "12345"
        assert rec["street_address"] == "100 MAIN ST"
        assert rec["city"] == "NAPLES"
        assert rec["zip_code"] == "34102"
        assert rec["event_date"] == date(2024, 1, 15)
        assert rec["event_type"] == "code_violation"

        # Verify SourceRecord can be constructed
        from theleadedge.models.source_record import SourceRecord

        sr = SourceRecord(**rec)
        assert sr.source_name == "code_violations"
        assert sr.record_type == "code_violation"


# ---------------------------------------------------------------------------
# Test: active violation filtering
# ---------------------------------------------------------------------------


class TestActiveFiltering:
    """Tests for status-based filtering."""

    def test_filters_active_violations(
        self, tmp_path: Path, active_violations_csv: Path
    ) -> None:
        """Only OPEN and ACTIVE violations are kept."""
        conn = CodeViolationConnector(
            import_dir=tmp_path,
            config=SAMPLE_CONFIG,
        )

        raw = [{"file_path": active_violations_csv}]
        results = conn.transform(raw)

        # Should have OPEN (12345) and ACTIVE (11111), not CLOSED or RESOLVED
        parcel_ids = [r["parcel_id"] for r in results]
        assert "12345" in parcel_ids  # OPEN
        assert "11111" in parcel_ids  # ACTIVE
        assert len(results) == 2

    def test_filters_out_closed(self, tmp_path: Path) -> None:
        """CLOSED and RESOLVED violations are filtered out."""
        csv_path = tmp_path / "code_violation_closed.csv"
        csv_path.write_text(
            "PARCEL_ID,ADDRESS,CITY,ZIP,VIOLATION_DATE,VIOLATION_TYPE,STATUS\n"
            "AAA,1 ST,NAPLES,34102,2024-01-01,WEEDS,CLOSED\n"
            "BBB,2 ST,NAPLES,34102,2024-01-01,TRASH,RESOLVED\n"
            "CCC,3 ST,NAPLES,34102,2024-01-01,JUNK,COMPLIANT\n"
            "DDD,4 ST,NAPLES,34102,2024-01-01,NOISE,DISMISSED\n",
            encoding="utf-8",
        )

        conn = CodeViolationConnector(
            import_dir=tmp_path,
            config=SAMPLE_CONFIG,
        )

        raw = [{"file_path": csv_path}]
        results = conn.transform(raw)

        # All four statuses are in the closed set -- zero results
        assert len(results) == 0

    def test_empty_status_treated_as_active(self, tmp_path: Path) -> None:
        """Rows with no status field are treated as active (included)."""
        csv_path = tmp_path / "violation_no_status.csv"
        csv_path.write_text(
            "PARCEL_ID,ADDRESS,CITY,ZIP,VIOLATION_DATE,VIOLATION_TYPE\n"
            "12345,100 MAIN ST,NAPLES,34102,2024-01-15,WEEDS\n",
            encoding="utf-8",
        )

        conn = CodeViolationConnector(
            import_dir=tmp_path,
            config=SAMPLE_CONFIG,
        )

        raw = [{"file_path": csv_path}]
        results = conn.transform(raw)

        assert len(results) == 1


# ---------------------------------------------------------------------------
# Test: missing parcel fallback
# ---------------------------------------------------------------------------


class TestMissingParcelFallback:
    """Tests for records with missing parcel IDs."""

    def test_missing_parcel_fallback(self, tmp_path: Path) -> None:
        """Records without parcel_id still produce a record with address."""
        csv_path = tmp_path / "code_violation_no_parcel.csv"
        csv_path.write_text(
            "ADDRESS,CITY,ZIP,VIOLATION_DATE,VIOLATION_TYPE,STATUS\n"
            "500 SUNSET DR,NAPLES,34102,2024-05-01,DEBRIS,OPEN\n",
            encoding="utf-8",
        )

        conn = CodeViolationConnector(
            import_dir=tmp_path,
            config=SAMPLE_CONFIG,
        )

        raw = [{"file_path": csv_path}]
        results = conn.transform(raw)

        assert len(results) == 1
        rec = results[0]
        assert rec["parcel_id"] is None
        assert rec["street_address"] == "500 SUNSET DR"
        assert rec["city"] == "NAPLES"


# ---------------------------------------------------------------------------
# Test: violation_type in raw_data
# ---------------------------------------------------------------------------


class TestViolationTypeInRawData:
    """Tests for violation_type presence in raw_data."""

    def test_violation_type_in_raw_data(
        self, tmp_path: Path, active_violations_csv: Path
    ) -> None:
        """violation_type appears in the raw_data dict."""
        conn = CodeViolationConnector(
            import_dir=tmp_path,
            config=SAMPLE_CONFIG,
        )

        raw = [{"file_path": active_violations_csv}]
        results = conn.transform(raw)

        assert len(results) >= 1
        rec = results[0]
        assert "violation_type" in rec["raw_data"]
        assert rec["raw_data"]["violation_type"] == "OVERGROWN VEGETATION"


# ---------------------------------------------------------------------------
# Test: health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """Tests for the health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_exists(self, tmp_path: Path) -> None:
        """Health check returns True when directory exists."""
        conn = CodeViolationConnector(
            import_dir=tmp_path,
            config=SAMPLE_CONFIG,
        )
        assert await conn.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_missing(self, tmp_path: Path) -> None:
        """Health check returns False when directory does not exist."""
        missing_dir = tmp_path / "nonexistent" / "deep"
        conn = CodeViolationConnector(
            import_dir=missing_dir,
            config=SAMPLE_CONFIG,
        )
        assert await conn.health_check() is False


# ---------------------------------------------------------------------------
# Test: file discovery
# ---------------------------------------------------------------------------


class TestFindFiles:
    """Tests for the _find_files method."""

    def test_finds_code_violation_files(self, tmp_path: Path) -> None:
        """Files prefixed with code_violation or violation are found."""
        (tmp_path / "code_violation_2024.csv").write_text(
            "PARCEL_ID\n", encoding="utf-8"
        )
        (tmp_path / "violation_collier.csv").write_text(
            "PARCEL_ID\n", encoding="utf-8"
        )
        # Not matching
        (tmp_path / "lis_pendens_2024.csv").write_text(
            "PARCEL_ID\n", encoding="utf-8"
        )

        conn = CodeViolationConnector(
            import_dir=tmp_path,
            config=SAMPLE_CONFIG,
        )
        found = conn._find_files()
        assert len(found) == 2
        names = {p.name for p in found}
        assert "code_violation_2024.csv" in names
        assert "violation_collier.csv" in names
