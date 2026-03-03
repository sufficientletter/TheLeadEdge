"""CLI entry point for TheLeadEdge.

Usage:
    python -m theleadedge import     # Import CSVs from data/mls_imports/
    python -m theleadedge score      # Re-score all active leads
    python -m theleadedge briefing   # Generate and send daily briefing
    python -m theleadedge run        # Import -> Score -> Briefing (full pipeline)

Each command loads settings from ``.env``, initializes the database, and
runs the appropriate pipeline with structured logging.

IMPORTANT: Never log PII (addresses, owner names, phone numbers).
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

import structlog

from theleadedge.config import Settings
from theleadedge.notifications.email import EmailSender
from theleadedge.pipelines.briefing import BriefingGenerator
from theleadedge.pipelines.ingest import IngestPipeline
from theleadedge.pipelines.score import ScorePipeline
from theleadedge.scoring.config_loader import load_scoring_config
from theleadedge.scoring.engine import ScoringEngine
from theleadedge.sources.mls_csv import MLSCsvConnector
from theleadedge.storage.database import get_engine, get_session, init_db

logger = structlog.get_logger()


async def cmd_import(settings: Settings) -> int:
    """Import MLS CSV files from the configured import directory.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    log = logger.bind(command="import")

    scoring_config = load_scoring_config(settings.scoring_config_path)
    connector = MLSCsvConnector(
        config_path=settings.config_dir / "mls_fields.yaml",
        import_dir=settings.mls_import_dir,
    )
    pipeline = IngestPipeline(
        csv_connector=connector,
        scoring_config=scoring_config,
        processed_dir=settings.processed_dir,
    )

    engine = get_engine(settings.database_url)
    await init_db(engine)

    now = datetime.utcnow()
    async with get_session(engine) as session:
        result = await pipeline.run(session, settings.mls_import_dir, now)

    log.info(
        "import_finished",
        success=result.success,
        fetched=result.records_fetched,
        created=result.records_created,
        updated=result.records_updated,
        skipped=result.records_skipped,
    )

    return 0 if result.success else 1


async def cmd_score(settings: Settings) -> int:
    """Re-score all active leads.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    log = logger.bind(command="score")

    scoring_config = load_scoring_config(settings.scoring_config_path)
    scoring_engine = ScoringEngine(scoring_config)
    pipeline = ScorePipeline(scoring_engine)

    engine = get_engine(settings.database_url)
    await init_db(engine)

    now = datetime.utcnow()
    async with get_session(engine) as session:
        results = await pipeline.score_all_active(session, now)

    tier_counts: dict[str, int] = {}
    for r in results:
        tier_counts[r.tier] = tier_counts.get(r.tier, 0) + 1

    log.info(
        "scoring_finished",
        leads_scored=len(results),
        tiers=tier_counts,
    )

    return 0


async def cmd_briefing(settings: Settings) -> int:
    """Generate and optionally send the daily briefing email.

    If SMTP credentials and a recipient are configured, sends the
    briefing via email.  Otherwise, writes the HTML to stdout.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    log = logger.bind(command="briefing")

    scoring_config = load_scoring_config(settings.scoring_config_path)
    template_dir = (
        Path(__file__).parent / "notifications" / "templates"
    )
    generator = BriefingGenerator(scoring_config, template_dir)

    engine = get_engine(settings.database_url)
    await init_db(engine)

    now = datetime.utcnow()
    async with get_session(engine) as session:
        html = await generator.generate(session, now)

    # Send via email if SMTP is configured
    if settings.smtp_username and settings.briefing_recipient:
        sender = EmailSender(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            from_name=settings.briefing_from_name,
        )
        subject = f"TheLeadEdge Briefing - {now.strftime('%B %d, %Y')}"
        sent = await sender.send(
            to=settings.briefing_recipient,
            subject=subject,
            html_body=html,
        )
        if sent:
            log.info("briefing_emailed", subject=subject)
            return 0
        log.error("briefing_email_failed")
        return 1

    # No SMTP configured -- write HTML to stdout
    log.info("briefing_generated_stdout", html_length=len(html))
    sys.stdout.write(html)
    return 0


async def cmd_run(settings: Settings) -> int:
    """Run the full pipeline: import -> score -> briefing.

    Returns
    -------
    int
        Exit code: 0 if all stages succeed, 1 if any stage fails.
    """
    log = logger.bind(command="run")

    log.info("full_pipeline_start")

    code = await cmd_import(settings)
    if code != 0:
        log.error("pipeline_aborted", stage="import", exit_code=code)
        return code

    code = await cmd_score(settings)
    if code != 0:
        log.error("pipeline_aborted", stage="score", exit_code=code)
        return code

    code = await cmd_briefing(settings)
    if code != 0:
        log.error("pipeline_aborted", stage="briefing", exit_code=code)
        return code

    log.info("full_pipeline_complete")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="theleadedge",
        description="TheLeadEdge -- Data-driven real estate lead generation",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser(
        "import",
        help="Import MLS CSV files from data/mls_imports/",
    )
    subparsers.add_parser(
        "score",
        help="Re-score all active leads",
    )
    subparsers.add_parser(
        "briefing",
        help="Generate and send daily briefing email",
    )
    subparsers.add_parser(
        "run",
        help="Full pipeline: import -> score -> briefing",
    )

    return parser


def cli() -> None:
    """Main CLI entrypoint.  Parse arguments and dispatch commands."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    settings = Settings()

    commands = {
        "import": cmd_import,
        "score": cmd_score,
        "briefing": cmd_briefing,
        "run": cmd_run,
    }

    handler = commands[args.command]
    exit_code = asyncio.run(handler(settings))
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
