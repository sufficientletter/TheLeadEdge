"""KPI card component -- value + label + delta indicator."""

from __future__ import annotations

from nicegui import ui


def kpi_card(
    label: str,
    value: str | int | float,
    delta: float | None = None,
    delta_label: str = "vs yesterday",
    icon: str | None = None,
    color: str = "primary",
) -> ui.card:
    """Render a KPI card with value, label, and optional delta.

    Parameters
    ----------
    label:
        Description of the metric.
    value:
        Display value (formatted string or number).
    delta:
        Optional change value (positive = green, negative = red).
    delta_label:
        Label for the delta (e.g. "vs yesterday").
    icon:
        Optional Material icon name.
    color:
        Quasar color name for accent.
    """
    with ui.card().classes("p-4 min-w-48") as card:
        with ui.row().classes("items-center gap-2"):
            if icon:
                ui.icon(icon).classes(f"text-{color} text-2xl")
            ui.label(label).classes("text-subtitle2 text-grey-7")
        ui.label(str(value)).classes("text-h4 font-bold q-mt-sm")
        if delta is not None:
            delta_color = "green" if delta >= 0 else "red"
            delta_icon = "arrow_upward" if delta >= 0 else "arrow_downward"
            with ui.row().classes("items-center gap-1 q-mt-xs"):
                ui.icon(delta_icon).classes(f"text-{delta_color} text-sm")
                ui.label(f"{delta:+.0f}").classes(
                    f"text-{delta_color} text-caption"
                )
                ui.label(delta_label).classes("text-grey-5 text-caption")
    return card
