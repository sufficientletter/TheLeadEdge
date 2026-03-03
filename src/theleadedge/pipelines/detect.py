"""MLS signal detection pipeline for TheLeadEdge.

The ``SignalDetector`` analyzes normalized property data (from CSV import)
and identifies behavioral signals indicating seller/buyer motivation.

Each detection rule examines specific field combinations and, when triggered,
produces a ``SignalCreate`` object ready for persistence.  The scoring
engine later processes these signals through decay and stacking to produce
composite lead scores.

**12 MLS signal detection rules:**

1.  ``expired_listing``         -- Recently expired (within 30 days)
2.  ``expired_listing_stale``   -- Expired 31-90 days ago
3.  ``price_reduction``         -- Single price cut
4.  ``price_reduction_multiple``-- Multiple price cuts (current < previous < original)
5.  ``price_reduction_severe``  -- Price drop >= 15% from original
6.  ``high_dom``                -- DaysOnMarket >= 90 or CDOM >= 120
7.  ``withdrawn_relisted``      -- CDOM > DOM (listing was recycled)
8.  ``back_on_market``          -- Pending fell through, back to Active
9.  ``listing_price_low_set``   -- Range pricing indicates desperation
10. ``foreclosure_flag``        -- REO/foreclosure flag set
11. ``short_sale_flag``         -- Short sale flag set
12. ``absentee_owner``          -- Owner mailing address differs from property

IMPORTANT: Never log PII (addresses, owner names, phone numbers).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import structlog

from theleadedge.models.signal import SignalCreate

if TYPE_CHECKING:
    from theleadedge.scoring.config_loader import ScoringConfig

logger = structlog.get_logger()


class SignalDetector:
    """Detects motivation signals from normalized MLS property data.

    Parameters
    ----------
    config:
        Scoring configuration loaded from ``scoring_weights.yaml``.
        Used to pull base_points and decay_type for each signal type.
    """

    def __init__(self, config: ScoringConfig) -> None:
        self.config = config
        self.log = logger.bind(component="signal_detector")

    def detect(
        self,
        property_data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> list[SignalCreate]:
        """Run all detection rules against a property record.

        Parameters
        ----------
        property_data:
            Normalized property record keyed by internal (RESO) field names.
        lead_id:
            Database ID of the lead to attach signals to.
        property_id:
            Database ID of the property.
        now:
            Reference timestamp for age calculations.

        Returns
        -------
        list[SignalCreate]
            All signals detected for this property.
        """
        signals: list[SignalCreate] = []

        for rule in [
            self._detect_expired_listing,
            self._detect_expired_listing_stale,
            self._detect_price_reduction,
            self._detect_price_reduction_multiple,
            self._detect_price_reduction_severe,
            self._detect_high_dom,
            self._detect_withdrawn_relisted,
            self._detect_back_on_market,
            self._detect_listing_price_low_set,
            self._detect_foreclosure_flag,
            self._detect_short_sale_flag,
            self._detect_absentee_owner,
        ]:
            result = rule(property_data, lead_id, property_id, now)
            if result is not None:
                signals.append(result)

        if signals:
            self.log.info(
                "signals_detected",
                lead_id=lead_id,
                property_id=property_id,
                signal_count=len(signals),
                signal_types=[s.signal_type for s in signals],
            )

        return signals

    def _make_signal(
        self,
        signal_type: str,
        lead_id: int,
        property_id: int,
        description: str,
        event_date: date | None = None,
    ) -> SignalCreate | None:
        """Build a SignalCreate using config values for the signal type.

        Returns None if the signal type is not configured or inactive.
        """
        sc = self.config.get_signal_config(signal_type)
        if sc is None or not sc.is_active:
            return None
        return SignalCreate(
            lead_id=lead_id,
            property_id=property_id,
            signal_type=signal_type,
            signal_category=sc.category,
            description=description,
            source="mls_csv",
            event_date=event_date,
            base_points=sc.base_points,
            decay_type=sc.decay_type,
            half_life_days=sc.half_life_days,
        )

    # ------------------------------------------------------------------
    # Detection rules
    # ------------------------------------------------------------------

    def _detect_expired_listing(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 1: Listing expired within the last 30 days."""
        status = data.get("StandardStatus", "")
        if status != "Expired":
            return None

        status_change = self._get_datetime(data, "StatusChangeTimestamp")
        if status_change is None:
            # No timestamp -- still detect but with lower confidence
            return self._make_signal(
                "expired_listing",
                lead_id,
                property_id,
                "Listing expired (no status change date available)",
            )

        age_days = (now - status_change).days
        if age_days > 30:
            return None

        return self._make_signal(
            "expired_listing",
            lead_id,
            property_id,
            f"Listing expired {age_days} days ago",
            event_date=status_change.date(),
        )

    def _detect_expired_listing_stale(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 2: Listing expired 31-90 days ago."""
        status = data.get("StandardStatus", "")
        if status != "Expired":
            return None

        status_change = self._get_datetime(data, "StatusChangeTimestamp")
        if status_change is None:
            return None

        age_days = (now - status_change).days
        if age_days < 31 or age_days > 90:
            return None

        return self._make_signal(
            "expired_listing_stale",
            lead_id,
            property_id,
            f"Listing expired {age_days} days ago (stale)",
            event_date=status_change.date(),
        )

    def _detect_price_reduction(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 3: Single price reduction (ListPrice < OriginalListPrice)."""
        list_price = data.get("ListPrice")
        original_price = data.get("OriginalListPrice")

        if list_price is None or original_price is None:
            return None
        if list_price >= original_price:
            return None

        reduction_pct = ((original_price - list_price) / original_price) * 100
        event_dt = self._get_date(data, "PriceChangeTimestamp")

        return self._make_signal(
            "price_reduction",
            lead_id,
            property_id,
            f"Price reduced {reduction_pct:.1f}% from original",
            event_date=event_dt,
        )

    def _detect_price_reduction_multiple(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 4: Multiple price reductions (current < previous < original)."""
        list_price = data.get("ListPrice")
        previous_price = data.get("PreviousListPrice")
        original_price = data.get("OriginalListPrice")

        if list_price is None or previous_price is None or original_price is None:
            return None
        if not (list_price < previous_price < original_price):
            return None

        event_dt = self._get_date(data, "PriceChangeTimestamp")

        return self._make_signal(
            "price_reduction_multiple",
            lead_id,
            property_id,
            "Multiple price reductions detected",
            event_date=event_dt,
        )

    def _detect_price_reduction_severe(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 5: Price drop >= 15% from original."""
        list_price = data.get("ListPrice")
        original_price = data.get("OriginalListPrice")

        if list_price is None or original_price is None:
            return None
        if original_price <= 0:
            return None

        reduction_pct = ((original_price - list_price) / original_price) * 100
        if reduction_pct < 15.0:
            return None

        event_dt = self._get_date(data, "PriceChangeTimestamp")

        return self._make_signal(
            "price_reduction_severe",
            lead_id,
            property_id,
            f"Severe price reduction: {reduction_pct:.1f}% from original",
            event_date=event_dt,
        )

    def _detect_high_dom(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 6: DaysOnMarket >= 90 or CumulativeDaysOnMarket >= 120."""
        dom = data.get("DaysOnMarket")
        cdom = data.get("CumulativeDaysOnMarket")

        dom_trigger = dom is not None and dom >= 90
        cdom_trigger = cdom is not None and cdom >= 120

        if not (dom_trigger or cdom_trigger):
            return None

        dom_value = cdom if cdom is not None else dom

        return self._make_signal(
            "high_dom",
            lead_id,
            property_id,
            f"High days on market: {dom_value} days",
        )

    def _detect_withdrawn_relisted(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 7: CumulativeDaysOnMarket > DaysOnMarket (listing recycled)."""
        dom = data.get("DaysOnMarket")
        cdom = data.get("CumulativeDaysOnMarket")

        if dom is None or cdom is None:
            return None
        if cdom <= dom:
            return None

        return self._make_signal(
            "withdrawn_relisted",
            lead_id,
            property_id,
            f"Withdrawn and relisted (DOM={dom}, CDOM={cdom})",
        )

    def _detect_back_on_market(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 8: Status changed from Pending back to Active recently."""
        status = data.get("StandardStatus", "")
        if status != "Active":
            return None

        pending_ts = self._get_datetime(data, "PendingTimestamp")
        status_change_ts = self._get_datetime(data, "StatusChangeTimestamp")

        if pending_ts is None or status_change_ts is None:
            return None

        # Status change must be after pending (went pending then came back)
        if status_change_ts <= pending_ts:
            return None

        # Only detect if the status change was within the last 30 days
        age_days = (now - status_change_ts).days
        if age_days > 30:
            return None

        return self._make_signal(
            "back_on_market",
            lead_id,
            property_id,
            f"Back on market after pending ({age_days} days ago)",
            event_date=status_change_ts.date(),
        )

    def _detect_listing_price_low_set(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 9: ListPriceLow is set (range pricing = desperation)."""
        list_price_low = data.get("ListPriceLow")
        if list_price_low is None or list_price_low <= 0:
            return None

        list_price = data.get("ListPrice")
        if list_price is not None and list_price > 0:
            spread_pct = ((list_price - list_price_low) / list_price) * 100
            desc = f"Range pricing set (spread: {spread_pct:.1f}%)"
        else:
            desc = "Range pricing set (ListPriceLow populated)"

        return self._make_signal(
            "listing_price_low_set",
            lead_id,
            property_id,
            desc,
        )

    def _detect_foreclosure_flag(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 10: ForeclosedREOYN is True."""
        if not data.get("ForeclosedREOYN", False):
            return None

        return self._make_signal(
            "foreclosure_flag",
            lead_id,
            property_id,
            "Foreclosure/REO flag set on listing",
        )

    def _detect_short_sale_flag(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 11: PotentialShortSaleYN is True."""
        if not data.get("PotentialShortSaleYN", False):
            return None

        return self._make_signal(
            "short_sale_flag",
            lead_id,
            property_id,
            "Potential short sale flag set on listing",
        )

    def _detect_absentee_owner(
        self,
        data: dict[str, Any],
        lead_id: int,
        property_id: int,
        now: datetime,
    ) -> SignalCreate | None:
        """Rule 12: Owner mailing address differs from property address.

        This is a basic heuristic -- if owner data is available and the
        mailing address does not match the property address components,
        the owner is likely absentee.
        """
        # Check if explicitly flagged
        if data.get("is_absentee", False):
            return self._make_signal(
                "absentee_owner",
                lead_id,
                property_id,
                "Owner flagged as absentee",
            )

        # Compare mailing city/state to property city/state when available
        owner_mailing = data.get("owner_mailing_address", "")
        property_city = data.get("City", "")

        if not owner_mailing or not property_city:
            return None

        # Simple heuristic: if the property city does not appear in the
        # owner mailing address, consider them absentee
        if property_city.upper() not in owner_mailing.upper():
            return self._make_signal(
                "absentee_owner",
                lead_id,
                property_id,
                "Owner mailing address differs from property location",
            )

        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_datetime(data: dict[str, Any], field: str) -> datetime | None:
        """Extract a datetime value from a property data dict.

        Handles both datetime objects and date objects (converting to midnight).
        """
        value = data.get(field)
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        return None

    @staticmethod
    def _get_date(data: dict[str, Any], field: str) -> date | None:
        """Extract a date value from a property data dict."""
        value = data.get(field)
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return None
