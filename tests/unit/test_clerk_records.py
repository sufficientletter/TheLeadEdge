"""Unit tests for the Clerk of Court record connector.

Tests cover file discovery, CSV/XLSX reading, encoding fallback, header
normalization, SourceRecord transformation, and health checks.

All test data is synthetic -- no real PII.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest

from theleadedge.sources.clerk_records import (
    ClerkRecordConnector,
    _parse_date,
)

# ---------------------------------------------------------------------------
# Shared config fixture (simulates clerk_fields.yaml content)
# ---------------------------------------------------------------------------

SAMPLE_CONFIG: dict[str, Any] = {
    "lis_pendens": {
        "parcel_id": ["PARCEL_ID", "PARCEL", "FOLIO"],
        "street_address": ["ADDRESS", "PROPERTY_ADDRESS", "SITE_ADDRESS"],
        "city": ["CITY", "PROPERTY_CITY"],
        "state": ["STATE"],
        "zip_code": ["ZIP", "ZIP_CODE"],
        "event_date": ["FILING_DATE", "RECORDED_DATE", "DATE_FILED"],
        "event_type": ["CASE_TYPE", "FILING_TYPE"],
        "owner_name": ["DEFENDANT", "OWNER_NAME", "OWNER"],
        "case_number": ["CASE_NUMBER", "CASE_NO"],
    },
    "probate": {
        "parcel_id": ["PARCEL_ID", "PARCEL"],
        "street_address": ["ADDRESS", "PROPERTY_ADDRESS"],
        "city": ["CITY"],
        "zip_code": ["ZIP", "ZIP_CODE"],
        "event_date": ["FILING_DATE", "DATE_OF_DEATH"],
        "owner_name": ["DECEDENT", "DECEDENT_NAME"],
        "case_number": ["CASE_NUMBER", "CASE_NO"],
    },
    "divorce": {
        "parcel_id": ["PARCEL_ID", "PARCEL"],
        "street_address": ["ADDRESS", "PROPERTY_ADDRESS"],
        "city": ["CITY"],
        "zip_code": ["ZIP", "ZIP_CODE"],
        "event_date": ["FILING_DATE", "PETITION_DATE"],
        "owner_name": ["PETITIONER", "PARTY_NAME"],
        "case_number": ["CASE_NUMBER", "CASE_NO"],
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a sample lis pendens CSV file."""
    csv_path = tmp_path / "lis_pendens_2024.csv"
    csv_path.write_text(
        "PARCEL_ID,ADDRESS,CITY,ZIP,FILING_DATE,CASE_NUMBER,DEFENDANT\n"
        "12345,100 MAIN ST,NAPLES,34102,2024-01-15,2024-CA-001,TEST OWNER\n"
        "67890,200 OAK AVE,NAPLES,34103,2024-02-20,2024-CA-002,TEST OWNER 2\n",
        encoding="utf-8",
    )
    return csv_path


@pytest.fixture
def sample_probate_csv(tmp_path: Path) -> Path:
    """Create a sample probate CSV file."""
    csv_path = tmp_path / "probate_2024_q1.csv"
    csv_path.write_text(
        "PARCEL_ID,ADDRESS,CITY,ZIP,FILING_DATE,CASE_NUMBER,DECEDENT\n"
        "11111,300 ELM ST,NAPLES,34104,2024-03-10,2024-CP-001,DECEDENT A\n",
        encoding="utf-8",
    )
    return csv_path


@pytest.fixture
def connector(tmp_path: Path) -> ClerkRecordConnector:
    """Create a ClerkRecordConnector for lis_pendens."""
    return ClerkRecordConnector(
        import_dir=tmp_path,
        record_type="lis_pendens",
        config=SAMPLE_CONFIG,
        county="collier",
    )


# ---------------------------------------------------------------------------
# Test: file discovery
# ---------------------------------------------------------------------------


class TestFindFiles:
    """Tests for the _find_files method."""

    def test_find_csv_files(self, tmp_path: Path) -> None:
        """CSV files matching the record type prefix are found."""
        (tmp_path / "lis_pendens_2024.csv").write_text(
            "PARCEL_ID\n12345\n", encoding="utf-8"
        )
        (tmp_path / "lis_pendens_q2.csv").write_text(
            "PARCEL_ID\n67890\n", encoding="utf-8"
        )
        # Unrelated file should NOT be found
        (tmp_path / "probate_2024.csv").write_text(
            "PARCEL_ID\n99999\n", encoding="utf-8"
        )

        conn = ClerkRecordConnector(
            import_dir=tmp_path,
            record_type="lis_pendens",
            config=SAMPLE_CONFIG,
        )
        found = conn._find_files()
        assert len(found) == 2
        assert all(p.name.startswith("lis_pendens") for p in found)

    def test_find_xlsx_files(self, tmp_path: Path) -> None:
        """XLSX files matching the record type prefix are found."""
        # Create a minimal XLSX via openpyxl
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["PARCEL_ID", "ADDRESS"])
        ws.append(["12345", "100 MAIN ST"])
        xlsx_path = tmp_path / "lis_pendens_2024.xlsx"
        wb.save(xlsx_path)
        wb.close()

        conn = ClerkRecordConnector(
            import_dir=tmp_path,
            record_type="lis_pendens",
            config=SAMPLE_CONFIG,
        )
        found = conn._find_files()
        assert len(found) == 1
        assert found[0].suffix == ".xlsx"

    def test_ignores_non_matching_files(self, tmp_path: Path) -> None:
        """Files that do not match the record type prefix are ignored."""
        (tmp_path / "divorce_2024.csv").write_text("PARCEL_ID\n", encoding="utf-8")
        (tmp_path / "random_file.txt").write_text("data\n", encoding="utf-8")

        conn = ClerkRecordConnector(
            import_dir=tmp_path,
            record_type="lis_pendens",
            config=SAMPLE_CONFIG,
        )
        found = conn._find_files()
        assert len(found) == 0


# ---------------------------------------------------------------------------
# Test: CSV reading
# ---------------------------------------------------------------------------


class TestReadCsv:
    """Tests for CSV file reading."""

    def test_read_csv_utf8(
        self, connector: ClerkRecordConnector, sample_csv: Path
    ) -> None:
        """UTF-8 encoded CSV is read correctly."""
        rows = connector._read_csv(sample_csv)
        assert len(rows) == 2
        assert rows[0]["PARCEL_ID"] == "12345"
        assert rows[0]["ADDRESS"] == "100 MAIN ST"
        assert rows[1]["PARCEL_ID"] == "67890"

    def test_read_csv_encoding_fallback(self, tmp_path: Path) -> None:
        """CP-1252 encoded file falls back and is read correctly."""
        csv_path = tmp_path / "lis_pendens_cp1252.csv"
        content = "PARCEL_ID,ADDRESS,CITY\n12345,100 MAIN ST\u00e9,NAPLES\n"
        csv_path.write_bytes(content.encode("cp1252"))

        conn = ClerkRecordConnector(
            import_dir=tmp_path,
            record_type="lis_pendens",
            config=SAMPLE_CONFIG,
        )
        rows = conn._read_csv(csv_path)
        assert len(rows) == 1
        # The accented character should be preserved
        assert "\u00e9" in rows[0]["ADDRESS"]


# ---------------------------------------------------------------------------
# Test: XLSX reading
# ---------------------------------------------------------------------------


class TestReadXlsx:
    """Tests for XLSX file reading."""

    def test_read_xlsx(self, tmp_path: Path) -> None:
        """XLSX file is read correctly via openpyxl."""
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["PARCEL_ID", "ADDRESS", "CITY", "ZIP", "FILING_DATE"])
        ws.append(["12345", "100 MAIN ST", "NAPLES", "34102", "2024-01-15"])
        ws.append(["67890", "200 OAK AVE", "NAPLES", "34103", "2024-02-20"])
        xlsx_path = tmp_path / "lis_pendens_2024.xlsx"
        wb.save(xlsx_path)
        wb.close()

        conn = ClerkRecordConnector(
            import_dir=tmp_path,
            record_type="lis_pendens",
            config=SAMPLE_CONFIG,
        )
        rows = conn._read_xlsx(xlsx_path)
        assert len(rows) == 2
        assert rows[0]["PARCEL_ID"] == "12345"
        assert rows[0]["ADDRESS"] == "100 MAIN ST"


# ---------------------------------------------------------------------------
# Test: header normalization
# ---------------------------------------------------------------------------


class TestNormalizeHeaders:
    """Tests for column alias mapping."""

    def test_normalize_headers(self, connector: ClerkRecordConnector) -> None:
        """Column aliases are correctly mapped to internal field names."""
        row = {
            "PARCEL_ID": "12345",
            "ADDRESS": "100 MAIN ST",
            "CITY": "NAPLES",
            "ZIP": "34102",
            "FILING_DATE": "2024-01-15",
            "CASE_NUMBER": "2024-CA-001",
            "DEFENDANT": "TEST OWNER",
        }
        normalized = connector._normalize_headers(row)

        assert normalized["parcel_id"] == "12345"
        assert normalized["street_address"] == "100 MAIN ST"
        assert normalized["city"] == "NAPLES"
        assert normalized["zip_code"] == "34102"
        assert normalized["event_date"] == "2024-01-15"
        assert normalized["case_number"] == "2024-CA-001"
        assert normalized["owner_name"] == "TEST OWNER"

    def test_normalize_headers_alternative_aliases(
        self, connector: ClerkRecordConnector
    ) -> None:
        """Alternative column names (second or third alias) are mapped."""
        row = {
            "FOLIO": "99999",
            "PROPERTY_ADDRESS": "500 PALM DR",
            "PROPERTY_CITY": "NAPLES",
            "ZIP_CODE": "34105",
            "RECORDED_DATE": "2024-06-01",
            "CASE_NO": "2024-CA-999",
            "OWNER_NAME": "ALT OWNER",
        }
        normalized = connector._normalize_headers(row)

        assert normalized["parcel_id"] == "99999"
        assert normalized["street_address"] == "500 PALM DR"
        assert normalized["city"] == "NAPLES"
        assert normalized["zip_code"] == "34105"
        assert normalized["event_date"] == "2024-06-01"
        assert normalized["case_number"] == "2024-CA-999"
        assert normalized["owner_name"] == "ALT OWNER"

    def test_normalize_headers_case_insensitive(
        self, connector: ClerkRecordConnector
    ) -> None:
        """Header matching is case-insensitive."""
        row = {
            "parcel_id": "12345",
            "address": "100 MAIN ST",
            "city": "NAPLES",
        }
        normalized = connector._normalize_headers(row)
        assert normalized["parcel_id"] == "12345"
        assert normalized["street_address"] == "100 MAIN ST"
        assert normalized["city"] == "NAPLES"


# ---------------------------------------------------------------------------
# Test: full transform
# ---------------------------------------------------------------------------


class TestTransform:
    """Tests for the complete transform pipeline."""

    def test_transform_produces_source_records(
        self, tmp_path: Path, sample_csv: Path
    ) -> None:
        """Full transform from CSV produces valid SourceRecord-compatible dicts."""
        conn = ClerkRecordConnector(
            import_dir=tmp_path,
            record_type="lis_pendens",
            config=SAMPLE_CONFIG,
        )

        raw = [{"file_path": sample_csv}]
        results = conn.transform(raw)

        assert len(results) == 2

        rec = results[0]
        assert rec["source_name"] == "clerk_records"
        assert rec["record_type"] == "lis_pendens"
        assert rec["parcel_id"] == "12345"
        assert rec["street_address"] == "100 MAIN ST"
        assert rec["city"] == "NAPLES"
        assert rec["zip_code"] == "34102"
        assert rec["event_date"] == date(2024, 1, 15)
        assert rec["owner_name"] == "TEST OWNER"
        assert "case_number" in rec["raw_data"]
        assert rec["raw_data"]["case_number"] == "2024-CA-001"

        # Verify SourceRecord can be constructed
        from theleadedge.models.source_record import SourceRecord

        sr = SourceRecord(**rec)
        assert sr.source_name == "clerk_records"
        assert sr.parcel_id == "12345"

    def test_transform_probate_records(
        self, tmp_path: Path, sample_probate_csv: Path
    ) -> None:
        """Probate record type uses probate-specific alias mapping."""
        conn = ClerkRecordConnector(
            import_dir=tmp_path,
            record_type="probate",
            config=SAMPLE_CONFIG,
        )

        raw = [{"file_path": sample_probate_csv}]
        results = conn.transform(raw)

        assert len(results) == 1
        rec = results[0]
        assert rec["record_type"] == "probate"
        assert rec["parcel_id"] == "11111"
        assert rec["owner_name"] == "DECEDENT A"


# ---------------------------------------------------------------------------
# Test: health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """Tests for the health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_directory_exists(self, tmp_path: Path) -> None:
        """Health check returns True when import directory exists."""
        conn = ClerkRecordConnector(
            import_dir=tmp_path,
            record_type="lis_pendens",
            config=SAMPLE_CONFIG,
        )
        assert await conn.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_directory_missing(self, tmp_path: Path) -> None:
        """Health check returns False when import directory does not exist."""
        missing_dir = tmp_path / "nonexistent" / "deep" / "path"
        conn = ClerkRecordConnector(
            import_dir=missing_dir,
            record_type="lis_pendens",
            config=SAMPLE_CONFIG,
        )
        assert await conn.health_check() is False


# ---------------------------------------------------------------------------
# Test: invalid record type
# ---------------------------------------------------------------------------


class TestValidation:
    """Tests for input validation."""

    def test_invalid_record_type_raises(self, tmp_path: Path) -> None:
        """Constructing with an invalid record_type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid record_type"):
            ClerkRecordConnector(
                import_dir=tmp_path,
                record_type="invalid_type",
                config=SAMPLE_CONFIG,
            )


# ---------------------------------------------------------------------------
# Test: date parsing
# ---------------------------------------------------------------------------


class TestParseDate:
    """Tests for the _parse_date helper."""

    def test_parse_iso_date(self) -> None:
        assert _parse_date("2024-01-15") == date(2024, 1, 15)

    def test_parse_us_date(self) -> None:
        assert _parse_date("01/15/2024") == date(2024, 1, 15)

    def test_parse_empty_returns_none(self) -> None:
        assert _parse_date("") is None
        assert _parse_date("   ") is None

    def test_parse_invalid_returns_none(self) -> None:
        assert _parse_date("not-a-date") is None
