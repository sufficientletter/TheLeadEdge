"""County Clerk of Court record connector.

Reads CSV/XLSX files from an import directory containing court records
obtained via Florida Sunshine Law requests. Supports multiple record types:
- Lis Pendens (pre-foreclosure filings)
- Probate cases
- Divorce / Domestic Relations filings

Files are placed in the import directory manually. The connector reads them,
normalizes the headers via flexible column mapping from config, and produces
SourceRecords for the matching pipeline.

Supports both Lee and Collier county naming conventions through configurable
header aliases (e.g., "PARCEL" / "PARCEL_ID" / "PARCEL_NUMBER" all map to
the internal parcel_id field).

IMPORTANT: Never log PII (names, addresses).
"""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from pathlib import Path
from typing import Any

import structlog
import yaml

from theleadedge.models.source_record import SourceRecord
from theleadedge.sources.base import DataSourceConnector

logger = structlog.get_logger()

# Supported record types for this connector
VALID_RECORD_TYPES = frozenset({"lis_pendens", "probate", "divorce"})

# Date formats to try when parsing event dates from clerk records
_DATE_FORMATS = [
    "%m/%d/%Y",
    "%Y-%m-%d",
    "%m-%d-%Y",
    "%m/%d/%y",
    "%Y/%m/%d",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
]


class ClerkRecordConnector(DataSourceConnector):
    """File-drop connector for county clerk court records.

    Scans an import directory for CSV/XLSX files matching the configured
    record type (lis_pendens, probate, divorce), reads and normalizes them,
    and produces ``SourceRecord`` instances for the public record pipeline.

    Parameters
    ----------
    import_dir:
        Directory where clerk record files are placed for import.
    record_type:
        One of ``"lis_pendens"``, ``"probate"``, or ``"divorce"``.
    config:
        Parsed YAML dict from ``config/clerk_fields.yaml``.
    county:
        County identifier for logging (default: ``"collier"``).
    """

    source_name = "clerk_records"

    def __init__(
        self,
        import_dir: Path,
        record_type: str,
        config: dict[str, Any],
        county: str = "collier",
    ) -> None:
        if record_type not in VALID_RECORD_TYPES:
            msg = (
                f"Invalid record_type {record_type!r}. "
                f"Must be one of: {', '.join(sorted(VALID_RECORD_TYPES))}"
            )
            raise ValueError(msg)

        super().__init__(name=self.source_name)
        self.import_dir = import_dir
        self.record_type = record_type
        self.county = county

        # Extract field mapping for this record type from config
        self._field_aliases: dict[str, list[str]] = config.get(record_type, {})
        self.log = logger.bind(
            source=self.source_name,
            record_type=record_type,
            county=county,
        )

    # ------------------------------------------------------------------
    # DataSourceConnector interface
    # ------------------------------------------------------------------

    async def authenticate(self) -> None:
        """No authentication needed for file-drop imports.

        Verifies the import directory exists.
        """
        if not self.import_dir.exists():
            self.import_dir.mkdir(parents=True, exist_ok=True)
            self.log.info(
                "import_dir_created",
                import_dir=str(self.import_dir),
            )
        self.log.info("authenticate_ok", import_dir=str(self.import_dir))

    async def fetch(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Scan import directory for files matching the record type.

        Returns raw file paths wrapped in dicts (to satisfy the base class
        interface). The actual file reading happens in ``transform()``.

        Parameters
        ----------
        since:
            Not used for file-drop imports.
        **filters:
            Not used.

        Returns
        -------
        list[dict]
            Each dict contains ``{"file_path": Path}`` for a matched file.
        """
        found = self._find_files()
        self.log.info("files_found", count=len(found))
        return [{"file_path": p} for p in found]

    def transform(self, raw_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Read files and produce SourceRecord-compatible dicts.

        Parameters
        ----------
        raw_records:
            List of dicts from ``fetch()``, each containing a ``file_path``.

        Returns
        -------
        list[dict]
            Dicts ready to construct ``SourceRecord`` instances.
        """
        all_rows: list[dict[str, str]] = []

        for entry in raw_records:
            file_path = entry["file_path"]
            if isinstance(file_path, str):
                file_path = Path(file_path)

            if file_path.suffix.lower() == ".xlsx":
                rows = self._read_xlsx(file_path)
            else:
                rows = self._read_csv(file_path)

            # Tag each row with the source filename for record ID generation
            for i, row in enumerate(rows):
                row["_source_file"] = file_path.stem
                row["_row_index"] = str(i)

            all_rows.extend(rows)

        results: list[dict[str, Any]] = []
        for row in all_rows:
            normalized = self._normalize_headers(row)

            source_file = row.get("_source_file", "unknown")
            row_index = row.get("_row_index", "0")
            source_record_id = f"{source_file}_{row_index}"

            # Parse event date
            event_date = _parse_date(normalized.get("event_date", ""))

            # Build raw_data with all original fields (excluding internal tags)
            raw_data: dict[str, Any] = {
                k: v for k, v in row.items()
                if not k.startswith("_")
            }

            # Add case_number to raw_data if present
            case_number = normalized.get("case_number", "")
            if case_number:
                raw_data["case_number"] = case_number

            result: dict[str, Any] = {
                "source_name": self.source_name,
                "source_record_id": source_record_id,
                "record_type": self.record_type,
                "parcel_id": normalized.get("parcel_id") or None,
                "street_address": normalized.get("street_address") or None,
                "city": normalized.get("city") or None,
                "state": normalized.get("state") or "FL",
                "zip_code": normalized.get("zip_code") or None,
                "event_date": event_date,
                "event_type": normalized.get("event_type") or self.record_type,
                "raw_data": raw_data,
                "owner_name": normalized.get("owner_name") or None,
            }

            results.append(result)

        self.log.info(
            "transform_complete",
            files_read=len(raw_records),
            records_produced=len(results),
        )
        return results

    async def health_check(self) -> bool:
        """Check that the import directory exists and is readable.

        Returns
        -------
        bool
            ``True`` if the directory exists and is accessible.
        """
        healthy = self.import_dir.exists() and self.import_dir.is_dir()
        self.log.info(
            "health_check",
            status="healthy" if healthy else "unhealthy",
            import_dir=str(self.import_dir),
        )
        return healthy

    # ------------------------------------------------------------------
    # Sync helper: transform to SourceRecord objects
    # ------------------------------------------------------------------

    def to_source_records(
        self, raw_records: list[dict[str, Any]]
    ) -> list[SourceRecord]:
        """Transform raw records into SourceRecord Pydantic instances.

        Convenience wrapper around ``transform()`` that produces actual
        ``SourceRecord`` objects instead of plain dicts.
        """
        dicts = self.transform(raw_records)
        return [SourceRecord(**d) for d in dicts]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_files(self) -> list[Path]:
        """Find files in the import directory matching the record type.

        Matches files whose name starts with the record type string
        (case-insensitive) and ends with ``.csv`` or ``.xlsx``.

        Returns
        -------
        list[Path]
            Sorted list of matching file paths.
        """
        if not self.import_dir.exists():
            return []

        matched: list[Path] = []
        prefix = self.record_type.lower()

        for path in self.import_dir.iterdir():
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix not in (".csv", ".xlsx"):
                continue
            if path.name.lower().startswith(prefix):
                matched.append(path)

        return sorted(matched)

    def _read_csv(self, path: Path) -> list[dict[str, str]]:
        """Read a CSV file with encoding fallback (UTF-8, CP-1252, Latin-1).

        Parameters
        ----------
        path:
            Path to the CSV file.

        Returns
        -------
        list[dict[str, str]]
            Rows as dictionaries keyed by column headers.
        """
        encodings = ["utf-8", "cp1252", "latin-1"]
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

        self.log.error("csv_decode_failed", file=path.name)
        return []

    def _read_xlsx(self, path: Path) -> list[dict[str, str]]:
        """Read an XLSX file via openpyxl in read-only mode.

        Parameters
        ----------
        path:
            Path to the XLSX file.

        Returns
        -------
        list[dict[str, str]]
            Rows as dictionaries keyed by column headers from the first row.
        """
        try:
            import openpyxl
        except ImportError:
            self.log.error(
                "openpyxl_not_installed",
                file=path.name,
            )
            return []

        rows: list[dict[str, str]] = []
        try:
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            ws = wb.active
            if ws is None:
                self.log.warning("xlsx_no_active_sheet", file=path.name)
                wb.close()
                return []

            row_iter = ws.iter_rows(values_only=True)
            # First row is the header
            header_row = next(row_iter, None)
            if header_row is None:
                self.log.warning("xlsx_empty_file", file=path.name)
                wb.close()
                return []

            headers = [str(h).strip() if h is not None else f"col_{i}"
                       for i, h in enumerate(header_row)]

            for data_row in row_iter:
                row_dict: dict[str, str] = {}
                for i, val in enumerate(data_row):
                    if i < len(headers):
                        row_dict[headers[i]] = str(val) if val is not None else ""
                rows.append(row_dict)

            wb.close()
            self.log.info(
                "xlsx_read",
                file=path.name,
                row_count=len(rows),
            )
        except Exception as exc:
            self.log.error(
                "xlsx_read_failed",
                file=path.name,
                error=str(exc),
            )

        return rows

    def _normalize_headers(self, row: dict[str, str]) -> dict[str, str]:
        """Map column aliases from the raw row to internal field names.

        Uses the field alias configuration to find matching columns.
        Comparison is case-insensitive.  The first alias that matches a
        column in the row wins.

        Parameters
        ----------
        row:
            A single raw row dict with original column headers.

        Returns
        -------
        dict[str, str]
            Dict keyed by internal field names with matched values.
        """
        # Build a case-insensitive lookup for the row's keys
        row_upper: dict[str, str] = {
            k.strip().upper(): v for k, v in row.items()
        }

        result: dict[str, str] = {}
        for internal_name, aliases in self._field_aliases.items():
            for alias in aliases:
                alias_upper = alias.strip().upper()
                if alias_upper in row_upper:
                    result[internal_name] = row_upper[alias_upper].strip()
                    break

        return result


def load_clerk_config(config_path: Path) -> dict[str, Any]:
    """Load the Clerk of Court field configuration from YAML.

    Parameters
    ----------
    config_path:
        Path to ``config/clerk_fields.yaml``.

    Returns
    -------
    dict
        Parsed YAML as a dict.
    """
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _parse_date(raw: str) -> date | None:
    """Parse a date string trying common formats.

    Parameters
    ----------
    raw:
        Raw date string from clerk records.

    Returns
    -------
    date or None
        Parsed date, or ``None`` if unparseable.
    """
    if not raw:
        return None
    stripped = str(raw).strip()
    if not stripped:
        return None

    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(stripped, fmt).date()
        except ValueError:
            continue
    return None
