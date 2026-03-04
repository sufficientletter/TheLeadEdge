"""Public record processing pipeline.

Orchestrates the flow from data source connectors through address matching,
signal detection, and persistence. High-confidence matches are auto-linked;
low-confidence matches are queued for manual review.

IMPORTANT: Never log PII. Log only IDs, match methods, and confidence values.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import structlog

from theleadedge.pipelines.detect import SignalDetector
from theleadedge.pipelines.match import RecordMapper
from theleadedge.storage.repositories import (
    FSBOListingRepo,
    LeadRepo,
    MarketSnapshotRepo,
    MatchQueueRepo,
    PropertyRepo,
    SignalRepo,
    SourceRecordRepo,
)

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

    from theleadedge.models.source_record import SourceRecord
    from theleadedge.scoring.config_loader import ScoringConfig

logger = structlog.get_logger()


class PublicRecordPipeline:
    """Orchestrates public record ingestion: match, persist, queue, signal.

    For each ``SourceRecord``:

    1. Check for duplicates (same source + source_record_id).
    2. Run cascading address match via ``RecordMapper``.
    3. If confidence >= threshold: auto-link to property, persist, and
       flag for future signal detection.
    4. If confidence > 0 but < threshold: persist and queue for manual review.
    5. If no match: persist as unmatched.

    Parameters
    ----------
    session:
        SQLAlchemy async session for database operations.
    config:
        Scoring configuration (will be used for signal detection in Batch 5).
    confidence_threshold:
        Minimum match confidence to auto-link a record to a property.
        Records below this threshold are queued for manual review.
    """

    def __init__(
        self,
        session: AsyncSession,
        config: ScoringConfig,
        confidence_threshold: float = 0.80,
    ) -> None:
        self.session = session
        self.config = config
        self.confidence_threshold = confidence_threshold
        self._source_repo = SourceRecordRepo(session)
        self._match_queue_repo = MatchQueueRepo(session)
        self._lead_repo = LeadRepo(session)
        self._signal_repo = SignalRepo(session)
        self._mapper = RecordMapper(session)
        self._detector = SignalDetector(config)
        self.log = logger.bind(component="public_record_pipeline")

    async def process_records(
        self,
        records: list[SourceRecord],
        now: datetime,
    ) -> dict[str, int]:
        """Process a batch of source records through the pipeline.

        Parameters
        ----------
        records:
            List of normalized source records from an external connector.
        now:
            Reference timestamp for signal detection (future use).

        Returns
        -------
        dict[str, int]
            Processing statistics with keys: ``total``, ``matched``,
            ``queued``, ``unmatched``, ``duplicates``, ``signals_created``.
        """
        stats = {
            "total": len(records),
            "matched": 0,
            "queued": 0,
            "unmatched": 0,
            "duplicates": 0,
            "signals_created": 0,
        }

        for record in records:
            # Step 1: Deduplication check
            existing = await self._source_repo.get_by_source_and_id(
                record.source_name, record.source_record_id
            )
            if existing is not None:
                stats["duplicates"] += 1
                self.log.debug(
                    "duplicate_record_skipped",
                    source=record.source_name,
                    source_record_id=record.source_record_id,
                )
                continue

            # Step 2: Address matching
            match_result = await self._mapper.match(record)

            # Step 3: Build the persistence kwargs
            source_kwargs = self._build_source_record_kwargs(record)

            if match_result.confidence >= self.confidence_threshold:
                # Auto-link: high-confidence match
                source_kwargs["matched_property_id"] = match_result.property_id
                source_kwargs["match_method"] = match_result.method
                source_kwargs["match_confidence"] = match_result.confidence

                source_row = await self._source_repo.create(**source_kwargs)

                # Signal detection on matched records
                property_id = match_result.property_id
                if property_id is not None:
                    lead_row = await self._lead_repo.get_by_property_id(
                        property_id
                    )
                    if lead_row is None:
                        lead_row = await self._lead_repo.create(
                            property_id=property_id
                        )

                    signals = self._detector.detect_from_source_record(
                        record=record,
                        lead_id=lead_row.id,
                        property_id=property_id,
                        now=now,
                    )

                    for sig in signals:
                        await self._signal_repo.create(
                            lead_id=sig.lead_id,
                            property_id=sig.property_id,
                            signal_type=sig.signal_type,
                            signal_category=sig.signal_category,
                            description=sig.description,
                            source=sig.source,
                            event_date=sig.event_date,
                            base_points=sig.base_points,
                            decay_type=sig.decay_type,
                            half_life_days=sig.half_life_days,
                            detected_at=now,
                            is_active=True,
                        )
                        stats["signals_created"] += 1

                self.log.info(
                    "record_matched",
                    source_record_db_id=source_row.id,
                    match_method=match_result.method,
                    match_confidence=match_result.confidence,
                    signals_created=stats["signals_created"],
                )

                stats["matched"] += 1

            elif match_result.confidence > 0:
                # Low-confidence: persist + queue for review
                source_kwargs["match_method"] = match_result.method
                source_kwargs["match_confidence"] = match_result.confidence

                source_row = await self._source_repo.create(**source_kwargs)

                await self._match_queue_repo.create(
                    source_record_id=source_row.id,
                    suggested_property_id=match_result.property_id,
                    match_confidence=match_result.confidence,
                    match_method=match_result.method,
                    status="pending",
                )

                self.log.info(
                    "record_queued_for_review",
                    source_record_db_id=source_row.id,
                    match_method=match_result.method,
                    match_confidence=match_result.confidence,
                )

                stats["queued"] += 1

            else:
                # No match at all
                source_row = await self._source_repo.create(**source_kwargs)

                self.log.debug(
                    "record_unmatched",
                    source_record_db_id=source_row.id,
                )

                stats["unmatched"] += 1

        self.log.info(
            "batch_processed",
            total=stats["total"],
            matched=stats["matched"],
            queued=stats["queued"],
            unmatched=stats["unmatched"],
            duplicates=stats["duplicates"],
        )

        return stats

    async def store_market_snapshots(
        self,
        snapshots: list[dict[str, object]],
        now: datetime,
    ) -> int:
        """Persist market snapshot data and detect neighborhood_hot signals.

        For each snapshot, creates a ``MarketSnapshotRow`` in the database.
        If the snapshot has an absorption_rate above the neighborhood_hot
        threshold, detects and persists signals for all leads in that ZIP.

        Parameters
        ----------
        snapshots:
            List of dicts suitable for ``MarketSnapshotRepo.create()``.
        now:
            Reference timestamp for signal detection.

        Returns
        -------
        int
            Number of snapshots persisted.
        """
        market_repo = MarketSnapshotRepo(self.session)
        property_repo = PropertyRepo(self.session)
        created = 0

        for snap in snapshots:
            await market_repo.create(**snap)
            created += 1

            # Trigger neighborhood_hot signal if absorption rate is high
            zip_code = str(snap.get("zip_code", ""))
            absorption_rate = snap.get("absorption_rate")

            if (
                zip_code
                and absorption_rate is not None
                and isinstance(absorption_rate, (int, float))
                and absorption_rate > 20.0
            ):
                # Find all properties in this ZIP, create signals
                properties = await property_repo.get_by_zip_code(zip_code)
                for prop in properties:
                    lead = await self._lead_repo.get_by_property_id(prop.id)
                    if lead is None:
                        continue

                    signal = self._detector.detect_neighborhood_hot(
                        lead_id=lead.id,
                        property_id=prop.id,
                        zip_code=zip_code,
                        absorption_rate=float(absorption_rate),
                    )
                    if signal is not None:
                        await self._signal_repo.create(
                            lead_id=signal.lead_id,
                            property_id=signal.property_id,
                            signal_type=signal.signal_type,
                            signal_category=signal.signal_category,
                            description=signal.description,
                            source=signal.source,
                            event_date=signal.event_date,
                            base_points=signal.base_points,
                            decay_type=signal.decay_type,
                            half_life_days=signal.half_life_days,
                            detected_at=now,
                            is_active=True,
                        )

        self.log.info(
            "market_snapshots_stored",
            created=created,
        )
        return created

    async def store_fsbo_listings(
        self,
        listings: list[dict[str, object]],
        now: datetime,
    ) -> int:
        """Persist FSBO listings and attempt address matching.

        For each listing, checks for duplicates by source_url, creates
        the ``FSBOListingRow``, and attempts to match the street address
        to an existing property in the database.

        Parameters
        ----------
        listings:
            List of dicts suitable for ``FSBOListingRepo.create()``.
        now:
            Reference timestamp (unused currently, reserved for future
            signal detection).

        Returns
        -------
        int
            Number of new listings persisted (excluding duplicates).
        """
        fsbo_repo = FSBOListingRepo(self.session)
        property_repo = PropertyRepo(self.session)
        created = 0

        for listing in listings:
            source_url = listing.get("source_url")

            # Skip duplicates
            if source_url and isinstance(source_url, str):
                existing = await fsbo_repo.get_by_source_url(source_url)
                if existing is not None:
                    continue

            # Attempt address match if we have a street_address
            street_address = listing.get("street_address")
            if street_address and isinstance(street_address, str):
                from theleadedge.utils.address import normalize_address

                addr_key = normalize_address(street_address)
                prop = await property_repo.get_by_address_key(addr_key)
                if prop is not None:
                    listing["matched_property_id"] = prop.id

            await fsbo_repo.create(**listing)
            created += 1

        self.log.info(
            "fsbo_listings_stored",
            created=created,
            total=len(listings),
        )
        return created

    @staticmethod
    def _build_source_record_kwargs(record: SourceRecord) -> dict[str, object]:
        """Convert a SourceRecord to kwargs for SourceRecordRepo.create().

        Serializes ``raw_data`` to JSON string and maps all relevant fields.
        """
        raw_data_json: str | None = None
        if record.raw_data:
            raw_data_json = json.dumps(record.raw_data, default=str)

        return {
            "source_name": record.source_name,
            "source_record_id": record.source_record_id,
            "record_type": record.record_type,
            "parcel_id": record.parcel_id,
            "street_address": record.street_address,
            "city": record.city,
            "state": record.state,
            "zip_code": record.zip_code,
            "event_date": record.event_date,
            "event_type": record.event_type,
            "raw_data": raw_data_json,
            "owner_name": record.owner_name,
            "mailing_address": record.mailing_address,
        }
