"""Public records panel -- source records summary for a property.

Shows matched source records (lis pendens, probate, code violations, etc.)
in a compact card layout.  Used on the lead detail page.

IMPORTANT: Never display owner PII from source records.
"""

from __future__ import annotations

from typing import Any

from nicegui import ui

from theleadedge.dashboard.theme import format_date

_TYPE_ICONS: dict[str, str] = {
    "lis_pendens": "gavel",
    "probate": "account_balance",
    "divorce": "family_restroom",
    "code_violation": "warning",
    "tax_delinquent": "money_off",
    "property_assessment": "home_work",
}


def public_records_panel(records: list[dict[str, Any]]) -> ui.element:
    """Render a panel of matched source records.

    Parameters
    ----------
    records:
        List of dicts with keys: source_name, record_type,
        event_date, event_type.  IMPORTANT: Never include owner PII.

    Returns
    -------
    ui.element
        The panel container element.
    """
    with ui.column().classes("w-full gap-2") as container:
        if not records:
            ui.label("No public records matched").classes(
                "text-grey q-pa-md"
            )
            return container
        for rec in records:
            icon = _TYPE_ICONS.get(rec.get("record_type", ""), "description")
            with ui.row().classes(
                "items-center gap-3 p-2 bg-grey-1 rounded"
            ):
                ui.icon(icon).classes("text-orange text-lg")
                with ui.column().classes("gap-0"):
                    ui.label(
                        rec.get("record_type", "").replace("_", " ").title()
                    ).classes("text-subtitle2")
                    with ui.row().classes("gap-2"):
                        ui.label(
                            f"Source: {rec.get('source_name', '')}"
                        ).classes("text-caption text-grey")
                        if rec.get("event_date"):
                            ui.label(
                                f"Date: {format_date(rec['event_date'])}"
                            ).classes("text-caption text-grey")
    return container
