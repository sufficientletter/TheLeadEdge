"""Code enforcement violation connector.

Reads CSV/XLSX files containing code violation records from Lee and Collier
county code enforcement departments. Filters to active/open violations only.

Files are placed in the import directory manually after receiving responses
to Florida Sunshine Law requests. The connector reads them, normalizes
headers via flexible column mapping from config, filters to open/active
violations, and produces SourceRecords for the matching pipeline.

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

# Statuses considered "active" (case-insensitive comparison)
_ACTIVE_STATUSES = frozenset({
    "OPEN",
    "ACTIVE",
    "PENDING",
    "IN VIOLATION",
    "NONCOMPLIANT",
    "NON-COMPLIANT",
})

# Statuses considered "closed" (case-insensitive comparison)
_CLOSED_STATUSES = frozenset({
    "CLOSED",
    "RESOLVED",
    "COMPLIANT",
    "DISMISSED",
    "ABATED",
    "COMPLETED",
})

# Date formats to try when parsing event dates
_DATE_FORMATS = [
    "%m/%d/%Y",
    "%Y-%m-%d",
    "%m-%d-%Y",
    "%m/%d/%y",
    "%Y/%m/%d",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
]


class CodeViolationConnector(DataSourceConnector):
    """File-drop connector for county code enforcement violation records.

    Scans an import directory for CSV/XLSX files matching the code violation
    pattern, reads and normalizes them, filters to only OPEN/ACTIVE
    violations, and produces ``SourceRecord`` instances.

    Parameters
    ----------
    import_dir:
        Directory where code violation files are placed for import.
    config:
        Parsed YAML dict from ``config/clerk_fields.yaml`` (the
        ``code_violation`` section will be used).
    county:
        County identifier for logging (default: ``"collier"``).
    """

    source_name = "code_violations"

    def __init__(
        self,
        import_dir: Path,
        config: dict[str, Any],
        county: str = "collier",
    ) -> None:
        super().__init__(name=self.source_name)
        self.import_dir = import_dir
        self.county = county

        # Extract field mapping for code_violation from config
        self._field_aliases: dict[str, list[str]] = config.get(
            "code_violation", {}
        )
        self.log = logger.bind(
            source=self.source_name,
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
        """Scan import directory for code violation files.

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
        """Read files, filter active violations, produce SourceRecord dicts.

        Only violations with OPEN/ACTIVE status are included.  Violations
        with CLOSED/RESOLVED/COMPLIANT status (or any status not in the
        active set) are filtered out.

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
        filtered_count = 0

        for row in all_rows:
            normalized = self._normalize_headers(row)

            # Filter: only keep OPEN/ACTIVE violations
            status = normalized.get("status", "").upper().strip()
            if not self._is_active_status(status):
                filtered_count += 1
                continue

            source_file = row.get("_source_file", "unknown")
            row_index = row.get("_row_index", "0")
            source_record_id = f"{source_file}_{row_index}"

            # Parse dates
            event_date = _parse_date(normalized.get("event_date", ""))
            compliance_date = _parse_date(normalized.get("compliance_date", ""))

            # Build raw_data with violation-specific fields
            raw_data: dict[str, Any] = {
                k: v for k, v in row.items()
                if not k.startswith("_")
            }
            # Add normalized violation fields to raw_data
            violation_type = normalized.get("violation_type", "")
            if violation_type:
                raw_data["violation_type"] = violation_type
            raw_data["status"] = status
            if compliance_date:
                raw_data["compliance_date"] = str(compliance_date)
            case_number = normalized.get("case_number", "")
            if case_number:
                raw_data["case_number"] = case_number

            result: dict[str, Any] = {
                "source_name": self.source_name,
                "source_record_id": source_record_id,
                "record_type": "code_violation",
                "parcel_id": normalized.get("parcel_id") or None,
                "street_address": normalized.get("street_address") or None,
                "city": normalized.get("city") or None,
                "state": "FL",
                "zip_code": normalized.get("zip_code") or None,
                "event_date": event_date,
                "event_type": "code_violation",
                "raw_data": raw_data,
                "owner_name": None,  # Code violations do not typically include owner
            }

            results.append(result)

        self.log.info(
            "transform_complete",
            files_read=len(raw_records),
            total_rows=len(all_rows),
            active_violations=len(results),
            filtered_inactive=filtered_count,
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
        """Find code violation files in the import directory.

        Matches files whose name starts with ``code_violation`` or
        ``violation`` (case-insensitive) and ends with ``.csv`` or
        ``.xlsx``.

        Returns
        -------
        list[Path]
            Sorted list of matching file paths.
        """
        if not self.import_dir.exists():
            return []

        matched: list[Path] = []
        prefixes = ("code_violation", "violation")

        for path in self.import_dir.iterdir():
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix not in (".csv", ".xlsx"):
                continue
            name_lower = path.name.lower()
            if any(name_lower.startswith(p) for p in prefixes):
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

            headers = [
                str(h).strip() if h is not None else f"col_{i}"
                for i, h in enumerate(header_row)
            ]

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

    @staticmethod
    def _is_active_status(status: str) -> bool:
        """Determine if a violation status represents an active/open case.

        Parameters
        ----------
        status:
            Uppercased status string.

        Returns
        -------
        bool
            ``True`` if the status is considered active/open.
            If the status is empty, the violation is included (assumed active).
        """
        if not status:
            # No status field present -- include by default (assume active)
            return True
        if status in _ACTIVE_STATUSES:
            return True
        # Closed → False; unknown → include by default
        return status not in _CLOSED_STATUSES


def load_clerk_config(config_path: Path) -> dict[str, Any]:
    """Load the Clerk / Code Enforcement field configuration from YAML.

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
        Raw date string from code violation records.

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
