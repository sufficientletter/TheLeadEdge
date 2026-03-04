"""Universal data-source output model.

Every external connector (Property Appraiser, Clerk of Court, Redfin, etc.)
transforms its raw data into SourceRecord instances.  The RecordMapper then
resolves each SourceRecord to an existing PropertyRow.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class SourceRecord(BaseModel):
    """Normalized record from any external data source."""

    source_name: str                          # e.g. "collier_pa", "lee_clerk"
    source_record_id: str                     # unique ID within the source
    # e.g. "lis_pendens", "probate", "tax_delinquent"
    record_type: str

    # Address / parcel
    parcel_id: str | None = None
    street_address: str | None = None
    city: str | None = None
    state: str = "FL"
    zip_code: str | None = None

    # Event
    event_date: date | None = None
    event_type: str | None = None             # more specific than record_type

    # Raw source data (for debugging / audit)
    raw_data: dict[str, Any] = Field(default_factory=dict)

    # Owner info (NEVER log PII)
    owner_name: str | None = None
    mailing_address: str | None = None

    # Matching (populated by RecordMapper)
    matched_property_id: int | None = None
    # "parcel_id", "address_exact", "address_key", "fuzzy"
    match_method: str | None = None
    match_confidence: float | None = None     # 0.0 - 1.0

    model_config = {"from_attributes": True}
