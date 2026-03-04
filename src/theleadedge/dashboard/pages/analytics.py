"""Analytics page -- ECharts visualizations for lead pipeline metrics.

Shows conversion funnel, score distribution, signal performance,
tier trends, and source ROI.
"""

from __future__ import annotations

from typing import Any

import structlog
from nicegui import ui

from theleadedge.config import Settings
from theleadedge.dashboard.layout import create_layout
from theleadedge.dashboard.theme import TIER_COLORS
from theleadedge.storage.database import get_engine, get_session
from theleadedge.storage.queries import (
    get_conversion_funnel,
    get_signal_performance,
    get_source_roi,
    get_tier_distribution_over_time,
)

logger = structlog.get_logger()


def _funnel_chart(funnel: dict[str, Any]) -> None:
    """Render a conversion funnel chart.

    Parameters
    ----------
    funnel:
        Dict with status counts (new, contacted, etc.) and
        a nested ``score_distribution`` dict.
    """
    ui.label("Conversion Funnel").classes("text-h6")
    # Exclude score_distribution from funnel data
    data = [
        {"value": v, "name": k.replace("_", " ").title()}
        for k, v in funnel.items()
        if v and isinstance(v, int) and v > 0
    ]
    if not data:
        ui.label("No funnel data yet").classes("text-grey")
        return
    ui.echart({
        "series": [{
            "type": "funnel",
            "data": data,
            "gap": 2,
            "label": {"show": True, "position": "inside"},
        }],
    }).classes("w-full h-64")


def _score_distribution_chart(distribution: dict[str, int]) -> None:
    """Render a score distribution bar chart.

    Parameters
    ----------
    distribution:
        Dict mapping score bucket labels (e.g. "0-10") to counts.
    """
    ui.label("Score Distribution").classes("text-h6")
    categories = list(distribution.keys())
    values = list(distribution.values())
    if not values or all(v == 0 for v in values):
        ui.label("No scoring data yet").classes("text-grey")
        return
    ui.echart({
        "xAxis": {"type": "category", "data": categories},
        "yAxis": {"type": "value"},
        "series": [{
            "data": values,
            "type": "bar",
            "itemStyle": {"color": "#3498db"},
        }],
    }).classes("w-full h-64")


def _signal_performance_chart(signals: list[dict[str, Any]]) -> None:
    """Render a signal performance horizontal bar chart.

    Parameters
    ----------
    signals:
        List of dicts with ``signal_type`` and ``count`` keys.
    """
    ui.label("Signal Performance").classes("text-h6")
    if not signals:
        ui.label("No signal data yet").classes("text-grey")
        return
    names = [s["signal_type"].replace("_", " ").title() for s in signals]
    counts = [s["count"] for s in signals]
    ui.echart({
        "yAxis": {"type": "category", "data": names},
        "xAxis": {"type": "value"},
        "series": [{
            "data": counts,
            "type": "bar",
            "itemStyle": {"color": "#e67e22"},
        }],
        "grid": {"left": "30%"},
    }).classes("w-full h-80")


def _tier_trend_chart(trends: list[dict[str, Any]]) -> None:
    """Render tier distribution over time as stacked area chart.

    Parameters
    ----------
    trends:
        List of dicts with ``date`` and tier count keys (S, A, B, C, D).
    """
    ui.label("Tier Trends").classes("text-h6")
    if not trends:
        ui.label("No trend data yet").classes("text-grey")
        return

    dates = [t["date"] for t in trends]
    series = []
    for tier in ["S", "A", "B", "C", "D"]:
        series.append({
            "name": f"Tier {tier}",
            "type": "line",
            "stack": "tiers",
            "areaStyle": {},
            "data": [t.get(tier, 0) for t in trends],
            "itemStyle": {"color": TIER_COLORS.get(tier, "#95a5a6")},
        })

    ui.echart({
        "tooltip": {"trigger": "axis"},
        "legend": {
            "data": [f"Tier {t}" for t in ["S", "A", "B", "C", "D"]],
        },
        "xAxis": {"type": "category", "data": dates},
        "yAxis": {"type": "value"},
        "series": series,
    }).classes("w-full h-64")


def _source_roi_chart(sources: list[dict[str, Any]]) -> None:
    """Render source ROI pie chart.

    Parameters
    ----------
    sources:
        List of dicts with ``source`` and ``count`` keys.
    """
    ui.label("Lead Sources").classes("text-h6")
    if not sources:
        ui.label("No source data yet").classes("text-grey")
        return
    data = [
        {
            "value": s["count"],
            "name": s["source"].replace("_", " ").title(),
        }
        for s in sources
    ]
    ui.echart({
        "series": [{
            "type": "pie",
            "radius": ["40%", "70%"],
            "data": data,
            "label": {"show": True},
        }],
    }).classes("w-full h-64")


@ui.page("/analytics")
async def page_analytics() -> None:
    """Analytics page."""
    create_layout("Analytics")
    with ui.column().classes("w-full p-4"):
        ui.label("Analytics").classes("text-h5")
        try:
            settings = Settings()
            engine = get_engine(settings.database_url)

            async with get_session(engine) as session:
                funnel = await get_conversion_funnel(session)
                signals = await get_signal_performance(session)
                trends = await get_tier_distribution_over_time(session)
                sources = await get_source_roi(session)

            with ui.row().classes("w-full gap-6"):
                with ui.column().classes("flex-1"):
                    _funnel_chart(funnel)
                with ui.column().classes("flex-1"):
                    _score_distribution_chart(
                        funnel.get("score_distribution", {})
                    )

            ui.separator().classes("q-my-md")

            with ui.row().classes("w-full gap-6"):
                with ui.column().classes("flex-1"):
                    _signal_performance_chart(signals)
                with ui.column().classes("flex-1"):
                    _source_roi_chart(sources)

            ui.separator().classes("q-my-md")
            _tier_trend_chart(trends)

            logger.info(
                "analytics_page_loaded",
                funnel_statuses=len(funnel) - 1,
                signal_types=len(signals),
                trend_dates=len(trends),
                source_count=len(sources),
            )

        except Exception:
            logger.exception("analytics_page_error")
            ui.label("Error loading analytics").classes("text-negative")
