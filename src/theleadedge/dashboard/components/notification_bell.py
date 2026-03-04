"""Notification bell component -- shows count of actionable items.

Renders a bell icon button with a badge showing the notification count.
Clicking opens a dropdown menu of notification items.

IMPORTANT: Never display PII in notification items.
"""

from __future__ import annotations

from typing import Any

from nicegui import ui


def notification_bell(
    count: int = 0,
    items: list[dict[str, Any]] | None = None,
    on_click: Any = None,
) -> ui.element:
    """Render a notification bell with badge count.

    Parameters
    ----------
    count:
        Number of notifications to display in the badge.
    items:
        Optional list of notification dicts with ``title`` and
        optional ``description`` keys.  Only the first 10 are shown.
    on_click:
        Optional callback when the bell button is clicked.
        If not provided, clicking opens the dropdown menu.

    Returns
    -------
    ui.element
        The container element wrapping the bell and menu.
    """
    with ui.element("div").classes("relative") as container:
        ui.button(
            icon="notifications",
            on_click=on_click or (lambda: menu.open()),
        ).props("flat round color=white")

        if count > 0:
            ui.badge(str(count)).props("color=red floating").classes(
                "absolute"
            )

        with ui.menu().props("auto-close") as menu:
            if items:
                for item in items[:10]:
                    with ui.menu_item(), ui.column().classes("gap-0"):
                        ui.label(item.get("title", "")).classes(
                            "text-subtitle2"
                        )
                        if item.get("description"):
                            ui.label(item["description"]).classes(
                                "text-caption text-grey"
                            )
            else:
                with ui.menu_item():
                    ui.label("No notifications").classes("text-grey")

    return container
