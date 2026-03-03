"""Temporal decay functions for signal score attenuation.

Signals lose value over time -- a price reduction from yesterday is more
actionable than one from three months ago.  These functions model that
decline using four distinct curves, each suited to different signal types.

All functions are **deterministic**: ``now`` is always passed explicitly
so that scoring is reproducible in tests and batch re-scores.

Decay types (from ``DecayType`` enum):

* **LINEAR** -- Steady decline to zero over ``2 * half_life_days``.
* **EXPONENTIAL** -- Rapid initial decline; asymptotically approaches zero.
* **STEP** -- Discrete drops at 7 / 30 / 90 / 180-day boundaries.
* **ESCALATING** -- Score *increases* as a deadline approaches (pre-foreclosure).

``freshness_premium`` is a separate multiplicative bonus applied *on top* of
the decayed value for signals detected very recently (under 48 hours).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from theleadedge.models.enums import DecayType

if TYPE_CHECKING:
    from datetime import datetime


def apply_decay(
    base_points: float,
    detected_at: datetime,
    now: datetime,
    decay_type: DecayType,
    half_life_days: float = 30.0,
    deadline: datetime | None = None,
) -> float:
    """Apply time-decay to a signal's base point value.

    Parameters
    ----------
    base_points:
        The signal's full undecayed point value.
    detected_at:
        When the signal was first detected.
    now:
        Current reference timestamp (passed explicitly for determinism).
    decay_type:
        Which decay curve to apply.
    half_life_days:
        Controls the rate of LINEAR and EXPONENTIAL decay.
    deadline:
        Required for ESCALATING decay -- the date by which urgency peaks.

    Returns
    -------
    float
        Decayed point value, clamped to ``[0, +inf)``.  Never negative.
    """
    age_days = max(0.0, (now - detected_at).total_seconds() / 86400)

    if decay_type == DecayType.LINEAR:
        max_days = half_life_days * 2
        if age_days >= max_days:
            return 0.0
        return base_points * (1.0 - age_days / max_days)

    if decay_type == DecayType.EXPONENTIAL:
        if half_life_days <= 0:
            return base_points
        return base_points * math.pow(0.5, age_days / half_life_days)

    if decay_type == DecayType.STEP:
        if age_days <= 7:
            return base_points * 1.0
        if age_days <= 30:
            return base_points * 0.75
        if age_days <= 90:
            return base_points * 0.50
        if age_days <= 180:
            return base_points * 0.25
        return base_points * 0.05

    if decay_type == DecayType.ESCALATING:
        if deadline is None:
            return base_points
        days_until = max(0.0, (deadline - now).total_seconds() / 86400)
        total_window = max(1.0, (deadline - detected_at).total_seconds() / 86400)
        urgency = 1.0 - (days_until / total_window)
        return base_points * max(0.3, min(1.5, 0.3 + urgency * 1.2))

    # Unknown decay type -- return unmodified
    return base_points


def freshness_premium(detected_at: datetime, now: datetime) -> float:
    """Bonus multiplier for very fresh signals.

    Rewards leads with recently-detected signals because timely outreach
    dramatically increases conversion probability.

    Returns
    -------
    float
        Multiplier between 1.0 (no bonus) and 1.5 (detected <4 hours ago).
    """
    hours_since = max(0.0, (now - detected_at).total_seconds() / 3600)
    if hours_since <= 4:
        return 1.5
    if hours_since <= 24:
        return 1.3
    if hours_since <= 48:
        return 1.15
    return 1.0
