"""Signal badge component -- signal type + points chip."""

from __future__ import annotations

from nicegui import ui

from theleadedge.dashboard.theme import get_signal_color


def signal_badge(
    signal_type: str,
    category: str = "mls",
    points: float | None = None,
) -> ui.element:
    """Render a signal badge chip.

    Parameters
    ----------
    signal_type:
        Signal name (e.g. "expired_listing").
    category:
        Signal category for color coding.
    points:
        Optional point value to display.
    """
    color = get_signal_color(category)
    display_name = signal_type.replace("_", " ").title()
    label_text = f"{display_name} (+{points:.0f})" if points else display_name

    chip = ui.chip(label_text, icon="bolt").style(
        f"background-color: {color}20; color: {color}; "
        f"border: 1px solid {color}40;"
    )
    return chip
