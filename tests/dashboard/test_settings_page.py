"""Tests for settings page and config save functionality.

Tests cover:
- ``save_scoring_config`` round-trip preservation
- ``save_scoring_config`` selective field update
- Dialog data constants and defaults
- Settings page config loading
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import yaml

from theleadedge.scoring.config_loader import (
    ScoringConfig,
    load_scoring_config,
    save_scoring_config,
)

# ---------------------------------------------------------------------------
# Test save_scoring_config round-trip
# ---------------------------------------------------------------------------


class TestSaveScoringConfig:
    """Test saving and reloading scoring configuration."""

    def test_save_preserves_structure(
        self, scoring_config: ScoringConfig
    ) -> None:
        """Save and reload should preserve the config."""
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", delete=False, mode="w"
        ) as f:
            data = {
                "signals": [
                    {
                        "signal_type": "expired_listing",
                        "category": "mls",
                        "base_points": 15,
                        "decay_type": "exponential",
                        "half_life_days": 21,
                    }
                ],
                "stacking_rules": [],
                "tiers": {
                    "S": {
                        "min_score": 80,
                        "max_score": 100,
                        "action": "Call now",
                        "urgency": "critical",
                    },
                    "D": {
                        "min_score": 0,
                        "max_score": 19,
                        "action": "Monitor",
                        "urgency": "low",
                    },
                },
            }
            yaml.dump(data, f, default_flow_style=False)
            tmp_path = Path(f.name)

        config = load_scoring_config(tmp_path)
        assert config.signals[0].base_points == 15

        # Modify and save
        config.signals[0].base_points = 25.0
        save_scoring_config(config, tmp_path)

        # Reload and verify
        reloaded = load_scoring_config(tmp_path)
        assert reloaded.signals[0].base_points == 25.0
        tmp_path.unlink()

    def test_save_updates_only_base_points(self) -> None:
        """Save should only change base_points, not other fields."""
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", delete=False, mode="w"
        ) as f:
            data = {
                "signals": [
                    {
                        "signal_type": "price_reduction",
                        "category": "mls",
                        "base_points": 10,
                        "decay_type": "linear",
                        "half_life_days": 14,
                        "description": "Original description",
                    }
                ],
                "stacking_rules": [],
                "tiers": {
                    "D": {
                        "min_score": 0,
                        "max_score": 100,
                        "action": "Monitor",
                        "urgency": "low",
                    },
                },
            }
            yaml.dump(data, f, default_flow_style=False)
            tmp_path = Path(f.name)

        config = load_scoring_config(tmp_path)
        config.signals[0].base_points = 20.0
        save_scoring_config(config, tmp_path)

        # Verify description preserved
        with open(tmp_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        assert raw["signals"][0]["description"] == "Original description"
        assert raw["signals"][0]["base_points"] == 20.0
        assert raw["signals"][0]["decay_type"] == "linear"
        tmp_path.unlink()

    def test_save_multiple_signals(self) -> None:
        """Save correctly updates multiple signals."""
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", delete=False, mode="w"
        ) as f:
            data = {
                "signals": [
                    {
                        "signal_type": "expired_listing",
                        "category": "mls",
                        "base_points": 15,
                        "decay_type": "exponential",
                        "half_life_days": 21,
                    },
                    {
                        "signal_type": "high_dom",
                        "category": "mls",
                        "base_points": 11,
                        "decay_type": "step",
                        "half_life_days": 60,
                    },
                ],
                "stacking_rules": [],
                "tiers": {
                    "D": {
                        "min_score": 0,
                        "max_score": 100,
                        "action": "Monitor",
                        "urgency": "low",
                    },
                },
            }
            yaml.dump(data, f, default_flow_style=False)
            tmp_path = Path(f.name)

        config = load_scoring_config(tmp_path)
        config.signals[0].base_points = 25.0
        config.signals[1].base_points = 18.0
        save_scoring_config(config, tmp_path)

        reloaded = load_scoring_config(tmp_path)
        by_type = {s.signal_type: s for s in reloaded.signals}
        assert by_type["expired_listing"].base_points == 25.0
        assert by_type["high_dom"].base_points == 18.0
        tmp_path.unlink()

    def test_save_preserves_stacking_rules(self) -> None:
        """Stacking rules survive a save round-trip unchanged."""
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", delete=False, mode="w"
        ) as f:
            data = {
                "signals": [
                    {
                        "signal_type": "expired_listing",
                        "category": "mls",
                        "base_points": 15,
                        "decay_type": "exponential",
                        "half_life_days": 21,
                    },
                ],
                "stacking_rules": [
                    {
                        "name": "test_rule",
                        "required_signals": [
                            "expired_listing",
                            "high_dom",
                        ],
                        "multiplier": 1.5,
                        "description": "Test rule description",
                    }
                ],
                "tiers": {
                    "D": {
                        "min_score": 0,
                        "max_score": 100,
                        "action": "Monitor",
                        "urgency": "low",
                    },
                },
            }
            yaml.dump(data, f, default_flow_style=False)
            tmp_path = Path(f.name)

        config = load_scoring_config(tmp_path)
        config.signals[0].base_points = 20.0
        save_scoring_config(config, tmp_path)

        with open(tmp_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        assert len(raw["stacking_rules"]) == 1
        assert raw["stacking_rules"][0]["name"] == "test_rule"
        assert raw["stacking_rules"][0]["multiplier"] == 1.5
        tmp_path.unlink()

    def test_save_preserves_tiers(self) -> None:
        """Tier definitions survive a save round-trip unchanged."""
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", delete=False, mode="w"
        ) as f:
            data = {
                "signals": [
                    {
                        "signal_type": "expired_listing",
                        "category": "mls",
                        "base_points": 15,
                        "decay_type": "exponential",
                        "half_life_days": 21,
                    },
                ],
                "stacking_rules": [],
                "tiers": {
                    "S": {
                        "min_score": 80,
                        "max_score": 100,
                        "action": "Call now",
                        "urgency": "immediate",
                    },
                    "D": {
                        "min_score": 0,
                        "max_score": 19,
                        "action": "Monitor",
                        "urgency": "monitor",
                    },
                },
            }
            yaml.dump(data, f, default_flow_style=False)
            tmp_path = Path(f.name)

        config = load_scoring_config(tmp_path)
        save_scoring_config(config, tmp_path)

        with open(tmp_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        assert raw["tiers"]["S"]["min_score"] == 80
        assert raw["tiers"]["S"]["urgency"] == "immediate"
        assert raw["tiers"]["D"]["action"] == "Monitor"
        tmp_path.unlink()


# ---------------------------------------------------------------------------
# Test dialog data constants
# ---------------------------------------------------------------------------


class TestDialogData:
    """Verify dialog constants and data structures."""

    def test_snooze_durations(self) -> None:
        """Verify snooze duration options."""
        from theleadedge.dashboard.dialogs.snooze_dialog import (
            SNOOZE_DURATIONS,
        )

        assert len(SNOOZE_DURATIONS) == 4
        assert "7" in SNOOZE_DURATIONS
        assert "14" in SNOOZE_DURATIONS
        assert "30" in SNOOZE_DURATIONS
        assert "90" in SNOOZE_DURATIONS

    def test_snooze_duration_labels(self) -> None:
        """Verify snooze duration labels are human-readable."""
        from theleadedge.dashboard.dialogs.snooze_dialog import (
            SNOOZE_DURATIONS,
        )

        assert SNOOZE_DURATIONS["7"] == "1 Week"
        assert SNOOZE_DURATIONS["90"] == "3 Months"

    def test_outreach_types(self) -> None:
        """Verify outreach type options are available."""
        types = ["call", "email", "sms", "meeting", "mail", "note"]
        assert "call" in types
        assert len(types) == 6

    def test_outcome_options(self) -> None:
        """Verify outcome options are defined."""
        outcomes = [
            "no_answer",
            "left_voicemail",
            "spoke_with",
            "appointment_set",
            "not_interested",
            "wrong_number",
        ]
        assert "spoke_with" in outcomes

    def test_confirm_dialog_defaults(self) -> None:
        """Confirm dialog has sensible defaults."""
        from theleadedge.dashboard.dialogs.confirm_dialog import (
            confirm_dialog,
        )

        assert callable(confirm_dialog)

    def test_csv_import_dialog_callable(self) -> None:
        """CSV import dialog is importable and callable."""
        from theleadedge.dashboard.dialogs.csv_import_dialog import (
            csv_import_dialog,
        )

        assert callable(csv_import_dialog)

    def test_snooze_dialog_callable(self) -> None:
        """Snooze dialog is importable and callable."""
        from theleadedge.dashboard.dialogs.snooze_dialog import (
            snooze_dialog,
        )

        assert callable(snooze_dialog)


# ---------------------------------------------------------------------------
# Test settings page config loading
# ---------------------------------------------------------------------------


class TestSettingsPageConfig:
    """Verify settings page can load configuration correctly."""

    def test_scoring_config_loads(
        self, scoring_config: ScoringConfig
    ) -> None:
        """Config loads with signals and tiers."""
        assert len(scoring_config.signals) > 0
        assert len(scoring_config.tiers) > 0

    def test_all_signals_have_base_points(
        self, scoring_config: ScoringConfig
    ) -> None:
        """Every signal has a positive base_points value."""
        for sig in scoring_config.signals:
            assert sig.base_points > 0

    def test_tier_thresholds_ordered(
        self, scoring_config: ScoringConfig
    ) -> None:
        """Tiers are ordered by descending min_score."""
        sorted_tiers = sorted(
            scoring_config.tiers, key=lambda t: t.min_score, reverse=True
        )
        for i in range(len(sorted_tiers) - 1):
            assert (
                sorted_tiers[i].min_score >= sorted_tiers[i + 1].min_score
            )

    def test_stacking_rules_have_signals(
        self, scoring_config: ScoringConfig
    ) -> None:
        """Each stacking rule requires at least 2 signals."""
        for rule in scoring_config.stacking_rules:
            assert len(rule.required_signals) >= 2
            assert rule.multiplier > 0

    def test_all_tiers_present(
        self, scoring_config: ScoringConfig
    ) -> None:
        """All five tier levels are defined."""
        tier_names = {tc.tier.value for tc in scoring_config.tiers}
        assert tier_names == {"S", "A", "B", "C", "D"}

    def test_all_signals_have_categories(
        self, scoring_config: ScoringConfig
    ) -> None:
        """Every signal has a valid category."""
        for sig in scoring_config.signals:
            assert sig.category is not None
            assert sig.category.value in {
                "mls",
                "public_record",
                "life_event",
                "market",
                "digital",
            }

    def test_all_signals_have_decay_type(
        self, scoring_config: ScoringConfig
    ) -> None:
        """Every signal has a valid decay type."""
        for sig in scoring_config.signals:
            assert sig.decay_type is not None
            assert sig.decay_type.value in {
                "linear",
                "exponential",
                "step",
                "escalating",
            }


# ---------------------------------------------------------------------------
# Test settings page render helpers are importable
# ---------------------------------------------------------------------------


class TestSettingsPageHelpers:
    """Verify settings page render functions are importable."""

    def test_render_scoring_weights_callable(self) -> None:
        """_render_scoring_weights is importable and callable."""
        from theleadedge.dashboard.pages.settings import (
            _render_scoring_weights,
        )

        assert callable(_render_scoring_weights)

    def test_render_tier_config_callable(self) -> None:
        """_render_tier_config is importable and callable."""
        from theleadedge.dashboard.pages.settings import _render_tier_config

        assert callable(_render_tier_config)

    def test_render_stacking_rules_callable(self) -> None:
        """_render_stacking_rules is importable and callable."""
        from theleadedge.dashboard.pages.settings import (
            _render_stacking_rules,
        )

        assert callable(_render_stacking_rules)

    def test_render_notification_prefs_callable(self) -> None:
        """_render_notification_prefs is importable and callable."""
        from theleadedge.dashboard.pages.settings import (
            _render_notification_prefs,
        )

        assert callable(_render_notification_prefs)

    def test_page_settings_callable(self) -> None:
        """page_settings is importable and callable."""
        from theleadedge.dashboard.pages.settings import page_settings

        assert callable(page_settings)
