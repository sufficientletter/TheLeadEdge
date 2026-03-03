"""Ingestion pipeline for TheLeadEdge.

End-to-end pipeline that reads MLS CSV exports, normalizes addresses,
deduplicates properties, upserts into the database, creates leads, and
runs signal detection on each record.

Pipeline steps:

1. Read CSV files via ``MLSCsvConnector`` (encoding fallback, field mapping).
2. Normalize addresses using ``utils.address`` for deduplication keys.
3. Upsert properties (match on listing_key, then normalized address).
4. Create or update leads (one lead per property).
5. Run ``SignalDetector`` on each property to detect motivation signals.
6. Persist detected signals.
7. Return a ``SyncResult`` summarizing the job.

IMPORTANT: Never log PII (addresses, owner names, phone numbers).
"""

from __future__ import annotations

import shutil
from datetime import datetime
from typing import TYPE_CHECKING, Any

import structlog

from theleadedge.pipelines.detect import SignalDetector
from theleadedge.sources.base import SyncResult
from theleadedge.storage.repositories import (
    LeadRepo,
    PropertyRepo,
    SignalRepo,
    SyncLogRepo,
)
from theleadedge.utils.address import normalize_address

if TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.ext.asyncio import AsyncSession

    from theleadedge.scoring.config_loader import ScoringConfig
    from theleadedge.sources.mls_csv import MLSCsvConnector

logger = structlog.get_logger()


# Internal field -> PropertyRow column name mapping.
# Maps RESO internal names (from mls_fields.yaml) to the ORM column names
# used in PropertyRow.
_FIELD_TO_COLUMN: dict[str, str] = {
    "ListingKey": "listing_key",
    "ListingId": "listing_id",
    "StandardStatus": "standard_status",
    "MlsStatus": "mls_status",
    "ListPrice": "list_price",
    "OriginalListPrice": "original_list_price",
    "PreviousListPrice": "previous_list_price",
    "ClosePrice": "close_price",
    "ListPriceLow": "list_price_low",
    "DaysOnMarket": "days_on_market",
    "CumulativeDaysOnMarket": "cumulative_dom",
    "PropertyType": "property_type",
    "PropertySubType": "property_sub_type",
    "BedroomsTotal": "bedrooms",
    "BathroomsTotalInteger": "bathrooms",
    "LivingArea": "living_area",
    "LotSizeAcres": "lot_size_acres",
    "YearBuilt": "year_built",
    "City": "city",
    "PostalCode": "zip_code",
    "CountyOrParish": "county",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "ListAgentKey": "list_agent_key",
    "ListAgentMlsId": "list_agent_mls_id",
    "ListAgentFullName": "list_agent_full_name",
    "ListOfficeMlsId": "list_office_mls_id",
    "ListOfficeName": "list_office_name",
    "BuyerAgentKey": "buyer_agent_key",
    "ForeclosedREOYN": "foreclosed_reo",
    "PotentialShortSaleYN": "potential_short_sale",
    "GulfAccessYN": "gulf_access",
    "StatusChangeTimestamp": "status_change_timestamp",
    "ListingContractDate": "listing_contract_date",
    "ExpirationDate": "expiration_date",
    "OnMarketDate": "on_market_date",
    "OffMarketDate": "off_market_date",
    "PendingTimestamp": "pending_timestamp",
    "WithdrawnDate": "withdrawn_date",
    "CancellationDate": "cancellation_date",
    "CloseDate": "close_date",
    "PriceChangeTimestamp": "price_change_timestamp",
    "ModificationTimestamp": "modification_timestamp",
    "OriginalEntryTimestamp": "original_entry_timestamp",
}


def _build_address(record: dict[str, Any]) -> str:
    """Construct a street address from CSV field components.

    IMPORTANT: The returned address is PII. Never log it.
    """
    street_number = record.get("StreetNumberNumeric", "")
    street_name = record.get("StreetName", "")

    if street_number and street_name:
        return f"{street_number} {street_name}"
    if street_name:
        return str(street_name)
    if street_number:
        return str(street_number)
    return ""


def _record_to_property_kwargs(record: dict[str, Any]) -> dict[str, Any]:
    """Convert a normalized record (RESO keys) to PropertyRow column kwargs.

    Filters out None values and unmapped fields.
    """
    kwargs: dict[str, Any] = {}

    for reso_name, column_name in _FIELD_TO_COLUMN.items():
        value = record.get(reso_name)
        if value is not None:
            kwargs[column_name] = value

    # Build and normalize address
    address = _build_address(record)
    if address:
        kwargs["address"] = address
        city = record.get("City", "")
        state = "FL"
        zip_code = str(record.get("PostalCode", ""))
        kwargs["address_normalized"] = normalize_address(
            street=address,
            city=city,
            state=state,
            zip_code=zip_code,
        )

    kwargs["data_source"] = "mls_csv"

    return kwargs


class IngestPipeline:
    """End-to-end MLS CSV ingestion pipeline.

    Parameters
    ----------
    csv_connector:
        Configured ``MLSCsvConnector`` for reading CSV files.
    scoring_config:
        Loaded ``ScoringConfig`` for signal detection.
    processed_dir:
        Directory to move successfully processed CSV files to.
        If ``None``, files are left in place.
    """

    def __init__(
        self,
        csv_connector: MLSCsvConnector,
        scoring_config: ScoringConfig,
        processed_dir: Path | None = None,
    ) -> None:
        self.connector = csv_connector
        self.detector = SignalDetector(scoring_config)
        self.processed_dir = processed_dir
        self.log = logger.bind(component="ingest_pipeline")

    async def run(
        self,
        session: AsyncSession,
        import_dir: Path,
        now: datetime,
    ) -> SyncResult:
        """Execute the full ingestion pipeline.

        Parameters
        ----------
        session:
            Active async database session (caller manages transaction).
        import_dir:
            Directory containing CSV files to ingest.
        now:
            Reference timestamp for signal detection age calculations.

        Returns
        -------
        SyncResult
            Summary of the ingestion job.
        """
        started = datetime.utcnow()
        result = SyncResult(
            source="mls_csv",
            job_type="csv_ingest",
            success=False,
            started_at=started,
        )

        prop_repo = PropertyRepo(session)
        lead_repo = LeadRepo(session)
        signal_repo = SignalRepo(session)
        sync_log_repo = SyncLogRepo(session)

        try:
            # Step 1: Read and transform CSV files
            self.connector.import_dir = import_dir
            raw_rows = await self.connector.fetch()
            result.records_fetched = len(raw_rows)

            transformed = self.connector.transform(raw_rows)

            self.log.info(
                "csv_transform_complete",
                raw_count=len(raw_rows),
                valid_count=len(transformed),
            )

            created_count = 0
            updated_count = 0
            skipped_count = 0
            total_signals = 0

            for record in transformed:
                listing_key = record.get("ListingKey")
                if not listing_key:
                    skipped_count += 1
                    continue

                # Step 2-3: Build property kwargs and upsert
                prop_kwargs = _record_to_property_kwargs(record)

                if not prop_kwargs.get("address"):
                    skipped_count += 1
                    self.log.warning(
                        "record_skipped_no_address",
                        listing_key=str(listing_key),
                    )
                    continue

                # Ensure zip_code is present (required by DB schema)
                if "zip_code" not in prop_kwargs or not prop_kwargs["zip_code"]:
                    skipped_count += 1
                    self.log.warning(
                        "record_skipped_no_zip",
                        listing_key=str(listing_key),
                    )
                    continue

                # Remove listing_key from kwargs since it's passed as the
                # first positional argument to upsert_by_listing_key.
                prop_kwargs.pop("listing_key", None)

                prop_row, is_new = await prop_repo.upsert_by_listing_key(
                    listing_key=str(listing_key),
                    **prop_kwargs,
                )

                if is_new:
                    created_count += 1
                else:
                    updated_count += 1

                # Step 4: Create or retrieve lead
                lead_row = await lead_repo.get_by_property_id(prop_row.id)
                if lead_row is None:
                    lead_row = await lead_repo.create(property_id=prop_row.id)

                # Step 5: Run signal detection
                signals = self.detector.detect(
                    property_data=record,
                    lead_id=lead_row.id,
                    property_id=prop_row.id,
                    now=now,
                )

                # Step 6: Persist detected signals
                for sig in signals:
                    await signal_repo.create(
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
                    total_signals += 1

            result.records_created = created_count
            result.records_updated = updated_count
            result.records_skipped = skipped_count
            result.success = True

            self.log.info(
                "ingest_complete",
                records_fetched=result.records_fetched,
                records_created=created_count,
                records_updated=updated_count,
                records_skipped=skipped_count,
                signals_detected=total_signals,
            )

            # Move processed files to processed directory
            if self.processed_dir is not None:
                self.processed_dir.mkdir(parents=True, exist_ok=True)
                for csv_file in sorted(import_dir.glob("*.csv")):
                    dest = self.processed_dir / csv_file.name
                    shutil.move(str(csv_file), str(dest))
                    self.log.info("csv_file_moved", file=csv_file.name)

            # Save sync log
            await sync_log_repo.create(
                source="mls_csv",
                job_type="csv_ingest",
                success=True,
                records_fetched=result.records_fetched,
                records_created=created_count,
                records_updated=updated_count,
                records_skipped=skipped_count,
                started_at=started,
                completed_at=datetime.utcnow(),
                duration_ms=int(
                    (datetime.utcnow() - started).total_seconds() * 1000
                ),
            )

        except Exception as exc:
            result.errors.append(str(exc))
            self.log.error("ingest_failed", error=str(exc))

            # Log failed sync
            await sync_log_repo.create(
                source="mls_csv",
                job_type="csv_ingest",
                success=False,
                records_fetched=result.records_fetched,
                errors=str(exc),
                started_at=started,
                completed_at=datetime.utcnow(),
                duration_ms=int(
                    (datetime.utcnow() - started).total_seconds() * 1000
                ),
            )

        result.completed_at = datetime.utcnow()
        result.duration_ms = int(
            (result.completed_at - result.started_at).total_seconds() * 1000
        )
        return result
