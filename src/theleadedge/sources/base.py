"""Abstract base class for all data source connectors.

Every data source (MLS CSV, public records API, digital signals) implements
``DataSourceConnector`` to provide a uniform interface for the ingestion
pipeline.

The ``sync()`` template method orchestrates authentication, fetch, transform,
and error handling.  Subclasses implement the three abstract methods:
``authenticate``, ``fetch``, and ``transform``.

``SyncResult`` captures the outcome of each sync job for audit logging
via ``SyncLogRow`` in the database.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import structlog
from pydantic import BaseModel

logger = structlog.get_logger()


class SyncResult(BaseModel):
    """Outcome of a data source sync job."""

    source: str
    job_type: str
    success: bool
    records_fetched: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    errors: list[str] = []
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None


class DataSourceConnector(ABC):
    """Abstract base for data source connectors.

    Subclasses must implement ``authenticate``, ``fetch``, ``transform``,
    and ``health_check``.  The ``sync`` method provides a template that
    handles timing, error capture, and result construction.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._is_authenticated = False
        self.log = logger.bind(source=name)

    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with the data source.

        For file-based sources (CSV), this may simply verify the file exists.
        For API-based sources, this performs OAuth or API key validation.
        """

    @abstractmethod
    async def fetch(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Fetch raw records from the data source.

        Parameters
        ----------
        since:
            If provided, only fetch records modified after this timestamp
            (incremental sync).  If ``None``, fetch all (full sync).
        **filters:
            Source-specific filter parameters.

        Returns
        -------
        list[dict]
            Raw records as dictionaries before normalization.
        """

    @abstractmethod
    def transform(self, raw_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform raw records into normalized internal format.

        Parameters
        ----------
        raw_records:
            Raw records from ``fetch()``.

        Returns
        -------
        list[dict]
            Records keyed by internal (RESO) field names, with parsed
            types (dates, booleans, floats).
        """

    async def sync(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> SyncResult:
        """Template method: authenticate, fetch, transform, report.

        Subclasses should override ``authenticate``, ``fetch``, and
        ``transform`` rather than this method.
        """
        started = datetime.utcnow()
        result = SyncResult(
            source=self.name,
            job_type="incremental" if since else "full_sync",
            success=False,
            started_at=started,
        )
        try:
            if not self._is_authenticated:
                await self.authenticate()
                self._is_authenticated = True

            raw = await self.fetch(since=since, **filters)
            result.records_fetched = len(raw)

            transformed = self.transform(raw)
            result.records_created = len(transformed)
            result.success = True

            self.log.info(
                "sync_completed",
                records_fetched=result.records_fetched,
                records_created=result.records_created,
            )
        except Exception as exc:
            result.errors.append(str(exc))
            self.log.error("sync_failed", error=str(exc))

        result.completed_at = datetime.utcnow()
        result.duration_ms = int(
            (result.completed_at - result.started_at).total_seconds() * 1000
        )
        return result

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the data source is reachable and operational."""
