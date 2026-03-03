"""TheLeadEdge data models.

Re-exports all Pydantic models and enums for convenient access::

    from theleadedge.models import Property, Lead, Signal, Tier
"""

from .enums import (
    DecayType,
    LeadStatus,
    MLSStatus,
    OutreachOutcome,
    OutreachType,
    SignalCategory,
    Tier,
)
from .lead import Lead, LeadCreate
from .outreach import OutreachEvent, OutreachEventCreate
from .property import (
    Property,
    PropertyBase,
    PropertyCreate,
    PropertyMLS,
    PropertyOwner,
    PropertyValuation,
)
from .score import ScoreHistory, ScoreResult
from .signal import Signal, SignalConfig, SignalCreate

__all__ = [
    # Enums
    "Tier",
    "LeadStatus",
    "SignalCategory",
    "DecayType",
    "MLSStatus",
    "OutreachType",
    "OutreachOutcome",
    # Property
    "Property",
    "PropertyCreate",
    "PropertyBase",
    "PropertyValuation",
    "PropertyMLS",
    "PropertyOwner",
    # Signal
    "Signal",
    "SignalCreate",
    "SignalConfig",
    # Score
    "ScoreResult",
    "ScoreHistory",
    # Outreach
    "OutreachEvent",
    "OutreachEventCreate",
    # Lead
    "Lead",
    "LeadCreate",
]
