"""Tests for neighborhood_hot signal detection.

The neighborhood_hot signal fires based on absorption rate data from
market snapshots (e.g., Redfin). It is a standalone detection method
on SignalDetector, not part of the SourceRecord routing.

All tests use synthetic data -- never real PII.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

from theleadedge.pipelines.detect import SignalDetector

if TYPE_CHECKING:
    from theleadedge.scoring.config_loader import ScoringConfig


class TestNeighborhoodHot:
    """Tests for SignalDetector.detect_neighborhood_hot()."""

    @pytest.fixture
    def detector(self, scoring_config: ScoringConfig) -> SignalDetector:
        return SignalDetector(scoring_config)

    @pytest.fixture
    def now(self) -> datetime:
        return datetime(2026, 3, 2, 10, 0, 0)

    def test_neighborhood_hot_fires(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Absorption rate > 20% fires neighborhood_hot signal."""
        signal = detector.detect_neighborhood_hot(
            lead_id=1,
            property_id=1,
            zip_code="34102",
            absorption_rate=35.0,
            now=now,
        )
        assert signal is not None
        assert signal.signal_type == "neighborhood_hot"
        assert "35.0%" in signal.description  # type: ignore[operator]
        assert "34102" in signal.description  # type: ignore[operator]
        assert signal.source == "redfin"

    def test_neighborhood_hot_below_threshold(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Absorption rate <= 20% does NOT fire."""
        signal = detector.detect_neighborhood_hot(
            lead_id=1,
            property_id=1,
            zip_code="34102",
            absorption_rate=20.0,
            now=now,
        )
        assert signal is None

    def test_neighborhood_hot_at_boundary(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Absorption rate exactly at 20.0 does NOT fire (needs to exceed)."""
        signal = detector.detect_neighborhood_hot(
            lead_id=1,
            property_id=1,
            zip_code="33904",
            absorption_rate=20.0,
            now=now,
        )
        assert signal is None

    def test_neighborhood_hot_just_above_threshold(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Absorption rate at 20.1% fires."""
        signal = detector.detect_neighborhood_hot(
            lead_id=1,
            property_id=1,
            zip_code="33904",
            absorption_rate=20.1,
            now=now,
        )
        assert signal is not None
        assert signal.signal_type == "neighborhood_hot"
