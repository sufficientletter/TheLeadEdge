"""Tests for dashboard theme helpers."""

from __future__ import annotations

from datetime import datetime

from theleadedge.dashboard.theme import (
    SIGNAL_COLORS,
    TIER_COLORS,
    format_date,
    format_price,
    format_score,
    get_signal_color,
    get_tier_color,
    tier_icon,
)


class TestTierColors:
    """Verify tier color constants."""

    def test_all_tiers_have_colors(self) -> None:
        for tier in ["S", "A", "B", "C", "D"]:
            assert tier in TIER_COLORS

    def test_s_tier_is_red(self) -> None:
        assert TIER_COLORS["S"] == "#e74c3c"

    def test_a_tier_is_orange(self) -> None:
        assert TIER_COLORS["A"] == "#e67e22"

    def test_b_tier_is_yellow(self) -> None:
        assert TIER_COLORS["B"] == "#f1c40f"

    def test_c_tier_is_blue(self) -> None:
        assert TIER_COLORS["C"] == "#3498db"

    def test_d_tier_is_gray(self) -> None:
        assert TIER_COLORS["D"] == "#95a5a6"


class TestSignalColors:
    """Verify signal category color constants."""

    def test_all_categories_have_colors(self) -> None:
        for cat in ["mls", "public_records", "financial", "behavioral", "external"]:
            assert cat in SIGNAL_COLORS

    def test_mls_color(self) -> None:
        assert SIGNAL_COLORS["mls"] == "#2196F3"

    def test_public_records_color(self) -> None:
        assert SIGNAL_COLORS["public_records"] == "#FF9800"


class TestFormatPrice:
    """Test price formatting."""

    def test_formats_price(self) -> None:
        assert format_price(1234567.0) == "$1,234,567"

    def test_formats_decimal_price(self) -> None:
        assert format_price(299000.99) == "$299,001"

    def test_rounds_half_to_even(self) -> None:
        assert format_price(299000.50) == "$299,000"

    def test_none_returns_na(self) -> None:
        assert format_price(None) == "N/A"

    def test_zero_price(self) -> None:
        assert format_price(0.0) == "$0"

    def test_small_price(self) -> None:
        assert format_price(100.0) == "$100"

    def test_large_price(self) -> None:
        assert format_price(25000000.0) == "$25,000,000"


class TestFormatScore:
    """Test score formatting."""

    def test_formats_score(self) -> None:
        assert format_score(85.23) == "85.2"

    def test_formats_zero(self) -> None:
        assert format_score(0.0) == "0.0"

    def test_formats_hundred(self) -> None:
        assert format_score(100.0) == "100.0"

    def test_rounds_down(self) -> None:
        assert format_score(42.34) == "42.3"

    def test_rounds_up(self) -> None:
        assert format_score(42.35) == "42.4"


class TestFormatDate:
    """Test date formatting."""

    def test_formats_date(self) -> None:
        dt = datetime(2026, 3, 5, 14, 30, 0)
        assert format_date(dt) == "Mar 05, 2026"

    def test_none_returns_dash(self) -> None:
        assert format_date(None) == "\u2014"

    def test_january(self) -> None:
        dt = datetime(2026, 1, 1)
        assert format_date(dt) == "Jan 01, 2026"

    def test_december(self) -> None:
        dt = datetime(2025, 12, 31)
        assert format_date(dt) == "Dec 31, 2025"


class TestTierIcon:
    """Test tier icon lookup."""

    def test_s_tier(self) -> None:
        assert tier_icon("S") == "\U0001f525"

    def test_a_tier(self) -> None:
        assert tier_icon("A") == "\u26a1"

    def test_b_tier(self) -> None:
        assert tier_icon("B") == "\U0001f4ca"

    def test_c_tier(self) -> None:
        assert tier_icon("C") == "\U0001f4cb"

    def test_d_tier(self) -> None:
        assert tier_icon("D") == "\U0001f4dd"

    def test_unknown_tier(self) -> None:
        assert tier_icon("X") == "\U0001f4dd"


class TestGetTierColor:
    """Test tier color lookup."""

    def test_known_tier(self) -> None:
        assert get_tier_color("S") == "#e74c3c"

    def test_unknown_tier_default(self) -> None:
        assert get_tier_color("Z") == "#95a5a6"

    def test_all_tiers(self) -> None:
        for tier, expected_color in TIER_COLORS.items():
            assert get_tier_color(tier) == expected_color


class TestGetSignalColor:
    """Test signal color lookup."""

    def test_known_category(self) -> None:
        assert get_signal_color("mls") == "#2196F3"

    def test_unknown_category_default(self) -> None:
        assert get_signal_color("unknown") == "#607D8B"

    def test_all_categories(self) -> None:
        for cat, expected_color in SIGNAL_COLORS.items():
            assert get_signal_color(cat) == expected_color
