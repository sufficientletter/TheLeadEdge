"""Property data models for TheLeadEdge.

Pydantic models representing real estate properties ingested from MLS CSV
exports, public records, and other data sources.  Defaults are tuned for
the Southwest Florida (SWFLA) market: state=FL, city=Naples, lat/lon bounds
covering Lee/Collier/Charlotte counties.

PII fields (owner name, phone, email, mailing address) live in
``PropertyOwner``.  NEVER log or print values from that model.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class PropertyBase(BaseModel):
    """Core property fields shared across create/read/update."""

    address: str
    city: str = "Naples"
    state: str = "FL"
    zip_code: str = Field(pattern=r"^\d{5}(-\d{4})?$")
    county: str | None = None

    # MLS identifiers
    listing_key: str | None = None
    listing_id: str | None = None

    # Physical characteristics
    bedrooms: int | None = Field(default=None, ge=0, le=50)
    bathrooms: int | None = Field(default=None, ge=0, le=50)
    living_area: float | None = Field(default=None, ge=0)
    lot_size_acres: float | None = Field(default=None, ge=0)
    year_built: int | None = Field(default=None, ge=1800, le=2030)
    property_type: str | None = None
    property_sub_type: str | None = None

    # Geolocation (SWFLA bounds)
    latitude: float | None = Field(default=None, ge=24.0, le=28.0)
    longitude: float | None = Field(default=None, ge=-83.0, le=-80.0)


class PropertyValuation(BaseModel):
    """Pricing and valuation fields."""

    list_price: float | None = Field(default=None, ge=0)
    original_list_price: float | None = Field(default=None, ge=0)
    previous_list_price: float | None = Field(default=None, ge=0)
    close_price: float | None = Field(default=None, ge=0)
    list_price_low: float | None = Field(default=None, ge=0)


class PropertyMLS(BaseModel):
    """MLS-specific fields.

    Date/timestamp fields track listing lifecycle events used by the
    signal detector to identify motivation indicators.
    """

    standard_status: str | None = None
    mls_status: str | None = None
    days_on_market: int | None = Field(default=None, ge=0)
    cumulative_dom: int | None = Field(default=None, ge=0)

    # Key dates
    listing_contract_date: date | None = None
    expiration_date: date | None = None
    on_market_date: date | None = None
    off_market_date: date | None = None
    pending_timestamp: datetime | None = None
    withdrawn_date: date | None = None
    cancellation_date: date | None = None
    close_date: date | None = None
    price_change_timestamp: datetime | None = None
    status_change_timestamp: datetime | None = None
    modification_timestamp: datetime | None = None
    original_entry_timestamp: datetime | None = None

    # Agent info
    list_agent_key: str | None = None
    list_agent_mls_id: str | None = None
    list_agent_full_name: str | None = None
    list_office_mls_id: str | None = None
    list_office_name: str | None = None
    buyer_agent_key: str | None = None

    # SWFLAMLS custom fields
    foreclosed_reo: bool = False
    potential_short_sale: bool = False
    gulf_access: bool = False


class PropertyOwner(BaseModel):
    """Owner information (NEVER log PII from this model)."""

    owner_name: str | None = None
    owner_phone: str | None = None
    owner_email: str | None = None
    owner_mailing_address: str | None = None
    is_absentee: bool = False
    is_corporate: bool = False


class Property(PropertyBase, PropertyValuation, PropertyMLS, PropertyOwner):
    """Full property model combining all field groups."""

    id: int | None = None
    address_normalized: str | None = None
    data_source: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PropertyCreate(PropertyBase, PropertyValuation, PropertyMLS, PropertyOwner):
    """Fields accepted when creating a new property."""

    data_source: str = "mls_csv"
