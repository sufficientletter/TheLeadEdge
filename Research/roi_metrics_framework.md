# ROI Metrics, KPI Framework & Success Measurement

> **Project**: TheLeadEdge — Real Estate Lead Generation System
> **Created**: 2026-02-28
> **Purpose**: Comprehensive measurement framework to evaluate every lead source, optimize spend, and scale what works
> **Prerequisite Reading**: lead_scoring_models.md, competitive_analysis.md, MASTER_RESEARCH.md

---

## Table of Contents

1. [Core KPI Dashboard](#1-core-kpi-dashboard)
2. [Funnel Metrics](#2-funnel-metrics)
3. [Lead Quality Metrics](#3-lead-quality-metrics)
4. [Financial Metrics](#4-financial-metrics)
5. [Operational Metrics](#5-operational-metrics)
6. [Strategy-Specific Benchmarks](#6-strategy-specific-benchmarks)
7. [A/B Testing Framework](#7-ab-testing-framework)
8. [Reporting Templates](#8-reporting-templates)
9. [Feedback Loop Design](#9-feedback-loop-design)
10. [Goal Setting Framework](#10-goal-setting-framework)

---

## 1. Core KPI Dashboard

These are the metrics that should be visible on the primary dashboard every single day. They answer the question: **Is the system working, and where should I spend my next hour?**

### 1.1 Leads Generated Per Source

Track the volume of new leads entering the pipeline from each source on a rolling basis.

| Source | Daily Target | Weekly Target | Monthly Target |
|--------|-------------|---------------|----------------|
| Expired Listings | 2-5 | 10-25 | 40-100 |
| Price Reduction Stacking (3+) | 1-3 | 5-15 | 20-60 |
| Pre-Foreclosure / NOD | 0-2 | 3-10 | 12-40 |
| Probate / Inherited | 0-1 | 2-5 | 8-20 |
| FSBO Failures | 1-2 | 5-10 | 20-40 |
| Withdrawn / Relisted | 0-2 | 3-8 | 12-32 |
| Absentee + High DOM | 0-1 | 2-5 | 8-20 |
| Past Client Lifecycle | 0-1 | 1-3 | 4-12 |
| Referral Network | 0-1 | 1-3 | 4-12 |
| Digital Signals (Zillow, Nextdoor) | 0-2 | 3-8 | 12-32 |
| **Total Pipeline Intake** | **7-20** | **35-92** | **140-368** |

**Calculation**:
```
Leads Generated (Source X, Period) = COUNT(new leads WHERE source = X AND created_date IN period)
```

**Storage Schema**:
```sql
CREATE TABLE lead_sources (
    lead_id         INTEGER PRIMARY KEY,
    source_type     TEXT NOT NULL,       -- 'expired', 'preforeclosure', 'fsbo', etc.
    source_detail   TEXT,                -- 'expired_tier1', 'expired_tier2', etc.
    identified_date TIMESTAMP NOT NULL,
    first_contact   TIMESTAMP,
    property_id     INTEGER REFERENCES properties(id),
    initial_score   REAL,
    current_score   REAL,
    funnel_stage    TEXT DEFAULT 'raw',
    cost_allocated  REAL DEFAULT 0.0
);
```

### 1.2 Conversion Rate by Lead Source

The single most important metric. This tells you which sources produce closed deals, not just activity.

**Full Conversion Chain**:
```
Lead --> Contact --> Appointment --> Listing Agreement --> Active Listing --> Pending --> Closed
```

**Tracking Table**:

| Source | Lead-to-Contact | Contact-to-Appt | Appt-to-Listing | Listing-to-Close | **Lead-to-Close** |
|--------|----------------|-----------------|-----------------|-------------------|-------------------|
| Expired Listings | 30-45% | 25-35% | 30-40% | 85-92% | **2.0-5.8%** |
| Pre-Foreclosure | 10-20% | 15-25% | 20-30% | 75-85% | **0.2-1.3%** |
| Probate | 15-25% | 20-30% | 25-35% | 80-90% | **0.6-2.4%** |
| FSBO | 25-40% | 20-30% | 25-40% | 85-92% | **1.1-4.4%** |
| Withdrawn/Relisted | 25-35% | 20-30% | 30-40% | 85-92% | **1.3-3.9%** |
| Past Client | 60-80% | 50-65% | 60-75% | 90-95% | **16.2-37.1%** |
| Referral Network | 50-70% | 40-55% | 50-65% | 88-95% | **8.8-24.3%** |
| Direct Mail (general) | 0.5-2% | 15-25% | 20-30% | 80-90% | **0.01-0.14%** |
| Digital/Online | 2-5% | 10-20% | 15-25% | 80-88% | **0.02-0.22%** |

**Formula**:
```
Conversion Rate (Stage A --> Stage B) = COUNT(leads reaching Stage B) / COUNT(leads reaching Stage A) * 100

End-to-End Conversion = Lead-to-Contact * Contact-to-Appt * Appt-to-Listing * Listing-to-Close
```

**Key Insight**: Past clients and referrals have 10-50x the conversion rate of cold lead sources. However, cold lead sources (expired, FSBO) produce far higher volume. Both matter. The system should optimize the high-volume sources while protecting time for the high-conversion relationship sources.

### 1.3 Cost Per Lead (CPL) by Source

What does it cost to generate one lead from each source?

| Source | Monthly Cost Components | Typical Monthly Leads | **Cost Per Lead** |
|--------|------------------------|-----------------------|-------------------|
| Expired Listings (REDX) | $60 (REDX) + $50 (skip trace ~500 records) | 40-100 | **$1.10-$2.75** |
| Pre-Foreclosure | $25 (county records) + $30 (skip trace) | 12-40 | **$1.38-$4.58** |
| Probate | $15 (court monitoring) + $20 (skip trace) | 8-20 | **$1.75-$4.38** |
| FSBO | $40 (REDX FSBO add-on) + $30 (skip trace) | 20-40 | **$1.75-$3.50** |
| Direct Mail | $0.75-$2.00 per piece x 500 pieces | 3-10 (responses) | **$37.50-$333** |
| Past Client | $20 (CRM cost allocation) | 4-12 | **$1.67-$5.00** |
| Referral Network | $50 (lunches, gifts) | 4-12 | **$4.17-$12.50** |
| Digital/Online (paid) | $200-$500 (ad spend) | 15-50 | **$4.00-$33.33** |
| MLS Mining (automated) | $100 (API/tool costs) | 40-80 | **$1.25-$2.50** |

**Formula**:
```
CPL (Source X) = Total Cost (Source X, Period) / Total Leads Generated (Source X, Period)

Total Cost includes:
  - Subscription fees (prorated by source)
  - Skip tracing costs
  - Postage / mail costs
  - Ad spend
  - Time cost (optional: hours * hourly rate equivalent)
```

### 1.4 Cost Per Acquisition (CPA) by Source

The true cost to produce one closed deal from each source. This is where you see the real ROI story.

| Source | CPL | Lead-to-Close | Leads to Close 1 Deal | **CPA** |
|--------|-----|---------------|------------------------|---------|
| Expired Listings | $1.50 | 3.5% | ~29 | **$43** |
| Pre-Foreclosure | $3.00 | 0.5% | ~200 | **$600** |
| Probate | $3.00 | 1.2% | ~83 | **$250** |
| FSBO | $2.50 | 2.5% | ~40 | **$100** |
| Direct Mail | $100 | 0.05% | ~2,000 | **$200,000** * |
| Past Client | $3.00 | 25% | ~4 | **$12** |
| Referral | $8.00 | 15% | ~7 | **$56** |
| Digital/Online | $15.00 | 0.1% | ~1,000 | **$15,000** |

*Direct mail CPA appears extreme because the conversion rate from raw mail response to close is very low. Direct mail is a volume-and-brand play, not a per-lead ROI play. Its value includes brand recognition that fuels other channels.

**Formula**:
```
CPA (Source X) = Total Cost (Source X, Period) / Total Closed Deals (Source X, Period)

-- OR equivalently:
CPA (Source X) = CPL (Source X) / Lead-to-Close Rate (Source X)
```

### 1.5 Average Commission Per Closed Deal by Source

Different lead sources produce different types of deals with different commission potential.

| Source | Typical Property Price Range | Commission Rate | **Avg Commission** |
|--------|----------------------------|-----------------|---------------------|
| Expired Listings | Market average | 2.5-3% (listing side) | **$8,000-$15,000** |
| Pre-Foreclosure | Below market (distress) | 2.5-3% | **$5,000-$10,000** |
| Probate | At or below market | 2.5-3% | **$6,000-$12,000** |
| FSBO | Market average | 2.5-3% (may negotiate lower initially) | **$7,000-$13,000** |
| Past Client | Market average | 2.5-3% (loyal, less negotiation) | **$9,000-$16,000** |
| Referral | Often above average (professional network) | 2.5-3% minus referral fee (25%) | **$6,000-$12,000** |
| Investor / Absentee | Varies widely | 2.5-3% | **$5,000-$14,000** |

**Note**: These ranges assume a median home price of ~$350,000-$500,000. Adjust to your local market. Commission rates in the example reflect seller-side listing commission.

**Formula**:
```
Avg Commission (Source X) = SUM(commission_earned WHERE source = X) / COUNT(closed_deals WHERE source = X)
```

### 1.6 ROI Per Lead Source

The definitive metric: for every dollar spent on a lead source, how many dollars come back?

| Source | Monthly Cost | Monthly Deals (est.) | Avg Commission | Revenue | **ROI** |
|--------|-------------|---------------------|----------------|---------|---------|
| Expired Listings | $110 | 1.5 | $10,000 | $15,000 | **13,536%** |
| Pre-Foreclosure | $55 | 0.2 | $7,000 | $1,400 | **2,445%** |
| Probate | $35 | 0.15 | $9,000 | $1,350 | **3,757%** |
| FSBO | $70 | 0.8 | $10,000 | $8,000 | **11,329%** |
| Direct Mail | $500 | 0.1 | $10,000 | $1,000 | **100%** |
| Past Client | $20 | 0.5 | $12,000 | $6,000 | **29,900%** |
| Referral | $50 | 0.3 | $9,000 | $2,700 | **5,300%** |
| Digital/Online | $350 | 0.05 | $10,000 | $500 | **43%** |

**Formula**:
```
ROI (Source X) = ((Revenue - Cost) / Cost) * 100

-- Revenue = Closed Deals * Avg Commission
-- Cost = Total monthly spend allocated to that source
```

**Important**: ROI percentages can be misleading in isolation. A 29,900% ROI on past clients is real but capped by volume (you cannot manufacture more past clients). Expired listings have slightly lower ROI but are scalable. The best strategy is to maximize the high-ROI/low-volume sources first, then scale the high-ROI/high-volume sources.

### 1.7 Time from Lead Identification to First Contact

Speed is the strongest predictor of conversion for time-sensitive lead sources. This metric should be tracked to the hour.

| Source | Target Contact Time | Why This Matters |
|--------|-------------------|-------------------|
| Expired Listings | < 4 hours from expiration | First agent to call with a CMA wins 60%+ of the time |
| FSBO (new listing) | < 24 hours | Before they entrench in "I can do this myself" mindset |
| FSBO (30+ days, struggling) | < 48 hours of price reduction | Pain is fresh, receptivity is highest |
| Pre-Foreclosure | 3-7 days after NOD filing | Too early feels predatory; too late and they have 10 mailers |
| Probate | 30-60 days after filing | Respect grieving period; approach as a resource |
| Price Reduction (3+) | < 24 hours of third reduction | Pattern of desperation is now undeniable |
| Withdrawn/Relisted | < 4 hours of relisting | They just fired an agent and are actively shopping |
| Back on Market (fell through) | < 2 hours | Seller is frustrated, wants a quick pivot |

**Formula**:
```
Avg Contact Delay (Source X) = AVG(first_contact_date - identified_date) WHERE source = X

-- Track in hours, not days, for time-sensitive sources
```

**Dashboard Implementation**: Display as a real-time gauge. Green = within target. Yellow = 1-2x target. Red = 2x+ target. Alert if any lead in a time-sensitive source exceeds target contact time.

### 1.8 Response Rate by Outreach Method

Not all contact methods work equally for all lead types. Track response rate by the combination of source and outreach method.

| Outreach Method | Expired | FSBO | Pre-Foreclosure | Probate | Past Client |
|----------------|---------|------|-----------------|---------|-------------|
| **Phone Call** | 8-15% | 10-18% | 3-7% | 5-10% | 40-60% |
| **Voicemail + Callback** | 3-5% | 4-7% | 2-4% | 3-5% | 15-25% |
| **Direct Mail (letter)** | 1-3% | 0.5-2% | 1-3% | 2-5% | 5-10% |
| **Direct Mail (postcard)** | 0.5-1.5% | 0.3-1% | 0.5-2% | 1-3% | 3-7% |
| **Handwritten Note** | 3-6% | 2-5% | 2-4% | 4-8% | 10-20% |
| **Email** | 2-5% | 3-6% | 1-3% | 2-4% | 15-30% |
| **Door Knock** | 15-25% | 12-20% | 8-15% | N/A | 50-70% |
| **Text/SMS** | 5-10% | 6-12% | 3-6% | 3-6% | 25-40% |

**Formula**:
```
Response Rate = COUNT(responses) / COUNT(outreach_attempts) * 100

-- A "response" = any reply, positive or negative. Track separately:
-- Positive response (interested, wants appointment)
-- Neutral response (not now, call back later)
-- Negative response (not interested, do not contact)
-- No response
```

**Key Takeaway**: Phone calls and door knocks dominate for time-sensitive leads (expired, FSBO). Direct mail works best for volume-based strategies (absentee owners, long-term owners). Email and text are strong secondary touchpoints in a multi-touch sequence. The optimal approach for most high-priority leads is: Phone Call --> Voicemail --> Text --> Email --> Mail piece (within 7 days).

---

## 2. Funnel Metrics

### 2.1 Full Funnel Definition

Every lead in the TheLeadEdge system moves through a defined funnel. Each stage has clear entry criteria, exit criteria, and actions.

```
Stage 1: RAW LEAD
  Entry:  Property/owner identified by any source
  Exit:   Scored and assigned to outreach queue
  Action: Auto-score, enrich data, skip trace if needed

Stage 2: QUALIFIED LEAD
  Entry:  Score >= threshold (40+ = warm or above)
  Exit:   Added to active outreach sequence
  Action: Verify contact info, assign outreach method

Stage 3: CONTACT MADE
  Entry:  Two-way communication established (spoke to owner)
  Exit:   Owner expressed any level of interest or set appointment
  Action: Log conversation notes, update score, set follow-up

Stage 4: APPOINTMENT SET
  Entry:  In-person or virtual meeting scheduled
  Exit:   Meeting completed, listing presentation delivered
  Action: Prepare CMA, customize listing presentation

Stage 5: LISTING AGREEMENT SIGNED
  Entry:  Seller signed listing agreement
  Exit:   Property prepared and entered into MLS
  Action: Professional photos, staging consultation, pricing strategy

Stage 6: ACTIVE LISTING
  Entry:  Property live in MLS
  Exit:   Offer accepted or listing expires/withdrawn
  Action: Showings, open houses, marketing, price adjustments

Stage 7: PENDING / UNDER CONTRACT
  Entry:  Accepted offer, contract signed
  Exit:   Closing completed or contract falls through
  Action: Manage inspections, appraisal, buyer coordination

Stage 8: CLOSED
  Entry:  Transaction recorded, commission disbursed
  Exit:   Client enters past-client nurture pipeline
  Action: Collect testimonial, add to referral request sequence
```

### 2.2 Drop-Off Rates at Each Stage

Where leads die in the funnel -- and what it tells you.

| Transition | Expected Drop-Off | Red Flag Threshold | Common Causes |
|-----------|-------------------|--------------------|----|
| Raw --> Qualified | 40-60% | >70% | Poor source quality, scoring too aggressive |
| Qualified --> Contact Made | 50-70% | >80% | Bad contact info, slow outreach, wrong channel |
| Contact --> Appointment | 60-75% | >85% | Weak pitch, poor timing, not addressing motivation |
| Appointment --> Listing | 40-60% | >70% | Commission objections, pricing disagreement, competing agents |
| Listing --> Active | 5-10% | >15% | Seller changed mind, unrealistic expectations |
| Active --> Pending | 15-30% | >40% | Overpriced, poor condition, weak marketing |
| Pending --> Closed | 5-15% | >20% | Financing fell through, inspection issues, appraisal gap |

**Formula**:
```
Drop-Off Rate (Stage A --> Stage B) = 1 - Conversion Rate (Stage A --> Stage B)

-- Example: If Contact --> Appointment rate is 30%, drop-off is 70%
```

### 2.3 Average Time in Each Stage

How long leads spend in each stage tells you about pipeline health and bottlenecks.

| Stage | Healthy Range | Warning Threshold | Critical Threshold |
|-------|--------------|-------------------|--------------------|
| Raw --> Qualified | < 1 hour (automated) | > 4 hours | > 24 hours |
| Qualified --> Contact Made | 4-48 hours | > 72 hours | > 7 days |
| Contact --> Appointment | 3-14 days | > 21 days | > 30 days |
| Appointment --> Listing Signed | 1-7 days | > 14 days | > 30 days |
| Listing Signed --> Active | 3-10 days | > 14 days | > 21 days |
| Active --> Pending | 14-60 days | > 90 days | > 120 days |
| Pending --> Closed | 21-45 days | > 60 days | > 75 days |
| **Total: Lead to Close** | **60-150 days** | **> 180 days** | **> 270 days** |

**Pipeline Velocity Formula**:
```
Pipeline Velocity = (Number of Leads * Win Rate * Avg Deal Value) / Avg Days in Pipeline

-- Example:
-- 50 active leads * 5% win rate * $10,000 avg commission / 120 avg days
-- = $208/day pipeline velocity
```

### 2.4 Industry Benchmark Conversion Rates

How the TheLeadEdge system should compare against published industry averages.

| Metric | Industry Average | Good | Excellent | TheLeadEdge Target |
|--------|-----------------|------|-----------|-------------------|
| Lead-to-Contact (all sources) | 20-30% | 35-45% | 50%+ | 40%+ |
| Contact-to-Appointment | 15-25% | 25-35% | 40%+ | 30%+ |
| Appointment-to-Listing | 25-35% | 35-50% | 55%+ | 40%+ |
| Listing-to-Close | 80-88% | 88-93% | 94%+ | 90%+ |
| Overall Lead-to-Close | 0.5-2% | 2-5% | 5%+ | 3%+ (blended) |
| Expired Lead-to-Listing | 3-5% | 5-8% | 10%+ | 7%+ |
| FSBO Lead-to-Listing | 2-4% | 4-7% | 8%+ | 5%+ |
| Referral Lead-to-Close | 10-15% | 15-25% | 30%+ | 20%+ |

---

## 3. Lead Quality Metrics

These metrics tell you whether the scoring model is actually predictive. Without these, you are flying blind on lead quality.

### 3.1 Score Accuracy (Calibration Analysis)

The fundamental question: **Do high-scored leads actually convert at higher rates than low-scored leads?**

**Measurement Method**:

For each score tier (S/A/B/C/D defined in lead_scoring_models.md), measure the actual conversion rate and compare it to the predicted/expected rate.

| Score Tier | Score Range | Expected Conversion | Actual Conversion (track) | Accuracy Ratio |
|-----------|-------------|--------------------|----|---|
| S (Hot) | 80-100 | 15-25% to appointment | ___ | Actual / Expected |
| A (High) | 60-79 | 8-15% to appointment | ___ | Actual / Expected |
| B (Warm) | 40-59 | 3-8% to appointment | ___ | Actual / Expected |
| C (Nurture) | 20-39 | 1-3% to appointment | ___ | Actual / Expected |
| D (Watch) | 0-19 | 0-1% to appointment | ___ | Actual / Expected |

**Accuracy Ratio Interpretation**:
- **0.8 - 1.2**: Well calibrated -- model is working as intended
- **< 0.8**: Model is overconfident (scoring too high for actual performance)
- **> 1.2**: Model is underconfident (scoring too low; missing opportunities)
- **< 0.5 or > 2.0**: Model needs retraining; weights are significantly off

**SQL Query**:
```sql
SELECT
    CASE
        WHEN initial_score >= 80 THEN 'S'
        WHEN initial_score >= 60 THEN 'A'
        WHEN initial_score >= 40 THEN 'B'
        WHEN initial_score >= 20 THEN 'C'
        ELSE 'D'
    END AS tier,
    COUNT(*) AS total_leads,
    SUM(CASE WHEN funnel_stage IN ('appointment','listing','pending','closed') THEN 1 ELSE 0 END) AS converted,
    ROUND(100.0 * SUM(CASE WHEN funnel_stage IN ('appointment','listing','pending','closed') THEN 1 ELSE 0 END) / COUNT(*), 2) AS conversion_pct
FROM lead_sources
WHERE identified_date >= DATE('now', '-90 days')
GROUP BY tier
ORDER BY tier;
```

### 3.2 Signal Correlation Analysis

Which individual signals actually correlate with conversion? This drives weight adjustments in the scoring model.

**Method**: For each signal in the scoring model, calculate the point-biserial correlation between signal presence (0/1) and conversion (0/1).

| Signal | Present in N Leads | Converted | Not Converted | Correlation (r) | P-value | Action |
|--------|-------------------|-----------|---------------|-----------------|---------|--------|
| Expired listing | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |
| Pre-foreclosure | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |
| 3+ price reductions | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |
| Absentee owner | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |
| Vacant property | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |
| Tax delinquent | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |
| Divorce filing | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |
| Probate filing | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |
| High DOM (90+) | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |
| Agent change/withdrawn | ___ | ___ | ___ | ___ | ___ | Keep / Adjust / Remove |

**Python Calculation**:
```python
from scipy.stats import pointbiserialr
import pandas as pd

def signal_correlation(df, signal_col, outcome_col='converted'):
    """Calculate correlation between a signal and conversion outcome."""
    r, p_value = pointbiserialr(df[signal_col], df[outcome_col])
    return {
        'signal': signal_col,
        'correlation': round(r, 4),
        'p_value': round(p_value, 4),
        'significant': p_value < 0.05,
        'action': 'increase_weight' if r > 0.15 else ('keep' if r > 0.05 else 'review')
    }

# Run for all signals
signals = ['expired', 'preforeclosure', 'price_reductions_3plus', 'absentee',
           'vacant', 'tax_delinquent', 'divorce', 'probate', 'high_dom', 'agent_change']

results = [signal_correlation(leads_df, sig) for sig in signals]
correlation_report = pd.DataFrame(results).sort_values('correlation', ascending=False)
```

### 3.3 False Positive Rate

Leads that scored high but never converted. Excessive false positives waste the agent's time and erode confidence in the system.

**Definition**: A false positive is a lead scored in Tier S or A (score >= 60) that reached the end of its lifecycle (90+ days in pipeline) without advancing past "Contact Made" stage.

**Formula**:
```
False Positive Rate = COUNT(leads WHERE score >= 60 AND lifecycle_ended AND stage <= 'contact_made')
                    / COUNT(leads WHERE score >= 60 AND lifecycle_ended) * 100

-- Target: < 60% (meaning 40%+ of high-scored leads advance meaningfully)
-- Warning: > 75%
-- Critical: > 85% (model is not predictive; needs overhaul)
```

**Tracking Over Time**:
| Month | Total S/A Leads | Converted (Appt+) | False Positives | FP Rate | Trend |
|-------|----------------|--------------------|----|---|---|
| Month 1 | ___ | ___ | ___ | ___% | Baseline |
| Month 2 | ___ | ___ | ___ | ___% | Up/Down |
| Month 3 | ___ | ___ | ___ | ___% | Up/Down |

### 3.4 False Negative Rate

Leads that scored low but actually converted. These are missed opportunities -- the system failed to recognize them as valuable.

**Definition**: A false negative is a lead scored in Tier C or D (score < 40) that eventually closed or reached listing agreement stage.

**Formula**:
```
False Negative Rate = COUNT(leads WHERE score < 40 AND stage IN ('listing','pending','closed'))
                    / COUNT(leads WHERE stage IN ('listing','pending','closed')) * 100

-- Target: < 15% (meaning 85%+ of deals came from leads the system rated warm or above)
-- Warning: > 25%
-- Critical: > 35% (model is missing too many real opportunities)
```

**When False Negatives Are High**:
- Review what signals were present in the low-scored leads that actually converted
- Those signals may need higher weights or may be entirely missing from the model
- Consider adding new signal types to capture the pattern
- Run the signal correlation analysis (Section 3.2) to identify underweighted signals

### 3.5 Score Calibration Over Time

Track how the model's predictive accuracy changes month over month. The goal is continuous improvement.

**Calibration Plot Data**:
```
For each score decile (0-9, 10-19, 20-29, ... 90-100):
  - Predicted conversion rate (based on model assumptions)
  - Actual conversion rate (based on observed outcomes)
  - Number of leads in the decile

Perfect calibration = predicted rate matches actual rate at every decile
```

**Brier Score** (overall calibration quality):
```
Brier Score = (1/N) * SUM( (predicted_probability - actual_outcome)^2 )

-- Range: 0 (perfect) to 1 (worst)
-- Target: < 0.15
-- Good: < 0.10
-- Excellent: < 0.05
```

**Python Implementation**:
```python
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss

def model_calibration(y_true, y_pred_proba, n_bins=10):
    """Assess model calibration quality."""
    brier = brier_score_loss(y_true, y_pred_proba)
    fraction_pos, mean_predicted = calibration_curve(y_true, y_pred_proba, n_bins=n_bins)

    return {
        'brier_score': round(brier, 4),
        'calibration_quality': 'excellent' if brier < 0.05 else ('good' if brier < 0.10 else ('fair' if brier < 0.15 else 'poor')),
        'fraction_positive_by_bin': fraction_pos.tolist(),
        'mean_predicted_by_bin': mean_predicted.tolist()
    }
```

---

## 4. Financial Metrics

These metrics connect lead generation activity to actual revenue and profitability. They answer: **Is this a profitable business system?**

### 4.1 Monthly Lead Gen Spend Breakdown

Track every dollar spent on lead generation, categorized by type.

| Category | Item | Monthly Cost | Annual Cost | Notes |
|----------|------|-------------|-------------|-------|
| **Subscriptions** | | | | |
| | Follow Up Boss CRM | $69 | $828 | Lead management |
| | REDX (Expired + FSBO) | $100 | $1,200 | Lead feeds |
| | BatchLeads (Skip Trace) | $99 | $1,188 | Contact info |
| | ATTOM API | $250 | $3,000 | Property data enrichment |
| | VPS Hosting | $20 | $240 | Run daily scripts |
| **Variable Costs** | | | | |
| | Additional Skip Traces | $30-80 | $360-960 | Overflow beyond plan |
| | Direct Mail (500 pcs/mo) | $375-1,000 | $4,500-12,000 | $0.75-2.00 per piece |
| | Handwritten Notes (50/mo) | $150 | $1,800 | $3.00 per note |
| | CMA Printing/Delivery | $25 | $300 | Professional presentation packages |
| **Advertising** | | | | |
| | Google/Facebook Ads | $0-500 | $0-6,000 | Optional |
| | Farming Mailers | $200-400 | $2,400-4,800 | Geographic farming |
| **Relationship** | | | | |
| | Referral Gifts/Lunches | $50-100 | $600-1,200 | Referral network cultivation |
| | Client Events | $50-100 | $600-1,200 | Past client engagement |
| **TOTAL** | | **$1,088-$2,743** | **$13,056-$32,916** | |

### 4.2 Revenue Attribution by Lead Source

For every closed deal, trace the revenue back to the originating lead source.

**Attribution Model**: First-touch attribution (credit goes to the source that originally identified the lead). If a lead came from multiple sources (e.g., identified via expired listing AND probate filing), credit the first signal detected.

```sql
SELECT
    ls.source_type,
    COUNT(DISTINCT t.transaction_id) AS closed_deals,
    SUM(t.commission_earned) AS total_revenue,
    ROUND(AVG(t.commission_earned), 2) AS avg_commission,
    ROUND(SUM(t.commission_earned) / NULLIF(SUM(ls.cost_allocated), 0), 2) AS revenue_per_dollar_spent
FROM transactions t
JOIN lead_sources ls ON t.lead_id = ls.lead_id
WHERE t.status = 'closed'
  AND t.close_date >= DATE('now', '-12 months')
GROUP BY ls.source_type
ORDER BY total_revenue DESC;
```

**Revenue Attribution Table** (fill monthly):

| Source | Closed Deals | Total Revenue | % of Revenue | Cost | **Net Profit** | **ROI** |
|--------|-------------|---------------|-------------|------|----------------|---------|
| Expired Listings | ___ | $___ | ___% | $___ | $___ | ___% |
| FSBO | ___ | $___ | ___% | $___ | $___ | ___% |
| Past Client | ___ | $___ | ___% | $___ | $___ | ___% |
| Referral | ___ | $___ | ___% | $___ | $___ | ___% |
| Pre-Foreclosure | ___ | $___ | ___% | $___ | $___ | ___% |
| Probate | ___ | $___ | ___% | $___ | $___ | ___% |
| Direct Mail | ___ | $___ | ___% | $___ | $___ | ___% |
| Digital/Online | ___ | $___ | ___% | $___ | $___ | ___% |
| Other | ___ | $___ | ___% | $___ | $___ | ___% |
| **TOTAL** | ___ | $___ | 100% | $___ | $___ | ___% |

### 4.3 Break-Even Analysis Per Lead Source

How many leads do you need to process from each source before the revenue covers the cost?

**Formula**:
```
Break-Even Leads = Fixed Monthly Cost (Source) / (Avg Commission * Lead-to-Close Rate)

-- Example: Expired Listings
-- Fixed Cost: $110/mo (REDX + skip trace allocation)
-- Avg Commission: $10,000
-- Lead-to-Close: 3.5%
-- Break-Even = $110 / ($10,000 * 0.035) = $110 / $350 = 0.31 leads
-- Meaning: Less than 1 closed deal per 3 months covers the cost

-- Example: Digital Ads
-- Fixed Cost: $500/mo
-- Avg Commission: $10,000
-- Lead-to-Close: 0.1%
-- Break-Even = $500 / ($10,000 * 0.001) = $500 / $10 = 50 closed-deal equivalents
-- Meaning: You need to generate 50,000 leads per month to break even (not viable as primary strategy)
```

**Break-Even Summary**:

| Source | Monthly Cost | Revenue Per Converted Lead | Monthly Break-Even Point | Months to First ROI |
|--------|-------------|---------------------------|--------------------------|---------------------|
| Expired Listings | $110 | $350 avg (10K * 3.5%) | 0.3 deals | < 1 month |
| FSBO | $70 | $250 avg (10K * 2.5%) | 0.3 deals | < 1 month |
| Pre-Foreclosure | $55 | $35 avg (7K * 0.5%) | 1.6 deals | 2-3 months |
| Probate | $35 | $108 avg (9K * 1.2%) | 0.3 deals | 1-2 months |
| Direct Mail | $500 | $5 avg (10K * 0.05%) | 100 deals | 12+ months |
| Past Client | $20 | $3,000 avg (12K * 25%) | 0.007 deals | Immediate |
| Digital/Online | $350 | $10 avg (10K * 0.1%) | 35 deals | 12+ months |

### 4.4 Lifetime Value of a Client (LTV)

One closed deal is not the end of the revenue story. Satisfied clients generate repeat business and referrals.

**Components of LTV**:

| Component | Average Value | Probability | Expected Value |
|-----------|--------------|-------------|----------------|
| Initial transaction commission | $10,000 | 100% | $10,000 |
| Repeat business (next sale in 7-10 yrs) | $12,000 | 15-25% (retention rate) | $1,800-$3,000 |
| Buyer-side referrals (friends/family buying) | $8,000 | 10-20% send a referral | $800-$1,600 |
| Seller-side referrals (friends/family selling) | $10,000 | 10-15% send a referral | $1,000-$1,500 |
| Cross-side transaction (listed home, they also buy) | $8,000 | 30-40% | $2,400-$3,200 |

**LTV Formula**:
```
LTV = Initial Commission
    + (Repeat Business Probability * Future Commission * Discount Factor)
    + (Referral Probability * Referral Commission * Avg Referrals per Client)
    + (Cross-Side Probability * Cross-Side Commission)

Simplified Estimate:
LTV = Initial Commission * LTV Multiplier

-- Conservative LTV Multiplier: 1.5x
-- Moderate LTV Multiplier: 2.0x
-- Aggressive (strong relationship agent): 2.5-3.0x

-- If Avg Commission = $10,000
-- Conservative LTV = $15,000
-- Moderate LTV = $20,000
-- Strong Relationship LTV = $25,000-$30,000
```

**This changes the CPA calculation dramatically**. If LTV is $20,000 instead of $10,000, you can afford 2x the CPA and still be profitable. This justifies higher investment in direct mail and digital leads that have long payback periods.

### 4.5 Opportunity Cost Analysis

Time is the most constrained resource. Every hour spent on a low-converting source is an hour NOT spent on a high-converting source.

**Time-Adjusted ROI**:
```
Time-Adjusted ROI = Revenue per Hour Spent (Source X)

Revenue per Hour = (Leads/Hour * Lead-to-Close Rate * Avg Commission)
```

| Source | Hours/Week | Revenue/Month (est.) | Revenue/Hour | Rank |
|--------|-----------|---------------------|-------------|------|
| Past Client Nurture | 1 | $6,000 | $1,500 | 1 |
| Referral Network | 2 | $2,700 | $338 | 2 |
| Expired Listings | 3 | $15,000 | $1,250 | 3 |
| FSBO Outreach | 2 | $8,000 | $1,000 | 4 |
| Withdrawn/Relisted | 1 | $3,000 | $750 | 5 |
| Pre-Foreclosure | 2 | $1,400 | $175 | 6 |
| Probate | 1 | $1,350 | $338 | 7 |
| Direct Mail Mgmt | 1 | $1,000 | $250 | 8 |
| Digital Ad Mgmt | 2 | $500 | $63 | 9 |

**Decision Rule**: If Revenue/Hour for Source X is less than 25% of Revenue/Hour for the highest source, reallocate time from Source X to a higher-performing source.

---

## 5. Operational Metrics

These metrics measure the health of the system itself -- not the leads, but the machine that processes them.

### 5.1 Daily Workflow Time

Track how long each daily task takes to identify efficiency gains.

| Task | Manual Time (no system) | With TheLeadEdge (Phase 1) | With Automation (Phase 4) | Time Saved |
|------|-------------------------|---------------------------|---------------------------|------------|
| Check MLS expireds | 15-20 min | 5 min | 0 min (auto) | 15-20 min |
| Check price reductions | 10-15 min | 3 min | 0 min (auto) | 10-15 min |
| Check public records | 20-30 min | 5 min | 1 min (review alerts) | 19-29 min |
| Score and prioritize leads | 15-20 min | 5 min | 0 min (auto-scored) | 15-20 min |
| Prepare outreach list | 10-15 min | 3 min | 0 min (auto-generated) | 10-15 min |
| Log activities/update CRM | 15-20 min | 5 min | 2 min (auto-logged) | 13-18 min |
| Review pipeline/follow-ups | 10-15 min | 5 min | 3 min (dashboard) | 7-12 min |
| **Daily Total** | **95-135 min** | **31 min** | **6 min** | **89-129 min** |

**Formula**:
```
Automation Time Savings = Manual Time - Automated Time
Efficiency Gain % = (Manual Time - Automated Time) / Manual Time * 100
Daily ROI of System = Time Saved * (Hourly Revenue Equivalent)
```

### 5.2 Data Freshness

How old are the leads when they reach the agent? Stale leads are wasted leads.

| Data Source | Data Update Frequency | Detection Delay | Total Freshness | Target |
|-------------|----------------------|-----------------|-----------------|--------|
| MLS Expireds | Real-time (RESO API) | < 1 hour (scheduled) | < 1 hour | < 4 hours |
| MLS Expireds | Daily CSV export | 12-24 hours | 12-24 hours | < 24 hours |
| Price Reductions | Real-time (RESO API) | < 1 hour | < 1 hour | < 12 hours |
| Pre-Foreclosure (NOD) | Daily (county postings) | 1-3 days (batch pull) | 2-4 days | < 7 days |
| Probate Filings | Weekly (court dockets) | 1-7 days | 2-14 days | < 14 days |
| Tax Delinquency | Monthly (county lists) | 1-30 days | 2-60 days | < 30 days |
| Skip Trace Results | On-demand | Minutes | Minutes | < 1 hour |

**Freshness Score**:
```
Freshness Score = MAX(0, 1 - (hours_since_event / max_acceptable_hours))

-- 1.0 = perfectly fresh
-- 0.5 = half-life reached
-- 0.0 = stale (past acceptable window)
```

### 5.3 Pipeline Velocity

How fast are leads moving through the system?

**Formula**:
```
Pipeline Velocity ($) = (Active Leads * Avg Win Rate * Avg Deal Value) / Avg Sales Cycle Days

-- Example:
-- 80 active leads * 4% win rate * $10,000 avg commission / 120 day avg cycle
-- = $267/day = ~$8,000/month expected revenue from current pipeline
```

**Velocity by Stage**:

| Stage | Avg Leads in Stage | Avg Days in Stage | Velocity (leads/week) |
|-------|-------------------|-------------------|-----------------------|
| Raw | 50-100 | 1-2 | 25-50 |
| Qualified | 30-60 | 2-5 | 10-30 |
| Contact Made | 10-20 | 7-14 | 3-7 |
| Appointment Set | 3-8 | 3-7 | 1-3 |
| Listing Agreement | 1-3 | 5-10 | 0.5-1 |
| Active Listing | 3-8 | 30-60 | 0.5-1 |
| Pending | 2-5 | 30-45 | 0.5-1 |

**Bottleneck Detection**: If any stage has significantly more leads and longer dwell time than the stage above, that stage is a bottleneck. Common bottlenecks:
- **Contact Made (leads stuck here)**: Agent not following up quickly enough, or lead info is bad
- **Appointment Set (low volume)**: Agent's pitch or value proposition needs improvement
- **Active Listing (long dwell)**: Pricing strategy issue or market conditions

### 5.4 Outreach Compliance Rate

Track adherence to legal requirements and best practices.

| Compliance Metric | Target | Measurement Method |
|-------------------|--------|-------------------|
| DNC list scrubbing rate | 100% | All phone lists run through DNC registry before calling |
| Opt-out processing time | < 24 hours | Time from opt-out request to list removal |
| CAN-SPAM compliance | 100% | All emails have unsubscribe link, physical address, honest subject |
| TCPA compliance (text) | 100% | Consent documented before automated texting |
| Pre-foreclosure solicitation timing | 100% | Respect state-specific wait periods after NOD filing |
| Probate sensitivity window | 100% | Minimum 30-day wait after filing before outreach |
| Contact frequency limits | < 3 calls/week per lead | Prevent harassment complaints |
| Contact hour compliance | 100% | Calls only 8 AM - 9 PM recipient local time |

---

## 6. Strategy-Specific Benchmarks

Industry benchmark ranges for each lead generation strategy, with context on what "good" looks like.

### 6.1 Expired Listings

| Metric | Low | Average | Good | Excellent |
|--------|-----|---------|------|-----------|
| Contact rate (reach owner by phone) | 8% | 15% | 25% | 35%+ |
| Appointment rate (from contacts) | 15% | 25% | 35% | 45%+ |
| Listing rate (from appointments) | 25% | 35% | 45% | 60%+ |
| Close rate (from listings) | 80% | 87% | 92% | 95%+ |
| Same-day CMA delivery rate | 10% | 30% | 60% | 80%+ |
| Overall lead-to-listing | 0.3% | 1.3% | 4% | 8%+ |
| Avg time to re-list with you | 14-21 days | 7-14 days | 3-7 days | < 3 days |
| Recommended daily call volume | 20-30 | 30-50 | 50-75 | 75-100 |

**Key Success Factors**: Speed of first contact (within 4 hours of expiration), quality of CMA, and differentiation from the 5-10 other agents calling the same day.

### 6.2 FSBO Conversion

| Metric | Low | Average | Good | Excellent |
|--------|-----|---------|------|-----------|
| Initial contact rate | 15% | 25% | 35% | 50%+ |
| Time to convert (days on market before listing) | 90+ days | 60-90 | 30-60 | < 30 |
| Conversion rate (FSBO to listing agreement) | 2% | 5% | 8% | 12%+ |
| Commission negotiation success (full rate) | 30% | 50% | 65% | 80%+ |
| Avg discount from full commission | 0.75-1.0% | 0.5-0.75% | 0.25-0.5% | 0% |
| Multi-touch to conversion (avg contacts needed) | 7-10 | 5-7 | 3-5 | 1-3 |

**Key Success Factors**: Patience (most FSBOs convert after 30-60 days of frustration), value demonstration (market analysis, marketing plan), and non-pushy initial approach.

### 6.3 Pre-Foreclosure

| Metric | Low | Average | Good | Excellent |
|--------|-----|---------|------|-----------|
| Mail response rate | 0.3% | 1% | 2% | 3%+ |
| Phone contact rate | 2% | 5% | 8% | 12%+ |
| Door knock response rate | 10% | 18% | 25% | 35%+ |
| Appointment rate (from responses) | 10% | 20% | 30% | 40%+ |
| Listing rate (from appointments) | 15% | 25% | 35% | 50%+ |
| Overall lead-to-close | 0.02% | 0.1% | 0.5% | 1%+ |
| Avg timeline (NOD to close) | 6-12 months | 4-6 months | 3-4 months | 2-3 months |
| Ethical comfort score (agent self-assessment) | N/A | N/A | N/A | N/A |

**Ethical Measurement Considerations**: Track client satisfaction specifically for pre-foreclosure clients. Did they feel helped or exploited? Use a post-transaction survey. If satisfaction scores are consistently low, reconsider approach even if conversion metrics are fine.

**Important State Regulations**:
- Some states require a waiting period after NOD before agent contact (e.g., California: 5 business days)
- Some states restrict solicitation of homeowners in default entirely
- Always verify local regulations before launching pre-foreclosure campaigns

### 6.4 Probate

| Metric | Low | Average | Good | Excellent |
|--------|-----|---------|------|-----------|
| Mail response rate | 1% | 3% | 5% | 8%+ |
| Phone contact rate | 5% | 10% | 15% | 20%+ |
| Appointment rate (from contacts) | 15% | 25% | 35% | 50%+ |
| Listing rate (from appointments) | 20% | 35% | 45% | 60%+ |
| Overall lead-to-close | 0.1% | 0.5% | 1.5% | 3%+ |
| Avg timeline (filing to close) | 12-18 months | 8-12 months | 6-8 months | 4-6 months |
| Executor/heir satisfaction rate | Track | Track | > 85% | > 95% |

**Key Success Factors**: Timing (30-60 days after filing), empathetic approach, expertise in probate sales process, connections with probate attorneys for referrals.

### 6.5 Direct Mail Campaigns

| Metric | Low | Average | Good | Excellent |
|--------|-----|---------|------|-----------|
| Response rate (letter) | 0.5% | 1.5% | 3% | 5%+ |
| Response rate (postcard) | 0.3% | 1% | 2% | 3%+ |
| Response rate (handwritten note) | 2% | 4% | 7% | 10%+ |
| Cost per piece (letter) | $1.50+ | $1.00-1.50 | $0.75-1.00 | < $0.75 |
| Cost per piece (postcard) | $0.75+ | $0.50-0.75 | $0.35-0.50 | < $0.35 |
| Cost per piece (handwritten) | $4.00+ | $3.00-4.00 | $2.50-3.00 | < $2.50 |
| Cost per response | $100+ | $50-100 | $25-50 | < $25 |
| Touches before response (avg) | 5-7 | 4-5 | 3-4 | 1-3 |
| ROI (annualized, including repeat mailings) | < 100% | 100-300% | 300-500% | 500%+ |

**Critical Rule**: Direct mail requires consistency. A single mailing has negligible ROI. The standard recommendation is a minimum of 3-5 touches over 3-6 months before evaluating results. Track per-campaign cohorts, not individual mailings.

### 6.6 Cold Calling

| Metric | Low | Average | Good | Excellent |
|--------|-----|---------|------|-----------|
| Dial-to-connect rate (reach a person) | 5% | 10% | 15% | 20%+ |
| Connect-to-conversation rate | 30% | 50% | 65% | 80%+ |
| Conversation-to-appointment rate | 2% | 5% | 8% | 12%+ |
| Overall dial-to-appointment rate | 0.3% | 0.5% | 0.8% | 2%+ |
| Calls per hour | 15-20 | 20-30 | 30-40 | 40+ (with dialer) |
| Appointments per hour of calling | 0.05 | 0.1 | 0.25 | 0.5+ |
| Optimal calling windows | N/A | 10-11:30 AM, 4-5:30 PM (local) | Same | Same |
| Recommended weekly call sessions | 1-2 | 3-4 | 5 | 5+ |

### 6.7 Digital / Email Marketing

| Metric | Low | Average | Good | Excellent |
|--------|-----|---------|------|-----------|
| Email open rate | 12% | 22% | 30% | 40%+ |
| Email click-through rate | 1% | 3% | 5% | 8%+ |
| Email reply rate | 0.5% | 1.5% | 3% | 5%+ |
| Email unsubscribe rate | > 1% | 0.5-1% | 0.2-0.5% | < 0.2% |
| Landing page conversion rate | 1% | 3% | 5% | 8%+ |
| Cost per click (Google Ads) | $5+ | $2-5 | $1-2 | < $1 |
| Cost per click (Facebook/Meta) | $3+ | $1-3 | $0.50-1 | < $0.50 |
| Online lead-to-close rate | 0.02% | 0.05% | 0.1% | 0.5%+ |
| Avg nurture time (online lead to close) | 12+ months | 6-12 months | 3-6 months | < 3 months |

---

## 7. A/B Testing Framework

With limited lead volume, testing must be disciplined and focused on the variables that have the greatest potential impact.

### 7.1 What to Test (Priority Order)

**High Impact (Test First)**:
| Variable | What to Compare | Expected Impact |
|----------|----------------|-----------------|
| Outreach timing | Same-day vs. next-day contact for expireds | 30-50% improvement in response rate |
| Outreach channel | Phone-first vs. mail-first for pre-foreclosure | 100-300% difference in response |
| CMA delivery method | Email PDF vs. hand-delivered package | 20-40% improvement in appointment rate |
| Subject line (email) | Pain-point vs. value-offer vs. curiosity | 15-25% improvement in open rate |
| Call script opening | "I noticed your listing expired" vs. "I have a buyer for your area" | 10-20% improvement in conversation rate |

**Medium Impact (Test After Basics Are Established)**:
| Variable | What to Compare | Expected Impact |
|----------|----------------|-----------------|
| Mail piece type | Postcard vs. letter vs. handwritten | 50-200% variation in response rate |
| Mail copy | Empathetic vs. data-driven vs. urgency-based | 10-30% variation |
| Follow-up cadence | 3 touches in 7 days vs. 5 touches in 14 days | 10-20% variation |
| Time of day (calls) | Morning (9-11 AM) vs. afternoon (4-6 PM) | 5-15% variation |
| Email sequence length | 3-email vs. 5-email vs. 7-email drip | 10-25% variation |

**Lower Impact (Test When You Have Volume)**:
| Variable | What to Compare | Expected Impact |
|----------|----------------|-----------------|
| Envelope color/style | White vs. yellow vs. handwritten-look | 5-10% variation |
| CMA format | Simple 1-pager vs. detailed 5-page report | 5-15% variation |
| Voicemail script | Short (15 sec) vs. long (30 sec) | 5-10% variation |
| Photography in mailers | With photos vs. text-only | 5-15% variation |

### 7.2 How to Run Tests with Small Lead Volumes

**The Minimum Viable Test Protocol**:

Real estate lead gen typically has small sample sizes (tens to low hundreds of leads per source per month). This requires adapted testing methods.

**Rule 1: Test one variable at a time**. Never change subject line AND timing AND channel simultaneously.

**Rule 2: Use minimum sample sizes per variant**:

| Response Rate | Min Sample Per Variant | Total Test Size | Detectable Difference |
|---------------|----------------------|-----------------|----------------------|
| ~1% (mail response) | 500 | 1,000 | 1% vs 2% (100% lift) |
| ~5% (phone connect) | 200 | 400 | 5% vs 10% (100% lift) |
| ~15% (expired contact) | 100 | 200 | 15% vs 25% (67% lift) |
| ~25% (email open) | 75 | 150 | 25% vs 40% (60% lift) |
| ~50% (past client response) | 50 | 100 | 50% vs 70% (40% lift) |

**Rule 3: When sample sizes are too small for statistical significance, use Bayesian estimation instead of frequentist testing**:

```python
import numpy as np
from scipy.stats import beta

def bayesian_ab_test(successes_a, trials_a, successes_b, trials_b, simulations=100000):
    """
    Bayesian A/B test using Beta distribution.
    Returns probability that B is better than A.
    Works well with small samples (even N < 50).
    """
    # Beta distribution with uninformative prior (alpha=1, beta=1)
    samples_a = beta.rvs(1 + successes_a, 1 + trials_a - successes_a, size=simulations)
    samples_b = beta.rvs(1 + successes_b, 1 + trials_b - successes_b, size=simulations)

    prob_b_better = np.mean(samples_b > samples_a)
    expected_lift = np.mean((samples_b - samples_a) / samples_a)

    return {
        'prob_b_better': round(prob_b_better, 3),
        'expected_lift': round(expected_lift * 100, 1),
        'recommendation': 'switch_to_b' if prob_b_better > 0.85 else
                         ('switch_to_a' if prob_b_better < 0.15 else 'keep_testing')
    }

# Example: Testing two expired listing scripts
# Script A: 8 appointments from 50 contacts (16%)
# Script B: 14 appointments from 50 contacts (28%)
result = bayesian_ab_test(8, 50, 14, 50)
# result: {'prob_b_better': 0.943, 'expected_lift': 82.3, 'recommendation': 'switch_to_b'}
```

**Decision Thresholds**:
- **> 85% probability one variant is better**: Declare a winner and implement
- **70-85% probability**: Keep testing for another cycle
- **< 70% probability**: No meaningful difference; pick the cheaper/easier option

### 7.3 Testing Cadence Recommendations

| Test Type | Test Duration | Minimum Cycles/Year | Notes |
|-----------|--------------|---------------------|-------|
| Email subject lines | 2-4 weeks per test | 6-12 | Fast feedback, high volume |
| Call scripts | 4-8 weeks per test | 4-6 | Need enough conversations to compare |
| Mail piece design | 8-12 weeks per test | 2-4 | Slow response cycle, need multiple touches |
| Outreach channel | 8-12 weeks per test | 2-4 | Each source should test its primary channel |
| Follow-up cadence | 12-16 weeks per test | 2-3 | Need full funnel data to evaluate |
| Scoring model weights | Quarterly review | 4 | Continuous improvement cycle |
| Overall strategy allocation | Quarterly review | 4 | Shift time/money to top performers |

### 7.4 Test Tracking Template

For each active test, maintain:

```
Test ID: TEST-2026-001
Test Name: Expired Listing Call Script - Empathetic vs Data-Driven
Variable: Opening script line
Variant A: "I understand your listing expired and that can be frustrating..."
Variant B: "I analyzed your listing data and found three specific reasons it may not have sold..."
Start Date: 2026-03-01
Target End Date: 2026-04-15
Minimum Sample: 50 contacts per variant
Success Metric: Appointment set rate (from contact)
Current Results:
  - Variant A: ___ appointments / ___ contacts = ___%
  - Variant B: ___ appointments / ___ contacts = ___%
  - Bayesian probability B > A: ___%
Status: Active / Paused / Complete
Winner: TBD
```

---

## 8. Reporting Templates

### 8.1 Weekly Performance Report

Generate every Monday morning. Time to complete: 10-15 minutes with TheLeadEdge system.

```
===================================================================
WEEKLY LEAD GENERATION REPORT
Week of: [Date] to [Date]
===================================================================

--- PIPELINE SUMMARY ---
New leads this week:            ___
  Expired:         ___    FSBO:           ___
  Pre-Foreclosure: ___    Probate:        ___
  Withdrawn:       ___    Past Client:    ___
  Referral:        ___    Other:          ___

Leads scored S (Hot):           ___  (target: 3-8)
Leads scored A (High):          ___  (target: 8-15)

--- ACTIVITY SUMMARY ---
Outreach attempts:              ___
  Phone calls:     ___    Emails:         ___
  Mail pieces:     ___    Door knocks:    ___
  Texts:           ___

Contacts made (2-way):         ___  (target: 15-25)
Appointments set:              ___  (target: 2-5)
Listing presentations:         ___  (target: 1-3)
New listings signed:           ___

--- CONVERSION SNAPSHOT ---
Contact rate this week:        ___% (vs. ___% last week)
Appointment rate this week:    ___% (vs. ___% last week)
Listing rate this week:        ___% (vs. ___% last week)

--- PIPELINE HEALTH ---
Total active leads:            ___
  S-Tier:   ___    A-Tier:   ___    B-Tier:   ___
Leads contacted but no appt:   ___  (follow up queue)
Appointments pending:          ___
Active listings:               ___
Pending transactions:          ___
Expected closings this month:  ___

--- SPEED METRICS ---
Avg time to first contact:     ___ hours (target: < 12)
Expired leads contacted same day: ___/___  (___%)
Stale leads (7+ days, no contact): ___  (ACTION REQUIRED if > 5)

--- TOP PRIORITIES THIS WEEK ---
1. ________________________________________________
2. ________________________________________________
3. ________________________________________________

--- NOTES / OBSERVATIONS ---
_________________________________________________
_________________________________________________
===================================================================
```

### 8.2 Monthly Strategy Review

Generate on the 1st of each month. Time: 30-45 minutes.

```
===================================================================
MONTHLY STRATEGY REVIEW
Month: [Month Year]
===================================================================

--- FINANCIAL SUMMARY ---
                        This Month      Last Month      3-Mo Avg
Total spend:            $___            $___            $___
Closed deals:           ___             ___             ___
Gross commission:       $___            $___            $___
Net profit:             $___            $___            $___
Blended ROI:            ___%            ___%            ___%
Blended CPA:            $___            $___            $___

--- SOURCE PERFORMANCE ---
| Source          | Leads | Contacts | Appts | Listings | Closes | Revenue  | Cost  | ROI     |
|-----------------|-------|----------|-------|----------|--------|----------|-------|---------|
| Expired         |       |          |       |          |        |          |       |         |
| FSBO            |       |          |       |          |        |          |       |         |
| Pre-Foreclosure |       |          |       |          |        |          |       |         |
| Probate         |       |          |       |          |        |          |       |         |
| Withdrawn       |       |          |       |          |        |          |       |         |
| Past Client     |       |          |       |          |        |          |       |         |
| Referral        |       |          |       |          |        |          |       |         |
| Direct Mail     |       |          |       |          |        |          |       |         |
| Digital         |       |          |       |          |        |          |       |         |
| TOTAL           |       |          |       |          |        |          |       |         |

--- FUNNEL ANALYSIS ---
| Stage Transition          | This Month | Last Month | Trend | Industry Avg |
|---------------------------|------------|------------|-------|-------------|
| Raw --> Qualified          |    %       |    %       |       |   40-60%    |
| Qualified --> Contact      |    %       |    %       |       |   30-50%    |
| Contact --> Appointment    |    %       |    %       |       |   20-30%    |
| Appointment --> Listing    |    %       |    %       |       |   30-45%    |
| Listing --> Closed         |    %       |    %       |       |   85-92%    |

--- SCORING MODEL PERFORMANCE ---
S-Tier leads: ___ generated, ___ converted (___%)  Expected: 15-25%
A-Tier leads: ___ generated, ___ converted (___%)  Expected: 8-15%
B-Tier leads: ___ generated, ___ converted (___%)  Expected: 3-8%
False positive rate: ___%  (target: < 60%)
False negative rate: ___%  (target: < 15%)

--- A/B TEST RESULTS ---
Test: ________________________________
Result: ______________________________
Action: ______________________________

--- DECISIONS ---
[ ] Continue all current strategies unchanged
[ ] Increase investment in: _________________________
[ ] Decrease investment in: _________________________
[ ] Kill strategy: __________________________________
[ ] Launch new test: ________________________________
[ ] Adjust scoring weights: _________________________

--- NEXT MONTH GOALS ---
Lead target: ___
Contact target: ___
Appointment target: ___
Listing target: ___
Revenue target: $___
===================================================================
```

### 8.3 Quarterly ROI Analysis

Generate every quarter. Time: 60-90 minutes. This is the strategic decision-making document.

```
===================================================================
QUARTERLY ROI ANALYSIS
Quarter: Q_ [Year]
Period: [Start Date] - [End Date]
===================================================================

--- EXECUTIVE SUMMARY ---
Total investment this quarter:      $___
Total revenue this quarter:         $___
Net profit:                         $___
Overall ROI:                        ___%
Deals closed:                       ___
Avg commission per deal:            $___
Avg CPA:                            $___
Pipeline value (expected closings next Q): $___

--- ROI BY SOURCE (RANKED) ---
| Rank | Source          | Investment | Revenue | Net Profit | ROI     | Trend vs Last Q |
|------|-----------------|-----------|---------|------------|---------|-----------------|
| 1    |                 |           |         |            |         |                 |
| 2    |                 |           |         |            |         |                 |
| 3    |                 |           |         |            |         |                 |
| ...  |                 |           |         |            |         |                 |

--- TIME-ADJUSTED ROI ---
| Source          | Hours Invested | Revenue | Revenue/Hour | Rank |
|-----------------|---------------|---------|-------------|------|
|                 |               |         |             |      |

--- SCORING MODEL QUARTERLY REVIEW ---
Overall calibration (Brier score):  ___
Top 3 most predictive signals:      1.___  2.___  3.___
Top 3 least predictive signals:     1.___  2.___  3.___
Signal weight adjustments made:     [ ] Yes  [ ] No
  Details: _________________________________

--- MARKET CONDITION IMPACT ---
Median home price trend:            Up / Flat / Down ___%
Average DOM trend:                  Increasing / Stable / Decreasing
Inventory level:                    ___  (months of supply)
Expired listing volume trend:       Up / Flat / Down ___%
Pre-foreclosure volume trend:       Up / Flat / Down ___%
Interest rate environment:          ___%  Direction: ___

--- STRATEGIC DECISIONS ---
Sources to increase investment:     _______________________________
Sources to decrease investment:     _______________________________
Sources to eliminate:               _______________________________
New sources to test:                _______________________________
Budget reallocation plan:           _______________________________
Scoring model changes:              _______________________________

--- NEXT QUARTER TARGETS ---
Revenue target:                     $___  (___% change from this Q)
Lead target:                        ___
Close target:                       ___
Budget:                             $___
Key initiatives:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________
===================================================================
```

### 8.4 Annual Business Planning Metrics

Generate in December/January. Time: 2-4 hours. This sets the direction for the year.

```
===================================================================
ANNUAL BUSINESS PLANNING
Year: [Year]
===================================================================

--- YEAR IN REVIEW ---
Total deals closed:                 ___
Total gross commission income (GCI): $___
Total lead gen investment:          $___
Net profit from lead gen:           $___
Annual ROI:                         ___%
Avg deal value:                     $___
Best performing source:             ___ (___% of revenue)
Worst performing source:            ___ (___% of revenue)
Biggest win:                        ___________________________
Biggest lesson:                     ___________________________

--- SOURCE EVOLUTION (YEAR-OVER-YEAR) ---
| Source          | Last Year Deals | This Year Deals | Change | Last Year Rev | This Year Rev | Change |
|-----------------|----------------|-----------------|--------|--------------|---------------|--------|
| Expired         |                |                 |        |              |               |        |
| FSBO            |                |                 |        |              |               |        |
| Pre-Foreclosure |                |                 |        |              |               |        |
| Probate         |                |                 |        |              |               |        |
| Past Client     |                |                 |        |              |               |        |
| Referral        |                |                 |        |              |               |        |
| Direct Mail     |                |                 |        |              |               |        |
| Digital         |                |                 |        |              |               |        |
| Other           |                |                 |        |              |               |        |
| TOTAL           |                |                 |        |              |               |        |

--- NEXT YEAR PROJECTIONS ---
(See Section 10 for detailed goal setting methodology)

Target GCI:                         $___
Target deals:                       ___
Target avg commission:              $___
Planned lead gen budget:            $___  (___% of projected GCI)
Budget allocation by source:        (table below)

| Source          | Budget | Expected Leads | Expected Deals | Expected Revenue |
|-----------------|--------|---------------|----------------|------------------|
|                 |        |               |                |                  |

--- SYSTEM IMPROVEMENT PLAN ---
Automation upgrades planned:        ___________________________
New data sources to integrate:      ___________________________
Scoring model improvements:         ___________________________
Technology investments:             ___________________________
Training / skill development:       ___________________________
===================================================================
```

---

## 9. Feedback Loop Design

The scoring model and strategy allocation are only as good as the feedback loops that refine them. This section defines how conversion data flows back into the system to make it smarter over time.

### 9.1 How Conversion Data Feeds Back Into the Scoring Model

**The Feedback Cycle**:

```
1. Lead Identified --> Scored by current model --> Enters pipeline
2. Lead progresses through funnel stages (or drops out)
3. Outcome recorded (converted / not converted)
4. Outcome compared to predicted score
5. Signal-outcome correlations recalculated
6. Model weights adjusted (if warranted)
7. Updated model applied to all future leads
```

**Implementation**:

```python
class ScoringFeedbackLoop:
    """
    Collects conversion outcomes and adjusts scoring weights.
    """

    def record_outcome(self, lead_id: int, outcome: str, stage_reached: str):
        """Record the final outcome for a lead."""
        # outcome: 'converted' | 'not_converted' | 'in_progress'
        # stage_reached: 'raw' | 'qualified' | 'contact' | 'appointment' | 'listing' | 'closed'
        db.execute("""
            UPDATE lead_sources
            SET outcome = ?, final_stage = ?, outcome_date = CURRENT_TIMESTAMP
            WHERE lead_id = ?
        """, (outcome, stage_reached, lead_id))

    def calculate_signal_effectiveness(self, min_sample: int = 30):
        """
        For each signal, calculate how well it predicts conversion.
        Only runs when we have enough data (min_sample per signal).
        """
        signals = db.execute("""
            SELECT signal_type,
                   COUNT(*) as total,
                   SUM(CASE WHEN outcome = 'converted' THEN 1 ELSE 0 END) as converted,
                   AVG(CASE WHEN outcome = 'converted' THEN 1.0 ELSE 0.0 END) as conversion_rate
            FROM lead_signals ls
            JOIN lead_sources lsrc ON ls.lead_id = lsrc.lead_id
            WHERE lsrc.outcome IS NOT NULL
            GROUP BY signal_type
            HAVING COUNT(*) >= ?
        """, (min_sample,)).fetchall()

        return signals

    def suggest_weight_adjustments(self):
        """
        Compare observed conversion rates to current weights.
        Suggest adjustments to bring them into alignment.
        """
        effectiveness = self.calculate_signal_effectiveness()
        base_rate = self.get_base_conversion_rate()

        suggestions = []
        for signal in effectiveness:
            lift = signal['conversion_rate'] / base_rate
            current_weight = self.get_current_weight(signal['signal_type'])

            # Ideal weight is proportional to lift
            ideal_weight = lift * 10  # Baseline of 10 for 1x lift
            adjustment = ideal_weight - current_weight

            if abs(adjustment) > 2:  # Only suggest if difference is meaningful
                suggestions.append({
                    'signal': signal['signal_type'],
                    'current_weight': current_weight,
                    'suggested_weight': round(ideal_weight, 1),
                    'adjustment': round(adjustment, 1),
                    'sample_size': signal['total'],
                    'observed_lift': round(lift, 2)
                })

        return suggestions
```

### 9.2 Model Retraining Triggers

The model should not be retrained constantly (that leads to overfitting to noise). Instead, retrain when specific conditions are met.

| Trigger | Condition | Action |
|---------|-----------|--------|
| **Calendar-based** | Every 90 days (quarterly) | Full signal correlation review and weight adjustment |
| **Volume-based** | Every 100 outcomes recorded (converted or not) | Recalculate signal effectiveness |
| **Performance-based** | Brier score degrades > 20% from baseline | Emergency recalibration |
| **False positive spike** | FP rate increases > 15 percentage points in 30 days | Review overweighted signals |
| **False negative spike** | FN rate increases > 10 percentage points in 30 days | Review underweighted signals |
| **Market shift** | Median DOM changes > 20% or inventory changes > 30% | Re-evaluate time-based thresholds |
| **New data source** | New signal type added to the system | Add to model with conservative initial weight, monitor for 60 days |

### 9.3 When to Kill an Underperforming Strategy

Not every lead source will work, and some will stop working over time. Use this framework to decide when to cut losses.

**Kill Decision Matrix**:

| Condition | Time Threshold | Data Threshold | Decision |
|-----------|---------------|----------------|----------|
| Zero conversions from source | 90 days | At least 50 leads processed | Pause and investigate |
| ROI < 50% (losing money) | 6 months | At least 100 leads processed | Kill unless trend is improving |
| ROI < breakeven but improving | 6 months | At least 100 leads processed | Continue with 90-day review |
| Revenue/hour < 25% of top source | 6 months | At least 50 hours invested | Reallocate time, keep passive |
| Agent satisfaction < 3/10 (self-reported) | Any | Any | Discuss; may kill regardless of numbers |

**Kill Process**:
1. Review the data to confirm underperformance is not due to external factors (market shift, seasonal variation, implementation error)
2. Verify sufficient sample size for the conclusion (see Section 7.2 minimum samples)
3. Check if the strategy could be improved with a different approach (different outreach method, timing, messaging) before killing it entirely
4. If killing: wind down over 30 days (complete active sequences), reallocate budget, document lessons learned

### 9.4 When to Double Down on a Winning Strategy

**Scale-Up Decision Matrix**:

| Condition | Confidence Required | Action |
|-----------|--------------------|----|
| ROI > 500% for 3+ months | High confidence (90+ day track record) | Increase budget 50-100% |
| Conversion rate > 2x industry average | High confidence | Increase outreach volume |
| Revenue/hour is highest of all sources | Moderate confidence (60+ days) | Reallocate time from lower sources |
| New signal combination shows 3x base conversion rate | Need 30+ leads with that combination | Add specific outreach sequence for that combination |
| Market conditions favor a source (e.g., rising foreclosures) | External data supports | Temporarily increase investment |

**Scale-Up Process**:
1. Confirm the performance is not a fluke (statistical significance or Bayesian > 90% confidence)
2. Increase budget incrementally (25-50% per quarter, not all at once)
3. Monitor for diminishing returns as you scale (saturation effect)
4. Set a ceiling based on market size (e.g., only 50 expireds/month in your market = natural cap)
5. Track marginal ROI (ROI on the incremental spend, not total)

### 9.5 Minimum Data Thresholds Before Making Decisions

**Critical Rule**: Never make strategy decisions on insufficient data. The table below defines the minimum data required for each type of decision.

| Decision Type | Minimum Sample Size | Minimum Time Period | Confidence Level Required |
|---------------|--------------------|--------------------|---------------------------|
| Kill a lead source | 50+ leads from source, 90+ days | 3 months | 85%+ probability it underperforms |
| Scale up a lead source | 30+ conversions from source | 3 months | 85%+ probability it outperforms |
| Change scoring weights | 30+ outcomes per signal being adjusted | 2 months | Correlation is statistically significant (p < 0.05) |
| Declare A/B test winner | See Section 7.2 minimum samples | Varies by metric | 85%+ Bayesian probability |
| Add a new signal to scoring model | 20+ leads with signal present and 20+ without | 2 months | Signal shows > 1.5x lift |
| Remove a signal from scoring model | 50+ leads with signal present | 3 months | Signal shows < 1.1x lift and p > 0.20 |
| Reallocate budget between sources | Both sources have 3+ months data | 3 months | Source ROI difference > 100% |
| Change outreach method for a source | 50+ outreach attempts per method | 6 weeks | Response rate difference > 50% |

---

## 10. Goal Setting Framework

### 10.1 First 90 Days: Realistic Goals for a New System

The first 90 days are about building the data foundation, not closing deals. Most leads from a new system will not close for 60-180 days.

**Phase 1 Goals (Days 1-30): Infrastructure & First Leads**

| Goal | Target | How to Measure |
|------|--------|----------------|
| System operational | MLS alerts + public record checks running daily | Daily briefing produced |
| Lead volume | 100+ raw leads identified | Count in tracker/database |
| Lead scoring | All leads scored and tiered | Scores assigned in system |
| First contacts | 30+ outreach attempts | CRM activity log |
| Conversations | 5-10 two-way conversations | CRM notes |
| Appointments | 1-3 appointments set | Calendar entries |
| Daily workflow | < 45 min/day on lead research | Time tracking |
| Baseline metrics | Tracking spreadsheet/dashboard active | All KPIs being recorded |

**Phase 2 Goals (Days 31-60): Refine & Scale**

| Goal | Target | How to Measure |
|------|--------|----------------|
| Lead volume | 200+ raw leads (cumulative) | Database count |
| Contact rate | 20%+ of scored leads contacted | Outreach / leads ratio |
| Appointments | 3-5 total (cumulative) | Calendar |
| First listing | 0-1 listing agreements signed | Signed agreements |
| A/B test | 1 test running | Test tracker |
| Scoring calibration | First calibration check completed | Score tier vs actual outcome |
| Outreach efficiency | Optimal channel identified for top 3 sources | Response rate data |

**Phase 3 Goals (Days 61-90): First Revenue**

| Goal | Target | How to Measure |
|------|--------|----------------|
| Leads (cumulative) | 400+ | Database |
| Active pipeline | 15-30 leads in contact/appointment stages | Funnel report |
| Listings (cumulative) | 1-3 | MLS |
| First closing | 0-1 closed deals from system leads | Transaction records |
| Model accuracy | First false positive/negative analysis completed | Calibration report |
| Time efficiency | < 30 min/day on lead research | Time tracking |
| First monthly report | Complete monthly review generated | Report document |

**What "Good" Looks Like at 90 Days**:
- 400+ leads in the database with scores
- 15-30 leads in active conversation/nurture
- 1-3 listing agreements (some may come from warm leads accelerated by the system)
- 0-1 closed deals (do not expect more this early; pipeline takes time to produce)
- Clear data on which sources and channels are working
- System requires < 30 min/day to operate
- All KPIs being tracked consistently

### 10.2 Six-Month Targets

By 6 months, the system should be self-funding and producing a predictable pipeline.

| Metric | Target | Notes |
|--------|--------|-------|
| Monthly lead intake | 100-200 scored leads | All sources combined |
| Monthly contacts | 30-50 conversations | Active outreach |
| Monthly appointments | 4-8 | Listing presentations |
| Monthly new listings | 1-3 | From system-generated leads |
| Closed deals (cumulative) | 4-8 | Total from system since launch |
| GCI from system leads (cumulative) | $40,000-$80,000 | Total since launch |
| Total investment to date | $6,000-$16,000 | All costs since launch |
| Cumulative ROI | 300-900% | Revenue / investment |
| Scoring model accuracy | Brier < 0.15 | Calibration checked quarterly |
| False positive rate | < 70% | Improving from baseline |
| System operation time | < 20 min/day | Automation reducing manual work |
| Best source identified | Data-backed decision | Shift resources to top 3 sources |

**Milestone**: At 6 months, you should be able to answer with confidence: "My best lead source is X, it costs $Y per deal, and each deal generates $Z in commission."

### 10.3 Twelve-Month Targets

By 12 months, the system is a core revenue driver with predictive capabilities.

| Metric | Conservative | Moderate | Aggressive |
|--------|-------------|----------|------------|
| Annual deals from system | 8-12 | 12-18 | 18-24+ |
| Annual GCI from system | $80K-$120K | $120K-$180K | $180K-$240K+ |
| Annual lead gen spend | $13K-$20K | $20K-$30K | $30K-$40K |
| Annual net profit | $60K-$100K | $90K-$150K | $140K-$200K |
| Annual ROI | 400-600% | 500-700% | 500-700% |
| Monthly pipeline value | $30K-$50K | $50K-$80K | $80K-$120K |
| Pipeline velocity | $150-$300/day | $300-$500/day | $500-$800/day |
| Scoring model accuracy (Brier) | < 0.12 | < 0.10 | < 0.08 |
| Automation coverage | 60% of workflow | 75% of workflow | 85% of workflow |
| Time per day | < 15 min | < 10 min | < 10 min |

### 10.4 Adjusting Goals Based on Market Conditions

Real estate is cyclical. Goals must flex with market reality.

**Market Condition Adjustments**:

| Market Condition | Impact on TheLeadEdge | Goal Adjustment |
|-----------------|---------------------|-----------------|
| **Rising inventory / buyer's market** | More expireds, more motivated sellers, longer DOM | Increase lead targets 20-30%, shift to expired/DOM strategies |
| **Low inventory / seller's market** | Fewer expireds, faster sales, less motivation | Decrease expired targets, increase buyer-side focus, focus on off-market/creative strategies |
| **Rising interest rates** | More pre-foreclosure, ARM resets, fewer buyers | Increase pre-foreclosure monitoring, longer close timelines, adjust pipeline velocity expectations |
| **Falling interest rates** | Refinance boom reduces sellers, more buyers | Decrease foreclosure targets, increase move-up buyer focus |
| **Recession / job losses** | More distressed sellers, lower prices, fewer buyers | Shift to distress strategies, lower commission expectations, increase volume targets |
| **Strong economy / job growth** | Relocation leads increase, fewer distress, higher prices | Focus on relocation and life-event strategies, increase commission expectations |
| **Seasonal (winter slowdown)** | Fewer listings, fewer leads, longer cycles | Reduce monthly targets 20-40% (Nov-Feb), build pipeline for spring |
| **Seasonal (spring/summer peak)** | Maximum volume and velocity | Increase targets 20-40% (Mar-Jun), capitalize on momentum |

**Adjustment Formula**:
```
Adjusted Target = Base Target * Market Multiplier * Seasonal Multiplier

Market Multiplier:
  Hot seller's market: 0.7
  Normal market: 1.0
  Buyer's market: 1.2
  Distressed market: 1.3

Seasonal Multiplier:
  Q1 (Jan-Mar): 0.8 (ramp up)
  Q2 (Apr-Jun): 1.2 (peak)
  Q3 (Jul-Sep): 1.1 (sustained)
  Q4 (Oct-Dec): 0.7 (slowdown)
```

### 10.5 Commission Income Projections

Use the conversion rate data from this document to project income based on lead volume.

**Projection Model**:

```
Monthly GCI Projection = SUM across all sources:
  (Monthly Leads from Source_i * Lead-to-Close Rate_i * Avg Commission_i)
```

**Scenario Planning Table**:

| Scenario | Monthly Leads (all sources) | Blended Close Rate | Avg Commission | **Monthly GCI** | **Annual GCI** |
|----------|---------------------------|--------------------|----|---|---|
| Conservative | 80 | 2% | $9,000 | **$14,400** | **$172,800** |
| Moderate | 120 | 3% | $10,000 | **$36,000** | **$432,000** |
| Aggressive | 200 | 4% | $11,000 | **$88,000** | **$1,056,000** |
| System Target (Y1) | 100 | 2.5% | $10,000 | **$25,000** | **$300,000** |

**Income Sensitivity Analysis** (how small improvements compound):

| If you improve... | By this much... | Annual GCI impact |
|-------------------|----------------|-------|
| Lead volume | +20 leads/month | +$60,000/year (at 2.5% close, $10K commission) |
| Close rate | +1 percentage point | +$120,000/year (at 100 leads/month, $10K commission) |
| Average commission | +$1,000/deal | +$30,000/year (at 30 closings/year) |
| Contact speed (expired) | Same day (from 2-day avg) | +$20,000-$40,000/year (estimated from higher conversion) |

**Key Insight from the Sensitivity Analysis**: Improving the close rate by just 1 percentage point (e.g., from 2.5% to 3.5%) has a larger impact than increasing lead volume by 20%. This is why the scoring model, outreach timing, and conversion optimization (Sections 3, 7) are more valuable than simply generating more leads.

---

## Appendix A: KPI Glossary

| Term | Definition | Formula |
|------|-----------|---------|
| CPL (Cost Per Lead) | Total cost to generate one lead from a source | Total Source Cost / Total Leads |
| CPA (Cost Per Acquisition) | Total cost to close one deal from a source | Total Source Cost / Total Closed Deals |
| GCI (Gross Commission Income) | Total commission earned before splits/fees | Sum of all commission checks |
| ROI (Return on Investment) | Percentage return on money invested | ((Revenue - Cost) / Cost) * 100 |
| LTV (Lifetime Value) | Total revenue expected from one client relationship | Initial Commission * LTV Multiplier |
| DOM (Days on Market) | Days a listing has been active in MLS | Current Date - List Date |
| Pipeline Velocity | Revenue momentum of the active pipeline | (Leads * Win Rate * Avg Deal) / Avg Cycle Days |
| Brier Score | Measures calibration of a probability model | Mean of (predicted - actual)^2 |
| False Positive Rate | % of high-scored leads that never converted | False Positives / All High-Scored Leads |
| False Negative Rate | % of converted leads that were scored low | Low-Scored Converters / All Converters |
| Blended Conversion Rate | Weighted average conversion across all sources | Total Closings / Total Leads |
| Break-Even Point | Number of leads/deals needed to cover costs | Fixed Cost / (Commission * Conversion Rate) |
| Marginal ROI | ROI on additional/incremental spend | Incremental Revenue / Incremental Cost |
| Contact Rate | % of outreach attempts that reach a person | Contacts / Outreach Attempts |
| Response Rate | % of leads that respond to any outreach | Responses / Leads Contacted |

## Appendix B: Database Schema for Metrics Tracking

```sql
-- Core lead tracking
CREATE TABLE lead_sources (
    lead_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type     TEXT NOT NULL,
    source_detail   TEXT,
    property_id     INTEGER REFERENCES properties(id),
    identified_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    initial_score   REAL,
    current_score   REAL,
    funnel_stage    TEXT DEFAULT 'raw',
    outcome         TEXT,                  -- 'converted', 'not_converted', 'in_progress'
    final_stage     TEXT,
    outcome_date    TIMESTAMP,
    cost_allocated  REAL DEFAULT 0.0,
    notes           TEXT
);

-- Funnel stage transitions
CREATE TABLE stage_transitions (
    transition_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id         INTEGER REFERENCES lead_sources(lead_id),
    from_stage      TEXT,
    to_stage        TEXT NOT NULL,
    transition_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    days_in_prior_stage REAL
);

-- Outreach activity tracking
CREATE TABLE outreach_activities (
    activity_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id         INTEGER REFERENCES lead_sources(lead_id),
    activity_type   TEXT NOT NULL,          -- 'call', 'email', 'mail', 'text', 'door_knock'
    activity_date   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    result          TEXT,                   -- 'connected', 'voicemail', 'no_answer', 'email_sent', etc.
    response        TEXT,                   -- 'positive', 'neutral', 'negative', 'none'
    notes           TEXT
);

-- Financial tracking
CREATE TABLE transactions (
    transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id         INTEGER REFERENCES lead_sources(lead_id),
    property_id     INTEGER REFERENCES properties(id),
    status          TEXT NOT NULL,          -- 'pending', 'closed', 'fell_through'
    list_price      REAL,
    sale_price      REAL,
    commission_rate REAL,
    commission_earned REAL,
    close_date      DATE,
    days_in_pipeline INTEGER
);

-- A/B test tracking
CREATE TABLE ab_tests (
    test_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name       TEXT NOT NULL,
    variable_tested TEXT NOT NULL,
    variant_a_desc  TEXT NOT NULL,
    variant_b_desc  TEXT NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE,
    success_metric  TEXT NOT NULL,
    status          TEXT DEFAULT 'active',  -- 'active', 'paused', 'complete'
    winner          TEXT,                   -- 'a', 'b', 'no_difference'
    notes           TEXT
);

CREATE TABLE ab_test_assignments (
    assignment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id         INTEGER REFERENCES ab_tests(test_id),
    lead_id         INTEGER REFERENCES lead_sources(lead_id),
    variant         TEXT NOT NULL,          -- 'a' or 'b'
    success         INTEGER DEFAULT 0,      -- 0 or 1
    assigned_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scoring model history
CREATE TABLE score_snapshots (
    snapshot_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id         INTEGER REFERENCES lead_sources(lead_id),
    score           REAL NOT NULL,
    score_date      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    signals_present TEXT                    -- JSON array of active signals
);

-- Monthly spend tracking
CREATE TABLE monthly_spend (
    spend_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    month           TEXT NOT NULL,          -- '2026-03'
    source_type     TEXT NOT NULL,
    category        TEXT NOT NULL,          -- 'subscription', 'variable', 'advertising', 'relationship'
    description     TEXT,
    amount          REAL NOT NULL
);

-- Key views for reporting
CREATE VIEW v_source_performance AS
SELECT
    ls.source_type,
    COUNT(*) AS total_leads,
    SUM(CASE WHEN ls.funnel_stage IN ('contact','appointment','listing','pending','closed') THEN 1 ELSE 0 END) AS contacted,
    SUM(CASE WHEN ls.funnel_stage IN ('appointment','listing','pending','closed') THEN 1 ELSE 0 END) AS appointments,
    SUM(CASE WHEN ls.funnel_stage IN ('listing','pending','closed') THEN 1 ELSE 0 END) AS listings,
    SUM(CASE WHEN ls.funnel_stage = 'closed' THEN 1 ELSE 0 END) AS closed_deals,
    COALESCE(SUM(t.commission_earned), 0) AS total_revenue,
    SUM(ls.cost_allocated) AS total_cost,
    CASE WHEN SUM(ls.cost_allocated) > 0
         THEN ROUND((COALESCE(SUM(t.commission_earned), 0) - SUM(ls.cost_allocated)) / SUM(ls.cost_allocated) * 100, 1)
         ELSE NULL END AS roi_pct
FROM lead_sources ls
LEFT JOIN transactions t ON ls.lead_id = t.lead_id AND t.status = 'closed'
GROUP BY ls.source_type;

CREATE VIEW v_funnel_conversion AS
SELECT
    source_type,
    ROUND(100.0 * SUM(CASE WHEN funnel_stage IN ('contact','appointment','listing','pending','closed') THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS pct_contacted,
    ROUND(100.0 * SUM(CASE WHEN funnel_stage IN ('appointment','listing','pending','closed') THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN funnel_stage IN ('contact','appointment','listing','pending','closed') THEN 1 ELSE 0 END), 0), 1) AS pct_contact_to_appt,
    ROUND(100.0 * SUM(CASE WHEN funnel_stage IN ('listing','pending','closed') THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN funnel_stage IN ('appointment','listing','pending','closed') THEN 1 ELSE 0 END), 0), 1) AS pct_appt_to_listing,
    ROUND(100.0 * SUM(CASE WHEN funnel_stage = 'closed' THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN funnel_stage IN ('listing','pending','closed') THEN 1 ELSE 0 END), 0), 1) AS pct_listing_to_close
FROM lead_sources
GROUP BY source_type;
```

## Appendix C: Quick-Reference Formula Sheet

```
=== COST METRICS ===
CPL = Total Source Cost / Total Leads
CPA = Total Source Cost / Closed Deals
CPA = CPL / Lead-to-Close Rate (equivalent)

=== REVENUE METRICS ===
GCI = Sum of all commission earned
Revenue Per Lead = Total Revenue / Total Leads (by source)
Revenue Per Hour = (Leads/Hour * Close Rate * Avg Commission)
Avg Commission = Total Commission / Closed Deals

=== ROI METRICS ===
ROI = ((Revenue - Cost) / Cost) * 100
Net Profit = Revenue - Cost
Marginal ROI = (Additional Revenue from Additional Spend) / Additional Spend * 100
Break-Even Leads = Fixed Cost / (Avg Commission * Close Rate)

=== CONVERSION METRICS ===
Conversion Rate = Leads Reaching Next Stage / Leads in Current Stage * 100
Drop-Off Rate = 1 - Conversion Rate
End-to-End Conversion = Product of all stage conversion rates
Blended Close Rate = Total Closings / Total Leads (across all sources)

=== PIPELINE METRICS ===
Pipeline Velocity ($) = (Active Leads * Win Rate * Avg Deal Value) / Avg Cycle Days
Pipeline Value = Sum of (Deal Probability * Deal Value) for all active leads
Avg Cycle Time = Avg(Close Date - Identified Date) for closed deals

=== SCORING METRICS ===
Brier Score = (1/N) * Sum((Predicted - Actual)^2)
False Positive Rate = FP / (FP + TP)
False Negative Rate = FN / (FN + TN)
Accuracy Ratio = Actual Conversion Rate / Predicted Conversion Rate
Point-Biserial r = correlation between binary signal and binary outcome

=== LIFETIME VALUE ===
LTV = Initial Commission * LTV Multiplier
Conservative LTV Multiplier = 1.5
Moderate LTV Multiplier = 2.0
Strong Relationship Multiplier = 2.5-3.0

=== PROJECTIONS ===
Monthly GCI = Sum(Monthly Leads_i * Close Rate_i * Avg Commission_i)
Annual GCI = Monthly GCI * 12
Adjusted Target = Base Target * Market Multiplier * Seasonal Multiplier
```

---

*This document provides the measurement infrastructure for the entire TheLeadEdge system. Every strategy, every lead source, and every dollar spent should be trackable using the frameworks defined here. Start with the Weekly Report (Section 8.1) on day one, add the Monthly Review (Section 8.2) after 30 days, and implement the Quarterly Analysis (Section 8.3) at the 90-day mark. The scoring feedback loop (Section 9) should begin collecting data immediately but should not drive weight adjustments until minimum data thresholds (Section 9.5) are met.*
