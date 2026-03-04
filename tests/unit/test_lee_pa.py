"""Unit tests for the Lee County Property Appraiser connector.

Tests cover authentication, ZIP download and extraction (mocked HTTP),
NAL/SDF parsing and joining on STRAP, absentee detection, homestead
detection, and health checks.

All HTTP calls are mocked -- no real network requests are made.
All test data is synthetic -- no real PII.
"""

from __future__ import annotations

import io
import zipfile
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest

from theleadedge.models.source_record import SourceRecord
from theleadedge.sources.property_appraiser import LeePAConnector

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_LEE_CONFIG: dict[str, Any] = {
    "lee": {
        "source_name": "lee_pa",
        "format": "nal_fixed_width",
    }
}


def _create_mock_zip(content: str, filename: str = "data.txt") -> bytes:
    """Create an in-memory ZIP file containing a single text file.

    Parameters
    ----------
    content:
        Text content for the file inside the ZIP.
    filename:
        Name of the file inside the ZIP archive.

    Returns
    -------
    bytes
        ZIP file content as bytes.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, content)
    return buf.getvalue()


def _build_nal_line(
    strap: str = "",
    owner_name_1: str = "",
    owner_name_2: str = "",
    mail_addr_1: str = "",
    mail_addr_2: str = "",
    mail_city: str = "",
    mail_state: str = "",
    mail_zip: str = "",
    site_addr: str = "",
    site_city: str = "",
    site_zip: str = "",
    use_code: str = "",
    assessed_value: str = "",
    homestead: str = "",
    taxable_value: str = "",
) -> str:
    """Build a synthetic NAL fixed-width line matching LEE_NAL_FIELDS layout.

    Each field is padded or truncated to its exact column width.
    Total line width: 313 characters.
    """
    parts = [
        strap.ljust(18),              # 0-18
        owner_name_1.ljust(40),       # 18-58
        owner_name_2.ljust(40),       # 58-98
        mail_addr_1.ljust(40),        # 98-138
        mail_addr_2.ljust(40),        # 138-178
        mail_city.ljust(25),          # 178-203
        mail_state.ljust(2),          # 203-205
        mail_zip.ljust(9),            # 205-214
        site_addr.ljust(40),          # 214-254
        site_city.ljust(25),          # 254-279
        site_zip.ljust(5),            # 279-284
        use_code.ljust(4),            # 284-288
        assessed_value.rjust(12),     # 288-300
        homestead.ljust(1),           # 300-301
        taxable_value.rjust(12),      # 301-313
    ]
    return "".join(parts)


def _build_sdf_line(
    strap: str = "",
    sale_date: str = "",
    sale_price: str = "",
    deed_type: str = "",
    qualified: str = "",
) -> str:
    """Build a synthetic SDF fixed-width line matching LEE_SDF_FIELDS layout.

    Total line width: 41 characters.
    """
    parts = [
        strap.ljust(18),              # 0-18
        sale_date.ljust(8),           # 18-26
        sale_price.rjust(12),         # 26-38
        deed_type.ljust(2),           # 38-40
        qualified.ljust(1),           # 40-41
    ]
    return "".join(parts)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def connector(tmp_path: Path) -> LeePAConnector:
    """Create a Lee PA connector with a temp download directory."""
    return LeePAConnector(
        download_dir=tmp_path,
        config=SAMPLE_LEE_CONFIG,
    )


# Synthetic NAL lines (NEVER real PII)
NAL_LINE_A = _build_nal_line(
    strap="012345678901234567",
    owner_name_1="SYNTHETIC OWNER A",
    owner_name_2="",
    mail_addr_1="100 MAIN ST",
    mail_addr_2="",
    mail_city="CAPE CORAL",
    mail_state="FL",
    mail_zip="33904",
    site_addr="100 MAIN ST",
    site_city="CAPE CORAL",
    site_zip="33904",
    use_code="0100",
    assessed_value="325000.0",
    homestead="Y",
    taxable_value="275000.0",
)

NAL_LINE_B = _build_nal_line(
    strap="098765432109876543",
    owner_name_1="SYNTHETIC OWNER B",
    owner_name_2="TRUST",
    mail_addr_1="PO BOX 999",
    mail_addr_2="",
    mail_city="NEW YORK",
    mail_state="NY",
    mail_zip="10001",
    site_addr="200 PALM AVE",
    site_city="FORT MYERS",
    site_zip="33901",
    use_code="0100",
    assessed_value="250000.0",
    homestead="N",
    taxable_value="250000.0",
)

SDF_LINE_A = _build_sdf_line(
    strap="012345678901234567",
    sale_date="01152020",
    sale_price="350000.0",
    deed_type="WD",
    qualified="Q",
)

SDF_LINE_B = _build_sdf_line(
    strap="098765432109876543",
    sale_date="06012019",
    sale_price="275000.0",
    deed_type="WD",
    qualified="Q",
)

NAL_CONTENT = f"{NAL_LINE_A}\n{NAL_LINE_B}"
SDF_CONTENT = f"{SDF_LINE_A}\n{SDF_LINE_B}"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAuthenticate:
    """Tests for the authenticate method."""

    async def test_authenticate_returns_none(
        self, connector: LeePAConnector
    ) -> None:
        """authenticate() should succeed (returns None) and create the dir."""
        result = await connector.authenticate()
        assert result is None
        assert connector.download_dir.exists()

    async def test_authenticate_creates_directory(self, tmp_path: Path) -> None:
        """authenticate() creates the download directory if missing."""
        subdir = tmp_path / "deep" / "nested" / "lee_data"
        conn = LeePAConnector(
            download_dir=subdir,
            config=SAMPLE_LEE_CONFIG,
        )
        await conn.authenticate()
        assert subdir.exists()


class TestFetch:
    """Tests for the fetch method (ZIP download + extraction)."""

    async def test_fetch_downloads_and_extracts_zip(self, tmp_path: Path) -> None:
        """fetch() should download ZIP files, extract, and return joined records."""
        nal_zip = _create_mock_zip(NAL_CONTENT, "NAL.txt")
        sdf_zip = _create_mock_zip(SDF_CONTENT, "SDF.txt")

        async def mock_handler(request: httpx.Request) -> httpx.Response:
            url_str = str(request.url)
            if "NAL.zip" in url_str:
                return httpx.Response(200, content=nal_zip)
            if "SDF.zip" in url_str:
                return httpx.Response(200, content=sdf_zip)
            return httpx.Response(404)

        transport = httpx.MockTransport(mock_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = LeePAConnector(
            download_dir=tmp_path,
            config=SAMPLE_LEE_CONFIG,
            http_client=client,
        )
        await conn.authenticate()
        raw_records = await conn.fetch()

        # Should have downloaded both ZIP files
        assert (tmp_path / "NAL.zip").exists()
        assert (tmp_path / "SDF.zip").exists()

        # Should have extracted contents
        assert (tmp_path / "NAL.txt").exists()
        assert (tmp_path / "SDF.txt").exists()

        # Should return joined records (one per NAL line)
        assert len(raw_records) == 2

        await client.aclose()

    async def test_fetch_handles_download_error(self, tmp_path: Path) -> None:
        """fetch() should raise on HTTP error."""

        async def error_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, content=b"Internal Server Error")

        transport = httpx.MockTransport(error_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = LeePAConnector(
            download_dir=tmp_path,
            config=SAMPLE_LEE_CONFIG,
            http_client=client,
        )
        await conn.authenticate()

        with pytest.raises(httpx.HTTPStatusError):
            await conn.fetch()

        await client.aclose()


class TestTransform:
    """Tests for the transform method (NAL/SDF parsing + enrichment)."""

    def test_transform_joins_on_strap(
        self, connector: LeePAConnector, tmp_path: Path
    ) -> None:
        """transform() should join NAL + SDF data on STRAP and produce records."""
        # Write NAL and SDF files directly, simulate post-extraction
        nal_path = tmp_path / "NAL.txt"
        sdf_path = tmp_path / "SDF.txt"
        nal_path.write_text(NAL_CONTENT, encoding="utf-8")
        sdf_path.write_text(SDF_CONTENT, encoding="utf-8")

        # Simulate extracted paths structure
        extracted = {
            "NAL.zip": [nal_path],
            "SDF.zip": [sdf_path],
        }
        raw_records = connector._load_and_join(extracted)
        results = connector.transform(raw_records)

        assert len(results) == 2

        # Find record A
        rec_a = next(
            r for r in results if r["parcel_id"] == "012345678901234567"
        )
        assert rec_a["source_name"] == "lee_pa"
        assert rec_a["record_type"] == "property_assessment"
        assert rec_a["raw_data"]["last_sale_price"] == 350000.0
        assert rec_a["raw_data"]["assessed_value"] == 325000.0
        assert rec_a["state"] == "FL"
        assert rec_a["event_date"] == date(2020, 1, 15)

    def test_transform_detects_absentee(
        self, connector: LeePAConnector, tmp_path: Path
    ) -> None:
        """transform() should detect absentee owners (different mail vs site)."""
        nal_path = tmp_path / "NAL.txt"
        sdf_path = tmp_path / "SDF.txt"
        nal_path.write_text(NAL_CONTENT, encoding="utf-8")
        sdf_path.write_text(SDF_CONTENT, encoding="utf-8")

        extracted = {
            "NAL.zip": [nal_path],
            "SDF.zip": [sdf_path],
        }
        raw_records = connector._load_and_join(extracted)
        results = connector.transform(raw_records)

        # Record A: same site and mail address -> NOT absentee
        rec_a = next(r for r in results if r["parcel_id"] == "012345678901234567")
        assert rec_a["raw_data"]["is_absentee"] is False

        # Record B: NY mailing address, FL site -> absentee
        rec_b = next(r for r in results if r["parcel_id"] == "098765432109876543")
        assert rec_b["raw_data"]["is_absentee"] is True

    def test_transform_detects_homestead(
        self, connector: LeePAConnector, tmp_path: Path
    ) -> None:
        """transform() should detect homestead exemption from 'Y' flag."""
        nal_path = tmp_path / "NAL.txt"
        sdf_path = tmp_path / "SDF.txt"
        nal_path.write_text(NAL_CONTENT, encoding="utf-8")
        sdf_path.write_text(SDF_CONTENT, encoding="utf-8")

        extracted = {
            "NAL.zip": [nal_path],
            "SDF.zip": [sdf_path],
        }
        raw_records = connector._load_and_join(extracted)
        results = connector.transform(raw_records)

        # Record A: homestead = "Y" -> exempt
        rec_a = next(r for r in results if r["parcel_id"] == "012345678901234567")
        assert rec_a["raw_data"]["homestead_exempt"] is True

        # Record B: homestead = "N" -> NOT exempt
        rec_b = next(r for r in results if r["parcel_id"] == "098765432109876543")
        assert rec_b["raw_data"]["homestead_exempt"] is False

    def test_transform_handles_missing_sales(
        self, connector: LeePAConnector, tmp_path: Path
    ) -> None:
        """transform() should produce records even without SDF sales data."""
        nal_path = tmp_path / "NAL.txt"
        sdf_path = tmp_path / "SDF.txt"
        nal_path.write_text(NAL_CONTENT, encoding="utf-8")
        sdf_path.write_text("", encoding="utf-8")  # Empty SDF

        extracted = {
            "NAL.zip": [nal_path],
            "SDF.zip": [sdf_path],
        }
        raw_records = connector._load_and_join(extracted)
        results = connector.transform(raw_records)

        assert len(results) == 2
        rec = next(r for r in results if r["parcel_id"] == "012345678901234567")
        assert rec["raw_data"]["last_sale_price"] is None
        assert rec["raw_data"]["last_sale_date"] is None
        # Assessment values should still be present
        assert rec["raw_data"]["assessed_value"] == 325000.0

    def test_transform_to_source_records(
        self, connector: LeePAConnector, tmp_path: Path
    ) -> None:
        """to_source_records() should produce valid SourceRecord instances."""
        nal_path = tmp_path / "NAL.txt"
        sdf_path = tmp_path / "SDF.txt"
        nal_path.write_text(NAL_CONTENT, encoding="utf-8")
        sdf_path.write_text(SDF_CONTENT, encoding="utf-8")

        extracted = {
            "NAL.zip": [nal_path],
            "SDF.zip": [sdf_path],
        }
        raw_records = connector._load_and_join(extracted)
        source_records = connector.to_source_records(raw_records)

        assert len(source_records) == 2
        assert all(isinstance(sr, SourceRecord) for sr in source_records)

        sr_a = next(
            sr for sr in source_records if sr.parcel_id == "012345678901234567"
        )
        assert sr_a.source_name == "lee_pa"
        assert sr_a.record_type == "property_assessment"
        assert sr_a.city == "CAPE CORAL"
        assert sr_a.state == "FL"
        assert sr_a.zip_code == "33904"


class TestHealthCheck:
    """Tests for the health_check and health_check_detailed methods."""

    async def test_health_check_healthy(self, tmp_path: Path) -> None:
        """health_check() returns True when all URLs respond 200."""

        async def ok_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200)

        transport = httpx.MockTransport(ok_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = LeePAConnector(
            download_dir=tmp_path,
            config=SAMPLE_LEE_CONFIG,
            http_client=client,
        )
        result = await conn.health_check()
        assert result is True

        detail = await conn.health_check_detailed()
        assert detail["status"] == "healthy"
        assert detail["urls_checked"] == 2
        for _url, code in detail["response_codes"].items():
            assert code == 200

        await client.aclose()

    async def test_health_check_unhealthy(self, tmp_path: Path) -> None:
        """health_check() returns False when a URL responds with 500."""

        async def error_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500)

        transport = httpx.MockTransport(error_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = LeePAConnector(
            download_dir=tmp_path,
            config=SAMPLE_LEE_CONFIG,
            http_client=client,
        )
        result = await conn.health_check()
        assert result is False

        detail = await conn.health_check_detailed()
        assert detail["status"] == "unhealthy"
        assert detail["urls_checked"] == 2

        await client.aclose()

    async def test_health_check_partial_failure(self, tmp_path: Path) -> None:
        """health_check() returns False if even one URL fails."""

        async def mixed_handler(request: httpx.Request) -> httpx.Response:
            url_str = str(request.url)
            if "NAL.zip" in url_str:
                return httpx.Response(200)
            # SDF returns 404
            return httpx.Response(404)

        transport = httpx.MockTransport(mixed_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = LeePAConnector(
            download_dir=tmp_path,
            config=SAMPLE_LEE_CONFIG,
            http_client=client,
        )
        result = await conn.health_check()
        assert result is False

        await client.aclose()


class TestAbsenteeDetection:
    """Focused tests for Lee County absentee owner detection."""

    def test_same_address_not_absentee(self) -> None:
        """Identical site and mail addresses should NOT be absentee."""
        record = {
            "site_addr": "100 MAIN ST",
            "site_city": "CAPE CORAL",
            "site_zip": "33904",
            "mail_addr_1": "100 MAIN ST",
            "mail_city": "CAPE CORAL",
            "mail_zip": "33904",
        }
        assert LeePAConnector._detect_absentee(record) is False

    def test_different_address_is_absentee(self) -> None:
        """Different site and mail addresses should be absentee."""
        record = {
            "site_addr": "200 PALM AVE",
            "site_city": "FORT MYERS",
            "site_zip": "33901",
            "mail_addr_1": "PO BOX 999",
            "mail_city": "NEW YORK",
            "mail_zip": "10001",
        }
        assert LeePAConnector._detect_absentee(record) is True

    def test_missing_addresses_not_absentee(self) -> None:
        """Missing address fields should default to not absentee."""
        record = {
            "site_addr": "",
            "mail_addr_1": "",
        }
        assert LeePAConnector._detect_absentee(record) is False

    def test_case_insensitive_comparison(self) -> None:
        """Address comparison should be case-insensitive."""
        record = {
            "site_addr": "100 Main St",
            "site_city": "cape coral",
            "site_zip": "33904",
            "mail_addr_1": "100 MAIN ST",
            "mail_city": "CAPE CORAL",
            "mail_zip": "33904",
        }
        assert LeePAConnector._detect_absentee(record) is False


class TestHomesteadDetection:
    """Focused tests for Lee County homestead detection."""

    def test_y_flag_is_homestead(self) -> None:
        """homestead = 'Y' means homestead exempt."""
        assert LeePAConnector._detect_homestead({"homestead": "Y"}) is True

    def test_lowercase_y_is_homestead(self) -> None:
        """homestead = 'y' (lowercase) should also be detected."""
        assert LeePAConnector._detect_homestead({"homestead": "y"}) is True

    def test_n_flag_not_homestead(self) -> None:
        """homestead = 'N' means NOT homestead exempt."""
        assert LeePAConnector._detect_homestead({"homestead": "N"}) is False

    def test_empty_not_homestead(self) -> None:
        """Empty homestead field means NOT homestead exempt."""
        assert LeePAConnector._detect_homestead({"homestead": ""}) is False
        assert LeePAConnector._detect_homestead({}) is False


class TestParseSaleDate:
    """Tests for MMDDYYYY date parsing."""

    def test_valid_date(self) -> None:
        """Standard MMDDYYYY format should parse correctly."""
        assert LeePAConnector._parse_sale_date("01152020") == date(2020, 1, 15)
        assert LeePAConnector._parse_sale_date("12312025") == date(2025, 12, 31)

    def test_empty_date(self) -> None:
        """Empty or None date should return None."""
        assert LeePAConnector._parse_sale_date("") is None
        assert LeePAConnector._parse_sale_date(None) is None

    def test_invalid_date(self) -> None:
        """Invalid date strings should return None."""
        assert LeePAConnector._parse_sale_date("INVALID!") is None
        assert LeePAConnector._parse_sale_date("99991301") is None  # month 13

    def test_wrong_length_date(self) -> None:
        """Dates not exactly 8 chars should return None."""
        assert LeePAConnector._parse_sale_date("0115202") is None  # 7 chars
        assert LeePAConnector._parse_sale_date("011520200") is None  # 9 chars


class TestZipExtraction:
    """Tests for ZIP file extraction helpers."""

    def test_extract_zip(self, connector: LeePAConnector, tmp_path: Path) -> None:
        """_extract_zip should extract all members to download_dir."""
        content = "test file content"
        zip_data = _create_mock_zip(content, "inner.txt")
        zip_path = tmp_path / "test.zip"
        zip_path.write_bytes(zip_data)

        extracted = connector._extract_zip(zip_path)

        assert len(extracted) == 1
        assert extracted[0] == tmp_path / "inner.txt"
        assert extracted[0].read_text() == content

    def test_extract_zip_multiple_files(
        self, connector: LeePAConnector, tmp_path: Path
    ) -> None:
        """_extract_zip should handle ZIPs with multiple files."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")

        zip_path = tmp_path / "multi.zip"
        zip_path.write_bytes(buf.getvalue())

        extracted = connector._extract_zip(zip_path)

        assert len(extracted) == 2
        names = {p.name for p in extracted}
        assert names == {"file1.txt", "file2.txt"}
