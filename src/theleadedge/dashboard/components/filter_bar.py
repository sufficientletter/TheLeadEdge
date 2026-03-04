"""Filter bar component -- tier, status, ZIP, price range filters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nicegui import ui


@dataclass
class FilterState:
    """Holds current filter selections."""

    tiers: list[str] = field(
        default_factory=lambda: ["S", "A", "B", "C", "D"]
    )
    statuses: list[str] = field(
        default_factory=lambda: [
            "new",
            "contacted",
            "qualified",
            "nurturing",
        ]
    )
    zip_code: str = ""
    min_price: float | None = None
    max_price: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for query parameters."""
        return {
            "tiers": self.tiers,
            "statuses": self.statuses,
            "zip_code": self.zip_code if self.zip_code else None,
            "min_price": self.min_price,
            "max_price": self.max_price,
        }


def filter_bar(
    state: FilterState,
    on_change: Any = None,
    zip_options: list[str] | None = None,
) -> ui.row:
    """Render a filter bar for lead/property filtering.

    Parameters
    ----------
    state:
        Current filter state (mutated in place).
    on_change:
        Callback when any filter changes.
    zip_options:
        Available ZIP codes for dropdown.
    """

    def _notify_change() -> None:
        if on_change:
            on_change(state)

    with ui.row().classes(
        "w-full items-end gap-4 flex-wrap p-2 bg-grey-1 rounded"
    ) as row:
        # Tier multi-select
        ui.select(
            label="Tiers",
            options=["S", "A", "B", "C", "D"],
            value=state.tiers,
            multiple=True,
            on_change=lambda e: (
                setattr(state, "tiers", e.value),
                _notify_change(),
            ),
        ).classes("min-w-32")

        # Status multi-select
        ui.select(
            label="Status",
            options=[
                "new",
                "contacted",
                "qualified",
                "nurturing",
                "closed",
                "stale",
            ],
            value=state.statuses,
            multiple=True,
            on_change=lambda e: (
                setattr(state, "statuses", e.value),
                _notify_change(),
            ),
        ).classes("min-w-40")

        # ZIP code
        if zip_options:
            ui.select(
                label="ZIP Code",
                options=[""] + zip_options,
                value=state.zip_code,
                on_change=lambda e: (
                    setattr(state, "zip_code", e.value),
                    _notify_change(),
                ),
            ).classes("min-w-32")
        else:
            ui.input(
                label="ZIP Code",
                value=state.zip_code,
                on_change=lambda e: (
                    setattr(state, "zip_code", e.value),
                    _notify_change(),
                ),
            ).classes("w-28")

        # Price range
        ui.number(
            label="Min Price",
            value=state.min_price,
            format="%.0f",
            on_change=lambda e: (
                setattr(state, "min_price", e.value),
                _notify_change(),
            ),
        ).classes("w-32")

        ui.number(
            label="Max Price",
            value=state.max_price,
            format="%.0f",
            on_change=lambda e: (
                setattr(state, "max_price", e.value),
                _notify_change(),
            ),
        ).classes("w-32")

        # Clear button
        def _clear() -> None:
            state.tiers = ["S", "A", "B", "C", "D"]
            state.statuses = [
                "new",
                "contacted",
                "qualified",
                "nurturing",
            ]
            state.zip_code = ""
            state.min_price = None
            state.max_price = None
            _notify_change()

        ui.button("Clear", icon="clear", on_click=_clear).props(
            "flat color=grey"
        )

    return row
