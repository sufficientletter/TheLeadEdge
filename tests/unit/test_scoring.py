"""Unit tests for the composite scoring engine.

Tests the ScoringEngine.calculate() method which combines decayed signal
values, freshness premiums, and stacking bonuses into a normalized score
with tier assignment.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from tests.factories import SignalFactory
from theleadedge.models.enums import DecayType, SignalCategory, Tier
from theleadedge.scoring.engine import ScoringEngine

if TYPE_CHECKING:
    from theleadedge.scoring.config_loader import ScoringConfig


class TestScoringEngine:
    """ScoringEngine.calculate() tests."""

    def test_score_single_signal(
        self, scoring_config: ScoringConfig, now: datetime
    ) -> None:
        """A lead with one active signal produces a non-zero score."""
        engine = ScoringEngine(scoring_config)
        signals = [
            SignalFactory.build(
                lead_id=1,
                signal_type="expired_listing",
                signal_category=SignalCategory.MLS,
                base_points=15.0,
                decay_type=DecayType.EXPONENTIAL,
                half_life_days=21.0,
                detected_at=now - timedelta(days=5),
                is_active=True,
            ),
        ]
        result = engine.calculate(lead_id=1, signals=signals, now=now)
        assert result.normalized_score > 0
        assert result.signal_count == 1
        assert "expired_listing" in result.top_signals

    def test_score_multiple_signals(
        self, scoring_config: ScoringConfig, now: datetime
    ) -> None:
        """Multiple active signals produce a higher score than one."""
        engine = ScoringEngine(scoring_config)
        single = [
            SignalFactory.build(
                lead_id=1,
                signal_type="expired_listing",
                detected_at=now - timedelta(days=5),
                is_active=True,
            ),
        ]
        multiple = [
            SignalFactory.build(
                lead_id=1,
                signal_type="expired_listing",
                detected_at=now - timedelta(days=5),
                is_active=True,
            ),
            SignalFactory.build(
                lead_id=1,
                signal_type="price_reduction",
                signal_category=SignalCategory.MLS,
                base_points=8.0,
                decay_type=DecayType.EXPONENTIAL,
                half_life_days=14.0,
                detected_at=now - timedelta(days=3),
                is_active=True,
            ),
            SignalFactory.build(
                lead_id=1,
                signal_type="high_dom",
                signal_category=SignalCategory.MLS,
                base_points=11.0,
                decay_type=DecayType.STEP,
                half_life_days=60.0,
                detected_at=now - timedelta(days=2),
                is_active=True,
            ),
        ]
        r_single = engine.calculate(lead_id=1, signals=single, now=now)
        r_multi = engine.calculate(lead_id=1, signals=multiple, now=now)
        assert r_multi.normalized_score > r_single.normalized_score
        assert r_multi.signal_count == 3

    def test_score_with_stacking_bonus(
        self, scoring_config: ScoringConfig, now: datetime
    ) -> None:
        """Distressed seller stacking bonus applies when all 3 signals present."""
        engine = ScoringEngine(scoring_config)
        signals = [
            SignalFactory.build(
                lead_id=1,
                signal_type="expired_listing",
                detected_at=now - timedelta(hours=2),
                is_active=True,
            ),
            SignalFactory.build(
                lead_id=1,
                signal_type="price_reduction_multiple",
                signal_category=SignalCategory.MLS,
                base_points=14.0,
                decay_type=DecayType.EXPONENTIAL,
                half_life_days=21.0,
                detected_at=now - timedelta(hours=2),
                is_active=True,
            ),
            SignalFactory.build(
                lead_id=1,
                signal_type="high_dom",
                signal_category=SignalCategory.MLS,
                base_points=11.0,
                decay_type=DecayType.STEP,
                half_life_days=60.0,
                detected_at=now - timedelta(hours=2),
                is_active=True,
            ),
        ]
        result = engine.calculate(lead_id=1, signals=signals, now=now)
        assert result.stacking_bonus > 0
        assert result.stacking_rule == "distressed_seller"

    def test_score_capped_at_100(
        self, scoring_config: ScoringConfig, now: datetime
    ) -> None:
        """Normalized score never exceeds 100 even with massive signal stacking."""
        engine = ScoringEngine(scoring_config)
        # Create many high-value signals to exceed 100
        signals = []
        for sig_type in [
            "foreclosure_flag",
            "pre_foreclosure",
            "price_reduction_severe",
            "expired_listing",
            "high_dom",
            "short_sale_flag",
            "price_reduction_multiple",
            "back_on_market",
            "withdrawn_relisted",
        ]:
            sc = scoring_config.get_signal_config(sig_type)
            if sc is not None:
                signals.append(
                    SignalFactory.build(
                        lead_id=1,
                        signal_type=sig_type,
                        signal_category=SignalCategory.MLS,
                        base_points=sc.base_points,
                        decay_type=sc.decay_type,
                        half_life_days=sc.half_life_days,
                        detected_at=now - timedelta(hours=1),
                        is_active=True,
                    )
                )
        result = engine.calculate(lead_id=1, signals=signals, now=now)
        assert result.normalized_score <= 100.0

    def test_score_tier_s(
        self, scoring_config: ScoringConfig, now: datetime
    ) -> None:
        """Score >= 80 maps to S-tier."""
        engine = ScoringEngine(scoring_config)
        # Stack enough fresh signals to reach S-tier
        signals = []
        for sig_type in [
            "foreclosure_flag",
            "pre_foreclosure",
            "price_reduction_severe",
            "expired_listing",
            "high_dom",
        ]:
            sc = scoring_config.get_signal_config(sig_type)
            if sc is not None:
                signals.append(
                    SignalFactory.build(
                        lead_id=1,
                        signal_type=sig_type,
                        signal_category=SignalCategory.MLS,
                        base_points=sc.base_points,
                        decay_type=sc.decay_type,
                        half_life_days=sc.half_life_days,
                        detected_at=now - timedelta(hours=1),
                        is_active=True,
                    )
                )
        result = engine.calculate(lead_id=1, signals=signals, now=now)
        assert result.normalized_score >= 80.0
        assert result.tier == Tier.S

    def test_score_tier_d(
        self, scoring_config: ScoringConfig, now: datetime
    ) -> None:
        """A very old, low-value signal produces a D-tier score."""
        engine = ScoringEngine(scoring_config)
        signals = [
            SignalFactory.build(
                lead_id=1,
                signal_type="listing_price_low_set",
                signal_category=SignalCategory.MLS,
                base_points=6.0,
                decay_type=DecayType.LINEAR,
                half_life_days=30.0,
                detected_at=now - timedelta(days=50),
                is_active=True,
            ),
        ]
        result = engine.calculate(lead_id=1, signals=signals, now=now)
        assert result.normalized_score < 20.0
        assert result.tier == Tier.D

    def test_score_no_signals(
        self, scoring_config: ScoringConfig, now: datetime
    ) -> None:
        """A lead with no signals scores zero, tier D."""
        engine = ScoringEngine(scoring_config)
        result = engine.calculate(lead_id=1, signals=[], now=now)
        assert result.normalized_score == 0.0
        assert result.tier == Tier.D
        assert result.signal_count == 0

    def test_score_deterministic(
        self, scoring_config: ScoringConfig, now: datetime
    ) -> None:
        """Same inputs always produce the same output."""
        engine = ScoringEngine(scoring_config)
        signals = [
            SignalFactory.build(
                lead_id=1,
                signal_type="expired_listing",
                detected_at=now - timedelta(days=10),
                is_active=True,
            ),
            SignalFactory.build(
                lead_id=1,
                signal_type="price_reduction",
                signal_category=SignalCategory.MLS,
                base_points=8.0,
                decay_type=DecayType.EXPONENTIAL,
                half_life_days=14.0,
                detected_at=now - timedelta(days=7),
                is_active=True,
            ),
        ]
        result_a = engine.calculate(lead_id=1, signals=signals, now=now)
        result_b = engine.calculate(lead_id=1, signals=signals, now=now)
        assert result_a.normalized_score == result_b.normalized_score
        assert result_a.tier == result_b.tier
        assert result_a.stacking_bonus == result_b.stacking_bonus

    def test_freshness_premium_applied(
        self, scoring_config: ScoringConfig, now: datetime
    ) -> None:
        """A very fresh signal gets a higher score than the same signal aged."""
        engine = ScoringEngine(scoring_config)
        fresh = [
            SignalFactory.build(
                lead_id=1,
                signal_type="expired_listing",
                detected_at=now - timedelta(hours=1),
                is_active=True,
            ),
        ]
        old = [
            SignalFactory.build(
                lead_id=1,
                signal_type="expired_listing",
                detected_at=now - timedelta(days=10),
                is_active=True,
            ),
        ]
        r_fresh = engine.calculate(lead_id=1, signals=fresh, now=now)
        r_old = engine.calculate(lead_id=1, signals=old, now=now)
        assert r_fresh.normalized_score > r_old.normalized_score
        assert r_fresh.freshness_bonus > 0
