"""Lead Pipeline page -- AG Grid table of all active leads.

Provides filterable, sortable lead management with inline actions.
Uses AG Grid (bundled with NiceGUI) for high-performance rendering.

IMPORTANT: Owner PII is NEVER included in AG Grid rowData (client-side JSON).
Only street-level address, city, ZIP, and MLS data are displayed.
"""

from __future__ import annotations

from typing import Any

import structlog
from nicegui import app, ui

from theleadedge.config import Settings
from theleadedge.dashboard.components.filter_bar import FilterState, filter_bar
from theleadedge.dashboard.layout import create_layout
from theleadedge.dashboard.theme import (
    format_date,
    format_price,
    get_tier_color,
)
from theleadedge.storage.database import LeadRow, get_engine, get_session
from theleadedge.storage.queries import get_leads_for_grid

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Grid data transformation
# ---------------------------------------------------------------------------

# AG Grid column definitions for the lead pipeline table.
_COLUMN_DEFS: list[dict[str, Any]] = [
    {
        "headerName": "Tier",
        "field": "tier",
        "width": 80,
        "sortable": True,
        "filter": True,
        "cellStyle": {"textAlign": "center", "fontWeight": "bold"},
    },
    {
        "headerName": "Score",
        "field": "score",
        "width": 90,
        "sortable": True,
        "filter": "agNumberColumnFilter",
        "sort": "desc",
    },
    {
        "headerName": "Address",
        "field": "address",
        "flex": 2,
        "sortable": True,
        "filter": True,
    },
    {
        "headerName": "City",
        "field": "city",
        "width": 120,
        "sortable": True,
        "filter": True,
    },
    {
        "headerName": "ZIP",
        "field": "zip_code",
        "width": 90,
        "sortable": True,
        "filter": True,
    },
    {
        "headerName": "List Price",
        "field": "list_price_display",
        "width": 130,
        "sortable": True,
        "comparator": "__raw_price_comparator__",
    },
    {
        "headerName": "Signals",
        "field": "signals",
        "width": 90,
        "sortable": True,
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "DOM",
        "field": "dom",
        "width": 80,
        "sortable": True,
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "Type",
        "field": "property_type",
        "width": 120,
        "sortable": True,
        "filter": True,
    },
    {
        "headerName": "MLS Status",
        "field": "mls_status",
        "width": 120,
        "sortable": True,
        "filter": True,
    },
    {
        "headerName": "Status",
        "field": "status",
        "width": 110,
        "sortable": True,
        "filter": True,
    },
    {
        "headerName": "Detected",
        "field": "detected",
        "width": 130,
        "sortable": True,
    },
]


def build_grid_data(leads: list[LeadRow]) -> list[dict[str, Any]]:
    """Convert LeadRow objects to AG Grid row data.

    IMPORTANT: Never include owner PII (name, phone, email) in grid data.
    Grid data is serialized to JSON and sent to the browser.

    Parameters
    ----------
    leads:
        List of LeadRow objects with property_rel eagerly loaded.

    Returns
    -------
    list[dict]
        Flat dictionaries suitable for AG Grid rowData.
    """
    rows: list[dict[str, Any]] = []
    for lead in leads:
        prop = lead.property_rel
        rows.append({
            "id": lead.id,
            "address": prop.address if prop else "\u2014",
            "city": prop.city if prop else "\u2014",
            "zip_code": prop.zip_code if prop else "\u2014",
            "tier": lead.tier,
            "score": round(lead.current_score, 1),
            "signals": lead.signal_count,
            "list_price": prop.list_price if prop else None,
            "list_price_display": format_price(
                prop.list_price if prop else None
            ),
            "dom": prop.days_on_market if prop else None,
            "property_type": (prop.property_type if prop else None) or "\u2014",
            "mls_status": (
                prop.standard_status if prop else None
            ) or "\u2014",
            "status": lead.status,
            "detected": (
                format_date(lead.detected_at) if lead.detected_at else "\u2014"
            ),
        })
    return rows


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


async def _load_leads(
    settings: Settings, filters: FilterState
) -> list[LeadRow]:
    """Load leads from the database with filters applied."""
    engine = get_engine(settings.database_url)
    filter_dict = filters.to_dict()

    async with get_session(engine) as session:
        leads = await get_leads_for_grid(
            session,
            tiers=filter_dict["tiers"],
            statuses=filter_dict["statuses"],
            zip_code=filter_dict["zip_code"],
            min_price=filter_dict["min_price"],
            max_price=filter_dict["max_price"],
        )

    return list(leads)


# ---------------------------------------------------------------------------
# Tier color styling for AG Grid cells
# ---------------------------------------------------------------------------


def _tier_cell_style(tier: str) -> dict[str, str]:
    """Return inline CSS for a tier cell."""
    color = get_tier_color(tier)
    return {
        "color": "white",
        "backgroundColor": color,
        "textAlign": "center",
        "fontWeight": "bold",
        "borderRadius": "4px",
    }


# ---------------------------------------------------------------------------
# Page route
# ---------------------------------------------------------------------------


@ui.page("/leads")
async def page_leads() -> None:
    """Lead Pipeline page -- AG Grid of all active leads."""
    create_layout("Lead Pipeline")

    settings: Settings = app.storage.general.get("settings", Settings())
    filters = FilterState()

    # ── Header section ───────────────────────────────────────────────────
    with ui.column().classes("w-full p-4 gap-4"):
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Lead Pipeline").classes("text-h4")
            refresh_btn = ui.button(
                "Refresh", icon="refresh"
            ).props("outline color=primary")

        # ── Filter bar ───────────────────────────────────────────────────
        async def _on_filter_change(_state: FilterState) -> None:
            """Reload grid data when filters change."""
            await _refresh_grid()

        filter_bar(
            state=filters,
            on_change=lambda s: ui.timer(
                0.1, lambda: _on_filter_change(s), once=True
            ),
        )

        # ── Summary row ──────────────────────────────────────────────────
        summary_label = ui.label("Loading...").classes("text-subtitle1 text-grey")

        # ── AG Grid ──────────────────────────────────────────────────────
        grid = ui.aggrid({
            "columnDefs": _COLUMN_DEFS,
            "rowData": [],
            "defaultColDef": {
                "resizable": True,
                "sortable": True,
            },
            "rowSelection": "single",
            "animateRows": True,
            "pagination": True,
            "paginationPageSize": 50,
            "domLayout": "autoHeight",
        }).classes("w-full")

        # ── Row click handler ────────────────────────────────────────────
        async def _on_row_click(e: Any) -> None:
            """Navigate to lead detail page on row click."""
            row_data = e.args.get("data", {}) if isinstance(e.args, dict) else {}
            lead_id = row_data.get("id")
            if lead_id:
                ui.navigate.to(f"/leads/{lead_id}")

        grid.on("cellClicked", _on_row_click)

        # ── Refresh function ─────────────────────────────────────────────
        async def _refresh_grid() -> None:
            """Reload lead data from the database and update the grid."""
            try:
                leads = await _load_leads(settings, filters)
                row_data = build_grid_data(leads)
                grid.options["rowData"] = row_data
                grid.update()

                # Update summary
                total = len(row_data)
                tier_counts: dict[str, int] = {}
                for row in row_data:
                    t = row.get("tier", "D")
                    tier_counts[t] = tier_counts.get(t, 0) + 1

                parts = [f"{total} leads"]
                for tier in ["S", "A", "B", "C", "D"]:
                    count = tier_counts.get(tier, 0)
                    if count > 0:
                        parts.append(f"{tier}: {count}")
                summary_label.set_text(" | ".join(parts))

                logger.info(
                    "leads_grid_refreshed", total=total, tier_counts=tier_counts
                )
            except Exception:
                logger.exception("leads_grid_refresh_failed")
                summary_label.set_text("Error loading leads")

        refresh_btn.on_click(_refresh_grid)

        # ── Initial load ─────────────────────────────────────────────────
        await _refresh_grid()
