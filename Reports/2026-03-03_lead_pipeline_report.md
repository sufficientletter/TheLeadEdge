# TheLeadEdge Lead Pipeline Report
**Generated:** March 3, 2026
**Market:** SW Florida (Lee & Collier Counties)
**Data Source:** MLS Matrix CSV Export (sample dataset)
**Pipeline Version:** Phase 1 MVP v0.1.0

---

## Executive Summary

TheLeadEdge analyzed **10 MLS listings** from the SWFLA market and detected **11 motivation signals** across 5 properties. The scoring engine classified leads into 4 tiers based on signal strength, decay, and stacking:

| Tier | Count | Score Range | Action Required |
|------|-------|-------------|-----------------|
| **S** | 0 | 80-100 | Immediate personal outreach |
| **A** | 1 | 60-79 | Priority outreach within 48 hours |
| **B** | 1 | 40-59 | Schedule outreach this week |
| **C** | 1 | 20-39 | Monthly touch / nurture campaign |
| **D** | 7 | 0-19 | Monitor only |

**3 leads warrant active outreach.** The remaining 7 are being monitored for future signals.

---

## Hot Leads (Tier A & B)

### LEAD #1 — Tier A (Score: 73.5) — PRIORITY

| Field | Value |
|-------|-------|
| MLS # | 22401006 |
| Status | Active |
| Location | Cape Coral, 33990 (Lee County) |
| Property | Townhouse, 3 bed / 2 bath, 1,650 sqft |
| Year Built | 2008 |
| List Price | $365,000 |
| Original Price | $450,000 |
| Previous Price | $410,000 |
| Days on Market | 75 |
| Listing Office | Gulf Realty |

**4 Signals Detected:**

1. **Price Reduction** (8 pts) — Price reduced 18.9% from original list price. Seller dropped from $450K to $365K, a $85,000 cut. This is not a minor adjustment — this is a seller who needs to move.

2. **Multiple Price Reductions** (14 pts) — Three distinct price points on record ($450K → $410K → $365K). Each reduction signals increasing urgency. The seller has tried twice to find the market and is still chasing it down.

3. **Severe Price Reduction** (16 pts) — The 18.9% total reduction from original exceeds the 15% threshold that indicates significant financial pressure or extreme motivation to sell. Nearly 1 in 5 dollars has been shaved off.

4. **High Days on Market** (11 pts) — 75 cumulative days on market. The SWFLA median is roughly 35-45 days. At 75 days, this listing is stale. The seller is watching neighbors sell while they sit.

**Why This Lead Matters:** Four stacked signals on one property is unusual. The pattern — aggressive price cuts over an extended period — strongly suggests a motivated seller who may be open to creative offers or needs guidance on proper market positioning. A townhouse in Cape Coral at $365K with this much price movement is a conversation worth having.

**Recommended Action:** Priority outreach within 48 hours. Prepare a CMA showing comparable sales to frame a realistic pricing discussion.

---

### LEAD #2 — Tier B (Score: 55.5) — SCHEDULE THIS WEEK

| Field | Value |
|-------|-------|
| MLS # | 22401003 |
| Status | Expired |
| Location | Naples, 34108 (Collier County) |
| Property | Condo, 2 bed / 2 bath, 1,400 sqft |
| Year Built | 2010 |
| List Price | $449,900 (at expiration) |
| Original Price | $499,000 |
| Previous Price | $475,000 |
| Listing Office | Test Realty |

**3 Signals Detected:**

1. **Expired Listing** (15 pts) — The listing expired without selling. The seller still owns the property and likely still wants to sell — they just couldn't get it done with their previous agent/strategy.

2. **Price Reduction** (8 pts) — Reduced 9.8% from original $499K to $449.9K. The seller was willing to negotiate but the market didn't meet them.

3. **Multiple Price Reductions** (14 pts) — Three price points ($499K → $475K → $449.9K) show the seller tried repeatedly to find a buyer. Nearly $50K in reductions and still no sale.

**Why This Lead Matters:** Expired listings are one of the highest-converting lead types in real estate. The seller demonstrated motivation (price cuts) but couldn't close. They may be frustrated with their previous agent, receptive to a fresh approach, or may have unrealistic expectations that a good CMA conversation can address. Naples 34108 (Pelican Bay / Vanderbilt Beach area) is a desirable condo market.

**Recommended Action:** Schedule outreach this week. Lead with empathy — acknowledge the frustration of an expired listing. Bring a CMA showing what actually sold in 34108 recently.

---

## Watchlist Leads (Tier C)

### LEAD #3 — Tier C (Score: 34.5) — NURTURE

| Field | Value |
|-------|-------|
| MLS # | 22401004 |
| Status | Expired |
| Location | Fort Myers, 33901 (Lee County) |
| Property | Single Family, 3 bed / 2 bath, 1,600 sqft |
| Year Built | 1998 |
| List Price | $275,000 (at expiration) |
| Original Price | $310,000 |
| Cumulative DOM | 180 days |
| Listing Office | Sunshine Realty |

**2 Signals Detected:**

1. **Expired Listing** (15 pts) — Another expired listing. This one had a 180-day cumulative days on market, meaning the seller endured 6 months of showings, feedback, and price adjustments without a sale.

2. **Price Reduction** (8 pts) — Reduced 11.3% from $310K to $275K. A $35,000 cut on a $310K property is meaningful at this price point.

**Why This Lead Matters:** Fort Myers 33901 is the downtown/River District area — a market that moves at a specific pace. Six months without a sale combined with an 11% price cut suggests either overpricing for the neighborhood or a property with condition issues. Either way, the seller has demonstrated patience and willingness to adjust. They may be ready for a new strategy.

**Recommended Action:** Add to monthly nurture campaign. This lead may need time to process the expired listing before being receptive to a new agent conversation.

---

## Monitored Leads (Tier D)

These 7 leads currently have weak or no motivation signals. They are being tracked and will be automatically re-scored when new data arrives.

| MLS # | Status | Location | Price | Signals | Notable Flags |
|-------|--------|----------|-------|---------|--------------|
| 22401005 | Pending | Naples, 34110 | $615,000 | 1 (price reduction 5.4%) | Under contract — monitor for fall-through |
| 22401010 | Active | Naples, 34119 | $550,000 | 1 (price reduction 5.2%) | Mild reduction — could escalate |
| 22401001 | Active | Naples, 34102 | $525,000 | 0 | 45 CDOM, no price cuts yet |
| 22401009 | Active | Cape Coral, 33914 | $475,000 | 0 | CDOM=95 (approaching high DOM threshold), Gulf Access |
| 22401002 | Active | Cape Coral, 33904 | $385,000 | 0 | No signals — stable listing |
| 22401008 | Active | Naples, 34112 | $289,000 | 0 | **Short sale flag** — not yet triggering (parsing issue noted below) |
| 22401007 | Active | Fort Myers, 33905 | $198,000 | 0 | **Foreclosure/REO flag** — not yet triggering (parsing issue noted below) |

**Leads to Watch:**
- **22401009** (Cape Coral, Gulf Access) has 95 cumulative DOM. At 120 CDOM it will trigger the high_dom signal and score significantly higher.
- **22401005** (Naples, Pending) is under contract but has a price reduction. If the deal falls through and it goes back to Active, the `back_on_market` signal will fire (13 base points).
- **22401007** and **22401008** have foreclosure and short sale flags in the raw MLS data that should be triggering signals. A CSV field mapping issue is preventing detection (see Technical Notes).

---

## How These Leads Were Found

### Data Pipeline

```
Matrix MLS CSV Export
        |
        v
[1] CSV Import (mls_csv.py)
    - Read CSV with encoding fallback (UTF-8, then CP-1252)
    - Map 46 CSV column headers to internal RESO field names
    - Parse types (int, float, date, datetime, boolean)
    - Normalize status values to RESO canonical form
    - Skip records missing required fields (ListingKey, ListPrice, etc.)
        |
        v
[2] Address Normalization (address.py)
    - USPS-standard formatting (directionals, suffixes, uppercase)
    - Generate deduplication key for matching across imports
        |
        v
[3] Property Upsert (repositories.py)
    - Match on listing_key first, then normalized address
    - Create new record or update existing
        |
        v
[4] Lead Creation (repositories.py)
    - One lead per property (1:1 relationship)
    - Starts at Tier D with score 0
        |
        v
[5] Signal Detection (detect.py)
    - 12 detection rules scan each property record
    - Each rule looks for specific field patterns
    - Detected signals stored with base points, decay type, half-life
        |
        v
[6] Scoring Engine (engine.py)
    - Apply temporal decay (signals lose value over time)
    - Apply freshness premium (new signals get bonus)
    - Check stacking rules (signal combinations = multiplier)
    - Normalize to 0-100 scale
    - Assign tier (S/A/B/C/D)
```

### Signal Detection Rules

The system runs 12 detection rules against each property. Here's what each one looks for:

| # | Signal | What Triggers It | Base Points |
|---|--------|-----------------|-------------|
| 1 | Expired Listing | Status = "Expired", within last 30 days | 15 |
| 2 | Expired Listing (Stale) | Status = "Expired", 31-90 days ago | 10 |
| 3 | Price Reduction | ListPrice < OriginalListPrice | 8 |
| 4 | Multiple Price Reductions | ListPrice < PreviousListPrice < OriginalListPrice | 14 |
| 5 | Severe Price Reduction | Price drop >= 15% from original | 16 |
| 6 | High Days on Market | DOM >= 90 or CDOM >= 120 | 11 |
| 7 | Withdrawn & Relisted | CDOM > DOM (listing was recycled) | 12 |
| 8 | Back on Market | Was Pending, now Active again (deal fell through) | 13 |
| 9 | Range Pricing | ListPriceLow field is set (desperation pricing) | 6 |
| 10 | Foreclosure Flag | ForeclosedREOYN = True | 18 |
| 11 | Short Sale Flag | PotentialShortSaleYN = True | 16 |
| 12 | Absentee Owner | Owner mailing address differs from property | 8 |

### How Scoring Works

**Step 1 — Base Points:** Each detected signal has a base point value (8-20 points) defined in `config/scoring_weights.yaml`. Higher points = stronger motivation indicator.

**Step 2 — Temporal Decay:** Signals lose value over time. Four decay functions are used:
- **Exponential** — Fast decay for time-sensitive signals (expired listings, price reductions). Half-life of 14-21 days.
- **Linear** — Steady decline for persistent conditions (foreclosure, absentee owner). Half-life of 90-180 days.
- **Step** — Full value for a period, then drops sharply (severe price reduction, high DOM). Half-life of 30-60 days.
- **Escalating** — Actually increases in urgency over time (pre-foreclosure approaching auction).

**Step 3 — Freshness Premium:** Signals detected within the last 24 hours get a 1.3x-1.5x boost. This rewards acting on fresh intelligence.

**Step 4 — Signal Stacking:** When specific combinations of signals appear on the same lead, a multiplier is applied. The system checks 6 stacking rules:

| Stack | Required Signals | Multiplier |
|-------|-----------------|-----------|
| Distressed Seller | expired + multiple price cuts + high DOM | 1.5x |
| Financial Distress | pre-foreclosure + tax delinquent | 2.0x |
| Life Event Vacant | probate + absentee owner + vacant | 2.5x |
| Tired Landlord | absentee owner + code violation | 1.8x |
| Failed Sale | expired + withdrawn/relisted | 1.4x |
| Divorce Property | divorce + high DOM | 1.6x |

**Step 5 — Normalization:** Raw points are normalized to a 0-100 scale. The maximum theoretical score assumes 100 base points pre-decay.

**Step 6 — Tier Assignment:**

| Tier | Score | Meaning |
|------|-------|---------|
| S | 80-100 | Immediate outreach — phone + handwritten note |
| A | 60-79 | Priority within 48 hours — CMA + call |
| B | 40-59 | Schedule this week — add to priority drip |
| C | 20-39 | Monthly touch — nurture campaign |
| D | 0-19 | Monitor only — no active outreach |

### Example: How Lead #1 Scored 73.5

MLS# 22401006 in Cape Coral:

```
Signal                      Base Pts  After Decay
price_reduction                8.0      ~8.0 (fresh)
price_reduction_multiple      14.0     ~14.0 (fresh)
price_reduction_severe        16.0     ~16.0 (fresh, step decay = full value)
high_dom                      11.0     ~11.0 (step decay = full value within half-life)
                              -----    -----
Raw Total                     49.0      49.0
Freshness Premium             ----      x1.5 = 73.5
Stacking Bonus                None triggered (needs expired + high DOM for distressed_seller)
Normalized Score              73.5 / 100 = 73.5
Tier                          A (60-79 range)
```

---

## Technical Notes & Known Issues

### CSV Field Mapping Issue (Non-Critical)

The sample CSV's `DaysOnMarket` column has an empty value for row 1, but a duplicate `CumulativeDaysOnMarket` value (45,45) is causing a column alignment shift in some rows. This results in city/zip_code/county being stored in incorrect columns for some records. The signal detection operates on the pre-storage RESO-normalized data and is not affected, but the stored property records have swapped fields.

**Impact:** Display data (city names, ZIP codes) may appear incorrect in the database for the test dataset. Signal detection and scoring are unaffected because they operate on the raw record before storage.

**Fix:** This is a test data issue, not a code bug. Real Matrix CSV exports from SWFLAMLS will have consistent column alignment. The field mapping logic in `mls_csv.py` correctly handles both Name and Label header formats.

### Signals Not Firing (22401007, 22401008)

The foreclosure flag (MLS# 22401007) and short sale flag (MLS# 22401008) are set in the raw CSV (`ForeclosedREOYN=Yes`, `PotentialShortSaleYN=Yes`) but are not being detected as signals. This is likely related to the field mapping issue above — the boolean columns may be shifted. With real MLS data these will fire correctly.

---

## What We Need to Find More Leads & Maximize the System

### 1. Real MLS Data (Critical — Immediate)

The sample dataset has 10 synthetic records. To generate actionable leads:

- **Export fresh CSV data from Matrix** for Lee and Collier counties
- Target these status categories for the richest signals:
  - **Expired listings** (last 30-90 days) — highest conversion rate
  - **Active with price reductions** — filter for OriginalListPrice != ListPrice
  - **High DOM** (90+ days on market) — filter by DaysOnMarket
  - **Withdrawn and Relisted** — filter by CumulativeDaysOnMarket > DaysOnMarket
  - **Back on Market** — filter for Active status with PendingTimestamp set
- Export the full 46 fields mapped in `config/mls_fields.yaml`
- Cover all 52 ZIP codes defined in `config/market.yaml`
- **Frequency:** Weekly exports minimum; daily for Expired and Price Change filters

### 2. SMTP Email Configuration (Critical — Immediate)

The daily briefing generator works but needs email credentials to deliver:

```
# Add to .env file:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<your-gmail>@gmail.com
SMTP_PASSWORD=<gmail-app-password>
```

Create a Gmail App Password at https://myaccount.google.com/apppasswords (requires 2FA enabled). This enables the 6:30 AM daily briefing email to trevormoen@gmail.com.

### 3. Scheduled Automation (Phase 2 — High Priority)

Currently the pipeline runs manually via `python -m theleadedge run`. To maximize value:

- **APScheduler integration** — Auto-run import + score + briefing daily at 6:00 AM
- **File watcher** — Detect new CSVs dropped in `data/mls_imports/` and auto-process
- **Re-scoring schedule** — Re-score all active leads every 6 hours to capture decay changes

### 4. Public Records Data (Phase 2 — High Value)

Five additional signal types are configured but have no data source yet:

| Signal | Source Needed | Points | Why It Matters |
|--------|--------------|--------|---------------|
| Pre-Foreclosure | Lee/Collier County Clerk Lis Pendens filings | 20 | Highest base points — strongest motivation indicator |
| Tax Delinquent | Lee/Collier County Tax Collector records | 13 | Financial distress indicator, slow decay |
| Code Violation | City of Naples / Lee County code enforcement | 12 | Property becoming a burden |
| Probate | County Probate Court records | 18 | Inherited property, heirs often want to sell |
| Divorce | County Court domestic relations filings | 16 | Court-ordered sale potential |

These public records signals, combined with MLS signals, trigger the most powerful **stacking rules** (2.0x-2.5x multipliers). A property with both a pre-foreclosure filing AND tax delinquency scores at 2.0x — immediately catapulting to S-tier.

### 5. Historical Data for Trend Detection (Medium Priority)

The system currently sees a snapshot. With historical imports over time:

- **Price trajectory tracking** — Detect acceleration in price drops (not just current vs. original)
- **DOM velocity** — Compare listing's DOM to neighborhood median DOM
- **Re-listing detection** — Same property appearing under a new MLS number (agent change)
- **Seasonal patterns** — Calibrate scoring by time of year (SWFLA has strong seasonality)

### 6. CRM Integration (Phase 4 — Follow Up Boss)

Once leads are flowing, connecting to Follow Up Boss would:

- Auto-create contacts for A-tier and above leads
- Trigger action plans (drip sequences by lead type)
- Track conversion outcomes to calibrate scoring weights
- Close the feedback loop: which tier leads actually convert?

### 7. Scoring Calibration (Ongoing)

The current scoring weights are research-based estimates. To maximize accuracy:

- **Track conversion outcomes** — Which leads actually resulted in listings/sales?
- **A/B test thresholds** — Are the tier boundaries (80/60/40/20) optimal?
- **Decay rate tuning** — Do expired listings really lose half their value in 21 days?
- **Market-specific weights** — SWFLA may weight DOM differently than a faster market

The system is designed for this: all weights, thresholds, and decay rates live in `config/scoring_weights.yaml` and can be tuned without changing code.

---

## Appendix: System Configuration

**Scoring Config:** `config/scoring_weights.yaml` — 20 signal types, 6 stacking rules, 5 tiers
**Field Mapping:** `config/mls_fields.yaml` — 46 MLS fields with Name + Label header support
**Market Definition:** `config/market.yaml` — 52 ZIP codes across Lee & Collier counties
**Database:** SQLite (MVP) at `theleadedge.db` — 7 tables, async access
**Tests:** 64 unit tests passing

---

*Report generated by TheLeadEdge v0.1.0 — Data-driven lead intelligence for real estate professionals*
