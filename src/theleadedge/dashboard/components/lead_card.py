"""Lead card component -- compact lead summary for lists and grids."""

from __future__ import annotations

from typing import Any

from nicegui import ui

from theleadedge.dashboard.components.tier_badge import tier_badge
from theleadedge.dashboard.theme import format_price, format_score


def lead_card(
    lead_id: int,
    address: str,
    city: str,
    zip_code: str,
    tier: str,
    score: float,
    list_price: float | None = None,
    signal_count: int = 0,
    status: str = "new",
    on_click: Any = None,
) -> ui.card:
    """Render a compact lead summary card.

    Parameters
    ----------
    lead_id:
        Database lead ID.
    address:
        Property street address.
    city:
        City name.
    zip_code:
        ZIP code.
    tier:
        Lead tier letter.
    score:
        Current score.
    list_price:
        Optional listing price.
    signal_count:
        Number of active signals.
    status:
        Lead status.
    on_click:
        Optional callback when card is clicked.

    IMPORTANT: address is the street-level address only --
    never display owner PII (name, phone, email).
    """
    with ui.card().classes(
        "p-3 w-full cursor-pointer hover:shadow-lg transition-shadow"
    ) as card:
        if on_click:
            card.on("click", on_click)
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-0"):
                ui.label(address).classes("text-subtitle1 font-medium")
                ui.label(f"{city}, FL {zip_code}").classes(
                    "text-caption text-grey"
                )
            tier_badge(tier)

        with ui.row().classes(
            "w-full items-center justify-between q-mt-sm"
        ):
            with ui.row().classes("items-center gap-4"):
                with ui.row().classes("items-center gap-1"):
                    ui.icon("score").classes("text-primary text-sm")
                    ui.label(format_score(score)).classes("text-body2")
                if list_price:
                    with ui.row().classes("items-center gap-1"):
                        ui.icon("attach_money").classes(
                            "text-green text-sm"
                        )
                        ui.label(format_price(list_price)).classes(
                            "text-body2"
                        )
            with ui.row().classes("items-center gap-2"):
                if signal_count > 0:
                    ui.badge(f"{signal_count} signals").props(
                        "color=blue outline"
                    )
                status_color = "green" if status == "new" else "grey"
                ui.badge(status).props(f"color={status_color} outline")
    # lead_id kept for caller reference (data binding, navigation)
    card.lead_id = lead_id  # type: ignore[attr-defined]
    return card
