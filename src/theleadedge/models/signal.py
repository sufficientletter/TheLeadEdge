"""Signal data models for TheLeadEdge.

Signals are discrete indicators of seller/buyer motivation detected from
MLS data, public records, life events, and market conditions.  Each signal
carries a base point value and a temporal decay function that reduces its
contribution to the composite lead score over time.

``SignalConfig`` defines signal *types* (loaded from scoring_weights.yaml).
``Signal`` represents a *detected instance* of a signal on a specific lead.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import DecayType, SignalCategory


class SignalConfig(BaseModel):
    """Configuration entry for a signal type (loaded from YAML)."""

    signal_type: str
    category: SignalCategory
    base_points: float
    decay_type: DecayType = DecayType.LINEAR
    half_life_days: float = 30.0
    description: str = ""
    is_active: bool = True


class Signal(BaseModel):
    """A detected signal indicating seller/buyer motivation."""

    id: int | None = None
    lead_id: int
    property_id: int
    signal_type: str
    signal_category: SignalCategory
    description: str | None = None
    source: str | None = None
    source_ref: str | None = None
    event_date: date | None = None
    raw_data: dict[str, Any] | None = None

    # Scoring
    points: float = 0.0
    base_points: float = 0.0
    weight: float = 1.0
    decay_type: DecayType = DecayType.LINEAR
    half_life_days: float | None = None

    # Lifecycle
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class SignalCreate(BaseModel):
    """Fields required to register a new signal."""

    lead_id: int
    property_id: int
    signal_type: str
    signal_category: SignalCategory
    description: str | None = None
    source: str | None = None
    event_date: date | None = None
    base_points: float
    decay_type: DecayType = DecayType.LINEAR
    half_life_days: float | None = None
    raw_data: dict[str, Any] | None = None
