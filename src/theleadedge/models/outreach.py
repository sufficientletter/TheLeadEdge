"""Outreach data models for TheLeadEdge.

Track every contact attempt with a lead.  The Realtor handles all client
contact -- these models record what happened for pipeline analysis and
follow-up scheduling.

NEVER log PII (names, phone numbers, email addresses) from outreach events.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .enums import OutreachOutcome, OutreachType


class OutreachEvent(BaseModel):
    """Record of contact with a lead."""

    id: int | None = None
    lead_id: int
    outreach_type: OutreachType
    outcome: OutreachOutcome | None = None
    description: str | None = None
    notes: str | None = None
    performed_at: datetime = Field(default_factory=datetime.utcnow)
    follow_up_date: datetime | None = None

    model_config = {"from_attributes": True}


class OutreachEventCreate(BaseModel):
    """Fields to log a new outreach event."""

    lead_id: int
    outreach_type: OutreachType
    outcome: OutreachOutcome | None = None
    description: str | None = None
    notes: str | None = None
    follow_up_date: datetime | None = None
