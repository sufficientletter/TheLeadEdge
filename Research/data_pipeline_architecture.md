# Data Pipeline Architecture Research

> **Project**: LeadFinder — Real Estate Lead Generation Dashboard
> **Created**: 2026-02-28
> **Purpose**: Backend architecture for data ingestion, scoring, storage, and serving

---

## 1. Data Pipeline Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                             │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ MLS/RESO│  │ ATTOM API│  │ County   │  │ REDX/Batch  │  │
│  │ Web API │  │          │  │ Records  │  │ Leads       │  │
│  └────┬────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘  │
└───────┼────────────┼────────────┼────────────────┼──────────┘
        │            │            │                │
        ▼            ▼            ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  APScheduler (Async)                                │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │    │
│  │  │MLS Sync  │ │Property  │ │Public Rec│ │Skip    │ │    │
│  │  │Daily 6AM │ │Enrichment│ │Weekly    │ │Trace   │ │    │
│  │  │          │ │On-demand │ │Mondays   │ │On-lead │ │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Data Cleaning │  │ Geocoding    │  │ Signal Detection │  │
│  │ & Validation  │  │ & Mapping    │  │ & Extraction     │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │             │
│         ▼                 ▼                    ▼             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              LEAD SCORING ENGINE                     │    │
│  │  Signal Weights → Score Calculation → Tier Assignment│   │
│  │  Urgency Decay → Freshness Bonus → Final Score       │   │
│  └─────────────────────────┬───────────────────────────┘    │
└─────────────────────────────┼───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SQLite / PostgreSQL                      │   │
│  │  Properties | Leads | Signals | Scores | Activities  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │ NiceGUI  │  │ REST API     │  │ Notifications         │ │
│  │ Dashboard│  │ (FastAPI)    │  │ (Email/Push)          │ │
│  └──────────┘  └──────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 ETL Patterns for Real Estate Data

**Extract**:
- MLS: RESO Web API with OData queries, or CSV exports from saved searches
- Property Data: ATTOM API batch requests (up to 100 properties per call)
- Public Records: County website scraping or aggregator APIs (PropertyRadar, BatchData)
- Skip Tracing: BatchLeads API on-demand when new leads detected

**Transform**:
- Address standardization (USPS format: 123 MAIN ST, PHOENIX, AZ 85281)
- Geocoding (address → lat/lng for map display)
- Data deduplication (same property from multiple sources)
- Signal extraction (detect patterns like "3+ price reductions")
- Score calculation (apply scoring model to all signals)

**Load**:
- Upsert properties (insert or update on address match)
- Append signals with timestamps (never delete — historical record)
- Update current scores, archive previous scores for trend tracking
- Trigger notifications for significant score changes

### 1.3 Scheduling Strategy

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

# Daily jobs
scheduler.add_job(sync_mls_data,       CronTrigger(hour=6, minute=0))   # 6:00 AM
scheduler.add_job(generate_briefing,    CronTrigger(hour=6, minute=30))  # 6:30 AM
scheduler.add_job(recalculate_scores,   CronTrigger(hour=6, minute=15))  # 6:15 AM
scheduler.add_job(check_score_changes,  CronTrigger(hour=6, minute=20))  # 6:20 AM

# Weekly jobs
scheduler.add_job(sync_public_records,  CronTrigger(day_of_week='mon', hour=5))
scheduler.add_job(sync_county_filings,  CronTrigger(day_of_week='wed', hour=5))

# Periodic jobs
scheduler.add_job(apply_urgency_decay,  CronTrigger(hour='*/6'))  # Every 6 hours
scheduler.add_job(geocode_new_leads,    CronTrigger(minute='*/30'))  # Every 30 min
scheduler.add_job(health_check,         CronTrigger(minute='*/5'))  # Every 5 min

# Monthly jobs
scheduler.add_job(sync_tax_records,     CronTrigger(day=1, hour=4))
scheduler.add_job(generate_monthly_report, CronTrigger(day=1, hour=7))
```

### 1.4 Data Freshness Requirements

| Data Source | Freshness Needed | Sync Frequency | Why |
|-------------|-----------------|----------------|-----|
| MLS Expireds | Same-day | Daily at 6 AM | First-mover advantage on expireds |
| MLS Price Changes | Same-day | Daily at 6 AM | Detect reduction patterns quickly |
| MLS Status Changes | Same-day | Daily at 6 AM | Catch withdrawals, back-on-market |
| Pre-Foreclosure | Within 1 week | Weekly (Monday) | NODs are filed periodically |
| Probate Filings | Within 1 week | Weekly | Court dockets update weekly |
| Tax Delinquency | Within 1 month | Monthly | Published quarterly/annually |
| Property Enrichment | On first detection | On-demand | Enrich when lead first created |
| Skip Tracing | On first detection | On-demand | Get owner contact when needed |
| Geocoding | Once per property | On insert | Only needs to happen once |
| Score Recalculation | Daily + on signal | Daily + event-triggered | Keep scores current |

### 1.5 Error Handling & Retry

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
)
async def fetch_mls_data(query: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{MLS_BASE_URL}/Property?$filter={query}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return response.json()

# Error tracking
class PipelineHealthTracker:
    """Track success/failure rates for each data source"""

    async def record_sync(self, source: str, success: bool, records: int, error: str = None):
        await db.execute(
            """INSERT INTO sync_log (source, success, record_count, error, timestamp)
               VALUES (?, ?, ?, ?, ?)""",
            (source, success, records, error, datetime.utcnow())
        )

    async def get_health_summary(self) -> dict:
        """Returns last 24hr success rate per source for dashboard health widget"""
        ...
```

---

## 2. Database Design

### 2.1 Core Schema

```sql
-- Properties: The central entity
CREATE TABLE properties (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    address         TEXT NOT NULL,
    address_normalized TEXT NOT NULL,  -- Standardized USPS format
    city            TEXT NOT NULL,
    state           TEXT NOT NULL DEFAULT 'AZ',
    zip_code        TEXT NOT NULL,
    county          TEXT,
    latitude        REAL,
    longitude       REAL,

    -- Property details
    bedrooms        INTEGER,
    bathrooms       REAL,
    sqft            INTEGER,
    lot_sqft        INTEGER,
    year_built      INTEGER,
    property_type   TEXT,  -- SFR, Condo, Townhouse, Multi

    -- Valuation
    list_price      INTEGER,
    original_list_price INTEGER,
    estimated_value INTEGER,
    estimated_equity INTEGER,
    last_sold_price INTEGER,
    last_sold_date  DATE,

    -- MLS info
    mls_number      TEXT UNIQUE,
    mls_status      TEXT,  -- Active, Expired, Withdrawn, Pending, Sold
    days_on_market  INTEGER,
    list_date       DATE,
    expiration_date DATE,
    listing_agent   TEXT,
    listing_office  TEXT,

    -- Owner info
    owner_name      TEXT,
    owner_phone     TEXT,
    owner_email     TEXT,
    owner_address   TEXT,
    is_absentee     BOOLEAN DEFAULT FALSE,
    is_corporate    BOOLEAN DEFAULT FALSE,
    ownership_years REAL,

    -- Metadata
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_source     TEXT,  -- MLS, ATTOM, Manual

    UNIQUE(address_normalized, zip_code)
);

-- Leads: A property becomes a lead when it has signals
CREATE TABLE leads (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id     INTEGER NOT NULL REFERENCES properties(id),

    -- Scoring
    current_score   REAL NOT NULL DEFAULT 0,
    tier            TEXT NOT NULL DEFAULT 'D',  -- S, A, B, C, D
    signal_count    INTEGER DEFAULT 0,

    -- Status tracking
    status          TEXT DEFAULT 'new',  -- new, contacted, meeting, listing, closed, archived
    is_active       BOOLEAN DEFAULT TRUE,
    priority_rank   INTEGER,

    -- Engagement
    contacted_at    DATETIME,
    contacted_by    TEXT,  -- phone, email, mail, door
    response        TEXT,  -- interested, not_interested, no_answer, callback
    notes           TEXT,

    -- CRM sync
    crm_id          TEXT,  -- Follow Up Boss person ID
    crm_synced_at   DATETIME,

    -- Metadata
    detected_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    scored_at       DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(property_id)
);

-- Signals: Individual indicators of motivation (append-only)
CREATE TABLE signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id         INTEGER NOT NULL REFERENCES leads(id),
    property_id     INTEGER NOT NULL REFERENCES properties(id),

    signal_type     TEXT NOT NULL,     -- expired, pre_foreclosure, price_reduction, etc.
    signal_category TEXT NOT NULL,     -- mls, public_record, life_event, market, digital
    points          REAL NOT NULL,     -- Points contributed to score
    weight          REAL DEFAULT 1.0,  -- Configurable weight multiplier

    -- Signal details
    description     TEXT,              -- Human-readable: "3rd price reduction: $425K → $379K"
    source          TEXT,              -- Where detected: MLS, County Recorder, ATTOM
    source_ref      TEXT,              -- Reference ID from source system
    raw_data        TEXT,              -- JSON blob of original data

    -- Timing
    detected_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_date      DATE,              -- When the actual event occurred
    expires_at      DATETIME,          -- When this signal stops contributing to score
    decay_type      TEXT DEFAULT 'linear',  -- linear, exponential, step

    is_active       BOOLEAN DEFAULT TRUE,

    UNIQUE(lead_id, signal_type, event_date)
);

-- Score History: Track score changes over time (append-only)
CREATE TABLE score_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id         INTEGER NOT NULL REFERENCES leads(id),
    score           REAL NOT NULL,
    tier            TEXT NOT NULL,
    signal_count    INTEGER,
    change_reason   TEXT,              -- "New signal: price_reduction", "Urgency decay"
    calculated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Price History: Track MLS price changes
CREATE TABLE price_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id     INTEGER NOT NULL REFERENCES properties(id),
    price           INTEGER NOT NULL,
    price_change    INTEGER,           -- Delta from previous price
    change_pct      REAL,              -- Percentage change
    change_date     DATE NOT NULL,
    source          TEXT DEFAULT 'MLS',

    UNIQUE(property_id, change_date, price)
);

-- Activities: All actions taken on leads
CREATE TABLE activities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id         INTEGER NOT NULL REFERENCES leads(id),
    activity_type   TEXT NOT NULL,      -- call, email, cma_sent, note, status_change, snoozed
    description     TEXT,
    outcome         TEXT,               -- answered, voicemail, email_opened, meeting_set
    performed_by    TEXT DEFAULT 'sarah',
    performed_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sync Log: Track data pipeline health
CREATE TABLE sync_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT NOT NULL,      -- mls, attom, county, batch_leads
    job_type        TEXT NOT NULL,      -- full_sync, incremental, on_demand
    success         BOOLEAN NOT NULL,
    records_fetched INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    error_message   TEXT,
    duration_ms     INTEGER,
    started_at      DATETIME,
    completed_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Signal Config: Adjustable scoring weights
CREATE TABLE signal_config (
    signal_type     TEXT PRIMARY KEY,
    category        TEXT NOT NULL,
    base_points     REAL NOT NULL,
    weight          REAL DEFAULT 1.0,   -- Admin-adjustable multiplier
    decay_type      TEXT DEFAULT 'linear',
    decay_rate      REAL DEFAULT 0.5,   -- Points lost per week
    description     TEXT,
    is_active       BOOLEAN DEFAULT TRUE
);

-- Indexes for common queries
CREATE INDEX idx_leads_score ON leads(current_score DESC) WHERE is_active = TRUE;
CREATE INDEX idx_leads_tier ON leads(tier) WHERE is_active = TRUE;
CREATE INDEX idx_leads_status ON leads(status) WHERE is_active = TRUE;
CREATE INDEX idx_signals_lead ON signals(lead_id) WHERE is_active = TRUE;
CREATE INDEX idx_signals_type ON signals(signal_type);
CREATE INDEX idx_properties_zip ON properties(zip_code);
CREATE INDEX idx_properties_geo ON properties(latitude, longitude);
CREATE INDEX idx_properties_mls ON properties(mls_number);
CREATE INDEX idx_score_history_lead ON score_history(lead_id, calculated_at DESC);
CREATE INDEX idx_price_history_prop ON price_history(property_id, change_date DESC);
CREATE INDEX idx_activities_lead ON activities(lead_id, performed_at DESC);

-- Full-text search for property lookups
CREATE VIRTUAL TABLE properties_fts USING fts5(
    address, city, owner_name, mls_number,
    content='properties', content_rowid='id'
);
```

### 2.2 SQLite vs PostgreSQL vs DuckDB

| Feature | SQLite | PostgreSQL | DuckDB |
|---------|--------|-----------|--------|
| **Setup** | Zero config, single file | Server install required | Single file, like SQLite |
| **Concurrency** | Single writer, multiple readers | Full MVCC concurrency | Analytical queries only |
| **Performance** | Great for <100K rows | Great at any scale | Best for analytics/OLAP |
| **FTS** | FTS5 (good enough) | tsvector (more powerful) | Not designed for FTS |
| **Geospatial** | Spatialite extension | PostGIS (industry standard) | Limited |
| **JSON** | JSON functions available | JSONB (excellent) | Native JSON support |
| **Backup** | Copy the file | pg_dump / streaming replication | Copy the file |
| **Cost** | Free, zero ops | Free, but needs server | Free, zero ops |
| **Best For** | Start here, <50K leads | Scale to, production | Analytics queries |

**Recommendation**: Start with SQLite. Migrate to PostgreSQL when you need:
- Multiple concurrent users
- PostGIS geospatial queries
- Full-text search beyond FTS5 capabilities
- Scheduled backups and replication

### 2.3 SQLModel ORM Layer

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date
from typing import Optional
from enum import Enum

class Tier(str, Enum):
    S = "S"  # Hot (80-100)
    A = "A"  # High (60-79)
    B = "B"  # Warm (40-59)
    C = "C"  # Nurture (20-39)
    D = "D"  # Watch (0-19)

class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    MEETING = "meeting"
    LISTING = "listing"
    CLOSED = "closed"
    ARCHIVED = "archived"

class Property(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    address: str
    address_normalized: str = Field(index=True)
    city: str
    state: str = "AZ"
    zip_code: str = Field(index=True)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    sqft: Optional[int] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None

    list_price: Optional[int] = None
    original_list_price: Optional[int] = None
    estimated_value: Optional[int] = None
    mls_number: Optional[str] = Field(default=None, unique=True)
    mls_status: Optional[str] = None
    days_on_market: Optional[int] = None

    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    is_absentee: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id", unique=True)
    current_score: float = 0
    tier: Tier = Tier.D
    signal_count: int = 0
    status: LeadStatus = LeadStatus.NEW
    is_active: bool = True
    detected_at: datetime = Field(default_factory=datetime.utcnow)

class Signal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id")
    property_id: int = Field(foreign_key="property.id")
    signal_type: str
    signal_category: str  # mls, public_record, life_event, market, digital
    points: float
    description: Optional[str] = None
    source: Optional[str] = None
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    event_date: Optional[date] = None
    decay_type: str = "linear"
    is_active: bool = True
```

---

## 3. API Integration Patterns

### 3.1 RESO Web API (MLS Standard)

The Real Estate Standards Organization (RESO) Web API is the modern standard for MLS data access. Based on OData v4.

**Authentication**: OAuth 2.0 (client credentials or authorization code flow)

```python
import httpx

class ResoClient:
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    async def authenticate(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "api",
                }
            )
            self.access_token = response.json()["access_token"]

    async def get_expired_listings(self, since_date: str) -> list:
        """Fetch recently expired listings"""
        query = (
            f"StandardStatus eq 'Expired' and "
            f"StatusChangeTimestamp gt {since_date}T00:00:00Z"
        )
        return await self._query("Property", query, orderby="StatusChangeTimestamp desc")

    async def get_price_reductions(self, min_reductions: int = 3) -> list:
        """Fetch active listings with multiple price reductions"""
        query = (
            f"StandardStatus eq 'Active' and "
            f"PriceChangeTimestamp gt null"
        )
        results = await self._query("Property", query)
        # Filter for multiple reductions in post-processing
        return [r for r in results if self._count_reductions(r) >= min_reductions]

    async def get_high_dom(self, min_days: int = 90) -> list:
        """Fetch active listings over DOM threshold"""
        query = (
            f"StandardStatus eq 'Active' and "
            f"DaysOnMarket ge {min_days}"
        )
        return await self._query("Property", query, orderby="DaysOnMarket desc")

    async def get_withdrawn_relisted(self) -> list:
        """Fetch listings that were withdrawn and relisted (agent change)"""
        query = (
            f"StandardStatus eq 'Active' and "
            f"CumulativeDaysOnMarket gt DaysOnMarket"  # CDOM > DOM = reset
        )
        return await self._query("Property", query)

    async def _query(self, resource: str, filter_str: str,
                     select: str = None, orderby: str = None,
                     top: int = 200, skip: int = 0) -> list:
        """Execute OData query with pagination"""
        params = {"$filter": filter_str, "$top": top, "$skip": skip}
        if select:
            params["$select"] = select
        if orderby:
            params["$orderby"] = orderby

        all_results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                response = await client.get(
                    f"{self.base_url}/{resource}",
                    params=params,
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("value", [])
                all_results.extend(results)

                # Check for next page
                next_link = data.get("@odata.nextLink")
                if not next_link or len(results) < top:
                    break
                params["$skip"] += top

        return all_results
```

**Key RESO Fields for Lead Scoring**:

| Field | Type | Use |
|-------|------|-----|
| StandardStatus | Enum | Active, Expired, Withdrawn, Pending, Sold |
| DaysOnMarket | Integer | DOM threshold detection |
| CumulativeDaysOnMarket | Integer | Detect CDOM resets (agent changes) |
| ListPrice | Decimal | Current asking price |
| OriginalListPrice | Decimal | Calculate total price reduction |
| PriceChangeTimestamp | DateTime | Track reduction velocity |
| StatusChangeTimestamp | DateTime | When status last changed |
| ListAgentKey | String | Track agent performance |
| ListOfficeName | String | Identify flat-fee/discount brokerages |
| PropertySubType | Enum | Filter by property type |
| PostalCode | String | Geographic targeting |

### 3.2 ATTOM API (Property Data Enrichment)

```python
class AttomClient:
    BASE_URL = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_property_detail(self, address: str, zip_code: str) -> dict:
        """Full property details including owner, valuation, tax"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/property/detail",
                params={"address1": address, "address2": zip_code},
                headers={"apikey": self.api_key, "Accept": "application/json"}
            )
            return response.json()

    async def get_avm(self, address: str, zip_code: str) -> dict:
        """Automated Valuation Model — estimated value + equity"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/valuation/homeequity",
                params={"address1": address, "address2": zip_code},
                headers={"apikey": self.api_key}
            )
            return response.json()

    async def get_preforeclosure(self, zip_code: str) -> list:
        """Pre-foreclosure filings by ZIP code"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/property/preforeclosure",
                params={"postalcode": zip_code, "pagesize": 100},
                headers={"apikey": self.api_key}
            )
            return response.json().get("property", [])
```

### 3.3 Geocoding

```python
from functools import lru_cache

class GeocodingService:
    """Free geocoding via Census Bureau or Nominatim"""

    CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

    async def geocode(self, address: str) -> tuple[float, float] | None:
        """Returns (latitude, longitude) or None"""
        # Try cache first
        cached = await self._get_cached(address)
        if cached:
            return cached

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.CENSUS_URL, params={
                "address": address,
                "benchmark": "Public_AR_Current",
                "format": "json"
            })
            data = response.json()
            matches = data.get("result", {}).get("addressMatches", [])
            if matches:
                coords = matches[0]["coordinates"]
                result = (coords["y"], coords["x"])  # lat, lng
                await self._cache_result(address, result)
                return result
        return None
```

---

## 4. Lead Scoring Engine Architecture

### 4.1 Scoring Engine Implementation

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
import math

@dataclass
class SignalWeight:
    signal_type: str
    category: str
    base_points: float
    decay_type: str  # linear, exponential, step
    decay_rate: float  # points lost per week (linear) or half-life in days (exponential)

# Default signal weights (admin-configurable via signal_config table)
DEFAULT_WEIGHTS = {
    # MLS Signals
    "expired_listing":       SignalWeight("expired_listing", "mls", 15, "exponential", 14),
    "price_reduction":       SignalWeight("price_reduction", "mls", 4, "linear", 1),  # Per reduction
    "price_reduction_3plus": SignalWeight("price_reduction_3plus", "mls", 12, "linear", 2),
    "high_dom_90":           SignalWeight("high_dom_90", "mls", 8, "linear", 0.5),
    "high_dom_120":          SignalWeight("high_dom_120", "mls", 10, "linear", 0.5),
    "high_dom_180":          SignalWeight("high_dom_180", "mls", 12, "linear", 0.5),
    "withdrawn_relisted":    SignalWeight("withdrawn_relisted", "mls", 10, "linear", 2),
    "agent_change":          SignalWeight("agent_change", "mls", 8, "linear", 1),
    "fsbo_expired":          SignalWeight("fsbo_expired", "mls", 12, "exponential", 14),

    # Public Record Signals
    "pre_foreclosure":       SignalWeight("pre_foreclosure", "public_record", 20, "step", 0),
    "probate":               SignalWeight("probate", "public_record", 18, "linear", 0.5),
    "divorce":               SignalWeight("divorce", "public_record", 17, "linear", 1),
    "tax_delinquent":        SignalWeight("tax_delinquent", "public_record", 10, "linear", 0.3),
    "code_violation":        SignalWeight("code_violation", "public_record", 8, "linear", 0.3),
    "absentee_owner":        SignalWeight("absentee_owner", "public_record", 8, "linear", 0.1),
    "long_term_owner":       SignalWeight("long_term_owner", "public_record", 5, "linear", 0.05),
    "vacant_property":       SignalWeight("vacant_property", "public_record", 6, "linear", 0.2),

    # Life Event Signals
    "job_transfer":          SignalWeight("job_transfer", "life_event", 12, "linear", 2),
    "retirement":            SignalWeight("retirement", "life_event", 8, "linear", 0.5),

    # Market Signals
    "neighborhood_hot":      SignalWeight("neighborhood_hot", "market", 5, "linear", 0.3),
    "comp_gap":              SignalWeight("comp_gap", "market", 6, "linear", 0.5),
}


class ScoringEngine:
    """Calculate lead scores from stacked signals with urgency decay"""

    def __init__(self, weights: dict[str, SignalWeight] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def calculate_score(self, signals: list[Signal]) -> tuple[float, str]:
        """
        Returns (score, tier) where score is 0-100 and tier is S/A/B/C/D
        """
        total = 0.0
        now = datetime.utcnow()

        for signal in signals:
            if not signal.is_active:
                continue

            weight = self.weights.get(signal.signal_type)
            if not weight:
                continue

            # Calculate decayed points
            age_days = (now - signal.detected_at).days
            decayed_points = self._apply_decay(
                weight.base_points * weight.decay_rate if weight.decay_type == 'step' else weight.base_points,
                age_days,
                weight.decay_type,
                weight.decay_rate
            )

            # Freshness bonus: 1.5x for signals detected within 4 hours
            age_hours = (now - signal.detected_at).total_seconds() / 3600
            if age_hours <= 4:
                decayed_points *= 1.5

            total += max(0, decayed_points)

        # Cap at 100
        score = min(100, total)

        # Assign tier
        tier = self._score_to_tier(score)

        return score, tier

    def _apply_decay(self, base_points: float, age_days: int,
                     decay_type: str, decay_rate: float) -> float:
        if decay_type == "linear":
            # Lose decay_rate points per week
            return base_points - (decay_rate * age_days / 7)

        elif decay_type == "exponential":
            # Half-life decay (decay_rate = half-life in days)
            if decay_rate <= 0:
                return base_points
            return base_points * math.exp(-0.693 * age_days / decay_rate)

        elif decay_type == "step":
            # Full value until deadline, then cliff to zero
            # For foreclosure: full value until auction date
            return base_points  # Step decay handled by signal expiration

        return base_points

    def _score_to_tier(self, score: float) -> str:
        if score >= 80:
            return "S"
        elif score >= 60:
            return "A"
        elif score >= 40:
            return "B"
        elif score >= 20:
            return "C"
        else:
            return "D"
```

### 4.2 Score Change Detection

```python
class ScoreChangeDetector:
    """Detect meaningful score changes and trigger notifications"""

    TIER_CHANGE_THRESHOLD = 1  # Any tier change is significant
    SCORE_CHANGE_THRESHOLD = 10  # Score change of 10+ points is notable

    async def detect_changes(self, lead: Lead, new_score: float, new_tier: str):
        """Compare new score with previous and trigger appropriate action"""
        old_score = lead.current_score
        old_tier = lead.tier

        changes = []

        # Tier promotion (more important than demotion)
        if self._tier_rank(new_tier) > self._tier_rank(old_tier):
            changes.append({
                "type": "tier_promotion",
                "message": f"{lead.address}: Promoted to {new_tier}-Tier ({old_score:.0f} → {new_score:.0f})",
                "priority": "high" if new_tier in ("S", "A") else "medium"
            })

        # Significant score increase
        elif new_score - old_score >= self.SCORE_CHANGE_THRESHOLD:
            changes.append({
                "type": "score_increase",
                "message": f"{lead.address}: Score {old_score:.0f} → {new_score:.0f} (+{new_score-old_score:.0f})",
                "priority": "medium"
            })

        # New S-tier lead (always critical)
        if new_tier == "S" and old_tier != "S":
            changes.append({
                "type": "new_hot_lead",
                "message": f"NEW HOT LEAD: {lead.address} scored {new_score:.0f}",
                "priority": "critical"
            })

        return changes

    def _tier_rank(self, tier: str) -> int:
        return {"D": 0, "C": 1, "B": 2, "A": 3, "S": 4}.get(tier, 0)
```

---

## 5. Caching & Performance

### 5.1 Caching Strategy

```python
from cachetools import TTLCache
import json

class CacheManager:
    """In-memory caching for frequently accessed data"""

    def __init__(self):
        # Geocoding results — rarely change, cache aggressively
        self.geocode_cache = TTLCache(maxsize=10000, ttl=86400 * 30)  # 30 days

        # Dashboard KPIs — refresh every 5 minutes
        self.kpi_cache = TTLCache(maxsize=50, ttl=300)  # 5 min

        # Lead list queries — refresh on any data change
        self.query_cache = TTLCache(maxsize=100, ttl=60)  # 1 min

    def get_geocode(self, address: str):
        return self.geocode_cache.get(address)

    def set_geocode(self, address: str, coords: tuple):
        self.geocode_cache[address] = coords

    def invalidate_queries(self):
        """Call after any data write to force fresh queries"""
        self.query_cache.clear()
```

### 5.2 Dashboard Query Optimization

```python
# Pre-computed views for fast dashboard rendering

# Morning briefing query — should return in <100ms
BRIEFING_QUERY = """
    SELECT l.*, p.address, p.city, p.zip_code, p.list_price,
           p.latitude, p.longitude, p.owner_name, p.owner_phone,
           COUNT(s.id) as signal_count,
           GROUP_CONCAT(s.signal_type || ':' || s.points, '|') as signal_summary
    FROM leads l
    JOIN properties p ON l.property_id = p.id
    LEFT JOIN signals s ON s.lead_id = l.id AND s.is_active = TRUE
    WHERE l.is_active = TRUE
      AND l.tier IN ('S', 'A')
      AND l.detected_at > datetime('now', '-7 days')
    GROUP BY l.id
    ORDER BY l.current_score DESC
    LIMIT 20
"""

# Lead list query with filters
LEAD_LIST_QUERY = """
    SELECT l.*, p.*,
           COUNT(s.id) as signal_count
    FROM leads l
    JOIN properties p ON l.property_id = p.id
    LEFT JOIN signals s ON s.lead_id = l.id AND s.is_active = TRUE
    WHERE l.is_active = TRUE
      AND (:tier IS NULL OR l.tier = :tier)
      AND (:zip IS NULL OR p.zip_code = :zip)
      AND (:min_score IS NULL OR l.current_score >= :min_score)
    GROUP BY l.id
    ORDER BY l.current_score DESC
    LIMIT :limit OFFSET :offset
"""

# Map query — lightweight, just coords + tier + score
MAP_QUERY = """
    SELECT l.id, l.current_score, l.tier, l.signal_count,
           p.address, p.latitude, p.longitude, p.list_price
    FROM leads l
    JOIN properties p ON l.property_id = p.id
    WHERE l.is_active = TRUE
      AND p.latitude IS NOT NULL
      AND p.longitude IS NOT NULL
"""
```

---

## 6. Background Jobs & Notifications

### 6.1 Morning Briefing Generator

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MorningBriefing:
    date: datetime
    hot_leads: list          # S-tier leads requiring action
    new_leads_today: list    # All new leads in last 24h
    score_changes: list      # Significant score changes
    market_pulse: dict       # Market-level stats
    priority_actions: list   # Ranked action items

async def generate_morning_briefing() -> MorningBriefing:
    """Generate the daily morning briefing — runs at 6:30 AM"""
    yesterday = datetime.utcnow() - timedelta(days=1)

    # Fetch data in parallel
    hot_leads = await get_leads_by_tier("S")
    new_leads = await get_leads_since(yesterday)
    score_changes = await get_significant_score_changes(since=yesterday)

    # Market pulse
    market_pulse = {
        "new_expireds_week": await count_expireds(days=7),
        "avg_dom": await get_avg_dom(),
        "new_price_reductions": await count_price_reductions(days=7),
        "expireds_vs_last_week": await compare_expireds_week_over_week(),
    }

    # Generate priority actions
    priority_actions = []
    for lead in hot_leads:
        if lead.status == "new":
            priority_actions.append({
                "action": "call",
                "lead": lead,
                "reason": f"Score {lead.current_score:.0f} — {lead.signal_count} signals stacked",
                "urgency": "immediate"
            })

    # Sort by score descending
    priority_actions.sort(key=lambda x: x["lead"].current_score, reverse=True)

    return MorningBriefing(
        date=datetime.utcnow(),
        hot_leads=hot_leads,
        new_leads_today=new_leads,
        score_changes=score_changes,
        market_pulse=market_pulse,
        priority_actions=priority_actions[:10]  # Top 10 actions
    )
```

### 6.2 Notification Service

```python
class NotificationService:
    """Multi-channel notification delivery"""

    async def notify(self, notification: dict):
        priority = notification.get("priority", "low")

        # Always: push to dashboard notification feed
        await self._push_to_dashboard(notification)

        # High/Critical: also send email
        if priority in ("high", "critical"):
            await self._send_email(notification)

        # Critical only: also send SMS (if configured)
        if priority == "critical":
            await self._send_sms(notification)

    async def _push_to_dashboard(self, notification: dict):
        """Push notification to all connected dashboard clients via WebSocket"""
        # NiceGUI handles this natively
        from nicegui import ui
        ui.notify(
            notification["message"],
            type="warning" if notification["priority"] == "critical" else "info",
            position="top-right",
            timeout=0 if notification["priority"] == "critical" else 10000
        )

    async def _send_email(self, notification: dict):
        """Send email via SendGrid"""
        # import sendgrid
        # sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        # ...
        pass

    async def _send_sms(self, notification: dict):
        """Send SMS via Twilio (critical alerts only)"""
        # from twilio.rest import Client
        # client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        # client.messages.create(body=notification["message"], from_=TWILIO_FROM, to=SARAH_PHONE)
        pass
```

---

## 7. Security & Compliance

### 7.1 MLS Data Handling

- MLS data is licensed, not owned — cannot be resold or shared publicly
- Store MLS data in local database only — never expose via public API
- Respect MLS board's terms: data for licensed Realtor's use only
- Do not display MLS data to consumers without IDX agreement
- Implement data retention policies — purge stale MLS data per board rules

### 7.2 Authentication

```python
from nicegui import app, ui
import hashlib

# Simple auth for single-user dashboard
USERS = {
    "sarah": hashlib.sha256("secure_password_here".encode()).hexdigest()
}

@ui.page('/login')
def login_page():
    def try_login():
        username = username_input.value
        password_hash = hashlib.sha256(password_input.value.encode()).hexdigest()
        if USERS.get(username) == password_hash:
            app.storage.user["authenticated"] = True
            app.storage.user["username"] = username
            ui.navigate.to("/")
        else:
            ui.notify("Invalid credentials", type="negative")

    with ui.card().classes('mx-auto mt-20 p-8'):
        ui.label('LeadFinder').classes('text-2xl font-bold mb-4')
        username_input = ui.input('Username')
        password_input = ui.input('Password', password=True)
        ui.button('Login', on_click=try_login).classes('w-full mt-4')

# Auth middleware
def require_auth():
    if not app.storage.user.get("authenticated"):
        ui.navigate.to("/login")
        return False
    return True
```

### 7.3 Fair Housing Compliance

- Never use protected class data (race, religion, national origin, sex, familial status, disability) in scoring
- Do not target or exclude neighborhoods based on demographic composition
- Document scoring criteria to demonstrate non-discriminatory basis
- All signals must be based on property/financial data, not occupant characteristics
- Include Fair Housing disclaimer in all automated outreach

### 7.4 API Key Management

```python
# Use environment variables, never hardcode
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MLS_CLIENT_ID = os.getenv("MLS_CLIENT_ID")
    MLS_CLIENT_SECRET = os.getenv("MLS_CLIENT_SECRET")
    ATTOM_API_KEY = os.getenv("ATTOM_API_KEY")
    BATCH_LEADS_API_KEY = os.getenv("BATCH_LEADS_API_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

    # Validate required keys on startup
    @classmethod
    def validate(cls):
        missing = [k for k, v in vars(cls).items()
                   if k.isupper() and v is None and k != "TWILIO_SID"]
        if missing:
            print(f"Warning: Missing config keys: {', '.join(missing)}")
```

### 7.5 Audit Logging

```sql
CREATE TABLE audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    user        TEXT,
    action      TEXT NOT NULL,  -- login, view_lead, call, send_cma, export, etc.
    entity_type TEXT,           -- lead, property, report
    entity_id   INTEGER,
    details     TEXT,           -- JSON with additional context
    ip_address  TEXT
);

-- Example entries:
-- "sarah viewed lead #123 (123 Main St)"
-- "sarah exported 47 leads to CSV"
-- "system scored lead #456 at 87 (S-Tier)"
-- "system sent morning briefing email"
```

---

*This architecture provides a solid foundation for LeadFinder's data pipeline, designed to scale from a simple SQLite-backed local tool to a full production system with PostgreSQL, multiple data sources, and real-time notifications.*
