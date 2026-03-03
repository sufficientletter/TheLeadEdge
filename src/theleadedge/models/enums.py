"""Shared enumerations for TheLeadEdge.

All enums use StrEnum for JSON-friendly serialization and readable database values.
Tier thresholds are defined here as documentation; actual thresholds live in Settings.
"""

from enum import StrEnum


class Tier(StrEnum):
    """Lead priority tier based on composite score.

    S (80-100): Immediate personal outreach — same day
    A (60-79):  Priority outreach within 48 hours
    B (40-59):  Scheduled outreach sequence — this week
    C (20-39):  Drip campaign, monthly touch
    D (0-19):   Monitor only — no active outreach
    """

    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class LeadStatus(StrEnum):
    """Lifecycle status of a lead from detection through conversion."""

    NEW = "new"
    CONTACTED = "contacted"
    MEETING = "meeting"
    LISTING = "listing"
    CLOSED = "closed"
    LOST = "lost"
    ARCHIVED = "archived"


class SignalCategory(StrEnum):
    """Category of a behavioral or data signal.

    Signals are grouped by source for weighting and analysis.
    """

    MLS = "mls"
    PUBLIC_RECORD = "public_record"
    LIFE_EVENT = "life_event"
    MARKET = "market"
    DIGITAL = "digital"


class DecayType(StrEnum):
    """Temporal decay function applied to signal scores.

    LINEAR:      Steady decline over time (general purpose)
    EXPONENTIAL: Rapid initial decline (time-sensitive signals like price drops)
    STEP:        Discrete drops at intervals (status changes)
    ESCALATING:  Score INCREASES as deadline approaches (pre-foreclosure, tax sale)
    """

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    STEP = "step"
    ESCALATING = "escalating"


class MLSStatus(StrEnum):
    """Standard RESO-aligned MLS listing statuses.

    These map to the StatusChangeTimestamp and StandardStatus fields
    in RESO Data Dictionary 2.0.
    """

    ACTIVE = "Active"
    ACTIVE_UNDER_CONTRACT = "Active Under Contract"
    PENDING = "Pending"
    CLOSED = "Closed"
    EXPIRED = "Expired"
    WITHDRAWN = "Withdrawn"
    CANCELED = "Canceled"
    COMING_SOON = "Coming Soon"
    HOLD = "Hold"
    DELETE = "Delete"


class OutreachType(StrEnum):
    """Method of outreach to a lead."""

    PHONE_CALL = "phone_call"
    EMAIL = "email"
    DIRECT_MAIL = "direct_mail"
    DOOR_KNOCK = "door_knock"
    HANDWRITTEN_NOTE = "handwritten_note"
    CMA_SENT = "cma_sent"
    TEXT = "text"


class OutreachOutcome(StrEnum):
    """Result of an outreach attempt."""

    NO_ANSWER = "no_answer"
    VOICEMAIL = "voicemail"
    ANSWERED = "answered"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    CALLBACK_REQUESTED = "callback_requested"
    MEETING_SET = "meeting_set"
    WRONG_NUMBER = "wrong_number"
    DO_NOT_CONTACT = "do_not_contact"
