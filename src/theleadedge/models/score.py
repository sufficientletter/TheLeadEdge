"""Score data models for TheLeadEdge.

``ScoreResult`` is the output of the scoring engine for a single lead --
it carries the raw/normalized score, tier assignment, top signals, and
recommended action for the Realtor.

``ScoreHistory`` captures point-in-time score snapshots for trend tracking
and scoring algorithm calibration.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .enums import Tier


class ScoreResult(BaseModel):
    """Output of the scoring engine for a single lead."""

    lead_id: int
    raw_score: float
    normalized_score: float = Field(ge=0, le=100)
    tier: Tier
    signal_count: int
    top_signals: list[str]
    stacking_bonus: float = 0.0
    stacking_rule: str | None = None
    freshness_bonus: float = 0.0
    recommended_action: str
    urgency_label: str


class ScoreHistory(BaseModel):
    """Historical score snapshot for trend tracking."""

    id: int | None = None
    lead_id: int
    score: float
    tier: Tier
    signal_count: int
    change_reason: str
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}
