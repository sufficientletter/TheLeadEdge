"""Map View page -- geographic lead visualization with Leaflet.

Displays leads on a map with tier-colored markers.  Clicking a marker
shows property address, tier, score, and a link to the detail page.

IMPORTANT: Never display owner PII in map popups.
"""

from __future__ import annotations

from typing import Any

import structlog
from nicegui import ui

from theleadedge.config import Settings
from theleadedge.dashboard.layout import create_layout
from theleadedge.dashboard.theme import TIER_COLORS, format_price
from theleadedge.storage.database import get_engine, get_session
from theleadedge.storage.queries import get_leads_for_map

logger = structlog.get_logger()

# SWFLA center coordinates
_DEFAULT_CENTER = (26.45, -81.80)
_DEFAULT_ZOOM = 10


def build_marker_data(leads: list[Any]) -> list[dict[str, Any]]:
    """Convert leads to marker data for the map.

    IMPORTANT: Never include owner PII (name, phone, email) in marker
    data.  Marker data is serialized to JSON and sent to the browser.

    Parameters
    ----------
    leads:
        List of LeadRow objects with property_rel eagerly loaded.

    Returns
    -------
    list[dict]
        Flat dictionaries with lat/lng, tier, score, address info.
    """
    markers: list[dict[str, Any]] = []
    for lead in leads:
        prop = lead.property_rel
        if prop and prop.latitude is not None and prop.longitude is not None:
            markers.append({
                "lat": prop.latitude,
                "lng": prop.longitude,
                "lead_id": lead.id,
                "address": prop.address,
                "city": prop.city or "",
                "zip_code": prop.zip_code or "",
                "tier": lead.tier,
                "score": lead.current_score,
                "list_price": prop.list_price,
                "color": TIER_COLORS.get(lead.tier, "#95a5a6"),
            })
    return markers


async def _load_map_data(settings: Settings) -> list[dict[str, Any]]:
    """Load leads with coordinates for the map."""
    engine = get_engine(settings.database_url)
    async with get_session(engine) as session:
        leads = await get_leads_for_map(session)

    return build_marker_data(list(leads))


@ui.page("/map")
async def page_map() -> None:
    """Map View page."""
    create_layout("Map View")
    with ui.column().classes("w-full p-4"):
        ui.label("Lead Map").classes("text-h5")
        try:
            settings = Settings()
            markers = await _load_map_data(settings)

            m = ui.leaflet(
                center=_DEFAULT_CENTER, zoom=_DEFAULT_ZOOM
            ).classes("w-full").style("height: 600px;")

            for mkr in markers:
                m.generic_layer(
                    name="marker",
                    args=[[mkr["lat"], mkr["lng"]]],
                ).run_method(
                    "bindPopup",
                    (
                        f"<b>{mkr['address']}</b><br>"
                        f"{mkr['city']}, FL {mkr['zip_code']}<br>"
                        f"Tier: {mkr['tier']} | "
                        f"Score: {mkr['score']:.1f}<br>"
                        f"Price: {format_price(mkr['list_price'])}<br>"
                        f"<a href='/leads/{mkr['lead_id']}'>"
                        f"View Details</a>"
                    ),
                )

            ui.label(
                f"{len(markers)} leads with coordinates"
            ).classes("text-caption text-grey q-mt-sm")

            logger.info("map_view_loaded", marker_count=len(markers))

        except Exception:
            logger.exception("map_view_error")
            ui.label("Error loading map data").classes("text-negative")
