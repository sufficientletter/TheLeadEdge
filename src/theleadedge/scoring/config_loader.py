"""Scoring configuration loader for TheLeadEdge.

Reads ``scoring_weights.yaml`` and ``feature_flags.yaml`` from the config
directory and hydrates them into typed Pydantic models.  This allows the
Realtor to tune signal weights, stacking rules, and tier thresholds by
editing YAML -- no code changes required.

Usage::

    from pathlib import Path
    from theleadedge.scoring.config_loader import load_scoring_config

    config = load_scoring_config(Path("config/scoring_weights.yaml"))
    tier, tier_cfg = config.get_tier_for_score(75.0)
    # tier = Tier.A, tier_cfg.action = "Priority outreach within 48 hours..."
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml
from pydantic import BaseModel

from theleadedge.models.enums import DecayType, SignalCategory, Tier
from theleadedge.models.signal import SignalConfig

if TYPE_CHECKING:
    from pathlib import Path


class StackingRule(BaseModel):
    """A rule that applies a bonus when specific signals co-occur."""

    name: str
    required_signals: set[str]
    multiplier: float
    description: str = ""


class TierConfig(BaseModel):
    """Configuration for a scoring tier."""

    tier: Tier
    min_score: int
    max_score: int
    action: str
    urgency: str


class ScoringConfig(BaseModel):
    """Complete scoring configuration loaded from YAML."""

    signals: list[SignalConfig]
    stacking_rules: list[StackingRule]
    tiers: list[TierConfig]

    def get_signal_config(self, signal_type: str) -> SignalConfig | None:
        """Look up configuration for a signal type by name."""
        for s in self.signals:
            if s.signal_type == signal_type:
                return s
        return None

    def get_tier_for_score(self, score: float) -> tuple[Tier, TierConfig]:
        """Determine tier and config for a given normalized score.

        Tiers are evaluated from highest threshold downward so the first
        match wins (S before A before B, etc.).
        """
        for tc in sorted(self.tiers, key=lambda t: t.min_score, reverse=True):
            if score >= tc.min_score:
                return tc.tier, tc
        # Fallback to lowest tier
        lowest = sorted(self.tiers, key=lambda t: t.min_score)[0]
        return lowest.tier, lowest


def load_scoring_config(path: Path) -> ScoringConfig:
    """Load scoring configuration from a YAML file.

    Parameters
    ----------
    path:
        Absolute or relative path to ``scoring_weights.yaml``.

    Returns
    -------
    ScoringConfig:
        Fully validated scoring configuration with signals, stacking
        rules, and tier definitions.

    Raises
    ------
    FileNotFoundError:
        If the YAML file does not exist.
    yaml.YAMLError:
        If the YAML is malformed.
    pydantic.ValidationError:
        If the data does not conform to the expected schema.
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    signals = [
        SignalConfig(
            signal_type=s["signal_type"],
            category=SignalCategory(s["category"]),
            base_points=s["base_points"],
            decay_type=DecayType(s["decay_type"]),
            half_life_days=s.get("half_life_days", 30.0),
            description=s.get("description", ""),
        )
        for s in data.get("signals", [])
    ]

    stacking_rules = [
        StackingRule(
            name=r["name"],
            required_signals=set(r["required_signals"]),
            multiplier=r["multiplier"],
            description=r.get("description", ""),
        )
        for r in data.get("stacking_rules", [])
    ]

    tiers: list[TierConfig] = []
    for tier_name, tc in data.get("tiers", {}).items():
        tiers.append(
            TierConfig(
                tier=Tier(tier_name),
                min_score=tc["min_score"],
                max_score=tc["max_score"],
                action=tc["action"],
                urgency=tc["urgency"],
            )
        )

    return ScoringConfig(
        signals=signals,
        stacking_rules=stacking_rules,
        tiers=tiers,
    )


def load_feature_flags(path: Path) -> dict[str, Any]:
    """Load feature flags from a YAML file.

    Returns the raw dictionary structure so callers can check flags like::

        flags = load_feature_flags(Path("config/feature_flags.yaml"))
        if flags["data_sources"]["mls_csv"]["enabled"]:
            ...

    Parameters
    ----------
    path:
        Absolute or relative path to ``feature_flags.yaml``.
    """
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
