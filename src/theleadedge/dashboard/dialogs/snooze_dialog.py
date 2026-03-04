"""Snooze dialog -- temporarily hide a lead from the active pipeline.

Provides a dialog for the Realtor to snooze a lead for a configurable
duration, removing it from the daily briefing until the snooze expires.

IMPORTANT: Never log or display PII.
"""

from __future__ import annotations

from typing import Any

from nicegui import ui

SNOOZE_DURATIONS: dict[str, str] = {
    "7": "1 Week",
    "14": "2 Weeks",
    "30": "1 Month",
    "90": "3 Months",
}


def snooze_dialog(
    lead_id: int,
    on_snooze: Any = None,
) -> ui.dialog:
    """Create a dialog for snoozing a lead.

    Parameters
    ----------
    lead_id:
        The lead to snooze.
    on_snooze:
        Callback receiving a dict with ``lead_id``, ``days``, and
        ``reason`` when the user confirms.

    Returns
    -------
    ui.dialog
        The dialog element (call ``.open()`` to show it).
    """
    with ui.dialog() as dialog, ui.card().classes("w-80"):
        ui.label("Snooze Lead").classes("text-h6")
        ui.label("Hide this lead for a period of time.").classes(
            "text-body2 text-grey"
        )

        duration = ui.select(
            "Snooze Duration",
            options=SNOOZE_DURATIONS,
            value="7",
        ).classes("w-full")

        reason = ui.input("Reason (optional)").classes("w-full")

        with ui.row().classes("w-full justify-end gap-2 q-mt-md"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def _snooze() -> None:
                result = {
                    "lead_id": lead_id,
                    "days": int(duration.value),
                    "reason": reason.value,
                }
                if on_snooze:
                    on_snooze(result)
                ui.notify(
                    f"Lead snoozed for {SNOOZE_DURATIONS[duration.value]}",
                    type="info",
                )
                dialog.close()

            ui.button("Snooze", icon="snooze", on_click=_snooze).props(
                "color=orange"
            )

    return dialog
