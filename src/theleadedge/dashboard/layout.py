"""Shared layout with responsive navigation.

Provides header with notification bell, left drawer for desktop,
bottom tab bar for mobile, and dark mode toggle.

Desktop: Left drawer with labeled nav links.
Mobile: Bottom tab bar for thumb-friendly navigation.
"""

from __future__ import annotations

from nicegui import ui

NAV_ITEMS: list[dict[str, str]] = [
    {"label": "Briefing", "icon": "dashboard", "path": "/"},
    {"label": "Leads", "icon": "people", "path": "/leads"},
    {"label": "Map", "icon": "map", "path": "/map"},
    {"label": "Records", "icon": "description", "path": "/records"},
    {"label": "Analytics", "icon": "analytics", "path": "/analytics"},
    {"label": "Settings", "icon": "settings", "path": "/settings"},
]


def create_layout(title: str = "TheLeadEdge") -> ui.left_drawer:
    """Create the shared page layout with responsive navigation.

    Desktop gets a left drawer with labeled navigation links.
    Mobile gets a bottom tab bar with the first five items for
    thumb-friendly access.

    Parameters
    ----------
    title:
        Page title displayed in the header bar.

    Returns
    -------
    ui.left_drawer
        The navigation drawer element, for further customization if needed.
    """
    dark = ui.dark_mode()

    # ── Header ────────────────────────────────────────────────────────────
    with ui.header().classes("items-center justify-between bg-primary"):
        with ui.row().classes("items-center"):
            # Menu toggle (hidden on small screens where bottom bar is used)
            ui.button(
                on_click=lambda: left_drawer.toggle(), icon="menu"
            ).props("flat color=white").classes("lt-md:hidden")
            ui.label(title).classes("text-h6 text-white")
        with ui.row().classes("items-center gap-1"):
            ui.button(
                icon="dark_mode", on_click=dark.toggle
            ).props("flat color=white round")

    # ── Desktop nav drawer ────────────────────────────────────────────────
    left_drawer = ui.left_drawer(value=True).classes(
        "bg-grey-1 gt-sm:block lt-md:hidden"
    )
    with left_drawer:
        ui.label("Navigation").classes(
            "text-subtitle2 q-px-md q-pt-md text-grey"
        )
        for item in NAV_ITEMS:
            ui.button(
                item["label"],
                icon=item["icon"],
                on_click=lambda path=item["path"]: ui.navigate.to(path),
            ).classes("w-full justify-start").props("flat align=left")

    # ── Mobile bottom tab bar ─────────────────────────────────────────────
    with (
        ui.footer().classes("md:hidden bg-white border-t"),
        ui.row().classes("w-full justify-around"),
    ):
        for item in NAV_ITEMS[:5]:  # First 5 items fit mobile
            ui.button(
                icon=item["icon"],
                on_click=lambda path=item["path"]: ui.navigate.to(
                    path
                ),
            ).props("flat dense").classes("text-xs")

    return left_drawer
