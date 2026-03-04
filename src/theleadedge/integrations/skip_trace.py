"""BatchSkipTracing phone enrichment integration.

Provides phone number enrichment for top-tier leads using the
BatchSkipTracing API (https://batchskiptracing.com).

The pipeline:
1. Queries S/A-tier leads without phone numbers
2. Batches them into CSV format
3. Uploads to BatchSkipTracing API
4. Polls for results
5. Updates PropertyRow.owner_phone with normalized numbers
6. Applies DNC (Do Not Call) scrubbing

CRITICAL: NEVER log phone numbers. NEVER store raw API responses
containing PII outside the database. Always normalize to E.164.

Cost: ~$0.10-0.15 per record. Only enrich S/A tier leads.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, Any

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from theleadedge.storage.database import LeadRow, PropertyRow
from theleadedge.utils.phone import normalize_phone
from theleadedge.utils.rate_limit import CircuitBreaker

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()

# Maximum records per batch upload
BATCH_SIZE = 100

# Polling interval in seconds when waiting for batch completion
POLL_INTERVAL_SECONDS = 5.0

# Maximum polling attempts before giving up
MAX_POLL_ATTEMPTS = 120


class BatchSkipTraceClient:
    """HTTP client for the BatchSkipTracing API.

    Wraps API calls with circuit breaker protection to prevent
    cascading failures when the service is unavailable.

    Parameters
    ----------
    api_key:
        BatchSkipTracing API key (never logged).
    base_url:
        API base URL.
    http_client:
        Optional httpx.AsyncClient for dependency injection in tests.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.batchskiptracing.com/v1",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._http_client = http_client
        self._breaker = CircuitBreaker(
            name="batch_skip_tracing",
            failure_threshold=3,
            recovery_timeout=120.0,
        )
        self.log = logger.bind(service="batch_skip_tracing")

    def _get_headers(self) -> dict[str, str]:
        """Build HTTP headers with API key auth."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _get_client(self) -> tuple[httpx.AsyncClient, bool]:
        """Return the HTTP client, creating one if needed.

        Returns
        -------
        tuple[httpx.AsyncClient, bool]
            The client and whether we own it (should close after use).
        """
        if self._http_client is not None:
            return self._http_client, False
        return httpx.AsyncClient(timeout=60.0), True

    async def submit_batch(self, records: list[dict[str, str]]) -> str:
        """Submit a batch of records for skip tracing.

        Parameters
        ----------
        records:
            List of dicts with keys: name, street_address, city, state,
            zip_code.

        Returns
        -------
        str
            Batch ID for tracking the request.

        Raises
        ------
        RuntimeError
            If the circuit breaker is open or the API returns an error.
        """
        if not self._breaker.is_available:
            msg = "Circuit breaker open for BatchSkipTracing"
            raise RuntimeError(msg)

        client, should_close = await self._get_client()
        try:
            response = await client.post(
                f"{self._base_url}/batches",
                json={"records": records},
                headers=self._get_headers(),
            )
            response.raise_for_status()
            data = response.json()
            batch_id = data.get("batch_id", "")

            self._breaker.record_success()
            self.log.info(
                "batch_submitted",
                record_count=len(records),
            )
            return batch_id

        except Exception as exc:
            self._breaker.record_failure()
            self.log.error("batch_submit_failed", error=str(exc))
            raise
        finally:
            if should_close:
                await client.aclose()

    async def get_batch_status(self, batch_id: str) -> dict[str, Any]:
        """Check the processing status of a submitted batch.

        Parameters
        ----------
        batch_id:
            The batch ID returned from ``submit_batch()``.

        Returns
        -------
        dict
            Status dict with keys: status ("processing" | "complete"),
            progress_pct (0-100).

        Raises
        ------
        RuntimeError
            If the circuit breaker is open or the API returns an error.
        """
        if not self._breaker.is_available:
            msg = "Circuit breaker open for BatchSkipTracing"
            raise RuntimeError(msg)

        client, should_close = await self._get_client()
        try:
            response = await client.get(
                f"{self._base_url}/batches/{batch_id}/status",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            data = response.json()

            self._breaker.record_success()
            return {
                "status": data.get("status", "processing"),
                "progress_pct": data.get("progress_pct", 0),
            }

        except Exception as exc:
            self._breaker.record_failure()
            self.log.error("batch_status_failed", error=str(exc))
            raise
        finally:
            if should_close:
                await client.aclose()

    async def get_batch_results(
        self, batch_id: str
    ) -> list[dict[str, Any]]:
        """Fetch the completed results for a batch.

        Parameters
        ----------
        batch_id:
            The batch ID returned from ``submit_batch()``.

        Returns
        -------
        list[dict]
            List of result dicts, each containing: name, phone1, phone2,
            phone3 (any of which may be empty).

        Raises
        ------
        RuntimeError
            If the circuit breaker is open or the API returns an error.
        """
        if not self._breaker.is_available:
            msg = "Circuit breaker open for BatchSkipTracing"
            raise RuntimeError(msg)

        client, should_close = await self._get_client()
        try:
            response = await client.get(
                f"{self._base_url}/batches/{batch_id}/results",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            data = response.json()

            self._breaker.record_success()
            results = data.get("results", [])
            # Log only count, NEVER phone numbers
            self.log.info(
                "batch_results_fetched",
                result_count=len(results),
            )
            return results

        except Exception as exc:
            self._breaker.record_failure()
            self.log.error("batch_results_failed", error=str(exc))
            raise
        finally:
            if should_close:
                await client.aclose()

    async def health_check(self) -> dict[str, Any]:
        """Check BatchSkipTracing API availability.

        Returns
        -------
        dict
            Health status with keys: healthy (bool), circuit_state (str).
        """
        if not self._breaker.is_available:
            return {
                "healthy": False,
                "circuit_state": str(self._breaker.state),
            }

        client, should_close = await self._get_client()
        try:
            response = await client.get(
                f"{self._base_url}/health",
                headers=self._get_headers(),
            )
            healthy = response.status_code == 200
            self.log.info(
                "health_check",
                status="healthy" if healthy else "unhealthy",
            )
            if healthy:
                self._breaker.record_success()
            return {
                "healthy": healthy,
                "circuit_state": str(self._breaker.state),
            }
        except Exception as exc:
            self._breaker.record_failure()
            self.log.error("health_check_failed", error=str(exc))
            return {
                "healthy": False,
                "circuit_state": str(self._breaker.state),
            }
        finally:
            if should_close:
                await client.aclose()


class PhoneEnrichmentPipeline:
    """Pipeline for enriching top-tier leads with phone numbers.

    Queries S/A-tier leads that lack phone numbers, submits them to
    BatchSkipTracing for enrichment, normalizes results to E.164,
    scrubs against a DNC list, and updates the database.

    Parameters
    ----------
    session:
        Active SQLAlchemy async session.
    client:
        BatchSkipTraceClient instance.
    dnc_numbers:
        Set of E.164 phone numbers on the Do Not Call list.
    """

    def __init__(
        self,
        session: AsyncSession,
        client: BatchSkipTraceClient,
        dnc_numbers: set[str] | None = None,
    ) -> None:
        self.session = session
        self.client = client
        self.dnc_numbers: set[str] = dnc_numbers or set()
        self.log = logger.bind(pipeline="phone_enrichment")

    async def enrich_top_tier(
        self,
        tiers: list[str] | None = None,
        now: datetime | None = None,
    ) -> dict[str, int]:
        """Enrich top-tier leads with phone numbers.

        Parameters
        ----------
        tiers:
            List of tier codes to enrich (default: ["S", "A"]).
        now:
            Current timestamp for logging (default: utcnow).

        Returns
        -------
        dict
            Statistics: leads_queried, batches_submitted, phones_found,
            dnc_filtered, properties_updated.
        """
        if tiers is None:
            tiers = ["S", "A"]
        if now is None:
            now = datetime.utcnow()

        stats = {
            "leads_queried": 0,
            "batches_submitted": 0,
            "phones_found": 0,
            "dnc_filtered": 0,
            "properties_updated": 0,
        }

        # Step 1: Query leads by tier that don't have phone numbers
        leads_with_props = await self._query_leads_without_phone(tiers)
        stats["leads_queried"] = len(leads_with_props)

        if not leads_with_props:
            self.log.info(
                "no_leads_to_enrich",
                tiers=tiers,
            )
            return stats

        self.log.info(
            "enrichment_start",
            leads_found=len(leads_with_props),
            tiers=tiers,
        )

        # Step 2: Batch into groups
        batches = self._create_batches(leads_with_props)

        # Step 3-5: Submit, poll, and process each batch
        for batch_records, batch_prop_map in batches:
            try:
                batch_id = await self.client.submit_batch(batch_records)
                stats["batches_submitted"] += 1

                # Poll for completion
                results = await self._poll_and_get_results(batch_id)

                # Step 6-8: Normalize, DNC filter, update
                batch_stats = await self._process_results(
                    results, batch_prop_map
                )
                stats["phones_found"] += batch_stats["phones_found"]
                stats["dnc_filtered"] += batch_stats["dnc_filtered"]
                stats["properties_updated"] += batch_stats["properties_updated"]

            except Exception as exc:
                self.log.error(
                    "batch_processing_failed",
                    error=str(exc),
                )

        self.log.info(
            "enrichment_complete",
            leads_queried=stats["leads_queried"],
            batches_submitted=stats["batches_submitted"],
            phones_found=stats["phones_found"],
            dnc_filtered=stats["dnc_filtered"],
            properties_updated=stats["properties_updated"],
        )
        return stats

    async def _query_leads_without_phone(
        self, tiers: list[str]
    ) -> list[tuple[LeadRow, PropertyRow]]:
        """Query active leads in the given tiers where the property has no phone.

        Parameters
        ----------
        tiers:
            List of tier codes (e.g., ["S", "A"]).

        Returns
        -------
        list[tuple[LeadRow, PropertyRow]]
            Matching leads with their associated properties.
        """
        stmt = (
            select(LeadRow)
            .where(
                LeadRow.is_active.is_(True),
                LeadRow.tier.in_(tiers),
            )
            .options(selectinload(LeadRow.property_rel))
            .order_by(LeadRow.current_score.desc())
        )
        result = await self.session.execute(stmt)
        leads = result.scalars().all()

        # Filter to those without phone numbers
        leads_with_props: list[tuple[LeadRow, PropertyRow]] = []
        for lead in leads:
            prop = lead.property_rel
            if prop is not None and not prop.owner_phone:
                leads_with_props.append((lead, prop))

        return leads_with_props

    def _create_batches(
        self,
        leads_with_props: list[tuple[LeadRow, PropertyRow]],
    ) -> list[tuple[list[dict[str, str]], dict[str, int]]]:
        """Split leads into batches of BATCH_SIZE records.

        Parameters
        ----------
        leads_with_props:
            List of (lead, property) tuples.

        Returns
        -------
        list[tuple[list[dict], dict]]
            Each tuple is (batch_records, prop_map) where prop_map maps
            owner name to property_id for result matching.
        """
        batches: list[tuple[list[dict[str, str]], dict[str, int]]] = []
        current_batch: list[dict[str, str]] = []
        current_map: dict[str, int] = {}

        for _lead, prop in leads_with_props:
            # Build the record for BatchSkipTracing
            name = prop.owner_name or prop.owner_name_raw or ""
            if not name:
                continue

            address = prop.address or ""
            city = prop.city or ""
            state = prop.state or "FL"
            zip_code = prop.zip_code or ""

            record = {
                "name": name,
                "street_address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
            }
            current_batch.append(record)
            # Use name as key for matching results back
            current_map[name.upper().strip()] = prop.id

            if len(current_batch) >= BATCH_SIZE:
                batches.append((current_batch, current_map))
                current_batch = []
                current_map = {}

        # Don't forget the last partial batch
        if current_batch:
            batches.append((current_batch, current_map))

        return batches

    async def _poll_and_get_results(
        self, batch_id: str
    ) -> list[dict[str, Any]]:
        """Poll for batch completion and return results.

        Parameters
        ----------
        batch_id:
            Batch ID from ``submit_batch()``.

        Returns
        -------
        list[dict]
            Result records from the API.

        Raises
        ------
        TimeoutError
            If the batch does not complete within MAX_POLL_ATTEMPTS.
        """
        for _attempt in range(MAX_POLL_ATTEMPTS):
            status = await self.client.get_batch_status(batch_id)

            if status["status"] == "complete":
                return await self.client.get_batch_results(batch_id)

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

        msg = f"Batch {batch_id} did not complete within {MAX_POLL_ATTEMPTS} attempts"
        raise TimeoutError(msg)

    async def _process_results(
        self,
        results: list[dict[str, Any]],
        prop_map: dict[str, int],
    ) -> dict[str, int]:
        """Normalize phones, scrub DNC, and update properties.

        Parameters
        ----------
        results:
            API result records with name and phone fields.
        prop_map:
            Mapping of uppercase owner names to property IDs.

        Returns
        -------
        dict
            Stats for this batch: phones_found, dnc_filtered,
            properties_updated.
        """
        batch_stats = {
            "phones_found": 0,
            "dnc_filtered": 0,
            "properties_updated": 0,
        }

        for result_record in results:
            name = (result_record.get("name") or "").upper().strip()
            prop_id = prop_map.get(name)
            if prop_id is None:
                continue

            # Extract all phone fields
            phones_raw: list[str] = []
            for key in ("phone1", "phone2", "phone3"):
                phone_val = result_record.get(key, "")
                if phone_val:
                    phones_raw.append(phone_val)

            if not phones_raw:
                continue

            # Normalize and pick the first valid phone
            best_phone: str | None = None
            for raw_phone in phones_raw:
                normalized = normalize_phone(raw_phone)
                if normalized is None:
                    continue

                batch_stats["phones_found"] += 1

                if self._scrub_dnc(normalized):
                    batch_stats["dnc_filtered"] += 1
                    continue

                if best_phone is None:
                    best_phone = normalized

            # Update the property if we found a valid, non-DNC phone
            if best_phone is not None:
                prop = await self.session.get(PropertyRow, prop_id)
                if prop is not None:
                    prop.owner_phone = best_phone
                    batch_stats["properties_updated"] += 1

        await self.session.flush()
        return batch_stats

    def _scrub_dnc(self, phone: str) -> bool:
        """Check if a phone number is on the DNC list.

        Parameters
        ----------
        phone:
            E.164 formatted phone number.

        Returns
        -------
        bool
            True if the number is on the DNC list (should be excluded).
        """
        return phone in self.dnc_numbers
