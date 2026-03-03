"""Unit tests for signal stacking bonus calculator.

Tests the best-single-rule algorithm that applies multiplier bonuses
when specific signal combinations co-occur on a lead.
"""

from __future__ import annotations

import pytest

from theleadedge.scoring.config_loader import StackingRule
from theleadedge.scoring.stacking import calculate_stacking_bonus

# ---------------------------------------------------------------------------
# Helper: build a stacking rule
# ---------------------------------------------------------------------------


def _rule(
    name: str,
    signals: list[str],
    multiplier: float,
) -> StackingRule:
    return StackingRule(
        name=name,
        required_signals=set(signals),
        multiplier=multiplier,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestStackingBonus:
    """Signal stacking bonus calculation tests."""

    def test_no_matching_rules(self) -> None:
        """When no stacking rule is satisfied, bonus is zero."""
        rules = [
            _rule("r1", ["expired_listing", "high_dom"], 1.5),
        ]
        bonus, rule_name = calculate_stacking_bonus(
            active_signal_types={"price_reduction"},
            signal_points_by_type={"price_reduction": 8.0},
            stacking_rules=rules,
        )
        assert bonus == 0.0
        assert rule_name is None

    def test_distressed_seller_triggers(self) -> None:
        """Distressed seller rule triggers with all 3 required signals."""
        rules = [
            _rule(
                "distressed_seller",
                ["expired_listing", "price_reduction_multiple", "high_dom"],
                1.5,
            ),
        ]
        signal_types = {"expired_listing", "price_reduction_multiple", "high_dom"}
        points = {
            "expired_listing": 15.0,
            "price_reduction_multiple": 14.0,
            "high_dom": 11.0,
        }
        bonus, rule_name = calculate_stacking_bonus(
            active_signal_types=signal_types,
            signal_points_by_type=points,
            stacking_rules=rules,
        )
        # Bonus = (15 + 14 + 11) * (1.5 - 1.0) = 40 * 0.5 = 20.0
        assert bonus == pytest.approx(20.0)
        assert rule_name == "distressed_seller"

    def test_financial_distress_triggers(self) -> None:
        """Financial distress rule with 2.0x multiplier."""
        rules = [
            _rule("financial_distress", ["pre_foreclosure", "tax_delinquent"], 2.0),
        ]
        signal_types = {"pre_foreclosure", "tax_delinquent", "high_dom"}
        points = {
            "pre_foreclosure": 20.0,
            "tax_delinquent": 13.0,
            "high_dom": 11.0,
        }
        bonus, rule_name = calculate_stacking_bonus(
            active_signal_types=signal_types,
            signal_points_by_type=points,
            stacking_rules=rules,
        )
        # Bonus = (20 + 13) * (2.0 - 1.0) = 33.0
        assert bonus == pytest.approx(33.0)
        assert rule_name == "financial_distress"

    def test_life_event_vacant_highest_multiplier(self) -> None:
        """Life event + vacant rule with 2.5x multiplier (highest)."""
        rules = [
            _rule(
                "life_event_vacant",
                ["probate", "absentee_owner", "vacant_property"],
                2.5,
            ),
        ]
        signal_types = {"probate", "absentee_owner", "vacant_property"}
        points = {
            "probate": 18.0,
            "absentee_owner": 8.0,
            "vacant_property": 10.0,
        }
        bonus, rule_name = calculate_stacking_bonus(
            active_signal_types=signal_types,
            signal_points_by_type=points,
            stacking_rules=rules,
        )
        # Bonus = (18 + 8 + 10) * (2.5 - 1.0) = 36 * 1.5 = 54.0
        assert bonus == pytest.approx(54.0)
        assert rule_name == "life_event_vacant"

    def test_best_single_rule_wins(self) -> None:
        """When multiple rules match, the one producing highest bonus wins."""
        rules = [
            _rule("rule_low", ["expired_listing", "high_dom"], 1.3),
            _rule(
                "rule_high",
                ["expired_listing", "price_reduction_multiple", "high_dom"],
                1.5,
            ),
        ]
        signal_types = {"expired_listing", "price_reduction_multiple", "high_dom"}
        points = {
            "expired_listing": 15.0,
            "price_reduction_multiple": 14.0,
            "high_dom": 11.0,
        }
        bonus, rule_name = calculate_stacking_bonus(
            active_signal_types=signal_types,
            signal_points_by_type=points,
            stacking_rules=rules,
        )
        # rule_low bonus  = (15 + 11) * 0.3 = 7.8
        # rule_high bonus = (15 + 14 + 11) * 0.5 = 20.0
        assert bonus == pytest.approx(20.0)
        assert rule_name == "rule_high"

    def test_partial_match_no_bonus(self) -> None:
        """Only 2 of 3 required signals present -- no bonus awarded."""
        rules = [
            _rule(
                "needs_three",
                ["expired_listing", "price_reduction_multiple", "high_dom"],
                1.5,
            ),
        ]
        # Missing high_dom
        signal_types = {"expired_listing", "price_reduction_multiple"}
        points = {
            "expired_listing": 15.0,
            "price_reduction_multiple": 14.0,
        }
        bonus, rule_name = calculate_stacking_bonus(
            active_signal_types=signal_types,
            signal_points_by_type=points,
            stacking_rules=rules,
        )
        assert bonus == 0.0
        assert rule_name is None

    def test_empty_signals_no_bonus(self) -> None:
        """No active signals produces zero bonus."""
        rules = [
            _rule("r1", ["expired_listing"], 1.5),
        ]
        bonus, rule_name = calculate_stacking_bonus(
            active_signal_types=set(),
            signal_points_by_type={},
            stacking_rules=rules,
        )
        assert bonus == 0.0
        assert rule_name is None

    def test_stacking_rules_from_config(self, scoring_config) -> None:
        """Verify stacking rules load correctly from real YAML config."""
        assert len(scoring_config.stacking_rules) >= 4
        rule_names = {r.name for r in scoring_config.stacking_rules}
        assert "distressed_seller" in rule_names
        assert "financial_distress" in rule_names
        assert "life_event_vacant" in rule_names
