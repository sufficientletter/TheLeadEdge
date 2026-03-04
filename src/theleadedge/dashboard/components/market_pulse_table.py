"""Market pulse table -- recent market stats by ZIP code.

Renders a sortable table of market snapshot data from MarketSnapshotRow.
Used on the Morning Briefing page to give the Realtor a quick market
overview alongside lead data.

IMPORTANT: Never display owner PII (names, phone numbers, emails).
"""

from __future__ import annotations

from typing import Any

from nicegui import ui

from theleadedge.dashboard.theme import format_price


def market_pulse_table(snapshots: list[dict[str, Any]]) -> ui.element:
    """Render a market pulse summary table.

    Parameters
    ----------
    snapshots:
        List of dicts with keys: zip_code, median_sale_price, median_dom,
        inventory, months_of_supply, absorption_rate.

    Returns
    -------
    ui.element
        The table element, or a placeholder label if no data.
    """
    columns = [
        {"name": "zip_code", "label": "ZIP", "field": "zip_code", "sortable": True},
        {
            "name": "median_sale_price",
            "label": "Median Price",
            "field": "median_sale_price",
            "sortable": True,
        },
        {"name": "median_dom", "label": "DOM", "field": "median_dom", "sortable": True},
        {
            "name": "inventory",
            "label": "Inventory",
            "field": "inventory",
            "sortable": True,
        },
        {
            "name": "months_of_supply",
            "label": "Months Supply",
            "field": "months_of_supply",
            "sortable": True,
        },
    ]

    rows: list[dict[str, str]] = []
    for s in snapshots:
        rows.append(
            {
                "zip_code": s.get("zip_code", ""),
                "median_sale_price": format_price(s.get("median_sale_price")),
                "median_dom": str(s.get("median_dom", "\u2014")),
                "inventory": str(s.get("inventory", "\u2014")),
                "months_of_supply": (
                    f"{s.get('months_of_supply', 0):.1f}"
                    if s.get("months_of_supply") is not None
                    else "\u2014"
                ),
            }
        )

    if not rows:
        with ui.element("div") as container:
            ui.label("No market data available").classes("text-grey q-pa-md")
        return container

    table = ui.table(columns=columns, rows=rows, row_key="zip_code").classes("w-full")
    table.props("dense flat bordered")
    return table
