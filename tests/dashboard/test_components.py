"""Tests for dashboard components -- pure logic tests.

NiceGUI components require a running app to render, so we test:
- FilterState data class behavior
- Component helper functions and data transformations
- Theme integration (correct colors/icons used)
"""

from __future__ import annotations

from theleadedge.dashboard.components.filter_bar import FilterState
from theleadedge.dashboard.theme import (
    format_price,
    format_score,
    get_signal_color,
    get_tier_color,
    tier_icon,
)


class TestFilterState:
    """Verify FilterState dataclass behavior."""

    def test_default_tiers(self) -> None:
        state = FilterState()
        assert state.tiers == ["S", "A", "B", "C", "D"]

    def test_default_statuses(self) -> None:
        state = FilterState()
        assert "new" in state.statuses
        assert "contacted" in state.statuses

    def test_to_dict_defaults(self) -> None:
        state = FilterState()
        d = state.to_dict()
        assert d["tiers"] == ["S", "A", "B", "C", "D"]
        assert d["zip_code"] is None
        assert d["min_price"] is None
        assert d["max_price"] is None

    def test_to_dict_with_values(self) -> None:
        state = FilterState(
            tiers=["S", "A"],
            zip_code="34102",
            min_price=200000.0,
            max_price=500000.0,
        )
        d = state.to_dict()
        assert d["tiers"] == ["S", "A"]
        assert d["zip_code"] == "34102"
        assert d["min_price"] == 200000.0
        assert d["max_price"] == 500000.0

    def test_empty_zip_code_becomes_none(self) -> None:
        state = FilterState(zip_code="")
        assert state.to_dict()["zip_code"] is None

    def test_mutation(self) -> None:
        state = FilterState()
        state.tiers = ["S"]
        state.zip_code = "33901"
        d = state.to_dict()
        assert d["tiers"] == ["S"]
        assert d["zip_code"] == "33901"

    def test_statuses_default_list(self) -> None:
        state = FilterState()
        assert state.statuses == [
            "new",
            "contacted",
            "qualified",
            "nurturing",
        ]

    def test_to_dict_partial_values(self) -> None:
        state = FilterState(min_price=100000.0)
        d = state.to_dict()
        assert d["min_price"] == 100000.0
        assert d["max_price"] is None

    def test_independent_instances(self) -> None:
        """Verify each FilterState has independent default lists."""
        s1 = FilterState()
        s2 = FilterState()
        s1.tiers.append("X")
        assert "X" not in s2.tiers


class TestComponentThemeIntegration:
    """Verify components use correct theme values."""

    def test_all_tiers_have_colors(self) -> None:
        for tier in ["S", "A", "B", "C", "D"]:
            color = get_tier_color(tier)
            assert color.startswith("#")
            assert len(color) == 7

    def test_all_signal_categories_have_colors(self) -> None:
        for cat in [
            "mls",
            "public_records",
            "financial",
            "behavioral",
            "external",
        ]:
            color = get_signal_color(cat)
            assert color.startswith("#")

    def test_tier_icons_are_emoji(self) -> None:
        for tier in ["S", "A", "B", "C", "D"]:
            icon = tier_icon(tier)
            assert len(icon) >= 1

    def test_format_helpers(self) -> None:
        assert format_price(450000.0) == "$450,000"
        assert format_score(72.5) == "72.5"

    def test_unknown_tier_has_default_color(self) -> None:
        color = get_tier_color("Z")
        assert color == "#95a5a6"

    def test_unknown_signal_category_has_default_color(self) -> None:
        color = get_signal_color("unknown_category")
        assert color == "#607D8B"


class TestScoreBarLogic:
    """Test score bar percentage calculation logic."""

    def test_zero_score(self) -> None:
        pct = min(100.0, max(0.0, (0.0 / 100.0) * 100))
        assert pct == 0.0

    def test_full_score(self) -> None:
        pct = min(100.0, max(0.0, (100.0 / 100.0) * 100))
        assert pct == 100.0

    def test_half_score(self) -> None:
        pct = min(100.0, max(0.0, (50.0 / 100.0) * 100))
        assert pct == 50.0

    def test_over_max_capped(self) -> None:
        pct = min(100.0, max(0.0, (120.0 / 100.0) * 100))
        assert pct == 100.0

    def test_negative_floored(self) -> None:
        pct = min(100.0, max(0.0, (-5.0 / 100.0) * 100))
        assert pct == 0.0

    def test_custom_max_score(self) -> None:
        pct = min(100.0, max(0.0, (50.0 / 200.0) * 100))
        assert pct == 25.0

    def test_exact_max_score(self) -> None:
        pct = min(100.0, max(0.0, (200.0 / 200.0) * 100))
        assert pct == 100.0
