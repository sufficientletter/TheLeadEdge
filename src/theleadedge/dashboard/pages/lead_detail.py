"""Lead Detail page -- deep-dive view for a single lead.

Shows score gauge, signal stack, property info, public records,
outreach timeline, and action dialogs.

IMPORTANT: Owner PII (name, phone, email) is shown ONLY in a
server-rendered section -- never in AG Grid or client-side JSON.
PII display requires the authenticated session.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import structlog
from nicegui import ui

from theleadedge.dashboard.app import get_settings

if TYPE_CHECKING:
    from theleadedge.config import Settings
from theleadedge.dashboard.components.activity_timeline import activity_timeline
from theleadedge.dashboard.components.public_records_panel import (
    public_records_panel,
)
from theleadedge.dashboard.components.score_gauge import score_gauge
from theleadedge.dashboard.components.signal_badge import signal_badge
from theleadedge.dashboard.components.tier_badge import tier_badge
from theleadedge.dashboard.dialogs.note_dialog import note_dialog
from theleadedge.dashboard.dialogs.outreach_form import outreach_form_dialog
from theleadedge.dashboard.layout import create_layout
from theleadedge.dashboard.theme import format_date, format_price
from theleadedge.storage.database import OutreachEventRow, get_engine, get_session
from theleadedge.storage.queries import (
    get_lead_detail,
    get_source_records_for_property,
)

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


async def _load_lead(
    settings: Settings, lead_id: int
) -> dict[str, Any] | None:
    """Load full lead detail from DB.

    Returns a dict with keys: lead, property, signals, score_history,
    outreach, source_records.  Returns None if lead not found.
    """
    engine = get_engine(settings.database_url)
    async with get_session(engine) as session:
        lead = await get_lead_detail(session, lead_id)
        if lead is None:
            return None

        prop = lead.property_rel
        signals = sorted(
            lead.signals, key=lambda s: s.points, reverse=True
        )
        score_history = sorted(
            lead.score_history,
            key=lambda s: s.calculated_at,
            reverse=True,
        )[:10]
        outreach = sorted(
            lead.outreach_events,
            key=lambda e: e.performed_at,
            reverse=True,
        )

        # Source records matched to this property
        source_records = await get_source_records_for_property(
            session, prop.id
        )

    return {
        "lead": lead,
        "property": prop,
        "signals": signals,
        "score_history": score_history,
        "outreach": outreach,
        "source_records": source_records,
    }


async def _save_outreach(settings: Settings, data: dict) -> None:
    """Persist an outreach event to the database."""
    engine = get_engine(settings.database_url)
    async with get_session(engine) as session:
        event = OutreachEventRow(
            lead_id=data["lead_id"],
            outreach_type=data["outreach_type"],
            outcome=data["outcome"],
            description=data["description"],
            performed_at=data["performed_at"],
        )
        session.add(event)


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _info_row(label: str, value: str) -> None:
    """Render a label: value info row inside a property card."""
    with ui.row().classes("w-full items-center gap-2"):
        ui.label(label).classes("text-caption text-grey-7 min-w-24")
        ui.label(value).classes("text-body2")


def _handle_save(data: dict, settings: Settings) -> None:
    """Handle outreach save (fire-and-forget async)."""
    asyncio.create_task(_save_outreach(settings, data))
    ui.notify("Outreach logged", type="positive")


def _render_detail(data: dict, settings: Settings) -> None:
    """Render the lead detail page content."""
    lead = data["lead"]
    prop = data["property"]

    # ── Header ────────────────────────────────────────────────────────────
    with ui.row().classes("w-full items-center justify-between"):
        with ui.row().classes("items-center gap-3"):
            ui.button(
                icon="arrow_back",
                on_click=lambda: ui.navigate.to("/leads"),
            ).props("flat round")
            ui.label(prop.address).classes("text-h5")
            tier_badge(lead.tier)
        with ui.row().classes("gap-2"):
            outreach_dlg = outreach_form_dialog(
                lead.id,
                on_save=lambda d: _handle_save(d, settings),
            )
            ui.button(
                "Log Outreach", icon="add_call", on_click=outreach_dlg.open
            ).props("color=primary")
            note_dlg = note_dialog(lead.id)
            ui.button(
                "Add Note", icon="note_add", on_click=note_dlg.open
            ).props("outline")

    ui.separator().classes("q-my-sm")

    # ── Two-column layout ─────────────────────────────────────────────────
    with ui.row().classes("w-full gap-6"):
        # Left column: Score + Signals
        with ui.column().classes("flex-1"):
            ui.label("Score").classes("text-h6")
            score_gauge(lead.current_score, lead.tier)

            ui.label("Active Signals").classes("text-h6 q-mt-md")
            active_signals = [s for s in data["signals"] if s.is_active]
            if active_signals:
                with ui.row().classes("flex-wrap gap-2"):
                    for sig in active_signals:
                        signal_badge(
                            sig.signal_type,
                            sig.signal_category,
                            sig.points,
                        )
            else:
                ui.label("No active signals").classes("text-grey")

            # Score History table
            if data["score_history"]:
                ui.label("Score History").classes("text-h6 q-mt-md")
                columns = [
                    {"name": "date", "label": "Date", "field": "date"},
                    {"name": "score", "label": "Score", "field": "score"},
                    {"name": "tier", "label": "Tier", "field": "tier"},
                    {"name": "reason", "label": "Reason", "field": "reason"},
                ]
                rows = [
                    {
                        "date": format_date(h.calculated_at),
                        "score": f"{h.score:.1f}",
                        "tier": h.tier,
                        "reason": (
                            h.change_reason[:50] if h.change_reason else ""
                        ),
                    }
                    for h in data["score_history"]
                ]
                ui.table(
                    columns=columns, rows=rows, row_key="date"
                ).props("dense flat bordered").classes("w-full")

        # Right column: Property Info + Records + Timeline
        with ui.column().classes("flex-1"):
            ui.label("Property Details").classes("text-h6")
            with ui.card().classes("w-full p-3"):
                _info_row(
                    "Address",
                    f"{prop.address}, {prop.city}, "
                    f"{prop.state} {prop.zip_code}",
                )
                _info_row("Price", format_price(prop.list_price))
                _info_row("Type", prop.property_type or "\u2014")
                dash = "\u2014"
                beds = prop.bedrooms or dash
                baths = prop.bathrooms or dash
                _info_row("Beds/Baths", f"{beds} / {baths}")
                _info_row(
                    "Living Area",
                    (
                        f"{prop.living_area:,.0f} sqft"
                        if prop.living_area
                        else "\u2014"
                    ),
                )
                _info_row(
                    "DOM",
                    (
                        str(prop.days_on_market)
                        if prop.days_on_market is not None
                        else "\u2014"
                    ),
                )
                _info_row("MLS Status", prop.standard_status or "\u2014")
                _info_row("Status", lead.status)
                _info_row("Detected", format_date(lead.detected_at))
                _info_row("Last Contact", format_date(lead.last_touch_at))

            # Public Records
            ui.label("Public Records").classes("text-h6 q-mt-md")
            records_data = [
                {
                    "source_name": r.source_name,
                    "record_type": r.record_type,
                    "event_date": r.event_date,
                    "event_type": r.event_type,
                }
                for r in data["source_records"]
            ]
            public_records_panel(records_data)

            # Activity Timeline
            ui.label("Outreach History").classes("text-h6 q-mt-md")
            events_data = [
                {
                    "type": e.outreach_type,
                    "outcome": e.outcome,
                    "description": e.description,
                    "performed_at": e.performed_at,
                    "follow_up_date": e.follow_up_date,
                }
                for e in data["outreach"]
            ]
            activity_timeline(events_data)


# ---------------------------------------------------------------------------
# Page route
# ---------------------------------------------------------------------------


@ui.page("/leads/{lead_id}")
async def page_lead_detail(lead_id: int) -> None:
    """Lead Detail page -- full deep-dive view for a single lead."""
    create_layout("Lead Detail")
    with ui.column().classes("w-full p-4"):
        try:
            settings: Settings = get_settings()
            data = await _load_lead(settings, lead_id)
            if data is None:
                ui.label(f"Lead #{lead_id} not found").classes(
                    "text-h5 text-negative"
                )
                return
            _render_detail(data, settings)
        except Exception:
            logger.exception("lead_detail_error", lead_id=lead_id)
            ui.label("Error loading lead details").classes("text-negative")
