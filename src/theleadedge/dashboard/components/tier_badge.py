"""Tier badge component -- colored S/A/B/C/D badge."""

from __future__ import annotations

from nicegui import ui

from theleadedge.dashboard.theme import get_tier_color, tier_icon


def tier_badge(tier: str, show_icon: bool = True) -> ui.badge:
    """Render a colored badge for a lead tier.

    Parameters
    ----------
    tier:
        Lead tier letter (S, A, B, C, D).
    show_icon:
        Whether to prepend the tier emoji.
    """
    color = get_tier_color(tier)
    text = f"{tier_icon(tier)} {tier}" if show_icon else tier
    badge = ui.badge(text).style(
        f"background-color: {color}; color: white; font-weight: bold; "
        f"font-size: 0.85rem; padding: 4px 10px;"
    )
    return badge
