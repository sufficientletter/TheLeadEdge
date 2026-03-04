"""Score gauge component -- ECharts radial gauge showing lead score.

Renders a half-circle gauge with tier-colored progress fill and
a large score number in the center.  Used on the lead detail page.
"""

from __future__ import annotations

from nicegui import ui

from theleadedge.dashboard.theme import get_tier_color


def score_gauge(score: float, tier: str) -> ui.echart:
    """Render a radial score gauge with tier-colored fill.

    Parameters
    ----------
    score:
        Numeric lead score (0-100).
    tier:
        Lead tier letter (S, A, B, C, D) for color selection.

    Returns
    -------
    ui.echart
        The ECharts gauge element.
    """
    color = get_tier_color(tier)
    chart = ui.echart({
        "series": [{
            "type": "gauge",
            "startAngle": 180,
            "endAngle": 0,
            "min": 0,
            "max": 100,
            "pointer": {"show": False},
            "progress": {
                "show": True,
                "overlap": False,
                "roundCap": True,
                "clip": False,
                "itemStyle": {"color": color},
            },
            "axisLine": {
                "lineStyle": {"width": 18, "color": [[1, "#E0E0E0"]]},
            },
            "axisTick": {"show": False},
            "splitLine": {"show": False},
            "axisLabel": {"show": False},
            "detail": {
                "valueAnimation": True,
                "fontSize": 32,
                "offsetCenter": [0, "-15%"],
                "formatter": "{value}",
            },
            "data": [{"value": round(score, 1)}],
        }],
    }).classes("w-64 h-40")
    return chart
