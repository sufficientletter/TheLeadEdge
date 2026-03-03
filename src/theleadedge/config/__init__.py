"""TheLeadEdge configuration.

Pydantic Settings loaded from .env and config/market.yaml.

Usage:
    from theleadedge.config import Settings

    settings = Settings()           # loads from .env + market.yaml
    print(settings.zip_codes)       # ['33901', '33903', ...]
    print(settings.database_url)    # sqlite+aiosqlite:///...
    print(settings.is_production)   # False
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


def _find_project_root() -> Path:
    """Walk up from this file to find the directory containing pyproject.toml."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path.cwd()


PROJECT_ROOT = _find_project_root()


def _load_zip_codes() -> list[str]:
    """Load ZIP codes from config/market.yaml.

    Reads all areas under the ``zip_codes`` key and flattens them into a
    deduplicated, sorted list of ZIP code strings.
    """
    market_path = PROJECT_ROOT / "config" / "market.yaml"
    if not market_path.exists():
        return []
    with open(market_path, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    zips: list[str] = []
    for _area, codes in (data.get("zip_codes") or {}).items():
        if codes:
            zips.extend(str(z) for z in codes)
    return sorted(set(zips))


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file.

    All fields can be overridden via environment variables (case-insensitive).
    Paths default relative to the project root detected at import time.
    """

    # ── Application ──────────────────────────────────────────────────────
    app_env: str = "development"
    log_level: str = "DEBUG"

    # ── State / Market ───────────────────────────────────────────────────
    state: str = "FL"
    market_name: str = "Southwest Florida"

    # ── Database ─────────────────────────────────────────────────────────
    database_url: str = Field(
        default=f"sqlite+aiosqlite:///{PROJECT_ROOT / 'theleadedge.db'}",
    )

    # ── Email (SMTP) ─────────────────────────────────────────────────────
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    briefing_recipient: str = ""
    briefing_from_name: str = "TheLeadEdge"

    # ── Follow Up Boss CRM (Phase 2) ────────────────────────────────────
    fub_api_key: str = ""
    fub_base_url: str = "https://api.followupboss.com/v1"

    # ── Paths ────────────────────────────────────────────────────────────
    mls_import_dir: Path = Field(
        default_factory=lambda: PROJECT_ROOT / "data" / "mls_imports",
    )
    processed_dir: Path = Field(
        default_factory=lambda: PROJECT_ROOT / "data" / "processed",
    )
    config_dir: Path = Field(
        default_factory=lambda: PROJECT_ROOT / "config",
    )

    # ── Market (loaded from market.yaml) ─────────────────────────────────
    zip_codes: list[str] = Field(default_factory=_load_zip_codes)

    # ── Scoring ──────────────────────────────────────────────────────────
    scoring_config_path: Path = Field(
        default_factory=lambda: PROJECT_ROOT / "config" / "scoring_weights.yaml",
    )

    # ── Feature Flags ────────────────────────────────────────────────────
    feature_flags_path: Path = Field(
        default_factory=lambda: PROJECT_ROOT / "config" / "feature_flags.yaml",
    )

    # ── Briefing Schedule ────────────────────────────────────────────────
    briefing_hour: int = 6
    briefing_minute: int = 30

    # ── Scoring Thresholds (from MASTER_BUILD_PLAN) ──────────────────────
    tier_s_min: int = 80
    tier_a_min: int = 60
    tier_b_min: int = 40
    tier_c_min: int = 20

    model_config = {
        "env_file": str(PROJECT_ROOT / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def is_production(self) -> bool:
        """Return True if running in production environment."""
        return self.app_env == "production"

    @property
    def project_root(self) -> Path:
        """Return the detected project root directory."""
        return PROJECT_ROOT
