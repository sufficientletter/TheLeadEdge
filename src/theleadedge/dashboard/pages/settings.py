"""Settings page -- configuration management.

Provides UI for editing scoring weights, viewing data source status,
and configuring notification preferences.

IMPORTANT: Never log or display PII.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from nicegui import ui

from theleadedge.config import Settings
from theleadedge.dashboard.layout import create_layout
from theleadedge.scoring.config_loader import load_scoring_config, save_scoring_config

if TYPE_CHECKING:
    from pathlib import Path

    from theleadedge.scoring.config_loader import ScoringConfig

logger = structlog.get_logger()


def _render_scoring_weights(config: ScoringConfig, config_path: Path) -> None:
    """Render editable scoring weights section."""
    ui.label("Signal Weights").classes("text-h6")
    ui.label(
        "Adjust base points for each signal type. "
        "Changes are saved to scoring_weights.yaml."
    ).classes("text-caption text-grey q-mb-md")

    weight_inputs: dict[str, ui.number] = {}

    with ui.column().classes("w-full gap-2"):
        for sig in sorted(
            config.signals, key=lambda s: s.base_points, reverse=True
        ):
            with ui.row().classes("w-full items-center gap-4"):
                ui.label(
                    sig.signal_type.replace("_", " ").title()
                ).classes("min-w-48 text-body1")
                weight_inputs[sig.signal_type] = ui.number(
                    label="Base Points",
                    value=sig.base_points,
                    min=0,
                    max=50,
                    step=1,
                ).classes("w-24")
                ui.label(f"Category: {sig.category.value}").classes(
                    "text-caption text-grey"
                )
                ui.label(f"Decay: {sig.decay_type.value}").classes(
                    "text-caption text-grey"
                )

    def _save_weights() -> None:
        try:
            for sig in config.signals:
                new_val = weight_inputs.get(sig.signal_type)
                if new_val and new_val.value is not None:
                    sig.base_points = float(new_val.value)
            save_scoring_config(config, config_path)
            ui.notify("Scoring weights saved", type="positive")
            logger.info("scoring_weights_saved")
        except Exception as exc:
            ui.notify(f"Error saving: {exc}", type="negative")
            logger.exception("scoring_weights_save_error")

    ui.button("Save Weights", icon="save", on_click=_save_weights).props(
        "color=primary"
    ).classes("q-mt-md")


def _render_tier_config(config: ScoringConfig) -> None:
    """Render tier threshold display."""
    ui.label("Tier Thresholds").classes("text-h6 q-mt-lg")

    columns = [
        {"name": "tier", "label": "Tier", "field": "tier"},
        {"name": "min", "label": "Min Score", "field": "min"},
        {"name": "max", "label": "Max Score", "field": "max"},
        {"name": "urgency", "label": "Urgency", "field": "urgency"},
    ]
    rows = [
        {
            "tier": tc.tier.value,
            "min": tc.min_score,
            "max": tc.max_score,
            "urgency": tc.urgency,
        }
        for tc in sorted(config.tiers, key=lambda t: t.min_score, reverse=True)
    ]
    ui.table(columns=columns, rows=rows, row_key="tier").props(
        "dense flat bordered"
    ).classes("w-full")


def _render_stacking_rules(config: ScoringConfig) -> None:
    """Render stacking rules display."""
    ui.label("Stacking Rules").classes("text-h6 q-mt-lg")

    for rule in config.stacking_rules:
        with ui.row().classes("items-center gap-3 p-2 bg-grey-1 rounded"):
            ui.label(rule.name).classes("text-subtitle2 font-medium")
            ui.badge(f"{rule.multiplier}x").props("color=blue")
            ui.label(
                f"Requires: {', '.join(sorted(rule.required_signals))}"
            ).classes("text-caption text-grey")


def _render_notification_prefs(settings: Settings) -> None:
    """Render notification preferences."""
    ui.label("Notifications").classes("text-h6 q-mt-lg")

    with ui.card().classes("w-full p-3"):
        ui.label(
            f"Briefing Time: {settings.briefing_hour}:"
            f"{settings.briefing_minute:02d} AM"
        ).classes("text-body1")
        ui.label(
            f"Recipient: "
            f"{'Configured' if settings.briefing_recipient else 'Not configured'}"
        ).classes("text-body2 text-grey")
        ui.label(
            f"SMTP: "
            f"{'Configured' if settings.smtp_username else 'Not configured'}"
        ).classes("text-body2 text-grey")


@ui.page("/settings")
async def page_settings() -> None:
    """Settings page."""
    create_layout("Settings")
    with ui.column().classes("w-full p-4"):
        ui.label("Settings").classes("text-h5")
        try:
            settings = Settings()
            config = load_scoring_config(settings.scoring_config_path)

            _render_scoring_weights(config, settings.scoring_config_path)
            _render_tier_config(config)
            _render_stacking_rules(config)
            ui.separator().classes("q-my-md")
            _render_notification_prefs(settings)

        except Exception:
            logger.exception("settings_page_error")
            ui.label("Error loading settings").classes("text-negative")
