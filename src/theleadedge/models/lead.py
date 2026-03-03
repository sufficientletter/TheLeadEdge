"""Lead data models for TheLeadEdge.

A Lead is a property identified as a potential listing opportunity.  It ties
together a ``Property``, zero or more ``Signal`` instances, a composite
score, a tier, and a lifecycle status.

Computed fields provide convenience accessors for score deltas and age
without touching the database.

Note: The relationship field is named ``property_data`` (not ``property``)
to avoid shadowing the Python builtin ``property`` descriptor, which is
required by ``@computed_field``.
"""

from datetime import datetime

from pydantic import BaseModel, Field, computed_field

from .enums import LeadStatus, Tier
from .property import Property
from .signal import Signal


class Lead(BaseModel):
    """A property identified as a potential listing opportunity."""

    id: int | None = None
    property_id: int
    status: LeadStatus = LeadStatus.NEW
    is_active: bool = True

    # Scoring
    current_score: float = 0.0
    previous_score: float | None = None
    tier: Tier = Tier.D
    signal_count: int = 0
    priority_rank: int | None = None

    # Engagement
    contacted_at: datetime | None = None
    last_touch_at: datetime | None = None
    next_touch_date: datetime | None = None
    contact_attempts: int = 0

    # CRM
    crm_id: str | None = None
    crm_synced_at: datetime | None = None

    # Timestamps
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    scored_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Relationships (populated by queries)
    # Named property_data to avoid shadowing the builtin property descriptor.
    property_data: Property | None = None
    signals: list[Signal] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def score_change(self) -> float:
        """Delta between current and previous score."""
        if self.previous_score is None:
            return 0.0
        return self.current_score - self.previous_score

    @computed_field  # type: ignore[prop-decorator]
    @property
    def days_since_detection(self) -> int:
        """Number of days since this lead was first detected."""
        return (datetime.utcnow() - self.detected_at).days

    model_config = {"from_attributes": True}


class LeadCreate(BaseModel):
    """Minimum fields to create a lead."""

    property_id: int
    status: LeadStatus = LeadStatus.NEW
