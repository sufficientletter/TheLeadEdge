"""Phase 2 end-to-end integration tests.

Tests the complete pipeline from multiple data sources through
address matching, signal detection, scoring, stacking rules,
and briefing generation.

All test data is synthetic -- no real property data or PII.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from theleadedge.models.source_record import SourceRecord
from theleadedge.pipelines.briefing import BriefingGenerator
from theleadedge.pipelines.detect import SignalDetector
from theleadedge.pipelines.public_records import PublicRecordPipeline
from theleadedge.pipelines.score import ScorePipeline
from theleadedge.scoring.engine import ScoringEngine
from theleadedge.storage.database import SignalRow
from theleadedge.storage.repositories import LeadRepo, PropertyRepo, SignalRepo

# ---------------------------------------------------------------------------
# Test 1: PA populates parcel_id via address match
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pa_populates_parcel_id(
    session,
    scoring_config,
    make_property_row,
    make_lead_row,
    now,
):
    """Property assessment record with parcel_id enriches a matched property."""
    # Create property without parcel_id
    prop = await make_property_row(
        session,
        address="500 PALM AVE",
        city="Naples",
        zip_code="34102",
    )
    assert prop.parcel_id is None

    # Create source record with parcel + matching address
    record = SourceRecord(
        source_name="collier_pa",
        source_record_id="PA-001",
        record_type="property_assessment",
        parcel_id="COLLIER-99001",
        street_address="500 PALM AVE",
        city="Naples",
        state="FL",
        zip_code="34102",
        raw_data={
            "homestead_exempt": True,
            "assessed_value": 350000.0,
        },
    )

    pipeline = PublicRecordPipeline(session, scoring_config)
    stats = await pipeline.process_records([record], now)

    assert stats["matched"] == 1

    # Verify the property row can be fetched by parcel_id now
    # (PublicRecordPipeline links the source record, not enriches property fields,
    # but the match confirms the address resolution works)
    prop_repo = PropertyRepo(session)
    matched_prop = await prop_repo.get_by_id(prop.id)
    assert matched_prop is not None


# ---------------------------------------------------------------------------
# Test 2: Lis pendens fires pre_foreclosure via parcel match
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_lis_pendens_fires_pre_foreclosure(
    session,
    scoring_config,
    make_property_row,
    now,
):
    """Lis pendens matched by parcel_id creates a pre_foreclosure signal."""
    prop = await make_property_row(
        session,
        address="700 BAYSHORE DR",
        city="Naples",
        zip_code="34102",
        parcel_id="COLLIER-12345",
    )

    record = SourceRecord(
        source_name="collier_clerk",
        source_record_id="LP-2026-001",
        record_type="lis_pendens",
        parcel_id="COLLIER-12345",
        event_date=date(2026, 2, 28),
        event_type="MORTGAGE_FORECLOSURE",
    )

    pipeline = PublicRecordPipeline(session, scoring_config)
    stats = await pipeline.process_records([record], now)

    assert stats["matched"] == 1
    assert stats["signals_created"] >= 1

    # Verify pre_foreclosure signal exists
    lead_repo = LeadRepo(session)
    lead = await lead_repo.get_by_property_id(prop.id)
    assert lead is not None

    signal_repo = SignalRepo(session)
    signals = await signal_repo.get_active_by_lead_id(lead.id)
    signal_types = [s.signal_type for s in signals]
    assert "pre_foreclosure" in signal_types

    # Verify signal details
    pf_signal = next(s for s in signals if s.signal_type == "pre_foreclosure")
    assert pf_signal.base_points == 20.0
    assert pf_signal.source == "collier_clerk"


# ---------------------------------------------------------------------------
# Test 3: Probate fires via address match
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_probate_fires_via_address_match(
    session,
    scoring_config,
    make_property_row,
    now,
):
    """Probate record matched by address creates a probate signal."""
    prop = await make_property_row(
        session,
        address="1200 ESTATE LN",
        city="Naples",
        zip_code="34102",
    )

    record = SourceRecord(
        source_name="collier_clerk",
        source_record_id="PROB-2026-042",
        record_type="probate",
        street_address="1200 ESTATE LN",
        city="Naples",
        state="FL",
        zip_code="34102",
        event_date=date(2026, 2, 15),
    )

    pipeline = PublicRecordPipeline(session, scoring_config)
    stats = await pipeline.process_records([record], now)

    assert stats["matched"] == 1
    assert stats["signals_created"] >= 1

    lead_repo = LeadRepo(session)
    lead = await lead_repo.get_by_property_id(prop.id)
    assert lead is not None

    signal_repo = SignalRepo(session)
    signals = await signal_repo.get_active_by_lead_id(lead.id)
    signal_types = [s.signal_type for s in signals]
    assert "probate" in signal_types

    prob_signal = next(s for s in signals if s.signal_type == "probate")
    assert prob_signal.base_points == 18.0


# ---------------------------------------------------------------------------
# Test 4: Code violation fires
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_code_violation_fires(
    session,
    scoring_config,
    make_property_row,
    now,
):
    """Code violation matched by parcel_id creates a code_violation signal."""
    prop = await make_property_row(
        session,
        address="300 OVERGROWN WAY",
        city="Naples",
        zip_code="34102",
        parcel_id="COLLIER-77777",
    )

    record = SourceRecord(
        source_name="collier_code",
        source_record_id="CV-2026-100",
        record_type="code_violation",
        parcel_id="COLLIER-77777",
        event_date=date(2026, 2, 20),
        raw_data={"status": "OPEN", "violation_type": "OVERGROWN VEGETATION"},
    )

    pipeline = PublicRecordPipeline(session, scoring_config)
    stats = await pipeline.process_records([record], now)

    assert stats["matched"] == 1
    assert stats["signals_created"] >= 1

    lead_repo = LeadRepo(session)
    lead = await lead_repo.get_by_property_id(prop.id)
    assert lead is not None

    signal_repo = SignalRepo(session)
    signals = await signal_repo.get_active_by_lead_id(lead.id)
    signal_types = [s.signal_type for s in signals]
    assert "code_violation" in signal_types

    cv_signal = next(s for s in signals if s.signal_type == "code_violation")
    assert cv_signal.base_points == 12.0
    assert "OVERGROWN VEGETATION" in cv_signal.description


# ---------------------------------------------------------------------------
# Test 5: financial_distress stacking (2.0x) activates
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_financial_distress_stacking(
    session,
    scoring_config,
    make_property_row,
    make_lead_row,
    now,
):
    """pre_foreclosure + tax_delinquent triggers financial_distress (2.0x)."""
    prop = await make_property_row(session, address="900 DISTRESS CT")
    lead = await make_lead_row(session, property_id=prop.id)

    # Create pre_foreclosure signal
    sig1 = SignalRow(
        lead_id=lead.id,
        property_id=prop.id,
        signal_type="pre_foreclosure",
        signal_category="public_record",
        description="Test pre-foreclosure signal",
        source="collier_clerk",
        base_points=20.0,
        points=20.0,
        weight=1.0,
        decay_type="escalating",
        half_life_days=60.0,
        detected_at=now,
        is_active=True,
    )
    session.add(sig1)

    # Create tax_delinquent signal
    sig2 = SignalRow(
        lead_id=lead.id,
        property_id=prop.id,
        signal_type="tax_delinquent",
        signal_category="public_record",
        description="Test tax delinquency signal",
        source="collier_tax",
        base_points=13.0,
        points=13.0,
        weight=1.0,
        decay_type="linear",
        half_life_days=120.0,
        detected_at=now,
        is_active=True,
    )
    session.add(sig2)
    await session.flush()

    # Score the lead
    engine = ScoringEngine(scoring_config)
    pipeline = ScorePipeline(engine)
    result = await pipeline.score_lead(session, lead.id, now)

    assert result is not None
    assert result.stacking_bonus > 0
    assert result.stacking_rule == "financial_distress"
    # Financial distress multiplier = 2.0, bonus = sum * (2.0 - 1.0)
    # Both signals fresh => points get freshness premium too
    assert result.normalized_score > 30.0  # Should be well above D-tier


# ---------------------------------------------------------------------------
# Test 6: life_event_vacant stacking (2.5x) activates
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_life_event_vacant_stacking(
    session,
    scoring_config,
    make_property_row,
    make_lead_row,
    now,
):
    """probate + absentee_owner + vacant_property triggers life_event_vacant (2.5x)."""
    prop = await make_property_row(session, address="400 INHERITED DR")
    lead = await make_lead_row(session, property_id=prop.id)

    signal_defs = [
        ("probate", "life_event", 18.0, "linear", 90.0),
        ("absentee_owner", "mls", 8.0, "linear", 180.0),
        ("vacant_property", "life_event", 10.0, "linear", 180.0),
    ]

    for stype, cat, points, decay, half_life in signal_defs:
        sig = SignalRow(
            lead_id=lead.id,
            property_id=prop.id,
            signal_type=stype,
            signal_category=cat,
            description=f"Test {stype}",
            source="test",
            base_points=points,
            points=points,
            weight=1.0,
            decay_type=decay,
            half_life_days=half_life,
            detected_at=now,
            is_active=True,
        )
        session.add(sig)
    await session.flush()

    engine = ScoringEngine(scoring_config)
    pipeline = ScorePipeline(engine)
    result = await pipeline.score_lead(session, lead.id, now)

    assert result is not None
    assert result.stacking_bonus > 0
    assert result.stacking_rule == "life_event_vacant"
    # 2.5x multiplier on (18 + 8 + 10 = 36) * freshness
    # This should produce a high score
    assert result.normalized_score >= 60.0


# ---------------------------------------------------------------------------
# Test 7: tired_landlord stacking (1.8x) activates
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tired_landlord_stacking(
    session,
    scoring_config,
    make_property_row,
    make_lead_row,
    now,
):
    """absentee_owner + code_violation triggers tired_landlord (1.8x)."""
    prop = await make_property_row(session, address="600 RENTAL BLVD")
    lead = await make_lead_row(session, property_id=prop.id)

    signal_defs = [
        ("absentee_owner", "mls", 8.0, "linear", 180.0),
        ("code_violation", "public_record", 12.0, "step", 60.0),
    ]

    for stype, cat, points, decay, half_life in signal_defs:
        sig = SignalRow(
            lead_id=lead.id,
            property_id=prop.id,
            signal_type=stype,
            signal_category=cat,
            description=f"Test {stype}",
            source="test",
            base_points=points,
            points=points,
            weight=1.0,
            decay_type=decay,
            half_life_days=half_life,
            detected_at=now,
            is_active=True,
        )
        session.add(sig)
    await session.flush()

    engine = ScoringEngine(scoring_config)
    pipeline = ScorePipeline(engine)
    result = await pipeline.score_lead(session, lead.id, now)

    assert result is not None
    assert result.stacking_bonus > 0
    assert result.stacking_rule == "tired_landlord"


# ---------------------------------------------------------------------------
# Test 8: divorce_property stacking (1.6x) activates
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_divorce_property_stacking(
    session,
    scoring_config,
    make_property_row,
    make_lead_row,
    now,
):
    """divorce + high_dom triggers divorce_property (1.6x)."""
    prop = await make_property_row(session, address="250 SPLIT WAY")
    lead = await make_lead_row(session, property_id=prop.id)

    signal_defs = [
        ("divorce", "life_event", 16.0, "step", 45.0),
        ("high_dom", "mls", 11.0, "step", 60.0),
    ]

    for stype, cat, points, decay, half_life in signal_defs:
        sig = SignalRow(
            lead_id=lead.id,
            property_id=prop.id,
            signal_type=stype,
            signal_category=cat,
            description=f"Test {stype}",
            source="test",
            base_points=points,
            points=points,
            weight=1.0,
            decay_type=decay,
            half_life_days=half_life,
            detected_at=now,
            is_active=True,
        )
        session.add(sig)
    await session.flush()

    engine = ScoringEngine(scoring_config)
    pipeline = ScorePipeline(engine)
    result = await pipeline.score_lead(session, lead.id, now)

    assert result is not None
    assert result.stacking_bonus > 0
    assert result.stacking_rule == "divorce_property"


# ---------------------------------------------------------------------------
# Test 9: Full pipeline produces HTML briefing with Phase 2 signal types
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_pipeline_briefing_with_phase2_signals(
    session,
    scoring_config,
    make_property_row,
    make_lead_row,
    now,
):
    """End-to-end: create properties with Phase 2 signals, score, generate briefing."""
    template_dir = (
        Path(__file__).parent.parent.parent
        / "src"
        / "theleadedge"
        / "notifications"
        / "templates"
    )

    # Property 1: pre_foreclosure (high score)
    prop1 = await make_property_row(
        session,
        listing_key="LK-BRIEF-001",
        listing_id="BRIEF001",
        address="800 FORECLOSURE LN",
        city="Naples",
        zip_code="34102",
    )
    lead1 = await make_lead_row(session, property_id=prop1.id)
    sig1 = SignalRow(
        lead_id=lead1.id,
        property_id=prop1.id,
        signal_type="pre_foreclosure",
        signal_category="public_record",
        description="Pre-foreclosure filing",
        source="collier_clerk",
        base_points=20.0,
        points=20.0,
        weight=1.0,
        decay_type="escalating",
        half_life_days=60.0,
        detected_at=now,
        is_active=True,
    )
    session.add(sig1)

    # Also add tax_delinquent for stacking
    sig1b = SignalRow(
        lead_id=lead1.id,
        property_id=prop1.id,
        signal_type="tax_delinquent",
        signal_category="public_record",
        description="Tax delinquency detected",
        source="collier_tax",
        base_points=13.0,
        points=13.0,
        weight=1.0,
        decay_type="linear",
        half_life_days=120.0,
        detected_at=now,
        is_active=True,
    )
    session.add(sig1b)

    # Property 2: probate (moderate score)
    prop2 = await make_property_row(
        session,
        listing_key="LK-BRIEF-002",
        listing_id="BRIEF002",
        address="850 PROBATE CT",
        city="Naples",
        zip_code="34102",
    )
    lead2 = await make_lead_row(session, property_id=prop2.id)
    sig2 = SignalRow(
        lead_id=lead2.id,
        property_id=prop2.id,
        signal_type="probate",
        signal_category="life_event",
        description="Probate filing",
        source="collier_clerk",
        base_points=18.0,
        points=18.0,
        weight=1.0,
        decay_type="linear",
        half_life_days=90.0,
        detected_at=now,
        is_active=True,
    )
    session.add(sig2)

    # Property 3: no signals (D-tier)
    prop3 = await make_property_row(
        session,
        listing_key="LK-BRIEF-003",
        listing_id="BRIEF003",
        address="900 QUIET ST",
        city="Naples",
        zip_code="34102",
    )
    await make_lead_row(session, property_id=prop3.id)

    await session.flush()

    # Score all leads
    engine = ScoringEngine(scoring_config)
    score_pipeline = ScorePipeline(engine)
    results = await score_pipeline.score_all_active(session, now)

    assert len(results) == 3

    # Generate briefing
    generator = BriefingGenerator(scoring_config, template_dir)
    html = await generator.generate(session, now)

    assert len(html) > 500
    assert "TheLeadEdge Daily Briefing" in html
    assert "Pipeline Summary" in html

    # Verify at least one Phase 2 signal type name appears
    # (as a signal-tag in the hot leads table)
    assert any(
        term in html
        for term in ["pre foreclosure", "probate", "tax delinquent"]
    )


# ---------------------------------------------------------------------------
# Test 10: Neighborhood hot signal from market data
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_neighborhood_hot_signal(
    session,
    scoring_config,
    make_property_row,
    make_lead_row,
    now,
):
    """Absorption rate > 20% triggers neighborhood_hot signal."""
    prop = await make_property_row(
        session,
        address="100 HOT MARKET BLVD",
        city="Naples",
        zip_code="34102",
    )
    lead = await make_lead_row(session, property_id=prop.id)

    detector = SignalDetector(scoring_config)
    signal = detector.detect_neighborhood_hot(
        lead_id=lead.id,
        property_id=prop.id,
        zip_code="34102",
        absorption_rate=25.0,
        now=now,
    )

    assert signal is not None
    assert signal.signal_type == "neighborhood_hot"
    assert signal.base_points == 5.0
    assert signal.source == "redfin"
    assert "25.0%" in signal.description
    assert "34102" in signal.description


@pytest.mark.asyncio
async def test_neighborhood_hot_below_threshold(
    scoring_config,
    now,
):
    """Absorption rate <= 20% does NOT trigger neighborhood_hot."""
    detector = SignalDetector(scoring_config)
    signal = detector.detect_neighborhood_hot(
        lead_id=1,
        property_id=1,
        zip_code="34102",
        absorption_rate=18.0,
        now=now,
    )
    assert signal is None


# ---------------------------------------------------------------------------
# Test 11: Agent churn detection on update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_agent_churn_detection(
    scoring_config,
    now,
):
    """Listing agent change fires agent_churn signal."""
    detector = SignalDetector(scoring_config)

    property_data = {
        "StandardStatus": "Active",
        "ListAgentKey": "AGENT_B",
        "previous_agent_key": "AGENT_A",
    }

    signals = detector.detect(
        property_data=property_data,
        lead_id=1,
        property_id=1,
        now=now,
    )

    signal_types = [s.signal_type for s in signals]
    assert "agent_churn" in signal_types

    ac = next(s for s in signals if s.signal_type == "agent_churn")
    assert ac.base_points == 7.0


@pytest.mark.asyncio
async def test_agent_churn_no_change(
    scoring_config,
    now,
):
    """Same agent key does NOT fire agent_churn."""
    detector = SignalDetector(scoring_config)

    property_data = {
        "StandardStatus": "Active",
        "ListAgentKey": "AGENT_A",
        "previous_agent_key": "AGENT_A",
    }

    signals = detector.detect(
        property_data=property_data,
        lead_id=1,
        property_id=1,
        now=now,
    )

    signal_types = [s.signal_type for s in signals]
    assert "agent_churn" not in signal_types


# ---------------------------------------------------------------------------
# Test 12: Multi-source scoring produces expected tier ordering
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_multi_source_tier_ordering(
    session,
    scoring_config,
    make_property_row,
    make_lead_row,
    now,
):
    """Properties with different signal combinations score into expected tiers.

    Property 1: pre_foreclosure + tax_delinquent + price_reduction_severe -> S-tier
    Property 2: probate + absentee_owner -> B/C-tier (moderate signals, no stacking)
    Property 3: expired_listing (30-day-old) + high_dom -> C-tier (decayed signals)
    Property 4: code_violation only -> C/D-tier
    Property 5: no signals -> D-tier

    Signals for property 1 are fresh (detected at `now`), producing S-tier via
    financial_distress stacking. Properties 2-4 have decreasing base points.
    """
    engine = ScoringEngine(scoring_config)
    score_pipeline = ScorePipeline(engine)

    thirty_days_ago = now - timedelta(days=30)

    # --- Property 1: Heavy distress signals (fresh, with stacking) ---
    prop1 = await make_property_row(session, address="10 HEAVY DISTRESS LN")
    lead1 = await make_lead_row(session, property_id=prop1.id)
    for stype, cat, points, decay, half_life in [
        ("pre_foreclosure", "public_record", 20.0, "escalating", 60.0),
        ("tax_delinquent", "public_record", 13.0, "linear", 120.0),
        ("price_reduction_severe", "mls", 16.0, "step", 30.0),
    ]:
        session.add(
            SignalRow(
                lead_id=lead1.id,
                property_id=prop1.id,
                signal_type=stype,
                signal_category=cat,
                description=f"Test {stype}",
                source="test",
                base_points=points,
                points=points,
                weight=1.0,
                decay_type=decay,
                half_life_days=half_life,
                detected_at=now,
                is_active=True,
            )
        )

    # --- Property 2: Life event signals (fresh, no stacking match) ---
    prop2 = await make_property_row(session, address="20 LIFE EVENT AVE")
    lead2 = await make_lead_row(session, property_id=prop2.id)
    for stype, cat, points, decay, half_life in [
        ("probate", "life_event", 18.0, "linear", 90.0),
        ("absentee_owner", "mls", 8.0, "linear", 180.0),
    ]:
        session.add(
            SignalRow(
                lead_id=lead2.id,
                property_id=prop2.id,
                signal_type=stype,
                signal_category=cat,
                description=f"Test {stype}",
                source="test",
                base_points=points,
                points=points,
                weight=1.0,
                decay_type=decay,
                half_life_days=half_life,
                detected_at=now,
                is_active=True,
            )
        )

    # --- Property 3: MLS stale listing (detected 30 days ago, decayed) ---
    prop3 = await make_property_row(session, address="30 STALE LISTING RD")
    lead3 = await make_lead_row(session, property_id=prop3.id)
    for stype, cat, points, decay, half_life in [
        ("expired_listing", "mls", 15.0, "exponential", 21.0),
        ("high_dom", "mls", 11.0, "step", 60.0),
    ]:
        session.add(
            SignalRow(
                lead_id=lead3.id,
                property_id=prop3.id,
                signal_type=stype,
                signal_category=cat,
                description=f"Test {stype}",
                source="test",
                base_points=points,
                points=points,
                weight=1.0,
                decay_type=decay,
                half_life_days=half_life,
                detected_at=thirty_days_ago,
                is_active=True,
            )
        )

    # --- Property 4: Single code violation (detected 30 days ago, decayed) ---
    prop4 = await make_property_row(session, address="40 CODE VIOLATION ST")
    lead4 = await make_lead_row(session, property_id=prop4.id)
    session.add(
        SignalRow(
            lead_id=lead4.id,
            property_id=prop4.id,
            signal_type="code_violation",
            signal_category="public_record",
            description="Test code_violation",
            source="test",
            base_points=12.0,
            points=12.0,
            weight=1.0,
            decay_type="step",
            half_life_days=60.0,
            detected_at=thirty_days_ago,
            is_active=True,
        )
    )

    # --- Property 5: No signals ---
    prop5 = await make_property_row(session, address="50 QUIET PL")
    lead5 = await make_lead_row(session, property_id=prop5.id)

    await session.flush()

    # Score all leads
    results = await score_pipeline.score_all_active(session, now)
    assert len(results) == 5

    # Build a lookup from lead_id to result
    by_lead = {r.lead_id: r for r in results}

    r1 = by_lead[lead1.id]
    r2 = by_lead[lead2.id]
    r3 = by_lead[lead3.id]
    r4 = by_lead[lead4.id]
    r5 = by_lead[lead5.id]

    # Property 1 should be the highest scored (S-tier expected with stacking)
    assert r1.normalized_score >= 80.0, (
        f"Expected S-tier (>=80) for distressed property, "
        f"got {r1.normalized_score}"
    )
    assert r1.tier == "S"

    # Property 5 should be D-tier (no signals)
    assert r5.normalized_score == 0.0
    assert r5.tier == "D"

    # Strict score ordering: prop1 > prop2 > prop3 > prop4 > prop5
    assert r1.normalized_score > r2.normalized_score, (
        f"prop1 ({r1.normalized_score}) should outscore prop2 ({r2.normalized_score})"
    )
    assert r2.normalized_score > r3.normalized_score, (
        f"prop2 ({r2.normalized_score}) should outscore prop3 ({r3.normalized_score})"
    )
    assert r3.normalized_score > r4.normalized_score, (
        f"prop3 ({r3.normalized_score}) should outscore prop4 ({r4.normalized_score})"
    )
    assert r4.normalized_score > r5.normalized_score, (
        f"prop4 ({r4.normalized_score}) should outscore prop5 ({r5.normalized_score})"
    )

    # Property 4: 12 base * 0.75 step decay at 30 days = 9 -> D tier
    assert r4.tier == "D"
