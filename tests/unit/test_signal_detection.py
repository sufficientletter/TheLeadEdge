"""Unit tests for MLS signal detection rules.

Tests the SignalDetector class that examines normalized property data
and identifies behavioral signals indicating seller/buyer motivation.

All tests use fake data -- never real PII.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from theleadedge.pipelines.detect import SignalDetector

if TYPE_CHECKING:
    from theleadedge.scoring.config_loader import ScoringConfig


class TestSignalDetector:
    """SignalDetector.detect() tests."""

    @pytest.fixture
    def detector(self, scoring_config: ScoringConfig) -> SignalDetector:
        """Create a SignalDetector with real scoring config."""
        return SignalDetector(scoring_config)

    @pytest.fixture
    def base_data(self) -> dict:
        """Base property data dict with minimal required fields."""
        return {
            "ListingKey": "LK100001",
            "ListingId": "22401000",
            "StandardStatus": "Active",
            "ListPrice": 450000.0,
            "OriginalListPrice": 450000.0,
            "City": "Naples",
            "PostalCode": "34102",
        }

    def test_detect_expired_listing(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Expired listing within 30 days triggers expired_listing signal."""
        data = {
            "ListingKey": "LK100001",
            "ListingId": "22401000",
            "StandardStatus": "Expired",
            "ListPrice": 400000.0,
            "StatusChangeTimestamp": now - timedelta(days=10),
            "City": "Naples",
            "PostalCode": "34102",
        }
        signals = detector.detect(data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "expired_listing" in signal_types

    def test_detect_price_reduction(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """ListPrice < OriginalListPrice triggers price_reduction signal."""
        base_data["ListPrice"] = 420000.0
        base_data["OriginalListPrice"] = 450000.0
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "price_reduction" in signal_types

    def test_detect_price_reduction_severe(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """Price drop >= 15% triggers price_reduction_severe signal."""
        base_data["ListPrice"] = 340000.0
        base_data["OriginalListPrice"] = 450000.0
        # Drop is (450000 - 340000) / 450000 = 24.4%
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "price_reduction_severe" in signal_types

    def test_detect_high_dom(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """DaysOnMarket >= 90 triggers high_dom signal."""
        base_data["DaysOnMarket"] = 120
        base_data["CumulativeDaysOnMarket"] = 120
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "high_dom" in signal_types

    def test_detect_withdrawn_relisted(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """CDOM > DOM indicates withdrawn/relisted behavior."""
        base_data["DaysOnMarket"] = 30
        base_data["CumulativeDaysOnMarket"] = 90
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "withdrawn_relisted" in signal_types

    def test_detect_foreclosure_flag(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """ForeclosedREOYN=True triggers foreclosure_flag signal."""
        base_data["ForeclosedREOYN"] = True
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "foreclosure_flag" in signal_types

    def test_detect_short_sale_flag(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """PotentialShortSaleYN=True triggers short_sale_flag signal."""
        base_data["PotentialShortSaleYN"] = True
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "short_sale_flag" in signal_types

    def test_detect_back_on_market(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Active listing with PendingTimestamp before StatusChangeTimestamp."""
        data = {
            "ListingKey": "LK100001",
            "ListingId": "22401000",
            "StandardStatus": "Active",
            "ListPrice": 400000.0,
            "PendingTimestamp": now - timedelta(days=20),
            "StatusChangeTimestamp": now - timedelta(days=5),
            "City": "Naples",
            "PostalCode": "34102",
        }
        signals = detector.detect(data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "back_on_market" in signal_types

    def test_detect_no_signals_for_normal_listing(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """A normal active listing with no distress indicators produces no signals."""
        data = {
            "ListingKey": "LK100001",
            "ListingId": "22401000",
            "StandardStatus": "Active",
            "ListPrice": 450000.0,
            "OriginalListPrice": 450000.0,
            "DaysOnMarket": 15,
            "CumulativeDaysOnMarket": 15,
            "City": "Naples",
            "PostalCode": "34102",
        }
        signals = detector.detect(data, lead_id=1, property_id=1, now=now)
        assert len(signals) == 0

    def test_detect_multiple_signals_single_property(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """A distressed property can trigger multiple signals simultaneously."""
        data = {
            "ListingKey": "LK100001",
            "ListingId": "22401000",
            "StandardStatus": "Expired",
            "ListPrice": 320000.0,
            "OriginalListPrice": 450000.0,
            "PreviousListPrice": 380000.0,
            "DaysOnMarket": 45,
            "CumulativeDaysOnMarket": 150,
            "StatusChangeTimestamp": now - timedelta(days=5),
            "ForeclosedREOYN": True,
            "City": "Naples",
            "PostalCode": "34102",
        }
        signals = detector.detect(data, lead_id=1, property_id=1, now=now)
        signal_types = {s.signal_type for s in signals}

        # Should detect multiple signals from this distressed property
        assert len(signals) >= 4
        assert "expired_listing" in signal_types
        assert "price_reduction" in signal_types
        assert "price_reduction_severe" in signal_types
        assert "foreclosure_flag" in signal_types
