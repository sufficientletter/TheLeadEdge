"""Factory Boy factories for TheLeadEdge test data.

All factories produce Florida (SWFLA) defaults matching the project's target
market.  Use ``FactoryClass.build()`` for Pydantic model instances (no DB)
or ``FactoryClass.create()`` when a database session is wired up.

NEVER include real PII in factory defaults -- use obviously synthetic data.
"""

from __future__ import annotations

from datetime import datetime

import factory

from theleadedge.models.enums import (
    DecayType,
    LeadStatus,
    SignalCategory,
    Tier,
)
from theleadedge.models.lead import Lead, LeadCreate
from theleadedge.models.property import Property, PropertyCreate
from theleadedge.models.score import ScoreHistory, ScoreResult
from theleadedge.models.signal import Signal, SignalCreate
from theleadedge.models.source_record import SourceRecord


class PropertyFactory(factory.Factory):
    """Factory for full Property model instances (FL / SWFLA defaults)."""

    class Meta:
        model = Property

    id = factory.Sequence(lambda n: n + 1)
    listing_key = factory.Sequence(lambda n: f"LK{100000 + n}")
    listing_id = factory.Sequence(lambda n: f"22401{n:04d}")
    address = factory.Sequence(lambda n: f"{100 + n} MAIN ST")
    city = "Naples"
    state = "FL"
    zip_code = "34102"
    county = "Collier"
    bedrooms = 3
    bathrooms = 2
    living_area = 1800.0
    lot_size_acres = 0.25
    year_built = 2005
    property_type = "Residential"
    property_sub_type = "Single Family Residence"
    latitude = 26.142
    longitude = -81.795
    list_price = 450000.0
    original_list_price = 475000.0
    standard_status = "Active"
    days_on_market = 45
    cumulative_dom = 45
    data_source = "mls_csv"


class PropertyCreateFactory(factory.Factory):
    """Factory for PropertyCreate payloads (FL / SWFLA defaults)."""

    class Meta:
        model = PropertyCreate

    listing_key = factory.Sequence(lambda n: f"LK{200000 + n}")
    listing_id = factory.Sequence(lambda n: f"22402{n:04d}")
    address = factory.Sequence(lambda n: f"{200 + n} PALM AVE")
    city = "Cape Coral"
    state = "FL"
    zip_code = "33904"
    list_price = 350000.0
    original_list_price = 375000.0
    standard_status = "Active"
    data_source = "mls_csv"


class SignalFactory(factory.Factory):
    """Factory for detected Signal instances."""

    class Meta:
        model = Signal

    id = factory.Sequence(lambda n: n + 1)
    lead_id = 1
    property_id = 1
    signal_type = "expired_listing"
    signal_category = SignalCategory.MLS
    description = "Listing expired without selling"
    source = "mls_csv"
    base_points = 15.0
    points = 15.0
    decay_type = DecayType.EXPONENTIAL
    half_life_days = 21.0
    detected_at = factory.LazyFunction(datetime.utcnow)
    is_active = True


class SignalCreateFactory(factory.Factory):
    """Factory for SignalCreate payloads."""

    class Meta:
        model = SignalCreate

    lead_id = 1
    property_id = 1
    signal_type = "price_reduction"
    signal_category = SignalCategory.MLS
    description = "Price reduced by 5%"
    source = "mls_csv"
    base_points = 12.0
    decay_type = DecayType.EXPONENTIAL
    half_life_days = 14.0


class LeadFactory(factory.Factory):
    """Factory for Lead model instances."""

    class Meta:
        model = Lead

    id = factory.Sequence(lambda n: n + 1)
    property_id = factory.Sequence(lambda n: n + 1)
    status = LeadStatus.NEW
    is_active = True
    current_score = 45.0
    tier = Tier.B
    signal_count = 2
    detected_at = factory.LazyFunction(datetime.utcnow)


class LeadCreateFactory(factory.Factory):
    """Factory for LeadCreate payloads."""

    class Meta:
        model = LeadCreate

    property_id = factory.Sequence(lambda n: n + 1)
    status = LeadStatus.NEW


class ScoreResultFactory(factory.Factory):
    """Factory for ScoreResult output objects."""

    class Meta:
        model = ScoreResult

    lead_id = 1
    raw_score = 65.0
    normalized_score = 65.0
    tier = Tier.A
    signal_count = 3
    top_signals = factory.LazyFunction(
        lambda: ["expired_listing", "price_reduction", "high_dom"]
    )
    stacking_bonus = 0.0
    stacking_rule = None
    freshness_bonus = 0.0
    recommended_action = "Priority outreach within 48 hours"
    urgency_label = "today"


class ScoreHistoryFactory(factory.Factory):
    """Factory for ScoreHistory snapshot records."""

    class Meta:
        model = ScoreHistory

    id = factory.Sequence(lambda n: n + 1)
    lead_id = 1
    score = 65.0
    tier = Tier.A
    signal_count = 3
    change_reason = "New signal: expired_listing"
    calculated_at = factory.LazyFunction(datetime.utcnow)


class SourceRecordFactory(factory.Factory):
    """Factory for SourceRecord model instances."""

    class Meta:
        model = SourceRecord

    source_name = "collier_pa"
    source_record_id = factory.Sequence(lambda n: f"SR{n:06d}")
    record_type = "property_assessment"
    parcel_id = factory.Sequence(lambda n: f"00{n:08d}")
    street_address = factory.Sequence(lambda n: f"{300 + n} PALM BLVD")
    city = "Naples"
    state = "FL"
    zip_code = "34102"
