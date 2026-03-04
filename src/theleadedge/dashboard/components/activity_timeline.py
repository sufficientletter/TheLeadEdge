"""Activity timeline component -- chronological event feed.

Renders a vertical timeline of outreach events (calls, emails, meetings,
notes, etc.) for a single lead.  Used on the lead detail page.

IMPORTANT: Never display PII (owner phone, email) in event descriptions.
"""

from __future__ import annotations

from typing import Any

from nicegui import ui

from theleadedge.dashboard.theme import format_date

_TYPE_ICONS: dict[str, str] = {
    "call": "phone",
    "email": "email",
    "sms": "sms",
    "meeting": "handshake",
    "note": "edit_note",
    "mail": "mail",
}


def activity_timeline(events: list[dict[str, Any]]) -> ui.element:
    """Render a chronological event timeline.

    Parameters
    ----------
    events:
        List of dicts with keys: type, outcome, description,
        performed_at, follow_up_date.

    Returns
    -------
    ui.element
        The timeline container element.
    """
    with ui.column().classes("w-full gap-2") as container:
        if not events:
            ui.label("No outreach activity yet").classes(
                "text-grey q-pa-md"
            )
            return container
        for event in events:
            icon = _TYPE_ICONS.get(event.get("type", ""), "event")
            with ui.row().classes(
                "items-start gap-3 p-2 border-l-2 border-grey-3 ml-2"
            ):
                ui.icon(icon).classes("text-primary text-lg mt-1")
                with ui.column().classes("gap-0"):
                    with ui.row().classes("items-center gap-2"):
                        ui.label(
                            event.get("type", "").replace("_", " ").title()
                        ).classes("text-subtitle2 font-medium")
                        if event.get("outcome"):
                            ui.badge(event["outcome"]).props(
                                "color=blue outline"
                            )
                    if event.get("description"):
                        ui.label(event["description"]).classes(
                            "text-body2 text-grey-8"
                        )
                    ui.label(
                        format_date(event.get("performed_at"))
                    ).classes("text-caption text-grey")
                    if event.get("follow_up_date"):
                        ui.label(
                            f"Follow-up: {format_date(event['follow_up_date'])}"
                        ).classes("text-caption text-orange")
    return container
