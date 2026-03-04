"""Action button group -- Call/Email/Log/Snooze buttons for leads."""

from __future__ import annotations

from typing import Any

from nicegui import ui


def action_buttons(
    lead_id: int,
    on_call: Any = None,
    on_email: Any = None,
    on_log: Any = None,
    on_snooze: Any = None,
    compact: bool = False,
) -> ui.row:
    """Render an action button group for a lead.

    Parameters
    ----------
    lead_id:
        Database lead ID (passed to callbacks).
    on_call:
        Callback for "Call" button.
    on_email:
        Callback for "Email" button.
    on_log:
        Callback for "Log Activity" button.
    on_snooze:
        Callback for "Snooze" button.
    compact:
        If True, show icon-only buttons.
    """
    with ui.row().classes("items-center gap-1") as row:
        if compact:
            if on_call:
                ui.button(
                    icon="phone",
                    on_click=lambda _lid=lead_id: on_call(_lid),
                ).props("flat round dense color=green").tooltip("Call")
            if on_email:
                ui.button(
                    icon="email",
                    on_click=lambda _lid=lead_id: on_email(_lid),
                ).props("flat round dense color=blue").tooltip("Email")
            if on_log:
                ui.button(
                    icon="edit_note",
                    on_click=lambda _lid=lead_id: on_log(_lid),
                ).props("flat round dense color=orange").tooltip(
                    "Log Activity"
                )
            if on_snooze:
                ui.button(
                    icon="snooze",
                    on_click=lambda _lid=lead_id: on_snooze(_lid),
                ).props("flat round dense color=grey").tooltip("Snooze")
        else:
            if on_call:
                ui.button(
                    "Call",
                    icon="phone",
                    on_click=lambda _lid=lead_id: on_call(_lid),
                ).props("color=green outline")
            if on_email:
                ui.button(
                    "Email",
                    icon="email",
                    on_click=lambda _lid=lead_id: on_email(_lid),
                ).props("color=blue outline")
            if on_log:
                ui.button(
                    "Log",
                    icon="edit_note",
                    on_click=lambda _lid=lead_id: on_log(_lid),
                ).props("color=orange outline")
            if on_snooze:
                ui.button(
                    "Snooze",
                    icon="snooze",
                    on_click=lambda _lid=lead_id: on_snooze(_lid),
                ).props("color=grey outline")
    return row
