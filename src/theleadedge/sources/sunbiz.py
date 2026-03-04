"""Florida Sunbiz LLC data connector.

Cross-references LLC entity data from the Florida Division of Corporations
(Sunbiz.org) with property ownership records to identify:
- Properties owned by LLCs (often investors)
- Out-of-state registered agents (absentee strengthening)
- Dissolved/inactive LLCs (abandoned property signal)

Data source: Sunbiz bulk data via SFTP (or HTTP fallback).
Format: Pipe-delimited text files.

IMPORTANT: Never log PII (owner names, addresses).
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from theleadedge.sources.base import DataSourceConnector

try:
    import asyncssh

    HAS_ASYNCSSH = True
except ImportError:
    HAS_ASYNCSSH = False

logger = structlog.get_logger()

# Statuses that indicate a dissolved/inactive entity
_DISSOLVED_STATUSES = frozenset({
    "DISSOLVED",
    "INACTIVE",
    "ADMIN DISSOLVED",
    "ADMINISTRATIVELY DISSOLVED",
    "REVOKED",
    "VOLUNTARILY DISSOLVED",
    "WITHDRAWN",
})

# Normalize whitespace for matching
_MULTI_SPACE_RE = re.compile(r"\s+")


def _normalize_name(name: str) -> str:
    """Normalize an entity or owner name for fuzzy matching.

    Strips whitespace, uppercases, removes common suffixes like LLC, INC,
    CORP, and punctuation to improve match rates.

    Parameters
    ----------
    name:
        Raw name string.

    Returns
    -------
    str
        Normalized name for comparison.
    """
    upper = name.upper().strip()
    # Remove common suffixes
    for suffix in (
        " LLC", " L.L.C.", " L.L.C", " INC", " INC.", " CORP",
        " CORP.", " LTD", " LTD.", " LP", " L.P.", " LLLP",
        " TRUST", " REVOCABLE TRUST", " IRREVOCABLE TRUST",
        " CO", " CO.", " COMPANY",
    ):
        if upper.endswith(suffix):
            upper = upper[: -len(suffix)]
    # Remove punctuation
    upper = re.sub(r"[.,\-'\"()]", "", upper)
    # Collapse whitespace
    upper = _MULTI_SPACE_RE.sub(" ", upper).strip()
    return upper


class SunbizConnector(DataSourceConnector):
    """Connector for Florida Sunbiz (Division of Corporations) LLC data.

    Fetches pipe-delimited bulk data files from Sunbiz via SFTP or HTTP
    fallback.  Parses entity records and cross-references them against
    property ownership records to identify LLC-owned properties, out-of-state
    agents, and dissolved entities.

    Parameters
    ----------
    download_dir:
        Local directory for storing downloaded Sunbiz files.
    sftp_host:
        Sunbiz SFTP server hostname (empty string to skip SFTP).
    sftp_user:
        SFTP username.
    sftp_password:
        SFTP password (never logged).
    http_client:
        Optional httpx.AsyncClient for dependency injection in tests.
    """

    source_name = "sunbiz"

    def __init__(
        self,
        download_dir: Path,
        sftp_host: str = "",
        sftp_user: str = "",
        sftp_password: str = "",
        http_client: Any | None = None,
    ) -> None:
        super().__init__(name=self.source_name)
        self.download_dir = download_dir
        self._sftp_host = sftp_host
        self._sftp_user = sftp_user
        self._sftp_password = sftp_password
        self._http_client = http_client
        self._use_sftp = bool(sftp_host and sftp_user and sftp_password)
        self.log = logger.bind(source=self.source_name)

    async def authenticate(self) -> None:
        """Verify SFTP credentials or HTTP fallback availability.

        If SFTP credentials are provided and asyncssh is installed,
        tests the SFTP connection.  Otherwise, marks HTTP fallback mode.
        """
        self.download_dir.mkdir(parents=True, exist_ok=True)

        if self._use_sftp and HAS_ASYNCSSH:
            try:
                async with (
                    asyncssh.connect(
                        self._sftp_host,
                        username=self._sftp_user,
                        password=self._sftp_password,
                        known_hosts=None,
                    ) as conn,
                    conn.start_sftp_client() as sftp,
                ):
                    await sftp.stat(".")
                self.log.info("sftp_auth_ok")
            except Exception as exc:
                self.log.warning(
                    "sftp_auth_failed_fallback_http",
                    error=str(exc),
                )
                self._use_sftp = False
        else:
            self.log.info(
                "authenticate_http_fallback",
                has_asyncssh=HAS_ASYNCSSH,
            )

    async def fetch(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Download Sunbiz bulk data files.

        Tries SFTP first if credentials are configured, then falls back
        to HTTP download.  Returns a list of dicts containing file paths.

        Parameters
        ----------
        since:
            Not used for Sunbiz bulk downloads (always full dataset).
        **filters:
            Not used.

        Returns
        -------
        list[dict]
            List of ``{"file_path": Path}`` for downloaded files.
        """
        if self._use_sftp and HAS_ASYNCSSH:
            return await self._fetch_sftp()
        return await self._fetch_http()

    async def _fetch_sftp(self) -> list[dict[str, Any]]:
        """Download files via SFTP."""
        downloaded: list[dict[str, Any]] = []
        try:
            async with (
                asyncssh.connect(
                    self._sftp_host,
                    username=self._sftp_user,
                    password=self._sftp_password,
                    known_hosts=None,
                ) as conn,
                conn.start_sftp_client() as sftp,
            ):
                remote_files = await sftp.listdir(".")
                for fname in remote_files:
                    if not fname.endswith(".txt"):
                        continue
                    local_path = self.download_dir / fname
                    await sftp.get(fname, str(local_path))
                    downloaded.append({"file_path": local_path})

            self.log.info(
                "sftp_fetch_complete",
                files_downloaded=len(downloaded),
            )
        except Exception as exc:
            self.log.error("sftp_fetch_failed", error=str(exc))

        return downloaded

    async def _fetch_http(self) -> list[dict[str, Any]]:
        """Scan the download directory for existing pipe-delimited files.

        In HTTP fallback mode, users manually download files or we scan
        for pre-placed files in the download directory.
        """
        downloaded: list[dict[str, Any]] = []
        if not self.download_dir.exists():
            return downloaded

        for path in sorted(self.download_dir.iterdir()):
            if path.suffix.lower() in (".txt", ".csv", ".dat"):
                downloaded.append({"file_path": path})

        self.log.info(
            "http_fallback_scan",
            files_found=len(downloaded),
            directory=str(self.download_dir),
        )
        return downloaded

    def transform(
        self, raw_records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Parse pipe-delimited Sunbiz files into entity dicts.

        Each line in a Sunbiz bulk file is pipe-delimited with fields:
        Document Number | Entity Name | Filing Date | Status | State |
        Registered Agent Name | Registered Agent Address |
        Registered Agent City | Registered Agent State |
        Principal Address | Principal City | Principal State | Principal Zip

        Parameters
        ----------
        raw_records:
            List of ``{"file_path": Path}`` from ``fetch()``.

        Returns
        -------
        list[dict]
            Parsed entity records with dissolution and out-of-state flags.
        """
        entities: list[dict[str, Any]] = []

        for entry in raw_records:
            file_path = entry.get("file_path")
            if file_path is None:
                continue

            path = Path(file_path)
            if not path.exists():
                self.log.warning(
                    "file_not_found",
                    file_path=str(path),
                )
                continue

            try:
                file_entities = self._parse_pipe_file(path)
                entities.extend(file_entities)
            except Exception as exc:
                self.log.error(
                    "parse_failed",
                    file_path=str(path),
                    error=str(exc),
                )

        self.log.info(
            "transform_complete",
            files_parsed=len(raw_records),
            entities_produced=len(entities),
        )
        return entities

    def _parse_pipe_file(self, path: Path) -> list[dict[str, Any]]:
        """Parse a single pipe-delimited Sunbiz file.

        Parameters
        ----------
        path:
            Path to the pipe-delimited text file.

        Returns
        -------
        list[dict]
            Parsed entity records.
        """
        entities: list[dict[str, Any]] = []

        with open(path, encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                parts = [p.strip() for p in line.split("|")]

                # Need at least document_number and entity_name
                if len(parts) < 2:
                    continue

                # Skip header rows
                if parts[0].upper() in ("DOCUMENT NUMBER", "DOC NUMBER", ""):
                    continue

                entity = self._parse_entity_line(parts, line_num)
                if entity is not None:
                    entities.append(entity)

        return entities

    def _parse_entity_line(
        self, parts: list[str], line_num: int
    ) -> dict[str, Any] | None:
        """Parse a single pipe-delimited line into an entity dict.

        Parameters
        ----------
        parts:
            Pipe-split fields from a single line.
        line_num:
            Line number in the source file (for diagnostics).

        Returns
        -------
        dict or None
            Entity dict, or None if the line is invalid.
        """
        document_number = parts[0].strip() if len(parts) > 0 else ""
        entity_name = parts[1].strip() if len(parts) > 1 else ""

        if not document_number or not entity_name:
            return None

        filing_date = parts[2].strip() if len(parts) > 2 else ""
        status = parts[3].strip().upper() if len(parts) > 3 else ""
        state = parts[4].strip().upper() if len(parts) > 4 else ""

        registered_agent_name = parts[5].strip() if len(parts) > 5 else ""
        registered_agent_address = parts[6].strip() if len(parts) > 6 else ""
        registered_agent_city = parts[7].strip() if len(parts) > 7 else ""
        registered_agent_state = (
            parts[8].strip().upper() if len(parts) > 8 else ""
        )

        principal_address = parts[9].strip() if len(parts) > 9 else ""
        principal_city = parts[10].strip() if len(parts) > 10 else ""
        principal_state = (
            parts[11].strip().upper() if len(parts) > 11 else ""
        )
        principal_zip = parts[12].strip() if len(parts) > 12 else ""

        is_dissolved = status in _DISSOLVED_STATUSES
        is_out_of_state_agent = bool(
            registered_agent_state
            and registered_agent_state != "FL"
            and registered_agent_state != ""
        )

        return {
            "document_number": document_number,
            "entity_name": entity_name,
            "filing_date": filing_date,
            "status": status,
            "state": state,
            "registered_agent_name": registered_agent_name,
            "registered_agent_address": registered_agent_address,
            "registered_agent_city": registered_agent_city,
            "registered_agent_state": registered_agent_state,
            "principal_address": principal_address,
            "principal_city": principal_city,
            "principal_state": principal_state,
            "principal_zip": principal_zip,
            "is_dissolved": is_dissolved,
            "is_out_of_state_agent": is_out_of_state_agent,
        }

    def cross_reference(
        self,
        entities: list[dict[str, Any]],
        property_owner_names: list[tuple[int, str]],
    ) -> list[dict[str, Any]]:
        """Match LLC entities to property owners by name.

        Compares normalized entity names against normalized property owner
        names.  Returns matches with the associated property_id.

        Parameters
        ----------
        entities:
            Parsed entity dicts from ``transform()``.
        property_owner_names:
            List of (property_id, owner_name_raw) tuples from the database.

        Returns
        -------
        list[dict]
            Matched records containing entity data plus ``property_id``.
        """
        # Build lookup: normalized_name -> list of (property_id, raw_name)
        owner_lookup: dict[str, list[tuple[int, str]]] = {}
        for prop_id, raw_name in property_owner_names:
            if not raw_name:
                continue
            normalized = _normalize_name(raw_name)
            if normalized:
                owner_lookup.setdefault(normalized, []).append(
                    (prop_id, raw_name)
                )

        matches: list[dict[str, Any]] = []
        for entity in entities:
            entity_normalized = _normalize_name(entity["entity_name"])
            if not entity_normalized:
                continue

            if entity_normalized in owner_lookup:
                for prop_id, _raw_name in owner_lookup[entity_normalized]:
                    match = {
                        **entity,
                        "property_id": prop_id,
                        "match_method": "exact_normalized",
                    }
                    matches.append(match)

        self.log.info(
            "cross_reference_complete",
            entities_checked=len(entities),
            owners_checked=len(property_owner_names),
            matches_found=len(matches),
        )
        return matches

    async def health_check(self) -> bool:
        """Check availability of Sunbiz data source.

        If SFTP is configured, attempts a connection test.
        Otherwise, checks that the download directory exists.

        Returns
        -------
        bool
            True if the data source is reachable.
        """
        if self._use_sftp and HAS_ASYNCSSH:
            try:
                async with (
                    asyncssh.connect(
                        self._sftp_host,
                        username=self._sftp_user,
                        password=self._sftp_password,
                        known_hosts=None,
                    ) as conn,
                    conn.start_sftp_client() as sftp,
                ):
                    await sftp.stat(".")
                self.log.info("health_check", status="healthy", mode="sftp")
                return True
            except Exception as exc:
                self.log.error(
                    "health_check_failed",
                    mode="sftp",
                    error=str(exc),
                )
                return False

        # HTTP/local fallback: check directory exists
        healthy = self.download_dir.exists()
        self.log.info(
            "health_check",
            status="healthy" if healthy else "unhealthy",
            mode="local",
            directory=str(self.download_dir),
        )
        return healthy
