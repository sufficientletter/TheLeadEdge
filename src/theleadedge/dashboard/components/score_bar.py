"""Score bar component -- horizontal bar with tier-colored fill."""

from __future__ import annotations

from nicegui import ui

from theleadedge.dashboard.theme import get_tier_color


def score_bar(
    score: float,
    tier: str,
    max_score: float = 100.0,
) -> ui.element:
    """Render a horizontal score bar with tier coloring.

    Parameters
    ----------
    score:
        Current score value.
    tier:
        Lead tier for color.
    max_score:
        Maximum possible score (for percentage calculation).
    """
    pct = min(100.0, max(0.0, (score / max_score) * 100))
    color = get_tier_color(tier)

    with ui.element("div").classes("w-full") as container:
        ui.label(f"{score:.1f}").classes("text-caption text-grey-7")
        with ui.element("div").style(
            "width: 100%; height: 8px; background-color: #e0e0e0; "
            "border-radius: 4px; overflow: hidden;"
        ):
            ui.element("div").style(
                f"width: {pct}%; height: 100%; "
                f"background-color: {color}; border-radius: 4px; "
                f"transition: width 0.3s ease;"
            )
    return container
