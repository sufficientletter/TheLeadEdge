"""Composite lead scoring engine for TheLeadEdge.

Combines decayed signal values, freshness premiums, and stacking bonuses
into a single normalized score (0--100) with a tier assignment and
recommended action for the Realtor.

Usage::

    from pathlib import Path
    from theleadedge.scoring.config_loader import load_scoring_config
    from theleadedge.scoring.engine import ScoringEngine

    config = load_scoring_config(Path("config/scoring_weights.yaml"))
    engine = ScoringEngine(config)
    result = engine.calculate(lead_id=42, signals=signals, now=datetime.utcnow())
    print(result.tier, result.recommended_action)

The ``calculate`` method is **deterministic**: given the same signals and
``now`` timestamp, it always produces the same ``ScoreResult``.  No
database access, no side effects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from theleadedge.models.score import ScoreResult

from .decay import apply_decay, freshness_premium
from .stacking import calculate_stacking_bonus

if TYPE_CHECKING:
    from datetime import datetime

    from theleadedge.models.signal import Signal
    from theleadedge.scoring.config_loader import ScoringConfig


class ScoringEngine:
    """Multi-signal lead scoring engine.

    Calculates a composite score from active signals by applying temporal
    decay, freshness premiums, and stacking bonuses, then maps the result
    to a tier with an action recommendation.

    Attributes
    ----------
    MAX_SCORE : float
        Hard ceiling for normalized scores.
    """

    MAX_SCORE: float = 100.0

    def __init__(self, config: ScoringConfig) -> None:
        self.config = config

    def calculate(
        self,
        lead_id: int,
        signals: list[Signal],
        now: datetime,
    ) -> ScoreResult:
        """Score a lead based on its current signals.

        Parameters
        ----------
        lead_id:
            Database ID of the lead being scored.
        signals:
            All signals associated with the lead (active and inactive).
            Inactive signals are skipped automatically.
        now:
            Reference timestamp for decay and freshness calculations.

        Returns
        -------
        ScoreResult
            Complete scoring output with tier, top signals, bonuses, and
            recommended action.
        """
        total_points = 0.0
        signal_contributions: dict[str, float] = {}
        active_signal_types: set[str] = set()
        total_freshness = 0.0

        for signal in signals:
            if not signal.is_active:
                continue

            sc = self.config.get_signal_config(signal.signal_type)
            if sc is None or not sc.is_active:
                continue

            decayed = apply_decay(
                base_points=sc.base_points,
                detected_at=signal.detected_at,
                now=now,
                decay_type=sc.decay_type,
                half_life_days=sc.half_life_days,
            )

            premium = freshness_premium(signal.detected_at, now)
            adjusted = decayed * premium
            freshness_delta = adjusted - decayed
            total_freshness += freshness_delta

            if adjusted > 0:
                active_signal_types.add(signal.signal_type)
                signal_contributions[signal.signal_type] = (
                    signal_contributions.get(signal.signal_type, 0.0) + adjusted
                )
                total_points += adjusted

        # Stacking bonus (best single rule)
        stacking_bonus, stacking_rule = calculate_stacking_bonus(
            active_signal_types,
            signal_contributions,
            self.config.stacking_rules,
        )
        total_points += stacking_bonus

        # Normalize to [0, MAX_SCORE] and assign tier
        normalized = min(self.MAX_SCORE, max(0.0, total_points))
        tier, tier_cfg = self.config.get_tier_for_score(normalized)

        top_signals = sorted(
            signal_contributions.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:3]

        return ScoreResult(
            lead_id=lead_id,
            raw_score=round(total_points, 2),
            normalized_score=round(normalized, 1),
            tier=tier,
            signal_count=len(active_signal_types),
            top_signals=[s[0] for s in top_signals],
            stacking_bonus=round(stacking_bonus, 1),
            stacking_rule=stacking_rule,
            freshness_bonus=round(total_freshness, 1),
            recommended_action=tier_cfg.action,
            urgency_label=tier_cfg.urgency,
        )
