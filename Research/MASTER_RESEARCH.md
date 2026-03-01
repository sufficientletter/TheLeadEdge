# YaniVision: Master Research Document

> **Project**: Data-driven real estate lead generation for a licensed Realtor with MLS access
> **Created**: 2026-02-28
> **Status**: All Research Complete — Ready for Build Phase

---

## Executive Summary

This document synthesizes research from **17 deep-dive analyses** across two research rounds totaling **~19,800+ lines** of actionable intelligence. The research covers MLS data mining, public records, lead scoring, creative strategies, competitive analysis, dashboard design, automation, data pipelines, RESO API integration, legal compliance, outreach templates, Python implementation patterns, county-level data sources, and ROI metrics.

### The Core Insight

**Your wife's MLS access is the competitive moat.** No existing tool in the market does deep MLS behavioral analysis — they all treat MLS as a static data source rather than a behavioral signal engine. The opportunity is to build an intelligence layer that:

1. Mines MLS status changes, price patterns, and agent behavior as *leading indicators*
2. Cross-references MLS signals with public records for *signal stacking*
3. Scores and prioritizes leads automatically so outreach is focused on the highest-probability targets
4. Automates the daily research workflow that would take 2+ hours manually into a 10-minute morning briefing

---

## Table of Contents

1. [Top 10 Highest-ROI Strategies](#1-top-10-highest-roi-strategies)
2. [MLS Data Mining Summary](#2-mls-data-mining-summary)
3. [Public Records Summary](#3-public-records-summary)
4. [Creative & Innovative Strategies Summary](#4-creative--innovative-strategies-summary)
5. [Lead Scoring Framework](#5-lead-scoring-framework)
6. [Competitive Landscape & Gaps](#6-competitive-landscape--gaps)
7. [Recommended Tech Stack](#7-recommended-tech-stack)
8. [Implementation Roadmap](#8-implementation-roadmap)
9. [Detailed Research Files](#9-detailed-research-files)

---

## 1. Top 10 Highest-ROI Strategies

Ranked by conversion probability, effort required, and potential commission value:

| Rank | Strategy | Source | Conversion Rate | Effort | Why It Works |
|------|----------|--------|-----------------|--------|--------------|
| 1 | **Expired Listings (Same-Day Contact)** | MLS | 8-12% with CMA | Low | Proven motivation, no agent, frustrated seller |
| 2 | **Pre-Foreclosure / NOD** | Public Records | 1-3% mail, higher with door knock | Medium | Legal clock creates urgency, equity preservation motive |
| 3 | **Price Reduction Stacking (3+ drops)** | MLS | 5-8% | Low | Accelerating desperation pattern, still active listing |
| 4 | **Probate / Inherited Properties** | Court Records | 3-7% response | Medium | 60-70% of inherited properties sell within 24 months |
| 5 | **Absentee Owners + High DOM** | MLS + Tax Records | 4-6% | Low | Distant owners with stale listings = maximum motivation |
| 6 | **FSBO Failures (30+ days, 2+ reductions)** | MLS + Zillow | 6-10% | Low | Seller learned the hard way they need an agent |
| 7 | **Withdrawn & Relisted (Agent Change)** | MLS History | 5-7% | Low | Seller fired their agent — actively seeking new representation |
| 8 | **Comparable Sales Gaps** | MLS Comps | 2-4% | Medium | Properties that *should* list based on neighbor activity |
| 9 | **Past Client Lifecycle (7-10 yr owners)** | CRM + MLS | 10-15% | Low | Warm relationship, predictable move timing |
| 10 | **Professional Referral Network** | Relationships | 15-25% | High initially | Divorce attorneys, estate planners, relocation HR = pre-qualified |

### Signal Stacking Multiplier

When multiple signals converge on the same property, conversion probability multiplies:

| Signal Combination | Estimated Conversion | Priority |
|-------------------|---------------------|----------|
| Expired + Pre-foreclosure + Vacant | 15-25% | IMMEDIATE |
| Price reduction x3 + High DOM + Absentee | 10-15% | Same day |
| Probate + Out-of-state heir + Vacant | 8-12% | Within 48 hrs |
| FSBO expired + Divorce filing | 10-15% | Same day |
| Long-term owner + Tax delinquent + Code violation | 8-12% | Within week |

---

## 2. MLS Data Mining Summary

*Full details: [mls_data_analysis.md](mls_data_analysis.md)*

### 10 MLS Strategies Covered

1. **Expired Listings** — Tier 1/2/3 classification, day-by-day contact timeline from Day 0 through Day 90
2. **Price Reduction Patterns** — Desperate vs. strategic reductions, tracking active listings likely to expire
3. **Days on Market (DOM) Analysis** — Market-specific thresholds, seller psychology timeline Day 0-180+
4. **Withdrawn & Relisted** — 6 withdrawal reasons, CDOM-vs-DOM filter trick for catching resets
5. **FSBO Conversions** — Week-by-week engagement timeline, flat-fee brokerage office filtering
6. **Pocket Listings & Coming Soon** — Public record signals that predict listings before they happen
7. **Rental to Sale Conversions** — Cross-referencing expired rental listings, tired landlord identification
8. **MLS Status History Mining** — Serial expiration, fallen-through pendings, agent churning patterns
9. **Agent Activity Patterns** — Agent failure-rate database, predicting future expireds
10. **Comparable Sales Gaps** — "Hidden Equity" campaign for properties that should list but haven't

### Daily Workflow (30 min/morning)

| Check | Time | Action |
|-------|------|--------|
| New expireds (last 24 hrs) | 5 min | Pull list, prioritize Tier 1, send CMAs |
| New price reductions (3+) | 5 min | Track acceleration pattern, note for outreach |
| DOM threshold crossers | 5 min | Properties crossing 60/90/120 day marks |
| Status changes | 5 min | Withdrawn, back-on-market, pending-to-active |
| FSBO + Zillow cross-check | 5 min | New FSBOs, failed FSBOs re-entering market |
| Lead scoring update | 5 min | Score new leads, reprioritize pipeline |

---

## 3. Public Records Summary

*Full details: [public_records_strategies.md](public_records_strategies.md)*

### 12 Public Record Lead Sources

| Source | Where to Find | Check Frequency | Conversion |
|--------|--------------|-----------------|------------|
| Pre-Foreclosure / NOD | County Recorder, PropertyRadar | Weekly | 1-3% mail |
| Probate / Inherited | Probate Court dockets | Weekly | 3-7% |
| Divorce Filings | Family Court records | Weekly | 2-5% |
| Tax Delinquency | County Treasurer lists | Monthly | 1-3% |
| Code Violations | Municipal enforcement DB | Monthly | 2-4% |
| Absentee Owners | Tax assessor (mail vs site addr) | Quarterly | 2-4% |
| Long-Term Ownership (10+ yr) | Deed records | Quarterly | 1-2% |
| Estate & Trust Transfers | County Recorder | Weekly | 3-5% |
| Building Permits | Municipal permit office | Monthly | 1-2% |
| Tax Assessment Spikes | County Assessor | Annually | 1-2% |
| Utility Disconnections | FOIA to municipal utilities | Monthly | 2-4% |
| Corporate-Owned Residential | LLC/Corp ownership filters | Quarterly | 2-5% |

### Key Insight: Cross-Referencing Is Everything

A single signal (e.g., absentee owner) is a cold lead. Stack 2-3 signals (absentee + tax delinquent + code violation) and you have a 9/10 motivation score. The research identifies 4 specific cross-reference workflows that dramatically increase conversion.

---

## 4. Creative & Innovative Strategies Summary

*Full details: [creative_strategies.md](creative_strategies.md)*

### 22 Unconventional Strategies Across 4 Categories

**Digital Signal Mining (5 strategies)**
- Zillow "Make Me Move" monitoring, FSBO price reduction velocity tracking
- LinkedIn job change detection (relocation leads)
- Google Alerts for company relocations, layoffs, new employers
- Apartment complex negative review mining (renters ready to buy)
- Nextdoor "thinking about selling" post monitoring

**Creative Data Cross-Referencing (7 strategies)**
- NCOA (National Change of Address) data correlation
- School enrollment change tracking
- Wedding registry + renter data (newlywed buyer pipeline)
- Death records + property records (with 90-day ethical waiting period)
- Vehicle/voter registration address changes

**Market-Level Intelligence (6 strategies)**
- Institutional investor exit signals (REIT sell patterns)
- ARM reset mapping (interest rate sensitivity)
- Gentrification 3-stage pattern recognition
- Infrastructure announcement monitoring (CIP documents = 5-10 years advance knowledge)
- Zoning change monitoring (value unlock opportunities)

**Relationship-Based (4 strategies)**
- Social graph mapping for warm introductions
- Past client lifecycle prediction (average move cycle = 7-10 years)
- Professional referral tiers (divorce attorneys, estate planners, HR relocation)
- Builder/contractor intel (post-renovation sales)

### Top 3 Most Practical Creative Strategies

1. **Past Client Lifecycle Prediction** — Practicality: 5, Automation: 5, Reward: 5
2. **Google Alerts for Market Events** — Practicality: 5, Automation: 5, Reward: 4
3. **Professional Referral Network** — Practicality: 5, Automation: 2, Reward: 5

---

## 5. Lead Scoring Framework

*Full details: [lead_scoring_models.md](lead_scoring_models.md)*

### Weighted Scoring Model

```
Lead Score = Σ(Signal × Weight) × Urgency Decay × Value Multiplier
```

**Signal Weights (Tier 1 — Strongest Predictors)**

| Signal | Points | Why |
|--------|--------|-----|
| Pre-foreclosure / NOD | 20 | Legal deadline, maximum urgency |
| Probate filing | 18 | Asset liquidation required |
| Active divorce + property | 17 | Court-ordered disposition |
| Expired listing (< 30 days) | 15 | Proven motivation, no agent |
| Multiple price reductions | 12 | Accelerating desperation |

**Score Tiers & Action**

| Tier | Score | Action | Timeline |
|------|-------|--------|----------|
| S (Hot) | 80-100 | Immediate personal outreach | Same day |
| A (High) | 60-79 | Priority CMA + contact | Within 48 hrs |
| B (Warm) | 40-59 | Scheduled outreach sequence | Within week |
| C (Nurture) | 20-39 | Drip campaign | Monthly touch |
| D (Watch) | 0-19 | Monitor for signal changes | Quarterly |

### Urgency Decay

Leads lose value over time. The model includes three decay functions:
- **Linear decay** for standard signals (loses ~2 points/week)
- **Exponential decay** for time-sensitive signals like expireds (half-life = 14 days)
- **Step decay** for deadline-driven signals like foreclosure (full value until deadline, then cliff)
- **Freshness premium**: 1.5x bonus for leads identified within 4 hours

### Seller Motivation Matrix

Two-axis framework:

```
                    HIGH TIMELINE PRESSURE
                           |
            URGENT         |         DESPERATE
         (Divorce,         |      (Foreclosure,
          Job Transfer)    |       Tax Sale Date)
                           |
LOW MOTIVATION ————————————+———————————— HIGH MOTIVATION
                           |
         OPPORTUNISTIC     |        CONSIDERING
         (Equity Rich,     |      (Empty Nester,
          Curious)         |       Life Change)
                           |
                    LOW TIMELINE PRESSURE
```

Each quadrant gets a different outreach strategy, messaging framework, and contact cadence.

---

## 6. Competitive Landscape & Gaps

*Full details: [competitive_analysis.md](competitive_analysis.md)*

### Market Overview

14 platforms analyzed, 5 data providers evaluated, 5 CRMs compared.

**Top Platforms by Category:**
- **Property Data**: PropStream ($99/mo) — best filters, 150M+ properties
- **Expired/FSBO Lists**: REDX ($60-300/mo) — real-time expired feeds
- **Predictive Analytics**: SmartZip / Offrs — AI-powered seller prediction
- **Skip Tracing**: BatchLeads ($99/mo) — owner contact info
- **CRM**: Follow Up Boss ($69/mo) — best API, 250+ integrations

### The 5 Critical Gaps No Tool Fills

| Gap | What's Missing | Our Opportunity |
|-----|---------------|-----------------|
| **Deep MLS Behavioral Analysis** | No tool analyzes MLS status changes as behavioral signals | Build an MLS intelligence engine |
| **Cross-Source Signal Correlation** | Every tool operates in a silo | Multi-source signal stacking system |
| **Predictive Listing Failure** | No tool predicts which active listings will expire | Agent performance + pricing analysis |
| **Agent Performance Intelligence** | No consumer tool scores listing agents | Failure rate database for targeting |
| **Life Event + Property Correlation** | Public records and MLS are never combined | Unified lead scoring across sources |

### Build vs. Buy Recommendation

| Component | Recommendation | Why |
|-----------|---------------|-----|
| CRM | **Buy** (Follow Up Boss) | Mature, great API, industry standard |
| Skip Tracing | **Buy** (BatchLeads or PropStream) | Commodity service, hard to replicate |
| Direct Mail | **Buy** (Click2Mail, Handwrytten) | Commodity service |
| Expired/FSBO Feeds | **Buy** (REDX) | Real-time data feeds already exist |
| **MLS Intelligence Engine** | **BUILD** | Does not exist anywhere in market |
| **Multi-Source Lead Scorer** | **BUILD** | No tool does true signal stacking |
| **Daily Lead Briefing** | **BUILD** | Custom reporting for your workflow |

---

## 7. Recommended Tech Stack

### For the Custom Build Components

| Layer | Tool | Cost | Purpose |
|-------|------|------|---------|
| Language | Python | Free | Data processing, APIs, automation |
| Database | SQLite → PostgreSQL | Free | Lead storage, scoring history |
| Data APIs | ATTOM (~$250/mo), BatchData (~$50/mo) | ~$300/mo | Property data, public records |
| MLS Access | RESO Web API (via wife's board) | Included w/ MLS dues | MLS data extraction |
| CRM | Follow Up Boss | $69/mo | Lead management, outreach |
| Skip Trace | BatchLeads | $99/mo | Owner contact info |
| Expired Feeds | REDX | $60/mo | Real-time expired/FSBO lists |
| Mail | Click2Mail | Pay per piece | Automated direct mail |
| Hosting | Local machine or VPS | $0-20/mo | Run daily scripts |
| **Total Estimated** | | **~$550-650/mo** | Full lead intelligence system |

### Phased API Budget

| Phase | Monthly Cost | What You Get |
|-------|-------------|-------------|
| Bootstrap (free only) | $0 | MLS alerts, manual public records, Google Alerts |
| Starter | $160/mo | + Follow Up Boss + REDX |
| Growth | $450/mo | + BatchLeads + basic data APIs |
| Advanced | $650/mo | + ATTOM API + automated pipeline |

---

## 8. Implementation Roadmap

### Phase 1: Quick Wins (Week 1-2) — $0 Cost

- [ ] Set up 10 MLS saved searches (expireds, price reductions, high DOM, withdrawn, FSBO)
- [ ] Create Google Alerts for: company relocations, layoffs, new employers in your market
- [ ] Build a spreadsheet lead tracker with the scoring model from Section 5
- [ ] Identify top 5 agents with highest expired listing rates in your market
- [ ] Pull first batch of county pre-foreclosure filings
- [ ] Set up Nextdoor monitoring for "thinking about selling" posts
- [ ] Establish the 30-minute daily workflow

### Phase 2: Tool Integration (Week 3-4) — ~$160/mo

- [ ] Set up Follow Up Boss CRM
- [ ] Subscribe to REDX for expired/FSBO feeds
- [ ] Create drip campaigns for each lead tier (S/A/B/C)
- [ ] Build CMA templates for rapid same-day delivery to expired leads
- [ ] Start tracking conversion metrics from Week 1 leads

### Phase 3: Data Pipeline (Month 2) — ~$450/mo

- [ ] Add BatchLeads for skip tracing
- [ ] Build Python scripts to automate MLS data pulls (if RESO API available)
- [ ] Automate public record checks (county recorder, probate court)
- [ ] Create automated daily lead briefing email
- [ ] Implement lead scoring algorithm in code

### Phase 4: Intelligence Engine (Month 3+) — ~$650/mo

- [ ] Build MLS behavioral analysis engine (status change patterns, agent scoring)
- [ ] Implement multi-source signal stacking (MLS + public records + digital signals)
- [ ] Add ATTOM API for comprehensive property data enrichment
- [ ] Build predictive listing failure model (which active listings will expire?)
- [ ] Create neighborhood heat mapping dashboard
- [ ] Implement urgency decay and automatic lead re-scoring

### Phase 5: Machine Learning (Month 6+)

- [ ] Collect enough conversion data to train models
- [ ] Build logistic regression baseline, graduate to XGBoost
- [ ] Train on local market data for market-specific predictions
- [ ] Continuous model improvement with feedback loop

---

## 9. Detailed Research Files

### Round 1 — Strategy & Intelligence Research

| File | Lines | Focus |
|------|-------|-------|
| [mls_data_analysis.md](mls_data_analysis.md) | 982 | 10 MLS mining strategies, daily workflow, lead scoring matrix |
| [public_records_strategies.md](public_records_strategies.md) | 1,008 | 12 public record sources, cross-referencing workflows, legal framework |
| [lead_scoring_models.md](lead_scoring_models.md) | 2,739 | Scoring models, automation architecture, API guide, data pipeline design |
| [creative_strategies.md](creative_strategies.md) | 1,343 | 22 innovative strategies, implementation roadmap, tech stack |
| [competitive_analysis.md](competitive_analysis.md) | ~800 | 14 platforms, 5 data providers, gap analysis, build vs. buy |

### Round 2 — Dashboard & Infrastructure Research

| File | Lines | Focus |
|------|-------|-------|
| [dashboard_frameworks.md](dashboard_frameworks.md) | — | Dashboard technology evaluation |
| [dashboard_ux_design.md](dashboard_ux_design.md) | — | UX design patterns for lead dashboards |
| [dashboard_examples.md](dashboard_examples.md) | — | Real-world dashboard examples and inspiration |
| [automation_integrations.md](automation_integrations.md) | — | CRM, email, and workflow automation |
| [data_pipeline_architecture.md](data_pipeline_architecture.md) | — | ETL/ELT pipeline design patterns |

### Round 3 — Final Research (Build-Ready)

| File | Lines | Focus |
|------|-------|-------|
| [reso_api_integration.md](reso_api_integration.md) | 2,647 | RESO Web API standard, Python client, 10 OData queries, 6 MLS platform profiles |
| [legal_compliance_framework.md](legal_compliance_framework.md) | 1,346 | Federal/state regulations, compliance by channel & lead source, pre-campaign checklist |
| [outreach_templates.md](outreach_templates.md) | 1,623 | Messaging for 12 lead types, drip sequences, CMA letters, voicemail scripts |
| [python_implementation.md](python_implementation.md) | 4,019 | Full technical blueprint: data models, connectors, scoring engine, pipeline, DB schema, tests |
| [local_data_sources.md](local_data_sources.md) | 1,584 | County-level access, FOIA templates, 6 aggregator profiles, 10-state graded snapshot |
| [roi_metrics_framework.md](roi_metrics_framework.md) | 1,808 | KPIs, funnel metrics, A/B testing, financial projections, feedback loops |

**Total Research**: ~19,800+ lines across 16 files

---

## Legal & Ethical Reminders

- All outreach must comply with **Do Not Call**, **CAN-SPAM**, **TCPA**, and **Fair Housing Act**
- MLS terms of service must be respected — data cannot be resold or shared outside authorized use
- Sensitive situations (foreclosure, probate, divorce) require empathetic, service-oriented outreach
- Never scrape protected data — use APIs and authorized access only
- Maintain records of consent and opt-outs for all contact lists
- Check state-specific regulations (some states restrict foreclosure solicitation timing)
- See [legal_compliance_framework.md](legal_compliance_framework.md) for the comprehensive compliance guide

---

*This research was compiled across 3 rounds of parallel research agents (5 + 5 + 6 = 16 agents) covering strategy, infrastructure, and build-readiness. Each detailed file is available in the Research/ directory for deep dives into specific topics. The project is now ready to transition from research to build phase.*
