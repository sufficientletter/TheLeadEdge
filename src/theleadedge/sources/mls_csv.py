"""MLS CSV import connector for TheLeadEdge.

Reads Matrix-exported CSV files and normalizes them into the internal field
schema defined by ``config/mls_fields.yaml``.

Key design decisions:

1. **Dual header format** -- Matrix exports use either PascalCase "Name"
   headers or human-readable "Label" headers.  We build a lookup from both
   to the canonical internal name.

2. **Encoding fallback** -- Try UTF-8 first, then CP-1252 (common Windows
   encoding from Matrix exports).

3. **Status normalization** -- Raw status values (e.g. "ACT", "EXP",
   "Sold") are mapped to RESO StandardStatus canonical values.

4. **Boolean mapping** -- "Yes"/"Y"/"1"/"True" -> True, etc.

5. **Date parsing** -- Multiple format patterns tried in order.

6. **Required field validation** -- Records missing ListingKey, ListingId,
   StandardStatus, or ListPrice are skipped and logged (without PII).

IMPORTANT: Never log PII from CSV records (addresses, owner names, etc.).
"""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from pathlib import Path
from typing import Any

import structlog
import yaml

from theleadedge.sources.base import DataSourceConnector

logger = structlog.get_logger()


class MLSFieldConfig:
    """Parsed representation of config/mls_fields.yaml.

    Builds lookup tables for header resolution, status normalization,
    boolean parsing, and date format patterns.
    """

    def __init__(self, config_path: Path) -> None:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Header lookup: both Name and Label -> internal
        self.header_to_internal: dict[str, str] = {}
        self.field_types: dict[str, str] = {}
        self.required_fields: set[str] = set()

        for fm in data.get("field_mapping", []):
            internal = fm["internal"]
            self.header_to_internal[fm["name"]] = internal
            self.header_to_internal[fm["label"]] = internal
            self.field_types[internal] = fm.get("type", "str")
            if fm.get("required", False):
                self.required_fields.add(internal)

        # Status normalization: raw_value (lowered) -> canonical
        self.status_map: dict[str, str] = {}
        for _key, entry in (data.get("status_mapping") or {}).items():
            canonical = entry["canonical"]
            for raw in entry.get("raw_values", []):
                self.status_map[raw.lower().strip()] = canonical

        # Boolean mapping
        bool_cfg = data.get("boolean_mapping", {})
        self.true_values: set[str] = {
            v.lower().strip() for v in bool_cfg.get("true_values", [])
        }
        self.false_values: set[str] = {
            v.lower().strip() for v in bool_cfg.get("false_values", [])
        }

        # Date format patterns
        date_cfg = data.get("date_formats", {})
        self.date_patterns: list[str] = date_cfg.get("date_patterns", [])
        self.datetime_patterns: list[str] = date_cfg.get("datetime_patterns", [])

        # Validation ranges
        self.range_checks: dict[str, dict[str, Any]] = {}
        for field_name, check in (
            data.get("validation", {}).get("range_checks") or {}
        ).items():
            self.range_checks[field_name] = check

    def resolve_header(self, header: str) -> str | None:
        """Map a CSV column header to its internal field name."""
        return self.header_to_internal.get(header.strip())

    def normalize_status(self, raw_status: str) -> str:
        """Normalize a raw status value to RESO canonical form."""
        canonical = self.status_map.get(raw_status.lower().strip())
        if canonical is not None:
            return canonical
        # If no mapping found, return the original trimmed value
        return raw_status.strip()

    def parse_bool(self, raw: str) -> bool:
        """Parse a raw boolean string to Python bool."""
        return raw.lower().strip() in self.true_values

    def parse_date(self, raw: str) -> date | None:
        """Parse a date string trying multiple format patterns."""
        stripped = raw.strip()
        if not stripped:
            return None
        for pattern in self.date_patterns:
            try:
                return datetime.strptime(stripped, pattern).date()
            except ValueError:
                continue
        # Also try datetime patterns and extract date
        for pattern in self.datetime_patterns:
            try:
                return datetime.strptime(stripped, pattern).date()
            except ValueError:
                continue
        return None

    def parse_datetime(self, raw: str) -> datetime | None:
        """Parse a datetime string trying multiple format patterns."""
        stripped = raw.strip()
        if not stripped:
            return None
        for pattern in self.datetime_patterns:
            try:
                return datetime.strptime(stripped, pattern)
            except ValueError:
                continue
        # Also try date-only patterns and convert to datetime
        for pattern in self.date_patterns:
            try:
                return datetime.combine(
                    datetime.strptime(stripped, pattern).date(),
                    datetime.min.time(),
                )
            except ValueError:
                continue
        return None

    def parse_value(self, internal_name: str, raw: str) -> Any:
        """Parse a raw CSV cell value according to its declared type."""
        field_type = self.field_types.get(internal_name, "str")
        stripped = raw.strip()

        if not stripped:
            return None

        if field_type == "str":
            return stripped

        if field_type == "int":
            try:
                # Handle comma-separated numbers and floats like "3.0"
                cleaned = stripped.replace(",", "")
                return int(float(cleaned))
            except (ValueError, OverflowError):
                return None

        if field_type == "float":
            try:
                cleaned = stripped.replace(",", "").replace("$", "")
                return float(cleaned)
            except (ValueError, OverflowError):
                return None

        if field_type == "bool":
            return self.parse_bool(stripped)

        if field_type == "date":
            return self.parse_date(stripped)

        if field_type == "datetime":
            return self.parse_datetime(stripped)

        return stripped


def _read_csv_with_fallback(file_path: Path) -> list[dict[str, str]]:
    """Read a CSV file, trying UTF-8 first then CP-1252.

    Returns a list of row dicts keyed by the original CSV header names.
    """
    encodings = ["utf-8", "cp1252"]
    for encoding in encodings:
        try:
            with open(file_path, encoding=encoding, newline="") as f:
                content = f.read()
            reader = csv.DictReader(io.StringIO(content))
            return list(reader)
        except UnicodeDecodeError:
            continue
    msg = f"Could not decode CSV with any supported encoding: {encodings}"
    raise ValueError(msg)


class MLSCsvConnector(DataSourceConnector):
    """Data source connector for MLS CSV file imports.

    Parameters
    ----------
    config_path:
        Path to ``config/mls_fields.yaml``.
    import_dir:
        Directory containing CSV files to import.
    """

    def __init__(
        self,
        config_path: Path,
        import_dir: Path,
    ) -> None:
        super().__init__(name="mls_csv")
        self.config_path = config_path
        self.import_dir = import_dir
        self._field_config: MLSFieldConfig | None = None

    @property
    def field_config(self) -> MLSFieldConfig:
        """Lazily load and cache the field configuration."""
        if self._field_config is None:
            self._field_config = MLSFieldConfig(self.config_path)
        return self._field_config

    async def authenticate(self) -> None:
        """Verify the import directory and config file exist."""
        if not self.config_path.exists():
            msg = f"MLS field config not found: {self.config_path}"
            raise FileNotFoundError(msg)
        if not self.import_dir.exists():
            self.import_dir.mkdir(parents=True, exist_ok=True)
            self.log.info("created_import_dir", path=str(self.import_dir))

    async def fetch(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Read all CSV files from the import directory.

        Parameters
        ----------
        since:
            If provided, only process CSV files modified after this timestamp.
        **filters:
            ``file_path`` -- If provided, read only this specific file.

        Returns
        -------
        list[dict]
            Raw CSV rows as dictionaries with original column headers.
        """
        specific_file: Path | None = filters.get("file_path")  # type: ignore[assignment]

        if specific_file is not None:
            csv_files = [Path(specific_file)]
        else:
            csv_files = sorted(self.import_dir.glob("*.csv"))

        if since is not None:
            csv_files = [
                f
                for f in csv_files
                if datetime.fromtimestamp(f.stat().st_mtime) > since
            ]

        all_rows: list[dict[str, Any]] = []
        for csv_file in csv_files:
            try:
                rows = _read_csv_with_fallback(csv_file)
                self.log.info(
                    "csv_file_read",
                    file=csv_file.name,
                    row_count=len(rows),
                )
                all_rows.extend(rows)
            except Exception as exc:
                self.log.error(
                    "csv_read_error",
                    file=csv_file.name,
                    error=str(exc),
                )

        return all_rows

    def transform(self, raw_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform raw CSV rows into internally-keyed, typed records.

        * Resolves headers via the field mapping (Name or Label).
        * Parses values to their declared types (int, float, date, etc.).
        * Normalizes status values to RESO canonical form.
        * Skips records missing required fields (logged without PII).

        Returns
        -------
        list[dict]
            Records keyed by internal RESO field names with parsed values.
        """
        transformed: list[dict[str, Any]] = []
        skipped = 0

        for row_idx, raw_row in enumerate(raw_records):
            record: dict[str, Any] = {}

            for csv_header, raw_value in raw_row.items():
                if csv_header is None or raw_value is None:
                    continue
                internal = self.field_config.resolve_header(csv_header)
                if internal is None:
                    continue
                parsed = self.field_config.parse_value(internal, str(raw_value))
                if parsed is not None:
                    record[internal] = parsed

            # Normalize StandardStatus through status mapping
            raw_status = record.get("StandardStatus")
            if isinstance(raw_status, str):
                record["StandardStatus"] = self.field_config.normalize_status(
                    raw_status
                )

            # Validate required fields
            missing = self.field_config.required_fields - set(record.keys())
            if missing:
                skipped += 1
                self.log.warning(
                    "record_skipped_missing_fields",
                    row_index=row_idx,
                    missing_fields=sorted(missing),
                )
                continue

            transformed.append(record)

        if skipped > 0:
            self.log.info(
                "transform_complete",
                total=len(raw_records),
                valid=len(transformed),
                skipped=skipped,
            )

        return transformed

    async def health_check(self) -> bool:
        """Check that the import directory and config file exist."""
        return self.import_dir.exists() and self.config_path.exists()
