"""Market data connectors for Redfin and Google Alerts.

RedfinMarketConnector:
  Downloads Redfin's weekly market data (gzipped TSV) from their public
  S3-hosted data center. Filters to the 52 SWFLA ZIP codes during parse.
  Calculates absorption_rate from inventory and homes_sold.

GoogleAlertsConnector:
  Parses RSS/Atom feeds from Google Alerts configured for real estate
  keywords. Extracts potential address mentions from alert content.

IMPORTANT: Never log PII. Market data is aggregated (no individual info).
"""

from __future__ import annotations

import gzip
import hashlib
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import feedparser
import structlog

from theleadedge.sources.base import DataSourceConnector

logger = structlog.get_logger()

# Redfin's public weekly data export URL (gzipped TSV, ~100MB)
REDFIN_DATA_URL = (
    "https://redfin-public-data.s3.us-west-2.amazonaws.com/"
    "redfin_market_tracker/zip_code_market_tracker.tsv000.gz"
)

# Address regex: digits followed by street name components
# Matches patterns like "123 Main St", "4567 NW Oak Ave"
_ADDRESS_RE = re.compile(
    r"\b(\d{1,6}\s+"  # house number
    r"(?:N|S|E|W|NE|NW|SE|SW|NORTH|SOUTH|EAST|WEST)?\s*"  # optional direction
    r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*"  # street name
    r"(?:\s+(?:St|Ave|Blvd|Dr|Ln|Ct|Rd|Way|Pl|Cir|Ter|Trl|Pkwy|Hwy))"  # suffix
    r"\.?)\b",
    re.IGNORECASE,
)


def _parse_float(value: str) -> float | None:
    """Parse a float from a TSV cell, returning None for empty/invalid."""
    if not value or value.strip() in ("", "NA", "N/A", "-"):
        return None
    try:
        return float(value.strip())
    except (ValueError, TypeError):
        return None


def _parse_int(value: str) -> int | None:
    """Parse an integer from a TSV cell, returning None for empty/invalid."""
    if not value or value.strip() in ("", "NA", "N/A", "-"):
        return None
    try:
        return int(float(value.strip()))
    except (ValueError, TypeError):
        return None


def _parse_date_str(value: str) -> date | None:
    """Parse a date string in YYYY-MM-DD format."""
    if not value or not value.strip():
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


class RedfinMarketConnector(DataSourceConnector):
    """Downloads and parses Redfin's weekly ZIP-code market data.

    Redfin publishes a gzipped TSV file containing weekly market metrics
    per ZIP code. This connector downloads it, filters to target ZIPs,
    and extracts market snapshot data for persistence.

    Parameters
    ----------
    download_dir:
        Directory where the downloaded gzipped file is stored.
    target_zip_codes:
        List of ZIP code strings to filter on (e.g., from market.yaml).
    http_client:
        Optional httpx.AsyncClient for dependency injection in tests.
    """

    source_name = "redfin"

    def __init__(
        self,
        download_dir: Path,
        target_zip_codes: list[str],
        http_client: Any | None = None,
    ) -> None:
        super().__init__(name=self.source_name)
        self.download_dir = download_dir
        self.target_zip_codes = set(target_zip_codes)
        self._http_client = http_client
        self.log = logger.bind(source=self.source_name)

    async def authenticate(self) -> None:
        """No authentication needed -- Redfin data is public."""
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.log.info("authenticate_ok", download_dir=str(self.download_dir))

    async def fetch(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Download the gzipped TSV file from Redfin's S3 bucket.

        Streams the download to avoid loading the entire ~100MB file
        into memory at once. The file is saved to download_dir.

        Returns
        -------
        list[dict]
            Single-element list with ``{"file_path": Path}`` pointing
            to the downloaded gzipped TSV.
        """
        import httpx

        self.download_dir.mkdir(parents=True, exist_ok=True)
        dest = self.download_dir / "zip_code_market_tracker.tsv.gz"

        client = self._http_client
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=300.0)
            should_close = True

        try:
            self.log.info("download_start", url=REDFIN_DATA_URL)
            async with client.stream("GET", REDFIN_DATA_URL) as response:
                response.raise_for_status()
                with open(dest, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        f.write(chunk)
            self.log.info("download_complete", file=str(dest))
        finally:
            if should_close:
                await client.aclose()

        return [{"file_path": dest}]

    def transform(
        self, raw_records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Parse the gzipped TSV and filter to target ZIP codes.

        Reads the file line-by-line to handle the large file efficiently.
        Calculates absorption_rate from homes_sold and inventory.

        Parameters
        ----------
        raw_records:
            List from ``fetch()`` containing ``{"file_path": Path}``.

        Returns
        -------
        list[dict]
            Dicts suitable for MarketSnapshotRow construction.
        """
        results: list[dict[str, Any]] = []

        for entry in raw_records:
            file_path = entry["file_path"]
            if isinstance(file_path, str):
                file_path = Path(file_path)

            results.extend(self._parse_gzipped_tsv(file_path))

        self.log.info(
            "transform_complete",
            snapshots_produced=len(results),
            target_zips=len(self.target_zip_codes),
        )
        return results

    def _parse_gzipped_tsv(self, file_path: Path) -> list[dict[str, Any]]:
        """Read gzipped TSV line by line, filtering to target ZIPs.

        Parameters
        ----------
        file_path:
            Path to the gzipped TSV file.

        Returns
        -------
        list[dict]
            Market snapshot dicts for matching ZIP codes.
        """
        results: list[dict[str, Any]] = []

        with gzip.open(file_path, "rt", encoding="utf-8") as f:
            header_line = f.readline().strip()
            if not header_line:
                self.log.warning("empty_tsv_file", file=str(file_path))
                return results

            headers = header_line.split("\t")
            # Strip surrounding quotes and whitespace, then lowercase
            headers = [h.strip().strip('"').strip() for h in headers]
            header_index = {h.lower(): i for i, h in enumerate(headers)}

            # Find the column index for 'region' (ZIP code column)
            region_idx = header_index.get("region")
            if region_idx is None:
                self.log.error(
                    "missing_region_column",
                    available_headers=list(header_index.keys())[:20],
                )
                return results

            for line in f:
                cols = line.strip().split("\t")
                if len(cols) <= region_idx:
                    continue

                # Strip quotes and extract ZIP from "Zip Code: XXXXX"
                region = cols[region_idx].strip().strip('"').strip()
                if region.startswith("Zip Code: "):
                    region = region[len("Zip Code: "):]

                if region not in self.target_zip_codes:
                    continue

                snapshot = self._row_to_snapshot(headers, cols, region)
                if snapshot is not None:
                    results.append(snapshot)

        return results

    def _row_to_snapshot(
        self,
        headers: list[str],
        cols: list[str],
        zip_code: str,
    ) -> dict[str, Any] | None:
        """Convert a single TSV row to a MarketSnapshotRow-compatible dict.

        Parameters
        ----------
        headers:
            Column names from the header row.
        cols:
            Column values for this data row.
        zip_code:
            The ZIP code (already matched to target list).

        Returns
        -------
        dict or None
            Snapshot dict, or None if row cannot be parsed.
        """
        col_map: dict[str, str] = {}
        for i, h in enumerate(headers):
            if i < len(cols):
                col_map[h.strip().lower()] = cols[i].strip().strip('"')

        period_begin = _parse_date_str(col_map.get("period_begin", ""))
        period_end = _parse_date_str(col_map.get("period_end", ""))

        homes_sold = _parse_int(col_map.get("homes_sold", ""))
        inventory = _parse_int(col_map.get("inventory", ""))

        # Calculate absorption_rate = homes_sold / inventory * 100
        absorption_rate: float | None = None
        if homes_sold is not None and inventory is not None and inventory > 0:
            absorption_rate = round(homes_sold / inventory * 100, 2)

        return {
            "zip_code": zip_code,
            "source": self.source_name,
            "period_start": period_begin,
            "period_end": period_end,
            "median_sale_price": _parse_float(
                col_map.get("median_sale_price", "")
            ),
            "median_list_price": _parse_float(
                col_map.get("median_list_price", "")
            ),
            "median_dom": _parse_int(
                col_map.get("median_dom", "")
            ),
            "homes_sold": homes_sold,
            "new_listings": _parse_int(
                col_map.get("new_listings", "")
            ),
            "inventory": inventory,
            "months_of_supply": _parse_float(
                col_map.get("months_of_supply", "")
            ),
            "absorption_rate": absorption_rate,
            "sale_to_list_ratio": _parse_float(
                col_map.get("avg_sale_to_list")
                or col_map.get("sale_to_list", "")
            ),
            "price_drops_pct": _parse_float(
                col_map.get("price_drops", "")
            ),
        }

    async def health_check(self) -> bool:
        """Check connectivity to Redfin's S3 data bucket via HEAD request.

        Returns
        -------
        bool
            True if the data URL is reachable (HTTP 200).
        """
        import httpx

        client = self._http_client
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=15.0)
            should_close = True

        try:
            response = await client.head(REDFIN_DATA_URL)
            healthy = response.status_code == 200
            self.log.info(
                "health_check",
                status="healthy" if healthy else "unhealthy",
                http_status=response.status_code,
            )
            return healthy
        except Exception as exc:
            self.log.error("health_check_failed", error=str(exc))
            return False
        finally:
            if should_close:
                await client.aclose()


# ---------------------------------------------------------------------------
# GoogleAlertsConnector
# ---------------------------------------------------------------------------


class GoogleAlertsConnector(DataSourceConnector):
    """Parses Google Alerts RSS/Atom feeds for real estate intelligence.

    Google Alerts can be configured to monitor keywords like "foreclosure
    southwest florida" and deliver results as RSS feeds. This connector
    fetches those feeds, parses entries, and extracts potential address
    mentions from the content.

    Parameters
    ----------
    feed_urls:
        List of Google Alerts RSS feed URLs.
    http_client:
        Optional httpx.AsyncClient for dependency injection in tests.
    """

    source_name = "google_alerts"

    def __init__(
        self,
        feed_urls: list[str],
        http_client: Any | None = None,
    ) -> None:
        super().__init__(name=self.source_name)
        self.feed_urls = [url for url in feed_urls if url]
        self._http_client = http_client
        self.log = logger.bind(source=self.source_name)

    async def authenticate(self) -> None:
        """No authentication needed -- RSS feeds are public."""
        self.log.info(
            "authenticate_ok",
            feed_count=len(self.feed_urls),
        )

    async def fetch(
        self,
        since: datetime | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Download each RSS/Atom feed as raw XML.

        Parameters
        ----------
        since:
            Not used for RSS feeds (feeds are always full).
        **filters:
            Not used.

        Returns
        -------
        list[dict]
            Each dict contains ``{"xml": str, "url": str}``.
        """
        import httpx

        client = self._http_client
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=30.0)
            should_close = True

        results: list[dict[str, Any]] = []
        try:
            for url in self.feed_urls:
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    results.append({
                        "xml": response.text,
                        "url": url,
                    })
                    self.log.info("feed_fetched", feed_url=url)
                except Exception as exc:
                    self.log.error(
                        "feed_fetch_failed",
                        feed_url=url,
                        error=str(exc),
                    )
        finally:
            if should_close:
                await client.aclose()

        return results

    def transform(
        self, raw_records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Parse RSS/Atom XML feeds and extract alert entries.

        For each entry, attempts to extract street addresses from the
        content using regex pattern matching.

        Parameters
        ----------
        raw_records:
            List from ``fetch()`` containing ``{"xml": str, "url": str}``.

        Returns
        -------
        list[dict]
            Dicts suitable for SourceRecord construction.
        """
        results: list[dict[str, Any]] = []

        for entry in raw_records:
            xml_text = entry.get("xml", "")
            feed_url = entry.get("url", "")

            parsed = feedparser.parse(xml_text)

            for item in parsed.entries:
                record = self._entry_to_source_record(item, feed_url)
                if record is not None:
                    results.append(record)

        self.log.info(
            "transform_complete",
            feeds_parsed=len(raw_records),
            records_produced=len(results),
        )
        return results

    def _entry_to_source_record(
        self,
        entry: Any,
        feed_url: str,
    ) -> dict[str, Any] | None:
        """Convert a feedparser entry to a SourceRecord-compatible dict.

        Parameters
        ----------
        entry:
            A feedparser entry object.
        feed_url:
            The source feed URL (for audit trail).

        Returns
        -------
        dict or None
            SourceRecord dict, or None if the entry is empty.
        """
        title = getattr(entry, "title", "") or ""
        link = getattr(entry, "link", "") or ""
        published = getattr(entry, "published", "") or ""

        # Extract content/summary text
        content_text = ""
        if hasattr(entry, "summary"):
            content_text = entry.summary or ""
        elif hasattr(entry, "content") and entry.content:
            content_text = entry.content[0].get("value", "")

        if not title and not content_text:
            return None

        # Parse published date
        event_date: date | None = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                dt = datetime(*entry.published_parsed[:6])
                event_date = dt.date()
            except (TypeError, ValueError):
                pass

        # Attempt address extraction from title + content
        full_text = f"{title} {content_text}"
        addresses = _ADDRESS_RE.findall(full_text)
        street_address = addresses[0].strip() if addresses else None

        # Generate a stable record ID from the link or title
        id_source = link or title
        record_id = hashlib.md5(
            id_source.encode("utf-8")
        ).hexdigest()[:16]

        # Content snippet for raw_data (strip HTML tags, truncate)
        content_snippet = re.sub(r"<[^>]+>", "", content_text)[:500]

        return {
            "source_name": self.source_name,
            "source_record_id": record_id,
            "record_type": "google_alert",
            "street_address": street_address,
            "event_date": event_date,
            "raw_data": {
                "title": title,
                "link": link,
                "content_snippet": content_snippet,
                "feed_url": feed_url,
                "published": published,
            },
        }

    async def health_check(self) -> bool:
        """Check connectivity by fetching and parsing the first feed URL.

        Returns
        -------
        bool
            True if the first feed URL can be fetched and parsed.
        """
        if not self.feed_urls:
            self.log.warning("health_check_no_feeds")
            return False

        import httpx

        client = self._http_client
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=15.0)
            should_close = True

        try:
            response = await client.get(self.feed_urls[0])
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
