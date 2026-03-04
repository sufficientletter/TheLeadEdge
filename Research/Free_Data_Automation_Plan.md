# Free Data Automation Plan: Phase 2 Implementation Blueprint

> **Project**: TheLeadEdge -- Real Estate Lead Generation System
> **Author**: Systems Architect
> **Created**: 2026-03-03
> **Status**: Implementation-ready specification
> **Prerequisite**: Phase 1 MVP complete (64 tests passing, CSV import + scoring + briefing operational)
> **Target Market**: Lee County + Collier County, Southwest Florida

---

## Executive Summary

Phase 1 established the core pipeline: MLS CSV import, 12 signal detection rules, YAML-driven scoring with decay and stacking, and automated daily email briefings. That pipeline currently operates on a single data source (MLS CSV exports) and activates 12 of 20 configured signal types.

This plan specifies how to automate ingestion of **eight free public data sources** that will activate the remaining **8 dormant signal types** and unlock **4 high-value stacking rules** that are already configured in `config/scoring_weights.yaml` but have no data feeding them.

The sources divide into three categories by automation approach:

| Category | Sources | Automation | Effort |
|----------|---------|------------|--------|
| **Direct HTTP Download** | County Property Appraisers (2), Redfin Data Center | Scheduled GET requests, parse CSV/TSV/NAL | Low |
| **File Drop Processing** | Sunshine Law responses (lis pendens, probate, code violations) | Parse email attachments or file drops | Low |
| **RSS/Feed Parsing** | Craigslist FSBO, Google Alerts | Standard RSS parsing | Low |
| **SFTP Bulk Download** | Florida Sunbiz LLC records | SFTP client, parse bulk data | Medium |

Every source is free. No API keys required. No authentication required (except Sunbiz SFTP which uses published public credentials). Total cost: $0/month (or optionally $29-99/month for ForeclosureAuctionData.com as a convenience supplement).

**Expected impact**: Activating the 8 dormant signals and 4 stacking rules will dramatically improve lead differentiation. A property with only MLS signals might score 30 points (Tier C). That same property with a lis pendens filing (+20 pts) and tax delinquency (+13 pts) triggers the `financial_distress` 2.0x stacking rule, pushing the composite score to 126 raw points before normalization -- a clear Tier S lead that would otherwise be invisible.

---

## Table of Contents

1. [Data Source Inventory](#1-data-source-inventory)
2. [Technical Architecture](#2-technical-architecture)
3. [Database Schema Changes](#3-database-schema-changes)
4. [Address Matching System](#4-address-matching-system)
5. [New Signal Detection Rules](#5-new-signal-detection-rules)
6. [Connector Implementations](#6-connector-implementations)
7. [Scheduling Configuration](#7-scheduling-configuration)
8. [CLI Extensions](#8-cli-extensions)
9. [Python Dependencies](#9-python-dependencies)
10. [What This Unlocks](#10-what-this-unlocks)
11. [Implementation Phases](#11-implementation-phases)
12. [Cost Analysis](#12-cost-analysis)
13. [Risk Assessment](#13-risk-assessment)
14. [File Manifest](#14-file-manifest)

---

## 1. Data Source Inventory

### 1.1 Collier County Property Appraiser (Direct HTTP)

| Attribute | Value |
|-----------|-------|
| **Source** | Collier County Property Appraiser |
| **URL** | `https://www.collierappraiser.com/Main_Data/DataDownloads.html` |
| **Documentation** | `https://www.collierappraiser.com/Main_Data/HowtoUsetheFiles.html` |
| **Format** | CSV files, downloadable via direct HTTP GET |
| **Authentication** | None required |
| **Update Frequency** | Monthly (county updates data periodically) |
| **Join Key** | PARCELID across all files |
| **Cost** | Free |

**Available Files**:

| File | Contents | Key Fields for TheLeadEdge |
|------|----------|---------------------------|
| Parcels | Parcel identification, site address, mailing address | PARCELID, site_addr, mail_addr, owner_name |
| Sales | Transaction history | sale_price, sale_date, instrument_no |
| Buildings | Structure details | year_built, total_area, bedrooms, bathrooms |
| Legal | Legal descriptions | subdivision, lot, block |
| Values History | 5 years of assessed values | just_value, assessed_value by year |

**Algorithms enabled**:
- **Absentee owner detection**: `mailing_address != site_address`
- **Investor detection**: Residential property with no homestead exemption
- **High equity identification**: No recorded sale in 15+ years
- **Value decline detection**: 5-year assessed value trend is downward
- **Vacant property inference**: No homestead + absentee + low assessed improvement value

### 1.2 Lee County Property Appraiser -- LEEPA (Direct HTTP)

| Attribute | Value |
|-----------|-------|
| **Source** | Lee County Property Appraiser (LEEPA) |
| **Tax Roll URL** | `https://www.leepa.org/Roll/TaxRoll.aspx` |
| **Sales Data URL** | `https://www.leepa.org/Roll/SDFTxt.aspx` |
| **Parcel List Tool** | `https://www.leepa.org/OnlineReports/ParcelListGenerator.aspx` |
| **Format** | NAL format (Florida DOR standard) ZIP files; SDF text files |
| **Authentication** | None required |
| **Update Frequency** | Annual tax roll; sales data spans 17 years |
| **Join Key** | STRAP (parcel ID in Lee County format) |
| **Cost** | Free |

**NAL Format**: The NAL (Name-Address-Legal) file follows the Florida Department of Revenue standard field layout. Fields are fixed-width positional, documented in the DOR's NAL file specification. Key fields include parcel ID (STRAP), owner name, mailing address, site address, property use code, assessed value, taxable value, and exemption codes.

**Sales Data Format (SDF)**: Tab-delimited or fixed-width text file containing 17 years of property sales. Fields include STRAP, sale date, sale price, deed type, qualified/unqualified flag, grantor, grantee.

### 1.3 Clerk of Court Records -- Sunshine Law Approach (File Drop)

| Attribute | Value |
|-----------|-------|
| **Source** | Lee County Clerk + Collier County Clerk |
| **Method** | Florida Sunshine Law (F.S. Chapter 119) public records requests |
| **Format** | CSV or Excel (requested format), delivered via email |
| **Authentication** | None -- public records are constitutionally guaranteed |
| **Update Frequency** | Monthly requests |
| **Cost** | Near-free (actual cost of electronic duplication, typically $0) |

**Three record types requested**:

| Record Type | Signal Activated | Request Frequency |
|-------------|-----------------|-------------------|
| Lis Pendens filings | `pre_foreclosure` (20 pts) | Monthly |
| Probate case index | `probate` (18 pts) | Monthly |
| Domestic Relations filings | `divorce` (16 pts) | Monthly |

**Contacts for Sunshine Law requests**:

| County | Contact | Method |
|--------|---------|--------|
| Lee County Clerk | Public Records Request | leeclerk.org/services/public-records-request |
| Lee County Code | (239) 533-8895, codeenforcement@leegov.com | Email/phone |
| Collier County Clerk | Renata Robbins, (239) 252-2646 | Email/phone |
| Collier County Code | (239) 252-2440 | Email/phone |

**Template letter structure** (detailed templates in `Research/clerk_of_court_automation_research.md`):

```
Subject: Public Records Request Pursuant to Florida Statute 119

Request: All [lis pendens / probate / domestic relations] filings
         recorded between [date range]
Format:  Electronic spreadsheet (CSV preferred, Excel acceptable)
Fields:  Case number, filing date, property address or parcel ID,
         party names, case type, case status
Delivery: Email attachment
```

**Standing requests**: Some Florida clerks honor standing/recurring monthly requests. The initial request letter should ask whether standing requests are possible. If not, calendar a monthly reminder to submit new requests.

### 1.4 Code Enforcement Violations (File Drop)

| Attribute | Value |
|-----------|-------|
| **Source** | Lee County Code Enforcement + Collier County Code Enforcement |
| **Method** | Florida Sunshine Law public records request |
| **Format** | CSV or Excel, delivered via email |
| **Authentication** | None |
| **Update Frequency** | Quarterly requests |
| **Cost** | Near-free |

**Contacts**:
- Lee County: codeenforcement@leegov.com, (239) 533-8895
- Collier County: (239) 252-2440

**Requested fields**: Case number, property address, parcel ID, violation type, violation date, status (open/closed), compliance deadline.

**Signal activated**: `code_violation` (12 pts, step decay, 60-day half-life).

### 1.5 Redfin Data Center (Direct HTTP / S3)

| Attribute | Value |
|-----------|-------|
| **Source** | Redfin Public Data Center |
| **URL** | `https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/zip_code_market_tracker.tsv000.gz` |
| **Format** | TSV (tab-separated values), gzip-compressed |
| **Authentication** | None -- publicly accessible S3 object |
| **Update Frequency** | Weekly |
| **Size** | ~150-200 MB compressed, covers all US ZIP codes |
| **Cost** | Free |

**Key fields for TheLeadEdge**:

| Field | Use |
|-------|-----|
| `period_begin`, `period_end` | Time range for the data point |
| `region` (ZIP code) | Filter to our 52 SWFLA ZIPs |
| `median_sale_price` | Market positioning |
| `median_dom` | Calibrate high_dom threshold dynamically |
| `homes_sold` | Absorption rate calculation |
| `inventory` | Supply-side pressure |
| `price_drops` | Market-wide price reduction rate |
| `avg_sale_to_list` | Market competitiveness indicator |
| `months_of_supply` | Buyer's vs. seller's market determination |

**Algorithms enabled**:
- **`neighborhood_hot` signal**: ZIP codes where absorption rate (homes_sold / inventory) exceeds the metro-wide median
- **Dynamic DOM threshold**: Replace hardcoded 90-day DOM threshold with `2 * median_dom` for each ZIP
- **Seasonal adjustment**: Detect seasonal patterns in DOM and inventory to reduce false positives

### 1.6 Craigslist FSBO (RSS Feed)

| Attribute | Value |
|-----------|-------|
| **Source** | Craigslist Fort Myers real estate by-owner |
| **URL** | `https://fortmyers.craigslist.org/search/rea?purveyor=owner&format=rss` |
| **Format** | RSS/XML (standard Atom/RSS feed) |
| **Authentication** | None |
| **Update Frequency** | Real-time; poll daily |
| **Cost** | Free |

**What it provides**: FSBO (For Sale By Owner) listings in the Fort Myers / SWFLA Craigslist region. These are property owners who have chosen not to use a listing agent -- a distinct lead category with its own outreach strategy.

**Key data from RSS entries**:
- Title (often includes address or neighborhood)
- Price (embedded in title or description)
- Description text (motivation indicators: "must sell", "relocating", "estate sale")
- Post date
- Geographic coordinates (when provided)
- Craigslist post URL

**Note**: Craigslist does not cover Naples/Collier as thoroughly as Fort Myers/Lee. The RSS feed may miss some SWFLA listings. This is a supplementary source, not primary.

### 1.7 Google Alerts (RSS Feed)

| Attribute | Value |
|-----------|-------|
| **Source** | Google Alerts with RSS delivery |
| **URL** | User-configured RSS feed URLs from Google Alerts |
| **Format** | RSS/Atom XML |
| **Authentication** | Google account required for setup (one-time) |
| **Update Frequency** | As-it-happens or daily digest |
| **Cost** | Free |

**Recommended alert queries**:
- `"for sale by owner" "Cape Coral" OR "Fort Myers" OR "Naples" OR "Lehigh Acres"`
- `"must sell" real estate "Lee County" OR "Collier County" Florida`
- `"estate sale" home "Southwest Florida"`
- `"foreclosure" "Lee County" OR "Collier County" Florida`
- `"pre-foreclosure" "Fort Myers" OR "Naples" Florida`

**Setup procedure**: Create alerts at google.com/alerts, select "RSS feed" as delivery method instead of email. Save the RSS feed URLs to a YAML config file that the connector reads.

### 1.8 Florida Sunbiz LLC Records (SFTP)

| Attribute | Value |
|-----------|-------|
| **Source** | Florida Division of Corporations (Sunbiz) |
| **SFTP Host** | `sftp.floridados.gov` |
| **SFTP Credentials** | User: `Public`, Password: `PubAccess1845!` (publicly published) |
| **Bulk Downloads** | `https://dos.fl.gov/sunbiz/other-services/data-downloads/` |
| **Format** | Pipe-delimited text files |
| **Update Frequency** | Quarterly SFTP refresh; annual bulk downloads |
| **Cost** | Free |

**Purpose**: Cross-reference LLC names from PA ownership data. Properties owned by LLCs with registered agents at out-of-state addresses are strong absentee owner / investor signals. Properties owned by recently dissolved LLCs may be distressed.

**Key fields**: Entity name, document number, filing date, status (Active/Inactive/Dissolved), registered agent name, registered agent address, principal address, mailing address.

**Note**: The SFTP credentials are published by the Florida Division of Corporations specifically for public access. They are not secrets. However, to follow the project security conventions, they should still be stored in `.env` rather than hardcoded, in case the Division changes them.

---

## 2. Technical Architecture

### 2.1 Connector Class Hierarchy

All new connectors extend `DataSourceConnector` at `src/theleadedge/sources/base.py`, inheriting the `sync()` template method that handles timing, error capture, and `SyncResult` construction.

```
DataSourceConnector (ABC)          # src/theleadedge/sources/base.py
  |
  +-- MLSCsvConnector              # src/theleadedge/sources/mls_csv.py     [EXISTS]
  |
  +-- PropertyAppraiserConnector   # src/theleadedge/sources/property_appraiser.py  [NEW]
  |     |
  |     +-- CollierPAConnector     # Collier County specifics (CSV format)
  |     +-- LeePAConnector         # Lee County specifics (NAL format)
  |
  +-- ClerkRecordConnector         # src/theleadedge/sources/clerk_records.py       [NEW]
  |     Parses Sunshine Law response files (CSV/Excel)
  |     for lis pendens, probate, and divorce filings
  |
  +-- CodeViolationConnector       # src/theleadedge/sources/code_violations.py     [NEW]
  |     Parses code enforcement response files (CSV/Excel)
  |
  +-- MarketDataConnector          # src/theleadedge/sources/market_data.py         [NEW]
  |     Downloads Redfin S3 data + parses Google Alerts RSS
  |
  +-- FSBOConnector                # src/theleadedge/sources/fsbo.py                [NEW]
  |     Parses Craigslist RSS feed for FSBO listings
  |
  +-- SunbizConnector              # src/theleadedge/sources/sunbiz.py              [NEW]
        Downloads LLC records via SFTP or bulk HTTP
```

### 2.2 Data Flow Architecture

```
                     DATA SOURCES
                     ============
                           |
     +----------+----------+----------+----------+----------+
     |          |          |          |          |          |
  Collier PA  Lee PA   Clerk CSV   Redfin   Craigslist  Sunbiz
  (HTTP CSV)  (HTTP NAL) (file drop) (S3 TSV) (RSS XML)  (SFTP)
     |          |          |          |          |          |
     +-----+----+     +----+    +----+     +----+     +----+
           |          |         |          |          |
     [Connector.fetch()]  [Connector.fetch()]  [Connector.fetch()]
           |          |         |          |          |
     [Connector.transform()]  ...         ...        ...
           |          |         |          |          |
     +-----+----------+---------+----------+----------+
                       |
              SourceRecord (Pydantic)
                       |
               RecordMapper.match()
              /        |         \
        parcel_id   address    fuzzy
        (exact)     (normalized) (review)
              \        |         /
               PropertyRow (DB)
                       |
              SignalDetector.detect()
                       |
              SignalRow (DB)
                       |
              ScoringEngine.score()
                       |
              LeadRow.current_score
                       |
              BriefingGenerator
                       |
                 Daily Email
```

### 2.3 Source Record Protocol

Every connector transforms raw data into `SourceRecord` instances that share a common interface for the matching pipeline.

```python
# src/theleadedge/models/source_record.py [NEW]

class SourceRecord(BaseModel):
    """Normalized record from any external data source.

    Used as the common interface between connectors and the
    address matching pipeline. Every connector's transform()
    method produces a list of these.
    """

    source_name: str                    # e.g., "collier_pa", "lee_clerk"
    source_record_id: str               # Unique ID from source system
    record_type: str                    # e.g., "parcel", "lis_pendens", "code_violation"

    # Address fields (at least one must be populated)
    parcel_id: str | None = None        # County parcel ID (most reliable join key)
    street_address: str | None = None   # Raw street address from source
    city: str | None = None
    state: str = "FL"
    zip_code: str | None = None

    # Normalized address (computed by RecordMapper)
    address_normalized: str | None = None

    # Record-specific data (varies by source)
    event_date: date | None = None
    event_type: str | None = None       # Sub-type: "lis_pendens", "probate", etc.
    raw_data: dict[str, Any] = {}       # Full raw record for audit

    # Owner information (PII -- NEVER log)
    owner_name: str | None = None
    mailing_address: str | None = None

    # Matching result (populated by RecordMapper)
    matched_property_id: int | None = None
    match_method: str | None = None     # "parcel_id", "address", "fuzzy", "manual"
    match_confidence: float = 0.0       # 0.0-1.0
```

### 2.4 Record Mapper

The `RecordMapper` resolves `SourceRecord` objects to existing `PropertyRow` records in the database using a cascading match strategy.

```python
# src/theleadedge/pipelines/match.py [NEW]

class RecordMapper:
    """Maps source records to properties using cascading match strategies.

    Match cascade (stops at first match):
    1. Parcel ID exact match (highest confidence)
    2. Listing Key (MLS-specific, for cross-referencing MLS data)
    3. Normalized address exact match
    4. Fuzzy address match (Levenshtein distance <= threshold)

    Unmatched records are queued for manual review or
    optionally create new PropertyRow entries.
    """

    async def match(
        self,
        session: AsyncSession,
        record: SourceRecord,
    ) -> MatchResult:
        ...
```

**Match result routing**:
- **Confidence >= 0.95** (parcel ID or exact address): Automatically link to PropertyRow, create signals
- **Confidence 0.70-0.94** (fuzzy match): Queue in `match_queue` table for human review
- **Confidence < 0.70** (no match): Optionally create new PropertyRow (for PA data) or skip (for clerk records)

---

## 3. Database Schema Changes

### 3.1 New Columns on PropertyRow

Add to `src/theleadedge/storage/database.py`, class `PropertyRow`:

```python
# --- Property Appraiser Enrichment (Phase 2) ---
parcel_id: Mapped[str | None] = mapped_column(String(30), index=True)
homestead_exempt: Mapped[bool] = mapped_column(Boolean, default=False)
assessed_value: Mapped[float | None] = mapped_column(Float)
assessed_value_previous: Mapped[float | None] = mapped_column(Float)
last_sale_date: Mapped[datetime | None] = mapped_column(Date)
last_sale_price: Mapped[float | None] = mapped_column(Float)
property_use_code: Mapped[str | None] = mapped_column(String(10))
owner_name_raw: Mapped[str | None] = mapped_column(String(200))  # PII - NEVER log
mailing_address_raw: Mapped[str | None] = mapped_column(String(300))  # PII - NEVER log
```

**Migration strategy**: Use Alembic for the first time. Create migration with `alembic revision --autogenerate -m "add PA enrichment columns"`. All new columns are nullable, so existing data is unaffected.

### 3.2 New Table: SourceRecordRow

Audit table tracking every record ingested from every source, with its match status.

```python
# Add to src/theleadedge/storage/database.py

class SourceRecordRow(Base):
    """Audit trail for records from external data sources."""

    __tablename__ = "source_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[str] = mapped_column(String(50), index=True)
    source_record_id: Mapped[str] = mapped_column(String(100))
    record_type: Mapped[str] = mapped_column(String(50))

    # Match result
    property_id: Mapped[int | None] = mapped_column(
        ForeignKey("properties.id"), index=True
    )
    match_method: Mapped[str | None] = mapped_column(String(20))
    match_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # Record metadata
    event_date: Mapped[datetime | None] = mapped_column(Date)
    event_type: Mapped[str | None] = mapped_column(String(50))
    raw_data_json: Mapped[str | None] = mapped_column(Text)  # JSON serialized

    # Lifecycle
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    processed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Unique constraint: prevent duplicate imports
    # __table_args__ = (
    #     UniqueConstraint("source_name", "source_record_id", name="uq_source_record"),
    # )
```

### 3.3 New Table: MatchQueueRow

Holds unmatched or low-confidence records pending manual review.

```python
class MatchQueueRow(Base):
    """Records pending manual address matching review."""

    __tablename__ = "match_queue"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_record_id: Mapped[int] = mapped_column(
        ForeignKey("source_records.id"), index=True
    )

    # Candidate matches (JSON array of {property_id, confidence, method})
    candidate_matches_json: Mapped[str | None] = mapped_column(Text)

    # Review status
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, matched, skipped, new_property
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    matched_property_id: Mapped[int | None] = mapped_column(
        ForeignKey("properties.id")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
```

### 3.4 New Table: MarketSnapshotRow

Stores Redfin market data snapshots per ZIP code per time period.

```python
class MarketSnapshotRow(Base):
    """Market data snapshot for a ZIP code from Redfin."""

    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    zip_code: Mapped[str] = mapped_column(String(10), index=True)
    period_begin: Mapped[datetime] = mapped_column(Date)
    period_end: Mapped[datetime] = mapped_column(Date)

    median_sale_price: Mapped[float | None] = mapped_column(Float)
    median_dom: Mapped[int | None] = mapped_column(Integer)
    homes_sold: Mapped[int | None] = mapped_column(Integer)
    new_listings: Mapped[int | None] = mapped_column(Integer)
    inventory: Mapped[int | None] = mapped_column(Integer)
    months_of_supply: Mapped[float | None] = mapped_column(Float)
    price_drops_pct: Mapped[float | None] = mapped_column(Float)
    avg_sale_to_list: Mapped[float | None] = mapped_column(Float)

    source: Mapped[str] = mapped_column(String(20), default="redfin")
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
```

### 3.5 New Table: FSBOListingRow

Stores FSBO listings from Craigslist and other sources.

```python
class FSBOListingRow(Base):
    """For Sale By Owner listing from Craigslist or other sources."""

    __tablename__ = "fsbo_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(30))  # "craigslist", "google_alert"
    source_url: Mapped[str] = mapped_column(String(500), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    asking_price: Mapped[float | None] = mapped_column(Float)

    # Location (extracted from listing)
    address_raw: Mapped[str | None] = mapped_column(String(300))
    city: Mapped[str | None] = mapped_column(String(100))
    zip_code: Mapped[str | None] = mapped_column(String(10))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    # Match to property
    property_id: Mapped[int | None] = mapped_column(
        ForeignKey("properties.id"), index=True
    )

    # Metadata
    posted_at: Mapped[datetime | None] = mapped_column(DateTime)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

### 3.6 Summary of Schema Changes

| Table | Action | Columns/Description |
|-------|--------|---------------------|
| `properties` | ALTER | +9 columns (parcel_id, homestead_exempt, assessed_value, etc.) |
| `source_records` | CREATE | Audit table for all external source records |
| `match_queue` | CREATE | Manual review queue for low-confidence matches |
| `market_snapshots` | CREATE | Redfin market data per ZIP per period |
| `fsbo_listings` | CREATE | FSBO listings from Craigslist and other sources |

Total: 1 table altered, 4 tables created. All changes are additive; no destructive migrations.

---

## 4. Address Matching System

### 4.1 The Core Challenge

Public records use parcel IDs and legal descriptions. MLS data uses street addresses and listing keys. Joining these requires a reliable address matching pipeline. The existing `utils/address.py` module (`normalize_address()` and `make_address_key()`) provides the foundation.

### 4.2 Match Cascade

The matcher tries strategies in order of reliability, stopping at the first confident match:

```
Strategy 1: Parcel ID Exact Match
  - Input: parcel_id from source record
  - Match: PropertyRow.parcel_id == source.parcel_id
  - Confidence: 1.0
  - Notes: Most reliable. PA data always has parcel IDs.
           Once a PropertyRow has parcel_id populated (from PA import),
           all subsequent sources can use it.

Strategy 2: Normalized Address Exact Match
  - Input: street_address, city, state, zip_code from source record
  - Process: normalize_address() from utils/address.py
  - Match: PropertyRow.address_normalized == normalize_address(source)
  - Confidence: 0.95
  - Notes: Handles directional/suffix variations ("N Main St" = "North Main Street")

Strategy 3: Address Key Match
  - Input: street_address, zip_code from source record
  - Process: make_address_key() strips units, removes non-alphanumeric
  - Match: make_address_key(source) == make_address_key(property)
  - Confidence: 0.85
  - Notes: Catches unit number variations (123 Main St #4 vs 123 Main St Apt 4)

Strategy 4: Fuzzy Address Match
  - Input: normalized address string
  - Process: Levenshtein distance calculation (using rapidfuzz library)
  - Match: ratio >= 85 AND zip_code matches exactly
  - Confidence: 0.70 * (ratio / 100)
  - Notes: Catches typos and minor variations. Requires ZIP match as guard rail.
           Results go to match_queue for review.
```

### 4.3 Implementation

```python
# src/theleadedge/pipelines/match.py [NEW]

from dataclasses import dataclass
from theleadedge.utils.address import normalize_address, make_address_key

@dataclass
class MatchResult:
    property_id: int | None
    method: str          # "parcel_id", "address_normalized", "address_key", "fuzzy", "none"
    confidence: float    # 0.0 - 1.0
    needs_review: bool   # True if confidence < 0.95

class RecordMapper:
    """Cascading address matcher for linking source records to properties."""

    FUZZY_THRESHOLD: int = 85  # Minimum Levenshtein ratio for fuzzy match
    REVIEW_THRESHOLD: float = 0.95  # Below this, queue for review

    async def match(
        self,
        session: AsyncSession,
        record: SourceRecord,
    ) -> MatchResult:
        """Try all match strategies in cascade order."""

        # Strategy 1: Parcel ID
        if record.parcel_id:
            prop = await self._match_parcel_id(session, record.parcel_id)
            if prop:
                return MatchResult(prop.id, "parcel_id", 1.0, False)

        # Strategy 2: Normalized address
        if record.street_address and record.zip_code:
            addr_norm = normalize_address(
                record.street_address, record.city or "", record.state, record.zip_code
            )
            prop = await self._match_address_normalized(session, addr_norm)
            if prop:
                return MatchResult(prop.id, "address_normalized", 0.95, False)

            # Strategy 3: Address key
            key = make_address_key(record.street_address, record.zip_code)
            prop = await self._match_address_key(session, key)
            if prop:
                return MatchResult(prop.id, "address_key", 0.85, True)

            # Strategy 4: Fuzzy match
            prop, ratio = await self._match_fuzzy(session, addr_norm, record.zip_code)
            if prop and ratio >= self.FUZZY_THRESHOLD:
                conf = 0.70 * (ratio / 100)
                return MatchResult(prop.id, "fuzzy", conf, True)

        return MatchResult(None, "none", 0.0, False)
```

### 4.4 Parcel ID as the Bridge

The Property Appraiser data is the highest-priority import because it populates `parcel_id` on `PropertyRow`. Once parcel IDs are populated:

1. MLS properties get parcel IDs via address matching with PA data
2. All subsequent clerk/code records can match on parcel ID directly
3. Match confidence jumps from 0.85-0.95 (address) to 1.0 (parcel ID)

This is why PA import is Priority 1 in the implementation order.

---

## 5. New Signal Detection Rules

### 5.1 Existing Signal Detector Extension

The current `SignalDetector` at `src/theleadedge/pipelines/detect.py` handles MLS-sourced signals. We need to extend it (or create a parallel `PublicRecordDetector`) for signals from public record sources.

**Design decision**: Extend the existing `SignalDetector` class with new methods rather than creating a separate class. The `_make_signal()` helper and config lookup already work for any signal type. The only difference is the `source` field on `SignalCreate` changes from `"mls_csv"` to the appropriate source name.

### 5.2 New Detection Rules

Each rule maps to a pre-configured signal type in `config/scoring_weights.yaml`:

**Rule 13: `pre_foreclosure`** (from Clerk lis pendens data)
```
Source:     ClerkRecordConnector (lis pendens filings)
Trigger:    record_type == "lis_pendens" AND parcel matches property
Points:     20 (escalating decay, 60-day half-life)
Event date: Filing date from clerk record
Source ref: Case number from clerk record
Note:       Escalating decay means urgency INCREASES as auction approaches
```

**Rule 14: `tax_delinquent`** (from PA data or Tax Collector)
```
Source:     PropertyAppraiserConnector (tax roll data)
Trigger:    Tax delinquency flag set OR delinquent_years >= 1
Points:     13 (linear decay, 120-day half-life)
Event date: Tax year end date
Note:       Tax delinquency data may come from PA tax roll or from
            a separate Tax Collector Sunshine Law request
```

**Rule 15: `code_violation`** (from Code Enforcement data)
```
Source:     CodeViolationConnector (code enforcement response)
Trigger:    Active/open code violation on parcel
Points:     12 (step decay, 60-day half-life)
Event date: Violation date from code enforcement record
Source ref: Case number from code enforcement
Note:       Multiple active violations on same property should create
            only one signal but with enhanced description
```

**Rule 16: `probate`** (from Clerk probate data)
```
Source:     ClerkRecordConnector (probate case index)
Trigger:    record_type == "probate" AND parcel or address matches property
Points:     18 (linear decay, 90-day half-life)
Event date: Filing date from clerk record
Source ref: Case number
Note:       Probate leads require maximum sensitivity in outreach.
            The person is dealing with loss. The scoring algorithm is neutral,
            but outreach templates must reflect empathy-first approach.
```

**Rule 17: `divorce`** (from Clerk domestic relations data)
```
Source:     ClerkRecordConnector (domestic relations filings)
Trigger:    record_type == "domestic_relations" AND parcel or address matches
Points:     16 (step decay, 45-day half-life)
Event date: Filing date
Source ref: Case number
Note:       Divorce cases with real property are the relevant subset.
            Not all domestic relations filings involve property.
```

**Rule 18: `vacant_property`** (composite signal from PA data)
```
Source:     PropertyAppraiserConnector (multiple PA fields)
Trigger:    ALL of the following:
            - homestead_exempt == False
            - is_absentee == True (mailing != site address)
            - property_use_code in residential codes
            Optional strengtheners:
            - No recent utility connect (if available)
            - Improvement value near zero
Points:     10 (linear decay, 180-day half-life)
Event date: Date of PA data snapshot
Note:       This is an inferred signal, not a direct observation.
            The 180-day half-life reflects its persistence.
```

**Rule 19: `neighborhood_hot`** (from Redfin market data)
```
Source:     MarketDataConnector (Redfin S3 data)
Trigger:    ZIP code absorption_rate > metro_median_absorption_rate
            where absorption_rate = homes_sold / inventory
Points:     5 (linear decay, 90-day half-life)
Event date: period_end from Redfin data
Note:       Applied at ZIP code level, not property level.
            All properties in a "hot" ZIP get this signal.
            Low base points (5) reflect that this is contextual, not property-specific.
```

**Rule 20: `agent_churn`** (from MLS data -- already detectable)
```
Source:     MLSCsvConnector (listing agent changes across imports)
Trigger:    list_agent_key on current import != list_agent_key on previous import
            for the same listing_key
Points:     7 (exponential decay, 30-day half-life)
Event date: Date of the import that detected the change
Note:       This signal requires comparing current import to stored data.
            Must check PropertyRow.list_agent_key before updating.
            Can be implemented in Phase 2 without any new data source --
            it only requires a code change in the ingest pipeline.
```

### 5.3 Detection Method Signatures

```python
# Added to SignalDetector class in src/theleadedge/pipelines/detect.py

def detect_from_source_record(
    self,
    record: SourceRecord,
    lead_id: int,
    property_id: int,
    now: datetime,
) -> list[SignalCreate]:
    """Detect signals from a public record source record.

    Unlike detect() which works on MLS property data dicts,
    this method works on SourceRecord instances from any connector.
    """
    signals: list[SignalCreate] = []

    if record.record_type == "lis_pendens":
        sig = self._detect_pre_foreclosure(record, lead_id, property_id)
        if sig:
            signals.append(sig)

    elif record.record_type == "probate":
        sig = self._detect_probate(record, lead_id, property_id)
        if sig:
            signals.append(sig)

    elif record.record_type == "domestic_relations":
        sig = self._detect_divorce(record, lead_id, property_id)
        if sig:
            signals.append(sig)

    elif record.record_type == "code_violation":
        sig = self._detect_code_violation(record, lead_id, property_id)
        if sig:
            signals.append(sig)

    elif record.record_type == "parcel":
        # PA data can trigger multiple signals
        sig = self._detect_vacant_property(record, lead_id, property_id)
        if sig:
            signals.append(sig)
        sig = self._detect_tax_delinquent(record, lead_id, property_id)
        if sig:
            signals.append(sig)

    return signals
```

---

## 6. Connector Implementations

### 6.1 PropertyAppraiserConnector

**Priority**: 1 (highest value, easiest implementation)
**File**: `src/theleadedge/sources/property_appraiser.py`

```python
class CollierPAConnector(DataSourceConnector):
    """Downloads and parses Collier County Property Appraiser bulk CSV files.

    Files are downloaded from collierappraiser.com/Main_Data/DataDownloads.html
    and joined on PARCELID.
    """

    DOWNLOAD_URLS = {
        "parcels": "https://www.collierappraiser.com/Main_Data/Parcels.csv",
        "sales": "https://www.collierappraiser.com/Main_Data/Sales.csv",
        "values": "https://www.collierappraiser.com/Main_Data/ValuesHistory.csv",
    }

    async def authenticate(self) -> None:
        """Verify the download URLs are reachable (HEAD request)."""
        ...

    async def fetch(self, since=None, **filters) -> list[dict]:
        """Download CSV files via HTTP GET using httpx.AsyncClient.

        Downloads to a temp directory, reads CSV, returns raw rows.
        Uses streaming download to handle large files without
        loading entire file into memory.
        """
        ...

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Join parcels + sales + values on PARCELID.

        Produces SourceRecord-compatible dicts with:
        - parcel_id, site_address, mailing_address, owner_name
        - last_sale_date, last_sale_price
        - assessed_value, homestead_exempt
        - absentee flag (mailing != site address)
        """
        ...
```

```python
class LeePAConnector(DataSourceConnector):
    """Downloads and parses Lee County Property Appraiser NAL format files.

    Tax roll files are in Florida DOR standard NAL format (fixed-width).
    Sales data is in SDF text format.
    """

    TAX_ROLL_URL = "https://www.leepa.org/Roll/TaxRoll.aspx"
    SALES_URL = "https://www.leepa.org/Roll/SDFTxt.aspx"

    async def fetch(self, since=None, **filters) -> list[dict]:
        """Download NAL ZIP file, extract, parse fixed-width fields."""
        ...

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Parse NAL fixed-width fields into SourceRecord-compatible dicts.

        NAL field layout follows Florida DOR specification:
        - Positions 1-2: County code
        - Positions 3-25: Parcel ID (STRAP)
        - Positions 26-55: Owner name
        - etc.
        """
        ...
```

**Key implementation detail**: The NAL format is fixed-width positional. We need a field layout specification. The Florida Department of Revenue publishes this, but we should also verify against actual Lee County files. The `struct` module or manual string slicing handles fixed-width parsing; no special library needed.

### 6.2 ClerkRecordConnector

**Priority**: 3 (lis pendens), 5 (probate), 6 (divorce)
**File**: `src/theleadedge/sources/clerk_records.py`

```python
class ClerkRecordConnector(DataSourceConnector):
    """Parses Clerk of Court records from Sunshine Law response files.

    The Realtor (or an assistant) submits monthly public records requests
    to Lee County and Collier County clerks. Response files are dropped
    into a configured directory. This connector watches that directory
    and processes new files.

    Supported input formats: CSV, XLSX, XLS
    """

    def __init__(
        self,
        name: str = "clerk_records",
        import_dir: Path = ...,
        record_type: str = "lis_pendens",  # or "probate", "domestic_relations"
    ) -> None:
        ...

    async def authenticate(self) -> None:
        """Verify the import directory exists."""
        ...

    async def fetch(self, since=None, **filters) -> list[dict]:
        """Read CSV/Excel files from the import directory.

        Uses csv module for CSV files, openpyxl for XLSX.
        Looks for files matching pattern: {record_type}_*.csv or .xlsx
        """
        ...

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Normalize clerk records to SourceRecord format.

        Maps common column variations:
        - "Case No" / "Case Number" / "CASE_NO" -> case_number
        - "Filing Date" / "File Date" / "DATE_FILED" -> event_date
        - "Property Address" / "PROP_ADDR" -> street_address
        - "Parcel" / "Parcel ID" / "PARCEL_ID" -> parcel_id

        Flexible header mapping handles inconsistent county formats.
        """
        ...
```

**Important**: Clerk response file formats are not standardized. Each county may deliver data in different column layouts. The connector must support flexible header mapping, similar to how `MLSCsvConnector` handles dual Name/Label headers. A YAML config file (`config/clerk_fields.yaml`) can define multiple column name variations for each internal field.

### 6.3 CodeViolationConnector

**Priority**: 2
**File**: `src/theleadedge/sources/code_violations.py`

```python
class CodeViolationConnector(DataSourceConnector):
    """Parses code enforcement violation data from Sunshine Law responses.

    Similar to ClerkRecordConnector but specific to code enforcement data
    which has different fields (violation type, compliance deadline, etc.).
    """

    async def fetch(self, since=None, **filters) -> list[dict]:
        """Read code violation files from import directory."""
        ...

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Normalize code violation records.

        Key fields: case_number, property_address, parcel_id,
        violation_type, violation_date, status, compliance_deadline
        """
        ...
```

### 6.4 MarketDataConnector

**Priority**: 4
**File**: `src/theleadedge/sources/market_data.py`

```python
class RedfinMarketConnector(DataSourceConnector):
    """Downloads Redfin market data from their public S3 bucket.

    The national ZIP-code-level market tracker file is ~150-200 MB compressed.
    We download, decompress, filter to our 52 SWFLA ZIP codes, and store
    per-ZIP market snapshots.
    """

    S3_URL = (
        "https://redfin-public-data.s3.us-west-2.amazonaws.com/"
        "redfin_market_tracker/zip_code_market_tracker.tsv000.gz"
    )

    def __init__(self, target_zips: list[str]) -> None:
        """Initialize with target ZIP codes from config/market.yaml."""
        super().__init__(name="redfin_market")
        self.target_zips = set(target_zips)

    async def fetch(self, since=None, **filters) -> list[dict]:
        """Download gzipped TSV from S3, stream decompress, filter to target ZIPs.

        Uses httpx streaming response to avoid loading 200MB into memory.
        Decompresses with gzip module as data arrives.
        Filters rows to only target ZIP codes during parsing (not after).
        """
        ...

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Parse TSV fields into MarketSnapshot-compatible dicts.

        Calculates derived metrics:
        - absorption_rate = homes_sold / inventory (if inventory > 0)
        - is_hot = absorption_rate > metro_median_absorption_rate
        """
        ...


class GoogleAlertsConnector(DataSourceConnector):
    """Parses Google Alerts RSS feeds for real estate signals.

    Feed URLs are configured in config/google_alerts.yaml.
    Each alert produces entries that may contain FSBO listings,
    foreclosure notices, or other market signals.
    """

    async def fetch(self, since=None, **filters) -> list[dict]:
        """Fetch and parse RSS feeds using feedparser."""
        ...
```

### 6.5 FSBOConnector

**Priority**: 7
**File**: `src/theleadedge/sources/fsbo.py`

```python
class CraigslistFSBOConnector(DataSourceConnector):
    """Monitors Craigslist Fort Myers real estate RSS for FSBO listings.

    Respects Craigslist's robots.txt and rate limits.
    Uses the standard RSS feed endpoint, not scraping.
    """

    RSS_URL = "https://fortmyers.craigslist.org/search/rea?purveyor=owner&format=rss"

    async def fetch(self, since=None, **filters) -> list[dict]:
        """Fetch RSS feed using httpx, parse with feedparser.

        If `since` is provided, only return entries published after that date.
        """
        ...

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Extract listing data from RSS entries.

        Parses title for price and address.
        Parses description for motivation keywords.
        Extracts coordinates from geo tags if present.
        """
        ...
```

### 6.6 SunbizConnector

**Priority**: 8 (lowest -- enrichment only)
**File**: `src/theleadedge/sources/sunbiz.py`

```python
class SunbizConnector(DataSourceConnector):
    """Downloads Florida LLC records from Sunbiz SFTP or bulk downloads.

    Used to cross-reference LLC names in PA ownership data.
    Identifies out-of-state investors and recently dissolved entities.
    """

    SFTP_HOST = "sftp.floridados.gov"
    # Credentials stored in .env: SUNBIZ_SFTP_USER, SUNBIZ_SFTP_PASSWORD
    BULK_URL = "https://dos.fl.gov/sunbiz/other-services/data-downloads/"

    async def fetch(self, since=None, **filters) -> list[dict]:
        """Download LLC records via SFTP using asyncssh.

        Falls back to bulk HTTP download if SFTP is unavailable.
        """
        ...

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Parse pipe-delimited Sunbiz records.

        Key fields: entity_name, document_number, filing_date,
        status, registered_agent_address, principal_address
        """
        ...
```

---

## 7. Scheduling Configuration

### 7.1 APScheduler Setup

The scheduler runs as a long-lived process alongside or within the main application. Uses APScheduler's `AsyncScheduler` with a SQLite job store for persistence across restarts.

**File**: `src/theleadedge/scheduler.py` [NEW]

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

def create_scheduler(settings: Settings) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    # --- Daily Jobs ---
    scheduler.add_job(
        job_mls_file_watcher,
        CronTrigger(hour=5, minute=0),
        id="mls_csv_watch",
        name="MLS CSV file watcher",
    )
    scheduler.add_job(
        job_full_pipeline,
        CronTrigger(hour=5, minute=30),
        id="full_pipeline",
        name="Import -> Score -> Briefing",
    )

    # --- Weekly Jobs (Monday) ---
    scheduler.add_job(
        job_redfin_download,
        CronTrigger(day_of_week="mon", hour=6, minute=0),
        id="redfin_market",
        name="Redfin market data download",
    )
    scheduler.add_job(
        job_craigslist_fsbo,
        CronTrigger(day_of_week="mon", hour=6, minute=30),
        id="craigslist_fsbo",
        name="Craigslist FSBO RSS scan",
    )
    scheduler.add_job(
        job_google_alerts,
        CronTrigger(day_of_week="mon", hour=6, minute=45),
        id="google_alerts",
        name="Google Alerts RSS scan",
    )

    # --- Monthly Jobs (1st of month) ---
    scheduler.add_job(
        job_collier_pa_download,
        CronTrigger(day=1, hour=4, minute=0),
        id="collier_pa",
        name="Collier County PA bulk download",
    )
    scheduler.add_job(
        job_lee_pa_download,
        CronTrigger(day=1, hour=4, minute=30),
        id="lee_pa",
        name="Lee County PA tax roll download",
    )
    scheduler.add_job(
        job_clerk_records_import,
        CronTrigger(day=1, hour=7, minute=0),
        id="clerk_records",
        name="Process Sunshine Law response files",
    )

    # --- Quarterly Jobs (Jan, Apr, Jul, Oct) ---
    scheduler.add_job(
        job_sunbiz_download,
        CronTrigger(month="1,4,7,10", day=1, hour=3, minute=0),
        id="sunbiz_llc",
        name="Sunbiz LLC records download",
    )

    return scheduler
```

### 7.2 Schedule Summary

| Job | Frequency | Time | Source | Data |
|-----|-----------|------|--------|------|
| MLS CSV file watch | Daily | 5:00 AM | Local filesystem | New CSV files |
| Full pipeline (import+score+brief) | Daily | 5:30 AM | Internal | Score recalc + email |
| Redfin market data | Weekly (Mon) | 6:00 AM | S3 HTTP | ZIP-level market stats |
| Craigslist FSBO | Weekly (Mon) | 6:30 AM | RSS | FSBO listings |
| Google Alerts | Weekly (Mon) | 6:45 AM | RSS | Market signals |
| Collier PA download | Monthly (1st) | 4:00 AM | HTTP | Parcel + sales + values |
| Lee PA download | Monthly (1st) | 4:30 AM | HTTP | Tax roll + sales |
| Clerk records import | Monthly (1st) | 7:00 AM | Local filesystem | Lis pendens, probate, etc. |
| Sunbiz LLC download | Quarterly | 3:00 AM | SFTP | LLC records |

**Time zone**: All times are US Eastern (America/New_York). APScheduler should be configured with `timezone="America/New_York"`.

### 7.3 Job Error Handling

Each job function follows a standard pattern:
1. Log job start with structured logging
2. Run the connector's `sync()` method
3. If sync succeeds, run the record mapper + signal detector
4. Write `SyncLogRow` with results
5. On failure, log error and write failed `SyncLogRow`
6. Never raise exceptions that would crash the scheduler

---

## 8. CLI Extensions

### 8.1 New Commands

Add to `src/theleadedge/main.py`:

```python
# New subparsers in build_parser():

subparsers.add_parser(
    "download-pa",
    help="Download Property Appraiser bulk data (Collier + Lee)",
)
subparsers.add_parser(
    "download-redfin",
    help="Download Redfin market data for SWFLA ZIP codes",
)
subparsers.add_parser(
    "import-public-records",
    help="Import Sunshine Law response files (lis pendens, probate, code violations)",
)
subparsers.add_parser(
    "match-records",
    help="Run address matching on unmatched source records",
)
subparsers.add_parser(
    "scheduler",
    help="Start the APScheduler daemon for automated pipeline execution",
)
subparsers.add_parser(
    "health",
    help="Check connectivity to all data sources",
)
```

### 8.2 Command Handlers

```python
async def cmd_download_pa(settings: Settings) -> int:
    """Download PA data from both counties, import, and match."""
    collier = CollierPAConnector(download_dir=settings.project_root / "data" / "pa_downloads")
    lee = LeePAConnector(download_dir=settings.project_root / "data" / "pa_downloads")

    for connector in [collier, lee]:
        result = await connector.sync()
        if not result.success:
            logger.error("pa_download_failed", source=connector.name, errors=result.errors)
            return 1
        # Run record mapper on fetched records
        # Create/update property records
        # Detect signals
    return 0

async def cmd_download_redfin(settings: Settings) -> int:
    """Download Redfin market data, filter to SWFLA ZIPs, store snapshots."""
    connector = RedfinMarketConnector(target_zips=settings.zip_codes)
    result = await connector.sync()
    if not result.success:
        return 1
    # Store market snapshots
    # Detect neighborhood_hot signals
    return 0

async def cmd_import_public_records(settings: Settings) -> int:
    """Import clerk response files and code enforcement data."""
    import_dir = settings.project_root / "data" / "public_records"
    for record_type in ["lis_pendens", "probate", "domestic_relations", "code_violation"]:
        subdir = import_dir / record_type
        if subdir.exists() and any(subdir.iterdir()):
            connector = ClerkRecordConnector(import_dir=subdir, record_type=record_type)
            result = await connector.sync()
            # Match records, detect signals
    return 0

async def cmd_scheduler(settings: Settings) -> int:
    """Start the APScheduler daemon."""
    scheduler = create_scheduler(settings)
    scheduler.start()
    # Run until interrupted
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
    return 0

async def cmd_health(settings: Settings) -> int:
    """Check all data source connectivity."""
    connectors = [
        CollierPAConnector(...),
        LeePAConnector(...),
        RedfinMarketConnector(target_zips=settings.zip_codes),
        CraigslistFSBOConnector(),
    ]
    all_healthy = True
    for c in connectors:
        healthy = await c.health_check()
        status = "OK" if healthy else "FAIL"
        logger.info("health_check", source=c.name, status=status)
        if not healthy:
            all_healthy = False
    return 0 if all_healthy else 1
```

---

## 9. Python Dependencies

### 9.1 New Dependencies for Phase 2

| Package | Purpose | Version | Source |
|---------|---------|---------|--------|
| `feedparser` | Parse RSS/Atom feeds (Craigslist, Google Alerts) | >=6.0 | PyPI |
| `rapidfuzz` | Fast Levenshtein distance for fuzzy address matching | >=3.6 | PyPI |
| `openpyxl` | Read XLSX files from clerk Sunshine Law responses | >=3.1 | PyPI |
| `apscheduler` | Job scheduling for automated pipeline execution | >=3.10 | PyPI |
| `asyncssh` | SFTP client for Sunbiz downloads (Phase 2.4 only) | >=2.14 | PyPI |

### 9.2 Updated pyproject.toml Dependencies

```toml
dependencies = [
    # --- Existing (Phase 1) ---
    "pydantic>=2.6",
    "pydantic-settings>=2.2",
    "sqlalchemy[asyncio]>=2.0",
    "aiosqlite>=0.20",
    "alembic>=1.13",
    "httpx>=0.27",
    "tenacity>=8.2",
    "jinja2>=3.1",
    "aiosmtplib>=3.0",
    "pyyaml>=6.0",
    "python-dotenv>=1.0",
    "structlog>=24.1",

    # --- New (Phase 2) ---
    "feedparser>=6.0",
    "rapidfuzz>=3.6",
    "openpyxl>=3.1",
    "apscheduler>=3.10",
]

[project.optional-dependencies]
sftp = [
    "asyncssh>=2.14",  # Only needed for Sunbiz SFTP downloads
]
```

### 9.3 Already Available (No New Install)

These capabilities are covered by existing dependencies:

| Need | Covered By |
|------|-----------|
| HTTP downloads (PA data, Redfin) | `httpx` (already installed) |
| Gzip decompression (Redfin TSV) | Python stdlib `gzip` |
| CSV parsing (PA data, clerk data) | Python stdlib `csv` |
| Fixed-width parsing (NAL format) | Python stdlib string slicing |
| ZIP extraction (Lee PA tax roll) | Python stdlib `zipfile` |
| Date parsing | Python stdlib `datetime` |
| Address normalization | `src/theleadedge/utils/address.py` (already exists) |
| Structured logging | `structlog` (already installed) |
| Async database operations | `sqlalchemy[asyncio]` + `aiosqlite` (already installed) |
| Retry with backoff | `tenacity` (already installed) |

---

## 10. What This Unlocks

### 10.1 Dormant Signal Activation

Currently, 12 of 20 signal types are active (all MLS-sourced). Phase 2 activates the remaining 8:

| Signal Type | Points | Activated By | Category |
|-------------|--------|--------------|----------|
| `pre_foreclosure` | 20 | Clerk lis pendens | public_record |
| `probate` | 18 | Clerk probate index | life_event |
| `divorce` | 16 | Clerk domestic relations | life_event |
| `tax_delinquent` | 13 | PA tax roll data | public_record |
| `code_violation` | 12 | Code enforcement data | public_record |
| `vacant_property` | 10 | PA composite analysis | life_event |
| `agent_churn` | 7 | MLS import comparison | market |
| `neighborhood_hot` | 5 | Redfin market data | market |

### 10.2 Stacking Rule Activation

Four of six stacking rules are currently inert because they require signals from public record or life event categories that have no data source. Phase 2 activates them:

**Stacking Rule: `financial_distress` (2.0x multiplier)**
```
Required:  pre_foreclosure + tax_delinquent
Activated: When Clerk lis pendens AND PA tax data are both imported
Effect:    A property with both signals gets:
           (20 + 13) * 2.0 = 66 base points from these signals alone
           Combined with any MLS signals, easily reaches Tier S
```

**Stacking Rule: `life_event_vacant` (2.5x multiplier -- highest)**
```
Required:  probate + absentee_owner + vacant_property
Activated: When Clerk probate AND PA absentee/vacancy data are both imported
Effect:    (18 + 8 + 10) * 2.5 = 90 base points
           The most powerful stacking rule. An inherited vacant property
           with an out-of-state heir is the highest-probability lead type.
```

**Stacking Rule: `tired_landlord` (1.8x multiplier)**
```
Required:  absentee_owner + code_violation
Activated: When Code enforcement AND PA absentee data are both imported
Effect:    (8 + 12) * 1.8 = 36 base points
           A distant owner with code problems is a motivated seller.
```

**Stacking Rule: `divorce_property` (1.6x multiplier)**
```
Required:  divorce + high_dom
Activated: When Clerk domestic relations data is imported
           AND the property is already flagged high_dom from MLS
Effect:    (16 + 11) * 1.6 = 43.2 base points
           Court-ordered sale stuck on market = very motivated.
```

### 10.3 Scoring Impact Scenarios

**Scenario A: Financial Distress Lead (currently invisible)**
```
Before Phase 2:
  Signals: expired_listing (15 pts) + high_dom (11 pts) = 26 pts -> Tier C
  Action: "Monthly touch -- add to nurture campaign"

After Phase 2 (with public record data):
  Signals: expired_listing (15) + high_dom (11) + pre_foreclosure (20) + tax_delinquent (13)
  Stacking: financial_distress 2.0x on pre_foreclosure + tax_delinquent
  Raw: 15 + 11 + (20 + 13) * 2.0 = 92 pts -> Tier S
  Action: "Immediate personal outreach -- phone call + handwritten note"
```

**Scenario B: Inherited Vacant Property (currently invisible)**
```
Before Phase 2:
  Signals: absentee_owner (8 pts) = 8 pts -> Tier D
  Action: "Monitor only -- no active outreach"

After Phase 2:
  Signals: absentee_owner (8) + probate (18) + vacant_property (10)
  Stacking: life_event_vacant 2.5x
  Raw: (8 + 18 + 10) * 2.5 = 90 pts -> Tier S
  Action: "Immediate personal outreach -- phone call + handwritten note"
  (With empathy-first approach per probate outreach guidelines)
```

**Scenario C: Tired Landlord (currently invisible)**
```
Before Phase 2:
  Signals: absentee_owner (8 pts) = 8 pts -> Tier D

After Phase 2:
  Signals: absentee_owner (8) + code_violation (12)
  Stacking: tired_landlord 1.8x
  Raw: (8 + 12) * 1.8 = 36 pts -> Tier C
  Add neighborhood_hot (5): 41 pts -> Tier B
  Action: "Scheduled outreach this week -- add to priority drip"
```

### 10.4 Coverage Matrix

After Phase 2 completion, signal coverage by source:

| Source | Signals Provided | Stacking Rules Enabled |
|--------|-----------------|----------------------|
| MLS CSV (existing) | 12 signals | distressed_seller, failed_sale |
| Property Appraiser | vacant_property, tax_delinquent, absentee_owner (enriched) | tired_landlord, life_event_vacant (partial) |
| Clerk (Lis Pendens) | pre_foreclosure | financial_distress |
| Clerk (Probate) | probate | life_event_vacant |
| Clerk (Divorce) | divorce | divorce_property |
| Code Enforcement | code_violation | tired_landlord |
| Redfin Market Data | neighborhood_hot | (contextual, no stacking rule) |
| MLS Import Comparison | agent_churn | (no stacking rule) |
| Craigslist FSBO | (new lead source) | (separate lead pipeline) |
| Sunbiz LLC | (enrichment only) | (enhances absentee_owner confidence) |

---

## 11. Implementation Phases

### Phase 2.1: Property Appraiser Integration (Weeks 1-3)

**Priority**: Highest. Populates parcel_id on PropertyRow, which is the foundation for all subsequent source matching.

| Task | Effort | Dependencies |
|------|--------|-------------|
| Add PA columns to PropertyRow (Alembic migration) | 2 hrs | None |
| Create SourceRecordRow + MatchQueueRow tables | 3 hrs | None |
| Implement CollierPAConnector (HTTP download + CSV parse) | 8 hrs | New tables |
| Implement LeePAConnector (HTTP download + NAL parse) | 10 hrs | New tables |
| Implement RecordMapper (address matching cascade) | 12 hrs | PA connectors |
| Add `vacant_property` detection rule | 3 hrs | PA data flowing |
| Add `tax_delinquent` detection rule | 2 hrs | PA data flowing |
| Add `agent_churn` detection rule (MLS import comparison) | 3 hrs | None (MLS only) |
| Add `download-pa` and `match-records` CLI commands | 3 hrs | All above |
| Tests for all new code | 8 hrs | All above |
| **Total** | **~54 hrs** | |

**Deliverables**:
- Parcel IDs populated on all matchable properties
- Absentee owner detection enhanced with PA data
- Vacant property signal active
- Tax delinquent signal active (if PA data includes delinquency)
- Agent churn signal active
- Address matching pipeline operational

### Phase 2.2: Code Enforcement + Clerk Lis Pendens (Weeks 4-5)

**Priority**: High. Enables `financial_distress` 2.0x stacking and `tired_landlord` 1.8x stacking.

| Task | Effort | Dependencies |
|------|--------|-------------|
| Create `config/clerk_fields.yaml` (flexible header mapping) | 2 hrs | None |
| Implement CodeViolationConnector | 5 hrs | Phase 2.1 (matcher) |
| Implement ClerkRecordConnector for lis pendens | 5 hrs | Phase 2.1 (matcher) |
| Add `code_violation` detection rule | 2 hrs | CodeViolationConnector |
| Add `pre_foreclosure` detection rule | 2 hrs | ClerkRecordConnector |
| Add `import-public-records` CLI command | 2 hrs | Connectors |
| Submit first Sunshine Law requests to both counties | 1 hr | Template letters |
| Tests | 5 hrs | All above |
| **Total** | **~24 hrs** | |

**Stacking rules activated**: `financial_distress` (2.0x), `tired_landlord` (1.8x)

### Phase 2.3: Redfin Market Data (Week 6)

**Priority**: Medium. Enables `neighborhood_hot` signal and dynamic DOM threshold calibration.

| Task | Effort | Dependencies |
|------|--------|-------------|
| Create MarketSnapshotRow table (Alembic migration) | 1 hr | None |
| Implement RedfinMarketConnector (S3 download, gzip, TSV parse) | 6 hrs | None |
| ZIP code filtering against `config/market.yaml` | 1 hr | Connector |
| Add `neighborhood_hot` detection rule | 3 hrs | Market data flowing |
| Dynamic DOM threshold calibration (replace hardcoded 90-day) | 4 hrs | Market data |
| Add `download-redfin` CLI command | 1 hr | Connector |
| Tests | 4 hrs | All above |
| **Total** | **~20 hrs** | |

### Phase 2.4: Clerk Probate + Divorce (Weeks 7-8)

**Priority**: Medium. Enables `life_event_vacant` 2.5x and `divorce_property` 1.6x stacking.

| Task | Effort | Dependencies |
|------|--------|-------------|
| Extend ClerkRecordConnector for probate parsing | 3 hrs | Phase 2.2 |
| Extend ClerkRecordConnector for domestic relations parsing | 3 hrs | Phase 2.2 |
| Add `probate` detection rule | 2 hrs | Probate data flowing |
| Add `divorce` detection rule | 2 hrs | Divorce data flowing |
| Submit Sunshine Law requests for probate + domestic relations | 1 hr | Template letters |
| Tests | 3 hrs | All above |
| **Total** | **~14 hrs** | |

**Stacking rules activated**: `life_event_vacant` (2.5x), `divorce_property` (1.6x)

### Phase 2.5: FSBO + Google Alerts + Scheduler (Weeks 9-10)

**Priority**: Lower. New lead source (not tied to existing signals) + automation.

| Task | Effort | Dependencies |
|------|--------|-------------|
| Create FSBOListingRow table (Alembic migration) | 1 hr | None |
| Implement CraigslistFSBOConnector (RSS parsing) | 4 hrs | None |
| Implement GoogleAlertsConnector (RSS parsing) | 3 hrs | None |
| Create `config/google_alerts.yaml` (feed URLs) | 1 hr | None |
| Implement scheduler module with APScheduler | 6 hrs | All connectors |
| Add `scheduler` CLI command | 2 hrs | Scheduler |
| Add `health` CLI command | 2 hrs | All connectors |
| Tests | 4 hrs | All above |
| **Total** | **~23 hrs** | |

### Phase 2.6: Sunbiz LLC Enrichment (Week 11, optional)

**Priority**: Lowest. Enrichment only, no direct signal value.

| Task | Effort | Dependencies |
|------|--------|-------------|
| Implement SunbizConnector (SFTP or HTTP bulk download) | 6 hrs | None |
| LLC-to-property cross-reference logic | 4 hrs | PA data (parcel IDs) |
| Enhance absentee_owner confidence with LLC data | 2 hrs | Cross-reference |
| Tests | 3 hrs | All above |
| **Total** | **~15 hrs** | |

### Phase 2 Total Effort Estimate

| Phase | Hours | Cumulative |
|-------|-------|------------|
| 2.1: Property Appraiser | 54 | 54 |
| 2.2: Code + Lis Pendens | 24 | 78 |
| 2.3: Redfin Market Data | 20 | 98 |
| 2.4: Probate + Divorce | 14 | 112 |
| 2.5: FSBO + Scheduler | 23 | 135 |
| 2.6: Sunbiz (optional) | 15 | 150 |
| **Total** | **~150 hrs** | |

---

## 12. Cost Analysis

### 12.1 Free Sources (Total: $0/month)

| Source | Cost | Notes |
|--------|------|-------|
| Collier County PA bulk data | Free | Public records, HTTP download |
| Lee County PA tax roll + sales | Free | Public records, HTTP download |
| Clerk of Court (Sunshine Law) | ~$0 | Electronic duplication cost only (usually waived) |
| Code Enforcement (Sunshine Law) | ~$0 | Same as above |
| Redfin Data Center | Free | Public S3 bucket, no account needed |
| Craigslist RSS | Free | Standard RSS, no API key |
| Google Alerts RSS | Free | Google account required (one-time setup) |
| Florida Sunbiz SFTP | Free | Public SFTP with published credentials |

### 12.2 Optional Paid Supplement

| Source | Cost | Value |
|--------|------|-------|
| ForeclosureAuctionData.com (single county) | $29/month | Structured foreclosure data, saves Sunshine Law processing time |
| ForeclosureAuctionData.com (both counties) | $99/month | Same, both Lee + Collier |

**Recommendation**: Start with free Sunshine Law approach. If the manual request/response cycle proves burdensome (more than 2 hours/month of admin time), the $99/month service pays for itself in time savings.

### 12.3 Infrastructure Costs

| Item | Cost | Notes |
|------|------|-------|
| Compute | $0 | Runs on existing development machine |
| Storage | $0 | SQLite, local filesystem |
| Network | $0 | Standard ISP, no cloud services |

**Total Phase 2 operating cost: $0/month** (or $99/month with optional ForeclosureAuctionData.com).

---

## 13. Risk Assessment

### 13.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PA download URLs change | Medium | Low | Health check detects; update URLs in config |
| NAL format varies from DOR spec | Low | Medium | Validate against actual Lee County files before coding |
| Clerk response formats inconsistent | High | Medium | Flexible header mapping in YAML config |
| Redfin changes S3 URL or format | Low | Medium | Health check detects; Redfin Data Center page documents changes |
| Craigslist blocks RSS access | Low | Low | FSBO is supplementary; alternative: manual monitoring |
| Fuzzy matching produces false positives | Medium | High | Require ZIP match as guard rail; queue low-confidence matches for review |
| Large PA files slow down import | Medium | Low | Stream processing; filter to target ZIPs during parse |

### 13.2 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Sunshine Law requests not honored | Low | High | Florida statute requires response; escalate if needed |
| Clerk response takes >30 days | Medium | Medium | Budget 30-day lead time; submit requests early |
| Standing requests denied | Medium | Low | Calendar monthly manual submissions |
| Data quality issues in clerk data | High | Medium | Validation rules + manual review queue |

### 13.3 Compliance Risks

| Risk | Mitigation |
|------|------------|
| PII exposure in logs | Existing structlog rules apply; extend to new connectors; NEVER log addresses, names, phones |
| Public records misuse | Florida Sunshine Law explicitly permits this use; data is public record |
| Fair Housing violation | Scoring algorithm is property-based, never demographic; no protected class data ingested |
| MLS ToS conflict | Public record sources are independent of MLS; no MLS ToS applies to PA or clerk data |

---

## 14. File Manifest

### 14.1 New Files to Create

```
src/theleadedge/
  models/
    source_record.py               # SourceRecord Pydantic model
  sources/
    property_appraiser.py          # CollierPAConnector + LeePAConnector
    clerk_records.py               # ClerkRecordConnector
    code_violations.py             # CodeViolationConnector
    market_data.py                 # RedfinMarketConnector + GoogleAlertsConnector
    fsbo.py                        # CraigslistFSBOConnector
    sunbiz.py                      # SunbizConnector
  pipelines/
    match.py                       # RecordMapper (address matching cascade)
    public_records.py              # PublicRecordPipeline (orchestrates source -> match -> signal)
  scheduler.py                     # APScheduler configuration and job functions
  storage/
    (Alembic migration files)      # Schema changes

config/
  clerk_fields.yaml                # Flexible header mapping for clerk response files
  google_alerts.yaml               # Google Alerts RSS feed URLs
  pa_fields.yaml                   # Field mapping for PA data (Collier CSV, Lee NAL)

tests/
  test_property_appraiser.py       # PA connector tests
  test_clerk_records.py            # Clerk connector tests
  test_code_violations.py          # Code violation connector tests
  test_market_data.py              # Redfin connector tests
  test_fsbo.py                     # FSBO connector tests
  test_record_mapper.py            # Address matching tests
  test_public_record_signals.py    # New signal detection rule tests
  test_scheduler.py                # Scheduler configuration tests

data/
  pa_downloads/                    # PA bulk file storage (gitignored)
  public_records/                  # Sunshine Law response files (gitignored)
    lis_pendens/
    probate/
    domestic_relations/
    code_violations/
  market_data/                     # Redfin downloads (gitignored)
```

### 14.2 Existing Files to Modify

| File | Changes |
|------|---------|
| `src/theleadedge/storage/database.py` | Add PA columns to PropertyRow; add SourceRecordRow, MatchQueueRow, MarketSnapshotRow, FSBOListingRow tables |
| `src/theleadedge/storage/repositories.py` | Add SourceRecordRepo, MatchQueueRepo, MarketSnapshotRepo, FSBOListingRepo |
| `src/theleadedge/pipelines/detect.py` | Add 8 new detection rules for public record signals |
| `src/theleadedge/main.py` | Add 5 new CLI commands (download-pa, download-redfin, import-public-records, match-records, scheduler, health) |
| `src/theleadedge/config/__init__.py` | Add PA download directory, public records directory, scheduler settings |
| `pyproject.toml` | Add new dependencies (feedparser, rapidfuzz, openpyxl, apscheduler) |
| `.gitignore` | Add data/pa_downloads/, data/public_records/, data/market_data/ |

### 14.3 Existing Files Referenced (No Changes)

| File | Role |
|------|------|
| `src/theleadedge/sources/base.py` | DataSourceConnector ABC -- all new connectors extend this |
| `src/theleadedge/sources/mls_csv.py` | Reference implementation for connector pattern |
| `src/theleadedge/models/signal.py` | SignalCreate model used by new detection rules |
| `src/theleadedge/models/enums.py` | SignalCategory, DecayType enums used by new signals |
| `src/theleadedge/scoring/config_loader.py` | ScoringConfig loads new signal types from YAML |
| `src/theleadedge/scoring/engine.py` | ScoringEngine handles new signals without code changes |
| `src/theleadedge/scoring/stacking.py` | Stacking logic handles new combinations without code changes |
| `src/theleadedge/utils/address.py` | normalize_address() and make_address_key() used by RecordMapper |
| `config/scoring_weights.yaml` | Already has all 20 signal types + 6 stacking rules configured |
| `config/market.yaml` | ZIP codes used to filter Redfin data |

---

## Appendix A: Data Directory Structure

```
data/                              # Root data directory (gitignored)
  mls_imports/                     # MLS CSV exports (Phase 1, existing)
  processed/                       # Processed MLS files (Phase 1, existing)
  pa_downloads/                    # Property Appraiser bulk files
    collier/
      parcels_YYYYMMDD.csv
      sales_YYYYMMDD.csv
      values_YYYYMMDD.csv
    lee/
      taxroll_YYYY.zip
      sdf_YYYYMMDD.txt
  public_records/                  # Sunshine Law response files
    lis_pendens/
      lee_lis_pendens_YYYYMM.csv
      collier_lis_pendens_YYYYMM.csv
    probate/
      lee_probate_YYYYMM.csv
      collier_probate_YYYYMM.csv
    domestic_relations/
      lee_domestic_YYYYMM.csv
      collier_domestic_YYYYMM.csv
    code_violations/
      lee_code_violations_YYYYQQ.csv
      collier_code_violations_YYYYQQ.csv
  market_data/                     # Redfin market downloads
    zip_code_market_tracker_YYYYMMDD.tsv
```

## Appendix B: Sunshine Law Request Templates

Full template letters for all four request types (lis pendens, probate, domestic relations, code violations) are documented in `Research/clerk_of_court_automation_research.md`. The templates include:

- Statutory citation (F.S. 119.01 et seq.)
- Specific records requested with date ranges
- Preferred electronic format (CSV or Excel)
- Specific fields requested
- Electronic delivery request
- Standing/recurring request inquiry

## Appendix C: NAL File Format Reference

The Florida Department of Revenue NAL (Name-Address-Legal) file format is a fixed-width positional format used by all 67 Florida counties for tax roll data. Key field positions for Lee County:

| Positions | Length | Field | Description |
|-----------|--------|-------|-------------|
| 1-2 | 2 | COUNTY | County code (36 = Lee) |
| 3-25 | 23 | STRAP | Parcel ID |
| 26-55 | 30 | OWNER_1 | Owner name line 1 |
| 56-85 | 30 | OWNER_2 | Owner name line 2 |
| 86-115 | 30 | MAIL_ADDR_1 | Mailing address line 1 |
| 116-145 | 30 | MAIL_ADDR_2 | Mailing address line 2 |
| 146-175 | 30 | MAIL_CITY | Mailing city |
| 176-177 | 2 | MAIL_STATE | Mailing state |
| 178-186 | 9 | MAIL_ZIP | Mailing ZIP |
| 187-216 | 30 | SITE_ADDR | Site (property) address |
| 217-246 | 30 | SITE_CITY | Site city |
| 247-248 | 2 | SITE_ZIP_PREFIX | Site ZIP prefix |
| 249-253 | 5 | SITE_ZIP | Site ZIP code |
| 254-257 | 4 | USE_CODE | Property use code |
| 258-269 | 12 | JUST_VALUE | Just (market) value |
| 270-281 | 12 | ASSESSED_VALUE | Assessed value |
| 282-293 | 12 | TAXABLE_VALUE | Taxable value |
| 294-297 | 4 | EXEMPT_CODE | Exemption code(s) |

**Note**: Actual field positions must be verified against the downloaded file. The DOR specification may differ slightly from the above. Parse a sample file and validate before relying on these positions in production code.
