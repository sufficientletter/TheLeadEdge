"""Unit tests for BatchSkipTracing phone enrichment integration.

Tests cover batch submission, result fetching, the full enrichment
pipeline, phone normalization, DNC filtering, tier filtering, and
circuit breaker behavior.

All test data is synthetic -- no real phone numbers or PII.
IMPORTANT: Test phone numbers are fabricated and not real.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import httpx
import pytest

from theleadedge.integrations.skip_trace import (
    BATCH_SIZE,
    BatchSkipTraceClient,
    PhoneEnrichmentPipeline,
)
from theleadedge.storage.database import LeadRow, PropertyRow
from theleadedge.utils.rate_limit import CircuitState

# ---------------------------------------------------------------------------
# Mock HTTP transport
# ---------------------------------------------------------------------------


def _make_mock_transport() -> httpx.MockTransport:
    """Create a mock transport that handles BatchSkipTracing API routes."""

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)

        # POST /batches -- submit batch
        if (
            "/batches" in url
            and request.method == "POST"
            and "/status" not in url
            and "/results" not in url
        ):
            return httpx.Response(
                200, json={"batch_id": "test-batch-123"}
            )

        # GET /batches/<id>/status
        if "/batches/test-batch-123/status" in url:
            return httpx.Response(
                200,
                json={"status": "complete", "progress_pct": 100},
            )

        # GET /batches/<id>/results
        if "/batches/test-batch-123/results" in url:
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "name": "JOHN DOE",
                            "phone1": "2395551234",
                            "phone2": "2395555678",
                            "phone3": "",
                        },
                        {
                            "name": "JANE SMITH",
                            "phone1": "9415559876",
                            "phone2": "",
                            "phone3": "",
                        },
                    ]
                },
            )

        # GET /health
        if "/health" in url:
            return httpx.Response(200, json={"status": "ok"})

        return httpx.Response(404, json={"error": "not found"})

    return httpx.MockTransport(handler)


def _make_failing_transport() -> httpx.MockTransport:
    """Create a mock transport that always fails."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "internal server error"})

    return httpx.MockTransport(handler)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_client() -> BatchSkipTraceClient:
    """Create a BatchSkipTraceClient with mock transport."""
    transport = _make_mock_transport()
    http_client = httpx.AsyncClient(transport=transport)
    return BatchSkipTraceClient(
        api_key="test-key-123",
        base_url="https://api.batchskiptracing.com/v1",
        http_client=http_client,
    )


@pytest.fixture
def failing_client() -> BatchSkipTraceClient:
    """Create a BatchSkipTraceClient that always fails."""
    transport = _make_failing_transport()
    http_client = httpx.AsyncClient(transport=transport)
    return BatchSkipTraceClient(
        api_key="test-key-123",
        base_url="https://api.batchskiptracing.com/v1",
        http_client=http_client,
    )


# ---------------------------------------------------------------------------
# Test: submit batch
# ---------------------------------------------------------------------------


class TestSubmitBatch:
    """Tests for the submit_batch method."""

    @pytest.mark.asyncio
    async def test_submit_batch_returns_batch_id(
        self, mock_client: BatchSkipTraceClient
    ) -> None:
        """Successful batch submission returns a batch ID."""
        records = [
            {
                "name": "John Doe",
                "street_address": "123 Main St",
                "city": "Naples",
                "state": "FL",
                "zip_code": "34102",
            }
        ]

        batch_id = await mock_client.submit_batch(records)
        assert batch_id == "test-batch-123"

    @pytest.mark.asyncio
    async def test_submit_batch_api_failure(
        self, failing_client: BatchSkipTraceClient
    ) -> None:
        """API error raises an exception."""
        records = [
            {
                "name": "John Doe",
                "street_address": "123 Main St",
                "city": "Naples",
                "state": "FL",
                "zip_code": "34102",
            }
        ]

        with pytest.raises(httpx.HTTPStatusError):
            await failing_client.submit_batch(records)


# ---------------------------------------------------------------------------
# Test: get batch results
# ---------------------------------------------------------------------------


class TestGetResults:
    """Tests for the get_batch_results method."""

    @pytest.mark.asyncio
    async def test_get_results_returns_phone_data(
        self, mock_client: BatchSkipTraceClient
    ) -> None:
        """Completed batch returns result records with phone fields."""
        results = await mock_client.get_batch_results("test-batch-123")

        assert len(results) == 2
        assert results[0]["name"] == "JOHN DOE"
        assert results[0]["phone1"] == "2395551234"
        assert results[1]["name"] == "JANE SMITH"

    @pytest.mark.asyncio
    async def test_get_batch_status(
        self, mock_client: BatchSkipTraceClient
    ) -> None:
        """Batch status check returns correct status."""
        status = await mock_client.get_batch_status("test-batch-123")

        assert status["status"] == "complete"
        assert status["progress_pct"] == 100


# ---------------------------------------------------------------------------
# Test: phone normalization through pipeline
# ---------------------------------------------------------------------------


class TestPhoneNormalization:
    """Tests for phone normalization in the enrichment pipeline."""

    @pytest.mark.asyncio
    async def test_raw_phones_normalized_to_e164(
        self, mock_client: BatchSkipTraceClient, session
    ) -> None:
        """Raw 10-digit phones from API are normalized to E.164 format."""
        from theleadedge.utils.phone import normalize_phone

        # The API returns raw 10-digit numbers
        assert normalize_phone("2395551234") == "+12395551234"
        assert normalize_phone("(239) 555-1234") == "+12395551234"
        assert normalize_phone("239-555-1234") == "+12395551234"
        assert normalize_phone("1-239-555-1234") == "+12395551234"

    @pytest.mark.asyncio
    async def test_invalid_phones_return_none(self) -> None:
        """Invalid phone numbers normalize to None."""
        from theleadedge.utils.phone import normalize_phone

        assert normalize_phone("") is None
        assert normalize_phone(None) is None
        assert normalize_phone("123") is None
        assert normalize_phone("abc") is None


# ---------------------------------------------------------------------------
# Test: DNC exclusion
# ---------------------------------------------------------------------------


class TestDNCExclusion:
    """Tests for DNC (Do Not Call) list filtering."""

    @pytest.mark.asyncio
    async def test_dnc_numbers_filtered(
        self, mock_client: BatchSkipTraceClient, session
    ) -> None:
        """Phone numbers on the DNC list are excluded from updates."""
        dnc_set = {"+12395551234"}  # Synthetic DNC number

        pipeline = PhoneEnrichmentPipeline(
            session=session,
            client=mock_client,
            dnc_numbers=dnc_set,
        )

        # Verify scrub method
        assert pipeline._scrub_dnc("+12395551234") is True
        assert pipeline._scrub_dnc("+19415559876") is False

    @pytest.mark.asyncio
    async def test_empty_dnc_allows_all(
        self, mock_client: BatchSkipTraceClient, session
    ) -> None:
        """Empty DNC set allows all phone numbers through."""
        pipeline = PhoneEnrichmentPipeline(
            session=session,
            client=mock_client,
            dnc_numbers=set(),
        )

        assert pipeline._scrub_dnc("+12395551234") is False
        assert pipeline._scrub_dnc("+19415559876") is False


# ---------------------------------------------------------------------------
# Test: tier filter
# ---------------------------------------------------------------------------


class TestTierFilter:
    """Tests for tier-based lead filtering."""

    @pytest.mark.asyncio
    async def test_only_specified_tiers_queried(
        self, mock_client: BatchSkipTraceClient, session
    ) -> None:
        """Only leads in the specified tiers are queried for enrichment."""
        # Create test properties and leads in different tiers
        prop_s = PropertyRow(
            address="100 S Tier St",
            city="Naples",
            state="FL",
            zip_code="34102",
            owner_name="S TIER OWNER",
        )
        prop_a = PropertyRow(
            address="200 A Tier St",
            city="Naples",
            state="FL",
            zip_code="34102",
            owner_name="A TIER OWNER",
        )
        prop_c = PropertyRow(
            address="300 C Tier St",
            city="Naples",
            state="FL",
            zip_code="34102",
            owner_name="C TIER OWNER",
        )
        session.add_all([prop_s, prop_a, prop_c])
        await session.flush()

        lead_s = LeadRow(
            property_id=prop_s.id,
            current_score=90.0,
            tier="S",
            is_active=True,
        )
        lead_a = LeadRow(
            property_id=prop_a.id,
            current_score=70.0,
            tier="A",
            is_active=True,
        )
        lead_c = LeadRow(
            property_id=prop_c.id,
            current_score=25.0,
            tier="C",
            is_active=True,
        )
        session.add_all([lead_s, lead_a, lead_c])
        await session.flush()

        pipeline = PhoneEnrichmentPipeline(
            session=session,
            client=mock_client,
        )

        # Query only S tier
        leads = await pipeline._query_leads_without_phone(["S"])
        prop_ids = {prop.id for _, prop in leads}
        assert prop_s.id in prop_ids
        assert prop_a.id not in prop_ids
        assert prop_c.id not in prop_ids

        # Query S and A tiers
        leads_sa = await pipeline._query_leads_without_phone(["S", "A"])
        prop_ids_sa = {prop.id for _, prop in leads_sa}
        assert prop_s.id in prop_ids_sa
        assert prop_a.id in prop_ids_sa
        assert prop_c.id not in prop_ids_sa

    @pytest.mark.asyncio
    async def test_leads_with_phone_excluded(
        self, mock_client: BatchSkipTraceClient, session
    ) -> None:
        """Leads whose property already has a phone number are excluded."""
        prop_with_phone = PropertyRow(
            address="400 Phone St",
            city="Naples",
            state="FL",
            zip_code="34102",
            owner_name="HAS PHONE OWNER",
            owner_phone="+12395550000",
        )
        session.add(prop_with_phone)
        await session.flush()

        lead_with_phone = LeadRow(
            property_id=prop_with_phone.id,
            current_score=95.0,
            tier="S",
            is_active=True,
        )
        session.add(lead_with_phone)
        await session.flush()

        pipeline = PhoneEnrichmentPipeline(
            session=session,
            client=mock_client,
        )

        leads = await pipeline._query_leads_without_phone(["S"])
        prop_ids = {prop.id for _, prop in leads}
        assert prop_with_phone.id not in prop_ids


# ---------------------------------------------------------------------------
# Test: circuit breaker
# ---------------------------------------------------------------------------


class TestCircuitBreaker:
    """Tests for circuit breaker integration."""

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(
        self, failing_client: BatchSkipTraceClient
    ) -> None:
        """Circuit breaker opens after repeated API failures."""
        records = [
            {
                "name": "Test",
                "street_address": "123 Main St",
                "city": "Naples",
                "state": "FL",
                "zip_code": "34102",
            }
        ]

        # Trigger failures until circuit opens
        # threshold is 3, so 3 failures should open the circuit
        for _ in range(3):
            with pytest.raises(httpx.HTTPStatusError):
                await failing_client.submit_batch(records)

        assert failing_client._breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_circuit_open_blocks_requests(
        self, failing_client: BatchSkipTraceClient
    ) -> None:
        """Open circuit raises RuntimeError without making API call."""
        import time

        # Force circuit open with recent failure time so it stays open
        failing_client._breaker.state = CircuitState.OPEN
        failing_client._breaker.failure_count = 10
        failing_client._breaker.last_failure_time = time.monotonic()

        records = [{"name": "Test", "street_address": "123 Main St",
                     "city": "Naples", "state": "FL", "zip_code": "34102"}]

        with pytest.raises(RuntimeError, match="Circuit breaker open"):
            await failing_client.submit_batch(records)

    @pytest.mark.asyncio
    async def test_circuit_resets_on_success(
        self, mock_client: BatchSkipTraceClient
    ) -> None:
        """Successful call resets the circuit breaker."""
        # Simulate some prior failures
        mock_client._breaker.failure_count = 2
        mock_client._breaker.state = CircuitState.HALF_OPEN

        records = [{"name": "Test", "street_address": "123 Main St",
                     "city": "Naples", "state": "FL", "zip_code": "34102"}]

        batch_id = await mock_client.submit_batch(records)
        assert batch_id == "test-batch-123"
        assert mock_client._breaker.state == CircuitState.CLOSED
        assert mock_client._breaker.failure_count == 0


# ---------------------------------------------------------------------------
# Test: full enrichment pipeline flow
# ---------------------------------------------------------------------------


class TestEnrichTopTierFlow:
    """Tests for the full enrichment pipeline end-to-end."""

    @pytest.mark.asyncio
    async def test_enrich_top_tier_updates_properties(
        self, mock_client: BatchSkipTraceClient, session
    ) -> None:
        """Full pipeline: query leads, submit batch, get results, update."""
        # Create property and lead matching the mock API results
        prop1 = PropertyRow(
            address="123 Main St",
            city="Naples",
            state="FL",
            zip_code="34102",
            owner_name="JOHN DOE",
        )
        prop2 = PropertyRow(
            address="456 Oak Ave",
            city="Naples",
            state="FL",
            zip_code="34102",
            owner_name="JANE SMITH",
        )
        session.add_all([prop1, prop2])
        await session.flush()

        lead1 = LeadRow(
            property_id=prop1.id,
            current_score=90.0,
            tier="S",
            is_active=True,
        )
        lead2 = LeadRow(
            property_id=prop2.id,
            current_score=85.0,
            tier="S",
            is_active=True,
        )
        session.add_all([lead1, lead2])
        await session.flush()

        pipeline = PhoneEnrichmentPipeline(
            session=session,
            client=mock_client,
        )

        now = datetime(2026, 3, 3, 12, 0, 0)
        stats = await pipeline.enrich_top_tier(tiers=["S"], now=now)

        assert stats["leads_queried"] == 2
        assert stats["batches_submitted"] == 1
        assert stats["phones_found"] >= 2
        assert stats["properties_updated"] >= 1

        # Verify property was updated with normalized phone
        await session.refresh(prop1)
        assert prop1.owner_phone is not None
        assert prop1.owner_phone.startswith("+1")

    @pytest.mark.asyncio
    async def test_enrich_no_leads(
        self, mock_client: BatchSkipTraceClient, session
    ) -> None:
        """Pipeline with no matching leads returns zero stats."""
        pipeline = PhoneEnrichmentPipeline(
            session=session,
            client=mock_client,
        )

        now = datetime(2026, 3, 3, 12, 0, 0)
        stats = await pipeline.enrich_top_tier(tiers=["S", "A"], now=now)

        assert stats["leads_queried"] == 0
        assert stats["batches_submitted"] == 0
        assert stats["phones_found"] == 0
        assert stats["properties_updated"] == 0

    @pytest.mark.asyncio
    async def test_enrich_with_dnc_filtering(
        self, mock_client: BatchSkipTraceClient, session
    ) -> None:
        """DNC numbers are counted but not applied to properties."""
        prop = PropertyRow(
            address="789 Palm Dr",
            city="Naples",
            state="FL",
            zip_code="34102",
            owner_name="JOHN DOE",
        )
        session.add(prop)
        await session.flush()

        lead = LeadRow(
            property_id=prop.id,
            current_score=90.0,
            tier="S",
            is_active=True,
        )
        session.add(lead)
        await session.flush()

        # Block the first phone that would be returned
        dnc_set = {"+12395551234", "+12395555678"}

        pipeline = PhoneEnrichmentPipeline(
            session=session,
            client=mock_client,
            dnc_numbers=dnc_set,
        )

        now = datetime(2026, 3, 3, 12, 0, 0)
        stats = await pipeline.enrich_top_tier(tiers=["S"], now=now)

        assert stats["dnc_filtered"] >= 2
        # Both phones blocked, so property should NOT be updated
        await session.refresh(prop)
        assert prop.owner_phone is None


# ---------------------------------------------------------------------------
# Test: health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """Tests for the BatchSkipTraceClient health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_healthy(
        self, mock_client: BatchSkipTraceClient
    ) -> None:
        """Healthy API returns healthy=True."""
        result = await mock_client.health_check()
        assert result["healthy"] is True
        assert result["circuit_state"] == "closed"

    @pytest.mark.asyncio
    async def test_health_check_circuit_open(
        self, mock_client: BatchSkipTraceClient
    ) -> None:
        """Open circuit reports unhealthy without making API call."""
        import time

        mock_client._breaker.state = CircuitState.OPEN
        mock_client._breaker.failure_count = 10
        mock_client._breaker.last_failure_time = time.monotonic()

        result = await mock_client.health_check()
        assert result["healthy"] is False
        assert result["circuit_state"] == "open"


# ---------------------------------------------------------------------------
# Test: batch creation
# ---------------------------------------------------------------------------


class TestBatchCreation:
    """Tests for the _create_batches helper."""

    @pytest.mark.asyncio
    async def test_batches_split_at_batch_size(
        self, mock_client: BatchSkipTraceClient, session
    ) -> None:
        """Leads are split into batches of BATCH_SIZE."""
        pipeline = PhoneEnrichmentPipeline(
            session=session,
            client=mock_client,
        )

        # Create more leads than BATCH_SIZE
        leads_with_props = []
        for i in range(BATCH_SIZE + 10):
            prop = MagicMock(spec=PropertyRow)
            prop.id = i + 1
            prop.owner_name = f"OWNER {i}"
            prop.owner_name_raw = None
            prop.address = f"{i} Test St"
            prop.city = "Naples"
            prop.state = "FL"
            prop.zip_code = "34102"

            lead = MagicMock(spec=LeadRow)
            lead.property_id = prop.id
            leads_with_props.append((lead, prop))

        batches = pipeline._create_batches(leads_with_props)

        assert len(batches) == 2
        assert len(batches[0][0]) == BATCH_SIZE
        assert len(batches[1][0]) == 10
