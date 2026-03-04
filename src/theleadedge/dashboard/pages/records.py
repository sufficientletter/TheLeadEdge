"""Public Records page -- tabbed browser for source records.

Browse lis pendens, probate, code violations, tax delinquency records.
Cross-referenced with MLS data.

IMPORTANT: Never display owner PII from public records.
"""

from __future__ import annotations

from typing import Any

import structlog
from nicegui import ui

from theleadedge.config import Settings
from theleadedge.dashboard.layout import create_layout
from theleadedge.dashboard.theme import format_date
from theleadedge.storage.database import get_engine, get_session
from theleadedge.storage.queries import (
    get_match_queue_pending,
    get_source_records_by_type,
)

logger = structlog.get_logger()

RECORD_TABS: list[dict[str, str]] = [
    {"key": "lis_pendens", "label": "Lis Pendens", "icon": "gavel"},
    {"key": "probate", "label": "Probate", "icon": "account_balance"},
    {"key": "code_violation", "label": "Code Violations", "icon": "warning"},
    {"key": "tax_delinquent", "label": "Tax Delinquent", "icon": "money_off"},
]


def build_record_rows(records: list[Any]) -> list[dict[str, Any]]:
    """Convert SourceRecordRow objects to table row data.

    IMPORTANT: Never include owner PII (owner_name, mailing_address)
    in the row data.  Table data is serialized to JSON for the browser.

    Parameters
    ----------
    records:
        List of SourceRecordRow objects.

    Returns
    -------
    list[dict]
        Flat dictionaries with address, event date, source, match status.
    """
    rows: list[dict[str, Any]] = []
    for r in records:
        rows.append({
            "id": r.id,
            "source": r.source_name,
            "type": r.record_type,
            "address": r.street_address or "\u2014",
            "city": r.city or "\u2014",
            "zip": r.zip_code or "\u2014",
            "event_date": format_date(r.event_date) if r.event_date else "\u2014",
            "matched": "Yes" if r.matched_property_id else "No",
            "property_id": r.matched_property_id,
        })
    return rows


def build_queue_rows(items: list[Any]) -> list[dict[str, Any]]:
    """Convert MatchQueueRow objects to table row data.

    Parameters
    ----------
    items:
        List of MatchQueueRow objects.

    Returns
    -------
    list[dict]
        Flat dictionaries with match confidence, method, status.
    """
    rows: list[dict[str, Any]] = []
    for item in items:
        rows.append({
            "id": item.id,
            "source_record_id": item.source_record_id,
            "confidence": (
                f"{item.match_confidence:.0%}" if item.match_confidence else "\u2014"
            ),
            "method": item.match_method or "\u2014",
            "status": item.status,
        })
    return rows


async def _load_records(
    settings: Settings, record_type: str
) -> list[dict[str, Any]]:
    """Load source records of a given type."""
    engine = get_engine(settings.database_url)
    async with get_session(engine) as session:
        records = await get_source_records_by_type(session, record_type)

    return build_record_rows(list(records))


async def _load_match_queue(settings: Settings) -> list[dict[str, Any]]:
    """Load pending match queue items."""
    engine = get_engine(settings.database_url)
    async with get_session(engine) as session:
        items = await get_match_queue_pending(session)

    return build_queue_rows(list(items))


def _render_records_table(
    rows: list[dict[str, Any]], record_type: str
) -> None:
    """Render a records table for the given record type."""
    if not rows:
        ui.label(
            f"No {record_type.replace('_', ' ')} records found"
        ).classes("text-grey q-pa-md")
        return

    columns = [
        {
            "name": "address",
            "label": "Address",
            "field": "address",
            "sortable": True,
        },
        {
            "name": "city",
            "label": "City",
            "field": "city",
            "sortable": True,
        },
        {
            "name": "zip",
            "label": "ZIP",
            "field": "zip",
            "sortable": True,
        },
        {
            "name": "event_date",
            "label": "Event Date",
            "field": "event_date",
            "sortable": True,
        },
        {"name": "source", "label": "Source", "field": "source"},
        {"name": "matched", "label": "Matched", "field": "matched"},
    ]
    ui.table(
        columns=columns, rows=rows, row_key="id"
    ).props("dense flat bordered").classes("w-full")


@ui.page("/records")
async def page_records() -> None:
    """Public Records page."""
    create_layout("Public Records")
    with ui.column().classes("w-full p-4"):
        ui.label("Public Records").classes("text-h5")
        try:
            settings = Settings()

            with ui.tabs().classes("w-full") as tabs:
                for tab_info in RECORD_TABS:
                    ui.tab(
                        tab_info["key"],
                        label=tab_info["label"],
                        icon=tab_info["icon"],
                    )
                ui.tab(
                    "match_queue",
                    label="Match Queue",
                    icon="compare_arrows",
                )

            with ui.tab_panels(tabs, value="lis_pendens").classes("w-full"):
                for tab_info in RECORD_TABS:
                    with ui.tab_panel(tab_info["key"]):
                        rows = await _load_records(settings, tab_info["key"])
                        _render_records_table(rows, tab_info["key"])

                with ui.tab_panel("match_queue"):
                    queue_rows = await _load_match_queue(settings)
                    if queue_rows:
                        cols = [
                            {
                                "name": "source_record_id",
                                "label": "Record ID",
                                "field": "source_record_id",
                            },
                            {
                                "name": "confidence",
                                "label": "Confidence",
                                "field": "confidence",
                            },
                            {
                                "name": "method",
                                "label": "Method",
                                "field": "method",
                            },
                            {
                                "name": "status",
                                "label": "Status",
                                "field": "status",
                            },
                        ]
                        ui.table(
                            columns=cols, rows=queue_rows, row_key="id"
                        ).props("dense flat bordered").classes("w-full")
                    else:
                        ui.label(
                            "No pending matches in queue"
                        ).classes("text-grey q-pa-md")

            logger.info("records_page_loaded")

        except Exception:
            logger.exception("records_page_error")
            ui.label("Error loading records").classes("text-negative")
