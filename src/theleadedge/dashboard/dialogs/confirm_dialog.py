"""Confirm dialog -- generic confirmation prompt.

Provides a reusable confirmation dialog that can be customized with
a title, message, button text, and callbacks.
"""

from __future__ import annotations

from typing import Any

from nicegui import ui


def confirm_dialog(
    title: str = "Confirm",
    message: str = "Are you sure?",
    on_confirm: Any = None,
    on_cancel: Any = None,
    confirm_text: str = "Confirm",
    confirm_color: str = "primary",
) -> ui.dialog:
    """Create a generic confirmation dialog.

    Parameters
    ----------
    title:
        Dialog title text.
    message:
        Body message displayed to the user.
    on_confirm:
        Callback invoked when the user confirms.
    on_cancel:
        Callback invoked when the user cancels.
    confirm_text:
        Label for the confirm button.
    confirm_color:
        Quasar color name for the confirm button.

    Returns
    -------
    ui.dialog
        The dialog element (call ``.open()`` to show it).
    """
    with ui.dialog() as dialog, ui.card().classes("w-80"):
        ui.label(title).classes("text-h6")
        ui.label(message).classes("text-body1 q-my-md")

        with ui.row().classes("w-full justify-end gap-2"):

            def _cancel() -> None:
                if on_cancel:
                    on_cancel()
                dialog.close()

            def _confirm() -> None:
                if on_confirm:
                    on_confirm()
                dialog.close()

            ui.button("Cancel", on_click=_cancel).props("flat")
            ui.button(confirm_text, on_click=_confirm).props(
                f"color={confirm_color}"
            )

    return dialog
