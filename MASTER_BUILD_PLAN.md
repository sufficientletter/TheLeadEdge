# TheLeadEdge: Master Build Plan

> **Project**: Data-driven real estate lead generation system
> **Realtor**: Yani (Ianula Moen), William Raveis Real Estate, Cape Coral FL
> **Market**: Lee + Collier County, SWFLA (52 ZIP codes)
> **MLS**: SWFLA MLS via CoreLogic Matrix (API: CoreLogic Trestle / RESO Web API)
> **Builder**: Developer building automated intelligence tools for licensed Realtors
> **Status**: Phase 1 MVP COMPLETE (64 tests, E2E verified). Phase 2 ACTIVE.
> **Created**: 2026-02-28
> **Updated**: 2026-03-03
> **Compiled from**: 6 planning agents (2026-02-28), updated with findings from 12+ specialist agents (2026-03-03)

---

## Executive Summary

TheLeadEdge is a Python-based intelligence system that mines MLS data, public records, and digital signals to find motivated real estate sellers and buyers before competitors. The Realtor's full MLS access through CoreLogic Matrix is the competitive moat -- no existing tool does deep MLS behavioral analysis combined with free public record data and automated scoring.

**Phase 1 MVP is COMPLETE and proven.** The system ingests MLS CSV exports, detects 12 behavioral signals, applies weighted scoring with temporal decay, and generates daily HTML briefing emails. 36 production modules, 64 unit tests, full end-to-end pipeline verified.

**The revised plan dramatically reduces costs by prioritizing free data sources.** Phase 2 replaces the original $160/month approach (REDX + CRM) with $0/month free county data, FSBO scraping, and market feeds -- deferring paid services until they prove necessary. Once CoreLogic Trestle API credentials arrive, automated MLS ingestion adds ~$42/month (API access through MLS dues).

**7 phases, starting at $0 and scaling to ~$407/month only when ROI justifies it.**

| Phase | Focus | Status | Monthly Cost |
|-------|-------|--------|-------------|
| 0 | Research & Planning + Immediate Value | COMPLETE | $0 |
| 1 | MVP -- CSV import, scoring, daily briefing | COMPLETE | $0 |
| 2 | Free Data Automation -- county PA, public records, market data, FSBO, RESO API | ACTIVE | $0-42/mo |
| 3 | Dashboard -- NiceGUI web interface | PLANNED | $0/mo |
| 4 | Integrations -- CRM, skip tracing, AI summaries, direct mail | PLANNED | ~$157/mo |
| 5 | Intelligence Engine -- ATTOM, predictive modeling, agent analysis | PLANNED | ~$407/mo |
| 6 | Optimization -- A/B testing, ML, calibration | PLANNED | ~$407/mo |

**Estimated 6-month cumulative spend: ~$1,420** (down from ~$2,637 in the original plan -- a 46% reduction).

**Expected 6-month ROI**: $40,000-$80,000 GCI on ~$1,420 total investment (2,800-5,600% return).

---

## Table of Contents

1. [Phase 0: Research & Planning + Immediate Value](#phase-0-research--planning--immediate-value--0--complete)
2. [Phase 1: MVP -- CSV Import, Scoring, Daily Briefing](#phase-1-mvp--csv-import-scoring-daily-briefing--0month--complete)
3. [Phase 2: Free Data Automation](#phase-2-free-data-automation--0-42month--active)
4. [Phase 3: Dashboard -- NiceGUI Web Interface](#phase-3-dashboard--nicegui-web-interface--0month)
5. [Phase 4: Integrations -- CRM, Skip Tracing, AI, Direct Mail](#phase-4-integrations--crm-skip-tracing-ai-direct-mail--157month)
6. [Phase 5: Intelligence Engine -- ATTOM, Predictive Modeling](#phase-5-intelligence-engine--attom-predictive-modeling--407month)
7. [Phase 6: Optimization -- A/B Testing, ML, Calibration](#phase-6-optimization--ab-testing-ml-calibration--407month)
8. [Technical Architecture](#technical-architecture)
9. [Cost Projection](#cost-projection)
10. [Kill Criteria](#kill-criteria)
11. [Decision Points](#decision-points)
12. [Research Reference Index](#research-reference-index)

---

## Phase 0: Research & Planning + Immediate Value -- $0 -- COMPLETE

**Goal**: Build the research foundation and give the Realtor immediate prospecting improvements using research insights + MLS access + free tools. Zero code.

**Status**: COMPLETE. 21 research files totaling 19,800+ lines. All planning, market analysis, compliance review, and scoring algorithm design finished.

### What Was Accomplished

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | 21 research files covering MLS data mining, public records, lead scoring, legal compliance, outreach strategy, automation architecture, dashboard UX, and more | DONE |
| 2 | SWFLA market analysis -- 52 ZIP codes across Lee + Collier County identified and configured | DONE |
| 3 | MLS platform confirmed: CoreLogic Matrix, API via CoreLogic Trestle (RESO Web API) | DONE |
| 4 | Scoring algorithm designed: 20 signal types, 4 decay functions, 6 stacking rules, 5 tiers | DONE |
| 5 | MLS field mapping: 46 fields with Name + Label dual-header support for CoreLogic Matrix exports | DONE |
| 6 | Legal compliance framework: MLS ToS, DNC, CAN-SPAM, TCPA, CCPA, Fair Housing reviewed for FL | DONE |
| 7 | Outreach templates customized for 12 lead types with drip sequences | DONE |
| 8 | Free data source inventory: Lee County Property Appraiser, Clerk of Court, FL lis pendens, Zillow FSBO, Redfin market data | DONE |
| 9 | 10 MLS saved searches configured (expireds, price reductions, high DOM, withdrawn, FSBO, back-on-market) | DONE |
| 10 | Cost-optimized build plan: free sources first, paid services deferred until ROI proven | DONE |

### Research Corpus (21 files)

| File | Focus |
|------|-------|
| `MASTER_RESEARCH.md` | Overview, top 10 strategies, signal stacking |
| `mls_data_analysis.md` | MLS saved searches, daily workflow, field analysis |
| `public_records_strategies.md` | 12 public record sources, cross-referencing |
| `lead_scoring_models.md` | Signal weights, decay, tiers, scoring math |
| `creative_strategies.md` | 22 innovative strategies, lifecycle prediction |
| `competitive_analysis.md` | 14 platforms, 5 gaps we exploit |
| `reso_api_integration.md` | RESO Web API, OAuth, OData, CoreLogic Trestle |
| `legal_compliance_framework.md` | DNC/TCPA/CAN-SPAM, FL state rules |
| `outreach_templates.md` | Scripts for 12 lead types, drip sequences |
| `python_implementation.md` | Primary build blueprint: models, connectors, engine |
| `local_data_sources.md` | County portals, FOIA templates |
| `roi_metrics_framework.md` | KPIs, funnels, A/B testing, income projections |
| `dashboard_frameworks.md` | Framework comparison (NiceGUI selected) |
| `dashboard_ux_design.md` | UX patterns, mobile, accessibility |
| `dashboard_examples.md` | Real-world dashboard inspiration |
| `automation_integrations.md` | CRM, email, workflow automation |
| `data_pipeline_architecture.md` | ETL patterns, DB design, sync strategies |
| `Free_Data_Automation_Plan.md` | Zero-cost data source strategy for Phase 2 |
| `Interim_Data_Playbook.md` | Manual + automated hybrid workflows |
| `NABOR_API_Access_Guide.md` | CoreLogic Trestle API access procedures |
| `clerk_of_court_automation_research.md` | Lee County Clerk automation for lis pendens, probate |

### Value Delivered
Transformed the Realtor from zero systematic prospecting to a structured daily pipeline backed by 19,800+ lines of validated research. Ahead of 80% of agents operating on random referrals.

---

## Phase 1: MVP (Weeks 1-2) — $0/month — COMPLETE

**Goal**: Automate the most painful manual step. CSV import → signal detection → scoring → daily briefing email.

**Status**: COMPLETE (2026-03-03). All objectives met. Full E2E verified.

### What Was Built

```
Realtor exports CSV from MLS portal (5 min)
    → drops in Data/ folder
        → TheLeadEdge ingests, deduplicates, detects signals
            → scores and tiers all leads
                → sends daily briefing email at 6:30 AM
```

### Results

| Metric | Target | Actual |
|--------|--------|--------|
| Unit tests | ~45 | 64 (1.09s) |
| Lint | ruff clean | ruff clean |
| E2E pipeline | CSV → email | 10 records → 11 signals → 2 S, 1 A, 2 C, 5 D → briefing HTML (7,551 bytes) |
| Signal types active | 12 | 12 (of 20 defined) |
| Stacking rules firing | 2+ | 2 (of 6 defined) |
| CLI commands | 1 | 4 (`import`, `score`, `briefing`, `run`) |

### Build History (7 Batches)

| Batch | What | Key Files |
|-------|------|-----------|
| 1 | Scaffolding | pyproject.toml, .gitignore, .env.example, __init__.py files |
| 2 | Enums, Settings, Utilities | enums.py, config/__init__.py, logging.py, address.py, phone.py, retry.py, rate_limit.py |
| 3 | Data Models + Config | property.py, signal.py, score.py, lead.py, outreach.py, scoring_weights.yaml, mls_fields.yaml, market.yaml |
| 4 | Database Layer | database.py (7 tables), repositories.py (7 repos), queries.py, alembic setup |
| 5 | Test Infrastructure | conftest.py, factories.py, .pre-commit-config.yaml |
| 6 | Scoring + CSV + Pipelines | decay.py, stacking.py, engine.py, base.py, mls_csv.py, detect.py (12 rules), score.py, ingest.py |
| 7 | Email, Briefing, CLI, Tests | email.py, daily_briefing.html, briefing.py, main.py, 5 test files |

### 12 Active Signal Detection Rules

| Signal | Category | Points | Decay |
|--------|----------|--------|-------|
| expired_listing | mls | 15 | exponential (21d) |
| expired_listing_stale | mls | 10 | exponential (45d) |
| price_reduction | mls | 8 | exponential (14d) |
| price_reduction_multiple | mls | 14 | exponential (21d) |
| price_reduction_severe | mls | 16 | step (30d) |
| high_dom | mls | 11 | step (60d) |
| withdrawn_relisted | mls | 12 | exponential (30d) |
| back_on_market | mls | 13 | exponential (14d) |
| listing_price_low_set | mls | 6 | linear (30d) |
| foreclosure_flag | mls | 18 | linear (90d) |
| short_sale_flag | mls | 16 | linear (90d) |
| absentee_owner | mls | 8 | linear (180d) |

### CLI Commands

```bash
python -m theleadedge import      # Import CSV from Data/ folder
python -m theleadedge score       # Score all leads (detect signals + calculate)
python -m theleadedge briefing    # Generate and send daily briefing email
python -m theleadedge run         # Full pipeline: import → score → briefing
```

### Phase 1 File Inventory

```
src/theleadedge/
├── __init__.py, __main__.py
├── main.py                        # CLI entrypoint
├── config/__init__.py             # Pydantic Settings
├── models/                        # 6 Pydantic model files
│   ├── enums.py, property.py, signal.py, score.py, lead.py, outreach.py
├── sources/
│   ├── base.py                    # DataSourceConnector ABC + SyncResult
│   └── mls_csv.py                 # MLS CSV import connector
├── scoring/
│   ├── decay.py                   # 4 decay functions
│   ├── stacking.py                # 6 stacking rules
│   ├── engine.py                  # ScoringEngine.calculate()
│   └── config_loader.py           # YAML → config objects
├── pipelines/
│   ├── ingest.py, detect.py, score.py, briefing.py
├── storage/
│   ├── database.py                # 7 ORM tables + async engine
│   ├── repositories.py            # 7 repo classes
│   └── queries.py                 # Named queries
├── notifications/
│   ├── email.py                   # SMTP sender
│   └── templates/daily_briefing.html
└── utils/
    ├── logging.py, address.py, phone.py, retry.py, rate_limit.py
config/
├── scoring_weights.yaml           # 20 signals, 6 stacking rules, 5 tiers
├── mls_fields.yaml                # 46 MLS fields, Name+Label dual headers
└── market.yaml                    # 52 SWFLA ZIP codes
tests/
├── conftest.py, factories.py
└── unit/ (5 test files, 64 tests)
```

### Value Delivered

Eliminates 20-30 min/day of manual spreadsheet work. Signal stacking catches combinations manual review would miss. Realtor exports CSV, runs one command, gets a scored briefing email with exactly who to call first.

---

## Phase 2: Free Data Automation + Pipeline Scheduling (Weeks 3-6) — $0/month — ACTIVE

**Goal**: Activate all 20 signal types and all 6 stacking rules using free public data sources. Automate the full pipeline on a schedule. Defer paid services until lead volume justifies the cost.

**Key Decision**: Prioritize free data sources ($0/month) before paid services. County PA data, Sunshine Law records, Redfin market feeds, and FSBO scraping are all available right now. The RESO API requires credential approval (1-3 week wait) and costs ~$42/month — build it last.

**Blueprint**: Full implementation spec in `Research/Free_Data_Automation_Plan.md`.

### What Changed from Original Phase 2

| Aspect | Original Plan | Revised Plan |
|--------|--------------|--------------|
| REDX expired/FSBO feed | $100/mo | REMOVED — free sources provide more signals |
| Follow Up Boss CRM | $58/mo | MOVED to Phase 4 |
| Public records | Manual, Phase 4 | FREE via Sunshine Law, now Phase 2.3 |
| Property appraiser data | Not planned | ADDED — free bulk downloads, highest priority |
| Address matching system | Not planned | ADDED — bridges MLS to public records |
| Redfin market data | Not planned | ADDED — free S3 download |
| Sunbiz LLC records | Not planned | ADDED — free SFTP |
| Monthly cost | $160/mo | $0/mo ($42/mo once RESO API arrives) |
| New signals activated | 0 | 8 (from 12 → 20) |
| Stacking rules firing | 2 | 6 (all active) |

### Sub-Phases

#### Phase 2.1: Foundation — Address Matching + DB Schema + Scheduler

**New PropertyRow columns**: parcel_id, owner_name_raw, mailing_address, homestead_exempt, assessed_value, last_sale_date, last_sale_price, year_built_pa, total_area_pa

**New tables**: source_records, match_queue, market_snapshots, fsbo_listings

**Address Matcher** — 4-strategy cascade:

| Strategy | Method | Confidence |
|----------|--------|------------|
| 1. Parcel ID | Exact match | 1.00 |
| 2. Normalized address | Standardized comparison | 0.95 |
| 3. Address key | Street number + name only | 0.85 |
| 4. Fuzzy match | rapidfuzz Levenshtein | 0.70+ |

**New dependencies**: rapidfuzz, feedparser, apscheduler

**Files**: `matching/address_matcher.py`, `matching/normalizer.py`, `pipelines/orchestrator.py`, `pipelines/match.py`

#### Phase 2.2: Property Appraiser Connectors (HIGHEST PRIORITY)

Why first: populates `parcel_id` which becomes the reliable bridge for all other sources.

| County | URL | Format |
|--------|-----|--------|
| Collier | collierappraiser.com/Main_Data/DataDownloads.html | CSV |
| Lee (LEEPA) | leepa.org/Roll/TaxRoll.aspx | NAL/ZIP |

**Enables**: absentee_owner enrichment, vacant_property detection, investor identification, high-equity leads

**Files**: `sources/property_appraiser.py`, `sources/collier_pa.py`, `sources/lee_pa.py`, `config/county_pa.yaml`

#### Phase 2.3: Public Records (Sunshine Law Responses)

Process CSV/Excel files from Florida Sunshine Law requests (F.S. 119.07). Templates in `Research/clerk_of_court_automation_research.md`.

| Record Type | Signal | Points | Stacking Rule Unlocked |
|-------------|--------|--------|----------------------|
| Lis Pendens | pre_foreclosure | 20 | financial_distress (2.0x) |
| Probate | probate | 18 | life_event_vacant (2.5x) |
| Divorce | divorce | 16 | divorce_property (1.6x) |
| Code violations | code_violation | 12 | tired_landlord (1.8x) |
| Tax delinquency | tax_delinquent | 13 | financial_distress (2.0x) |

**Files**: `sources/clerk_of_court.py`, `sources/code_violations.py`, `sources/tax_collector.py`

#### Phase 2.4: Market Data + FSBO Monitoring

| Source | URL | Format | Signal |
|--------|-----|--------|--------|
| Redfin Data Center | S3 bucket (gzipped TSV) | TSV | neighborhood_hot (5 pts) |
| Craigslist FSBO | fortmyers.craigslist.org RSS | RSS/XML | FSBO lead source |
| Google Alerts | RSS feeds for keywords | RSS | Digital signals |

**Files**: `sources/redfin_market.py`, `sources/fsbo_feed.py`, `sources/google_alerts.py`

#### Phase 2.5: Sunbiz LLC Records

SFTP from sftp.floridados.gov (public credentials). Cross-reference LLC names with PA owner data to identify investor-owned properties. Quarterly download.

**Files**: `sources/sunbiz.py`

#### Phase 2.6: RESO API Connector (When Credentials Arrive)

| Attribute | Value |
|-----------|-------|
| Provider | CoreLogic Trestle |
| Auth | OAuth2 Client Credentials |
| Rate limits | 7,200/hr, 180/min, 200/page |
| Cost | ~$42/month ($500/year) |
| Sync | Incremental via ModificationTimestamp, full weekly |

Replaces daily CSV exports with automated 30-minute polling. Blocked on Yani calling NABOR for credential approval.

**Files**: `sources/reso_api.py`, `sources/reso_transform.py`, `config/reso_api.yaml`

### Phase 2 CLI Commands

```bash
python -m theleadedge download-pa            # Download county PA bulk files
python -m theleadedge download-redfin        # Download Redfin market data
python -m theleadedge import-public-records  # Import Sunshine Law response files
python -m theleadedge match-records          # Run address matching
python -m theleadedge scheduler start        # Start APScheduler daemon
python -m theleadedge health                 # Check data source connectivity
```

### Phase 2 Schedule

| Job | Time | Description |
|-----|------|-------------|
| mls_file_watch | Daily 5:00 AM | Watch for new CSV (or API poll if RESO active) |
| morning_pipeline | Daily 6:00 AM | Full: ingest → detect → score |
| daily_briefing | Daily 6:30 AM | Generate + send HTML briefing |
| s_tier_alert | On detection | Instant email for new S-tier leads |
| redfin_market | Weekly Mon 6:00 AM | Download Redfin market data |
| fsbo_scan | Weekly Mon 6:30 AM | Craigslist FSBO RSS scan |
| county_pa_download | Monthly 1st 5:00 AM | Lee + Collier PA bulk files |
| public_records_import | Monthly 1st 5:30 AM | Process Sunshine Law responses |
| sunbiz_download | Quarterly | Sunbiz LLC SFTP download |
| reso_incremental | Every 30 min (when active) | RESO API incremental sync |

### Phase 2 Success Criteria

| Metric | Target |
|--------|--------|
| Signal types active | 20/20 |
| Stacking rules firing | 6/6 |
| Unattended operation | Fully scheduled, no manual intervention |
| Address match rate | 85%+ public records → properties |
| S-tier alerts | Within 5 minutes of detection |
| Monthly cost | $0 ($42/mo with RESO API) |
| New unit tests | ~84 (total ~148) |

### Phase 2 Build Order

| Order | Sub-phase | Depends On | Effort |
|-------|-----------|------------|--------|
| 1 | 2.1 Foundation | Phase 1 | 3-4 days |
| 2 | 2.2 Property Appraiser | 2.1 | 3-4 days |
| 3 | 2.3 Public Records | 2.1 | 3-4 days |
| 4 | 2.4 Market + FSBO | 2.1 | 2-3 days |
| 5 | 2.5 Sunbiz | 2.2 | 1-2 days |
| 6 | 2.6 RESO API | 2.1; blocked on credentials | 3-4 days |

Phases 2.2 and 2.3 can run in parallel after 2.1 completes.

### Value to Realtor

The system becomes a fully automated intelligence engine at $0/month. Instead of manually exporting CSVs, the Realtor wakes up to a scored briefing that incorporates MLS signals, property ownership patterns, financial distress indicators, life events, and neighborhood momentum. S-tier leads with multiple converging signals trigger instant alerts. The Realtor's only job is to make the calls.

---

## Phase 3: Dashboard (Month 2) -- $0/month

**Goal**: Web UI so the operator can see leads visually, not just via email. By Phase 3, the pipeline has MLS signals (Phase 1) plus public records signals (Phase 2) -- the dashboard surfaces that full picture.

### Framework: NiceGUI 2.x

Chosen over Streamlit (no WebSocket push), Dash (callback hell), and React (overkill). NiceGUI gives: pure Python, Quasar Material Design, native Leaflet maps, AG Grid tables, ECharts, PWA support for mobile, and FastAPI backend.

### Pages (build order = maximum value delivery)

| Phase | Days | Page | Key Components |
|-------|------|------|----------------|
| 1 | 1-2 | App Shell | Nav, auth, dark mode, theme |
| 2 | 3-5 | **Lead Pipeline** `/leads` | AG Grid table, tier/signal badges, filter bar, action buttons |
| 3 | 6-8 | **Lead Detail** `/leads/{id}` | Score gauge, signal stack, owner info, public records panel, activity timeline, outreach log |
| 4 | 9-11 | **Morning Briefing** `/` | 4 KPI cards, priority actions, new leads, score changes, market pulse |
| 5 | 12-15 | **Map View** `/map` | Leaflet map, tier-colored pins, heat map, marker clustering, sidebar |
| 6 | 16-18 | **Public Records** `/records` | Lis pendens, probate, code violations, tax delinquency -- cross-referenced with MLS leads |
| 7 | 19-22 | **Analytics** `/analytics` | Conversion funnel, ROI by source, score distribution, signal performance |
| 8 | 23-26 | **Settings** `/settings` | Scoring weight editor, data source toggles, notification prefs, CSV import |
| 9 | 27-30 | Mobile Polish | Responsive layouts, PWA manifest, bottom tab bar, real-time push |

### File Structure (30 new files)

```
src/theleadedge/dashboard/
├── app.py                    # NiceGUI setup, routing, auth
├── theme.py                  # Colors, tier/signal palette, Tailwind
├── components/               # 12 reusable components
│   ├── kpi_card.py          # Value + delta + sparkline
│   ├── lead_card.py         # Compact lead summary
│   ├── tier_badge.py        # S/A/B/C/D colored badge
│   ├── signal_badge.py      # Signal type indicator
│   ├── score_gauge.py       # EChart radial gauge
│   ├── score_bar.py         # Linear progress bar
│   ├── action_buttons.py    # Call/CMA/Email group
│   ├── activity_timeline.py # Quasar timeline
│   ├── notification_bell.py # Header bell + badge
│   ├── public_records_panel.py  # Lis pendens, probate, code violations summary
│   ├── market_pulse_table.py
│   └── filter_bar.py
├── pages/                    # 7 page views
│   ├── briefing.py          # Morning briefing home page
│   ├── leads.py             # Lead pipeline table
│   ├── lead_detail.py       # Individual lead deep-dive
│   ├── records.py           # Public records browser
│   ├── map_view.py          # Geographic lead map
│   ├── analytics.py         # Performance analytics
│   └── settings.py          # Configuration UI
├── dialogs/                  # 5 modal dialogs
│   ├── outreach_form.py, note_dialog.py, snooze_dialog.py
│   ├── confirm_dialog.py, csv_import_dialog.py
└── static/                   # PWA + Leaflet plugins
    ├── manifest.json, icons, leaflet-plugins.js
```

### Outreach Integration

| Action | Trigger | What Happens |
|--------|---------|-------------|
| Click-to-Call | "Call" button | `tel:` link on mobile, logs outreach event |
| One-click CMA | "CMA" button | Generates PDF via WeasyPrint, optionally emails |
| Send Email | "Email" button | Pre-drafted from templates, editable before send |
| Mark Contacted | Status update | Updates lead status, asks for outcome |
| Push to CRM | "Add to CRM" | Creates Follow Up Boss contact with full context (Phase 4) |

### Public Records View

The `/records` page is new compared to the original plan. With Phase 2 bringing in lis pendens, probate filings, code violations, and property appraiser data, the dashboard needs a dedicated view.

| Section | Data Source | What It Shows |
|---------|-----------|--------------|
| Pre-Foreclosure | Clerk of Court lis pendens | New filings, cross-referenced with MLS leads, days since filing |
| Probate | Clerk of Court probate index | Decedent name, personal rep, property match, filing date |
| Code Violations | County code enforcement | Active violations, repeat offenders, lien amounts |
| Tax Delinquency | Tax collector lists | Delinquent parcels, years delinquent, amount owed |
| Absentee Owners | Property appraiser bulk data | Mailing vs. site address mismatch, ownership duration, equity estimate |

### Success Criteria
- Dashboard loads in <2 seconds, works on mobile
- Operator can manage leads without touching a spreadsheet
- Map view helps plan driving routes
- Public records view surfaces cross-referenced leads that email briefing cannot

---

## Phase 4: Integrations (Month 2-3) -- $157/month

**Goal**: CRM integration, skip tracing for contact info, AI-generated lead summaries, and direct mail automation. This phase transforms scored leads into actionable outreach.

**Context**: RESO API and public records automation moved to Phase 2 (free data sources). This phase focuses on paid services that amplify the intelligence layer.

### New Components

| # | Component | File | Cost |
|---|-----------|------|------|
| 1 | **Follow Up Boss CRM** integration | `integrations/crm.py` | $58/mo |
| 2 | **BatchLeads skip trace** (auto for S/A tier) | `sources/skip_trace.py` | $99/mo |
| 3 | **Claude AI lead summaries** | `integrations/ai.py` | $5-20/mo |
| 4 | **Direct mail automation** (Click2Mail/Handwrytten) | `integrations/mail.py` | $50-150/mo |
| 5 | **CMA PDF generation** (WeasyPrint) | `reports/cma.py` | $0 |
| 6 | **DNC + compliance pipeline** | `pipelines/compliance.py` | $0 |
| 7 | **S-tier instant alerts** | `notifications/templates/s_tier_alert.html` | $0 |
| 8 | **Notification dispatcher** (route by tier) | `notifications/dispatcher.py` | $0 |

### Follow Up Boss Integration Detail

| Feature | Direction | Trigger | What Happens |
|---------|-----------|---------|-------------|
| Lead push | System -> CRM | S/A-tier score event | Create or update contact, apply action plan, add notes with signal summary |
| Lead pull | CRM -> System | Hourly sync | Pull disposition, stage changes, notes for outcome tracking |
| Tag sync | Bidirectional | On score/tier change | Apply tier tags (S-Tier Lead, etc.), signal tags (Pre-Foreclosure, Probate) |
| Activity log | System -> CRM | On outreach event | Log calls, emails, mail pieces as CRM activities |

**Decision gate**: Confirm with the Realtor (Yani) that Follow Up Boss is the preferred CRM before subscribing. William Raveis may provide a brokerage CRM that overlaps.

### Compliance Requirements (Critical -- Florida-Specific)

- DNC scrubbing mandatory before phone numbers reach the operator (federal + Florida state lists)
- Pre-foreclosure: Florida is a judicial foreclosure state -- no specific waiting period statute, but ethical practice requires sensitivity. Allow minimum 30 days after lis pendens filing before outreach.
- Probate: 30-day minimum wait after filing before outreach
- TCPA: system MUST NOT send automated texts without documented prior express written consent
- Fair Housing: all mail templates reviewed for discriminatory language or targeting
- Contact frequency limits enforced (max 3 calls/week per lead)
- Florida is a two-party consent state for call recording -- always disclose

### Value to Realtor
Complete actionable intelligence: phone numbers via skip trace, email addresses, AI-generated lead summaries explaining why this lead is hot, CMA ready to send, and a suggested script matched to lead type. For distress leads, sensitive letters sent automatically with waiting periods enforced. S-tier leads appear in CRM with action plans within minutes.

---

## Phase 5: Intelligence Engine (Month 3-4) -- $407/month

**Goal**: Build what no competitor has. This is the competitive moat.

**Context**: Phase 2 already brings in Redfin market data for neighborhood baselines and property appraiser data for equity analysis. Phase 5 layers on ATTOM for nationwide enrichment and builds the predictive models that no existing tool offers.

### New Components

| # | Component | What | Cost |
|---|-----------|------|------|
| 1 | **ATTOM API** | Property enrichment: equity estimates, AVM, owner demographics, foreclosure status, deed history | $250/mo |
| 2 | **MLS behavioral analysis** | Price velocity, DOM deviation, listing lifecycle patterns, relisting frequency | $0 |
| 3 | **Agent performance database** | Sell-through rate, average DOM, failure rate for top 50 listing agents in SWFLA | $0 |
| 4 | **Predictive listing failure** | Logistic regression: which active listings will expire? Features: agent history, price-to-comp ratio, DOM trajectory, season | $0 |
| 5 | **Neighborhood heat mapping** | Absorption rate, momentum, price trends by micro-area (enhanced from Phase 2 Redfin baselines) | $0 |
| 6 | **Enhanced signal stacking** | MLS + public records + ATTOM cross-correlation, new stacking combos | $0 |

### New Files

```
src/theleadedge/
├── sources/
│   └── attom.py                     # ATTOM Property API connector
├── intelligence/
│   ├── __init__.py
│   ├── behavioral.py                # MLS listing behavior analysis
│   ├── agent_tracker.py             # Agent performance tracking + scoring
│   ├── predictor.py                 # Pre-expiration prediction model
│   └── heat_map.py                  # Neighborhood momentum calculator
```

### The Killer Feature: Pre-Expiration Leads

Contact likely-to-fail listings BEFORE they expire -- weeks ahead of every competitor. No existing tool does this.

**How it works**:
1. Train a logistic regression model on historical expired/sold outcomes
2. Features: listing agent sell-through rate, price-to-comp ratio, DOM trajectory, seasonal factors, price reduction count, days until expiration
3. Score active listings daily for expiration probability
4. Surface listings with >60% predicted failure probability as "Pre-Expiration" leads
5. Requires ~6 months of MLS history data for initial training (available from Trestle HistoryTransactional resource)

### ATTOM API Integration

| Endpoint | Use | Trigger |
|----------|-----|---------|
| Property Detail | Bedrooms, bathrooms, sqft, lot size, year built | On new lead creation |
| AVM (Automated Valuation) | Estimated value, equity calculation | On new lead + monthly refresh |
| Owner | Owner name, mailing address, length of ownership | On new lead creation |
| Sale History | Purchase price, date, deed type | On new lead creation |
| Pre-Foreclosure | NOD/lis pendens, auction date, default amount | Weekly scan of target ZIPs |
| Assessment | Tax assessed value, tax amount, exemptions | On new lead creation |

### Value to Realtor
Unfair advantage. The operator contacts failing listings before expiration, knows which agents underperform (and can pitch those agents' frustrated sellers), and surfaces multi-signal convergence leads (15-25% conversion probability) that no single tool catches. ATTOM enrichment fills gaps that county public records miss.

---

## Phase 6: Optimization (Month 4+) -- $407/month

**Goal**: Close the feedback loop. Make the system smarter over time.

### Components

| # | Component | File | Trigger |
|---|-----------|------|---------|
| 1 | **Score calibration** | `scoring/calibration.py` | Every 90 days |
| 2 | **Signal effectiveness analysis** | `scoring/feedback.py` | Every 100 outcomes |
| 3 | **A/B testing framework** (Bayesian) | `testing/ab.py` | Continuous |
| 4 | **Monthly reporting** | `reports/monthly.py` | 1st of month |
| 5 | **ML model training** (when 200+ outcomes) | `scoring/ml_model.py` | Quarterly |
| 6 | **Past client lifecycle prediction** | `pipelines/lifecycle.py` | Monthly |

### Feedback Loop
```
Lead -> Score -> Outreach -> Outcome recorded in CRM
                                    |
                    Signal effectiveness analysis
                                    |
                    Weight adjustment suggestions
                                    |
                    Human review -> YAML update -> Re-score all
```

The system NEVER auto-adjusts weights. It suggests changes; the human approves.

### What "Calibration" Means in Practice

After 90 days of operation with outcome tracking:

1. **Signal ROI analysis**: Which signals actually led to listings/closings? Which are noise?
2. **Decay rate tuning**: Are leads going stale faster or slower than the model assumes?
3. **Tier threshold adjustment**: Are S-tier leads actually converting at a higher rate than A-tier? If not, adjust thresholds.
4. **Stacking rule validation**: Do the multiplier combos hold up? Financial distress (2.0x) -- does it actually convert 2x better?
5. **Source quality comparison**: MLS signals vs. public records vs. ATTOM -- which source contributes the most predictive signals?

All calibration output goes into a human-readable report. The operator reviews and approves changes to `config/scoring_weights.yaml`. No black-box auto-tuning.

---

## Technical Architecture

### Tech Stack

| Layer | Tool | Cost |
|-------|------|------|
| Language | Python 3.11+ | Free |
| Models | Pydantic v2 | Free |
| Database | SQLite (MVP) -> PostgreSQL (scale) | Free |
| ORM | SQLAlchemy 2.0 (async) + aiosqlite | Free |
| HTTP | httpx (async) | Free |
| Scheduling | APScheduler | Free |
| Dashboard | NiceGUI 2.x | Free |
| Email | SMTP via aiosmtplib (Gmail) | Free |
| Templating | Jinja2 (briefing emails) | Free |
| Config | PyYAML (scoring, fields, market) | Free |
| Logging | structlog (JSON prod, colored dev) | Free |
| Testing | pytest + hypothesis + Factory Boy | Free |
| Linting | ruff | Free |

### Project Structure (Actual -- as built in Phase 1)

```
TheLeadEdge/
├── CLAUDE.md                            # Project constitution
├── MASTER_BUILD_PLAN.md                 # This file
├── pyproject.toml                       # Dependencies, build config
├── .env.example                         # Config template (secrets)
├── .gitignore                           # Excludes data/, .env, *.db
├── .pre-commit-config.yaml              # ruff hooks
├── alembic.ini                          # Migration config
├── alembic/                             # Migration scripts
│   └── env.py
├── config/                              # YAML configuration (project root)
│   ├── scoring_weights.yaml             # 20 signals, 6 stacking rules, 5 tiers
│   ├── mls_fields.yaml                  # 46 fields, Name+Label dual headers
│   └── market.yaml                      # 52 SWFLA ZIP codes, MLS/CRM config
├── Research/                            # Research corpus (21 files, 25,000+ lines)
│   ├── MASTER_RESEARCH.md
│   ├── NABOR_API_Access_Guide.md        # CoreLogic Trestle API access steps
│   ├── Interim_Data_Playbook.md         # Pre-API data strategy
│   ├── Free_Data_Automation_Plan.md     # Phase 2 blueprint (8 free sources)
│   ├── clerk_of_court_automation_research.md  # Clerk records automation feasibility
│   └── (17 original research files)
├── Docs/
│   └── MLS_API_Pitch_Yani.html          # API pitch document for Realtor
├── TeamLeadJournal/                     # Session journals
├── logs/                                # Agent action logs
├── Strategies/                          # Lead-finding strategies
├── src/theleadedge/                     # Source code (src layout)
│   ├── __init__.py
│   ├── __main__.py                      # python -m theleadedge
│   ├── main.py                          # CLI: import, score, briefing, run
│   ├── config/
│   │   └── __init__.py                  # Settings loader (Pydantic Settings)
│   ├── models/                          # Pydantic v2 data models
│   │   ├── __init__.py
│   │   ├── enums.py                     # Tier, LeadStatus, SignalCategory, DecayType, etc.
│   │   ├── property.py                  # PropertyBase/Valuation/MLS/Owner
│   │   ├── signal.py                    # Signal, SignalCreate, SignalConfig
│   │   ├── score.py                     # ScoreResult, ScoreHistory
│   │   ├── lead.py                      # Lead with computed fields
│   │   └── outreach.py                  # OutreachEvent
│   ├── sources/                         # Data source connectors
│   │   ├── __init__.py
│   │   ├── base.py                      # DataSourceConnector ABC + SyncResult
│   │   ├── mls_csv.py                   # MLS CSV import (Phase 1) -- BUILT
│   │   ├── property_appraiser.py        # County PA HTTP downloads (Phase 2.2)
│   │   ├── clerk_of_court.py            # Sunshine Law CSV parsing (Phase 2.3)
│   │   ├── code_violation.py            # Code enforcement data (Phase 2.3)
│   │   ├── market_data.py              # Redfin S3 + Google Alerts (Phase 2.4)
│   │   ├── fsbo.py                      # Craigslist RSS + FSBO sites (Phase 2.4)
│   │   ├── sunbiz.py                    # FL LLC records SFTP (Phase 2.5)
│   │   ├── mls_api.py                   # RESO Web API via Trestle (Phase 2.6)
│   │   ├── skip_trace.py               # BatchLeads (Phase 4)
│   │   └── attom.py                     # ATTOM enrichment (Phase 5)
│   ├── scoring/                         # Scoring engine
│   │   ├── __init__.py
│   │   ├── decay.py                     # 4 decay functions -- BUILT
│   │   ├── stacking.py                  # 6 stacking rules -- BUILT
│   │   ├── engine.py                    # ScoringEngine.calculate() -- BUILT
│   │   ├── config_loader.py             # YAML -> config objects -- BUILT
│   │   ├── feedback.py                  # Calibration + effectiveness (Phase 6)
│   │   └── ml_model.py                  # ML training (Phase 6)
│   ├── pipelines/                       # Processing pipelines
│   │   ├── __init__.py
│   │   ├── ingest.py                    # CSV import pipeline -- BUILT
│   │   ├── detect.py                    # SignalDetector (12 rules) -- BUILT
│   │   ├── score.py                     # ScorePipeline -- BUILT
│   │   ├── briefing.py                  # BriefingGenerator -- BUILT
│   │   ├── orchestrator.py              # APScheduler job manager (Phase 2.1)
│   │   ├── match.py                     # Address matching pipeline (Phase 2.2)
│   │   └── compliance.py               # DNC scrub + suppression (Phase 4)
│   ├── matching/                        # Record matching (Phase 2.2)
│   │   ├── address_matcher.py           # 4-strategy address matching
│   │   └── record_mapper.py             # SourceRecord -> PropertyRow resolver
│   ├── storage/                         # Database layer
│   │   ├── __init__.py
│   │   ├── database.py                  # 7 ORM tables + async engine -- BUILT
│   │   ├── repositories.py              # 7 repo classes -- BUILT
│   │   └── queries.py                   # Named queries for briefing -- BUILT
│   ├── notifications/                   # Email + alerts
│   │   ├── __init__.py
│   │   ├── email.py                     # SMTP sender -- BUILT
│   │   ├── dispatcher.py               # Route by tier urgency (Phase 4)
│   │   └── templates/
│   │       ├── daily_briefing.html      # Jinja2 briefing template -- BUILT
│   │       └── s_tier_alert.html        # Instant S-tier alert (Phase 4)
│   ├── integrations/                    # External service integrations
│   │   ├── __init__.py
│   │   ├── crm.py                       # Follow Up Boss client (Phase 4)
│   │   ├── ai.py                        # Claude API summaries (Phase 4)
│   │   └── mail.py                      # Direct mail API (Phase 4)
│   ├── intelligence/                    # Predictive models (Phase 5)
│   │   ├── __init__.py
│   │   ├── behavioral.py               # MLS listing behavior analysis
│   │   ├── agent_tracker.py             # Agent performance tracking
│   │   ├── predictor.py                 # Pre-expiration prediction model
│   │   └── heat_map.py                  # Neighborhood momentum calculator
│   ├── reports/                         # Generated reports (Phase 4+)
│   │   ├── cma.py                       # CMA PDF generation (WeasyPrint)
│   │   └── monthly.py                   # Monthly performance report (Phase 6)
│   ├── dashboard/                       # NiceGUI web UI (Phase 3)
│   │   ├── app.py, theme.py
│   │   ├── components/                  # 12 reusable widgets
│   │   ├── pages/                       # 7 page views
│   │   ├── dialogs/                     # 5 modal dialogs
│   │   └── static/                      # PWA manifest + icons
│   └── utils/                           # Shared utilities
│       ├── __init__.py
│       ├── logging.py                   # structlog setup -- BUILT
│       ├── address.py                   # USPS address normalization -- BUILT
│       ├── phone.py                     # Phone normalization to E.164 -- BUILT
│       ├── retry.py                     # tenacity retry decorators -- BUILT
│       └── rate_limit.py               # CircuitBreaker class -- BUILT
├── tests/                               # Test suite
│   ├── conftest.py                      # Fixtures: in-memory DB, settings -- BUILT
│   ├── factories.py                     # Factory Boy factories -- BUILT
│   └── unit/                            # 64 tests passing
│       ├── test_decay.py               # ~12 parametrized tests -- BUILT
│       ├── test_stacking.py             # ~8 tests -- BUILT
│       ├── test_scoring.py              # ~15 tests -- BUILT
│       ├── test_address.py              # ~6 tests -- BUILT
│       └── test_signal_detection.py     # ~23 tests -- BUILT
└── data/                                # Data directory (gitignored)
    ├── mls_imports/                     # Drop MLS CSVs here
    └── processed/                       # Archived after import
```

### Data Connectors Summary

| Connector | Auth | Direction | Frequency | Phase | Cost |
|-----------|------|-----------|-----------|-------|------|
| MLS CSV | None (file) | Ingest | On-demand | 1 | Free |
| Collier County PA | None (HTTP GET) | Ingest | Monthly | 2 | Free |
| Lee County PA (LEEPA) | None (HTTP GET) | Ingest | Monthly | 2 | Free |
| Clerk of Court (Sunshine Law) | None (CSV/email) | Ingest | Monthly | 2 | Free |
| Code Enforcement | None (CSV/email) | Ingest | Quarterly | 2 | Free |
| Redfin Data Center | None (S3 GET) | Ingest | Weekly | 2 | Free |
| Craigslist FSBO | None (RSS) | Ingest | Daily | 2 | Free |
| FL Sunbiz LLC | None (SFTP) | Ingest | Quarterly | 2 | Free |
| MLS RESO API (Trestle) | OAuth 2.0 | Ingest | Every 30 min | 2 | ~$42/mo |
| Follow Up Boss CRM | HTTP Basic | Push + Pull | On score + hourly | 4 | $58/mo |
| BatchLeads skip trace | Bearer | Enrich | On-demand (S/A only) | 4 | $99/mo |
| ATTOM | API key | Enrich | Weekly + on-demand | 5 | $250/mo |

### Scoring Engine

```
Signal Detection -> Decay Functions -> Freshness Premium -> Sum Points
                                                              |
                                          Stacking Rules (best single match)
                                                              |
                                          Normalize to 0-100 -> Assign Tier
```

**20 signal types** across 5 categories (MLS, public record, life event, market, digital).

**4 decay functions**: linear, exponential, step, escalating (deadline-driven).

**6 stacking rules**: distressed_seller (1.5x), financial_distress (2.0x), life_event_vacant (2.5x), tired_landlord (1.8x), failed_sale (1.4x), divorce_property (1.6x).

**5 tiers**: S (80-100, same day) -> A (60-79, 48 hrs) -> B (40-59, this week) -> C (20-39, monthly) -> D (0-19, monitor).

All configurable via `config/scoring_weights.yaml` -- no code changes needed to tune.

### Address Matching Architecture (Phase 2)

Cross-referencing MLS leads with public records requires robust address matching. The matching pipeline uses a 4-strategy cascade.

```
Source Record (PA/Clerk/Code Enforcement)
    |
    v
Strategy 1: Parcel ID exact match (highest confidence)
    |-- Match? -> Link to PropertyRow
    |-- No match? -> Continue
    v
Strategy 2: Normalized address exact match
    |-- Match? -> Link to PropertyRow
    |-- No match? -> Continue
    v
Strategy 3: Fuzzy address match (Levenshtein distance < 3)
    |-- Match? -> Link to PropertyRow (flag for review)
    |-- No match? -> Continue
    v
Strategy 4: Owner name + ZIP match
    |-- Match? -> Link to PropertyRow (flag for review)
    |-- No match? -> Create new PropertyRow from public record
```

**Key files**: `matching/address_matcher.py`, `matching/record_mapper.py`, `pipelines/match.py`

---

## Cost Projection

| Month | Phase | Monthly Spend | Cumulative | Expected Revenue |
|-------|-------|--------------|------------|-----------------|
| 0 (Day 1) | Phase 0 | $0 | $0 | -- |
| 1 | Phase 1 (MVP) | $0 | $0 | Leads in pipeline |
| 1-2 | Phase 2 (free data) | $0 | $0 | More leads, richer signals |
| 2 | Phase 2.6 (API, optional) | $42 | $42 | Automated MLS ingestion |
| 2-3 | Phase 3 (dashboard) | $0 | $42 | Visual lead management |
| 3 | Phase 4 (CRM + skip trace) | $157 | $199 | First listings, CRM pipeline |
| 4 | Phase 5 (intelligence) | $407 | $606 | Predictive edge, first closings |
| 5 | Phase 5+6 | $407 | $1,013 | Multiple closings |
| 6 | Phase 6 | $407 | $1,420 | Steady, optimized pipeline |

**Phase 2 costs $0/month** -- all 8 data sources are free public records or free data feeds. The optional MLS RESO API via Trestle adds ~$42/month (prorated from ~$500/year) but is not required while CSV exports remain the primary ingestion path.

**Break-even**: First closed deal (~$10K commission) covers the entire first year of tool costs. Expected in Month 3-4.

**Total 6-month spend**: $1,420 (down from $2,637 in the original plan -- a 46% reduction).

**6-Month Revenue Scenarios**:
- Conservative: $40,000 GCI (4 deals)
- Moderate: $60,000 GCI (6 deals)
- Aggressive: $80,000+ GCI (8+ deals)

### Cost Comparison: Original vs. Revised Plan

| Phase | Original Monthly | Revised Monthly | Savings |
|-------|-----------------|-----------------|---------|
| Phase 2 | $160 (REDX $100 + FUB $58) | $0 (free data sources) | $160/mo |
| Phase 3 | $160 | $0 | $0 |
| Phase 4 | $450 | $157 (FUB $58 + skip $99) | $293/mo |
| Phase 5 | $650 | $407 (FUB $58 + skip $99 + ATTOM $250) | $243/mo |
| Phase 6 | $650 | $407 | $243/mo |

---

## Kill Criteria

| What to Kill | When | Do Instead |
|-------------|------|------------|
| A lead source | 0 responses after 90 days + 100 leads | Reallocate to best-performing source |
| A public record source | <2 actionable leads per month after 3 months | Drop the data pipeline, use manual checks |
| Direct mail campaign | <0.5% response after 3 mailings (500+ pieces) | Change format/audience or stop |
| Skip tracing subscription | <10% valid phone numbers on S/A leads for 60 days | Switch providers (Tracerfy, REISkip) or use free tools |
| ATTOM API | No score calibration improvement after 60 days | Downgrade to manual enrichment via county PA data |
| Trestle API | CSV exports provide equivalent data quality | Cancel subscription, stay on CSV workflow |
| Follow Up Boss | Operator prefers brokerage CRM or manual tracking | Cancel, export data, use briefing emails only |
| Predictive model | <30% precision on expiration predictions | Fall back to rules-based flags |
| A/B test | No signal after 60 days | Pick cheaper option, move on |
| **The entire system** | **Operator hasn't used it for 2 consecutive weeks** | **Conversation. Redesign around what the operator actually uses.** |

---

## Decision Points

Questions to ask the Realtor before/during build.

### Before Starting -- RESOLVED

- [x] Which ZIP codes / neighborhoods to focus on?
  **RESOLVED**: 52 ZIP codes across Lee County + Collier County, configured in `config/market.yaml`. Covers Cape Coral, Fort Myers, Naples, Lehigh Acres, Bonita Springs, Estero, Marco Island, North Fort Myers, Fort Myers Beach.
- [x] What is the MLS platform?
  **RESOLVED**: CoreLogic Matrix (SWFLA MLS). API via CoreLogic Trestle (RESO Web API). See `Research/NABOR_API_Access_Guide.md`.
- [x] Who is the Realtor?
  **RESOLVED**: Yani (Ianula Moen), William Raveis Real Estate, Cape Coral FL. Licensed through NABOR (Naples Area Board of REALTORS) with SWFLA MLS access.
- [ ] Does the brokerage already provide a CRM?
  **UNRESOLVED**: Ask Yani if William Raveis provides a CRM. If yes, evaluate before subscribing to Follow Up Boss ($58/mo).
- [ ] Is the operator comfortable door-knocking for expired/pre-foreclosure leads?
  **UNRESOLVED**: Determines whether map view driving-route optimization is worth building in Phase 3.

### After Phase 1 (Week 2)
- [ ] After 3 days of briefing emails -- what is missing? What info does the operator wish they had?
- [ ] Does the operator want S-tier alerts as separate instant emails?
- [ ] Are the scoring tiers calibrated to the operator's intuition? Do S-tier leads feel genuinely urgent?

### After Phase 2 (Week 4)
- [ ] Which public record sources produce the most actionable leads? (Prioritize pipeline investment accordingly)
- [ ] Is the Sunshine Law request workflow sustainable, or do we need to automate with Playwright?
- [ ] Has Yani applied for Trestle API credentials? If not, is the CSV workflow sufficient?

### After Phase 3 (Month 2)
- [ ] Does the operator use the dashboard or just the emails? (Invest accordingly)
- [ ] Phone or desktop primarily? (Drives mobile investment)
- [ ] What metrics does the operator actually look at? (Don't build dashboards that get ignored)
- [ ] Is the public records view useful, or is the email briefing sufficient?

### After Phase 4 (Month 3)
- [ ] Does the operator like Follow Up Boss, or prefer a different CRM?
- [ ] Is skip tracing producing valid contact info? What is the hit rate?
- [ ] Are AI lead summaries useful, or does the operator prefer raw signal data?

### After Phase 5 (Month 4)
- [ ] Is the operator comfortable with pre-expiration outreach to active listings?
- [ ] At $407/month, is the ROI there? How many deals from the system?
- [ ] How many direct mail pieces per month feels right?
- [ ] Is ATTOM enrichment adding value over free county PA data?

---

## Research Reference Index

All research files in `Research/` directory (21 files, 25,000+ lines):

| File | Size | Use For |
|------|------|---------|
| `MASTER_RESEARCH.md` | 20 KB | Overview, top 10 strategies, signal stacking table |
| `mls_data_analysis.md` | 60 KB | MLS saved search setup, daily workflow, Matrix export config |
| `public_records_strategies.md` | 66 KB | 12 public record sources, cross-referencing techniques |
| `lead_scoring_models.md` | 102 KB | Signal weights, decay math, tiers, scoring algorithm |
| `creative_strategies.md` | 79 KB | 22 innovative strategies, lifecycle prediction |
| `competitive_analysis.md` | 68 KB | 14 platforms, 5 gaps we exploit |
| `reso_api_integration.md` | 106 KB | RESO Web API, OAuth, OData queries, Python client patterns |
| `legal_compliance_framework.md` | 86 KB | DNC/TCPA/CAN-SPAM, FL state rules, compliance checklists |
| `outreach_templates.md` | 89 KB | Scripts for 12 lead types, drip sequences, timing |
| `python_implementation.md` | 138 KB | **Primary build blueprint**: models, connectors, engine, tests |
| `local_data_sources.md` | 83 KB | County portals, FOIA templates, 10-state snapshot |
| `roi_metrics_framework.md` | 85 KB | KPIs, funnels, A/B testing, income projections |
| `dashboard_frameworks.md` | 33 KB | Framework comparison (NiceGUI selected) |
| `dashboard_ux_design.md` | 38 KB | UX patterns, mobile, accessibility |
| `dashboard_examples.md` | 31 KB | Real-world dashboard inspiration |
| `automation_integrations.md` | 29 KB | CRM, email, workflow automation |
| `data_pipeline_architecture.md` | 45 KB | ETL patterns, DB design, sync strategies |
| `NABOR_API_Access_Guide.md` | 15 KB | **CoreLogic Trestle API**: registration, auth, endpoints, costs, compliance |
| `Interim_Data_Playbook.md` | 17 KB | **Pre-API data strategy**: Matrix exports, county downloads, free sources |
| `Free_Data_Automation_Plan.md` | 75 KB | **Phase 2 blueprint**: 8 free data sources, schemas, automation specs |
| `clerk_of_court_automation_research.md` | 30 KB | **Clerk records**: Lee + Collier feasibility, Sunshine Law templates, aggregator alternatives |

---

*This build plan was compiled from 6 parallel planning agents analyzing 25,000+ lines of research across 21 files. Each phase is designed to deliver value incrementally -- the operator benefits from Day 1, and the system gets smarter every month. Phase 2 prioritizes free data sources ($0/month) before any paid services, keeping the barrier to ROI as low as possible.*
