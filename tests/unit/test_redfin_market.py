"""Unit tests for the Redfin market data connector.

Tests cover gzipped TSV download (mocked HTTP), ZIP code filtering,
absorption rate calculation, field parsing, and health checks.

All test data is synthetic -- no real market data.
"""

from __future__ import annotations

import gzip
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from theleadedge.sources.market_data import (
    REDFIN_DATA_URL,
    RedfinMarketConnector,
    _parse_date_str,
    _parse_float,
    _parse_int,
)

# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

# Redfin TSV column headers (subset matching what the connector parses)
TSV_HEADERS = (
    "period_begin\tperiod_end\tregion\tmedian_sale_price\t"
    "median_list_price\tmedian_dom\thomes_sold\tnew_listings\t"
    "inventory\tmonths_of_supply\tsale_to_list\tprice_drops"
)


def _make_tsv_row(
    period_begin: str = "2026-01-06",
    period_end: str = "2026-01-12",
    region: str = "34102",
    median_sale_price: str = "450000",
    median_list_price: str = "475000",
    median_dom: str = "45",
    homes_sold: str = "12",
    new_listings: str = "18",
    inventory: str = "50",
    months_of_supply: str = "4.2",
    sale_to_list: str = "0.97",
    price_drops: str = "0.15",
) -> str:
    """Build a single TSV data row."""
    return (
        f"{period_begin}\t{period_end}\t{region}\t{median_sale_price}\t"
        f"{median_list_price}\t{median_dom}\t{homes_sold}\t{new_listings}\t"
        f"{inventory}\t{months_of_supply}\t{sale_to_list}\t{price_drops}"
    )


def create_mock_redfin_tsv(rows: list[str]) -> bytes:
    """Create a gzipped TSV file from header + data rows.

    Parameters
    ----------
    rows:
        List of TSV data row strings (without the header).

    Returns
    -------
    bytes
        Gzipped content.
    """
    lines = [TSV_HEADERS] + rows
    content = "\n".join(lines).encode("utf-8")
    return gzip.compress(content)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def target_zips() -> list[str]:
    """A small set of target ZIP codes for testing."""
    return ["34102", "34103", "33901"]


@pytest.fixture
def connector(tmp_path: Path, target_zips: list[str]) -> RedfinMarketConnector:
    """Create a RedfinMarketConnector with test settings."""
    return RedfinMarketConnector(
        download_dir=tmp_path,
        target_zip_codes=target_zips,
    )


# ---------------------------------------------------------------------------
# Test: fetch downloads gzipped file
# ---------------------------------------------------------------------------


class TestFetch:
    """Tests for the fetch method with mocked HTTP."""

    @pytest.mark.asyncio
    async def test_fetch_downloads_gzipped_file(
        self, tmp_path: Path, target_zips: list[str]
    ) -> None:
        """Mocked HTTP streaming download writes file to download_dir."""
        tsv_data = create_mock_redfin_tsv([
            _make_tsv_row(region="34102"),
        ])

        # Build async iterator for streaming
        async def mock_aiter_bytes(chunk_size: int = 65536):
            yield tsv_data

        # Mock the streaming response context manager
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.aiter_bytes = mock_aiter_bytes

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_client = AsyncMock()
        mock_client.stream = MagicMock(return_value=mock_stream_ctx)
        mock_client.aclose = AsyncMock()

        connector = RedfinMarketConnector(
            download_dir=tmp_path,
            target_zip_codes=target_zips,
            http_client=mock_client,
        )

        result = await connector.fetch()

        assert len(result) == 1
        file_path = result[0]["file_path"]
        assert isinstance(file_path, Path)
        assert file_path.exists()
        assert file_path.name.endswith(".gz")


# ---------------------------------------------------------------------------
# Test: transform filters to target ZIPs
# ---------------------------------------------------------------------------


class TestTransform:
    """Tests for the transform method."""

    def test_transform_filters_to_target_zips(
        self, tmp_path: Path, target_zips: list[str]
    ) -> None:
        """Only rows matching target ZIP codes appear in output."""
        rows = [
            _make_tsv_row(region="34102"),  # target
            _make_tsv_row(region="90210"),  # NOT target
            _make_tsv_row(region="33901"),  # target
            _make_tsv_row(region="99999"),  # NOT target
        ]
        gz_path = tmp_path / "test.tsv.gz"
        gz_path.write_bytes(create_mock_redfin_tsv(rows))

        connector = RedfinMarketConnector(
            download_dir=tmp_path,
            target_zip_codes=target_zips,
        )
        results = connector.transform([{"file_path": gz_path}])

        assert len(results) == 2
        result_zips = {r["zip_code"] for r in results}
        assert result_zips == {"34102", "33901"}

    def test_transform_calculates_absorption_rate(
        self, tmp_path: Path, target_zips: list[str]
    ) -> None:
        """Absorption rate is calculated as homes_sold / inventory * 100."""
        rows = [
            _make_tsv_row(region="34102", homes_sold="25", inventory="100"),
        ]
        gz_path = tmp_path / "test.tsv.gz"
        gz_path.write_bytes(create_mock_redfin_tsv(rows))

        connector = RedfinMarketConnector(
            download_dir=tmp_path,
            target_zip_codes=target_zips,
        )
        results = connector.transform([{"file_path": gz_path}])

        assert len(results) == 1
        assert results[0]["absorption_rate"] == 25.0  # 25/100 * 100

    def test_transform_handles_zero_inventory(
        self, tmp_path: Path, target_zips: list[str]
    ) -> None:
        """When inventory is zero, absorption_rate should be None."""
        rows = [
            _make_tsv_row(region="34102", homes_sold="5", inventory="0"),
        ]
        gz_path = tmp_path / "test.tsv.gz"
        gz_path.write_bytes(create_mock_redfin_tsv(rows))

        connector = RedfinMarketConnector(
            download_dir=tmp_path,
            target_zip_codes=target_zips,
        )
        results = connector.transform([{"file_path": gz_path}])

        assert len(results) == 1
        assert results[0]["absorption_rate"] is None

    def test_transform_parses_tsv_fields(
        self, tmp_path: Path, target_zips: list[str]
    ) -> None:
        """All expected fields are extracted from the TSV correctly."""
        rows = [
            _make_tsv_row(
                region="34103",
                period_begin="2026-02-03",
                period_end="2026-02-09",
                median_sale_price="525000",
                median_list_price="550000",
                median_dom="62",
                homes_sold="8",
                new_listings="15",
                inventory="42",
                months_of_supply="5.3",
                sale_to_list="0.95",
                price_drops="0.22",
            ),
        ]
        gz_path = tmp_path / "test.tsv.gz"
        gz_path.write_bytes(create_mock_redfin_tsv(rows))

        connector = RedfinMarketConnector(
            download_dir=tmp_path,
            target_zip_codes=target_zips,
        )
        results = connector.transform([{"file_path": gz_path}])

        assert len(results) == 1
        r = results[0]
        assert r["zip_code"] == "34103"
        assert r["source"] == "redfin"
        assert r["median_sale_price"] == 525000.0
        assert r["median_list_price"] == 550000.0
        assert r["median_dom"] == 62
        assert r["homes_sold"] == 8
        assert r["new_listings"] == 15
        assert r["inventory"] == 42
        assert r["months_of_supply"] == 5.3
        assert r["sale_to_list_ratio"] == 0.95
        assert r["price_drops_pct"] == 0.22
        # absorption_rate = 8/42*100 = 19.05
        assert r["absorption_rate"] == pytest.approx(19.05, abs=0.01)


# ---------------------------------------------------------------------------
# Test: health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """Tests for the health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_healthy(
        self, tmp_path: Path, target_zips: list[str]
    ) -> None:
        """HEAD request returning 200 means healthy."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()

        connector = RedfinMarketConnector(
            download_dir=tmp_path,
            target_zip_codes=target_zips,
            http_client=mock_client,
        )

        result = await connector.health_check()
        assert result is True
        mock_client.head.assert_called_once_with(REDFIN_DATA_URL)

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(
        self, tmp_path: Path, target_zips: list[str]
    ) -> None:
        """HEAD request returning non-200 means unhealthy."""
        mock_response = MagicMock()
        mock_response.status_code = 403

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()

        connector = RedfinMarketConnector(
            download_dir=tmp_path,
            target_zip_codes=target_zips,
            http_client=mock_client,
        )

        result = await connector.health_check()
        assert result is False


# ---------------------------------------------------------------------------
# Test: helper functions
# ---------------------------------------------------------------------------


class TestHelpers:
    """Tests for parsing helper functions."""

    def test_parse_float_valid(self) -> None:
        assert _parse_float("123.45") == 123.45

    def test_parse_float_empty(self) -> None:
        assert _parse_float("") is None
        assert _parse_float("NA") is None

    def test_parse_int_valid(self) -> None:
        assert _parse_int("42") == 42

    def test_parse_int_float_string(self) -> None:
        assert _parse_int("42.7") == 42

    def test_parse_int_empty(self) -> None:
        assert _parse_int("") is None
        assert _parse_int("N/A") is None

    def test_parse_date_str_valid(self) -> None:
        from datetime import date
        assert _parse_date_str("2026-01-15") == date(2026, 1, 15)

    def test_parse_date_str_empty(self) -> None:
        assert _parse_date_str("") is None
