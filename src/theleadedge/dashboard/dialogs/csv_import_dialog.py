"""CSV import dialog -- upload and import MLS CSV files.

Provides a dialog for uploading MLS CSV export files into the
ingestion pipeline.  The actual file processing is delegated to
the caller via the ``on_import`` callback.

IMPORTANT: Never log or display PII.
"""

from __future__ import annotations

from typing import Any

from nicegui import ui


def csv_import_dialog(
    on_import: Any = None,
) -> ui.dialog:
    """Create a dialog for CSV file import.

    Parameters
    ----------
    on_import:
        Callback invoked when the user confirms the import.

    Returns
    -------
    ui.dialog
        The dialog element (call ``.open()`` to show it).
    """
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Import CSV").classes("text-h6")
        ui.label(
            "Upload MLS CSV export files for import into the pipeline."
        ).classes("text-body2 text-grey q-mb-md")

        ui.upload(
            label="Select CSV File",
            auto_upload=False,
            max_files=1,
        ).props("accept=.csv").classes("w-full")

        with ui.row().classes("w-full justify-end gap-2 q-mt-md"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def _import() -> None:
                if on_import:
                    on_import()
                ui.notify("Import started", type="info")
                dialog.close()

            ui.button("Import", icon="upload", on_click=_import).props(
                "color=primary"
            )

    return dialog
