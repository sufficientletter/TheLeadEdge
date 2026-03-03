"""Score pipeline for TheLeadEdge.

Orchestrates the scoring of individual leads and batch re-scoring of all
active leads.  For each lead:

1. Fetch active signals from the database.
2. Convert ORM rows to Pydantic ``Signal`` models.
3. Run the ``ScoringEngine.calculate()`` method.
4. Update the lead row with new score and tier.
5. Save a ``ScoreHistoryRow`` snapshot for trend tracking.
6. Detect tier changes for alerting.

The pipeline owns the database interaction; the engine itself is pure
computation with no side effects.

IMPORTANT: Never log PII (addresses, owner names, phone numbers).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from theleadedge.models.enums import SignalCategory
from theleadedge.models.signal import Signal
from theleadedge.storage.repositories import (
    LeadRepo,
    ScoreHistoryRepo,
    SignalRepo,
)

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

    from theleadedge.models.score import ScoreResult
    from theleadedge.scoring.engine import ScoringEngine

logger = structlog.get_logger()


class ScorePipeline:
    """Orchestrates lead scoring with database persistence.

    Parameters
    ----------
    scoring_engine:
        Configured ``ScoringEngine`` instance with loaded signal weights.
    """

    def __init__(self, scoring_engine: ScoringEngine) -> None:
        self.engine = scoring_engine
        self.log = logger.bind(component="score_pipeline")

    async def score_lead(
        self,
        session: AsyncSession,
        lead_id: int,
        now: datetime,
    ) -> ScoreResult | None:
        """Score a single lead.

        Fetches active signals, calculates score, updates the lead row,
        and saves a score history snapshot.

        Parameters
        ----------
        session:
            Active async database session (caller manages transaction).
        lead_id:
            Database ID of the lead to score.
        now:
            Reference timestamp for decay and freshness calculations.

        Returns
        -------
        ScoreResult | None
            Scoring result, or ``None`` if the lead was not found.
        """
        lead_repo = LeadRepo(session)
        signal_repo = SignalRepo(session)
        history_repo = ScoreHistoryRepo(session)

        # Verify lead exists
        lead_row = await lead_repo.get_by_id(lead_id)
        if lead_row is None:
            self.log.warning("lead_not_found", lead_id=lead_id)
            return None

        # Deactivate expired signals first
        expired_count = await signal_repo.deactivate_expired(now)
        if expired_count > 0:
            self.log.info(
                "expired_signals_deactivated",
                lead_id=lead_id,
                count=expired_count,
            )

        # Fetch active signals and convert to Pydantic models
        signal_rows = await signal_repo.get_active_by_lead_id(lead_id)
        signals = [
            Signal(
                id=row.id,
                lead_id=row.lead_id,
                property_id=row.property_id,
                signal_type=row.signal_type,
                signal_category=SignalCategory(row.signal_category),
                description=row.description,
                source=row.source,
                source_ref=row.source_ref,
                event_date=row.event_date,
                points=row.points,
                base_points=row.base_points,
                weight=row.weight,
                decay_type=row.decay_type,
                half_life_days=row.half_life_days,
                detected_at=row.detected_at,
                expires_at=row.expires_at,
                is_active=row.is_active,
            )
            for row in signal_rows
        ]

        # Calculate score (pure computation, no side effects)
        result = self.engine.calculate(lead_id=lead_id, signals=signals, now=now)

        # Detect tier change
        old_tier = lead_row.tier
        tier_changed = old_tier != result.tier

        # Update lead row
        await lead_repo.update_score(
            id=lead_id,
            score=result.normalized_score,
            tier=result.tier,
            signal_count=result.signal_count,
        )

        # Build change reason for history
        if tier_changed:
            change_reason = f"Tier change: {old_tier} -> {result.tier}"
        else:
            change_reason = "Periodic re-score"

        # Save score history snapshot
        await history_repo.create(
            lead_id=lead_id,
            score=result.normalized_score,
            tier=result.tier,
            signal_count=result.signal_count,
            change_reason=change_reason,
            calculated_at=now,
        )

        self.log.info(
            "lead_scored",
            lead_id=lead_id,
            score=result.normalized_score,
            tier=result.tier,
            signal_count=result.signal_count,
            tier_changed=tier_changed,
            stacking_rule=result.stacking_rule,
        )

        return result

    async def score_all_active(
        self,
        session: AsyncSession,
        now: datetime,
    ) -> list[ScoreResult]:
        """Re-score all active leads.

        Parameters
        ----------
        session:
            Active async database session (caller manages transaction).
        now:
            Reference timestamp for decay and freshness calculations.

        Returns
        -------
        list[ScoreResult]
            Scoring results for all active leads.
        """
        lead_repo = LeadRepo(session)
        active_leads = await lead_repo.get_active()

        results: list[ScoreResult] = []
        tier_changes = 0

        for lead_row in active_leads:
            result = await self.score_lead(session, lead_row.id, now)
            if result is not None:
                results.append(result)
                if lead_row.tier != result.tier:
                    tier_changes += 1

        self.log.info(
            "batch_scoring_complete",
            leads_scored=len(results),
            tier_changes=tier_changes,
        )

        return results
