"""APScheduler configuration for automated pipeline execution.

Creates an AsyncIOScheduler with predefined jobs for all data pipelines.
Uses America/New_York timezone (EST/EDT) for scheduling.

Jobs:
- Daily 5:00 AM: MLS CSV file watcher (scan for new imports)
- Daily 5:30 AM: Full pipeline (import -> score -> briefing)
- Weekly Mon 6:00 AM: Redfin market data download
- Weekly Mon 6:30 AM: Craigslist FSBO + Google Alerts
- Monthly 1st 4:00 AM: Collier PA + Lee PA bulk data
- Monthly 1st 7:00 AM: Clerk records processing
- Quarterly: Sunbiz LLC refresh

Each job:
  - try/except with structured logging on completion
  - Feature flag check (skip if disabled)
  - structlog logging (never log PII)

IMPORTANT: Never log PII. Log only job names, durations, record counts.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from theleadedge.scoring.config_loader import load_feature_flags

if TYPE_CHECKING:
    from theleadedge.config import Settings

logger = structlog.get_logger()


async def _run_job(
    job_name: str,
    job_func: Any,
    settings: Settings,
    **kwargs: Any,
) -> None:
    """Wrapper that runs a job with error handling and audit logging.

    Checks feature flags before execution.  Logs start, completion, and
    failure events with duration in milliseconds.  Never logs PII.

    Parameters
    ----------
    job_name:
        Identifier for logging and feature-flag lookup.
    job_func:
        Async callable to execute.
    settings:
        Application settings (used for feature-flag path and passed to job).
    **kwargs:
        Additional keyword arguments forwarded to *job_func*.
    """
    log = logger.bind(job=job_name)
    started = datetime.now(tz=UTC)

    # Check feature flag -- convention: enable_<job_name> key
    try:
        flags = load_feature_flags(settings.feature_flags_path)
    except FileNotFoundError:
        flags = {}

    if not flags.get(f"enable_{job_name}", True):
        log.info("job_skipped_disabled")
        return

    try:
        log.info("job_started")
        await job_func(settings, **kwargs)
        duration_ms = int(
            (datetime.now(tz=UTC) - started).total_seconds() * 1000,
        )
        log.info("job_completed", duration_ms=duration_ms)
    except Exception as exc:
        duration_ms = int(
            (datetime.now(tz=UTC) - started).total_seconds() * 1000,
        )
        log.error("job_failed", error=str(exc), duration_ms=duration_ms)


def create_scheduler(settings: Settings) -> AsyncIOScheduler:
    """Create and configure the APScheduler with all pipeline jobs.

    Does NOT start the scheduler -- call ``scheduler.start()`` after
    creation.  All jobs use lazy imports inside their wrappers to avoid
    circular imports at module load time.

    Parameters
    ----------
    settings:
        Application settings (timezone, paths, feature flags, etc.).

    Returns
    -------
    AsyncIOScheduler
        Configured scheduler with all jobs registered.
    """
    scheduler = AsyncIOScheduler(
        timezone=settings.scheduler_timezone,
    )

    # ------------------------------------------------------------------
    # Daily 5:00 AM -- MLS CSV file watcher
    # ------------------------------------------------------------------
    async def job_mls_import() -> None:
        from theleadedge.main import cmd_import

        await _run_job("mls_import", _wrap_simple(cmd_import), settings)

    scheduler.add_job(
        job_mls_import,
        CronTrigger(hour=5, minute=0),
        id="mls_import",
        name="MLS CSV Import",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Daily 5:30 AM -- Full pipeline (import -> score -> briefing)
    # ------------------------------------------------------------------
    async def job_full_pipeline() -> None:
        from theleadedge.main import cmd_run

        await _run_job("full_pipeline", _wrap_simple(cmd_run), settings)

    scheduler.add_job(
        job_full_pipeline,
        CronTrigger(hour=5, minute=30),
        id="full_pipeline",
        name="Full Pipeline (import+score+briefing)",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Weekly Monday 6:00 AM -- Redfin market data
    # ------------------------------------------------------------------
    async def job_redfin() -> None:
        from theleadedge.main import cmd_download_redfin

        await _run_job(
            "redfin_market",
            _wrap_simple(cmd_download_redfin),
            settings,
        )

    scheduler.add_job(
        job_redfin,
        CronTrigger(day_of_week="mon", hour=6, minute=0),
        id="redfin_market",
        name="Redfin Market Data",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Weekly Monday 6:30 AM -- FSBO + Google Alerts
    # ------------------------------------------------------------------
    async def job_fsbo_alerts() -> None:
        await _run_job("fsbo_alerts", _run_fsbo_alerts, settings)

    scheduler.add_job(
        job_fsbo_alerts,
        CronTrigger(day_of_week="mon", hour=6, minute=30),
        id="fsbo_alerts",
        name="FSBO + Google Alerts",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Monthly 1st 4:00 AM -- Property Appraiser bulk data
    # ------------------------------------------------------------------
    async def job_pa_download() -> None:
        await _run_job("pa_download", _run_pa_download, settings)

    scheduler.add_job(
        job_pa_download,
        CronTrigger(day=1, hour=4, minute=0),
        id="pa_download",
        name="Property Appraiser (Collier + Lee)",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Monthly 1st 7:00 AM -- Clerk records processing
    # ------------------------------------------------------------------
    async def job_clerk_records() -> None:
        await _run_job("clerk_records", _run_clerk_records, settings)

    scheduler.add_job(
        job_clerk_records,
        CronTrigger(day=1, hour=7, minute=0),
        id="clerk_records",
        name="Clerk Records Processing",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Quarterly (Jan, Apr, Jul, Oct) 1st 3:00 AM -- Sunbiz LLC
    # ------------------------------------------------------------------
    async def job_sunbiz() -> None:
        await _run_job("sunbiz_llc", _run_sunbiz, settings)

    scheduler.add_job(
        job_sunbiz,
        CronTrigger(month="1,4,7,10", day=1, hour=3, minute=0),
        id="sunbiz_llc",
        name="Sunbiz LLC Refresh",
        replace_existing=True,
    )

    return scheduler


# ---------------------------------------------------------------------------
# Adapter to make cmd_* functions (which take only Settings) compatible
# with _run_job's (settings, **kwargs) signature.
# ---------------------------------------------------------------------------


def _wrap_simple(
    func: Any,
) -> Any:
    """Wrap a ``cmd_*(settings) -> int`` function for use with _run_job.

    ``_run_job`` calls ``job_func(settings, **kwargs)`` but existing CLI
    commands only accept *settings*.  This adapter absorbs extra kwargs.
    """

    async def _wrapper(settings: Settings, **_kwargs: Any) -> None:
        await func(settings)

    return _wrapper


# ---------------------------------------------------------------------------
# Placeholder job implementations (will be fleshed out in later batches)
# ---------------------------------------------------------------------------


async def _run_fsbo_alerts(settings: Settings, **_kwargs: Any) -> None:
    """Run FSBO and Google Alerts connectors.

    Placeholder -- actual connector orchestration will be wired in when
    the full scheduler integration batch is built.
    """
    logger.info("fsbo_alerts_placeholder")


async def _run_pa_download(settings: Settings, **_kwargs: Any) -> None:
    """Run Collier + Lee PA downloads.

    Placeholder -- actual downloads triggered via cmd_download_pa.
    """
    logger.info("pa_download_placeholder")


async def _run_clerk_records(settings: Settings, **_kwargs: Any) -> None:
    """Process clerk records from import directory.

    Placeholder -- actual processing triggered via cmd_import_public_records.
    """
    logger.info("clerk_records_placeholder")


async def _run_sunbiz(settings: Settings, **_kwargs: Any) -> None:
    """Run Sunbiz LLC data refresh.

    Placeholder -- Sunbiz SFTP/scrape connector not yet implemented.
    """
    logger.info("sunbiz_placeholder")
