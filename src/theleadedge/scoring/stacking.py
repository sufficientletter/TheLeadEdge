"""Signal stacking bonus calculator.

When multiple motivation signals co-occur on the same lead, the combined
effect is greater than the sum of parts.  A seller with an expired listing
*and* multiple price reductions *and* high DOM is far more motivated than
any single signal alone.

Stacking rules are defined in ``scoring_weights.yaml`` and loaded as
``StackingRule`` objects by ``config_loader``.  Each rule specifies:

* ``required_signals`` -- the set of signal types that must all be active
* ``multiplier`` -- applied to the sum of those signals' decayed points

**Algorithm**: Best-single-rule.  All matching rules are evaluated and only
the one producing the highest bonus is applied.  This avoids runaway score
inflation when many rules overlap.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from theleadedge.scoring.config_loader import StackingRule


def calculate_stacking_bonus(
    active_signal_types: set[str],
    signal_points_by_type: dict[str, float],
    stacking_rules: list[StackingRule],
) -> tuple[float, str | None]:
    """Check all stacking rules and return the best bonus.

    Only the single highest-bonus matching rule is applied.

    Parameters
    ----------
    active_signal_types:
        Set of signal type names currently active on the lead.
    signal_points_by_type:
        Mapping of signal type name to its current (decayed) point value.
    stacking_rules:
        All stacking rules from the scoring configuration.

    Returns
    -------
    tuple[float, str | None]
        ``(bonus_points, rule_name)`` where ``rule_name`` is ``None``
        if no rule matched.
    """
    best_bonus = 0.0
    best_rule_name: str | None = None

    for rule in stacking_rules:
        if rule.required_signals.issubset(active_signal_types):
            stacked_points = sum(
                signal_points_by_type.get(st, 0.0) for st in rule.required_signals
            )
            bonus = stacked_points * (rule.multiplier - 1.0)
            if bonus > best_bonus:
                best_bonus = bonus
                best_rule_name = rule.name

    return best_bonus, best_rule_name
