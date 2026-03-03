# Python Implementation Patterns & Technical Architecture

> **Project**: TheLeadEdge -- Real Estate Lead Generation System
> **Created**: 2026-02-28
> **Purpose**: Technical blueprint for the build phase. Covers project structure, data models, connectors, scoring engine, pipelines, database schema, configuration, error handling, and testing.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Key Python Libraries](#2-key-python-libraries)
3. [Data Models (Pydantic)](#3-data-models)
4. [Data Source Connectors](#4-data-source-connectors)
5. [Lead Scoring Engine](#5-lead-scoring-engine)
6. [Daily Pipeline Architecture](#6-daily-pipeline-architecture)
7. [Database Schema & Migrations](#7-database-schema--migrations)
8. [Configuration Management](#8-configuration-management)
9. [Error Handling & Resilience](#9-error-handling--resilience)
10. [Testing Strategy](#10-testing-strategy)

---

## 1. Project Structure

```
theleadedge/
├── pyproject.toml              # Project metadata, dependencies (PEP 621)
├── alembic.ini                 # Alembic migration config
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── config/
│   ├── __init__.py
│   ├── settings.py             # Pydantic Settings (env-based config)
│   ├── scoring_weights.yaml    # Tunable signal weights
│   └── feature_flags.yaml      # Enable/disable data sources
├── theleadedge/
│   ├── __init__.py
│   ├── main.py                 # Application entrypoint (scheduler + dashboard)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── property.py         # Property data model
│   │   ├── lead.py             # Lead data model
│   │   ├── signal.py           # Signal data model
│   │   ├── score.py            # Score & ScoreHistory models
│   │   ├── outreach.py         # OutreachEvent model
│   │   └── enums.py            # Shared enumerations (Tier, LeadStatus, etc.)
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract DataSourceConnector
│   │   ├── mls.py              # MLSConnector (RESO Web API)
│   │   ├── mls_csv.py          # MLSCsvConnector (CSV import fallback)
│   │   ├── attom.py            # AttomConnector (property enrichment)
│   │   ├── public_records.py   # PublicRecordConnector (county/aggregator)
│   │   ├── skip_trace.py       # SkipTraceConnector (BatchLeads)
│   │   ├── expired_feed.py     # ExpiredFeedConnector (REDX)
│   │   └── geocoding.py        # GeocodingService (Census Bureau)
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── engine.py           # ScoringEngine (calculate, decay, tier)
│   │   ├── decay.py            # Decay function implementations
│   │   ├── stacking.py         # Signal stacking bonus rules
│   │   └── config_loader.py    # Load weights from YAML
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # DailyPipelineOrchestrator
│   │   ├── ingest.py           # Data ingestion (fetch + validate + store)
│   │   ├── detect.py           # Signal detection from raw data
│   │   ├── enrich.py           # Property enrichment pipeline
│   │   ├── score.py            # Scoring pipeline (score + tier + rank)
│   │   ├── deduplicate.py      # Address matching & deduplication
│   │   └── briefing.py         # Daily briefing generation
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── email.py            # Email sender (SMTP / SendGrid)
│   │   ├── templates/
│   │   │   ├── daily_briefing.html
│   │   │   ├── s_tier_alert.html
│   │   │   └── weekly_summary.html
│   │   └── dispatcher.py       # Route alerts by tier/urgency
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy engine & session factory
│   │   ├── repositories.py     # CRUD operations (PropertyRepo, LeadRepo, etc.)
│   │   └── queries.py          # Named complex queries
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── crm.py              # Follow Up Boss client & sync
│   │   └── ai.py               # Claude API for summaries & drafts
│   └── utils/
│       ├── __init__.py
│       ├── address.py           # Address normalization (USPS format)
│       ├── phone.py             # Phone number normalization
│       ├── logging.py           # Structured logging setup
│       ├── retry.py             # Retry decorator with backoff
│       └── rate_limit.py        # Token-bucket rate limiter
├── tests/
│   ├── conftest.py             # Shared fixtures, test DB
│   ├── factories.py            # Factory Boy model factories
│   ├── unit/
│   │   ├── test_scoring.py
│   │   ├── test_decay.py
│   │   ├── test_stacking.py
│   │   ├── test_address.py
│   │   └── test_deduplication.py
│   ├── integration/
│   │   ├── test_mls_connector.py
│   │   ├── test_attom_connector.py
│   │   ├── test_pipeline.py
│   │   └── test_crm_sync.py
│   └── e2e/
│       └── test_daily_pipeline.py
├── .env.example                # Template for environment variables
├── .gitignore
└── README.md
```

### Key Design Principles

- **Separation of concerns**: Each module has a single responsibility. Sources fetch data. Pipelines orchestrate workflows. Scoring calculates scores. Storage persists state.
- **Dependency injection**: Connectors and services are injected, not imported as globals. This enables testing with mocks and swapping implementations.
- **Config-driven behavior**: Scoring weights, feature flags, and schedules live in YAML files editable without code changes.
- **Async-first**: All I/O-bound operations (API calls, database queries) use `async`/`await` via `httpx` and SQLAlchemy async engine.

---

## 2. Key Python Libraries

### Core Dependencies

```toml
# pyproject.toml
[project]
name = "theleadedge"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Data validation & settings
    "pydantic>=2.6",
    "pydantic-settings>=2.2",

    # Database
    "sqlalchemy[asyncio]>=2.0",
    "aiosqlite>=0.20",          # Async SQLite driver
    "alembic>=1.13",            # Schema migrations
    # "asyncpg>=0.29",          # Uncomment when migrating to PostgreSQL

    # HTTP & APIs
    "httpx>=0.27",              # Async HTTP client
    "tenacity>=8.2",            # Retry with backoff

    # Scheduling
    "apscheduler>=3.10",        # Cron-style job scheduling

    # Email & notifications
    "jinja2>=3.1",              # HTML email templates
    "sendgrid>=6.11",           # SendGrid SDK (or use aiosmtplib)

    # Configuration
    "pyyaml>=6.0",              # YAML config files
    "python-dotenv>=1.0",       # .env file loading

    # Data processing
    "pandas>=2.2",              # Tabular data operations

    # Logging
    "structlog>=24.1",          # Structured logging

    # Dashboard (Phase 1 uses NiceGUI per dashboard research)
    "nicegui>=2.0",             # Web UI framework (includes FastAPI)
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-mock>=3.12",
    "factory-boy>=3.3",
    "coverage>=7.4",
    "ruff>=0.3",                # Linter + formatter
    "mypy>=1.8",                # Type checking
]

pdf = [
    "weasyprint>=61",           # HTML-to-PDF for CMA reports
]

ai = [
    "anthropic>=0.25",          # Claude API for lead summaries
]
```

### Library Selection Rationale

| Category | Library | Why This Over Alternatives |
|----------|---------|--------------------------|
| HTTP | `httpx` | Async-native, similar API to `requests`, HTTP/2 support |
| ORM | `sqlalchemy 2.0+` | Industry standard, async support, Alembic migrations |
| Validation | `pydantic v2` | 5-50x faster than v1, native in FastAPI/NiceGUI |
| Retry | `tenacity` | More flexible than `backoff`, supports async |
| Scheduling | `apscheduler` | Cron expressions, persistent job store, async support |
| Logging | `structlog` | JSON-structured logs, easy filtering, correlation IDs |
| Dashboard | `nicegui` | Best visual quality of Python frameworks (see dashboard_frameworks.md) |
| Templates | `jinja2` | Standard for HTML templating, used by NiceGUI internally |
| Config | `pydantic-settings` | Type-safe env loading, validation, dotenv support |
| Testing | `pytest` + `factory-boy` | Fixtures, parametrize, clean model factories |

---

## 3. Data Models

All models use Pydantic v2 for validation and serialization. SQLAlchemy models mirror these for persistence. The pattern: Pydantic models define the schema and validate data at the boundary; SQLAlchemy models handle persistence.

### 3.1 Shared Enumerations

```python
# theleadedge/models/enums.py
from enum import StrEnum

class Tier(StrEnum):
    S = "S"   # 80-100: Immediate personal outreach
    A = "A"   # 60-79:  Priority outreach within 48 hours
    B = "B"   # 40-59:  Scheduled outreach sequence
    C = "C"   # 20-39:  Drip campaign, monthly touch
    D = "D"   # 0-19:   Monitor only

class LeadStatus(StrEnum):
    NEW = "new"
    CONTACTED = "contacted"
    MEETING = "meeting"
    LISTING = "listing"
    CLOSED = "closed"
    LOST = "lost"
    ARCHIVED = "archived"

class SignalCategory(StrEnum):
    MLS = "mls"
    PUBLIC_RECORD = "public_record"
    LIFE_EVENT = "life_event"
    MARKET = "market"
    DIGITAL = "digital"

class DecayType(StrEnum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    STEP = "step"
    ESCALATING = "escalating"  # Urgency increases toward deadline

class MLSStatus(StrEnum):
    ACTIVE = "Active"
    PENDING = "Pending"
    EXPIRED = "Expired"
    WITHDRAWN = "Withdrawn"
    SOLD = "Sold"
    COMING_SOON = "ComingSoon"

class OutreachType(StrEnum):
    PHONE_CALL = "phone_call"
    EMAIL = "email"
    DIRECT_MAIL = "direct_mail"
    DOOR_KNOCK = "door_knock"
    HANDWRITTEN_NOTE = "handwritten_note"
    CMA_SENT = "cma_sent"
    TEXT = "text"

class OutreachOutcome(StrEnum):
    NO_ANSWER = "no_answer"
    VOICEMAIL = "voicemail"
    ANSWERED = "answered"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    CALLBACK_REQUESTED = "callback_requested"
    MEETING_SET = "meeting_set"
    WRONG_NUMBER = "wrong_number"
    DO_NOT_CONTACT = "do_not_contact"
```

### 3.2 Property Model

```python
# theleadedge/models/property.py
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re

class PropertyBase(BaseModel):
    """Core property fields shared across create/read/update."""
    address: str
    city: str
    state: str = "AZ"
    zip_code: str = Field(pattern=r"^\d{5}(-\d{4})?$")
    county: Optional[str] = None

    # Physical characteristics
    bedrooms: Optional[int] = Field(default=None, ge=0, le=20)
    bathrooms: Optional[float] = Field(default=None, ge=0, le=20)
    sqft: Optional[int] = Field(default=None, ge=0)
    lot_sqft: Optional[int] = Field(default=None, ge=0)
    year_built: Optional[int] = Field(default=None, ge=1800, le=2030)
    property_type: Optional[str] = None  # SFR, Condo, Townhouse, Multi

    # Geolocation
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

class PropertyValuation(BaseModel):
    """Pricing and valuation fields."""
    list_price: Optional[int] = Field(default=None, ge=0)
    original_list_price: Optional[int] = Field(default=None, ge=0)
    estimated_value: Optional[int] = Field(default=None, ge=0)
    estimated_equity: Optional[int] = None
    last_sold_price: Optional[int] = Field(default=None, ge=0)
    last_sold_date: Optional[date] = None

class PropertyMLS(BaseModel):
    """MLS-specific fields."""
    mls_number: Optional[str] = None
    mls_status: Optional[str] = None
    days_on_market: Optional[int] = Field(default=None, ge=0)
    cumulative_dom: Optional[int] = Field(default=None, ge=0)
    list_date: Optional[date] = None
    expiration_date: Optional[date] = None
    status_change_date: Optional[date] = None
    listing_agent: Optional[str] = None
    listing_office: Optional[str] = None
    price_change_count: int = 0

class PropertyOwner(BaseModel):
    """Owner information."""
    owner_name: Optional[str] = None
    owner_first_name: Optional[str] = None
    owner_last_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_mailing_address: Optional[str] = None
    is_absentee: bool = False
    is_corporate: bool = False
    ownership_years: Optional[float] = None

    @field_validator("owner_phone", mode="before")
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        digits = re.sub(r"\D", "", v)
        if len(digits) == 10:
            return f"+1{digits}"
        if len(digits) == 11 and digits.startswith("1"):
            return f"+{digits}"
        return v  # Return as-is if non-standard

class Property(PropertyBase, PropertyValuation, PropertyMLS, PropertyOwner):
    """Full property model combining all field groups."""
    id: Optional[int] = None
    address_normalized: Optional[str] = None
    data_source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy

class PropertyCreate(PropertyBase, PropertyValuation, PropertyMLS, PropertyOwner):
    """Fields accepted when creating a new property."""
    data_source: str = "manual"

class PropertyUpdate(BaseModel):
    """Partial update -- all fields optional."""
    list_price: Optional[int] = None
    mls_status: Optional[str] = None
    days_on_market: Optional[int] = None
    estimated_value: Optional[int] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    is_absentee: Optional[bool] = None
    price_change_count: Optional[int] = None
```

### 3.3 Signal Model

```python
# theleadedge/models/signal.py
from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from .enums import SignalCategory, DecayType

class SignalBase(BaseModel):
    """A single indicator of seller motivation."""
    signal_type: str            # e.g., "expired_listing", "pre_foreclosure"
    signal_category: SignalCategory
    description: Optional[str] = None  # Human-readable: "3rd price reduction: $425K -> $379K"
    source: Optional[str] = None       # "MLS", "ATTOM", "County Recorder"
    source_ref: Optional[str] = None   # External ID from source system
    event_date: Optional[date] = None  # When the real-world event occurred
    raw_data: Optional[dict[str, Any]] = None  # Original payload for debugging

class Signal(SignalBase):
    """Full signal with scoring metadata."""
    id: Optional[int] = None
    lead_id: int
    property_id: int
    points: float = 0.0          # Points contributed after decay
    base_points: float = 0.0     # Points before decay
    weight: float = 1.0          # Configurable multiplier
    decay_type: DecayType = DecayType.LINEAR
    half_life_days: Optional[float] = None  # For exponential decay
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True

class SignalCreate(SignalBase):
    """Fields required to register a new signal."""
    lead_id: int
    property_id: int
    base_points: float
    decay_type: DecayType = DecayType.LINEAR
    half_life_days: Optional[float] = None

class SignalConfig(BaseModel):
    """Configuration entry for a signal type (loaded from YAML)."""
    signal_type: str
    category: SignalCategory
    base_points: float
    decay_type: DecayType = DecayType.LINEAR
    half_life_days: float = 30.0
    description: str = ""
    is_active: bool = True
```

### 3.4 Lead Model

```python
# theleadedge/models/lead.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, computed_field
from .enums import Tier, LeadStatus
from .signal import Signal
from .property import Property

class LeadBase(BaseModel):
    """A property that has been identified as a potential listing opportunity."""
    property_id: int
    status: LeadStatus = LeadStatus.NEW
    is_active: bool = True

class Lead(LeadBase):
    """Full lead with scoring and metadata."""
    id: Optional[int] = None
    current_score: float = 0.0
    previous_score: Optional[float] = None
    tier: Tier = Tier.D
    signal_count: int = 0
    priority_rank: Optional[int] = None

    # Engagement tracking
    contacted_at: Optional[datetime] = None
    last_touch_at: Optional[datetime] = None
    next_touch_date: Optional[datetime] = None
    contact_attempts: int = 0

    # CRM sync
    crm_id: Optional[str] = None
    crm_synced_at: Optional[datetime] = None

    # AI-generated
    summary: Optional[str] = None

    # Timestamps
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    scored_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Relationships (populated by queries, not stored on lead row)
    property: Optional[Property] = None
    signals: list[Signal] = Field(default_factory=list)

    @computed_field
    @property
    def score_change(self) -> float:
        """Delta from previous score. Positive = improving lead."""
        if self.previous_score is None:
            return 0.0
        return self.current_score - self.previous_score

    @computed_field
    @property
    def days_since_detection(self) -> int:
        return (datetime.utcnow() - self.detected_at).days

    class Config:
        from_attributes = True

class LeadCreate(LeadBase):
    """Minimum fields to create a lead."""
    pass

class LeadUpdate(BaseModel):
    """Partial update for a lead."""
    status: Optional[LeadStatus] = None
    is_active: Optional[bool] = None
    contacted_at: Optional[datetime] = None
    next_touch_date: Optional[datetime] = None
    notes: Optional[str] = None
    crm_id: Optional[str] = None
```

### 3.5 Score Model

```python
# theleadedge/models/score.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .enums import Tier

class ScoreResult(BaseModel):
    """Output of the scoring engine for a single lead."""
    lead_id: int
    raw_score: float
    normalized_score: float = Field(ge=0, le=100)
    tier: Tier
    signal_count: int
    top_signals: list[str]  # Top 3 signal types by contribution
    stacking_bonus: float = 0.0
    freshness_bonus: float = 0.0
    recommended_action: str
    urgency_label: str  # "immediate", "today", "this_week", "this_month", "monitor"
    next_touch_date: Optional[datetime] = None

    @property
    def recommended_action_text(self) -> str:
        actions = {
            Tier.S: "Immediate personal outreach -- phone call + handwritten note",
            Tier.A: "Priority outreach within 48 hours -- CMA + call",
            Tier.B: "Scheduled outreach this week -- add to priority drip",
            Tier.C: "Monthly touch -- add to nurture campaign",
            Tier.D: "Monitor only -- no active outreach",
        }
        return actions.get(self.tier, "Review manually")

class ScoreHistory(BaseModel):
    """Historical score snapshot for trend tracking."""
    id: Optional[int] = None
    lead_id: int
    score: float
    tier: Tier
    signal_count: int
    change_reason: str  # "New signal: price_reduction", "Urgency decay", "Re-score"
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
```

### 3.6 OutreachEvent Model

```python
# theleadedge/models/outreach.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .enums import OutreachType, OutreachOutcome

class OutreachEvent(BaseModel):
    """Record of contact with a lead."""
    id: Optional[int] = None
    lead_id: int
    outreach_type: OutreachType
    outcome: Optional[OutreachOutcome] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    performed_by: str = "sarah"
    performed_at: datetime = Field(default_factory=datetime.utcnow)
    follow_up_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class OutreachEventCreate(BaseModel):
    """Fields to log a new outreach event."""
    lead_id: int
    outreach_type: OutreachType
    outcome: Optional[OutreachOutcome] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    performed_by: str = "sarah"
    follow_up_date: Optional[datetime] = None
```

---

## 4. Data Source Connectors

### 4.1 Abstract Base Connector

All data sources implement a common interface. This enables the Strategy pattern -- connectors are interchangeable and testable behind a uniform contract.

```python
# theleadedge/sources/base.py
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

class SyncResult(BaseModel):
    """Standardized output from any data source sync."""
    source: str
    job_type: str           # "full_sync", "incremental", "on_demand"
    success: bool
    records_fetched: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    errors: list[str] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

class DataSourceConnector(ABC):
    """
    Abstract base for all external data source connectors.

    Each connector handles:
    1. Authentication with the external service
    2. Fetching data (full sync or incremental)
    3. Transforming external data into our Property/Signal models
    4. Rate limiting and error handling

    Subclasses must implement fetch() and transform().
    """

    def __init__(self, name: str):
        self.name = name
        self._is_authenticated = False
        self.log = logger.bind(source=name)

    @abstractmethod
    async def authenticate(self) -> None:
        """Establish credentials with the external service."""
        ...

    @abstractmethod
    async def fetch(
        self,
        since: Optional[datetime] = None,
        **filters: Any,
    ) -> list[dict]:
        """
        Fetch raw records from the external source.

        Args:
            since: For incremental sync, only fetch records changed after this time.
            **filters: Source-specific filters (zip_code, status, etc.)

        Returns:
            List of raw dictionaries from the source API.
        """
        ...

    @abstractmethod
    def transform(self, raw_records: list[dict]) -> list[dict]:
        """
        Transform raw source data into standardized property/signal dicts.

        Returns:
            List of dicts conforming to PropertyCreate or SignalCreate schemas.
        """
        ...

    async def sync(self, since: Optional[datetime] = None, **filters: Any) -> SyncResult:
        """
        Full sync workflow: authenticate -> fetch -> transform.
        Orchestrator calls this; subclasses implement the pieces.
        """
        started = datetime.utcnow()
        result = SyncResult(
            source=self.name, job_type="incremental" if since else "full_sync",
            success=False, started_at=started,
        )

        try:
            if not self._is_authenticated:
                await self.authenticate()
                self._is_authenticated = True

            raw = await self.fetch(since=since, **filters)
            result.records_fetched = len(raw)
            self.log.info("fetch_complete", count=len(raw))

            transformed = self.transform(raw)
            result.records_created = len(transformed)
            result.success = True

        except Exception as e:
            result.errors.append(str(e))
            self.log.error("sync_failed", error=str(e), exc_info=True)

        result.completed_at = datetime.utcnow()
        result.duration_ms = int(
            (result.completed_at - result.started_at).total_seconds() * 1000
        )
        return result

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the service is reachable and authenticated."""
        ...
```

### 4.2 MLS Connector (RESO Web API)

```python
# theleadedge/sources/mls.py
from datetime import datetime
from typing import Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import Settings
from .base import DataSourceConnector

class MLSConnector(DataSourceConnector):
    """
    Connects to MLS data via the RESO Web API (OData v4).

    Authentication: OAuth 2.0 client credentials flow.
    Pagination: Server-driven via @odata.nextLink.
    Rate limits: Respects Retry-After headers on 429 responses.

    Priority queries for lead generation:
    - Expired listings (last N days)
    - Active listings with price reductions
    - High DOM listings (90/120/180+ days)
    - Withdrawn-and-relisted (CDOM > DOM)
    - Pending-to-active (fallen-through deals)
    """

    USEFUL_FIELDS = (
        "ListingKey,ListingId,StandardStatus,ListPrice,OriginalListPrice,"
        "DaysOnMarket,CumulativeDaysOnMarket,PostalCode,City,StateOrProvince,"
        "StreetNumber,StreetName,StreetSuffix,UnitNumber,"
        "BedroomsTotal,BathroomsTotalInteger,LivingArea,LotSizeSquareFeet,"
        "YearBuilt,PropertySubType,"
        "ListAgentKey,ListAgentFullName,ListOfficeName,"
        "StatusChangeTimestamp,PriceChangeTimestamp,"
        "ListingContractDate,ExpirationDate,"
        "PublicRemarks,PrivateRemarks"
    )

    def __init__(self, settings: Settings):
        super().__init__(name="mls_reso")
        self.base_url = settings.mls_base_url
        self.client_id = settings.mls_client_id
        self.client_secret = settings.mls_client_secret.get_secret_value()
        self.token_url = settings.mls_token_url
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

    async def authenticate(self) -> None:
        """OAuth 2.0 client credentials flow."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "api",
                },
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            self.token_expires_at = datetime.utcnow().replace(
                second=0, microsecond=0
            )
            self._is_authenticated = True
            self.log.info("authenticated", expires_in=expires_in)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
    )
    async def _odata_query(
        self,
        resource: str = "Property",
        filter_str: str = "",
        select: Optional[str] = None,
        orderby: Optional[str] = None,
        top: int = 200,
    ) -> list[dict]:
        """Execute an OData query with automatic pagination."""
        params: dict[str, Any] = {"$top": top}
        if filter_str:
            params["$filter"] = filter_str
        if select:
            params["$select"] = select
        if orderby:
            params["$orderby"] = orderby

        all_results: list[dict] = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/{resource}"
            while url:
                response = await client.get(
                    url,
                    params=params if url.startswith(self.base_url) else None,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                )

                # Handle token expiry
                if response.status_code == 401:
                    await self.authenticate()
                    continue

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    self.log.warning("rate_limited", retry_after=retry_after)
                    import asyncio
                    await asyncio.sleep(retry_after)
                    continue

                response.raise_for_status()
                data = response.json()
                results = data.get("value", [])
                all_results.extend(results)

                # Server-driven pagination
                url = data.get("@odata.nextLink")
                params = {}  # nextLink includes all params

        return all_results

    async def fetch(self, since: Optional[datetime] = None, **filters: Any) -> list[dict]:
        """Fetch listings matching lead-generation criteria."""
        query_type = filters.get("query_type", "expired")
        zip_codes = filters.get("zip_codes", [])
        zip_filter = ""
        if zip_codes:
            zip_parts = " or ".join(f"PostalCode eq '{z}'" for z in zip_codes)
            zip_filter = f" and ({zip_parts})"

        since_str = (since or datetime.utcnow().replace(hour=0, minute=0)).isoformat() + "Z"

        queries = {
            "expired": (
                f"StandardStatus eq 'Expired'"
                f" and StatusChangeTimestamp gt {since_str}"
                f"{zip_filter}"
            ),
            "price_reductions": (
                f"StandardStatus eq 'Active'"
                f" and ListPrice lt OriginalListPrice"
                f" and PriceChangeTimestamp gt {since_str}"
                f"{zip_filter}"
            ),
            "high_dom": (
                f"StandardStatus eq 'Active'"
                f" and DaysOnMarket ge 90"
                f"{zip_filter}"
            ),
            "withdrawn_relisted": (
                f"StandardStatus eq 'Active'"
                f" and CumulativeDaysOnMarket gt DaysOnMarket"
                f"{zip_filter}"
            ),
            "back_on_market": (
                f"StandardStatus eq 'Active'"
                f" and StatusChangeTimestamp gt {since_str}"
                f"{zip_filter}"
                # Post-filter for pending-to-active in transform step
            ),
        }

        filter_str = queries.get(query_type, queries["expired"])
        return await self._odata_query(
            filter_str=filter_str,
            select=self.USEFUL_FIELDS,
            orderby="StatusChangeTimestamp desc",
        )

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Transform RESO records into PropertyCreate-compatible dicts."""
        results = []
        for rec in raw_records:
            street_parts = [
                rec.get("StreetNumber", ""),
                rec.get("StreetName", ""),
                rec.get("StreetSuffix", ""),
            ]
            address = " ".join(p for p in street_parts if p).strip()
            if rec.get("UnitNumber"):
                address += f" #{rec['UnitNumber']}"

            results.append({
                "address": address,
                "city": rec.get("City", ""),
                "state": rec.get("StateOrProvince", "AZ"),
                "zip_code": rec.get("PostalCode", ""),
                "bedrooms": rec.get("BedroomsTotal"),
                "bathrooms": rec.get("BathroomsTotalInteger"),
                "sqft": rec.get("LivingArea"),
                "lot_sqft": rec.get("LotSizeSquareFeet"),
                "year_built": rec.get("YearBuilt"),
                "property_type": rec.get("PropertySubType"),
                "list_price": rec.get("ListPrice"),
                "original_list_price": rec.get("OriginalListPrice"),
                "mls_number": rec.get("ListingId") or rec.get("ListingKey"),
                "mls_status": rec.get("StandardStatus"),
                "days_on_market": rec.get("DaysOnMarket"),
                "cumulative_dom": rec.get("CumulativeDaysOnMarket"),
                "list_date": rec.get("ListingContractDate"),
                "expiration_date": rec.get("ExpirationDate"),
                "listing_agent": rec.get("ListAgentFullName"),
                "listing_office": rec.get("ListOfficeName"),
                "data_source": "mls_reso",
            })
        return results

    async def health_check(self) -> bool:
        try:
            if not self._is_authenticated:
                await self.authenticate()
            results = await self._odata_query(
                filter_str="StandardStatus eq 'Active'",
                select="ListingKey",
                top=1,
            )
            return True
        except Exception:
            return False
```

### 4.3 MLS CSV Import Connector (Fallback)

```python
# theleadedge/sources/mls_csv.py
import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .base import DataSourceConnector

class MLSCsvConnector(DataSourceConnector):
    """
    Fallback connector: import MLS data from saved search CSV exports.

    Use this when the RESO Web API is not yet available.
    Sarah exports a saved search from her MLS portal as CSV,
    drops it into a watched folder, and this connector ingests it.
    """

    def __init__(self, import_dir: str = "./data/mls_imports"):
        super().__init__(name="mls_csv")
        self.import_dir = Path(import_dir)

    async def authenticate(self) -> None:
        """No auth needed for file import."""
        self._is_authenticated = True

    async def fetch(self, since: Optional[datetime] = None, **filters: Any) -> list[dict]:
        """Read all unprocessed CSV files from the import directory."""
        all_rows: list[dict] = []
        if not self.import_dir.exists():
            self.log.warning("import_dir_missing", path=str(self.import_dir))
            return all_rows

        for csv_path in sorted(self.import_dir.glob("*.csv")):
            self.log.info("reading_csv", file=csv_path.name)
            with open(csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                all_rows.extend(rows)

            # Move processed file to archive
            archive_dir = self.import_dir / "processed"
            archive_dir.mkdir(exist_ok=True)
            csv_path.rename(archive_dir / csv_path.name)

        return all_rows

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """
        Map CSV column names to our property schema.
        Column names vary by MLS. This mapping handles the most
        common FlexMLS / Trestle / Matrix export formats.
        """
        # Column name mapping: {possible_csv_name: our_field_name}
        column_map = {
            "MLS #": "mls_number", "MLS Number": "mls_number", "ListingId": "mls_number",
            "Status": "mls_status", "StandardStatus": "mls_status",
            "List Price": "list_price", "ListPrice": "list_price", "Current Price": "list_price",
            "Original List Price": "original_list_price", "OriginalListPrice": "original_list_price",
            "Address": "address", "Street Address": "address",
            "City": "city",
            "State": "state",
            "Zip": "zip_code", "Zip Code": "zip_code", "PostalCode": "zip_code",
            "Beds": "bedrooms", "Bedrooms": "bedrooms", "BR": "bedrooms",
            "Baths": "bathrooms", "Bathrooms": "bathrooms",
            "SqFt": "sqft", "Square Feet": "sqft", "Living Area": "sqft",
            "Year Built": "year_built", "YearBuilt": "year_built",
            "DOM": "days_on_market", "Days on Market": "days_on_market",
            "CDOM": "cumulative_dom",
            "List Agent": "listing_agent", "Listing Agent": "listing_agent",
            "List Office": "listing_office", "Listing Office": "listing_office",
            "Property Type": "property_type", "Type": "property_type",
        }

        results = []
        for row in raw_records:
            mapped: dict[str, Any] = {"data_source": "mls_csv"}
            for csv_col, our_field in column_map.items():
                if csv_col in row and row[csv_col]:
                    value = row[csv_col].strip()
                    # Type conversions
                    if our_field in ("list_price", "original_list_price", "sqft", "year_built",
                                     "days_on_market", "cumulative_dom", "bedrooms"):
                        value = int(float(value.replace(",", "").replace("$", "")))
                    elif our_field == "bathrooms":
                        value = float(value)
                    mapped[our_field] = value

            if mapped.get("address") and mapped.get("zip_code"):
                results.append(mapped)

        return results

    async def health_check(self) -> bool:
        return self.import_dir.exists()
```

### 4.4 ATTOM Property Data Connector

```python
# theleadedge/sources/attom.py
from datetime import datetime
from typing import Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import Settings
from .base import DataSourceConnector

class AttomConnector(DataSourceConnector):
    """
    ATTOM Data property enrichment API.

    Used for:
    - Property details (owner, valuation, tax info)
    - AVM (Automated Valuation Model) for equity estimates
    - Pre-foreclosure filing data
    - Tax delinquency records

    Pricing: ~$250/month for standard API access.
    Rate limits: Varies by plan, typically 100 calls/minute.
    """

    BASE_URL = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"

    def __init__(self, settings: Settings):
        super().__init__(name="attom")
        self.api_key = settings.attom_api_key.get_secret_value()

    async def authenticate(self) -> None:
        """ATTOM uses API key auth -- no OAuth flow needed."""
        self._is_authenticated = True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30))
    async def _api_get(self, endpoint: str, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                headers={"apikey": self.api_key, "Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def fetch(self, since: Optional[datetime] = None, **filters: Any) -> list[dict]:
        """
        Fetch property data. Supports two modes:
        - Batch by ZIP code (for pre-foreclosure scanning)
        - Single property enrichment (address + zip)
        """
        mode = filters.get("mode", "enrich_single")

        if mode == "preforeclosure":
            zip_code = filters["zip_code"]
            data = await self._api_get("property/preforeclosure", {
                "postalcode": zip_code,
                "pagesize": 100,
            })
            return data.get("property", [])

        elif mode == "enrich_single":
            address = filters["address"]
            zip_code = filters["zip_code"]
            data = await self._api_get("property/detail", {
                "address1": address,
                "address2": zip_code,
            })
            return data.get("property", [])

        elif mode == "avm":
            address = filters["address"]
            zip_code = filters["zip_code"]
            data = await self._api_get("valuation/homeequity", {
                "address1": address,
                "address2": zip_code,
            })
            return data.get("property", [])

        return []

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Transform ATTOM records into our property schema."""
        results = []
        for rec in raw_records:
            addr = rec.get("address", {})
            owner = rec.get("owner", {})
            assessment = rec.get("assessment", {})
            building = rec.get("building", {}).get("size", {})
            lot = rec.get("lot", {})

            results.append({
                "address": addr.get("oneLine", ""),
                "city": addr.get("locality", ""),
                "state": addr.get("countrySubd", "AZ"),
                "zip_code": addr.get("postal1", ""),
                "latitude": rec.get("location", {}).get("latitude"),
                "longitude": rec.get("location", {}).get("longitude"),
                "bedrooms": building.get("bedrooms"),
                "bathrooms": building.get("bathCount"),
                "sqft": building.get("livingSize"),
                "lot_sqft": lot.get("lotSize1"),
                "year_built": rec.get("summary", {}).get("yearBuilt"),
                "estimated_value": assessment.get("assessed", {}).get("assdTtlValue"),
                "owner_name": " ".join(filter(None, [
                    owner.get("owner1", {}).get("firstNameAndMi"),
                    owner.get("owner1", {}).get("lastName"),
                ])),
                "owner_mailing_address": owner.get("mailAddressOneLine"),
                "is_absentee": owner.get("absenteeOwnerStatus") == "A",
                "ownership_years": None,  # Calculated from sale date
                "data_source": "attom",
            })
        return results

    async def health_check(self) -> bool:
        try:
            # Minimal API call to verify connectivity
            await self._api_get("property/detail", {
                "address1": "123 Main St",
                "address2": "85001",
            })
            return True
        except Exception:
            return False
```

### 4.5 Skip Trace Connector (BatchLeads)

```python
# theleadedge/sources/skip_trace.py
from datetime import datetime
from typing import Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import Settings
from .base import DataSourceConnector

class SkipTraceConnector(DataSourceConnector):
    """
    BatchLeads skip tracing API for owner contact information.

    Called on-demand when a new lead is detected and we need
    phone/email for the property owner.

    Pricing: ~$0.15-0.25 per skip trace.
    """

    BASE_URL = "https://api.batchleads.io/api/v1"

    def __init__(self, settings: Settings):
        super().__init__(name="skip_trace")
        self.api_key = settings.batch_leads_api_key.get_secret_value()

    async def authenticate(self) -> None:
        self._is_authenticated = True

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=2, max=15))
    async def fetch(self, since: Optional[datetime] = None, **filters: Any) -> list[dict]:
        """Skip trace a single property owner."""
        address = filters["address"]
        city = filters["city"]
        state = filters.get("state", "AZ")
        zip_code = filters["zip_code"]

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/skip-trace",
                json={
                    "address": address,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            return [response.json()]

    def transform(self, raw_records: list[dict]) -> list[dict]:
        """Extract phone and email from skip trace results."""
        results = []
        for rec in raw_records:
            owner = rec.get("owner", {})
            phones = rec.get("phones", [])
            emails = rec.get("emails", [])

            results.append({
                "owner_first_name": owner.get("firstName"),
                "owner_last_name": owner.get("lastName"),
                "owner_phone": phones[0].get("phone") if phones else None,
                "owner_email": emails[0].get("email") if emails else None,
                "owner_mailing_address": rec.get("mailingAddress"),
                "is_absentee": rec.get("isAbsentee", False),
            })
        return results

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/account",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                return response.status_code == 200
        except Exception:
            return False
```

### 4.6 Connector Registry (Strategy Pattern)

```python
# theleadedge/sources/__init__.py
from typing import Optional
from config.settings import Settings
from .base import DataSourceConnector
from .mls import MLSConnector
from .mls_csv import MLSCsvConnector
from .attom import AttomConnector
from .skip_trace import SkipTraceConnector

class ConnectorRegistry:
    """
    Registry of all data source connectors.
    Enables runtime lookup and feature-flag-based activation.

    Usage:
        registry = ConnectorRegistry(settings)
        mls = registry.get("mls")
        if mls:
            result = await mls.sync(since=last_sync)
    """

    def __init__(self, settings: Settings):
        self._connectors: dict[str, DataSourceConnector] = {}
        self._settings = settings
        self._register_connectors()

    def _register_connectors(self) -> None:
        s = self._settings

        # MLS: prefer RESO API, fall back to CSV import
        if s.feature_mls_api_enabled and s.mls_base_url:
            self._connectors["mls"] = MLSConnector(s)
        else:
            self._connectors["mls"] = MLSCsvConnector(s.mls_csv_import_dir)

        # Property enrichment
        if s.feature_attom_enabled and s.attom_api_key:
            self._connectors["attom"] = AttomConnector(s)

        # Skip tracing
        if s.feature_skip_trace_enabled and s.batch_leads_api_key:
            self._connectors["skip_trace"] = SkipTraceConnector(s)

    def get(self, name: str) -> Optional[DataSourceConnector]:
        return self._connectors.get(name)

    def all_active(self) -> dict[str, DataSourceConnector]:
        return dict(self._connectors)

    async def health_check_all(self) -> dict[str, bool]:
        results = {}
        for name, connector in self._connectors.items():
            results[name] = await connector.health_check()
        return results
```

---

## 5. Lead Scoring Engine

The scoring engine is the core intelligence of TheLeadEdge. It takes a collection of signals for a lead, applies configurable weights, time-decay functions, and stacking bonuses, then outputs a normalized 0-100 score with a tier assignment.

### 5.1 Decay Functions

```python
# theleadedge/scoring/decay.py
import math
from datetime import datetime
from theleadedge.models.enums import DecayType

def apply_decay(
    base_points: float,
    detected_at: datetime,
    now: datetime,
    decay_type: DecayType,
    half_life_days: float = 30.0,
    deadline: datetime | None = None,
) -> float:
    """
    Apply time-decay to a signal's base point value.

    Args:
        base_points: The original unmodified point value.
        detected_at: When the signal was first detected.
        now: Current timestamp (injected for testability).
        decay_type: Which decay function to apply.
        half_life_days: Used by exponential and linear decay.
        deadline: Used by escalating decay (e.g., foreclosure auction date).

    Returns:
        Decayed point value (never negative, may be zero).
    """
    age_days = max(0, (now - detected_at).total_seconds() / 86400)

    if decay_type == DecayType.LINEAR:
        # Points reduce linearly to zero at 2x the half-life
        max_days = half_life_days * 2
        if age_days >= max_days:
            return 0.0
        return base_points * (1.0 - age_days / max_days)

    elif decay_type == DecayType.EXPONENTIAL:
        # Classic half-life: value halves every half_life_days
        if half_life_days <= 0:
            return base_points
        return base_points * math.pow(0.5, age_days / half_life_days)

    elif decay_type == DecayType.STEP:
        # Discrete urgency tiers -- sharp drops at phase boundaries
        if age_days <= 7:
            return base_points * 1.0
        elif age_days <= 30:
            return base_points * 0.75
        elif age_days <= 90:
            return base_points * 0.50
        elif age_days <= 180:
            return base_points * 0.25
        else:
            return base_points * 0.05

    elif decay_type == DecayType.ESCALATING:
        # Urgency INCREASES as a deadline approaches (pre-foreclosure, tax sale)
        if deadline is None:
            return base_points
        days_until = max(0, (deadline - now).total_seconds() / 86400)
        total_window = max(1, (deadline - detected_at).total_seconds() / 86400)
        urgency = 1.0 - (days_until / total_window)
        return base_points * max(0.3, min(1.5, 0.3 + urgency * 1.2))

    return base_points


def freshness_premium(detected_at: datetime, now: datetime) -> float:
    """
    Bonus multiplier for very fresh signals.

    Being the first agent to reach out is a major competitive advantage.
    Signals detected within the last few hours get a premium.
    """
    hours_since = (now - detected_at).total_seconds() / 3600

    if hours_since <= 4:
        return 1.5   # First to know -- maximum advantage
    elif hours_since <= 24:
        return 1.3   # Same day -- still strong advantage
    elif hours_since <= 48:
        return 1.15  # Next day
    else:
        return 1.0   # No premium
```

### 5.2 Signal Stacking Rules

```python
# theleadedge/scoring/stacking.py
from dataclasses import dataclass

@dataclass
class StackingRule:
    """A rule that applies a bonus when specific signals co-occur."""
    name: str
    required_signals: set[str]   # All must be present to trigger
    multiplier: float            # Applied to the sum of those signals' points
    description: str

# Signal stacking rules -- when multiple signals converge,
# motivation probability increases non-linearly.
STACKING_RULES: list[StackingRule] = [
    StackingRule(
        name="distressed_seller",
        required_signals={"expired_listing", "price_reduction_3plus", "high_dom_90"},
        multiplier=1.5,
        description="Expired + multiple price cuts + high DOM = chasing the market",
    ),
    StackingRule(
        name="financial_distress",
        required_signals={"pre_foreclosure", "tax_delinquent"},
        multiplier=2.0,
        description="Foreclosure + tax delinquency = severe financial pressure",
    ),
    StackingRule(
        name="life_event_vacant",
        required_signals={"probate", "absentee_owner", "vacant_property"},
        multiplier=2.5,
        description="Inherited + out-of-state heir + vacant = highest motivation",
    ),
    StackingRule(
        name="tired_landlord",
        required_signals={"absentee_owner", "code_violation"},
        multiplier=1.8,
        description="Distant owner with code problems = burden property",
    ),
    StackingRule(
        name="failed_sale",
        required_signals={"expired_listing", "withdrawn_relisted"},
        multiplier=1.4,
        description="Failed once, trying again = frustrated but motivated",
    ),
    StackingRule(
        name="divorce_property",
        required_signals={"divorce", "high_dom_90"},
        multiplier=1.6,
        description="Court-ordered sale + stale listing = urgency",
    ),
]


def calculate_stacking_bonus(
    active_signal_types: set[str],
    signal_points_by_type: dict[str, float],
) -> tuple[float, list[str]]:
    """
    Check all stacking rules and return the total bonus points
    plus a list of triggered rule names.

    Only the single highest-multiplier matching rule is applied
    to avoid runaway score inflation.
    """
    best_bonus = 0.0
    triggered_rules: list[str] = []

    for rule in STACKING_RULES:
        if rule.required_signals.issubset(active_signal_types):
            # Sum the base points of the signals involved in this stack
            stacked_points = sum(
                signal_points_by_type.get(st, 0) for st in rule.required_signals
            )
            bonus = stacked_points * (rule.multiplier - 1.0)  # Extra points only

            if bonus > best_bonus:
                best_bonus = bonus
                triggered_rules = [rule.name]

    return best_bonus, triggered_rules
```

### 5.3 Scoring Weight Configuration (YAML)

```yaml
# config/scoring_weights.yaml
#
# Adjust these weights without changing code. The scoring engine
# reloads this file on startup and on manual refresh.
#
# Fields:
#   base_points: Raw point value before decay
#   decay_type: linear | exponential | step | escalating
#   half_life_days: Controls how fast the signal loses value
#   category: mls | public_record | life_event | market | digital

signals:
  # --- MLS Signals ---
  expired_listing:
    category: mls
    base_points: 15
    decay_type: exponential
    half_life_days: 21
    description: "Listing expired without selling"

  price_reduction:
    category: mls
    base_points: 4
    decay_type: linear
    half_life_days: 14
    description: "Single price reduction event"

  price_reduction_3plus:
    category: mls
    base_points: 12
    decay_type: linear
    half_life_days: 21
    description: "3+ cumulative price reductions"

  high_dom_90:
    category: mls
    base_points: 8
    decay_type: linear
    half_life_days: 60
    description: "90+ days on market"

  high_dom_120:
    category: mls
    base_points: 10
    decay_type: linear
    half_life_days: 60
    description: "120+ days on market"

  high_dom_180:
    category: mls
    base_points: 12
    decay_type: linear
    half_life_days: 90
    description: "180+ days on market (severely stale)"

  withdrawn_relisted:
    category: mls
    base_points: 10
    decay_type: linear
    half_life_days: 30
    description: "Withdrawn then relisted (agent change)"

  back_on_market:
    category: mls
    base_points: 13
    decay_type: exponential
    half_life_days: 14
    description: "Deal fell through, pending back to active"

  fsbo_expired:
    category: mls
    base_points: 12
    decay_type: exponential
    half_life_days: 14
    description: "FSBO attempt failed"

  # --- Public Record Signals ---
  pre_foreclosure:
    category: public_record
    base_points: 20
    decay_type: escalating
    half_life_days: 60
    description: "Notice of Default filed"

  probate:
    category: public_record
    base_points: 18
    decay_type: linear
    half_life_days: 90
    description: "Probate filing -- inherited property"

  divorce:
    category: public_record
    base_points: 16
    decay_type: step
    half_life_days: 45
    description: "Divorce filing with real property"

  tax_delinquent:
    category: public_record
    base_points: 13
    decay_type: linear
    half_life_days: 120
    description: "Property taxes delinquent 1+ years"

  code_violation:
    category: public_record
    base_points: 8
    decay_type: step
    half_life_days: 60
    description: "Active code enforcement violation"

  absentee_owner:
    category: public_record
    base_points: 8
    decay_type: linear
    half_life_days: 180
    description: "Owner mailing address differs from property"

  vacant_property:
    category: public_record
    base_points: 6
    decay_type: linear
    half_life_days: 180
    description: "Property appears vacant"

  long_term_owner:
    category: public_record
    base_points: 5
    decay_type: linear
    half_life_days: 365
    description: "20+ years of ownership"

  # --- Life Event Signals ---
  job_transfer:
    category: life_event
    base_points: 12
    decay_type: linear
    half_life_days: 30
    description: "Owner job change/relocation detected"

  retirement:
    category: life_event
    base_points: 8
    decay_type: linear
    half_life_days: 90
    description: "Owner retirement detected"

  # --- Market Signals ---
  neighborhood_hot:
    category: market
    base_points: 5
    decay_type: linear
    half_life_days: 60
    description: "Neighborhood sales velocity above average"

  comp_gap:
    category: market
    base_points: 6
    decay_type: linear
    half_life_days: 45
    description: "Comparable sales suggest property is undervalued"
```

### 5.4 Config Loader

```python
# theleadedge/scoring/config_loader.py
from pathlib import Path
from typing import Any
import yaml
from theleadedge.models.signal import SignalConfig
from theleadedge.models.enums import SignalCategory, DecayType

def load_scoring_config(
    config_path: str = "config/scoring_weights.yaml",
) -> dict[str, SignalConfig]:
    """
    Load signal weight configuration from YAML file.

    Returns a dict of signal_type -> SignalConfig.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Scoring config not found: {config_path}")

    with open(path) as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    configs: dict[str, SignalConfig] = {}
    for signal_type, values in raw.get("signals", {}).items():
        configs[signal_type] = SignalConfig(
            signal_type=signal_type,
            category=SignalCategory(values["category"]),
            base_points=values["base_points"],
            decay_type=DecayType(values["decay_type"]),
            half_life_days=values.get("half_life_days", 30),
            description=values.get("description", ""),
        )

    return configs
```

### 5.5 Scoring Engine

```python
# theleadedge/scoring/engine.py
from datetime import datetime
from theleadedge.models.signal import Signal, SignalConfig
from theleadedge.models.score import ScoreResult
from theleadedge.models.enums import Tier, DecayType
from .decay import apply_decay, freshness_premium
from .stacking import calculate_stacking_bonus
from .config_loader import load_scoring_config

class ScoringEngine:
    """
    Calculates lead scores from stacked signals with time decay.

    Design principles:
    - Config-driven: weights loaded from YAML, adjustable without code changes.
    - Deterministic: given the same signals and timestamp, produces the same score.
    - Testable: `now` parameter is injected, not read from system clock.
    - Capped at 100: prevents score inflation from too many signals.
    """

    MAX_SCORE = 100.0

    def __init__(self, config_path: str = "config/scoring_weights.yaml"):
        self.signal_configs = load_scoring_config(config_path)

    def calculate(
        self,
        lead_id: int,
        signals: list[Signal],
        now: datetime | None = None,
    ) -> ScoreResult:
        """
        Calculate the composite score for a lead.

        Steps:
        1. For each active signal, look up its config and apply time decay.
        2. Apply freshness premium to very recent signals.
        3. Sum all decayed signal points.
        4. Check stacking rules for bonus multiplier.
        5. Normalize to 0-100 and assign tier.
        """
        now = now or datetime.utcnow()
        total_points = 0.0
        signal_contributions: dict[str, float] = {}  # signal_type -> points
        active_signal_types: set[str] = set()

        for signal in signals:
            if not signal.is_active:
                continue

            config = self.signal_configs.get(signal.signal_type)
            if config is None or not config.is_active:
                continue

            # Step 1: Apply time decay
            decayed = apply_decay(
                base_points=config.base_points,
                detected_at=signal.detected_at,
                now=now,
                decay_type=config.decay_type,
                half_life_days=config.half_life_days,
            )

            # Step 2: Apply freshness premium
            premium = freshness_premium(signal.detected_at, now)
            adjusted = decayed * premium

            if adjusted > 0:
                active_signal_types.add(signal.signal_type)
                signal_contributions[signal.signal_type] = (
                    signal_contributions.get(signal.signal_type, 0) + adjusted
                )
                total_points += adjusted

        # Step 3: Stacking bonus (best single rule only)
        stacking_bonus, triggered_rules = calculate_stacking_bonus(
            active_signal_types, signal_contributions
        )
        total_points += stacking_bonus

        # Step 4: Freshness bonus tracking (separate from premium above)
        fresh_bonus = sum(
            signal_contributions.get(st, 0) * 0.0  # Premium already applied above
            for st in active_signal_types
        )

        # Step 5: Normalize and assign tier
        normalized = min(self.MAX_SCORE, max(0.0, total_points))
        tier = self._score_to_tier(normalized)

        # Top contributing signal types
        top_signals = sorted(
            signal_contributions.items(), key=lambda x: x[1], reverse=True
        )[:3]

        return ScoreResult(
            lead_id=lead_id,
            raw_score=total_points,
            normalized_score=round(normalized, 1),
            tier=tier,
            signal_count=len(active_signal_types),
            top_signals=[s[0] for s in top_signals],
            stacking_bonus=round(stacking_bonus, 1),
            freshness_bonus=0.0,  # Tracked separately if needed
            recommended_action=self._tier_to_action(tier),
            urgency_label=self._tier_to_urgency(tier),
            next_touch_date=None,  # Set by the pipeline based on tier
        )

    def _score_to_tier(self, score: float) -> Tier:
        if score >= 80:
            return Tier.S
        elif score >= 60:
            return Tier.A
        elif score >= 40:
            return Tier.B
        elif score >= 20:
            return Tier.C
        else:
            return Tier.D

    def _tier_to_action(self, tier: Tier) -> str:
        return {
            Tier.S: "Immediate personal outreach -- phone + handwritten note",
            Tier.A: "Priority outreach within 48 hours -- CMA + call",
            Tier.B: "Scheduled outreach this week -- priority drip campaign",
            Tier.C: "Monthly touch -- standard drip campaign",
            Tier.D: "Monitor only -- no active outreach",
        }[tier]

    def _tier_to_urgency(self, tier: Tier) -> str:
        return {
            Tier.S: "immediate",
            Tier.A: "today",
            Tier.B: "this_week",
            Tier.C: "this_month",
            Tier.D: "monitor",
        }[tier]

    def recalculate_all(
        self,
        leads_with_signals: list[tuple[int, list[Signal]]],
        now: datetime | None = None,
    ) -> list[ScoreResult]:
        """Batch re-score all active leads (called daily or on-demand)."""
        return [
            self.calculate(lead_id, signals, now)
            for lead_id, signals in leads_with_signals
        ]
```

---

## 6. Daily Pipeline Architecture

### 6.1 Pipeline Orchestrator

```python
# theleadedge/pipelines/orchestrator.py
import asyncio
from datetime import datetime, timedelta
from typing import Optional
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import Settings
from theleadedge.sources import ConnectorRegistry
from theleadedge.scoring.engine import ScoringEngine
from theleadedge.storage.database import Database
from theleadedge.storage.repositories import PropertyRepo, LeadRepo, SignalRepo, ScoreHistoryRepo
from theleadedge.notifications.dispatcher import NotificationDispatcher
from .ingest import IngestPipeline
from .detect import SignalDetector
from .score import ScorePipeline
from .deduplicate import Deduplicator
from .briefing import BriefingGenerator

logger = structlog.get_logger()

class DailyPipelineOrchestrator:
    """
    Coordinates the full daily data pipeline.

    Morning workflow (runs at 6:00 AM):
    1. Pull new data from all active sources (MLS, public records, etc.)
    2. Deduplicate and normalize addresses
    3. Detect new signals from raw data
    4. Create or update leads for properties with signals
    5. Score/re-score all active leads
    6. Generate S-tier immediate alerts
    7. Generate daily briefing email for A/B-tier leads
    8. Log sync results for dashboard health monitoring
    """

    def __init__(
        self,
        settings: Settings,
        db: Database,
        connectors: ConnectorRegistry,
        scoring_engine: ScoringEngine,
    ):
        self.settings = settings
        self.db = db
        self.connectors = connectors
        self.scoring = scoring_engine
        self.scheduler = AsyncIOScheduler()

        # Sub-pipelines
        self.ingest = IngestPipeline(db, connectors)
        self.dedup = Deduplicator(db)
        self.detector = SignalDetector(db, scoring_engine.signal_configs)
        self.scorer = ScorePipeline(db, scoring_engine)
        self.briefing = BriefingGenerator(db, settings)
        self.notifications = NotificationDispatcher(settings)

        # Repositories
        self.property_repo = PropertyRepo(db)
        self.lead_repo = LeadRepo(db)
        self.signal_repo = SignalRepo(db)
        self.score_history_repo = ScoreHistoryRepo(db)

    def setup_schedule(self) -> None:
        """Register all scheduled jobs with APScheduler."""

        # === Daily jobs ===
        self.scheduler.add_job(
            self.run_morning_pipeline,
            CronTrigger(hour=6, minute=0),
            id="morning_pipeline",
            name="Morning Data Pipeline",
        )
        self.scheduler.add_job(
            self.run_daily_rescore,
            CronTrigger(hour=6, minute=15),
            id="daily_rescore",
            name="Daily Score Recalculation",
        )
        self.scheduler.add_job(
            self.run_daily_briefing,
            CronTrigger(hour=6, minute=30),
            id="daily_briefing",
            name="Daily Briefing Email",
        )

        # === Weekly jobs ===
        self.scheduler.add_job(
            self.run_public_records_sync,
            CronTrigger(day_of_week="mon", hour=5, minute=0),
            id="weekly_public_records",
            name="Weekly Public Records Sync",
        )

        # === Periodic jobs ===
        self.scheduler.add_job(
            self.run_urgency_decay,
            CronTrigger(hour="*/6"),
            id="urgency_decay",
            name="Urgency Decay (every 6 hours)",
        )

        logger.info("scheduler_configured", job_count=len(self.scheduler.get_jobs()))

    async def run_morning_pipeline(self) -> None:
        """Full morning data pull and processing."""
        run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        log = logger.bind(run_id=run_id, pipeline="morning")
        log.info("pipeline_started")

        started = datetime.utcnow()
        since = started - timedelta(days=1)  # Incremental: last 24 hours

        try:
            # Step 1: Ingest data from all active sources
            ingest_results = await self.ingest.run(since=since)
            new_properties = ingest_results.get("new_properties", [])
            updated_properties = ingest_results.get("updated_properties", [])
            log.info("ingest_complete",
                     new=len(new_properties), updated=len(updated_properties))

            # Step 2: Deduplicate
            dedup_count = await self.dedup.run(new_properties)
            log.info("dedup_complete", merged=dedup_count)

            # Step 3: Detect signals
            new_signals = await self.detector.run(new_properties + updated_properties)
            log.info("signals_detected", count=len(new_signals))

            # Step 4: Create leads for properties with new signals
            new_leads = await self._ensure_leads_exist(new_signals)
            log.info("leads_created", count=len(new_leads))

            # Step 5: Score/re-score affected leads
            score_results = await self.scorer.run_for_leads(
                [s.lead_id for s in new_signals]
            )
            log.info("scoring_complete", scored=len(score_results))

            # Step 6: Immediate alerts for S-tier
            s_tier = [r for r in score_results if r.tier == "S"]
            if s_tier:
                await self.notifications.send_s_tier_alerts(s_tier)
                log.info("s_tier_alerts_sent", count=len(s_tier))

            duration = (datetime.utcnow() - started).total_seconds()
            log.info("pipeline_complete", duration_seconds=round(duration, 1))

        except Exception as e:
            log.error("pipeline_failed", error=str(e), exc_info=True)

    async def run_daily_rescore(self) -> None:
        """Re-score ALL active leads to apply decay and detect tier changes."""
        log = logger.bind(pipeline="rescore")
        log.info("rescore_started")

        active_leads = await self.lead_repo.get_active_leads()
        score_results = await self.scorer.run_for_leads(
            [lead.id for lead in active_leads]
        )

        # Detect tier changes for notifications
        tier_changes = []
        for result in score_results:
            lead = next((l for l in active_leads if l.id == result.lead_id), None)
            if lead and lead.tier != result.tier:
                tier_changes.append((lead, result))

        if tier_changes:
            log.info("tier_changes_detected", count=len(tier_changes))

        log.info("rescore_complete", total=len(score_results))

    async def run_daily_briefing(self) -> None:
        """Generate and send the daily briefing email."""
        log = logger.bind(pipeline="briefing")
        html = await self.briefing.generate()
        await self.notifications.send_daily_briefing(html)
        log.info("briefing_sent")

    async def run_public_records_sync(self) -> None:
        """Weekly public records data pull."""
        log = logger.bind(pipeline="public_records")
        attom = self.connectors.get("attom")
        if attom:
            for zip_code in self.settings.target_zip_codes:
                result = await attom.sync(mode="preforeclosure", zip_code=zip_code)
                log.info("preforeclosure_sync", zip=zip_code, records=result.records_fetched)

    async def run_urgency_decay(self) -> None:
        """Periodic decay application -- re-scores leads to reflect time passing."""
        await self.run_daily_rescore()

    async def _ensure_leads_exist(self, signals: list) -> list:
        """Create Lead records for properties that do not yet have one."""
        new_leads = []
        for signal in signals:
            existing = await self.lead_repo.get_by_property_id(signal.property_id)
            if not existing:
                lead = await self.lead_repo.create(property_id=signal.property_id)
                new_leads.append(lead)
                # Back-fill signal with lead_id
                signal.lead_id = lead.id
        return new_leads

    def start(self) -> None:
        """Start the scheduler. Call from main.py."""
        self.setup_schedule()
        self.scheduler.start()

    def stop(self) -> None:
        self.scheduler.shutdown()
```

### 6.2 Ingestion Pipeline

```python
# theleadedge/pipelines/ingest.py
from datetime import datetime
from typing import Any, Optional
import structlog

from theleadedge.sources import ConnectorRegistry
from theleadedge.sources.base import SyncResult
from theleadedge.storage.database import Database
from theleadedge.storage.repositories import PropertyRepo, SyncLogRepo
from theleadedge.models.property import PropertyCreate
from theleadedge.utils.address import normalize_address

logger = structlog.get_logger()

class IngestPipeline:
    """
    Fetches data from all active connectors, normalizes addresses,
    and upserts into the properties table.
    """

    def __init__(self, db: Database, connectors: ConnectorRegistry):
        self.db = db
        self.connectors = connectors
        self.property_repo = PropertyRepo(db)
        self.sync_log_repo = SyncLogRepo(db)

    async def run(
        self, since: Optional[datetime] = None
    ) -> dict[str, list]:
        """
        Run ingestion for all active data sources.

        Returns:
            {"new_properties": [...], "updated_properties": [...]}
        """
        new_properties = []
        updated_properties = []

        # MLS: fetch multiple query types
        mls = self.connectors.get("mls")
        if mls:
            for query_type in ["expired", "price_reductions", "high_dom", "withdrawn_relisted"]:
                result = await mls.sync(since=since, query_type=query_type)
                await self.sync_log_repo.log(result)

                if result.success:
                    raw = await mls.fetch(since=since, query_type=query_type)
                    transformed = mls.transform(raw)
                    for prop_data in transformed:
                        new, updated = await self._upsert_property(prop_data)
                        if new:
                            new_properties.append(new)
                        elif updated:
                            updated_properties.append(updated)

        return {
            "new_properties": new_properties,
            "updated_properties": updated_properties,
        }

    async def _upsert_property(self, data: dict) -> tuple[Any, Any]:
        """
        Insert or update a property record.

        Matching key: normalized address + zip_code.
        If match found: update changed fields.
        If no match: insert new record.

        Returns (new_property, None) or (None, updated_property).
        """
        data["address_normalized"] = normalize_address(
            data.get("address", ""), data.get("city", ""),
            data.get("state", "AZ"), data.get("zip_code", ""),
        )

        existing = await self.property_repo.find_by_normalized_address(
            data["address_normalized"], data["zip_code"]
        )

        if existing:
            updated = await self.property_repo.update(existing.id, data)
            return None, updated
        else:
            prop_create = PropertyCreate(**data)
            new = await self.property_repo.create(prop_create)
            return new, None
```

### 6.3 Signal Detector

```python
# theleadedge/pipelines/detect.py
from datetime import datetime
from typing import Optional
import structlog

from theleadedge.models.signal import SignalConfig, SignalCreate
from theleadedge.models.enums import SignalCategory
from theleadedge.storage.database import Database
from theleadedge.storage.repositories import SignalRepo

logger = structlog.get_logger()

class SignalDetector:
    """
    Analyzes property data to detect motivation signals.

    Each detection method examines specific data points and creates
    Signal records when criteria are met. Signals are append-only
    and deduplicated by (lead_id, signal_type, event_date).
    """

    def __init__(self, db: Database, signal_configs: dict[str, SignalConfig]):
        self.db = db
        self.signal_repo = SignalRepo(db)
        self.configs = signal_configs

    async def run(self, properties: list) -> list:
        """Detect signals for a batch of properties."""
        all_signals = []
        for prop in properties:
            signals = await self._detect_for_property(prop)
            all_signals.extend(signals)
        logger.info("signal_detection_complete", total=len(all_signals))
        return all_signals

    async def _detect_for_property(self, prop) -> list:
        """Run all detection rules against a single property."""
        detected = []

        # Expired listing
        if prop.mls_status == "Expired":
            detected.append(self._make_signal(
                prop, "expired_listing",
                f"Listing expired after {prop.days_on_market or '?'} DOM",
            ))

        # Price reductions
        if prop.original_list_price and prop.list_price:
            if prop.list_price < prop.original_list_price:
                reduction_pct = (
                    (prop.original_list_price - prop.list_price)
                    / prop.original_list_price * 100
                )
                detected.append(self._make_signal(
                    prop, "price_reduction",
                    f"Price reduced {reduction_pct:.1f}%: "
                    f"${prop.original_list_price:,} -> ${prop.list_price:,}",
                ))

            # 3+ reductions
            if hasattr(prop, "price_change_count") and prop.price_change_count >= 3:
                detected.append(self._make_signal(
                    prop, "price_reduction_3plus",
                    f"{prop.price_change_count} price reductions totaling "
                    f"${prop.original_list_price - prop.list_price:,}",
                ))

        # High DOM thresholds
        dom = prop.days_on_market or 0
        if dom >= 180:
            detected.append(self._make_signal(
                prop, "high_dom_180", f"{dom} days on market (severely stale)",
            ))
        elif dom >= 120:
            detected.append(self._make_signal(
                prop, "high_dom_120", f"{dom} days on market",
            ))
        elif dom >= 90:
            detected.append(self._make_signal(
                prop, "high_dom_90", f"{dom} days on market",
            ))

        # Withdrawn and relisted (CDOM > DOM = DOM was reset)
        cdom = getattr(prop, "cumulative_dom", None) or 0
        if cdom > dom > 0:
            detected.append(self._make_signal(
                prop, "withdrawn_relisted",
                f"CDOM {cdom} > DOM {dom} -- listing was reset (agent change likely)",
            ))

        # Absentee owner
        if prop.is_absentee:
            detected.append(self._make_signal(
                prop, "absentee_owner",
                f"Owner mailing address differs from property",
            ))

        # Long-term owner
        if prop.ownership_years and prop.ownership_years >= 20:
            detected.append(self._make_signal(
                prop, "long_term_owner",
                f"Owned for {prop.ownership_years:.0f} years",
            ))

        # Deduplicate against existing signals before persisting
        new_signals = []
        for sig_data in detected:
            exists = await self.signal_repo.exists(
                property_id=prop.id,
                signal_type=sig_data["signal_type"],
                event_date=sig_data.get("event_date"),
            )
            if not exists:
                signal = await self.signal_repo.create(SignalCreate(**sig_data))
                new_signals.append(signal)

        return new_signals

    def _make_signal(self, prop, signal_type: str, description: str) -> dict:
        """Build signal creation dict from property and config."""
        config = self.configs.get(signal_type)
        return {
            "property_id": prop.id,
            "lead_id": 0,  # Will be set after lead creation
            "signal_type": signal_type,
            "signal_category": config.category if config else SignalCategory.MLS,
            "base_points": config.base_points if config else 0,
            "decay_type": config.decay_type if config else "linear",
            "half_life_days": config.half_life_days if config else 30,
            "description": description,
            "source": prop.data_source if hasattr(prop, "data_source") else "unknown",
            "event_date": datetime.utcnow().date(),
        }
```

### 6.4 Daily Briefing Generator

```python
# theleadedge/pipelines/briefing.py
from datetime import datetime, timedelta
from pathlib import Path
import structlog
from jinja2 import Environment, FileSystemLoader

from config.settings import Settings
from theleadedge.storage.database import Database
from theleadedge.storage.repositories import LeadRepo, SignalRepo, ScoreHistoryRepo

logger = structlog.get_logger()

class BriefingGenerator:
    """
    Generates the daily morning briefing HTML email.

    Contents:
    - New S-tier and A-tier leads (immediate action items)
    - Score movers (leads that jumped tiers since yesterday)
    - Pipeline summary (counts by tier)
    - Today's follow-ups (leads with next_touch_date = today)
    - Data source health status
    """

    def __init__(self, db: Database, settings: Settings):
        self.db = db
        self.settings = settings
        self.lead_repo = LeadRepo(db)
        self.signal_repo = SignalRepo(db)
        self.score_history_repo = ScoreHistoryRepo(db)

        template_dir = Path(__file__).parent.parent / "notifications" / "templates"
        self.jinja = Environment(loader=FileSystemLoader(str(template_dir)))

    async def generate(self) -> str:
        """Generate the briefing HTML."""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        # Gather data for the briefing
        new_hot_leads = await self.lead_repo.get_leads_by_tier(
            tiers=["S", "A"], since=yesterday
        )
        tier_movers = await self.score_history_repo.get_tier_changes(since=yesterday)
        pipeline_counts = await self.lead_repo.get_pipeline_summary()
        todays_followups = await self.lead_repo.get_followups_due(date=now.date())

        # Render HTML template
        template = self.jinja.get_template("daily_briefing.html")
        html = template.render(
            date=now.strftime("%A, %B %d, %Y"),
            new_hot_leads=new_hot_leads,
            tier_movers=tier_movers,
            pipeline=pipeline_counts,
            followups=todays_followups,
            total_active=sum(pipeline_counts.values()),
        )

        return html
```

---

## 7. Database Schema & Migrations

### 7.1 SQLAlchemy Table Definitions

```python
# theleadedge/storage/database.py
from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import (
    Column, Integer, Float, String, Boolean, Date, DateTime, Text,
    ForeignKey, Index, UniqueConstraint, event,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship

from config.settings import Settings

class Base(DeclarativeBase):
    pass

# ---- Table Definitions ----

class PropertyTable(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, nullable=False)
    address_normalized = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False, default="AZ")
    zip_code = Column(String, nullable=False, index=True)
    county = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    # Property details
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    sqft = Column(Integer)
    lot_sqft = Column(Integer)
    year_built = Column(Integer)
    property_type = Column(String)

    # Valuation
    list_price = Column(Integer)
    original_list_price = Column(Integer)
    estimated_value = Column(Integer)
    estimated_equity = Column(Integer)
    last_sold_price = Column(Integer)
    last_sold_date = Column(Date)

    # MLS
    mls_number = Column(String, unique=True)
    mls_status = Column(String)
    days_on_market = Column(Integer)
    cumulative_dom = Column(Integer)
    list_date = Column(Date)
    expiration_date = Column(Date)
    status_change_date = Column(Date)
    listing_agent = Column(String)
    listing_office = Column(String)
    price_change_count = Column(Integer, default=0)

    # Owner
    owner_name = Column(String)
    owner_first_name = Column(String)
    owner_last_name = Column(String)
    owner_phone = Column(String)
    owner_email = Column(String)
    owner_mailing_address = Column(String)
    is_absentee = Column(Boolean, default=False)
    is_corporate = Column(Boolean, default=False)
    ownership_years = Column(Float)

    # Metadata
    data_source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lead = relationship("LeadTable", back_populates="property", uselist=False)
    signals = relationship("SignalTable", back_populates="property")

    __table_args__ = (
        UniqueConstraint("address_normalized", "zip_code", name="uq_property_addr_zip"),
        Index("idx_properties_geo", "latitude", "longitude"),
    )


class LeadTable(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), unique=True, nullable=False)

    # Scoring
    current_score = Column(Float, default=0, nullable=False)
    previous_score = Column(Float)
    tier = Column(String(1), default="D", nullable=False)
    signal_count = Column(Integer, default=0)
    priority_rank = Column(Integer)

    # Status
    status = Column(String, default="new")
    is_active = Column(Boolean, default=True)

    # Engagement
    contacted_at = Column(DateTime)
    last_touch_at = Column(DateTime)
    next_touch_date = Column(DateTime)
    contact_attempts = Column(Integer, default=0)

    # CRM
    crm_id = Column(String)
    crm_synced_at = Column(DateTime)

    # AI
    summary = Column(Text)

    # Metadata
    detected_at = Column(DateTime, default=datetime.utcnow)
    scored_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    property = relationship("PropertyTable", back_populates="lead")
    signals = relationship("SignalTable", back_populates="lead")
    activities = relationship("ActivityTable", back_populates="lead")
    score_history = relationship("ScoreHistoryTable", back_populates="lead")

    __table_args__ = (
        Index("idx_leads_score", "current_score", postgresql_where="is_active = true"),
        Index("idx_leads_tier", "tier", postgresql_where="is_active = true"),
        Index("idx_leads_status", "status", postgresql_where="is_active = true"),
    )


class SignalTable(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)

    signal_type = Column(String, nullable=False)
    signal_category = Column(String, nullable=False)
    base_points = Column(Float, nullable=False)
    points = Column(Float, default=0)       # Current decayed value
    weight = Column(Float, default=1.0)
    decay_type = Column(String, default="linear")
    half_life_days = Column(Float, default=30)

    description = Column(Text)
    source = Column(String)
    source_ref = Column(String)
    raw_data = Column(Text)  # JSON string

    detected_at = Column(DateTime, default=datetime.utcnow)
    event_date = Column(Date)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    lead = relationship("LeadTable", back_populates="signals")
    property = relationship("PropertyTable", back_populates="signals")

    __table_args__ = (
        UniqueConstraint("lead_id", "signal_type", "event_date", name="uq_signal_lead_type_date"),
        Index("idx_signals_lead", "lead_id", postgresql_where="is_active = true"),
        Index("idx_signals_type", "signal_type"),
    )


class ScoreHistoryTable(Base):
    __tablename__ = "score_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    score = Column(Float, nullable=False)
    tier = Column(String(1), nullable=False)
    signal_count = Column(Integer)
    change_reason = Column(Text)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("LeadTable", back_populates="score_history")

    __table_args__ = (
        Index("idx_score_history_lead", "lead_id", "calculated_at"),
    )


class ActivityTable(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    activity_type = Column(String, nullable=False)
    description = Column(Text)
    outcome = Column(String)
    performed_by = Column(String, default="sarah")
    performed_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("LeadTable", back_populates="activities")

    __table_args__ = (
        Index("idx_activities_lead", "lead_id", "performed_at"),
    )


class PriceHistoryTable(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    price = Column(Integer, nullable=False)
    price_change = Column(Integer)
    change_pct = Column(Float)
    change_date = Column(Date, nullable=False)
    source = Column(String, default="MLS")

    __table_args__ = (
        UniqueConstraint("property_id", "change_date", "price", name="uq_price_prop_date_price"),
        Index("idx_price_history_prop", "property_id", "change_date"),
    )


class SyncLogTable(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)
    job_type = Column(String, nullable=False)
    success = Column(Boolean, nullable=False)
    records_fetched = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    started_at = Column(DateTime)
    completed_at = Column(DateTime, default=datetime.utcnow)


# ---- Database Engine ----

class Database:
    """Async database engine and session factory."""

    def __init__(self, settings: Settings):
        self.engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def create_tables(self) -> None:
        """Create all tables (development only -- use Alembic in production)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def close(self) -> None:
        await self.engine.dispose()
```

### 7.2 Alembic Migration Setup

```python
# alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from config.settings import Settings
from theleadedge.storage.database import Base

# Load settings
settings = Settings()
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode -- generates SQL scripts."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 7.3 Migration Path: SQLite to PostgreSQL

The system starts with SQLite for zero-ops simplicity. When scaling requires it, migrate to PostgreSQL.

**When to migrate:**
- Multiple concurrent users accessing the dashboard
- Need for PostGIS geospatial queries (radius search, polygon filtering)
- Database exceeds 50,000 lead records
- Need for streaming replication or point-in-time recovery

**Migration steps:**
1. Update `DATABASE_URL` in `.env` from `sqlite+aiosqlite:///./data/theleadedge.db` to `postgresql+asyncpg://user:pass@host/theleadedge`
2. Replace `aiosqlite` dependency with `asyncpg`
3. Run `alembic upgrade head` against the new PostgreSQL database
4. Use `pgloader` or a custom script to migrate existing SQLite data
5. Update partial index syntax (SQLite uses `WHERE` in `CREATE INDEX`, PostgreSQL uses `WHERE` in `CREATE INDEX` with slightly different syntax -- Alembic handles this)

```ini
# alembic.ini (key settings)
[alembic]
script_location = alembic
# SQLite (default)
sqlalchemy.url = sqlite+aiosqlite:///./data/theleadedge.db
# PostgreSQL (uncomment when ready)
# sqlalchemy.url = postgresql+asyncpg://theleadedge:password@localhost/theleadedge
```

---

## 8. Configuration Management

### 8.1 Environment-Based Settings (Pydantic Settings)

```python
# config/settings.py
from pathlib import Path
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and .env file.

    Priority order (highest to lowest):
    1. Environment variables
    2. .env file
    3. Default values defined here

    Secrets use SecretStr to prevent accidental logging.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = "TheLeadEdge"
    app_env: str = "development"  # development | staging | production
    debug: bool = True
    log_level: str = "INFO"
    log_format: str = "json"  # "json" for production, "console" for dev

    # ---- Database ----
    database_url: str = "sqlite+aiosqlite:///./data/theleadedge.db"
    database_echo: bool = False  # Log all SQL statements (noisy, dev only)

    # ---- MLS / RESO API ----
    mls_base_url: Optional[str] = None
    mls_token_url: Optional[str] = None
    mls_client_id: Optional[str] = None
    mls_client_secret: Optional[SecretStr] = None
    mls_csv_import_dir: str = "./data/mls_imports"

    # ---- ATTOM Property Data ----
    attom_api_key: Optional[SecretStr] = None

    # ---- Skip Tracing (BatchLeads) ----
    batch_leads_api_key: Optional[SecretStr] = None

    # ---- REDX Expired Feeds ----
    redx_api_key: Optional[SecretStr] = None

    # ---- CRM (Follow Up Boss) ----
    fub_api_key: Optional[SecretStr] = None
    fub_base_url: str = "https://api.followupboss.com/v1"

    # ---- AI (Claude API for summaries) ----
    anthropic_api_key: Optional[SecretStr] = None

    # ---- Email Notifications ----
    email_provider: str = "smtp"  # "smtp" or "sendgrid"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[SecretStr] = None
    sendgrid_api_key: Optional[SecretStr] = None
    email_from: str = "theleadedge@yourdomain.com"
    email_to: str = "sarah@yourdomain.com"  # Daily briefing recipient

    # ---- Dashboard ----
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 8080
    dashboard_username: str = "sarah"
    dashboard_password_hash: Optional[str] = None
    secret_key: str = "change-me-in-production"

    # ---- Feature Flags ----
    feature_mls_api_enabled: bool = False   # Start with CSV import
    feature_attom_enabled: bool = False
    feature_skip_trace_enabled: bool = False
    feature_redx_enabled: bool = False
    feature_crm_sync_enabled: bool = False
    feature_ai_summaries_enabled: bool = False
    feature_email_notifications_enabled: bool = True

    # ---- Target Geography ----
    target_zip_codes: list[str] = Field(
        default=["85281", "85282", "85283", "85284"],
        description="ZIP codes to monitor for leads",
    )
    target_state: str = "AZ"

    # ---- Scoring ----
    scoring_config_path: str = "config/scoring_weights.yaml"
    max_lead_score: float = 100.0

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
```

### 8.2 .env Example File

```bash
# .env.example
# Copy to .env and fill in your values. NEVER commit .env to git.

# Application
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=generate-a-random-string-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/theleadedge.db
# DATABASE_URL=postgresql+asyncpg://theleadedge:password@localhost/theleadedge

# MLS / RESO API (Phase 3+)
# MLS_BASE_URL=https://api.mlsboard.com/reso/odata
# MLS_TOKEN_URL=https://api.mlsboard.com/oauth2/token
# MLS_CLIENT_ID=your_client_id
# MLS_CLIENT_SECRET=your_client_secret

# MLS CSV Import (Phase 1-2 fallback)
MLS_CSV_IMPORT_DIR=./data/mls_imports

# ATTOM Property Data (Phase 4+)
# ATTOM_API_KEY=your_attom_api_key

# Skip Tracing - BatchLeads (Phase 3+)
# BATCH_LEADS_API_KEY=your_batch_leads_key

# CRM - Follow Up Boss (Phase 2+)
# FUB_API_KEY=your_fub_api_key

# AI - Claude API (Phase 4+)
# ANTHROPIC_API_KEY=your_anthropic_key

# Email Notifications
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=theleadedge@yourdomain.com
EMAIL_TO=sarah@yourdomain.com

# Dashboard
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8080
DASHBOARD_USERNAME=sarah

# Feature Flags (enable as you add integrations)
FEATURE_MLS_API_ENABLED=false
FEATURE_ATTOM_ENABLED=false
FEATURE_SKIP_TRACE_ENABLED=false
FEATURE_CRM_SYNC_ENABLED=false
FEATURE_AI_SUMMARIES_ENABLED=false
FEATURE_EMAIL_NOTIFICATIONS_ENABLED=true

# Target Geography
TARGET_ZIP_CODES=["85281","85282","85283","85284"]
TARGET_STATE=AZ
```

### 8.3 Feature Flags (YAML)

```yaml
# config/feature_flags.yaml
#
# Fine-grained control over what runs.
# Separate from env-based flags for features that need
# more context than a simple boolean.

data_sources:
  mls_api:
    enabled: false
    note: "Enable after receiving RESO API credentials from MLS board"
  mls_csv:
    enabled: true
    note: "Fallback: import saved search CSV exports"
  attom:
    enabled: false
    note: "Enable after subscribing to ATTOM (~$250/mo)"
  skip_trace:
    enabled: false
    note: "Enable after subscribing to BatchLeads (~$99/mo)"
  redx:
    enabled: false
    note: "Enable after subscribing to REDX (~$60/mo)"

integrations:
  crm_push:
    enabled: false
    note: "Push leads to Follow Up Boss"
  crm_pull:
    enabled: false
    note: "Pull status updates from Follow Up Boss"
  ai_summaries:
    enabled: false
    note: "Generate AI lead summaries via Claude API"
  direct_mail:
    enabled: false
    note: "Send physical mail via Click2Mail"

notifications:
  s_tier_immediate_alert:
    enabled: true
    note: "Send email immediately when S-tier lead detected"
  daily_briefing:
    enabled: true
    note: "Morning briefing email at 6:30 AM"
  weekly_summary:
    enabled: true
    note: "Weekly performance summary on Monday"

pipeline:
  auto_skip_trace_new_leads:
    enabled: false
    note: "Automatically skip-trace new S/A tier leads"
  auto_enrich_properties:
    enabled: false
    note: "Auto-enrich with ATTOM data on detection"
  auto_geocode:
    enabled: true
    note: "Geocode new properties via Census Bureau (free)"
```

---

## 9. Error Handling & Resilience

### 9.1 Retry Logic with Exponential Backoff

```python
# theleadedge/utils/retry.py
import asyncio
from functools import wraps
from typing import Any, Callable, Type
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryCallState,
)
import httpx

logger = structlog.get_logger()

# Pre-built retry decorator for HTTP API calls
api_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type((
        httpx.TimeoutException,
        httpx.HTTPStatusError,
        ConnectionError,
    )),
    before_sleep=before_sleep_log(logger, "WARNING"),
    reraise=True,
)

# Gentler retry for non-critical operations
gentle_retry = retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=15),
    retry=retry_if_exception_type((httpx.TimeoutException, ConnectionError)),
    reraise=True,
)
```

### 9.2 Circuit Breaker for External Services

```python
# theleadedge/utils/rate_limit.py
import asyncio
import time
from dataclasses import dataclass, field
from enum import StrEnum
import structlog

logger = structlog.get_logger()

class CircuitState(StrEnum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject calls immediately
    HALF_OPEN = "half_open" # Testing if service recovered

@dataclass
class CircuitBreaker:
    """
    Circuit breaker pattern for external API calls.

    Prevents cascading failures when an external service is down.
    After `failure_threshold` consecutive failures, the circuit opens
    and all calls are rejected for `recovery_timeout` seconds.
    Then it enters half-open state and lets one call through to test.

    Usage:
        breaker = CircuitBreaker(name="attom", failure_threshold=5)

        if breaker.can_execute():
            try:
                result = await call_attom_api()
                breaker.record_success()
            except Exception as e:
                breaker.record_failure()
                raise
        else:
            logger.warning("circuit_open", service="attom")
            # Use cached data or skip this source
    """
    name: str
    failure_threshold: int = 5
    recovery_timeout: float = 300.0  # 5 minutes
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0
    success_count: int = 0

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time.monotonic() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("circuit_half_open", service=self.name)
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True  # Allow one test call
        return False

    def record_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info("circuit_closed", service=self.name)
        self.success_count += 1

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.monotonic()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("circuit_reopened", service=self.name)
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("circuit_opened", service=self.name,
                         failures=self.failure_count)

    def reset(self) -> None:
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
```

### 9.3 Graceful Degradation

```python
# theleadedge/pipelines/ingest.py (additional method)

async def run_with_degradation(self, since=None) -> dict:
    """
    Run ingestion with graceful degradation.

    If a data source fails, log the error and continue with
    other sources. The pipeline should never fail entirely
    because one external service is down.
    """
    results = {"new_properties": [], "updated_properties": [], "errors": []}

    sources_to_run = [
        ("mls", ["expired", "price_reductions", "high_dom"]),
        ("attom", ["preforeclosure"]),
    ]

    for source_name, query_types in sources_to_run:
        connector = self.connectors.get(source_name)
        if connector is None:
            continue

        # Check circuit breaker
        breaker = self._breakers.get(source_name)
        if breaker and not breaker.can_execute():
            logger.warning("source_skipped_circuit_open", source=source_name)
            results["errors"].append(f"{source_name}: circuit breaker open")
            continue

        try:
            for query_type in query_types:
                sync_result = await connector.sync(
                    since=since, query_type=query_type
                )
                if sync_result.success:
                    if breaker:
                        breaker.record_success()
                    # Process results...
                else:
                    if breaker:
                        breaker.record_failure()
                    results["errors"].append(
                        f"{source_name}/{query_type}: {sync_result.errors}"
                    )
        except Exception as e:
            if breaker:
                breaker.record_failure()
            results["errors"].append(f"{source_name}: {str(e)}")
            logger.error("source_failed", source=source_name, error=str(e))
            # Continue to next source -- do not abort pipeline

    if results["errors"]:
        logger.warning("pipeline_degraded", error_count=len(results["errors"]))

    return results
```

### 9.4 Structured Logging Setup

```python
# theleadedge/utils/logging.py
import logging
import sys
import structlog
from config.settings import Settings

def setup_logging(settings: Settings) -> None:
    """
    Configure structured logging for the application.

    Development: Human-readable colored console output.
    Production: JSON-formatted logs for log aggregation tools.
    """

    # Shared processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.log_format == "json":
        # Production: JSON output
        renderer = structlog.processors.JSONRenderer()
    else:
        # Development: colored console output
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.database_echo else logging.WARNING
    )
```

### 9.5 Correlation IDs for Request Tracing

```python
# Usage in pipeline runs -- bind a correlation ID for tracing
import uuid
import structlog

structlog.contextvars.clear_contextvars()
structlog.contextvars.bind_contextvars(
    run_id=str(uuid.uuid4())[:8],
    pipeline="morning",
)

logger = structlog.get_logger()
logger.info("pipeline_started")
# Output: {"run_id": "a1b2c3d4", "pipeline": "morning", "event": "pipeline_started", ...}
```

---

## 10. Testing Strategy

### 10.1 Test Configuration

```python
# tests/conftest.py
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from theleadedge.storage.database import Base, Database
from theleadedge.scoring.engine import ScoringEngine
from config.settings import Settings

@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for all async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def settings() -> Settings:
    """Test settings with in-memory database and features disabled."""
    return Settings(
        app_env="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        database_echo=False,
        feature_mls_api_enabled=False,
        feature_attom_enabled=False,
        feature_skip_trace_enabled=False,
        feature_crm_sync_enabled=False,
        feature_ai_summaries_enabled=False,
        feature_email_notifications_enabled=False,
        scoring_config_path="config/scoring_weights.yaml",
    )

@pytest_asyncio.fixture
async def db(settings) -> AsyncGenerator[Database, None]:
    """In-memory test database, tables created fresh for each test."""
    database = Database(settings)
    await database.create_tables()
    yield database
    await database.close()

@pytest_asyncio.fixture
async def session(db) -> AsyncGenerator[AsyncSession, None]:
    """Database session for a single test."""
    async for s in db.get_session():
        yield s

@pytest.fixture
def scoring_engine() -> ScoringEngine:
    """Scoring engine loaded with default test weights."""
    return ScoringEngine(config_path="config/scoring_weights.yaml")

@pytest.fixture
def now() -> datetime:
    """Fixed 'now' timestamp for deterministic tests."""
    return datetime(2026, 2, 28, 8, 0, 0)
```

### 10.2 Test Factories (Factory Boy)

```python
# tests/factories.py
from datetime import datetime, timedelta, date
import factory
from theleadedge.models.property import Property
from theleadedge.models.lead import Lead
from theleadedge.models.signal import Signal
from theleadedge.models.enums import (
    Tier, LeadStatus, SignalCategory, DecayType, MLSStatus,
)

class PropertyFactory(factory.Factory):
    class Meta:
        model = Property

    id = factory.Sequence(lambda n: n + 1)
    address = factory.Faker("street_address")
    address_normalized = factory.LazyAttribute(
        lambda o: o.address.upper().replace(".", "").strip()
    )
    city = "Phoenix"
    state = "AZ"
    zip_code = factory.Iterator(["85281", "85282", "85283", "85284"])
    bedrooms = factory.Faker("random_int", min=2, max=5)
    bathrooms = factory.Faker("pyfloat", min_value=1, max_value=4, right_digits=1)
    sqft = factory.Faker("random_int", min=1000, max=4000)
    year_built = factory.Faker("random_int", min=1960, max=2024)
    property_type = "SFR"
    list_price = factory.Faker("random_int", min=200000, max=800000)
    original_list_price = factory.LazyAttribute(
        lambda o: o.list_price + factory.Faker("random_int", min=10000, max=50000).evaluate(None, None, {"locale": None})
    )
    mls_number = factory.Sequence(lambda n: f"MLS-{n:06d}")
    mls_status = MLSStatus.EXPIRED
    days_on_market = factory.Faker("random_int", min=30, max=200)
    listing_agent = factory.Faker("name")
    listing_office = factory.Faker("company")
    data_source = "mls_reso"
    is_absentee = False
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class LeadFactory(factory.Factory):
    class Meta:
        model = Lead

    id = factory.Sequence(lambda n: n + 1)
    property_id = factory.Sequence(lambda n: n + 1)
    current_score = 0.0
    tier = Tier.D
    signal_count = 0
    status = LeadStatus.NEW
    is_active = True
    detected_at = factory.LazyFunction(datetime.utcnow)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class SignalFactory(factory.Factory):
    class Meta:
        model = Signal

    id = factory.Sequence(lambda n: n + 1)
    lead_id = factory.Sequence(lambda n: n + 1)
    property_id = factory.Sequence(lambda n: n + 1)
    signal_type = "expired_listing"
    signal_category = SignalCategory.MLS
    base_points = 15.0
    points = 15.0
    weight = 1.0
    decay_type = DecayType.EXPONENTIAL
    half_life_days = 21.0
    description = "Listing expired after 95 DOM"
    source = "mls_reso"
    detected_at = factory.LazyFunction(datetime.utcnow)
    event_date = factory.LazyFunction(lambda: date.today())
    is_active = True
```

### 10.3 Unit Tests: Scoring Engine

```python
# tests/unit/test_scoring.py
from datetime import datetime, timedelta
import pytest
from theleadedge.scoring.engine import ScoringEngine
from theleadedge.models.enums import Tier, DecayType, SignalCategory
from tests.factories import SignalFactory

class TestScoringEngine:
    """Test the core scoring engine logic."""

    def test_empty_signals_returns_zero(self, scoring_engine, now):
        result = scoring_engine.calculate(lead_id=1, signals=[], now=now)
        assert result.normalized_score == 0
        assert result.tier == Tier.D

    def test_single_expired_signal_scores_correctly(self, scoring_engine, now):
        signal = SignalFactory(
            signal_type="expired_listing",
            detected_at=now,  # Just detected -- no decay
        )
        result = scoring_engine.calculate(lead_id=1, signals=[signal], now=now)
        # base_points=15, freshness premium=1.5 (within 4 hours) = 22.5
        assert result.normalized_score == pytest.approx(22.5, abs=1.0)
        assert result.tier == Tier.C

    def test_multiple_signals_stack_additively(self, scoring_engine, now):
        signals = [
            SignalFactory(signal_type="expired_listing", detected_at=now),
            SignalFactory(signal_type="pre_foreclosure", detected_at=now),
            SignalFactory(signal_type="absentee_owner", detected_at=now),
        ]
        result = scoring_engine.calculate(lead_id=1, signals=signals, now=now)
        # 15 + 20 + 8 = 43 base, x1.5 freshness = 64.5
        assert result.normalized_score > 40
        assert result.tier in (Tier.A, Tier.B)

    def test_old_signals_decay(self, scoring_engine, now):
        old = now - timedelta(days=60)
        signal = SignalFactory(
            signal_type="expired_listing",
            detected_at=old,
        )
        result = scoring_engine.calculate(lead_id=1, signals=[signal], now=now)
        # 60 days old with 21-day half-life: 15 * 0.5^(60/21) = ~1.9
        assert result.normalized_score < 5
        assert result.tier == Tier.D

    def test_s_tier_from_stacked_signals(self, scoring_engine, now):
        signals = [
            SignalFactory(signal_type="pre_foreclosure", base_points=20, detected_at=now),
            SignalFactory(signal_type="tax_delinquent", base_points=13, detected_at=now),
            SignalFactory(signal_type="expired_listing", base_points=15, detected_at=now),
            SignalFactory(signal_type="absentee_owner", base_points=8, detected_at=now),
            SignalFactory(signal_type="vacant_property", base_points=6, detected_at=now),
        ]
        result = scoring_engine.calculate(lead_id=1, signals=signals, now=now)
        # High signal convergence should push into S-tier
        assert result.normalized_score >= 80
        assert result.tier == Tier.S

    def test_inactive_signals_are_ignored(self, scoring_engine, now):
        signals = [
            SignalFactory(signal_type="expired_listing", detected_at=now, is_active=True),
            SignalFactory(signal_type="pre_foreclosure", detected_at=now, is_active=False),
        ]
        result = scoring_engine.calculate(lead_id=1, signals=signals, now=now)
        # Only one active signal should contribute
        assert result.signal_count == 1

    def test_score_capped_at_100(self, scoring_engine, now):
        # Create many high-value signals
        signals = [
            SignalFactory(signal_type="pre_foreclosure", detected_at=now),
            SignalFactory(signal_type="probate", detected_at=now),
            SignalFactory(signal_type="divorce", detected_at=now),
            SignalFactory(signal_type="expired_listing", detected_at=now),
            SignalFactory(signal_type="tax_delinquent", detected_at=now),
            SignalFactory(signal_type="code_violation", detected_at=now),
            SignalFactory(signal_type="absentee_owner", detected_at=now),
            SignalFactory(signal_type="vacant_property", detected_at=now),
        ]
        result = scoring_engine.calculate(lead_id=1, signals=signals, now=now)
        assert result.normalized_score <= 100.0

    def test_tier_boundaries(self, scoring_engine):
        assert scoring_engine._score_to_tier(100) == Tier.S
        assert scoring_engine._score_to_tier(80) == Tier.S
        assert scoring_engine._score_to_tier(79.9) == Tier.A
        assert scoring_engine._score_to_tier(60) == Tier.A
        assert scoring_engine._score_to_tier(59.9) == Tier.B
        assert scoring_engine._score_to_tier(40) == Tier.B
        assert scoring_engine._score_to_tier(39.9) == Tier.C
        assert scoring_engine._score_to_tier(20) == Tier.C
        assert scoring_engine._score_to_tier(19.9) == Tier.D
        assert scoring_engine._score_to_tier(0) == Tier.D
```

### 10.4 Unit Tests: Decay Functions

```python
# tests/unit/test_decay.py
from datetime import datetime, timedelta
import pytest
from theleadedge.scoring.decay import apply_decay, freshness_premium
from theleadedge.models.enums import DecayType

class TestLinearDecay:
    def test_no_decay_at_time_zero(self):
        now = datetime(2026, 3, 1)
        result = apply_decay(10.0, detected_at=now, now=now,
                           decay_type=DecayType.LINEAR, half_life_days=30)
        assert result == 10.0

    def test_half_value_at_half_life(self):
        now = datetime(2026, 3, 1)
        detected = now - timedelta(days=30)
        result = apply_decay(10.0, detected_at=detected, now=now,
                           decay_type=DecayType.LINEAR, half_life_days=30)
        assert result == pytest.approx(5.0, abs=0.1)

    def test_zero_at_double_half_life(self):
        now = datetime(2026, 3, 1)
        detected = now - timedelta(days=60)
        result = apply_decay(10.0, detected_at=detected, now=now,
                           decay_type=DecayType.LINEAR, half_life_days=30)
        assert result == 0.0

    def test_stays_zero_after_expiry(self):
        now = datetime(2026, 3, 1)
        detected = now - timedelta(days=120)
        result = apply_decay(10.0, detected_at=detected, now=now,
                           decay_type=DecayType.LINEAR, half_life_days=30)
        assert result == 0.0


class TestExponentialDecay:
    def test_no_decay_at_time_zero(self):
        now = datetime(2026, 3, 1)
        result = apply_decay(15.0, detected_at=now, now=now,
                           decay_type=DecayType.EXPONENTIAL, half_life_days=21)
        assert result == 15.0

    def test_half_value_at_half_life(self):
        now = datetime(2026, 3, 1)
        detected = now - timedelta(days=21)
        result = apply_decay(15.0, detected_at=detected, now=now,
                           decay_type=DecayType.EXPONENTIAL, half_life_days=21)
        assert result == pytest.approx(7.5, abs=0.1)

    def test_never_reaches_zero(self):
        now = datetime(2026, 3, 1)
        detected = now - timedelta(days=365)
        result = apply_decay(15.0, detected_at=detected, now=now,
                           decay_type=DecayType.EXPONENTIAL, half_life_days=21)
        assert result > 0  # Exponential decay approaches but never hits zero


class TestStepDecay:
    @pytest.mark.parametrize("days,expected_mult", [
        (0, 1.0), (3, 1.0), (7, 1.0),
        (8, 0.75), (14, 0.75), (30, 0.75),
        (31, 0.50), (60, 0.50), (90, 0.50),
        (91, 0.25), (120, 0.25), (180, 0.25),
        (181, 0.05), (365, 0.05),
    ])
    def test_step_boundaries(self, days, expected_mult):
        now = datetime(2026, 3, 1)
        detected = now - timedelta(days=days)
        result = apply_decay(20.0, detected_at=detected, now=now,
                           decay_type=DecayType.STEP)
        assert result == pytest.approx(20.0 * expected_mult, abs=0.01)


class TestFreshnessPremium:
    @pytest.mark.parametrize("hours,expected", [
        (0, 1.5), (2, 1.5), (4, 1.5),
        (5, 1.3), (12, 1.3), (24, 1.3),
        (25, 1.15), (36, 1.15), (48, 1.15),
        (49, 1.0), (100, 1.0),
    ])
    def test_premium_tiers(self, hours, expected):
        now = datetime(2026, 3, 1)
        detected = now - timedelta(hours=hours)
        result = freshness_premium(detected, now)
        assert result == expected
```

### 10.5 Integration Tests: Connectors (with Mocking)

```python
# tests/integration/test_mls_connector.py
import pytest
import httpx
from unittest.mock import AsyncMock, patch
from datetime import datetime

from theleadedge.sources.mls import MLSConnector
from config.settings import Settings

@pytest.fixture
def mls_settings():
    return Settings(
        mls_base_url="https://api.testmls.com/reso/odata",
        mls_token_url="https://api.testmls.com/oauth2/token",
        mls_client_id="test_client",
        mls_client_secret="test_secret",
    )

@pytest.fixture
def mls_connector(mls_settings):
    return MLSConnector(mls_settings)

class TestMLSConnector:

    @pytest.mark.asyncio
    async def test_authenticate_stores_token(self, mls_connector):
        mock_response = httpx.Response(
            200,
            json={"access_token": "test_token_123", "expires_in": 3600},
        )
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            await mls_connector.authenticate()
            assert mls_connector.access_token == "test_token_123"
            assert mls_connector._is_authenticated is True

    @pytest.mark.asyncio
    async def test_fetch_expired_returns_properties(self, mls_connector):
        mls_connector.access_token = "test_token"
        mls_connector._is_authenticated = True

        mock_data = {
            "value": [
                {
                    "ListingKey": "12345",
                    "ListingId": "MLS-001",
                    "StandardStatus": "Expired",
                    "ListPrice": 425000,
                    "OriginalListPrice": 475000,
                    "DaysOnMarket": 142,
                    "CumulativeDaysOnMarket": 142,
                    "City": "Phoenix",
                    "StateOrProvince": "AZ",
                    "PostalCode": "85281",
                    "StreetNumber": "123",
                    "StreetName": "Main",
                    "StreetSuffix": "St",
                    "BedroomsTotal": 3,
                    "BathroomsTotalInteger": 2,
                    "LivingArea": 1850,
                    "YearBuilt": 1998,
                    "PropertySubType": "Single Family Residence",
                    "ListAgentFullName": "Jane Smith",
                    "ListOfficeName": "ABC Realty",
                }
            ]
        }
        mock_response = httpx.Response(200, json=mock_data)

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            results = await mls_connector.fetch(query_type="expired")
            assert len(results) == 1
            assert results[0]["ListingId"] == "MLS-001"

    def test_transform_maps_fields_correctly(self, mls_connector):
        raw = [{
            "ListingKey": "12345",
            "ListingId": "MLS-001",
            "StandardStatus": "Expired",
            "ListPrice": 425000,
            "OriginalListPrice": 475000,
            "DaysOnMarket": 142,
            "City": "Phoenix",
            "StateOrProvince": "AZ",
            "PostalCode": "85281",
            "StreetNumber": "123",
            "StreetName": "Main",
            "StreetSuffix": "St",
            "BedroomsTotal": 3,
            "BathroomsTotalInteger": 2,
            "LivingArea": 1850,
            "YearBuilt": 1998,
        }]

        transformed = mls_connector.transform(raw)
        assert len(transformed) == 1
        prop = transformed[0]
        assert prop["address"] == "123 Main St"
        assert prop["city"] == "Phoenix"
        assert prop["zip_code"] == "85281"
        assert prop["list_price"] == 425000
        assert prop["mls_number"] == "MLS-001"
        assert prop["mls_status"] == "Expired"
        assert prop["days_on_market"] == 142
        assert prop["data_source"] == "mls_reso"


    @pytest.mark.asyncio
    async def test_handles_rate_limiting(self, mls_connector):
        """Verify the connector respects 429 responses."""
        mls_connector.access_token = "test_token"
        mls_connector._is_authenticated = True

        rate_limit_response = httpx.Response(
            429,
            headers={"Retry-After": "1"},
        )
        success_response = httpx.Response(
            200,
            json={"value": []},
        )

        call_count = 0
        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return rate_limit_response
            return success_response

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, side_effect=mock_get):
            results = await mls_connector._odata_query(filter_str="StandardStatus eq 'Expired'")
            assert call_count == 2  # First call rate-limited, second succeeded
```

### 10.6 End-to-End Pipeline Test

```python
# tests/e2e/test_daily_pipeline.py
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from theleadedge.pipelines.orchestrator import DailyPipelineOrchestrator
from theleadedge.sources import ConnectorRegistry
from theleadedge.scoring.engine import ScoringEngine
from theleadedge.storage.database import Database
from config.settings import Settings

@pytest.fixture
def e2e_settings():
    return Settings(
        app_env="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        feature_mls_api_enabled=False,  # Use CSV import
        feature_email_notifications_enabled=False,
        mls_csv_import_dir="./tests/fixtures/mls_csv",
    )

@pytest_asyncio.fixture
async def e2e_db(e2e_settings):
    db = Database(e2e_settings)
    await db.create_tables()
    yield db
    await db.close()

class TestDailyPipeline:
    """
    End-to-end test: CSV import -> signal detection -> scoring -> briefing.

    Uses fixture CSV files that simulate a real MLS export.
    """

    @pytest.mark.asyncio
    async def test_full_pipeline_from_csv(self, e2e_settings, e2e_db):
        connectors = ConnectorRegistry(e2e_settings)
        scoring = ScoringEngine(e2e_settings.scoring_config_path)

        orchestrator = DailyPipelineOrchestrator(
            settings=e2e_settings,
            db=e2e_db,
            connectors=connectors,
            scoring_engine=scoring,
        )

        # Mock the notification dispatcher to avoid sending real emails
        orchestrator.notifications = MagicMock()
        orchestrator.notifications.send_s_tier_alerts = AsyncMock()
        orchestrator.notifications.send_daily_briefing = AsyncMock()

        # Run the full pipeline
        await orchestrator.run_morning_pipeline()

        # Verify: properties were ingested
        async for session in e2e_db.get_session():
            from theleadedge.storage.database import PropertyTable, LeadTable, SignalTable
            from sqlalchemy import select, func

            prop_count = await session.scalar(select(func.count()).select_from(PropertyTable))
            lead_count = await session.scalar(select(func.count()).select_from(LeadTable))
            signal_count = await session.scalar(select(func.count()).select_from(SignalTable))

            assert prop_count > 0, "No properties were ingested"
            assert lead_count > 0, "No leads were created"
            assert signal_count > 0, "No signals were detected"
```

### 10.7 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests (fast, no I/O)
pytest tests/unit/ -v

# Run with coverage report
pytest tests/ --cov=theleadedge --cov-report=html

# Run specific test class
pytest tests/unit/test_scoring.py::TestScoringEngine -v

# Run in parallel (with pytest-xdist)
pytest tests/ -n auto
```

---

## Appendix A: Application Entrypoint

```python
# theleadedge/main.py
import asyncio
import structlog

from config.settings import Settings
from theleadedge.utils.logging import setup_logging
from theleadedge.storage.database import Database
from theleadedge.sources import ConnectorRegistry
from theleadedge.scoring.engine import ScoringEngine
from theleadedge.pipelines.orchestrator import DailyPipelineOrchestrator

logger = structlog.get_logger()

async def main():
    # 1. Load configuration
    settings = Settings()
    setup_logging(settings)
    logger.info("starting", env=settings.app_env)

    # 2. Initialize database
    db = Database(settings)
    if settings.app_env == "development":
        await db.create_tables()
    logger.info("database_ready", url=settings.database_url.split("@")[-1])

    # 3. Initialize connectors
    connectors = ConnectorRegistry(settings)
    health = await connectors.health_check_all()
    logger.info("connectors_ready", health=health)

    # 4. Initialize scoring engine
    scoring = ScoringEngine(settings.scoring_config_path)
    logger.info("scoring_engine_ready",
                signal_count=len(scoring.signal_configs))

    # 5. Initialize and start pipeline scheduler
    orchestrator = DailyPipelineOrchestrator(
        settings=settings,
        db=db,
        connectors=connectors,
        scoring_engine=scoring,
    )
    orchestrator.start()
    logger.info("scheduler_started")

    # 6. Start dashboard (NiceGUI runs its own event loop)
    if settings.app_env != "testing":
        from nicegui import ui
        # Dashboard UI code would be imported here
        ui.run(
            host=settings.dashboard_host,
            port=settings.dashboard_port,
            title="TheLeadEdge",
            reload=settings.debug,
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Appendix B: Address Normalization Utility

```python
# theleadedge/utils/address.py
import re

# Common abbreviation mappings (USPS standard)
SUFFIX_MAP = {
    "street": "ST", "st": "ST", "str": "ST",
    "avenue": "AVE", "ave": "AVE", "av": "AVE",
    "boulevard": "BLVD", "blvd": "BLVD",
    "drive": "DR", "dr": "DR", "drv": "DR",
    "lane": "LN", "ln": "LN",
    "road": "RD", "rd": "RD",
    "court": "CT", "ct": "CT",
    "circle": "CIR", "cir": "CIR",
    "place": "PL", "pl": "PL",
    "trail": "TRL", "trl": "TRL",
    "way": "WAY",
    "terrace": "TER", "ter": "TER",
    "parkway": "PKWY", "pkwy": "PKWY",
    "highway": "HWY", "hwy": "HWY",
}

DIRECTION_MAP = {
    "north": "N", "south": "S", "east": "E", "west": "W",
    "northeast": "NE", "northwest": "NW",
    "southeast": "SE", "southwest": "SW",
    "n": "N", "s": "S", "e": "E", "w": "W",
    "ne": "NE", "nw": "NW", "se": "SE", "sw": "SW",
}

UNIT_MAP = {
    "apartment": "APT", "apt": "APT",
    "suite": "STE", "ste": "STE",
    "unit": "UNIT", "#": "#",
    "number": "#", "no": "#",
}

def normalize_address(
    address: str,
    city: str = "",
    state: str = "",
    zip_code: str = "",
) -> str:
    """
    Normalize an address to USPS standard format for deduplication.

    Examples:
        "123 North Main Street Apt 4B" -> "123 N MAIN ST APT 4B"
        "456 SW Elm Blvd."            -> "456 SW ELM BLVD"

    The normalized form is used as the deduplication key:
    properties with the same normalized address + zip are considered
    the same property.
    """
    if not address:
        return ""

    # Uppercase and strip punctuation
    addr = address.upper().strip()
    addr = re.sub(r"[.,#]", " ", addr)
    addr = re.sub(r"\s+", " ", addr).strip()

    # Normalize directionals
    words = addr.split()
    normalized_words = []
    for word in words:
        lower = word.lower()
        if lower in DIRECTION_MAP:
            normalized_words.append(DIRECTION_MAP[lower])
        elif lower in SUFFIX_MAP:
            normalized_words.append(SUFFIX_MAP[lower])
        elif lower in UNIT_MAP:
            normalized_words.append(UNIT_MAP[lower])
        else:
            normalized_words.append(word)

    addr = " ".join(normalized_words)

    # Build full normalized address
    parts = [addr]
    if city:
        parts.append(city.upper().strip())
    if state:
        parts.append(state.upper().strip())
    if zip_code:
        parts.append(zip_code.strip()[:5])  # 5-digit ZIP only

    return ", ".join(parts)
```

---

## Appendix C: Quick Reference -- Build Order

This is the recommended order for implementing the system, aligned with the phased roadmap from MASTER_RESEARCH.md:

| Order | Component | Files | Dependencies |
|-------|-----------|-------|-------------|
| 1 | Settings & Logging | `config/settings.py`, `utils/logging.py` | None |
| 2 | Data Models | `models/*.py` | pydantic |
| 3 | Database & Tables | `storage/database.py` | sqlalchemy |
| 4 | Address Normalization | `utils/address.py` | None |
| 5 | CSV Connector | `sources/mls_csv.py` | `sources/base.py` |
| 6 | Signal Detection | `pipelines/detect.py` | models, storage |
| 7 | Decay Functions | `scoring/decay.py` | None |
| 8 | Stacking Rules | `scoring/stacking.py` | None |
| 9 | Scoring Engine | `scoring/engine.py` | decay, stacking, config |
| 10 | Ingestion Pipeline | `pipelines/ingest.py` | connectors, storage |
| 11 | Orchestrator | `pipelines/orchestrator.py` | All above |
| 12 | Email Notifications | `notifications/email.py` | jinja2 |
| 13 | Daily Briefing | `pipelines/briefing.py` | storage, jinja2 |
| 14 | Dashboard (NiceGUI) | `main.py` + UI modules | All above |
| 15 | MLS API Connector | `sources/mls.py` | httpx, tenacity |
| 16 | ATTOM Connector | `sources/attom.py` | httpx |
| 17 | CRM Integration | `integrations/crm.py` | httpx |
| 18 | AI Summaries | `integrations/ai.py` | anthropic |
| 19 | Skip Trace | `sources/skip_trace.py` | httpx |
| 20 | Alembic Migrations | `alembic/` | sqlalchemy |

Start with items 1-13 for a fully functional local system that ingests CSV exports, detects signals, scores leads, and sends a morning briefing email. Items 14-20 add API integrations and the web dashboard incrementally.

---

*This document serves as the technical blueprint for the TheLeadEdge build phase. All code patterns are designed to be copied, adapted, and extended. The architecture prioritizes testability, configurability, and incremental enhancement -- start simple with CSV imports and SQLite, then progressively enable API connectors and advanced features as subscriptions are added.*
