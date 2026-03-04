"""FSBO (For Sale By Owner) listing connector for Craigslist RSS feeds.

Monitors Craigslist real estate RSS feeds for FSBO listings in the
target market area. Extracts price from listing title/description
and geo coordinates from feed entries.

IMPORTANT: Never log PII. FSBO listings are public postings.
"""

from __future__ import annotations

import contextlib
import re
from datetime import datetime
from typing import Any

import feedparser
import structlog

from theleadedge.sources.base import DataSourceConnector

logger = structlog.get_logger()

# Default Craigslist RSS feed URL for Fort Myers / SWFL real estate
DEFAULT_FEED_URL = (
    "https://fortmyers.craigslist.org/search/rea"
    "?format=rss&is_paid=all&sale_date=all_dates"
)

# Price regex: matches $123,456 or $1234567 style prices
_PRICE_RE = re.compile(r"\$[\d,]+")

# Address regex: digits + street name pattern
_ADDRESS_RE = re.compile(
    r"\b(\d{1,6}\s+"
    r"(?:N|S|E|W|NE|NW|SE|SW|NORTH|SOUTH|EAST|WEST)?\s*"
    r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*"
    r"(?:\s+(?:St|Ave|Blvd|Dr|Ln|Ct|Rd|Way|Pl|Cir|Ter|Trl|Pkwy|Hwy))"
    r"\.?)\b",
    re.IGNORECASE,
)


class CraigslistFSBOConnector(DataSourceConnector):
    """RSS connector for Craigslist FSBO real estate listings.

    Fetches the Craigslist real estate RSS feed for the Fort Myers / SWFL
    area, parses entries, and extracts listing data including price,
    geo coordinates, and any address information.

    Parameters
    ----------
    feed_url:
        Craigslist RSS feed URL. Defaults to the Fort Myers SWFL area.
    http_client:
        Optional httpx.AsyncClient for dependency injection in tests.
    """

    source_name = "craigslist_fsbo"

    def __init__(
        self,
        feed_url: str = DEFAULT_FEED_URL,
        http_client: Any | None = None,
    ) -> None:
        super().__init__(name=self.source_name)
        self.feed_url = feed_url
        self._http_client = http_client
        self.log = logger.bind(source=self.source_name)

    async def authenticate(self) -> None:
        """No authentication needed -- Craigslist RSS is public."""
        self.log.info("authenticate_ok", feed_url=self.feed_url)

    async def fetch(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Download the Craigslist RSS feed as raw XML.

        Parameters
        ----------
        since:
            Not used for RSS feeds (feeds are always current).
        **filters:
            Not used.

        Returns
        -------
        list[dict]
            Single-element list with ``{"xml": str}``.
        """
        import httpx

        client = self._http_client
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=30.0)
            should_close = True

        try:
            response = await client.get(self.feed_url)
            response.raise_for_status()
            self.log.info("feed_fetched", feed_url=self.feed_url)
            return [{"xml": response.text}]
        except Exception as exc:
            self.log.error(
                "feed_fetch_failed",
                feed_url=self.feed_url,
                error=str(exc),
            )
            return []
        finally:
            if should_close:
                await client.aclose()

    def transform(
        self, raw_records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Parse Craigslist RSS and extract FSBO listing data.

        For each entry, extracts:
        - Title and link
        - Price from title/description via regex
        - Geo coordinates from feed entry (Craigslist provides these)
        - Address from content (if available)
        - Published date

        Parameters
        ----------
        raw_records:
            List from ``fetch()`` containing ``{"xml": str}``.

        Returns
        -------
        list[dict]
            Dicts suitable for FSBOListingRow construction.
        """
        results: list[dict[str, Any]] = []

        for entry in raw_records:
            xml_text = entry.get("xml", "")
            if not xml_text:
                continue

            parsed = feedparser.parse(xml_text)

            for item in parsed.entries:
                listing = self._entry_to_fsbo(item)
                if listing is not None:
                    results.append(listing)

        self.log.info(
            "transform_complete",
            feeds_parsed=len(raw_records),
            listings_produced=len(results),
        )
        return results

    def _entry_to_fsbo(self, entry: Any) -> dict[str, Any] | None:
        """Convert a feedparser entry to an FSBOListingRow-compatible dict.

        Parameters
        ----------
        entry:
            A feedparser entry object from the Craigslist feed.

        Returns
        -------
        dict or None
            FSBO listing dict, or None if the entry is empty.
        """
        title = getattr(entry, "title", "") or ""
        link = getattr(entry, "link", "") or ""

        if not title and not link:
            return None

        # Extract content/summary text
        content_text = ""
        if hasattr(entry, "summary"):
            content_text = entry.summary or ""
        elif hasattr(entry, "description"):
            content_text = entry.description or ""

        # Parse price from title first, then content
        full_text = f"{title} {content_text}"
        asking_price = _extract_price(full_text)

        # Parse geo coordinates (Craigslist includes these)
        latitude: float | None = None
        longitude: float | None = None

        # feedparser puts geo data in geo_lat / geo_long
        if hasattr(entry, "geo_lat") and entry.geo_lat:
            with contextlib.suppress(ValueError, TypeError):
                latitude = float(entry.geo_lat)
        if hasattr(entry, "geo_long") and entry.geo_long:
            with contextlib.suppress(ValueError, TypeError):
                longitude = float(entry.geo_long)

        # Also check georss_point (format: "lat long")
        if latitude is None and hasattr(entry, "georss_point"):
            point = getattr(entry, "georss_point", "")
            if point:
                parts = point.strip().split()
                if len(parts) == 2:
                    try:
                        latitude = float(parts[0])
                        longitude = float(parts[1])
                    except (ValueError, TypeError):
                        pass

        # Attempt address extraction from content
        addresses = _ADDRESS_RE.findall(full_text)
        street_address = addresses[0].strip() if addresses else None

        # Parse published date
        posted_at: datetime | None = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            with contextlib.suppress(TypeError, ValueError):
                posted_at = datetime(*entry.published_parsed[:6])

        return {
            "source": self.source_name,
            "source_url": link or None,
            "title": title[:300] if title else None,
            "street_address": street_address,
            "asking_price": asking_price,
            "latitude": latitude,
            "longitude": longitude,
            "posted_at": posted_at,
        }

    async def health_check(self) -> bool:
        """Check connectivity by fetching and parsing the RSS feed.

        Returns
        -------
        bool
            True if the feed can be fetched and parsed successfully.
        """
        import httpx

        client = self._http_client
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=15.0)
            should_close = True

        try:
            response = await client.get(self.feed_url)
            parsed = feedparser.parse(response.text)
            healthy = parsed.bozo == 0 or len(parsed.entries) > 0
            self.log.info(
                "health_check",
                status="healthy" if healthy else "unhealthy",
                entries=len(parsed.entries),
            )
            return healthy
        except Exception as exc:
            self.log.error("health_check_failed", error=str(exc))
            return False
        finally:
            if should_close:
                await client.aclose()


def _extract_price(text: str) -> float | None:
    """Extract a price value from text using regex.

    Matches patterns like ``$450,000`` or ``$1234567``. Returns the
    first match as a float, or None if no price is found.

    Parameters
    ----------
    text:
        Text to search for price patterns.

    Returns
    -------
    float or None
        Extracted price as a float, or None.
    """
    match = _PRICE_RE.search(text)
    if not match:
        return None
    price_str = match.group(0).replace("$", "").replace(",", "")
    try:
        return float(price_str)
    except (ValueError, TypeError):
        return None
