"""Outreach form dialog -- log a call, email, or other contact attempt.

Provides a structured form for the Realtor to record outreach activity
against a lead.  The dialog collects type, outcome, notes, and an
optional follow-up date.

IMPORTANT: Never pre-fill owner contact info (phone, email).
The Realtor looks that up themselves outside this system.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from nicegui import ui


def outreach_form_dialog(
    lead_id: int,
    on_save: Any = None,
) -> ui.dialog:
    """Create a dialog for logging outreach activity.

    Parameters
    ----------
    lead_id:
        The lead to log activity against.
    on_save:
        Callback receiving a dict with outreach data on save.

    Returns
    -------
    ui.dialog
        The dialog element (call ``.open()`` to show it).
    """
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Log Outreach").classes("text-h6")

        outreach_type = ui.select(
            "Type",
            options=["call", "email", "sms", "meeting", "mail", "note"],
            value="call",
        ).classes("w-full")

        outcome = ui.select(
            "Outcome",
            options=[
                "no_answer",
                "left_voicemail",
                "spoke_with",
                "appointment_set",
                "not_interested",
                "wrong_number",
            ],
            value="no_answer",
        ).classes("w-full")

        description = ui.textarea("Notes").classes("w-full")

        follow_up = ui.input(
            "Follow-up Date (YYYY-MM-DD)", value=""
        ).classes("w-full")

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def _save() -> None:
                result = {
                    "lead_id": lead_id,
                    "outreach_type": outreach_type.value,
                    "outcome": outcome.value,
                    "description": description.value,
                    "performed_at": datetime.utcnow(),
                    "follow_up_date": (
                        follow_up.value if follow_up.value else None
                    ),
                }
                if on_save:
                    on_save(result)
                dialog.close()

            ui.button("Save", on_click=_save).props("color=primary")

    return dialog
