# YaniVision: Master Build Plan

> **Project**: Data-driven real estate lead generation system
> **Builder**: Husband (developer) for wife (licensed Realtor with MLS access)
> **Status**: Research complete (19,800+ lines across 16 files). Ready to build.
> **Created**: 2026-02-28
> **Compiled from**: 6 parallel planning agents analyzing all research files

---

## Executive Summary

YaniVision is a Python-based intelligence system that mines MLS data, public records, and digital signals to find motivated real estate sellers and buyers before competitors. The wife's MLS access is the competitive moat -- no existing tool does deep MLS behavioral analysis.

**The plan has 7 phases, starting with $0 cost on Day 1 and scaling to ~$650/month by Month 4.** The system is usable and delivering value by Week 2.

**Expected 6-month ROI**: $40,000-$80,000 GCI on ~$3,000 total investment (1,300-2,700% return).

---

## Table of Contents

1. [Phase 0: Immediate Value (Day 1)](#phase-0-immediate-value-day-1--0)
2. [Phase 1: MVP (Weeks 1-2)](#phase-1-mvp-weeks-1-2--0month)
3. [Phase 2: Automated Pipeline (Weeks 3-4)](#phase-2-automated-pipeline-weeks-3-4--160month)
4. [Phase 3: Dashboard (Month 2)](#phase-3-dashboard-month-2--160month)
5. [Phase 4: Integrations (Month 2-3)](#phase-4-integrations-month-2-3--450month)
6. [Phase 5: Intelligence Engine (Month 3-4)](#phase-5-intelligence-engine-month-3-4--650month)
7. [Phase 6: Optimization (Month 4+)](#phase-6-optimization-month-4--650month)
8. [Technical Architecture](#technical-architecture)
9. [Cost Projection](#cost-projection)
10. [Kill Criteria](#kill-criteria)
11. [Decision Points](#decision-points)

---

## Phase 0: Immediate Value (Day 1) — $0

**Goal**: She finds better leads TODAY using research insights + MLS access + free tools. Zero code.

### Deliverables

| # | Task | Time | Source |
|---|------|------|--------|
| 1 | Configure 10 MLS saved searches (expireds, price reductions, high DOM, withdrawn, FSBO, back-on-market, agent churn) | 45 min | `mls_data_analysis.md` |
| 2 | Set up Google Alerts (company relocations, layoffs, new employers in market) | 15 min | `creative_strategies.md` |
| 3 | Create spreadsheet lead tracker with scoring reference card (S/A/B/C/D tiers) | 30 min | `lead_scoring_models.md` |
| 4 | Customize outreach templates with her name/brokerage (expired, FSBO, pre-foreclosure, probate scripts) | 1 hr | `outreach_templates.md` |
| 5 | Establish 30-minute daily workflow (check searches, score leads, plan outreach) | 15 min | `MASTER_RESEARCH.md` Sec 2 |
| 6 | Register for DNC list access, review MLS ToS, check state foreclosure rules | 30 min | `legal_compliance_framework.md` |

### Success Criteria
- 10 saved searches producing daily results
- First 10+ leads identified and scored
- First outreach attempts made
- All templates customized and ready

### Value to Realtor
Goes from zero systematic prospecting to a structured daily pipeline. Ahead of 80% of agents operating on random referrals.

---

## Phase 1: MVP (Weeks 1-2) — $0/month

**Goal**: Automate the most painful manual step. CSV import → signal detection → scoring → daily briefing email.

### What Gets Built

```
Wife exports CSV from MLS portal (5 min)
    → drops in folder
        → YaniVision ingests, deduplicates, detects signals
            → scores and tiers all leads
                → sends daily briefing email at 6:30 AM
```

### Build Order (27 steps, dependency-driven)

#### Foundation (Steps 1-11)

| Step | File | What | Complexity |
|------|------|------|------------|
| 1 | Directory scaffolding + `__init__.py` files | Create project structure | Simple |
| 2 | `pyproject.toml` | Dependencies: pydantic, sqlalchemy, aiosqlite, httpx, apscheduler, jinja2, pyyaml, structlog | Simple |
| 3 | Virtual env + `pip install -e ".[dev]"` | Dev environment | Simple |
| 4 | `.env.example` + `.gitignore` | Config template, ignore secrets + data | Simple |
| 5 | `yanivision/models/enums.py` | Tier, LeadStatus, SignalCategory, DecayType, MLSStatus, OutreachType, OutreachOutcome | Simple |
| 6 | `config/settings.py` | Pydantic Settings (~45 fields across 10 categories) | Medium |
| 7 | `yanivision/utils/logging.py` | structlog setup (JSON prod, colored dev) | Medium |
| 8 | `yanivision/utils/address.py` | USPS address normalization for dedup | Medium |
| 9 | `yanivision/utils/phone.py` | Phone normalization to E.164 | Simple |
| 10 | `yanivision/utils/retry.py` | tenacity retry decorators (api_retry, gentle_retry) | Simple |
| 11 | `yanivision/utils/rate_limit.py` | CircuitBreaker class | Medium |

#### Data Models (Steps 12-17)

| Step | File | What | Complexity |
|------|------|------|------------|
| 12 | `yanivision/models/property.py` | PropertyBase/Valuation/MLS/Owner composite model | Medium |
| 13 | `yanivision/models/signal.py` | Signal, SignalCreate, SignalConfig | Medium |
| 14 | `yanivision/models/score.py` | ScoreResult, ScoreHistory | Simple |
| 15 | `yanivision/models/outreach.py` | OutreachEvent, OutreachEventCreate | Simple |
| 16 | `yanivision/models/lead.py` | Lead with computed fields (score_change, days_since_detection) | Medium |
| 17 | `yanivision/models/__init__.py` | Re-export all models | Simple |

#### Scoring Engine (Steps 18-20)

| Step | File | What | Complexity |
|------|------|------|------------|
| 18 | `config/scoring_weights.yaml` | 20 signal types + 6 stacking rules + tier thresholds | Simple |
| 19 | `config/feature_flags.yaml` | Data sources, integrations, notifications toggles | Simple |
| 20 | `yanivision/scoring/config_loader.py` | Load YAML → SignalConfig + StackingRule + TierConfig | Simple |

#### Database (Steps 21-24)

| Step | File | What | Complexity |
|------|------|------|------------|
| 21 | `yanivision/storage/database.py` | 7 SQLAlchemy tables + async engine + session factory | Complex |
| 22 | `yanivision/storage/repositories.py` | PropertyRepo, LeadRepo, SignalRepo, ScoreHistoryRepo, SyncLogRepo | Complex |
| 23 | `yanivision/storage/queries.py` | Named queries for briefing, lead list, map | Medium |
| 24 | `alembic.ini` + `alembic/env.py` | Migration setup (generate initial schema) | Medium |

#### Tests + Factories (Steps 25-27)

| Step | File | What | Complexity |
|------|------|------|------------|
| 25 | `.pre-commit-config.yaml` | ruff + mypy hooks | Simple |
| 26 | `tests/conftest.py` | In-memory DB, settings, scoring engine, fixed timestamp fixtures | Medium |
| 27 | `tests/factories.py` | PropertyFactory, LeadFactory, SignalFactory (Factory Boy) | Medium |

#### Scoring + Detection + Briefing (the payoff)

| Step | File | What | Complexity |
|------|------|------|------------|
| 28 | `yanivision/scoring/decay.py` | 4 decay functions (linear, exponential, step, escalating) + freshness premium | Low |
| 29 | `yanivision/scoring/stacking.py` | 6 stacking rules, best-single-rule algorithm | Low-Med |
| 30 | `yanivision/scoring/engine.py` | ScoringEngine.calculate() — the core intelligence | Medium |
| 31 | `yanivision/sources/base.py` | Abstract DataSourceConnector + SyncResult | Medium |
| 32 | `yanivision/sources/mls_csv.py` | CSV import from MLS exports (FlexMLS/Matrix column mapping) | Low |
| 33 | `yanivision/pipelines/detect.py` | SignalDetector — 12 detection rules for MLS signals | Medium |
| 34 | `yanivision/pipelines/score.py` | ScorePipeline — fetch signals, calculate, persist, detect tier changes | Medium |
| 35 | `yanivision/pipelines/ingest.py` | IngestPipeline — CSV read, normalize, deduplicate, upsert | Medium |
| 36 | `yanivision/notifications/email.py` | SMTP email sender (Gmail free) | Low |
| 37 | `yanivision/notifications/templates/daily_briefing.html` | Jinja2 HTML email template | Medium |
| 38 | `yanivision/pipelines/briefing.py` | BriefingGenerator — hot leads, tier movers, pipeline summary | Medium |
| 39 | `yanivision/main.py` | CLI runner: import → detect → score → email | Low |

#### Unit Tests

| Step | File | Test Count |
|------|------|-----------|
| 40 | `tests/unit/test_decay.py` | ~12 parametrized tests |
| 41 | `tests/unit/test_stacking.py` | ~8 tests |
| 42 | `tests/unit/test_scoring.py` | ~9 tests |
| 43 | `tests/unit/test_address.py` | ~6 tests |
| 44 | `tests/unit/test_signal_detection.py` | ~10 tests |

### Verification Checkpoint
- `ruff check .` passes
- `pytest tests/` — all ~45 tests green
- `alembic upgrade head` creates SQLite DB with 7 tables
- Drop a CSV in `data/mls_imports/`, run `python -m yanivision`, receive briefing email

### Success Criteria
- Wife exports CSV, drops in folder, runs one command → scored briefing email in 60 seconds
- Scoring matches her manual intuition from Phase 0 spreadsheet
- Briefing tells her exactly who to call first

### Value to Realtor
Eliminates 20-30 min/day of manual spreadsheet work. Signal stacking catches combinations manual review would miss.

---

## Phase 2: Automated Pipeline (Weeks 3-4) — $160/month

**Goal**: Remove manual CSV export. Automate everything. Add CRM.

### What Gets Built

| # | Component | File(s) | Cost |
|---|-----------|---------|------|
| 1 | **Pipeline orchestrator** | `pipelines/orchestrator.py` | $0 |
| 2 | **APScheduler** (6:00 ingest, 6:15 rescore, 6:30 briefing, 7:00 CRM sync) | In orchestrator | $0 |
| 3 | **RESO API connector** (if available) OR enhanced CSV automation | `sources/mls.py` | $0 |
| 4 | **REDX expired/FSBO feed** connector | `sources/expired_feed.py` | $100/mo |
| 5 | **Follow Up Boss CRM** integration | `integrations/crm.py` | $58/mo |
| 6 | **S-tier instant alerts** | `notifications/templates/s_tier_alert.html` | $0 |
| 7 | **Notification dispatcher** (route by tier) | `notifications/dispatcher.py` | $0 |
| 8 | **Deduplication pipeline** | `pipelines/deduplicate.py` | $0 |
| 9 | **DNC scrubbing step** | Built into pipeline | $0 |

### Schedule

| Job | Time | Description |
|-----|------|-------------|
| `morning_pipeline` | 06:00 | Ingest from all sources → detect → score |
| `daily_rescore` | 06:15 | Re-score all leads (apply decay) |
| `daily_briefing` | 06:30 | Generate + send HTML email |
| `crm_sync` | 07:00 | Push S/A leads to Follow Up Boss |
| `urgency_decay` | Every 6h | Re-score for time decay |
| `weekly_public_records` | Mon 05:00 | County recorder check |

### Success Criteria
- System runs fully unattended every morning
- S-tier leads appear in CRM within minutes
- Wife's workflow: check email, review briefing, make calls — 10 min total

### Value to Realtor
Fully automated morning pipeline. S-tier leads go straight into CRM with action plan. REDX provides phone numbers. Daily workflow drops from 30 → 10 minutes.

---

## Phase 3: Dashboard (Month 2) — $160/month

**Goal**: Web UI so she can see leads visually, not just via email.

### Framework: NiceGUI 2.x

Chosen over Streamlit (no WebSocket push), Dash (callback hell), and React (overkill). NiceGUI gives: pure Python, Quasar Material Design, native Leaflet maps, AG Grid tables, ECharts, PWA support for mobile, and FastAPI backend.

### Pages (build order = maximum value delivery)

| Phase | Days | Page | Key Components |
|-------|------|------|----------------|
| 1 | 1-2 | App Shell | Nav, auth, dark mode, theme |
| 2 | 3-5 | **Lead Pipeline** `/leads` | AG Grid table, tier/signal badges, filter bar, action buttons |
| 3 | 6-8 | **Lead Detail** `/leads/{id}` | Score gauge, signal stack, owner info, activity timeline, outreach log |
| 4 | 9-11 | **Morning Briefing** `/` | 4 KPI cards, priority actions, new leads, score changes, market pulse |
| 5 | 12-15 | **Map View** `/map` | Leaflet map, tier-colored pins, heat map, marker clustering, sidebar |
| 6 | 16-18 | **Analytics** `/analytics` | Conversion funnel, ROI by source, score distribution, signal performance |
| 7 | 19-22 | **Settings** `/settings` | Scoring weight editor, data source toggles, notification prefs, CSV import |
| 8 | 23-26 | Mobile Polish | Responsive layouts, PWA manifest, bottom tab bar, real-time push |

### File Structure (28 new files)

```
yanivision/dashboard/
├── app.py                    # NiceGUI setup, routing, auth
├── theme.py                  # Colors, tier/signal palette, Tailwind
├── components/               # 11 reusable components
│   ├── kpi_card.py          # Value + delta + sparkline
│   ├── lead_card.py         # Compact lead summary
│   ├── tier_badge.py        # S/A/B/C/D colored badge
│   ├── signal_badge.py      # Signal type indicator
│   ├── score_gauge.py       # EChart radial gauge
│   ├── score_bar.py         # Linear progress bar
│   ├── action_buttons.py    # Call/CMA/Email group
│   ├── activity_timeline.py # Quasar timeline
│   ├── notification_bell.py # Header bell + badge
│   ├── market_pulse_table.py
│   └── filter_bar.py
├── pages/                    # 6 page views
│   ├── briefing.py, leads.py, lead_detail.py
│   ├── map_view.py, analytics.py, settings.py
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
| Push to CRM | "Add to CRM" | Creates Follow Up Boss contact with full context |

### Success Criteria
- Dashboard loads in <2 seconds, works on her phone
- She can manage leads without touching a spreadsheet
- Map view helps plan driving routes

---

## Phase 4: Integrations (Month 2-3) — $450/month

**Goal**: Skip tracing, public records, AI summaries, direct mail.

### New Components

| # | Component | File | Cost |
|---|-----------|------|------|
| 1 | **BatchLeads skip trace** (auto for S/A tier) | `sources/skip_trace.py` | $99/mo |
| 2 | **Public records automation** (county NODs, probate, tax) | `sources/public_records.py` | $0 (manual) |
| 3 | **Claude AI lead summaries** | `integrations/ai.py` | $5-20/mo |
| 4 | **Direct mail automation** (Click2Mail/Handwrytten) | `integrations/mail.py` | $50-150/mo |
| 5 | **CMA PDF generation** (WeasyPrint) | `reports/cma.py` | $0 |
| 6 | **DNC + compliance automation** | `pipelines/compliance.py` | $0 |

### Compliance Requirements (Critical)
- DNC scrubbing mandatory before phone numbers reach the Realtor
- Pre-foreclosure: state-specific waiting periods enforced in code (e.g., CA: 5 business days after NOD)
- Probate: 30-day minimum wait after filing
- TCPA: system MUST NOT send automated texts without documented consent
- Fair Housing: all mail templates reviewed
- Contact frequency limits enforced (max 3 calls/week per lead)

### Value to Realtor
Complete actionable intelligence: phone numbers, email addresses, AI summaries, CMA ready to send, and a suggested script. For distress leads, sensitive letters sent automatically with waiting periods enforced.

---

## Phase 5: Intelligence Engine (Month 3-4) — $650/month

**Goal**: Build what no competitor has. This is the competitive moat.

### New Components

| # | Component | What | Cost |
|---|-----------|------|------|
| 1 | **ATTOM API** | Property enrichment, equity, owner, foreclosure | $250/mo |
| 2 | **MLS behavioral analysis** | Price velocity, DOM deviation, listing lifecycle patterns | $0 |
| 3 | **Agent performance database** | Sell-through rate, failure rate for top 50 agents | $0 |
| 4 | **Predictive listing failure** | Logistic regression: which active listings will expire? | $0 |
| 5 | **Neighborhood heat mapping** | Absorption rate, momentum, price trends by micro-area | $0 |
| 6 | **Enhanced signal stacking** | MLS + public records + ATTOM cross-correlation | $0 |

### The Killer Feature: Pre-Expiration Leads
Contact likely-to-fail listings BEFORE they expire — weeks ahead of every REDX subscriber. No existing tool does this.

### Value to Realtor
Unfair advantage. She contacts failing listings before expiration, knows which agents underperform, and surfaces multi-signal convergence leads (15-25% conversion probability) that no single tool catches.

---

## Phase 6: Optimization (Month 4+) — $650/month

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
Lead → Score → Outreach → Outcome recorded in CRM
                                    ↓
                    Signal effectiveness analysis
                                    ↓
                    Weight adjustment suggestions
                                    ↓
                    Human review → YAML update → Re-score all
```

The system NEVER auto-adjusts weights. It suggests changes; the human approves.

---

## Technical Architecture

### Tech Stack

| Layer | Tool | Cost |
|-------|------|------|
| Language | Python 3.11+ | Free |
| Models | Pydantic v2 | Free |
| Database | SQLite → PostgreSQL | Free |
| ORM | SQLAlchemy 2.0 (async) | Free |
| HTTP | httpx | Free |
| Scheduling | APScheduler | Free |
| Dashboard | NiceGUI 2.x | Free |
| Email | SMTP / SendGrid | Free |
| Logging | structlog | Free |
| Testing | pytest + Factory Boy | Free |
| Linting | ruff + mypy | Free |

### Project Structure

```
YaniVision/
├── CLAUDE.md
├── MASTER_BUILD_PLAN.md          # This file
├── Research/                      # 16 research files (19,800+ lines)
├── yanivision/                    # Python package root
│   ├── pyproject.toml
│   ├── .env.example
│   ├── alembic.ini
│   ├── alembic/
│   ├── config/
│   │   ├── settings.py           # Pydantic Settings (45 fields)
│   │   ├── scoring_weights.yaml  # Signal weights, stacking rules, tiers
│   │   └── feature_flags.yaml    # Data source + integration toggles
│   ├── yanivision/
│   │   ├── main.py               # Entrypoint: scheduler + NiceGUI
│   │   ├── models/               # 6 Pydantic model files
│   │   ├── sources/              # 7 data connectors
│   │   │   ├── base.py           # Abstract connector + SyncResult
│   │   │   ├── mls_csv.py        # CSV import (Phase 1)
│   │   │   ├── mls.py            # RESO Web API (Phase 2+)
│   │   │   ├── expired_feed.py   # REDX (Phase 2)
│   │   │   ├── attom.py          # ATTOM enrichment (Phase 5)
│   │   │   ├── skip_trace.py     # BatchLeads (Phase 4)
│   │   │   └── public_records.py # County data (Phase 4)
│   │   ├── scoring/
│   │   │   ├── engine.py         # ScoringEngine.calculate()
│   │   │   ├── decay.py          # 4 decay functions + freshness
│   │   │   ├── stacking.py       # 6 stacking rules
│   │   │   ├── config_loader.py  # YAML → config objects
│   │   │   ├── feedback.py       # Calibration + effectiveness (Phase 6)
│   │   │   └── ml_model.py       # ML training (Phase 6)
│   │   ├── pipelines/
│   │   │   ├── orchestrator.py   # APScheduler daily pipeline
│   │   │   ├── ingest.py         # Fetch + normalize + dedup + upsert
│   │   │   ├── detect.py         # SignalDetector (12+ rules)
│   │   │   ├── score.py          # ScorePipeline wrapper
│   │   │   ├── deduplicate.py    # Address-based dedup
│   │   │   ├── briefing.py       # Daily briefing generator
│   │   │   └── compliance.py     # DNC scrub + suppression (Phase 4)
│   │   ├── notifications/
│   │   │   ├── email.py          # SMTP + SendGrid senders
│   │   │   ├── dispatcher.py     # Route by tier urgency
│   │   │   └── templates/        # Jinja2 HTML email templates
│   │   ├── integrations/
│   │   │   ├── crm.py            # Follow Up Boss client (Phase 2)
│   │   │   ├── ai.py             # Claude API summaries (Phase 4)
│   │   │   └── mail.py           # Direct mail API (Phase 4)
│   │   ├── storage/
│   │   │   ├── database.py       # 7 SQLAlchemy tables + engine
│   │   │   ├── repositories.py   # CRUD repos for all tables
│   │   │   └── queries.py        # Named queries for dashboard
│   │   ├── dashboard/            # NiceGUI web UI (Phase 3)
│   │   │   ├── app.py, theme.py
│   │   │   ├── components/       # 11 reusable widgets
│   │   │   ├── pages/            # 6 page views
│   │   │   ├── dialogs/          # 5 modal dialogs
│   │   │   └── static/           # PWA manifest + icons
│   │   └── utils/
│   │       ├── address.py, phone.py, logging.py
│   │       ├── retry.py, rate_limit.py
│   ├── tests/
│   │   ├── conftest.py, factories.py
│   │   ├── unit/                 # ~45 tests
│   │   ├── integration/          # ~15 tests
│   │   └── e2e/                  # ~5 tests
│   └── data/
│       ├── mls_imports/          # Drop CSVs here
│       └── processed/            # Archived after import
```

### Data Connectors Summary

| Connector | Auth | Direction | Frequency | Phase | Cost |
|-----------|------|-----------|-----------|-------|------|
| MLS CSV | None (file) | Ingest | On-demand | 1 | Free |
| MLS RESO API | OAuth 2.0 | Ingest | Every 30 min | 2 | Free (MLS dues) |
| REDX | None (CSV) | Ingest | Daily | 2 | $100/mo |
| Follow Up Boss | HTTP Basic | Push + Pull | On score + hourly | 2 | $58/mo |
| BatchLeads | Bearer | Enrich | On-demand (S/A only) | 4 | $99/mo |
| ATTOM | API key | Enrich | Weekly + on-demand | 5 | $250/mo |

### Scoring Engine

```
Signal Detection → Decay Functions → Freshness Premium → Sum Points
                                                            ↓
                                        Stacking Rules (best single match)
                                                            ↓
                                        Normalize to 0-100 → Assign Tier
```

**20 signal types** across 5 categories (MLS, public record, life event, market, digital).

**4 decay functions**: linear, exponential, step, escalating (deadline-driven).

**6 stacking rules**: distressed_seller (1.5x), financial_distress (2.0x), life_event_vacant (2.5x), tired_landlord (1.8x), failed_sale (1.4x), divorce_property (1.6x).

**5 tiers**: S (80-100, same day) → A (60-79, 48 hrs) → B (40-59, this week) → C (20-39, monthly) → D (0-19, monitor).

All configurable via `scoring_weights.yaml` — no code changes needed to tune.

---

## Cost Projection

| Month | Phase | Monthly Spend | Cumulative | Expected Revenue |
|-------|-------|--------------|------------|-----------------|
| 0 (Day 1) | Phase 0 | $0 | $0 | — |
| 1 | Phase 1 + 2 start | $0 → $158 | ~$79 | Leads in pipeline |
| 2 | Phase 2 + 3 | $158 | $237 | First appointments |
| 3 | Phase 4 | $450 | $687 | First listing(s) |
| 4 | Phase 5 | $650 | $1,337 | First closing(s) |
| 5 | Phase 5+6 | $650 | $1,987 | Multiple closings |
| 6 | Phase 6 | $650 | $2,637 | Steady pipeline |

**Break-even**: First closed deal (~$10K commission) covers ~15 months of tool costs. Expected in Month 3-4.

**6-Month Revenue Scenarios**:
- Conservative: $40,000 GCI (4 deals)
- Moderate: $60,000 GCI (6 deals)
- Aggressive: $80,000+ GCI (8+ deals)

---

## Kill Criteria

| What to Kill | When | Do Instead |
|-------------|------|------------|
| A lead source | 0 responses after 90 days + 100 leads | Reallocate to best-performing source |
| Direct mail campaign | <0.5% response after 3 mailings (500+ pieces) | Change format/audience or stop |
| REDX subscription | <5% phone contact rate for 60 days | Try Vulcan7 or drop phone prospecting |
| ATTOM API | No score calibration improvement after 60 days | Downgrade to manual enrichment |
| Predictive model | <30% precision on expiration predictions | Fall back to rules-based flags |
| A/B test | No signal after 60 days | Pick cheaper option, move on |
| **The entire system** | **Wife hasn't used it for 2 consecutive weeks** | **Conversation. Redesign around what she actually uses.** |

---

## Decision Points

Questions to ask the Realtor before/during build:

### Before Starting
- [ ] Which 5-10 ZIP codes / neighborhoods to focus on?
- [ ] What is her MLS platform? (FlexMLS, Matrix, Paragon → determines RESO API availability)
- [ ] Does her brokerage already provide a CRM?
- [ ] Is she comfortable door-knocking for expired/pre-foreclosure leads?

### After Phase 1 (Week 2)
- [ ] After 3 days of briefing emails — what's missing? What info does she wish she had?
- [ ] Does she want S-tier alerts as separate instant emails?

### After Phase 2 (Week 4)
- [ ] Does she like Follow Up Boss, or prefer a different CRM?
- [ ] REDX vs Vulcan7? Start with REDX, switch if contact rates are poor.

### After Phase 3 (Month 2)
- [ ] Does she use the dashboard or just the emails? (Invest accordingly)
- [ ] Phone or desktop primarily? (Drives mobile investment)
- [ ] What metrics does she actually look at? (Don't build dashboards she ignores)

### After Phase 5 (Month 4)
- [ ] Is she comfortable with pre-expiration outreach to active listings?
- [ ] At $650/month, is the ROI there? How many deals from the system?
- [ ] How many direct mail pieces per month feels right?

---

## Research Reference Index

All research files in `Research/` directory:

| File | Lines | Use For |
|------|-------|---------|
| `MASTER_RESEARCH.md` | 367 | Overview, top 10 strategies, signal stacking table |
| `mls_data_analysis.md` | 982 | MLS saved search setup, daily workflow |
| `public_records_strategies.md` | 1,008 | 12 public record sources, cross-referencing |
| `lead_scoring_models.md` | 2,739 | Signal weights, decay, tiers, scoring math |
| `creative_strategies.md` | 1,343 | 22 innovative strategies, lifecycle prediction |
| `competitive_analysis.md` | ~800 | 14 platforms, 5 gaps we exploit |
| `reso_api_integration.md` | 2,647 | RESO Web API, OAuth, OData queries, Python client |
| `legal_compliance_framework.md` | 1,346 | DNC/TCPA/CAN-SPAM, state rules, checklists |
| `outreach_templates.md` | 1,623 | Scripts for 12 lead types, drip sequences |
| `python_implementation.md` | 4,019 | **Primary build blueprint**: models, connectors, engine, tests |
| `local_data_sources.md` | 1,584 | County portals, FOIA templates, 10-state snapshot |
| `roi_metrics_framework.md` | 1,808 | KPIs, funnels, A/B testing, income projections |
| `dashboard_frameworks.md` | — | Framework comparison (NiceGUI selected) |
| `dashboard_ux_design.md` | — | UX patterns, mobile, accessibility |
| `dashboard_examples.md` | — | Real-world dashboard inspiration |
| `automation_integrations.md` | — | CRM, email, workflow automation |
| `data_pipeline_architecture.md` | — | ETL patterns, DB design, sync strategies |

---

*This build plan was compiled from 6 parallel planning agents analyzing 19,800+ lines of research. Each phase is designed to deliver value incrementally — the Realtor benefits from Day 1, and the system gets smarter every month.*
