"""Property Appraiser data connectors for Collier and Lee counties.

Collier County:
    Downloads bulk property data CSV files from collierappraiser.com,
    joins on PARCELID, and produces SourceRecords with parcel enrichment data.

Lee County:
    Downloads ZIP archives from leepa.org containing NAL (Name-Address-Legal)
    fixed-width files, parses them, joins on STRAP identifier, and produces
    SourceRecords with the same enrichment data.

Detects:
- Absentee owners (property address != mailing address)
- Homestead exemption status
- High equity (assessed value vs last sale price)

All downloads use httpx streaming to handle large files (50-100MB).

IMPORTANT: Never log owner names or addresses (PII).
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from datetime import date, datetime
from pathlib import Path
from typing import Any

import httpx
import structlog
import yaml

from theleadedge.models.source_record import SourceRecord
from theleadedge.sources.base import DataSourceConnector
from theleadedge.utils.nal_parser import (
    NalFieldSpec,
    load_nal_field_specs,
    parse_nal_file,
)

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://www.collierappraiser.com/Downloads"
PARCELS_FILE = "Parcels.csv"
SALES_FILE = "Sales.csv"
VALUES_FILE = "Values.csv"

_ALL_FILES = [PARCELS_FILE, SALES_FILE, VALUES_FILE]

# Chunk size for streaming downloads (64 KB)
_DOWNLOAD_CHUNK_SIZE = 65_536


class CollierPAFieldConfig:
    """Parsed field mappings from ``config/pa_fields.yaml`` for Collier County.

    Provides lookup dicts that map internal names to raw CSV column headers
    for each of the three data files.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        collier: dict[str, Any] = config.get("collier", config)
        self.source_name: str = collier.get("source_name", "collier_pa")

        # Build internal -> raw header lookups per file type
        self.parcels: dict[str, str] = collier.get("parcels", {})
        self.sales: dict[str, str] = collier.get("sales", {})
        self.values: dict[str, str] = collier.get("values", {})

    def _col(self, mapping: dict[str, str], internal: str) -> str:
        """Return the raw column header for an internal field name."""
        return mapping.get(internal, internal.upper())


class CollierPAConnector(DataSourceConnector):
    """Data source connector for Collier County Property Appraiser bulk data.

    Downloads three CSV files (Parcels, Sales, Values), joins them on
    PARCEL_ID, and produces ``SourceRecord`` instances enriched with
    assessment data, absentee detection, and homestead status.

    Parameters
    ----------
    download_dir:
        Local directory where downloaded CSV files are saved.
    config:
        Parsed YAML dict from ``config/pa_fields.yaml`` (the full document
        or just the ``collier`` section).
    http_client:
        Optional pre-configured ``httpx.AsyncClient`` for testing / reuse.
    """

    source_name = "collier_pa"

    def __init__(
        self,
        download_dir: Path,
        config: dict[str, Any],
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(name=self.source_name)
        self.download_dir = download_dir
        self._field_config = CollierPAFieldConfig(config)
        self._http_client = http_client

    # ------------------------------------------------------------------
    # DataSourceConnector interface
    # ------------------------------------------------------------------

    async def authenticate(self) -> None:
        """No authentication required for public downloads.

        Creates the download directory if it does not exist.
        """
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.log.info("authenticate_ok", download_dir=str(self.download_dir))

    async def fetch(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Download the three bulk CSV files and return raw joined records.

        Parameters
        ----------
        since:
            Ignored for bulk downloads (always full sync).
        **filters:
            Not used.

        Returns
        -------
        list[dict]
            Raw joined records ready for ``transform()``.
        """
        paths = await self._download_files()
        return self._load_and_join(paths)

    def transform(self, raw_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform raw joined records into SourceRecord-compatible dicts.

        Each record gets:
        - ``is_absentee``: site address differs from mailing address
        - ``homestead_exempt``: homestead exemption flag is set
        - Assessment and sale data included in ``raw_data``

        Returns
        -------
        list[dict]
            Dicts that can be used to construct ``SourceRecord`` instances.
        """
        results: list[dict[str, Any]] = []
        pc = self._field_config.parcels
        sc = self._field_config.sales
        vc = self._field_config.values

        for record in raw_records:
            parcel_id = record.get(pc.get("parcel_id", "PARCEL_ID"), "")
            if not parcel_id:
                continue

            # Parse sale data
            raw_sale_price = record.get(sc.get("sale_price", "SALE_PRICE"), "")
            sale_price = _parse_float(raw_sale_price)
            raw_sale_date = record.get(sc.get("sale_date", "SALE_DATE"), "")
            sale_date = _parse_date(raw_sale_date)

            # Parse values data
            raw_assessed = record.get(vc.get("assessed_value", "ASSESSED_VALUE"), "")
            assessed_value = _parse_float(raw_assessed)
            homestead_exempt = self._detect_homestead(record)

            # Absentee detection
            is_absentee = self._detect_absentee(record)

            # Use code
            use_code = record.get(pc.get("use_code", "USE_CODE"), "")

            # Build address (do NOT log this -- PII)
            site_addr = record.get(pc.get("site_address", "SITE_ADDR"), "")
            site_city = record.get(pc.get("site_city", "SITE_CITY"), "")
            site_state = record.get(pc.get("site_state", "SITE_STATE"), "FL")
            site_zip = record.get(pc.get("site_zip", "SITE_ZIP"), "")

            # Owner / mailing (PII -- stored but NEVER logged)
            owner_name = record.get(pc.get("owner_name", "OWNER_NAME"), "")
            mail_addr = record.get(pc.get("mail_address", "MAIL_ADDR"), "")
            mail_city = record.get(pc.get("mail_city", "MAIL_CITY"), "")
            mail_state = record.get(pc.get("mail_state", "MAIL_STATE"), "")
            mail_zip = record.get(pc.get("mail_zip", "MAIL_ZIP"), "")

            mailing_full = " ".join(
                filter(None, [mail_addr, mail_city, mail_state, mail_zip])
            )

            raw_data: dict[str, Any] = {
                "assessed_value": assessed_value,
                "homestead_exempt": homestead_exempt,
                "last_sale_date": str(sale_date) if sale_date else None,
                "last_sale_price": sale_price,
                "property_use_code": use_code,
                "is_absentee": is_absentee,
            }

            # Include market value if present
            raw_market = record.get(vc.get("market_value", "MARKET_VALUE"), "")
            market_value = _parse_float(raw_market)
            if market_value is not None:
                raw_data["market_value"] = market_value

            # Include taxable value if present
            raw_taxable = record.get(vc.get("taxable_value", "TAXABLE_VALUE"), "")
            taxable_value = _parse_float(raw_taxable)
            if taxable_value is not None:
                raw_data["taxable_value"] = taxable_value

            results.append({
                "source_name": self.source_name,
                "source_record_id": str(parcel_id),
                "record_type": "property_assessment",
                "parcel_id": str(parcel_id),
                "street_address": site_addr or None,
                "city": site_city or None,
                "state": site_state or "FL",
                "zip_code": site_zip or None,
                "event_date": sale_date,
                "event_type": "assessment",
                "raw_data": raw_data,
                "owner_name": owner_name or None,
                "mailing_address": mailing_full or None,
            })

        self.log.info(
            "transform_complete",
            total_input=len(raw_records),
            records_produced=len(results),
        )
        return results

    async def health_check(self) -> bool:
        """Check that the Collier PA download URLs are accessible.

        Sends HEAD requests to each file URL.  Returns ``True`` if all
        respond with 2xx, ``False`` otherwise.
        """
        result = await self.health_check_detailed()
        return result.get("status") == "healthy"

    # ------------------------------------------------------------------
    # Extended health check (returns detail dict)
    # ------------------------------------------------------------------

    async def health_check_detailed(self) -> dict[str, Any]:
        """Detailed health check with per-URL status codes.

        Returns
        -------
        dict
            ``{"status": "healthy"|"unhealthy", "urls_checked": int,
            "response_codes": {url: code, ...}}``
        """
        response_codes: dict[str, int] = {}
        all_ok = True

        client = self._http_client or httpx.AsyncClient(
            follow_redirects=True, timeout=30
        )
        should_close = self._http_client is None

        try:
            for filename in _ALL_FILES:
                url = f"{BASE_URL}/{filename}"
                try:
                    resp = await client.head(url)
                    response_codes[url] = resp.status_code
                    if resp.status_code >= 400:
                        all_ok = False
                except httpx.HTTPError:
                    response_codes[url] = 0
                    all_ok = False
        finally:
            if should_close:
                await client.aclose()

        status = "healthy" if all_ok else "unhealthy"
        self.log.info(
            "health_check",
            status=status,
            urls_checked=len(_ALL_FILES),
        )
        return {
            "status": status,
            "urls_checked": len(_ALL_FILES),
            "response_codes": response_codes,
        }

    # ------------------------------------------------------------------
    # Sync helper: transform to SourceRecord objects
    # ------------------------------------------------------------------

    def to_source_records(
        self, raw_records: list[dict[str, Any]]
    ) -> list[SourceRecord]:
        """Transform raw joined records into SourceRecord Pydantic instances.

        Convenience wrapper around ``transform()`` that produces actual
        ``SourceRecord`` objects instead of plain dicts.
        """
        dicts = self.transform(raw_records)
        return [SourceRecord(**d) for d in dicts]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _download_files(self) -> dict[str, Path]:
        """Download the three CSV files via httpx streaming.

        Returns
        -------
        dict[str, Path]
            Mapping from filename (``"Parcels.csv"``, etc.) to local path.

        Raises
        ------
        httpx.HTTPStatusError
            If any download returns a non-2xx response.
        """
        self.download_dir.mkdir(parents=True, exist_ok=True)
        paths: dict[str, Path] = {}

        client = self._http_client or httpx.AsyncClient(
            follow_redirects=True, timeout=300
        )
        should_close = self._http_client is None

        try:
            for filename in _ALL_FILES:
                url = f"{BASE_URL}/{filename}"
                dest = self.download_dir / filename
                self.log.info(
                    "download_start",
                    file=filename,
                )
                try:
                    async with client.stream("GET", url) as resp:
                        resp.raise_for_status()
                        with open(dest, "wb") as f:
                            async for chunk in resp.aiter_bytes(
                                chunk_size=_DOWNLOAD_CHUNK_SIZE
                            ):
                                f.write(chunk)
                    paths[filename] = dest
                    self.log.info(
                        "download_complete",
                        file=filename,
                        size_bytes=dest.stat().st_size,
                    )
                except httpx.HTTPError as exc:
                    self.log.error(
                        "download_failed",
                        file=filename,
                        error=str(exc),
                    )
                    raise
        finally:
            if should_close:
                await client.aclose()

        return paths

    def _load_and_join(self, paths: dict[str, Path]) -> list[dict[str, Any]]:
        """Read and join the three CSV files on PARCEL_ID.

        Parameters
        ----------
        paths:
            Mapping of filename to local Path (from ``_download_files``).

        Returns
        -------
        list[dict]
            Joined records with columns from all three files.
        """
        parcels_path = paths.get(PARCELS_FILE)
        sales_path = paths.get(SALES_FILE)
        values_path = paths.get(VALUES_FILE)

        parcels = self._read_csv(parcels_path) if parcels_path else []
        sales = self._read_csv(sales_path) if sales_path else []
        values = self._read_csv(values_path) if values_path else []

        return self._join_data(parcels, sales, values)

    def _read_csv(self, path: Path) -> list[dict[str, str]]:
        """Read a CSV file with encoding fallback (UTF-8, then CP-1252).

        Parameters
        ----------
        path:
            Path to the CSV file.

        Returns
        -------
        list[dict[str, str]]
            Rows as dictionaries keyed by column headers.
        """
        encodings = ["utf-8", "cp1252"]
        for encoding in encodings:
            try:
                with open(path, encoding=encoding, newline="") as f:
                    content = f.read()
                reader = csv.DictReader(io.StringIO(content))
                rows = list(reader)
                self.log.info(
                    "csv_read",
                    file=path.name,
                    row_count=len(rows),
                    encoding=encoding,
                )
                return rows
            except UnicodeDecodeError:
                continue
        self.log.error(
            "csv_decode_failed",
            file=path.name,
        )
        return []

    def _join_data(
        self,
        parcels: list[dict[str, str]],
        sales: list[dict[str, str]],
        values: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        """Join parcels, sales, and values on PARCEL_ID.

        Sales and values are matched to parcels by parcel ID.  For sales,
        the most recent sale (by date) is used.  If a parcel has no sales
        or values data, the parcel record is still included with empty
        sale/value fields.

        Parameters
        ----------
        parcels:
            Rows from Parcels.csv.
        sales:
            Rows from Sales.csv.
        values:
            Rows from Values.csv.

        Returns
        -------
        list[dict]
            Merged records.
        """
        pc = self._field_config.parcels
        sc = self._field_config.sales
        vc = self._field_config.values

        parcel_id_col = pc.get("parcel_id", "PARCEL_ID")
        sale_parcel_col = sc.get("parcel_id", "PARCEL_ID")
        value_parcel_col = vc.get("parcel_id", "PARCEL_ID")

        # Build lookup: parcel_id -> most recent sale record
        sales_by_parcel: dict[str, dict[str, str]] = {}
        sale_date_col = sc.get("sale_date", "SALE_DATE")
        for row in sales:
            pid = row.get(sale_parcel_col, "").strip()
            if not pid:
                continue
            existing = sales_by_parcel.get(pid)
            if existing is None:
                sales_by_parcel[pid] = row
            else:
                # Keep the more recent sale
                existing_date = _parse_date(existing.get(sale_date_col, ""))
                current_date = _parse_date(row.get(sale_date_col, ""))
                if current_date and (
                    existing_date is None or current_date > existing_date
                ):
                    sales_by_parcel[pid] = row

        # Build lookup: parcel_id -> values record
        values_by_parcel: dict[str, dict[str, str]] = {}
        for row in values:
            pid = row.get(value_parcel_col, "").strip()
            if pid:
                values_by_parcel[pid] = row

        # Join
        joined: list[dict[str, Any]] = []
        for parcel in parcels:
            pid = parcel.get(parcel_id_col, "").strip()
            if not pid:
                continue

            merged: dict[str, Any] = dict(parcel)

            sale_row = sales_by_parcel.get(pid, {})
            for key, val in sale_row.items():
                if key != sale_parcel_col:
                    merged[key] = val

            value_row = values_by_parcel.get(pid, {})
            for key, val in value_row.items():
                if key != value_parcel_col:
                    merged[key] = val

            joined.append(merged)

        self.log.info(
            "join_complete",
            parcels=len(parcels),
            sales_matched=sum(
                1 for p in parcels
                if p.get(parcel_id_col, "").strip() in sales_by_parcel
            ),
            values_matched=sum(
                1 for p in parcels
                if p.get(parcel_id_col, "").strip() in values_by_parcel
            ),
            joined=len(joined),
        )
        return joined

    def _detect_absentee(self, record: dict[str, Any]) -> bool:
        """Detect absentee owner by comparing site and mailing addresses.

        An owner is absentee when their mailing address differs from the
        property site address.  Comparison is case-insensitive and
        whitespace-normalized.

        Returns ``False`` if either address is missing.
        """
        pc = self._field_config.parcels
        site_addr = str(record.get(pc.get("site_address", "SITE_ADDR"), "")).strip()
        mail_addr = str(record.get(pc.get("mail_address", "MAIL_ADDR"), "")).strip()

        if not site_addr or not mail_addr:
            return False

        # Also compare city + state + zip for full picture
        site_city = str(record.get(pc.get("site_city", "SITE_CITY"), "")).strip()
        site_zip = str(record.get(pc.get("site_zip", "SITE_ZIP"), "")).strip()
        mail_city = str(record.get(pc.get("mail_city", "MAIL_CITY"), "")).strip()
        mail_zip = str(record.get(pc.get("mail_zip", "MAIL_ZIP"), "")).strip()

        # Normalize for comparison
        site_full = _normalize_for_compare(f"{site_addr} {site_city} {site_zip}")
        mail_full = _normalize_for_compare(f"{mail_addr} {mail_city} {mail_zip}")

        return site_full != mail_full

    def _detect_homestead(self, record: dict[str, Any]) -> bool:
        """Detect homestead exemption from value data.

        Checks the homestead field for truthy values.  Common encodings:
        ``"Y"``, ``"YES"``, ``"1"``, ``"True"``, or a non-zero numeric
        value representing the exemption amount.
        """
        vc = self._field_config.values
        raw = str(record.get(vc.get("homestead_exempt", "HOMESTEAD"), "")).strip()

        if not raw:
            return False

        # Check common boolean-like values
        if raw.upper() in ("Y", "YES", "1", "TRUE", "X"):
            return True

        # Check for numeric exemption amount > 0
        try:
            return float(raw.replace(",", "").replace("$", "")) > 0
        except (ValueError, OverflowError):
            return False


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _parse_float(raw: str) -> float | None:
    """Parse a string to float, handling currency and comma formatting."""
    if not raw:
        return None
    cleaned = str(raw).strip().replace(",", "").replace("$", "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except (ValueError, OverflowError):
        return None


def _parse_date(raw: str) -> date | None:
    """Parse a date string trying common formats."""
    if not raw:
        return None
    stripped = str(raw).strip()
    if not stripped:
        return None

    formats = [
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%m-%d-%Y",
        "%m/%d/%y",
        "%Y/%m/%d",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(stripped, fmt).date()
        except ValueError:
            continue
    return None


def _normalize_for_compare(text: str) -> str:
    """Normalize an address string for comparison.

    Lowercases, strips excess whitespace, removes punctuation.
    """
    normalized = text.lower().strip()
    normalized = re.sub(r"[^\w\s]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def load_pa_config(config_path: Path) -> dict[str, Any]:
    """Load the Property Appraiser field configuration from YAML.

    Parameters
    ----------
    config_path:
        Path to ``config/pa_fields.yaml``.

    Returns
    -------
    dict
        Parsed YAML as a dict.
    """
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ---------------------------------------------------------------------------
# Lee County Property Appraiser (NAL fixed-width format)
# ---------------------------------------------------------------------------

# Default NAL field positions for Lee County (FL DOR standard).
LEE_NAL_FIELDS: list[NalFieldSpec] = [
    NalFieldSpec("strap", 0, 18),
    NalFieldSpec("owner_name_1", 18, 58),
    NalFieldSpec("owner_name_2", 58, 98),
    NalFieldSpec("mail_addr_1", 98, 138),
    NalFieldSpec("mail_addr_2", 138, 178),
    NalFieldSpec("mail_city", 178, 203),
    NalFieldSpec("mail_state", 203, 205),
    NalFieldSpec("mail_zip", 205, 214),
    NalFieldSpec("site_addr", 214, 254),
    NalFieldSpec("site_city", 254, 279),
    NalFieldSpec("site_zip", 279, 284),
    NalFieldSpec("use_code", 284, 288),
    NalFieldSpec("assessed_value", 288, 300, "float"),
    NalFieldSpec("homestead", 300, 301),
    NalFieldSpec("taxable_value", 301, 313, "float"),
]

LEE_SDF_FIELDS: list[NalFieldSpec] = [
    NalFieldSpec("strap", 0, 18),
    NalFieldSpec("sale_date", 18, 26),
    NalFieldSpec("sale_price", 26, 38, "float"),
    NalFieldSpec("deed_type", 38, 40),
    NalFieldSpec("qualified", 40, 41),
]

# Chunk size for streaming downloads (64 KB)
_LEE_DOWNLOAD_CHUNK_SIZE = 65_536


class LeePAConnector(DataSourceConnector):
    """Lee County Property Appraiser connector (NAL fixed-width format).

    Downloads ZIP archives from Lee County PA, extracts NAL/SDF files,
    parses fixed-width records, and joins on STRAP (Situs/Tax Roll
    Assessment Parcel) identifier.

    Parameters
    ----------
    download_dir:
        Local directory where downloaded/extracted files are saved.
    config:
        Parsed YAML dict from ``config/pa_fields.yaml`` (the full document
        or just the ``lee`` section).
    http_client:
        Optional pre-configured ``httpx.AsyncClient`` for testing / reuse.
    """

    source_name = "lee_pa"

    # Lee County PA download URLs (public bulk data)
    BASE_URL = "https://www.leepa.org/Downloads"
    NAL_FILE = "NAL.zip"
    SDF_FILE = "SDF.zip"

    _ALL_ZIP_FILES = [NAL_FILE, SDF_FILE]

    def __init__(
        self,
        download_dir: Path,
        config: dict[str, Any],
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(name=self.source_name)
        self.download_dir = download_dir
        self._http_client = http_client

        # Load field specs from config or fall back to hardcoded defaults
        lee_config = config.get("lee", config)
        nal_section = lee_config.get("nal_fields")
        sdf_section = lee_config.get("sdf_fields")
        self._nal_fields = (
            load_nal_field_specs(nal_section) if nal_section else LEE_NAL_FIELDS
        )
        self._sdf_fields = (
            load_nal_field_specs(sdf_section) if sdf_section else LEE_SDF_FIELDS
        )

    # ------------------------------------------------------------------
    # DataSourceConnector interface
    # ------------------------------------------------------------------

    async def authenticate(self) -> None:
        """No authentication required for public downloads.

        Creates the download directory if it does not exist.
        """
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.log.info("authenticate_ok", download_dir=str(self.download_dir))

    async def fetch(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Download ZIP files, extract, and return raw joined records.

        Parameters
        ----------
        since:
            Ignored for bulk downloads (always full sync).
        **filters:
            Not used.

        Returns
        -------
        list[dict]
            Raw joined records ready for ``transform()``.
        """
        zip_paths = await self._download_zips()
        extracted = self._extract_all_zips(zip_paths)
        return self._load_and_join(extracted)

    def transform(self, raw_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform raw joined records into SourceRecord-compatible dicts.

        Each record gets:
        - ``is_absentee``: site address differs from mailing address
        - ``homestead_exempt``: homestead flag is ``"Y"``
        - Assessment and sale data included in ``raw_data``

        Returns
        -------
        list[dict]
            Dicts that can be used to construct ``SourceRecord`` instances.
        """
        results: list[dict[str, Any]] = []

        for record in raw_records:
            strap = record.get("strap")
            if not strap:
                continue

            # Parse sale data
            sale_price = record.get("sale_price")  # already float or None
            sale_date = self._parse_sale_date(record.get("sale_date"))

            # Assessment data
            assessed_value = record.get("assessed_value")  # already float or None
            taxable_value = record.get("taxable_value")  # already float or None
            homestead_exempt = self._detect_homestead(record)

            # Absentee detection
            is_absentee = self._detect_absentee(record)

            # Use code
            use_code = record.get("use_code") or ""

            # Address fields (PII -- stored but NEVER logged)
            site_addr = record.get("site_addr") or ""
            site_city = record.get("site_city") or ""
            site_zip = record.get("site_zip") or ""

            # Owner / mailing (PII -- stored but NEVER logged)
            owner_1 = record.get("owner_name_1") or ""
            owner_2 = record.get("owner_name_2") or ""
            owner_name = " ".join(filter(None, [owner_1, owner_2])).strip()

            mail_1 = record.get("mail_addr_1") or ""
            mail_2 = record.get("mail_addr_2") or ""
            mail_city = record.get("mail_city") or ""
            mail_state = record.get("mail_state") or ""
            mail_zip = record.get("mail_zip") or ""
            mailing_full = " ".join(
                filter(None, [mail_1, mail_2, mail_city, mail_state, mail_zip])
            )

            raw_data: dict[str, Any] = {
                "assessed_value": assessed_value,
                "homestead_exempt": homestead_exempt,
                "last_sale_date": str(sale_date) if sale_date else None,
                "last_sale_price": sale_price,
                "property_use_code": use_code,
                "is_absentee": is_absentee,
            }

            if taxable_value is not None:
                raw_data["taxable_value"] = taxable_value

            # Deed type from SDF
            deed_type = record.get("deed_type")
            if deed_type:
                raw_data["deed_type"] = deed_type

            results.append({
                "source_name": self.source_name,
                "source_record_id": str(strap),
                "record_type": "property_assessment",
                "parcel_id": str(strap),
                "street_address": site_addr or None,
                "city": site_city or None,
                "state": "FL",
                "zip_code": site_zip or None,
                "event_date": sale_date,
                "event_type": "assessment",
                "raw_data": raw_data,
                "owner_name": owner_name or None,
                "mailing_address": mailing_full or None,
            })

        self.log.info(
            "transform_complete",
            total_input=len(raw_records),
            records_produced=len(results),
        )
        return results

    async def health_check(self) -> bool:
        """Check that the Lee PA download URLs are accessible.

        Sends HEAD requests to each ZIP file URL.  Returns ``True`` if all
        respond with 2xx, ``False`` otherwise.
        """
        result = await self.health_check_detailed()
        return result.get("status") == "healthy"

    # ------------------------------------------------------------------
    # Extended health check (returns detail dict)
    # ------------------------------------------------------------------

    async def health_check_detailed(self) -> dict[str, Any]:
        """Detailed health check with per-URL status codes.

        Returns
        -------
        dict
            ``{"status": "healthy"|"unhealthy", "urls_checked": int,
            "response_codes": {url: code, ...}}``
        """
        response_codes: dict[str, int] = {}
        all_ok = True

        client = self._http_client or httpx.AsyncClient(
            follow_redirects=True, timeout=30
        )
        should_close = self._http_client is None

        try:
            for filename in self._ALL_ZIP_FILES:
                url = f"{self.BASE_URL}/{filename}"
                try:
                    resp = await client.head(url)
                    response_codes[url] = resp.status_code
                    if resp.status_code >= 400:
                        all_ok = False
                except httpx.HTTPError:
                    response_codes[url] = 0
                    all_ok = False
        finally:
            if should_close:
                await client.aclose()

        status = "healthy" if all_ok else "unhealthy"
        self.log.info(
            "health_check",
            status=status,
            urls_checked=len(self._ALL_ZIP_FILES),
        )
        return {
            "status": status,
            "urls_checked": len(self._ALL_ZIP_FILES),
            "response_codes": response_codes,
        }

    # ------------------------------------------------------------------
    # Sync helper: transform to SourceRecord objects
    # ------------------------------------------------------------------

    def to_source_records(
        self, raw_records: list[dict[str, Any]]
    ) -> list[SourceRecord]:
        """Transform raw joined records into SourceRecord Pydantic instances.

        Convenience wrapper around ``transform()`` that produces actual
        ``SourceRecord`` objects instead of plain dicts.
        """
        dicts = self.transform(raw_records)
        return [SourceRecord(**d) for d in dicts]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _download_zips(self) -> dict[str, Path]:
        """Download the ZIP files via httpx streaming.

        Returns
        -------
        dict[str, Path]
            Mapping from filename (``"NAL.zip"``, ``"SDF.zip"``) to local path.

        Raises
        ------
        httpx.HTTPStatusError
            If any download returns a non-2xx response.
        """
        self.download_dir.mkdir(parents=True, exist_ok=True)
        paths: dict[str, Path] = {}

        client = self._http_client or httpx.AsyncClient(
            follow_redirects=True, timeout=300
        )
        should_close = self._http_client is None

        try:
            for filename in self._ALL_ZIP_FILES:
                url = f"{self.BASE_URL}/{filename}"
                dest = self.download_dir / filename
                self.log.info("download_start", file=filename)
                try:
                    async with client.stream("GET", url) as resp:
                        resp.raise_for_status()
                        with open(dest, "wb") as f:
                            async for chunk in resp.aiter_bytes(
                                chunk_size=_LEE_DOWNLOAD_CHUNK_SIZE
                            ):
                                f.write(chunk)
                    paths[filename] = dest
                    self.log.info(
                        "download_complete",
                        file=filename,
                        size_bytes=dest.stat().st_size,
                    )
                except httpx.HTTPError as exc:
                    self.log.error(
                        "download_failed",
                        file=filename,
                        error=str(exc),
                    )
                    raise
        finally:
            if should_close:
                await client.aclose()

        return paths

    def _extract_zip(self, zip_path: Path) -> list[Path]:
        """Extract a ZIP file into the download directory.

        Parameters
        ----------
        zip_path:
            Path to the ZIP archive.

        Returns
        -------
        list[Path]
            Paths of extracted files.
        """
        extracted: list[Path] = []
        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                dest = self.download_dir / member
                zf.extract(member, self.download_dir)
                extracted.append(dest)
                self.log.info(
                    "zip_extract",
                    archive=zip_path.name,
                    member=member,
                )
        return extracted

    def _extract_all_zips(
        self, zip_paths: dict[str, Path]
    ) -> dict[str, list[Path]]:
        """Extract all downloaded ZIP files.

        Returns
        -------
        dict[str, list[Path]]
            Mapping from ZIP filename to list of extracted file paths.
        """
        result: dict[str, list[Path]] = {}
        for filename, path in zip_paths.items():
            result[filename] = self._extract_zip(path)
        return result

    def _load_and_join(
        self, extracted: dict[str, list[Path]]
    ) -> list[dict[str, Any]]:
        """Parse NAL and SDF files and join on STRAP.

        Parameters
        ----------
        extracted:
            Mapping from ZIP filename to extracted file paths.

        Returns
        -------
        list[dict]
            Joined records with NAL and SDF data merged by STRAP.
        """
        # Parse NAL records from all files in the NAL zip
        nal_records: list[dict[str, Any]] = []
        for path in extracted.get(self.NAL_FILE, []):
            content = self._read_file_content(path)
            records = parse_nal_file(content, self._nal_fields)
            nal_records.extend(records)

        # Parse SDF records from all files in the SDF zip
        sdf_records: list[dict[str, Any]] = []
        for path in extracted.get(self.SDF_FILE, []):
            content = self._read_file_content(path)
            records = parse_nal_file(content, self._sdf_fields)
            sdf_records.extend(records)

        self.log.info(
            "nal_sdf_parsed",
            nal_count=len(nal_records),
            sdf_count=len(sdf_records),
        )

        # Build lookup: STRAP -> most recent SDF sale record
        sales_by_strap: dict[str, dict[str, Any]] = {}
        for row in sdf_records:
            strap = row.get("strap")
            if not strap:
                continue
            strap_str = str(strap).strip()
            existing = sales_by_strap.get(strap_str)
            if existing is None:
                sales_by_strap[strap_str] = row
            else:
                # Keep the more recent sale
                existing_date = self._parse_sale_date(existing.get("sale_date"))
                current_date = self._parse_sale_date(row.get("sale_date"))
                if current_date and (
                    existing_date is None or current_date > existing_date
                ):
                    sales_by_strap[strap_str] = row

        # Join NAL + SDF on STRAP
        joined: list[dict[str, Any]] = []
        for nal_rec in nal_records:
            strap = nal_rec.get("strap")
            if not strap:
                continue
            strap_str = str(strap).strip()

            merged: dict[str, Any] = dict(nal_rec)

            # Merge in SDF data (sales)
            sdf_row = sales_by_strap.get(strap_str, {})
            for key, val in sdf_row.items():
                if key != "strap":
                    merged[key] = val

            joined.append(merged)

        self.log.info(
            "join_complete",
            nal_records=len(nal_records),
            sales_matched=sum(
                1
                for rec in nal_records
                if str(rec.get("strap", "")).strip() in sales_by_strap
            ),
            joined=len(joined),
        )
        return joined

    def _read_file_content(self, path: Path) -> str:
        """Read a text file with encoding fallback (UTF-8, then CP-1252).

        Parameters
        ----------
        path:
            Path to the text file.

        Returns
        -------
        str
            File content as a string.
        """
        encodings = ["utf-8", "cp1252"]
        for encoding in encodings:
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        self.log.error("file_decode_failed", file=path.name)
        return ""

    @staticmethod
    def _parse_sale_date(date_str: str | None) -> date | None:
        """Parse a sale date in MMDDYYYY format.

        Lee County SDF files use 8-digit date format: MMDDYYYY.

        Parameters
        ----------
        date_str:
            Raw date string, e.g. ``"01152020"`` for January 15, 2020.

        Returns
        -------
        date or None
            Parsed date, or ``None`` if invalid or empty.
        """
        if not date_str:
            return None
        cleaned = str(date_str).strip()
        if not cleaned or len(cleaned) != 8:
            return None
        try:
            return datetime.strptime(cleaned, "%m%d%Y").date()
        except ValueError:
            return None

    @staticmethod
    def _detect_absentee(record: dict[str, Any]) -> bool:
        """Detect absentee owner by comparing site and mailing addresses.

        An owner is absentee when their mailing address differs from the
        property site address.  Comparison is case-insensitive and
        whitespace-normalized.

        Returns ``False`` if either address is missing.
        """
        site_addr = str(record.get("site_addr") or "").strip()
        mail_addr = str(record.get("mail_addr_1") or "").strip()

        if not site_addr or not mail_addr:
            return False

        site_city = str(record.get("site_city") or "").strip()
        site_zip = str(record.get("site_zip") or "").strip()
        mail_city = str(record.get("mail_city") or "").strip()
        mail_zip = str(record.get("mail_zip") or "").strip()

        site_full = _normalize_for_compare(f"{site_addr} {site_city} {site_zip}")
        mail_full = _normalize_for_compare(f"{mail_addr} {mail_city} {mail_zip}")

        return site_full != mail_full

    @staticmethod
    def _detect_homestead(record: dict[str, Any]) -> bool:
        """Detect homestead exemption from NAL homestead flag.

        Lee County NAL uses a single-character field: ``"Y"`` for
        homestead, anything else for non-homestead.
        """
        raw = str(record.get("homestead") or "").strip().upper()
        return raw == "Y"
