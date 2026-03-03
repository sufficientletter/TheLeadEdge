"""Daily briefing generator for TheLeadEdge.

Queries the database for hot leads, tier changes, pipeline summary, and
follow-ups due, then renders an HTML email body from the Jinja2 template.

The generated HTML is PII-safe: it references leads by MLS number and
city/ZIP only -- never by owner name, phone, or email address.

Usage::

    from pathlib import Path
    from theleadedge.pipelines.briefing import BriefingGenerator
    from theleadedge.scoring.config_loader import load_scoring_config

    config = load_scoring_config(Path("config/scoring_weights.yaml"))
    template_dir = Path("src/theleadedge/notifications/templates")
    generator = BriefingGenerator(config, template_dir)

    async with get_session() as session:
        html = await generator.generate(session, datetime.utcnow())
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import structlog
from jinja2 import Environment, FileSystemLoader

from theleadedge.storage.queries import (
    get_follow_ups_due,
    get_hot_leads,
    get_pipeline_summary,
    get_tier_changes,
)

if TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.ext.asyncio import AsyncSession

    from theleadedge.scoring.config_loader import ScoringConfig

logger = structlog.get_logger()


class BriefingGenerator:
    """Generate daily briefing HTML from database state.

    Parameters
    ----------
    config:
        Scoring configuration (used for tier threshold display).
    template_dir:
        Directory containing Jinja2 templates (must contain
        ``daily_briefing.html``).
    """

    def __init__(self, config: ScoringConfig, template_dir: Path) -> None:
        self.config = config
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
        )
        self.log = logger.bind(component="briefing_generator")

    async def generate(
        self,
        session: AsyncSession,
        now: datetime,
    ) -> str:
        """Generate daily briefing HTML.

        Queries the database for:
        - Hot leads (B-tier and above)
        - Pipeline summary (counts by tier)
        - Tier changes in the last 24 hours
        - Follow-ups due now or overdue

        Parameters
        ----------
        session:
            Active async database session.
        now:
            Reference timestamp for the briefing.

        Returns
        -------
        str
            Rendered HTML string ready for email delivery.
        """
        hot_leads = await get_hot_leads(session, min_tier="B")
        pipeline = await get_pipeline_summary(session)
        tier_changes = await get_tier_changes(
            session, since=now - timedelta(hours=24)
        )
        follow_ups = await get_follow_ups_due(session, before=now)

        self.log.info(
            "briefing_data_gathered",
            hot_leads=len(hot_leads),
            tier_changes=len(tier_changes),
            follow_ups=len(follow_ups),
            total_active=pipeline.get("total_active", 0),
        )

        template = self.env.get_template("daily_briefing.html")
        html = template.render(
            date=now.strftime("%A, %B %d, %Y"),
            hot_leads=hot_leads,
            pipeline=pipeline,
            tier_changes=tier_changes,
            follow_ups=follow_ups,
            now=now,
        )

        self.log.info("briefing_generated", html_length=len(html))
        return html
