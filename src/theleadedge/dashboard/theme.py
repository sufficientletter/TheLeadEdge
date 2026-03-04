"""Dashboard theme constants and formatting helpers.

Provides consistent styling and data formatting across all dashboard pages.
Tier colors, signal category colors, and display formatters.

IMPORTANT: Never log or display PII (addresses, owner names, phone numbers).
"""

from __future__ import annotations

from datetime import datetime

# ── Tier Colors ───────────────────────────────────────────────────────────────
# S-tier (hot) = red, down to D-tier (cold) = gray.

TIER_COLORS: dict[str, str] = {
    "S": "#e74c3c",
    "A": "#e67e22",
    "B": "#f1c40f",
    "C": "#3498db",
    "D": "#95a5a6",
}

# ── Signal Category Colors ────────────────────────────────────────────────────

SIGNAL_COLORS: dict[str, str] = {
    "mls": "#2196F3",
    "public_records": "#FF9800",
    "financial": "#4CAF50",
    "behavioral": "#9C27B0",
    "external": "#607D8B",
}

# ── Tier Icons ────────────────────────────────────────────────────────────────

_TIER_ICONS: dict[str, str] = {
    "S": "\U0001f525",   # fire
    "A": "\u26a1",       # lightning
    "B": "\U0001f4ca",   # bar chart
    "C": "\U0001f4cb",   # clipboard
    "D": "\U0001f4dd",   # memo
}

_DEFAULT_TIER_ICON = "\U0001f4dd"  # memo
_DEFAULT_TIER_COLOR = "#95a5a6"    # gray
_DEFAULT_SIGNAL_COLOR = "#607D8B"  # blue-gray


def format_price(value: float | None) -> str:
    """Format a price as USD with commas, no decimals.

    Parameters
    ----------
    value:
        Dollar amount, or None.

    Returns
    -------
    str
        Formatted string like ``$1,234,567`` or ``N/A`` if None.
    """
    if value is None:
        return "N/A"
    return f"${value:,.0f}"


def format_score(score: float) -> str:
    """Format a lead score to one decimal place.

    Parameters
    ----------
    score:
        Numeric score (0-100).

    Returns
    -------
    str
        Score with one decimal, e.g. ``85.2``.
    """
    return f"{score:.1f}"


def format_date(dt: datetime | None) -> str:
    """Format a datetime for display.

    Parameters
    ----------
    dt:
        Datetime to format, or None.

    Returns
    -------
    str
        Human-readable date like ``Mar 05, 2026`` or em-dash if None.
    """
    if dt is None:
        return "\u2014"
    return dt.strftime("%b %d, %Y")


def tier_icon(tier: str) -> str:
    """Return an emoji icon for the given tier.

    Parameters
    ----------
    tier:
        Lead tier letter (S, A, B, C, D).

    Returns
    -------
    str
        Emoji string.
    """
    return _TIER_ICONS.get(tier, _DEFAULT_TIER_ICON)


def get_tier_color(tier: str) -> str:
    """Return the hex color for a tier.

    Parameters
    ----------
    tier:
        Lead tier letter (S, A, B, C, D).

    Returns
    -------
    str
        Hex color string. Defaults to gray for unknown tiers.
    """
    return TIER_COLORS.get(tier, _DEFAULT_TIER_COLOR)


def get_signal_color(category: str) -> str:
    """Return the hex color for a signal category.

    Parameters
    ----------
    category:
        Signal category name (mls, public_records, financial, etc.).

    Returns
    -------
    str
        Hex color string. Defaults to blue-gray for unknown categories.
    """
    return SIGNAL_COLORS.get(category, _DEFAULT_SIGNAL_COLOR)
