"""Property Appraiser data connectors for Collier and Lee counties.

Collier County:
    Downloads bulk property data ZIP files from collierappraiser.com via their
    ASP download handler (which 302-redirects to Google Drive), extracts the
    CSV contents, joins on PARCELID, and produces SourceRecords with parcel
    enrichment data.

    As of 2026, the download mechanism uses::

        https://www.collierappraiser.com/Main_Data/downloadgdfile.asp
            ?folderName=INT%20FILES%20(NEW)&file=<filename>.zip

    Each ZIP archive contains one or more CSV files.

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
import urllib.parse
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

# The Collier PA switched from direct CSV downloads to an ASP handler that
# 302-redirects to Google Drive.  Each download is a ZIP containing CSV(s).
BASE_URL = "https://www.collierappraiser.com/Main_Data/downloadgdfile.asp"
_DOWNLOAD_FOLDER = "INT FILES (NEW)"

# ZIP filenames served by the ASP handler (contain CSV files inside)
PARCELS_FILE = "int_parcels_csv.zip"
SALES_FILE = "int_sales_csv.zip"
VALUES_FILE = "int_values_rp_history_csv.zip"

_ALL_FILES = [PARCELS_FILE, SALES_FILE, VALUES_FILE]

# Legacy filenames kept for backward compatibility in tests and references.
# These are the names of the CSV files *inside* the ZIP archives.
PARCELS_CSV = "Parcels.csv"
SALES_CSV = "Sales.csv"
VALUES_CSV = "Values.csv"

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

        Sends HEAD requests to the ASP download handler for each file.
        The handler returns 302 redirects to Google Drive; we consider
        a 2xx or 3xx response as healthy (the redirect itself indicates
        the file is configured).

        Returns
        -------
        dict
            ``{"status": "healthy"|"unhealthy", "urls_checked": int,
            "response_codes": {url: code, ...}}``
        """
        response_codes: dict[str, int] = {}
        all_ok = True

        # For health checks we do NOT follow redirects, because the ASP
        # handler returns 302 -> Google Drive.  A 302 means the file exists.
        client = self._http_client or httpx.AsyncClient(
            follow_redirects=False, timeout=30
        )
        should_close = self._http_client is None

        try:
            for filename in _ALL_FILES:
                url = self._build_download_url(filename)
                try:
                    resp = await client.head(url)
                    response_codes[url] = resp.status_code
                    # 2xx or 3xx (redirect) both indicate the file is available
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

    @staticmethod
    def _build_download_url(filename: str) -> str:
        """Build the full ASP download URL for a given ZIP filename.

        The Collier PA serves files through an ASP handler that accepts
        ``folderName`` and ``file`` query parameters and 302-redirects
        to Google Drive for the actual download.

        Parameters
        ----------
        filename:
            ZIP filename, e.g. ``"int_parcels_csv.zip"``.

        Returns
        -------
        str
            Fully-qualified URL for the download handler.
        """
        params = urllib.parse.urlencode({
            "folderName": _DOWNLOAD_FOLDER,
            "file": filename,
        })
        return f"{BASE_URL}?{params}"

    async def _download_files(self) -> dict[str, Path]:
        """Download ZIP archives and extract their CSV contents.

        The Collier PA serves ZIP files via an ASP handler that redirects
        to Google Drive.  Google Drive returns an HTML confirmation page
        for large files instead of the actual content.  This method
        handles the confirmation by injecting ``confirm=t`` into the
        Google Drive URL.

        Each ZIP contains one or more CSV files.  This method downloads
        the ZIPs, extracts CSVs, and returns paths to the extracted CSV
        files keyed by the original ZIP filename.

        Returns
        -------
        dict[str, Path]
            Mapping from ZIP filename to local path of the extracted CSV.
            The CSV path is the first ``.csv`` file found inside each ZIP.

        Raises
        ------
        httpx.HTTPStatusError
            If any download returns a non-2xx response.
        ValueError
            If a ZIP archive contains no CSV files.
        """
        self.download_dir.mkdir(parents=True, exist_ok=True)
        paths: dict[str, Path] = {}

        client = self._http_client or httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(30.0, read=300.0),
        )
        should_close = self._http_client is None

        try:
            for filename in _ALL_FILES:
                url = self._build_download_url(filename)
                zip_dest = self.download_dir / filename
                self.log.info(
                    "download_start",
                    file=filename,
                )
                try:
                    await self._download_with_gdrive_confirm(
                        client, url, zip_dest
                    )
                    self.log.info(
                        "download_complete",
                        file=filename,
                        size_bytes=zip_dest.stat().st_size,
                    )

                    # Extract CSV from ZIP
                    csv_path = self._extract_csv_from_zip(zip_dest)
                    paths[filename] = csv_path

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

    async def _download_with_gdrive_confirm(
        self,
        client: httpx.AsyncClient,
        url: str,
        dest: Path,
    ) -> None:
        """Download a file, handling Google Drive confirmation pages.

        Google Drive serves an HTML confirmation page (with a "Download
        anyway" button) for large files instead of the actual content.
        This method detects that situation and retries with the
        ``confirm=t`` query parameter, which bypasses the interstitial.

        The detection works as follows:

        1. Follow the initial redirect from the Collier PA ASP handler
           to Google Drive.
        2. Stream the response body.  If the first chunk starts with
           ``<`` (HTML), the response is likely the confirmation page.
        3. In that case, rebuild the URL with ``confirm=t`` and retry.

        Parameters
        ----------
        client:
            An ``httpx.AsyncClient`` with ``follow_redirects=True``.
        url:
            The initial download URL (Collier PA ASP handler).
        dest:
            Local file path to write the downloaded content.
        """
        retry_url: str | None = None

        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            final_url = str(resp.url)

            # Check if we landed on Google Drive
            if "drive.google.com" not in final_url and "drive.usercontent.google.com" not in final_url:
                # Not Google Drive (e.g. test mocks) -- stream directly
                with open(dest, "wb") as f:
                    async for chunk in resp.aiter_bytes(
                        chunk_size=_DOWNLOAD_CHUNK_SIZE
                    ):
                        f.write(chunk)
                return

            # Google Drive URL -- use a single iterator to probe the first
            # chunk and then continue streaming remaining data.
            aiter = resp.aiter_bytes(chunk_size=_DOWNLOAD_CHUNK_SIZE)
            try:
                probe = await aiter.__anext__()
            except StopAsyncIteration:
                probe = b""

            if not probe or probe.lstrip()[:1] != b"<":
                # Actual file content -- write probe + remaining chunks
                with open(dest, "wb") as f:
                    f.write(probe)
                    async for chunk in aiter:
                        f.write(chunk)
                return

            # Got HTML confirmation page -- parse the form action URL
            # and its hidden fields to build the real download URL.
            html = probe
            async for chunk in aiter:
                html += chunk
            self.log.info(
                "gdrive_confirmation_detected",
                original_url=final_url,
            )
            retry_url = self._extract_gdrive_download_url(html, final_url)

        # Stream context is closed; retry with the confirmed URL
        if retry_url is not None:
            await self._stream_download(client, retry_url, dest)

    @staticmethod
    def _extract_gdrive_download_url(html: bytes, fallback_url: str) -> str:
        """Parse the Google Drive confirmation page for the real download URL.

        Google Drive serves an HTML page with a ``<form>`` whose ``action``
        points to ``drive.usercontent.google.com/download`` and whose hidden
        inputs provide ``id``, ``export``, ``confirm``, and ``uuid`` params.

        Parameters
        ----------
        html:
            Raw bytes of the confirmation HTML page.
        fallback_url:
            URL to fall back to (with ``confirm=t`` injected) if parsing fails.

        Returns
        -------
        str
            The direct download URL with all required parameters.
        """
        import re

        text = html.decode("utf-8", errors="replace")

        # Extract form action URL
        action_match = re.search(
            r'<form[^>]+action="([^"]+)"', text
        )
        if not action_match:
            # Fallback: inject confirm=t into the original URL
            parsed = urllib.parse.urlparse(fallback_url)
            params = urllib.parse.parse_qs(parsed.query)
            params["confirm"] = ["t"]
            new_query = urllib.parse.urlencode(params, doseq=True)
            return urllib.parse.urlunparse(parsed._replace(query=new_query))

        action_url = action_match.group(1)

        # Extract all hidden input fields
        hidden_inputs = re.findall(
            r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]+value="([^"]*)"',
            text,
        )
        params_dict = {name: value for name, value in hidden_inputs}
        query_string = urllib.parse.urlencode(params_dict)

        return f"{action_url}?{query_string}"

    async def _stream_download(
        self,
        client: httpx.AsyncClient,
        url: str,
        dest: Path,
    ) -> None:
        """Stream-download a URL to a local file.

        Parameters
        ----------
        client:
            An ``httpx.AsyncClient``.
        url:
            URL to download.
        dest:
            Local file path to write.

        Raises
        ------
        httpx.HTTPStatusError
            If the response status is not 2xx.
        """
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                async for chunk in resp.aiter_bytes(
                    chunk_size=_DOWNLOAD_CHUNK_SIZE
                ):
                    f.write(chunk)

    def _extract_csv_from_zip(self, zip_path: Path) -> Path:
        """Extract the first CSV file from a ZIP archive.

        Parameters
        ----------
        zip_path:
            Path to the downloaded ZIP file.

        Returns
        -------
        Path
            Path to the extracted CSV file.

        Raises
        ------
        ValueError
            If the ZIP contains no ``.csv`` files.
        """
        with zipfile.ZipFile(zip_path, "r") as zf:
            csv_members = [
                name for name in zf.namelist()
                if name.lower().endswith(".csv")
            ]
            if not csv_members:
                msg = f"No CSV files found in {zip_path.name}"
                self.log.error("zip_no_csv", archive=zip_path.name)
                raise ValueError(msg)

            # Extract all CSV files; return path to the first one
            for member in csv_members:
                zf.extract(member, self.download_dir)
                self.log.info(
                    "zip_extract",
                    archive=zip_path.name,
                    member=member,
                )

            extracted_path = self.download_dir / csv_members[0]
            return extracted_path

    def _load_and_join(self, paths: dict[str, Path]) -> list[dict[str, Any]]:
        """Read and join the three CSV files on PARCEL_ID.

        Parameters
        ----------
        paths:
            Mapping of ZIP filename (or legacy CSV filename) to local
            CSV Path (from ``_download_files``).

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


def _latest_available_tax_year() -> int:
    """Return the most recently published Lee County PA tax roll year.

    Florida DOR certifies the final tax roll in October of the roll year.
    Before October the current-year roll does not yet exist, so we fall
    back to the previous year.  After certification (October–December)
    the current year is available.

    Examples
    --------
    - Called in January 2026  -> returns 2025
    - Called in October 2026  -> returns 2026
    """
    today = date.today()
    # October == month 10; certification happens during that month
    if today.month >= 10:
        return today.year
    return today.year - 1


class LeePAConnector(DataSourceConnector):
    """Lee County Property Appraiser connector (NAL fixed-width format).

    Downloads NAL tax roll ZIP archives and SDF sale data text files from
    the Lee County PA website, parses the fixed-width records, and joins
    on STRAP (Situs/Tax Roll Assessment Parcel) identifier.

    The Lee PA publishes data at year-specific URLs:
    - NAL: ``/TaxRoll/nalzip/{YEAR} Tax Roll NAL12D8.zip``
    - SDF: ``/TaxRoll/sdftxt/SDF{YEAR}Final.TXT`` (plain text, not zipped)
    - Parcel Data: ``/TaxRoll/ParcelData/LCPA_Parcel_Data_TXT.zip`` (monthly)

    Parameters
    ----------
    download_dir:
        Local directory where downloaded/extracted files are saved.
    config:
        Parsed YAML dict from ``config/pa_fields.yaml`` (the full document
        or just the ``lee`` section).
    http_client:
        Optional pre-configured ``httpx.AsyncClient`` for testing / reuse.
    tax_year:
        Tax roll year for NAL/SDF downloads (default: current year).
    """

    source_name = "lee_pa"

    # Lee County PA base URL
    BASE_URL = "https://www.leepa.org"

    # URL path templates (year is interpolated at runtime)
    NAL_ZIP_PATH = "/TaxRoll/nalzip/{year} Tax Roll NAL12D8.zip"
    SDF_TXT_PATH = "/TaxRoll/sdftxt/SDF{year}Final.TXT"

    # Monthly parcel data (alternative to annual NAL files)
    PARCEL_DATA_PATH = "/TaxRoll/ParcelData/LCPA_Parcel_Data_TXT.zip"

    def __init__(
        self,
        download_dir: Path,
        config: dict[str, Any],
        http_client: httpx.AsyncClient | None = None,
        tax_year: int | None = None,
    ) -> None:
        super().__init__(name=self.source_name)
        self.download_dir = download_dir
        self._http_client = http_client
        self.tax_year = tax_year or _latest_available_tax_year()

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

    @property
    def nal_url(self) -> str:
        """Full URL for the NAL ZIP archive for the configured tax year."""
        path = self.NAL_ZIP_PATH.format(year=self.tax_year)
        return f"{self.BASE_URL}{path}"

    @property
    def sdf_url(self) -> str:
        """Full URL for the SDF text file for the configured tax year."""
        path = self.SDF_TXT_PATH.format(year=self.tax_year)
        return f"{self.BASE_URL}{path}"

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
        """Download NAL ZIP and SDF text file, then return raw joined records.

        The NAL file is downloaded as a ZIP archive and extracted.  The SDF
        file is a plain text file (not zipped) and is saved directly.

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
        nal_paths = await self._download_nal_zip()
        sdf_path = await self._download_sdf_txt()
        return self._load_and_join_from_paths(nal_paths, sdf_path)

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

        Sends HEAD requests to the NAL ZIP and SDF TXT URLs.  Returns
        ``True`` if both respond with 2xx, ``False`` otherwise.
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
        urls_to_check = [self.nal_url, self.sdf_url]
        response_codes: dict[str, int] = {}
        all_ok = True

        client = self._http_client or httpx.AsyncClient(
            follow_redirects=True, timeout=30
        )
        should_close = self._http_client is None

        try:
            for url in urls_to_check:
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
            urls_checked=len(urls_to_check),
            tax_year=self.tax_year,
        )
        return {
            "status": status,
            "urls_checked": len(urls_to_check),
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

    async def _download_nal_zip(self) -> list[Path]:
        """Download and extract the NAL ZIP archive via httpx streaming.

        The Lee PA publishes NAL files as year-specific ZIP archives at
        ``/TaxRoll/nalzip/{YEAR} Tax Roll NAL12D8.zip``.

        Returns
        -------
        list[Path]
            Paths of extracted files from the NAL ZIP.

        Raises
        ------
        httpx.HTTPStatusError
            If the download returns a non-2xx response.
        """
        self.download_dir.mkdir(parents=True, exist_ok=True)

        url = self.nal_url
        dest = self.download_dir / f"NAL_{self.tax_year}.zip"
        self.log.info("download_start", file="NAL", tax_year=self.tax_year)

        client = self._http_client or httpx.AsyncClient(
            follow_redirects=True, timeout=300
        )
        should_close = self._http_client is None

        try:
            try:
                async with client.stream("GET", url) as resp:
                    resp.raise_for_status()
                    with open(dest, "wb") as f:
                        async for chunk in resp.aiter_bytes(
                            chunk_size=_LEE_DOWNLOAD_CHUNK_SIZE
                        ):
                            f.write(chunk)
                self.log.info(
                    "download_complete",
                    file="NAL",
                    tax_year=self.tax_year,
                    size_bytes=dest.stat().st_size,
                )
            except httpx.HTTPError as exc:
                self.log.error(
                    "download_failed",
                    file="NAL",
                    tax_year=self.tax_year,
                    error=str(exc),
                )
                raise
        finally:
            if should_close:
                await client.aclose()

        return self._extract_zip(dest)

    async def _download_sdf_txt(self) -> Path | None:
        """Download the SDF sale data text file.

        The Lee PA publishes SDF files as plain text (not zipped) at
        ``/TaxRoll/sdftxt/SDF{YEAR}Final.TXT``.

        Returns
        -------
        Path or None
            Path to the downloaded SDF text file, or None on failure.

        Raises
        ------
        httpx.HTTPStatusError
            If the download returns a non-2xx response.
        """
        self.download_dir.mkdir(parents=True, exist_ok=True)

        url = self.sdf_url
        dest = self.download_dir / f"SDF_{self.tax_year}.txt"
        self.log.info("download_start", file="SDF", tax_year=self.tax_year)

        client = self._http_client or httpx.AsyncClient(
            follow_redirects=True, timeout=300
        )
        should_close = self._http_client is None

        try:
            try:
                async with client.stream("GET", url) as resp:
                    resp.raise_for_status()
                    with open(dest, "wb") as f:
                        async for chunk in resp.aiter_bytes(
                            chunk_size=_LEE_DOWNLOAD_CHUNK_SIZE
                        ):
                            f.write(chunk)
                self.log.info(
                    "download_complete",
                    file="SDF",
                    tax_year=self.tax_year,
                    size_bytes=dest.stat().st_size,
                )
            except httpx.HTTPError as exc:
                self.log.error(
                    "download_failed",
                    file="SDF",
                    tax_year=self.tax_year,
                    error=str(exc),
                )
                raise
        finally:
            if should_close:
                await client.aclose()

        return dest

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

    def _load_and_join_from_paths(
        self,
        nal_paths: list[Path],
        sdf_path: Path | None,
    ) -> list[dict[str, Any]]:
        """Parse NAL and SDF files and join on STRAP.

        Parameters
        ----------
        nal_paths:
            List of extracted file paths from the NAL ZIP.
        sdf_path:
            Path to the downloaded SDF text file (may be None).

        Returns
        -------
        list[dict]
            Joined records with NAL and SDF data merged by STRAP.
        """
        # Parse NAL records from all extracted files
        nal_records: list[dict[str, Any]] = []
        for path in nal_paths:
            content = self._read_file_content(path)
            records = parse_nal_file(content, self._nal_fields)
            nal_records.extend(records)

        # Parse SDF records from the text file
        sdf_records: list[dict[str, Any]] = []
        if sdf_path and sdf_path.exists():
            content = self._read_file_content(sdf_path)
            sdf_records = parse_nal_file(content, self._sdf_fields)

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
