"""Unit tests for temporal decay functions.

Tests all four decay curves (linear, exponential, step, escalating) and
the freshness premium multiplier.  All tests use fixed timestamps for
deterministic results.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from theleadedge.models.enums import DecayType
from theleadedge.scoring.decay import apply_decay, freshness_premium

# ---------------------------------------------------------------------------
# Linear Decay
# ---------------------------------------------------------------------------


class TestLinearDecay:
    """Linear decay tests: steady decline over 2 * half_life_days."""

    def test_linear_decay_at_zero_days(self, now: datetime) -> None:
        """Signal detected right now retains full base points."""
        result = apply_decay(
            base_points=10.0,
            detected_at=now,
            now=now,
            decay_type=DecayType.LINEAR,
            half_life_days=30.0,
        )
        assert result == pytest.approx(10.0)

    def test_linear_decay_at_half_life(self, now: datetime) -> None:
        """At exactly half_life_days, signal retains 50% of base points."""
        detected = now - timedelta(days=30)
        result = apply_decay(
            base_points=10.0,
            detected_at=detected,
            now=now,
            decay_type=DecayType.LINEAR,
            half_life_days=30.0,
        )
        assert result == pytest.approx(5.0)

    def test_linear_decay_at_double_half_life(self, now: datetime) -> None:
        """At 2 * half_life_days, signal value reaches zero."""
        detected = now - timedelta(days=60)
        result = apply_decay(
            base_points=10.0,
            detected_at=detected,
            now=now,
            decay_type=DecayType.LINEAR,
            half_life_days=30.0,
        )
        assert result == pytest.approx(0.0)

    def test_linear_decay_past_expiry(self, now: datetime) -> None:
        """Signals older than 2 * half_life_days return zero."""
        detected = now - timedelta(days=120)
        result = apply_decay(
            base_points=15.0,
            detected_at=detected,
            now=now,
            decay_type=DecayType.LINEAR,
            half_life_days=30.0,
        )
        assert result == 0.0


# ---------------------------------------------------------------------------
# Exponential Decay
# ---------------------------------------------------------------------------


class TestExponentialDecay:
    """Exponential decay tests: rapid initial decline, asymptotic to zero."""

    def test_exponential_decay_at_zero(self, now: datetime) -> None:
        """Signal detected right now retains full base points."""
        result = apply_decay(
            base_points=12.0,
            detected_at=now,
            now=now,
            decay_type=DecayType.EXPONENTIAL,
            half_life_days=14.0,
        )
        assert result == pytest.approx(12.0)

    def test_exponential_decay_at_half_life(self, now: datetime) -> None:
        """At exactly half_life_days, signal retains 50% of base points."""
        detected = now - timedelta(days=14)
        result = apply_decay(
            base_points=12.0,
            detected_at=detected,
            now=now,
            decay_type=DecayType.EXPONENTIAL,
            half_life_days=14.0,
        )
        assert result == pytest.approx(6.0, rel=1e-3)

    def test_exponential_never_reaches_zero(self, now: datetime) -> None:
        """Even after a long time, exponential decay never truly hits zero."""
        detected = now - timedelta(days=365)
        result = apply_decay(
            base_points=10.0,
            detected_at=detected,
            now=now,
            decay_type=DecayType.EXPONENTIAL,
            half_life_days=14.0,
        )
        assert result > 0.0
        # After 365 days with 14-day half life: 0.5^(365/14) ~ very small
        assert result < 0.01


# ---------------------------------------------------------------------------
# Step Decay
# ---------------------------------------------------------------------------


class TestStepDecay:
    """Step decay tests: discrete drops at 7/30/90/180-day boundaries."""

    @pytest.mark.parametrize(
        ("age_days", "expected_fraction"),
        [
            (0, 1.0),       # Within 7 days: full value
            (5, 1.0),       # Within 7 days: full value
            (7, 1.0),       # At boundary: still full
            (8, 0.75),      # Past 7 days: 75%
            (20, 0.75),     # Within 30 days: 75%
            (30, 0.75),     # At 30 boundary: still 75%
            (31, 0.50),     # Past 30 days: 50%
            (60, 0.50),     # Within 90 days: 50%
            (90, 0.50),     # At 90 boundary: still 50%
            (91, 0.25),     # Past 90 days: 25%
            (150, 0.25),    # Within 180 days: 25%
            (180, 0.25),    # At 180 boundary: still 25%
            (181, 0.05),    # Past 180 days: 5%
            (365, 0.05),    # Far past: 5%
        ],
    )
    def test_step_decay_brackets(
        self,
        now: datetime,
        age_days: int,
        expected_fraction: float,
    ) -> None:
        """Step decay applies correct multiplier at each bracket boundary."""
        base = 20.0
        detected = now - timedelta(days=age_days)
        result = apply_decay(
            base_points=base,
            detected_at=detected,
            now=now,
            decay_type=DecayType.STEP,
        )
        assert result == pytest.approx(base * expected_fraction)


# ---------------------------------------------------------------------------
# Escalating Decay
# ---------------------------------------------------------------------------


class TestEscalatingDecay:
    """Escalating decay tests: value increases as deadline approaches."""

    def test_escalating_near_deadline(self, now: datetime) -> None:
        """Close to deadline, urgency is high -- score approaches max."""
        detected = now - timedelta(days=50)
        deadline = now + timedelta(days=5)
        result = apply_decay(
            base_points=20.0,
            detected_at=detected,
            now=now,
            decay_type=DecayType.ESCALATING,
            deadline=deadline,
        )
        # Urgency high: closer to 1.5x multiplier
        assert result > 20.0
        assert result <= 30.0  # max is 1.5 * base

    def test_escalating_far_from_deadline(self, now: datetime) -> None:
        """Far from deadline, urgency is low -- score near base level."""
        detected = now - timedelta(days=5)
        deadline = now + timedelta(days=55)
        result = apply_decay(
            base_points=20.0,
            detected_at=detected,
            now=now,
            decay_type=DecayType.ESCALATING,
            deadline=deadline,
        )
        # Urgency low: closer to 0.3x floor
        assert result >= 6.0   # 0.3 * 20
        assert result < 20.0   # Less than full base

    def test_escalating_no_deadline(self, now: datetime) -> None:
        """Without a deadline, escalating decay returns unmodified base."""
        detected = now - timedelta(days=10)
        result = apply_decay(
            base_points=20.0,
            detected_at=detected,
            now=now,
            decay_type=DecayType.ESCALATING,
            deadline=None,
        )
        assert result == pytest.approx(20.0)


# ---------------------------------------------------------------------------
# Freshness Premium
# ---------------------------------------------------------------------------


class TestFreshnessPremium:
    """Freshness premium tests: multiplier bonus for very fresh signals."""

    def test_freshness_premium_within_4hrs(self, now: datetime) -> None:
        """Signal detected < 4 hours ago gets 1.5x multiplier."""
        detected = now - timedelta(hours=2)
        result = freshness_premium(detected, now)
        assert result == pytest.approx(1.5)

    def test_freshness_premium_next_day(self, now: datetime) -> None:
        """Signal detected 24-48 hours ago gets 1.15x multiplier."""
        detected = now - timedelta(hours=36)
        result = freshness_premium(detected, now)
        assert result == pytest.approx(1.15)

    def test_freshness_premium_old(self, now: datetime) -> None:
        """Signal detected > 48 hours ago gets no bonus (1.0x)."""
        detected = now - timedelta(hours=72)
        result = freshness_premium(detected, now)
        assert result == pytest.approx(1.0)

    def test_freshness_premium_exactly_at_boundary(self, now: datetime) -> None:
        """Signal detected exactly at 4-hour boundary gets 1.5x."""
        detected = now - timedelta(hours=4)
        result = freshness_premium(detected, now)
        assert result == pytest.approx(1.5)

    def test_freshness_premium_just_past_4hrs(self, now: datetime) -> None:
        """Signal detected just past 4 hours gets 1.3x."""
        detected = now - timedelta(hours=4, minutes=1)
        result = freshness_premium(detected, now)
        assert result == pytest.approx(1.3)
