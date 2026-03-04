"""Tests for Phase 2 signal detection rules (public records + external sources).

Validates the 7 new detection rules added in Phase 2:
- pre_foreclosure (lis_pendens / pre_foreclosure routing)
- tax_delinquent (tax_delinquent / tax_lien routing)
- code_violation (active only)
- probate
- divorce (divorce / domestic_relations routing)
- vacant_property (composite: !homestead + absentee + residential)

Also validates detect_from_source_record() routing, source propagation,
and event_date propagation.

All tests use synthetic data -- never real PII.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

import pytest

from theleadedge.models.source_record import SourceRecord
from theleadedge.pipelines.detect import SignalDetector

if TYPE_CHECKING:
    from theleadedge.scoring.config_loader import ScoringConfig


def _make_source_record(**overrides: object) -> SourceRecord:
    """Build a SourceRecord with sensible defaults and optional overrides."""
    defaults: dict[str, object] = {
        "source_name": "test_source",
        "source_record_id": "TST-001",
        "record_type": "lis_pendens",
        "street_address": "100 TEST ST",
        "city": "Naples",
        "state": "FL",
        "zip_code": "34102",
    }
    defaults.update(overrides)
    return SourceRecord(**defaults)  # type: ignore[arg-type]


class TestDetectFromSourceRecordRouting:
    """Tests for detect_from_source_record() routing and core behavior."""

    @pytest.fixture
    def detector(self, scoring_config: ScoringConfig) -> SignalDetector:
        return SignalDetector(scoring_config)

    @pytest.fixture
    def now(self) -> datetime:
        return datetime(2026, 3, 2, 10, 0, 0)

    def test_lis_pendens_fires_pre_foreclosure(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """record_type='lis_pendens' routes to pre_foreclosure signal."""
        record = _make_source_record(record_type="lis_pendens")
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].signal_type == "pre_foreclosure"

    def test_pre_foreclosure_direct(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """record_type='pre_foreclosure' routes to pre_foreclosure signal."""
        record = _make_source_record(record_type="pre_foreclosure")
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].signal_type == "pre_foreclosure"

    def test_tax_delinquent_fires(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """record_type='tax_delinquent' produces tax_delinquent signal."""
        record = _make_source_record(record_type="tax_delinquent")
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].signal_type == "tax_delinquent"
        assert signals[0].description == "Tax delinquency detected"

    def test_tax_delinquent_with_amount(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """raw_data containing amount_owed is included in the description."""
        record = _make_source_record(
            record_type="tax_delinquent",
            raw_data={"amount_owed": 12500.0},
        )
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert "$12,500" in signals[0].description  # type: ignore[operator]

    def test_code_violation_fires_active(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """record_type='code_violation' with status='OPEN' fires signal."""
        record = _make_source_record(
            record_type="code_violation",
            raw_data={"status": "OPEN", "violation_type": "overgrown_lot"},
        )
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].signal_type == "code_violation"
        assert "overgrown_lot" in signals[0].description  # type: ignore[operator]

    def test_code_violation_ignores_closed(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """code_violation with status='CLOSED' does NOT fire."""
        record = _make_source_record(
            record_type="code_violation",
            raw_data={"status": "CLOSED", "violation_type": "fence"},
        )
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 0

    def test_probate_fires(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """record_type='probate' fires probate signal."""
        record = _make_source_record(record_type="probate")
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].signal_type == "probate"
        assert signals[0].description == "Probate filing associated with property"

    def test_divorce_fires(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """record_type='divorce' fires divorce signal."""
        record = _make_source_record(record_type="divorce")
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].signal_type == "divorce"

    def test_domestic_relations_routes_to_divorce(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """record_type='domestic_relations' routes to divorce signal."""
        record = _make_source_record(record_type="domestic_relations")
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].signal_type == "divorce"

    def test_vacant_property_fires(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """PA + !homestead + absentee + residential fires vacant."""
        record = _make_source_record(
            record_type="property_assessment",
            raw_data={
                "homestead_exempt": False,
                "is_absentee": True,
                "property_use_code": "0100",
            },
        )
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].signal_type == "vacant_property"
        assert "non-homestead absentee" in signals[0].description  # type: ignore[operator]

    def test_vacant_property_skips_homestead(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Homestead-exempt property does NOT fire vacant_property."""
        record = _make_source_record(
            record_type="property_assessment",
            raw_data={
                "homestead_exempt": True,
                "is_absentee": True,
                "property_use_code": "0100",
            },
        )
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 0

    def test_vacant_property_skips_non_absentee(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Non-absentee property does NOT fire vacant_property."""
        record = _make_source_record(
            record_type="property_assessment",
            raw_data={
                "homestead_exempt": False,
                "is_absentee": False,
                "property_use_code": "0100",
            },
        )
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 0

    def test_unknown_record_type_no_signal(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Unrecognized record_type produces no signals."""
        record = _make_source_record(record_type="unknown_type")
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 0

    def test_source_is_set_correctly(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """Signal source matches the record's source_name."""
        record = _make_source_record(
            record_type="probate",
            source_name="lee_clerk",
        )
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].source == "lee_clerk"

    def test_event_date_propagated(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """event_date from the source record is propagated to the signal."""
        event = date(2026, 2, 15)
        record = _make_source_record(
            record_type="probate",
            event_date=event,
        )
        signals = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert len(signals) == 1
        assert signals[0].event_date == event

    def test_detect_from_source_record_returns_list(
        self,
        detector: SignalDetector,
        now: datetime,
    ) -> None:
        """detect_from_source_record always returns a list."""
        record = _make_source_record(record_type="probate")
        result = detector.detect_from_source_record(
            record, lead_id=1, property_id=1, now=now
        )
        assert isinstance(result, list)

        # Also verify for unknown type
        record2 = _make_source_record(record_type="unknown")
        result2 = detector.detect_from_source_record(
            record2, lead_id=1, property_id=1, now=now
        )
        assert isinstance(result2, list)
        assert len(result2) == 0
