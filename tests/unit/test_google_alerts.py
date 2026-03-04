"""Unit tests for the Google Alerts connector.

Tests cover Atom/RSS feed parsing, empty feed handling, address
extraction from content, and health checks.

All test data is synthetic -- no real alerts or PII.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from theleadedge.sources.market_data import GoogleAlertsConnector

# ---------------------------------------------------------------------------
# Sample feed data
# ---------------------------------------------------------------------------

SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Google Alert - foreclosure southwest florida</title>
  <entry>
    <title>New foreclosure filings surge in Lee County</title>
    <link href="https://example.com/article/1" rel="alternate"/>
    <published>2024-01-15T10:00:00Z</published>
    <content type="html">
      Foreclosure filings at 123 Palm Ave in Fort Myers have increased.
      Property at 456 Oak Dr also affected. Lee County sees record numbers.
    </content>
  </entry>
  <entry>
    <title>Cape Coral real estate market update</title>
    <link href="https://example.com/article/2" rel="alternate"/>
    <published>2024-01-16T08:30:00Z</published>
    <content type="html">
      Market data shows prices stabilizing in Cape Coral area.
      No specific property addresses mentioned in this report.
    </content>
  </entry>
</feed>"""

SAMPLE_ATOM_EMPTY = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Google Alert - empty alert</title>
</feed>"""

SAMPLE_RSS_WITH_ADDRESS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Google Alert - property auction lee county</title>
    <item>
      <title>Property auction at 789 Sunset Blvd in Naples</title>
      <link>https://example.com/auction/1</link>
      <description>
        Auction scheduled for property located at 789 Sunset Blvd.
        Starting bid at a reduced price.
      </description>
      <pubDate>Wed, 17 Jan 2024 14:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def connector() -> GoogleAlertsConnector:
    """Create a GoogleAlertsConnector with test feed URLs."""
    return GoogleAlertsConnector(
        feed_urls=[
            "https://www.google.com/alerts/feeds/test1",
            "https://www.google.com/alerts/feeds/test2",
        ],
    )


# ---------------------------------------------------------------------------
# Test: transform parses Atom feed
# ---------------------------------------------------------------------------


class TestTransform:
    """Tests for the transform method."""

    def test_transform_parses_atom_feed(
        self, connector: GoogleAlertsConnector
    ) -> None:
        """Atom XML feed entries are parsed into SourceRecord-compatible dicts."""
        raw = [{"xml": SAMPLE_ATOM, "url": "https://example.com/feed1"}]
        results = connector.transform(raw)

        assert len(results) == 2

        first = results[0]
        assert first["source_name"] == "google_alerts"
        assert first["record_type"] == "google_alert"
        assert first["raw_data"]["title"] == (
            "New foreclosure filings surge in Lee County"
        )
        assert first["raw_data"]["link"] == "https://example.com/article/1"
        assert first["event_date"] is not None
        # Source record ID should be a stable hash
        assert len(first["source_record_id"]) == 16

    def test_transform_empty_feed(
        self, connector: GoogleAlertsConnector
    ) -> None:
        """Empty Atom feed produces no results."""
        raw = [{"xml": SAMPLE_ATOM_EMPTY, "url": "https://example.com/feed1"}]
        results = connector.transform(raw)
        assert len(results) == 0

    def test_transform_extracts_addresses(
        self, connector: GoogleAlertsConnector
    ) -> None:
        """Street addresses in content are extracted via regex."""
        raw = [{"xml": SAMPLE_RSS_WITH_ADDRESS, "url": "https://example.com/feed2"}]
        results = connector.transform(raw)

        assert len(results) == 1
        rec = results[0]
        # Address "789 Sunset Blvd" should be extracted
        assert rec["street_address"] is not None
        assert "789" in rec["street_address"]
        assert "Sunset" in rec["street_address"]

    def test_transform_no_address_in_content(
        self, connector: GoogleAlertsConnector
    ) -> None:
        """Entries without recognizable addresses produce street_address=None."""
        # The second entry in SAMPLE_ATOM has no specific address
        raw = [{"xml": SAMPLE_ATOM, "url": "https://example.com/feed1"}]
        results = connector.transform(raw)

        # Second entry should have no address
        second = results[1]
        assert second["street_address"] is None

    def test_transform_multiple_feeds(
        self, connector: GoogleAlertsConnector
    ) -> None:
        """Multiple feed XMLs are all parsed and combined."""
        raw = [
            {"xml": SAMPLE_ATOM, "url": "https://example.com/feed1"},
            {"xml": SAMPLE_RSS_WITH_ADDRESS, "url": "https://example.com/feed2"},
        ]
        results = connector.transform(raw)

        # 2 from SAMPLE_ATOM + 1 from SAMPLE_RSS_WITH_ADDRESS
        assert len(results) == 3


# ---------------------------------------------------------------------------
# Test: health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """Tests for the health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self) -> None:
        """Successful feed fetch and parse returns True."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_ATOM
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()

        connector = GoogleAlertsConnector(
            feed_urls=["https://www.google.com/alerts/feeds/test"],
            http_client=mock_client,
        )
        result = await connector.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_no_feeds(self) -> None:
        """Health check with no feed URLs returns False."""
        connector = GoogleAlertsConnector(feed_urls=[])
        result = await connector.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_network_error(self) -> None:
        """Network error during health check returns False."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=ConnectionError("refused"))
        mock_client.aclose = AsyncMock()

        connector = GoogleAlertsConnector(
            feed_urls=["https://www.google.com/alerts/feeds/test"],
            http_client=mock_client,
        )
        result = await connector.health_check()
        assert result is False
