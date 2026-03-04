"""Tests for agent_churn signal detection during MLS import.

The agent_churn signal fires when the listing agent changes on an existing
property. The SignalDetector._detect_agent_churn rule checks for a
'previous_agent_key' field injected by the ingest pipeline.

All tests use synthetic data -- never real PII.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

from theleadedge.pipelines.detect import SignalDetector

if TYPE_CHECKING:
    from theleadedge.scoring.config_loader import ScoringConfig


class TestAgentChurn:
    """Tests for _detect_agent_churn via detect()."""

    @pytest.fixture
    def detector(self, scoring_config: ScoringConfig) -> SignalDetector:
        return SignalDetector(scoring_config)

    @pytest.fixture
    def now(self) -> datetime:
        return datetime(2026, 3, 2, 10, 0, 0)

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
            "DaysOnMarket": 15,
            "CumulativeDaysOnMarket": 15,
        }

    def test_agent_churn_fires(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """Different previous_agent_key and ListAgentKey fires agent_churn."""
        base_data["previous_agent_key"] = "AGENT_OLD_001"
        base_data["ListAgentKey"] = "AGENT_NEW_002"
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "agent_churn" in signal_types

    def test_agent_churn_same_agent(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """Same agent key does NOT fire agent_churn."""
        base_data["previous_agent_key"] = "AGENT_SAME_001"
        base_data["ListAgentKey"] = "AGENT_SAME_001"
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "agent_churn" not in signal_types

    def test_agent_churn_no_previous(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """No previous_agent_key (new listing) does NOT fire agent_churn."""
        base_data["ListAgentKey"] = "AGENT_NEW_002"
        # No previous_agent_key set at all
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "agent_churn" not in signal_types

    def test_agent_churn_empty_current(
        self,
        detector: SignalDetector,
        base_data: dict,
        now: datetime,
    ) -> None:
        """Empty current ListAgentKey does NOT fire agent_churn."""
        base_data["previous_agent_key"] = "AGENT_OLD_001"
        base_data["ListAgentKey"] = ""
        signals = detector.detect(base_data, lead_id=1, property_id=1, now=now)
        signal_types = [s.signal_type for s in signals]
        assert "agent_churn" not in signal_types
