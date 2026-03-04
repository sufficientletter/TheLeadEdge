"""CLI entry point for TheLeadEdge.

Usage:
    python -m theleadedge import     # Import CSVs from data/mls_imports/
    python -m theleadedge score      # Re-score all active leads
    python -m theleadedge briefing   # Generate and send daily briefing
    python -m theleadedge run        # Import -> Score -> Briefing (full pipeline)
    python -m theleadedge import-public-records --type lis_pendens
                                     # Import clerk/code violation records
    python -m theleadedge download-redfin
                                     # Download and process Redfin market data
    python -m theleadedge enrich     # Enrich top-tier leads with phone numbers
    python -m theleadedge scheduler  # Start the scheduler daemon
    python -m theleadedge health     # Check all connector health
    python -m theleadedge data-health  # Data pipeline health report
    python -m theleadedge match-records  # Process unmatched source records
    python -m theleadedge download-pa   # Download PA data (both counties)
    python -m theleadedge dashboard  # Launch the web dashboard

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
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from theleadedge.sources.base import DataSourceConnector

from theleadedge.config import Settings
from theleadedge.notifications.email import EmailSender
from theleadedge.pipelines.briefing import BriefingGenerator
from theleadedge.pipelines.ingest import IngestPipeline
from theleadedge.pipelines.score import ScorePipeline
from theleadedge.scoring.config_loader import load_scoring_config
from theleadedge.scoring.engine import ScoringEngine
from theleadedge.sources.clerk_records import (
    ClerkRecordConnector,
    load_clerk_config,
)
from theleadedge.sources.code_violations import CodeViolationConnector
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


async def cmd_import_public_records(
    settings: Settings,
    args: argparse.Namespace,
) -> int:
    """Import public record files (clerk records or code violations).

    Reads files from the import directory, normalizes them via the
    appropriate connector, and processes them through the public record
    pipeline (matching, signal detection, persistence).

    Parameters
    ----------
    settings:
        Application settings.
    args:
        Parsed CLI arguments with ``type``, ``county``, and ``dir``.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    log = logger.bind(
        command="import-public-records",
        record_type=args.type,
        county=args.county,
    )

    # Determine import directory
    import_dir = (
        Path(args.dir) if args.dir
        else settings.public_records_dir / args.type
    )

    import_dir.mkdir(parents=True, exist_ok=True)

    # Load clerk field config
    clerk_config_path = settings.config_dir / "clerk_fields.yaml"
    if not clerk_config_path.exists():
        log.error(
            "config_not_found",
            path=str(clerk_config_path),
        )
        return 1

    clerk_config = load_clerk_config(clerk_config_path)

    # Create the appropriate connector
    record_type: str = args.type
    if record_type == "code_violation":
        connector: DataSourceConnector = CodeViolationConnector(
            import_dir=import_dir,
            config=clerk_config,
            county=args.county,
        )
    else:
        connector = ClerkRecordConnector(
            import_dir=import_dir,
            record_type=record_type,
            config=clerk_config,
            county=args.county,
        )

    # Authenticate (creates dirs if needed)
    await connector.authenticate()

    # Fetch file list
    raw_files = await connector.fetch()
    if not raw_files:
        log.info("no_files_found", import_dir=str(import_dir))
        print(f"No {record_type} files found in {import_dir}")
        return 0

    # Transform raw files to SourceRecord dicts
    record_dicts = connector.transform(raw_files)
    if not record_dicts:
        log.info("no_records_produced")
        print("Files found but no records produced after transformation.")
        return 0

    # Convert to SourceRecord Pydantic models
    from theleadedge.models.source_record import SourceRecord

    source_records = [SourceRecord(**d) for d in record_dicts]

    # Process through PublicRecordPipeline
    from theleadedge.pipelines.public_records import PublicRecordPipeline

    scoring_config = load_scoring_config(settings.scoring_config_path)
    engine = get_engine(settings.database_url)
    await init_db(engine)

    now = datetime.utcnow()
    async with get_session(engine) as session:
        pipeline = PublicRecordPipeline(
            session=session,
            config=scoring_config,
        )
        stats = await pipeline.process_records(source_records, now)

    log.info("import_public_records_finished", **stats)
    print(f"Public records import complete ({record_type}):")
    print(f"  Total:      {stats['total']}")
    print(f"  Matched:    {stats['matched']}")
    print(f"  Queued:     {stats['queued']}")
    print(f"  Unmatched:  {stats['unmatched']}")
    print(f"  Duplicates: {stats['duplicates']}")
    print(f"  Signals:    {stats['signals_created']}")

    return 0


async def cmd_download_redfin(settings: Settings) -> int:
    """Download and process Redfin market data for target ZIP codes.

    Downloads the weekly gzipped TSV from Redfin's public data center,
    filters to configured SWFLA ZIP codes, calculates absorption rates,
    and persists MarketSnapshotRows to the database.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    log = logger.bind(command="download-redfin")

    from theleadedge.sources.market_data import RedfinMarketConnector
    from theleadedge.storage.repositories import MarketSnapshotRepo

    download_dir = settings.pa_download_dir.parent / "redfin"
    download_dir.mkdir(parents=True, exist_ok=True)

    connector = RedfinMarketConnector(
        download_dir=download_dir,
        target_zip_codes=settings.zip_codes,
    )

    try:
        await connector.authenticate()
        raw = await connector.fetch()
        snapshots = connector.transform(raw)
    except Exception as exc:
        log.error("redfin_download_failed", error=str(exc))
        print(f"Redfin download failed: {exc}")
        return 1

    if not snapshots:
        log.info("no_matching_snapshots")
        print("No market data found for target ZIP codes.")
        return 0

    engine = get_engine(settings.database_url)
    await init_db(engine)

    created_count = 0
    async with get_session(engine) as session:
        repo = MarketSnapshotRepo(session)
        for snap in snapshots:
            await repo.create(**snap)
            created_count += 1

    log.info(
        "redfin_import_finished",
        snapshots_created=created_count,
        zips_found=len({s["zip_code"] for s in snapshots}),
    )
    print("Redfin market data import complete:")
    print(f"  Snapshots created: {created_count}")
    print(f"  ZIP codes:         {len({s['zip_code'] for s in snapshots})}")

    return 0


async def cmd_enrich(settings: Settings, args: argparse.Namespace) -> int:
    """Enrich top-tier leads with phone numbers via BatchSkipTracing.

    Queries leads in the specified tiers that lack phone numbers,
    submits them to the BatchSkipTracing API for enrichment,
    normalizes results to E.164, scrubs against a DNC list, and
    updates the database.

    Parameters
    ----------
    settings:
        Application settings.
    args:
        Parsed CLI arguments with ``tier`` (comma-separated tiers).

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    log = logger.bind(command="enrich")

    tiers = [t.strip().upper() for t in args.tier.split(",")]

    if not settings.skip_trace_api_key:
        log.error("skip_trace_api_key_not_configured")
        print("Error: SKIP_TRACE_API_KEY not configured in .env")
        return 1

    from theleadedge.integrations.skip_trace import (
        BatchSkipTraceClient,
        PhoneEnrichmentPipeline,
    )

    client = BatchSkipTraceClient(
        api_key=settings.skip_trace_api_key,
        base_url=settings.skip_trace_base_url,
    )

    engine = get_engine(settings.database_url)
    await init_db(engine)

    now = datetime.utcnow()
    async with get_session(engine) as session:
        pipeline = PhoneEnrichmentPipeline(
            session=session,
            client=client,
        )
        stats = await pipeline.enrich_top_tier(tiers=tiers, now=now)

    log.info("enrich_finished", **stats)
    print("Phone enrichment complete:")
    print(f"  Leads queried:      {stats['leads_queried']}")
    print(f"  Batches submitted:  {stats['batches_submitted']}")
    print(f"  Phones found:       {stats['phones_found']}")
    print(f"  DNC filtered:       {stats['dnc_filtered']}")
    print(f"  Properties updated: {stats['properties_updated']}")

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


async def cmd_scheduler(settings: Settings) -> int:
    """Start the APScheduler daemon for automated pipeline execution.

    Creates all scheduled jobs (daily, weekly, monthly, quarterly)
    and runs until interrupted with Ctrl+C.

    Returns
    -------
    int
        Exit code: 0 on clean shutdown.
    """
    log = logger.bind(command="scheduler")

    from theleadedge.scheduler import create_scheduler

    scheduler = create_scheduler(settings)
    scheduler.start()

    job_count = len(scheduler.get_jobs())
    log.info("scheduler_started", jobs=job_count)
    print(f"Scheduler started with {job_count} jobs.")
    print("Press Ctrl+C to stop.")

    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        log.info("scheduler_stopped")
        print("\nScheduler stopped.")

    return 0


async def cmd_health(settings: Settings) -> int:
    """Check health of all data source connectors.

    Instantiates each connector and calls its ``health_check()`` method.
    Reports overall system status as HEALTHY or DEGRADED.

    Returns
    -------
    int
        Exit code: 0 if all healthy, 1 if any degraded.
    """
    log = logger.bind(command="health")
    results: dict[str, bool] = {}

    # MLS CSV connector
    try:
        mls = MLSCsvConnector(
            config_path=settings.config_dir / "mls_fields.yaml",
            import_dir=settings.mls_import_dir,
        )
        results["mls_csv"] = await mls.health_check()
    except Exception:
        results["mls_csv"] = False

    # Check database connectivity
    try:
        engine = get_engine(settings.database_url)
        await init_db(engine)
        results["database"] = True
    except Exception:
        results["database"] = False

    # Check config files
    results["scoring_config"] = settings.scoring_config_path.exists()
    results["feature_flags"] = settings.feature_flags_path.exists()

    all_healthy = all(results.values())
    status = "HEALTHY" if all_healthy else "DEGRADED"

    print(f"System Health: {status}")
    for name, healthy in results.items():
        icon = "OK" if healthy else "FAIL"
        print(f"  {name}: {icon}")

    log.info("health_check", status=status, results=results)
    return 0 if all_healthy else 1


async def cmd_data_health(settings: Settings) -> int:
    """Generate data pipeline health report.

    Queries the database for lead tier distribution and recent sync
    log entries to give a quick overview of pipeline state.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    from theleadedge.storage.queries import (
        get_pipeline_summary,
        get_recent_syncs,
    )

    engine = get_engine(settings.database_url)
    await init_db(engine)

    async with get_session(engine) as session:
        summary = await get_pipeline_summary(session)
        syncs = await get_recent_syncs(session)

    print("=== Data Pipeline Health ===")
    print(f"Total active leads: {summary['total_active']}")
    print("Leads by tier:")
    for tier, count in summary.get("tiers", {}).items():
        print(f"  {tier}: {count}")
    print(f"\nRecent syncs: {len(syncs)}")
    for sync in syncs[:5]:
        status = "OK" if sync.success else "FAIL"
        print(
            f"  {sync.source} ({sync.job_type}):"
            f" {status} -- {sync.records_created} created"
        )

    return 0


async def cmd_match_records(settings: Settings) -> int:
    """Process unmatched source records through the RecordMapper.

    Queries all source records without a matched property and runs
    them through the cascading address matcher (parcel ID, normalized
    address, address key, fuzzy).

    Returns
    -------
    int
        Exit code: 0 on success, 1 on failure.
    """
    log = logger.bind(command="match-records")

    from theleadedge.models.source_record import SourceRecord
    from theleadedge.pipelines.match import RecordMapper
    from theleadedge.storage.repositories import SourceRecordRepo

    engine = get_engine(settings.database_url)
    await init_db(engine)

    matched_count = 0
    total_count = 0

    async with get_session(engine) as session:
        repo = SourceRecordRepo(session)
        mapper = RecordMapper(session)

        unmatched = await repo.get_unmatched()
        total_count = len(unmatched)

        for row in unmatched:
            record = SourceRecord(
                source_name=row.source_name,
                source_record_id=row.source_record_id,
                record_type=row.record_type,
                parcel_id=row.parcel_id,
                street_address=row.street_address,
                city=row.city,
                state=row.state,
                zip_code=row.zip_code,
            )
            result = await mapper.match(record)
            if result.property_id is not None:
                row.matched_property_id = result.property_id
                row.match_method = result.method
                row.match_confidence = result.confidence
                matched_count += 1

    log.info(
        "match_records_finished",
        total=total_count,
        matched=matched_count,
        still_unmatched=total_count - matched_count,
    )
    print(f"Processed {total_count} unmatched records.")
    print(f"  Matched: {matched_count}")
    print(f"  Still unmatched: {total_count - matched_count}")

    return 0


async def cmd_dashboard(settings: Settings, args: argparse.Namespace) -> int:
    """Launch the NiceGUI dashboard web server.

    Parameters
    ----------
    settings:
        Application settings.
    args:
        Parsed CLI arguments with ``host``, ``port``, and ``reload``.

    Returns
    -------
    int
        Exit code: 0 on success.
    """
    from theleadedge.dashboard.app import run_dashboard

    host = args.host or settings.dashboard_host
    port = args.port or settings.dashboard_port

    run_dashboard(
        host=host,
        port=port,
        reload=args.reload,
        settings=settings,
    )
    return 0


async def cmd_download_pa(settings: Settings) -> int:
    """Download Property Appraiser data for both counties.

    Instantiates Collier and Lee PA connectors, downloads their bulk
    data files, and reports record counts.

    Returns
    -------
    int
        Exit code: 0 on success, 1 if both counties fail.
    """
    log = logger.bind(command="download-pa")

    from theleadedge.sources.property_appraiser import (
        CollierPAConnector,
        LeePAConnector,
    )

    download_dir = settings.pa_download_dir
    download_dir.mkdir(parents=True, exist_ok=True)

    total_records = 0
    failures = 0

    # Collier County
    try:
        collier = CollierPAConnector(
            download_dir=download_dir / "collier",
        )
        await collier.authenticate()
        raw = await collier.fetch()
        records = collier.transform(raw)
        total_records += len(records)
        print(f"Collier PA: {len(records)} records")
        log.info("collier_pa_complete", records=len(records))
    except Exception as exc:
        log.error("collier_pa_failed", error=str(exc))
        print(f"Collier PA failed: {exc}")
        failures += 1

    # Lee County
    try:
        lee = LeePAConnector(
            download_dir=download_dir / "lee",
        )
        await lee.authenticate()
        raw = await lee.fetch()
        records = lee.transform(raw)
        total_records += len(records)
        print(f"Lee PA: {len(records)} records")
        log.info("lee_pa_complete", records=len(records))
    except Exception as exc:
        log.error("lee_pa_failed", error=str(exc))
        print(f"Lee PA failed: {exc}")
        failures += 1

    print(f"\nTotal PA records: {total_records}")
    return 1 if failures == 2 else 0


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

    subparsers.add_parser(
        "download-redfin",
        help="Download and process Redfin market data",
    )

    enrich_parser = subparsers.add_parser(
        "enrich",
        help="Enrich leads with phone numbers via BatchSkipTracing",
    )
    enrich_parser.add_argument(
        "--tier",
        default="S,A",
        help="Comma-separated tiers to enrich (default: S,A)",
    )

    pr_parser = subparsers.add_parser(
        "import-public-records",
        help="Import public record files (clerk records, code violations)",
    )
    pr_parser.add_argument(
        "--type",
        required=True,
        choices=["lis_pendens", "probate", "divorce", "code_violation"],
        help="Type of public records to import",
    )
    pr_parser.add_argument(
        "--county",
        default="collier",
        choices=["collier", "lee"],
        help="County (default: collier)",
    )
    pr_parser.add_argument(
        "--dir",
        default=None,
        help="Import directory (default: data/public_records/<type>)",
    )

    # Phase 2 commands
    subparsers.add_parser(
        "scheduler",
        help="Start the scheduler daemon",
    )
    subparsers.add_parser(
        "health",
        help="Check all connector health",
    )
    subparsers.add_parser(
        "data-health",
        help="Data pipeline health report",
    )
    subparsers.add_parser(
        "match-records",
        help="Process unmatched source records",
    )
    subparsers.add_parser(
        "download-pa",
        help="Download PA data (both counties)",
    )

    # Phase 3 commands
    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Launch the web dashboard",
    )
    dashboard_parser.add_argument(
        "--host", default=None, help="Host to bind to (default: 0.0.0.0)"
    )
    dashboard_parser.add_argument(
        "--port", type=int, default=None, help="Port to bind to (default: 8080)"
    )
    dashboard_parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
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

    # Commands that take only settings
    commands: dict[str, Any] = {
        "import": cmd_import,
        "score": cmd_score,
        "briefing": cmd_briefing,
        "run": cmd_run,
        "download-redfin": cmd_download_redfin,
        "scheduler": cmd_scheduler,
        "health": cmd_health,
        "data-health": cmd_data_health,
        "match-records": cmd_match_records,
        "download-pa": cmd_download_pa,
    }

    if args.command == "import-public-records":
        exit_code = asyncio.run(cmd_import_public_records(settings, args))
    elif args.command == "enrich":
        exit_code = asyncio.run(cmd_enrich(settings, args))
    elif args.command == "dashboard":
        exit_code = asyncio.run(cmd_dashboard(settings, args))
    else:
        handler = commands[args.command]
        exit_code = asyncio.run(handler(settings))

    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
