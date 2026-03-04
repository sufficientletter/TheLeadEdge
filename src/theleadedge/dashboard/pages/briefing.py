"""Morning Briefing page -- the Realtor's daily landing page.

Shows 4 KPI cards, priority actions (follow-ups due), new high-tier leads,
recent score changes, and market pulse data.

IMPORTANT: Never display owner PII (names, phone numbers, emails).
Only property addresses are shown (street, city, ZIP).
"""

from __future__ import annotations

from datetime import datetime, timedelta

import structlog
from nicegui import ui

from theleadedge.config import Settings
from theleadedge.dashboard.components.kpi_card import kpi_card
from theleadedge.dashboard.components.lead_card import lead_card
from theleadedge.dashboard.components.market_pulse_table import market_pulse_table
from theleadedge.dashboard.components.tier_badge import tier_badge
from theleadedge.dashboard.layout import create_layout
from theleadedge.dashboard.theme import format_score
from theleadedge.storage.database import get_engine, get_session
from theleadedge.storage.queries import (
    get_briefing_kpis,
    get_follow_ups_due,
    get_hot_leads,
    get_latest_market_snapshots,
    get_pipeline_summary,
    get_tier_changes,
)

logger = structlog.get_logger()


async def _load_briefing_data(settings: Settings, now: datetime) -> dict:
    """Load all data needed for the briefing page.

    Parameters
    ----------
    settings:
        Application settings (for database URL).
    now:
        Current datetime (for computing "since" windows).

    Returns
    -------
    dict
        Keys: summary, hot_leads, follow_ups, tier_changes, kpis,
        market_snapshots.
    """
    engine = get_engine(settings.database_url)
    since = now - timedelta(hours=24)

    async with get_session(engine) as session:
        summary = await get_pipeline_summary(session)
        hot_leads = await get_hot_leads(session, min_tier="B")
        follow_ups = await get_follow_ups_due(session, before=now)
        tier_changes = await get_tier_changes(session, since=since)
        kpis = await get_briefing_kpis(session)
        market_snapshots = await get_latest_market_snapshots(session)

    return {
        "summary": summary,
        "hot_leads": list(hot_leads)[:10],
        "follow_ups": list(follow_ups)[:5],
        "tier_changes": tier_changes[:5],
        "kpis": kpis,
        "market_snapshots": market_snapshots,
    }


def _render_briefing(data: dict) -> None:
    """Render the briefing page content.

    Parameters
    ----------
    data:
        Data dict from ``_load_briefing_data``.
    """
    kpis = data["kpis"]

    # -- KPI Cards Row ---------------------------------------------------------
    with ui.row().classes("w-full gap-4 flex-wrap"):
        kpi_card(
            "Active Leads", kpis["total_active"], icon="people", color="primary"
        )
        kpi_card(
            "Hot Leads",
            kpis["hot_count"],
            icon="local_fire_department",
            color="red",
        )
        kpi_card(
            "Follow-ups Due",
            kpis["follow_ups_due"],
            icon="schedule",
            color="orange",
        )
        kpi_card(
            "New Today", kpis["new_today"], icon="fiber_new", color="green"
        )

    ui.separator().classes("q-my-md")

    # -- Two-column layout: Priority Actions | Hot Leads -----------------------
    with ui.row().classes("w-full gap-4"):
        # Left column: Follow-ups due
        with ui.column().classes("flex-1"):
            ui.label("Priority Actions").classes("text-h6")
            if data["follow_ups"]:
                for lead_row in data["follow_ups"]:
                    prop = lead_row.property_rel
                    lead_card(
                        lead_id=lead_row.id,
                        address=prop.address,
                        city=prop.city,
                        zip_code=prop.zip_code,
                        tier=lead_row.tier,
                        score=lead_row.current_score,
                        list_price=prop.list_price,
                        signal_count=lead_row.signal_count,
                        status=lead_row.status,
                        on_click=lambda lid=lead_row.id: ui.navigate.to(
                            f"/leads/{lid}"
                        ),
                    )
            else:
                ui.label("No follow-ups due").classes("text-grey q-pa-md")

        # Right column: Hot leads
        with ui.column().classes("flex-1"):
            ui.label("Hot Leads").classes("text-h6")
            if data["hot_leads"]:
                for lead_row in data["hot_leads"][:5]:
                    prop = lead_row.property_rel
                    lead_card(
                        lead_id=lead_row.id,
                        address=prop.address,
                        city=prop.city,
                        zip_code=prop.zip_code,
                        tier=lead_row.tier,
                        score=lead_row.current_score,
                        list_price=prop.list_price,
                        signal_count=lead_row.signal_count,
                        status=lead_row.status,
                        on_click=lambda lid=lead_row.id: ui.navigate.to(
                            f"/leads/{lid}"
                        ),
                    )
            else:
                ui.label("No hot leads yet").classes("text-grey q-pa-md")

    # -- Tier Changes ----------------------------------------------------------
    if data["tier_changes"]:
        ui.separator().classes("q-my-md")
        ui.label("Recent Score Changes").classes("text-h6")
        with ui.column().classes("w-full gap-2"):
            for change in data["tier_changes"]:
                change_lead = change["lead"]
                prop = change_lead.property_rel
                with ui.row().classes("items-center gap-2 p-2 bg-grey-1 rounded"):
                    ui.label(prop.address).classes("text-body1")
                    tier_badge(change["old_tier"])
                    ui.icon("arrow_forward").classes("text-grey")
                    tier_badge(change["new_tier"])
                    ui.label(
                        f"{format_score(change['old_score'])} "
                        f"-> {format_score(change['new_score'])}"
                    ).classes("text-caption text-grey")

    # -- Market Pulse ----------------------------------------------------------
    if data["market_snapshots"]:
        ui.separator().classes("q-my-md")
        ui.label("Market Pulse").classes("text-h6")
        market_pulse_table(data["market_snapshots"])

    # -- Pipeline Summary Footer -----------------------------------------------
    summary = data["summary"]
    ui.separator().classes("q-my-md")
    with ui.row().classes("w-full items-center gap-4"):
        ui.label("Pipeline Summary").classes("text-subtitle1 text-grey-7")
        for tier_letter in ["S", "A", "B", "C", "D"]:
            count = summary["tiers"].get(tier_letter, 0)
            if count > 0:
                with ui.row().classes("items-center gap-1"):
                    tier_badge(tier_letter)
                    ui.label(str(count)).classes("text-body2")


@ui.page("/")
async def page_briefing() -> None:
    """Morning Briefing dashboard -- main landing page."""
    create_layout("Morning Briefing")
    with ui.column().classes("w-full p-4"):
        try:
            settings = Settings()
            now = datetime.utcnow()
            data = await _load_briefing_data(settings, now)
            _render_briefing(data)
        except Exception:
            logger.exception("briefing_page_load_error")
            ui.label("Morning Briefing").classes("text-h4")
            ui.label(
                "Unable to load briefing data. Check logs for details."
            ).classes("text-negative")
