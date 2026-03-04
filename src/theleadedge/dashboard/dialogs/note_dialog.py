"""Note dialog -- add a note to a lead.

Simple text-area dialog for the Realtor to attach freeform notes
to a lead record.
"""

from __future__ import annotations

from typing import Any

from nicegui import ui


def note_dialog(
    lead_id: int,
    on_save: Any = None,
) -> ui.dialog:
    """Create a dialog for adding notes to a lead.

    Parameters
    ----------
    lead_id:
        The lead to attach the note to.
    on_save:
        Callback receiving a dict with ``lead_id`` and ``note`` on save.

    Returns
    -------
    ui.dialog
        The dialog element (call ``.open()`` to show it).
    """
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Add Note").classes("text-h6")
        note_text = ui.textarea("Note").classes("w-full")

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def _save() -> None:
                if note_text.value and on_save:
                    on_save({"lead_id": lead_id, "note": note_text.value})
                dialog.close()

            ui.button("Save", on_click=_save).props("color=primary")

    return dialog
