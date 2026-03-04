"""Tests for APScheduler configuration module.

Verifies scheduler creation, job registration, timezone, feature flag
gating, and error handling in the job wrapper.

IMPORTANT: Never start the scheduler in tests -- only inspect configuration.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from theleadedge.config import Settings
from theleadedge.scheduler import _run_job, create_scheduler

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    """Build a Settings instance with temporary paths for isolation."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Minimal feature_flags.yaml
    flags_path = config_dir / "feature_flags.yaml"
    flags_path.write_text(
        "data_sources:\n  mls_csv:\n    enabled: true\n",
        encoding="utf-8",
    )

    # Minimal scoring_weights.yaml (needed by Settings)
    scoring_path = config_dir / "scoring_weights.yaml"
    scoring_path.write_text(
        "signals: []\nstacking_rules: []\ntiers:\n"
        "  D:\n    min_score: 0\n    max_score: 19\n"
        "    action: Monitor\n    urgency: low\n",
        encoding="utf-8",
    )

    return Settings(
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'test.db'}",
        config_dir=config_dir,
        feature_flags_path=flags_path,
        scoring_config_path=scoring_path,
        mls_import_dir=tmp_path / "mls_imports",
        processed_dir=tmp_path / "processed",
        pa_download_dir=tmp_path / "pa_downloads",
        public_records_dir=tmp_path / "public_records",
        scheduler_timezone="America/New_York",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_create_scheduler_returns_scheduler(settings: Settings) -> None:
    """create_scheduler returns an AsyncIOScheduler instance."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = create_scheduler(settings)
    assert isinstance(scheduler, AsyncIOScheduler)


def test_scheduler_has_expected_jobs(settings: Settings) -> None:
    """Scheduler should register exactly 7 jobs."""
    scheduler = create_scheduler(settings)
    jobs = scheduler.get_jobs()
    assert len(jobs) == 7

    expected_ids = {
        "mls_import",
        "full_pipeline",
        "redfin_market",
        "fsbo_alerts",
        "pa_download",
        "clerk_records",
        "sunbiz_llc",
    }
    actual_ids = {j.id for j in jobs}
    assert actual_ids == expected_ids


def test_scheduler_timezone(settings: Settings) -> None:
    """Scheduler timezone should match settings."""
    scheduler = create_scheduler(settings)
    # APScheduler stores timezone on the scheduler object
    assert str(scheduler.timezone) == "America/New_York"


def test_job_ids_unique(settings: Settings) -> None:
    """All job IDs should be unique (no duplicates)."""
    scheduler = create_scheduler(settings)
    jobs = scheduler.get_jobs()
    ids = [j.id for j in jobs]
    assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"


@pytest.mark.asyncio()
async def test_feature_flag_disables_job(
    settings: Settings,
    tmp_path: Path,
) -> None:
    """When feature flag is False, job should be skipped."""
    # Write flags with our specific job disabled
    flags_path = settings.feature_flags_path
    flags_path.write_text(
        "enable_test_job: false\n",
        encoding="utf-8",
    )

    mock_func = AsyncMock()

    await _run_job("test_job", mock_func, settings)

    mock_func.assert_not_called()


@pytest.mark.asyncio()
async def test_run_job_handles_error(settings: Settings) -> None:
    """Job exceptions should be caught and logged, not propagated."""
    async def failing_job(s: Settings, **kwargs: object) -> None:
        msg = "simulated failure"
        raise RuntimeError(msg)

    # Should not raise -- exception is caught internally
    await _run_job("failing_job", failing_job, settings)
