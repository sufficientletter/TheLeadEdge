"""Unit tests for the Collier County Property Appraiser connector.

Tests cover authentication, file download (mocked HTTP), CSV parsing/joining,
absentee detection, homestead detection, and health checks.

All HTTP calls are mocked -- no real network requests are made.
All test data is synthetic -- no real PII.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

import httpx
import pytest

from theleadedge.models.source_record import SourceRecord
from theleadedge.sources.property_appraiser import (
    PARCELS_FILE,
    SALES_FILE,
    VALUES_FILE,
    CollierPAConnector,
    _parse_date,
    _parse_float,
    load_pa_config,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CONFIG: dict[str, Any] = {
    "collier": {
        "source_name": "collier_pa",
        "parcels": {
            "parcel_id": "PARCEL_ID",
            "owner_name": "OWNER_NAME",
            "site_address": "SITE_ADDR",
            "site_city": "SITE_CITY",
            "site_state": "SITE_STATE",
            "site_zip": "SITE_ZIP",
            "mail_address": "MAIL_ADDR",
            "mail_city": "MAIL_CITY",
            "mail_state": "MAIL_STATE",
            "mail_zip": "MAIL_ZIP",
            "use_code": "USE_CODE",
        },
        "sales": {
            "parcel_id": "PARCEL_ID",
            "sale_date": "SALE_DATE",
            "sale_price": "SALE_PRICE",
            "deed_type": "DEED_TYPE",
            "qualified": "QUALIFIED",
        },
        "values": {
            "parcel_id": "PARCEL_ID",
            "assessed_value": "ASSESSED_VALUE",
            "market_value": "MARKET_VALUE",
            "homestead_exempt": "HOMESTEAD",
            "taxable_value": "TAXABLE_VALUE",
        },
    }
}


def _make_parcels_csv(rows: list[dict[str, str]]) -> str:
    """Build a Parcels CSV string from row dicts."""
    fieldnames = [
        "PARCEL_ID",
        "OWNER_NAME",
        "SITE_ADDR",
        "SITE_CITY",
        "SITE_STATE",
        "SITE_ZIP",
        "MAIL_ADDR",
        "MAIL_CITY",
        "MAIL_STATE",
        "MAIL_ZIP",
        "USE_CODE",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def _make_sales_csv(rows: list[dict[str, str]]) -> str:
    """Build a Sales CSV string from row dicts."""
    fieldnames = [
        "PARCEL_ID",
        "SALE_DATE",
        "SALE_PRICE",
        "DEED_TYPE",
        "QUALIFIED",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def _make_values_csv(rows: list[dict[str, str]]) -> str:
    """Build a Values CSV string from row dicts."""
    fieldnames = [
        "PARCEL_ID",
        "ASSESSED_VALUE",
        "MARKET_VALUE",
        "HOMESTEAD",
        "TAXABLE_VALUE",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def _write_csv_files(
    tmp_path: Path,
    parcels: list[dict[str, str]] | None = None,
    sales: list[dict[str, str]] | None = None,
    values: list[dict[str, str]] | None = None,
) -> None:
    """Write CSV files to tmp_path for transform tests."""
    if parcels is not None:
        (tmp_path / PARCELS_FILE).write_text(
            _make_parcels_csv(parcels), encoding="utf-8"
        )
    if sales is not None:
        (tmp_path / SALES_FILE).write_text(
            _make_sales_csv(sales), encoding="utf-8"
        )
    if values is not None:
        (tmp_path / VALUES_FILE).write_text(
            _make_values_csv(values), encoding="utf-8"
        )


@pytest.fixture
def connector(tmp_path: Path) -> CollierPAConnector:
    """Create a connector with a temp download directory."""
    return CollierPAConnector(
        download_dir=tmp_path,
        config=SAMPLE_CONFIG,
    )


# Default test parcels
DEFAULT_PARCELS = [
    {
        "PARCEL_ID": "00123456789",
        "OWNER_NAME": "SYNTHETIC OWNER A",
        "SITE_ADDR": "100 MAIN ST",
        "SITE_CITY": "NAPLES",
        "SITE_STATE": "FL",
        "SITE_ZIP": "34102",
        "MAIL_ADDR": "100 MAIN ST",
        "MAIL_CITY": "NAPLES",
        "MAIL_STATE": "FL",
        "MAIL_ZIP": "34102",
        "USE_CODE": "0100",
    },
    {
        "PARCEL_ID": "00987654321",
        "OWNER_NAME": "SYNTHETIC OWNER B",
        "SITE_ADDR": "200 PALM AVE",
        "SITE_CITY": "NAPLES",
        "SITE_STATE": "FL",
        "SITE_ZIP": "34103",
        "MAIL_ADDR": "PO BOX 999",
        "MAIL_CITY": "NEW YORK",
        "MAIL_STATE": "NY",
        "MAIL_ZIP": "10001",
        "USE_CODE": "0100",
    },
]

DEFAULT_SALES = [
    {
        "PARCEL_ID": "00123456789",
        "SALE_DATE": "01/15/2020",
        "SALE_PRICE": "350000",
        "DEED_TYPE": "WD",
        "QUALIFIED": "Q",
    },
    {
        "PARCEL_ID": "00987654321",
        "SALE_DATE": "06/01/2019",
        "SALE_PRICE": "275000",
        "DEED_TYPE": "WD",
        "QUALIFIED": "Q",
    },
]

DEFAULT_VALUES = [
    {
        "PARCEL_ID": "00123456789",
        "ASSESSED_VALUE": "325000",
        "MARKET_VALUE": "400000",
        "HOMESTEAD": "50000",
        "TAXABLE_VALUE": "275000",
    },
    {
        "PARCEL_ID": "00987654321",
        "ASSESSED_VALUE": "250000",
        "MARKET_VALUE": "310000",
        "HOMESTEAD": "0",
        "TAXABLE_VALUE": "250000",
    },
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAuthenticate:
    """Tests for the authenticate method."""

    async def test_authenticate_returns_none(
        self, connector: CollierPAConnector
    ) -> None:
        """authenticate() should succeed (returns None) and create the dir."""
        result = await connector.authenticate()
        assert result is None
        assert connector.download_dir.exists()

    async def test_authenticate_creates_directory(self, tmp_path: Path) -> None:
        """authenticate() creates the download directory if missing."""
        subdir = tmp_path / "deep" / "nested" / "pa_data"
        conn = CollierPAConnector(
            download_dir=subdir,
            config=SAMPLE_CONFIG,
        )
        await conn.authenticate()
        assert subdir.exists()


class TestFetch:
    """Tests for the fetch method (HTTP download)."""

    async def test_fetch_downloads_three_files(self, tmp_path: Path) -> None:
        """fetch() should download 3 CSV files via streaming HTTP."""
        parcels_csv = _make_parcels_csv(DEFAULT_PARCELS)
        sales_csv = _make_sales_csv(DEFAULT_SALES)
        values_csv = _make_values_csv(DEFAULT_VALUES)

        async def mock_handler(request: httpx.Request) -> httpx.Response:
            url_str = str(request.url)
            if PARCELS_FILE in url_str:
                return httpx.Response(200, content=parcels_csv.encode("utf-8"))
            if SALES_FILE in url_str:
                return httpx.Response(200, content=sales_csv.encode("utf-8"))
            if VALUES_FILE in url_str:
                return httpx.Response(200, content=values_csv.encode("utf-8"))
            return httpx.Response(404)

        transport = httpx.MockTransport(mock_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = CollierPAConnector(
            download_dir=tmp_path,
            config=SAMPLE_CONFIG,
            http_client=client,
        )
        await conn.authenticate()
        raw_records = await conn.fetch()

        # Should have downloaded all 3 files
        assert (tmp_path / PARCELS_FILE).exists()
        assert (tmp_path / SALES_FILE).exists()
        assert (tmp_path / VALUES_FILE).exists()

        # Should return joined records (one per parcel)
        assert len(raw_records) == 2

        await client.aclose()

    async def test_fetch_handles_download_error(self, tmp_path: Path) -> None:
        """fetch() should raise on HTTP error (e.g. 404 or 500)."""

        async def error_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, content=b"Internal Server Error")

        transport = httpx.MockTransport(error_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = CollierPAConnector(
            download_dir=tmp_path,
            config=SAMPLE_CONFIG,
            http_client=client,
        )
        await conn.authenticate()

        with pytest.raises(httpx.HTTPStatusError):
            await conn.fetch()

        await client.aclose()


class TestTransform:
    """Tests for the transform method (CSV parsing + enrichment)."""

    def test_transform_joins_on_parcel_id(
        self, connector: CollierPAConnector, tmp_path: Path
    ) -> None:
        """transform() should join parcels, sales, and values on PARCEL_ID."""
        _write_csv_files(
            tmp_path,
            parcels=DEFAULT_PARCELS,
            sales=DEFAULT_SALES,
            values=DEFAULT_VALUES,
        )

        paths = {
            PARCELS_FILE: tmp_path / PARCELS_FILE,
            SALES_FILE: tmp_path / SALES_FILE,
            VALUES_FILE: tmp_path / VALUES_FILE,
        }
        raw_records = connector._load_and_join(paths)
        results = connector.transform(raw_records)

        assert len(results) == 2

        # Find the record for parcel 00123456789
        rec_a = next(
            r for r in results if r["parcel_id"] == "00123456789"
        )
        assert rec_a["source_name"] == "collier_pa"
        assert rec_a["record_type"] == "property_assessment"
        assert rec_a["raw_data"]["last_sale_price"] == 350000.0
        assert rec_a["raw_data"]["assessed_value"] == 325000.0

    def test_transform_detects_absentee(
        self, connector: CollierPAConnector, tmp_path: Path
    ) -> None:
        """transform() should detect absentee owners (different mail vs site)."""
        _write_csv_files(
            tmp_path,
            parcels=DEFAULT_PARCELS,
            sales=DEFAULT_SALES,
            values=DEFAULT_VALUES,
        )

        paths = {
            PARCELS_FILE: tmp_path / PARCELS_FILE,
            SALES_FILE: tmp_path / SALES_FILE,
            VALUES_FILE: tmp_path / VALUES_FILE,
        }
        raw_records = connector._load_and_join(paths)
        results = connector.transform(raw_records)

        # Parcel A: same site and mail address -> NOT absentee
        rec_a = next(r for r in results if r["parcel_id"] == "00123456789")
        assert rec_a["raw_data"]["is_absentee"] is False

        # Parcel B: NY mailing address, FL site -> absentee
        rec_b = next(r for r in results if r["parcel_id"] == "00987654321")
        assert rec_b["raw_data"]["is_absentee"] is True

    def test_transform_detects_homestead(
        self, connector: CollierPAConnector, tmp_path: Path
    ) -> None:
        """transform() should detect homestead exemption from HOMESTEAD field."""
        _write_csv_files(
            tmp_path,
            parcels=DEFAULT_PARCELS,
            sales=DEFAULT_SALES,
            values=DEFAULT_VALUES,
        )

        paths = {
            PARCELS_FILE: tmp_path / PARCELS_FILE,
            SALES_FILE: tmp_path / SALES_FILE,
            VALUES_FILE: tmp_path / VALUES_FILE,
        }
        raw_records = connector._load_and_join(paths)
        results = connector.transform(raw_records)

        # Parcel A: HOMESTEAD = "50000" -> exempt
        rec_a = next(r for r in results if r["parcel_id"] == "00123456789")
        assert rec_a["raw_data"]["homestead_exempt"] is True

        # Parcel B: HOMESTEAD = "0" -> NOT exempt
        rec_b = next(r for r in results if r["parcel_id"] == "00987654321")
        assert rec_b["raw_data"]["homestead_exempt"] is False

    def test_transform_handles_missing_sales(
        self, connector: CollierPAConnector, tmp_path: Path
    ) -> None:
        """transform() should produce records even without sales data."""
        _write_csv_files(
            tmp_path,
            parcels=DEFAULT_PARCELS,
            sales=[],  # no sales
            values=DEFAULT_VALUES,
        )

        paths = {
            PARCELS_FILE: tmp_path / PARCELS_FILE,
            SALES_FILE: tmp_path / SALES_FILE,
            VALUES_FILE: tmp_path / VALUES_FILE,
        }
        raw_records = connector._load_and_join(paths)
        results = connector.transform(raw_records)

        assert len(results) == 2
        rec = next(r for r in results if r["parcel_id"] == "00123456789")
        assert rec["raw_data"]["last_sale_price"] is None
        assert rec["raw_data"]["last_sale_date"] is None
        # Values should still be present
        assert rec["raw_data"]["assessed_value"] == 325000.0

    def test_transform_handles_missing_values(
        self, connector: CollierPAConnector, tmp_path: Path
    ) -> None:
        """transform() should produce records even without values data."""
        _write_csv_files(
            tmp_path,
            parcels=DEFAULT_PARCELS,
            sales=DEFAULT_SALES,
            values=[],  # no values
        )

        paths = {
            PARCELS_FILE: tmp_path / PARCELS_FILE,
            SALES_FILE: tmp_path / SALES_FILE,
            VALUES_FILE: tmp_path / VALUES_FILE,
        }
        raw_records = connector._load_and_join(paths)
        results = connector.transform(raw_records)

        assert len(results) == 2
        rec = next(r for r in results if r["parcel_id"] == "00123456789")
        # Sale data should still be present
        assert rec["raw_data"]["last_sale_price"] == 350000.0
        # Value data should be None
        assert rec["raw_data"]["assessed_value"] is None
        assert rec["raw_data"]["homestead_exempt"] is False

    def test_transform_to_source_records(
        self, connector: CollierPAConnector, tmp_path: Path
    ) -> None:
        """to_source_records() should produce valid SourceRecord instances."""
        _write_csv_files(
            tmp_path,
            parcels=DEFAULT_PARCELS,
            sales=DEFAULT_SALES,
            values=DEFAULT_VALUES,
        )

        paths = {
            PARCELS_FILE: tmp_path / PARCELS_FILE,
            SALES_FILE: tmp_path / SALES_FILE,
            VALUES_FILE: tmp_path / VALUES_FILE,
        }
        raw_records = connector._load_and_join(paths)
        source_records = connector.to_source_records(raw_records)

        assert len(source_records) == 2
        assert all(isinstance(sr, SourceRecord) for sr in source_records)

        sr_a = next(sr for sr in source_records if sr.parcel_id == "00123456789")
        assert sr_a.source_name == "collier_pa"
        assert sr_a.record_type == "property_assessment"
        assert sr_a.city == "NAPLES"
        assert sr_a.state == "FL"
        assert sr_a.zip_code == "34102"


class TestHealthCheck:
    """Tests for the health_check and health_check_detailed methods."""

    async def test_health_check_healthy(self, tmp_path: Path) -> None:
        """health_check() returns True when all URLs respond 200."""

        async def ok_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200)

        transport = httpx.MockTransport(ok_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = CollierPAConnector(
            download_dir=tmp_path,
            config=SAMPLE_CONFIG,
            http_client=client,
        )
        result = await conn.health_check()
        assert result is True

        detail = await conn.health_check_detailed()
        assert detail["status"] == "healthy"
        assert detail["urls_checked"] == 3
        for _url, code in detail["response_codes"].items():
            assert code == 200

        await client.aclose()

    async def test_health_check_unhealthy(self, tmp_path: Path) -> None:
        """health_check() returns False when a URL responds with 500."""

        async def error_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500)

        transport = httpx.MockTransport(error_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = CollierPAConnector(
            download_dir=tmp_path,
            config=SAMPLE_CONFIG,
            http_client=client,
        )
        result = await conn.health_check()
        assert result is False

        detail = await conn.health_check_detailed()
        assert detail["status"] == "unhealthy"
        assert detail["urls_checked"] == 3
        for _url, code in detail["response_codes"].items():
            assert code == 500

        await client.aclose()

    async def test_health_check_partial_failure(self, tmp_path: Path) -> None:
        """health_check() returns False if even one URL is unreachable."""

        async def mixed_handler(request: httpx.Request) -> httpx.Response:
            url_str = str(request.url)
            if PARCELS_FILE in url_str:
                return httpx.Response(200)
            if SALES_FILE in url_str:
                return httpx.Response(200)
            # Values returns 404
            return httpx.Response(404)

        transport = httpx.MockTransport(mixed_handler)
        client = httpx.AsyncClient(transport=transport)

        conn = CollierPAConnector(
            download_dir=tmp_path,
            config=SAMPLE_CONFIG,
            http_client=client,
        )
        result = await conn.health_check()
        assert result is False

        detail = await conn.health_check_detailed()
        assert detail["status"] == "unhealthy"

        await client.aclose()


class TestHelpers:
    """Tests for module-level parsing helpers."""

    def test_parse_float_valid(self) -> None:
        """_parse_float parses clean and formatted numbers."""
        assert _parse_float("350000") == 350000.0
        assert _parse_float("1,250,000") == 1250000.0
        assert _parse_float("$450,000.50") == 450000.50
        assert _parse_float("0") == 0.0

    def test_parse_float_empty(self) -> None:
        """_parse_float returns None for empty/blank strings."""
        assert _parse_float("") is None
        assert _parse_float("   ") is None

    def test_parse_float_invalid(self) -> None:
        """_parse_float returns None for non-numeric strings."""
        assert _parse_float("N/A") is None
        assert _parse_float("abc") is None

    def test_parse_date_valid(self) -> None:
        """_parse_date parses common date formats."""
        from datetime import date

        assert _parse_date("01/15/2020") == date(2020, 1, 15)
        assert _parse_date("2020-01-15") == date(2020, 1, 15)
        assert _parse_date("06/01/2019") == date(2019, 6, 1)

    def test_parse_date_empty(self) -> None:
        """_parse_date returns None for empty strings."""
        assert _parse_date("") is None
        assert _parse_date("   ") is None

    def test_parse_date_invalid(self) -> None:
        """_parse_date returns None for unparseable strings."""
        assert _parse_date("not-a-date") is None

    def test_load_pa_config(self, tmp_path: Path) -> None:
        """load_pa_config reads and parses YAML correctly."""
        import yaml

        config_path = tmp_path / "pa_fields.yaml"
        config_path.write_text(
            yaml.dump(SAMPLE_CONFIG), encoding="utf-8"
        )
        loaded = load_pa_config(config_path)
        assert "collier" in loaded
        assert loaded["collier"]["source_name"] == "collier_pa"


class TestAbsenteeDetection:
    """Focused tests for absentee owner detection logic."""

    def test_same_address_not_absentee(
        self, connector: CollierPAConnector
    ) -> None:
        """Identical site and mail addresses should NOT be absentee."""
        record = {
            "SITE_ADDR": "100 MAIN ST",
            "SITE_CITY": "NAPLES",
            "SITE_STATE": "FL",
            "SITE_ZIP": "34102",
            "MAIL_ADDR": "100 MAIN ST",
            "MAIL_CITY": "NAPLES",
            "MAIL_STATE": "FL",
            "MAIL_ZIP": "34102",
        }
        assert connector._detect_absentee(record) is False

    def test_different_address_is_absentee(
        self, connector: CollierPAConnector
    ) -> None:
        """Different site and mail addresses should be absentee."""
        record = {
            "SITE_ADDR": "200 PALM AVE",
            "SITE_CITY": "NAPLES",
            "SITE_STATE": "FL",
            "SITE_ZIP": "34103",
            "MAIL_ADDR": "PO BOX 999",
            "MAIL_CITY": "NEW YORK",
            "MAIL_STATE": "NY",
            "MAIL_ZIP": "10001",
        }
        assert connector._detect_absentee(record) is True

    def test_missing_addresses_not_absentee(
        self, connector: CollierPAConnector
    ) -> None:
        """Missing address fields should default to not absentee."""
        record = {
            "SITE_ADDR": "",
            "MAIL_ADDR": "",
        }
        assert connector._detect_absentee(record) is False

    def test_case_insensitive_comparison(
        self, connector: CollierPAConnector
    ) -> None:
        """Address comparison should be case-insensitive."""
        record = {
            "SITE_ADDR": "100 Main St",
            "SITE_CITY": "naples",
            "SITE_STATE": "fl",
            "SITE_ZIP": "34102",
            "MAIL_ADDR": "100 MAIN ST",
            "MAIL_CITY": "NAPLES",
            "MAIL_STATE": "FL",
            "MAIL_ZIP": "34102",
        }
        assert connector._detect_absentee(record) is False


class TestHomesteadDetection:
    """Focused tests for homestead exemption detection logic."""

    def test_numeric_exemption_is_homestead(
        self, connector: CollierPAConnector
    ) -> None:
        """Non-zero HOMESTEAD value means homestead exempt."""
        record = {"HOMESTEAD": "50000"}
        assert connector._detect_homestead(record) is True

    def test_zero_exemption_not_homestead(
        self, connector: CollierPAConnector
    ) -> None:
        """HOMESTEAD = 0 means NOT homestead exempt."""
        record = {"HOMESTEAD": "0"}
        assert connector._detect_homestead(record) is False

    def test_yes_flag_is_homestead(
        self, connector: CollierPAConnector
    ) -> None:
        """HOMESTEAD = 'Y' or 'YES' means homestead exempt."""
        assert connector._detect_homestead({"HOMESTEAD": "Y"}) is True
        assert connector._detect_homestead({"HOMESTEAD": "YES"}) is True
        assert connector._detect_homestead({"HOMESTEAD": "True"}) is True

    def test_empty_not_homestead(
        self, connector: CollierPAConnector
    ) -> None:
        """Empty HOMESTEAD field means NOT homestead exempt."""
        assert connector._detect_homestead({"HOMESTEAD": ""}) is False
        assert connector._detect_homestead({}) is False
