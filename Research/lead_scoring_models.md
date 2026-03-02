# Lead Scoring Models & Automation Opportunities for Real Estate Lead Generation

**Research Document | TheLeadEdge Project**
**Last Updated: 2026-02-28**

---

## Table of Contents

- [Part 1: Lead Scoring Models](#part-1-lead-scoring-models)
  - [1.1 Multi-Signal Scoring](#11-multi-signal-scoring)
  - [1.2 Motivation Indicators by Weight](#12-motivation-indicators-by-weight)
  - [1.3 Urgency Scoring](#13-urgency-scoring)
  - [1.4 Property Value Scoring](#14-property-value-scoring)
  - [1.5 Neighborhood Heat Mapping](#15-neighborhood-heat-mapping)
  - [1.6 Seller Motivation Matrix](#16-seller-motivation-matrix)
  - [1.7 Machine Learning Approaches](#17-machine-learning-approaches)
- [Part 2: Automation Opportunities](#part-2-automation-opportunities)
  - [2.1 MLS Alert Automation](#21-mls-alert-automation)
  - [2.2 Public Record Monitoring](#22-public-record-monitoring)
  - [2.3 CRM Integration](#23-crm-integration)
  - [2.4 Automated Outreach Sequences](#24-automated-outreach-sequences)
  - [2.5 Data Pipeline Architecture](#25-data-pipeline-architecture)
  - [2.6 API Opportunities](#26-api-opportunities)
  - [2.7 Web Scraping Considerations](#27-web-scraping-considerations)
  - [2.8 Report Generation](#28-report-generation)
- [Part 3: Tools & Platforms](#part-3-tools--platforms)
  - [3.1 Existing Tools in the Market](#31-existing-tools-in-the-market)
  - [3.2 Pricing and Capabilities Comparison](#32-pricing-and-capabilities-comparison)
  - [3.3 Gaps a Custom Solution Could Fill](#33-gaps-a-custom-solution-could-fill)
  - [3.4 Free vs Paid Data Sources](#34-free-vs-paid-data-sources)

---

# Part 1: Lead Scoring Models

## 1.1 Multi-Signal Scoring

### The Core Concept

Multi-signal scoring combines multiple independent data points into a single composite score that represents the probability a property owner is ready, willing, and motivated to sell. No single signal is reliable on its own, but when signals converge, prediction accuracy increases dramatically.

### The Additive Scoring Model

The simplest and most practical approach is a weighted additive model:

```
Lead Score = (Signal_1 * Weight_1) + (Signal_2 * Weight_2) + ... + (Signal_N * Weight_N)
```

**Example: Composite Lead Score Calculation**

| Signal | Present? | Weight | Points |
|--------|----------|--------|--------|
| Expired listing (last 90 days) | Yes | 15 | 15 |
| Price reduction (2+ reductions) | Yes | 12 | 12 |
| High DOM (90+ days) | Yes | 10 | 10 |
| Pre-foreclosure / NOD filed | No | 20 | 0 |
| Owner is out-of-state | Yes | 8 | 8 |
| Property vacant | Yes | 10 | 10 |
| Tax delinquent | No | 12 | 0 |
| Recent divorce filing | No | 14 | 0 |
| Probate filing | No | 16 | 0 |
| Equity > 40% | Yes | 5 | 5 |
| **Total Score** | | | **60** |

### Signal Categories

Organize signals into categories to prevent over-indexing on one type:

**MLS-Derived Signals**
- Expired listings (failed to sell)
- Withdrawn then relisted
- Price reductions (count and magnitude)
- Days on market exceeding area median
- Agent remarks suggesting motivation ("must sell", "bring all offers", "motivated seller")
- Status changes (active -> pending -> back to active = fell through)
- Photo quality decline (less investment in listing = fatigue)
- Listing description language analysis

**Public Record Signals**
- Notice of Default (NOD) / Lis Pendens
- Tax delinquency (1+ years behind)
- Probate filings
- Divorce filings
- Code violations / condemned notices
- Mechanic's liens (contractor disputes)
- Bankruptcy filings
- Property tax assessment increases (may trigger desire to sell)

**Property Condition Signals**
- Vacant property indicators
- Utility disconnection records (where available)
- Building permit history (no maintenance permits in 10+ years)
- Google Street View age of property appearance
- Code enforcement complaints

**Owner Situation Signals**
- Out-of-state owner (absentee)
- Corporate/LLC ownership (investor may want to liquidate)
- Length of ownership (20+ years = potential estate planning)
- Multiple properties owned (portfolio optimization)
- Owner age (public record in some states, 65+ may indicate downsizing)
- Recent death of a co-owner (public obituaries cross-referenced)

**Market Context Signals**
- Neighborhood sales velocity increasing
- Comparable properties selling above asking
- Area appreciation rate
- New construction nearby (competition for older homes)
- School rating changes
- Zoning changes or rezoning applications

### Signal Stacking (Multiplicative Bonuses)

When certain signals appear together, the probability of motivation increases non-linearly. Apply multipliers for specific combinations:

```
# Distressed Seller Stack
IF (expired_listing AND price_reduction >= 2 AND dom > 90):
    bonus_multiplier = 1.5

# Financial Distress Stack
IF (tax_delinquent AND pre_foreclosure):
    bonus_multiplier = 2.0

# Life Event Stack
IF (probate_filing AND out_of_state_heir AND vacant):
    bonus_multiplier = 2.5

# Tired Landlord Stack
IF (absentee_owner AND code_violations AND tenant_eviction_filed):
    bonus_multiplier = 1.8

Final_Score = Base_Score * bonus_multiplier
```

### Score Normalization

Normalize scores to a 0-100 scale for easy interpretation:

```python
def normalize_score(raw_score, max_possible_score):
    """Normalize to 0-100 scale with sigmoid smoothing."""
    linear = (raw_score / max_possible_score) * 100
    # Apply sigmoid to prevent extreme clustering
    import math
    sigmoid = 100 / (1 + math.exp(-0.05 * (linear - 50)))
    return round(sigmoid, 1)
```

### Score Tiers

| Tier | Score Range | Label | Recommended Action |
|------|-------------|-------|--------------------|
| S | 85-100 | Extremely Hot | Immediate personal outreach (phone call + handwritten note) |
| A | 70-84 | Very Hot | Personal outreach within 24 hours |
| B | 55-69 | Warm | Priority drip campaign + direct mail |
| C | 40-54 | Lukewarm | Standard drip campaign |
| D | 25-39 | Cool | Add to long-term nurture list |
| F | 0-24 | Cold | Monitor only, no active outreach |

---

## 1.2 Motivation Indicators by Weight

### Tier 1: Strongest Motivation Signals (Weight: 15-20 points)

These signals individually suggest high motivation and urgency:

| Signal | Weight | Rationale |
|--------|--------|-----------|
| Pre-foreclosure / NOD filed | 20 | Owner faces losing the property; deadline-driven motivation |
| Probate filing (inherited property) | 18 | Heirs often want to liquidate quickly; emotional burden |
| Active bankruptcy filing | 17 | Court-mandated liquidation may be required |
| Tax lien sale scheduled | 17 | Property will be lost at auction without action |
| Divorce with property in filing | 16 | Court may order sale; both parties want to move on |
| Condemned / uninhabitable notice | 15 | Owner faces demolition costs or forced sale |
| Expired listing (0-30 days ago) | 15 | Already tried to sell; still motivated but frustrated |

### Tier 2: Strong Motivation Signals (Weight: 10-14 points)

| Signal | Weight | Rationale |
|--------|--------|-----------|
| Multiple price reductions (3+) | 14 | Chasing the market down; increasingly desperate |
| Failed sale (pending back to active) | 13 | Deal fell through; seller may be demoralized |
| Tax delinquent 2+ years | 13 | Long-term financial stress |
| Vacant property + absentee owner | 12 | Carrying costs with no benefit |
| Code violations (multiple / unresolved) | 12 | Fines accumulating; costly to fix |
| DOM 2x+ area median | 11 | Property "going stale"; seller losing hope |
| Expired listing (31-90 days ago) | 10 | Motivation may still exist but cooling |
| Eviction filing by landlord | 10 | Tired landlord signal |

### Tier 3: Moderate Motivation Signals (Weight: 5-9 points)

| Signal | Weight | Rationale |
|--------|--------|-----------|
| Out-of-state owner | 8 | Managing remotely is burdensome |
| Ownership 20+ years | 7 | Likely significant equity; may be ready to downsize |
| Single price reduction (10%+) | 7 | Meaningful cut suggests real motivation |
| Recently inherited (no probate court) | 7 | May not want to keep property |
| Corporate/LLC ownership | 6 | Business decision, not emotional |
| Free & clear (no mortgage) | 5 | Lower barrier to sell; all equity |
| Building permits for repairs | 5 | May be prepping to sell |
| Property tax assessment spike | 5 | Higher carrying costs |

### Tier 4: Weak but Useful Signals (Weight: 1-4 points)

| Signal | Weight | Rationale |
|--------|--------|-----------|
| Owner age 65+ | 4 | Potential downsizer |
| Single-family owned by entity | 3 | May be underperforming rental |
| Neighborhood appreciation > 15%/yr | 3 | Owner sitting on gains |
| Recently refinanced at high rate | 3 | May prefer to sell vs. pay high rate |
| No homestead exemption | 2 | Likely non-owner-occupied |
| Utility account in different name | 2 | Tenant-occupied, landlord may sell |
| Property last sold 5-10 years ago | 1 | Moderate equity built up |

### Calibration Notes

These weights should be calibrated over time based on actual conversion data. The initial weights above are based on industry norms and agent experience. Track:

- **Conversion rate by signal**: What percentage of leads with each signal actually list?
- **Signal-to-close time**: How quickly does each signal type convert?
- **Commission value by signal**: Which signals correlate with higher-value transactions?

After 6-12 months of tracking, use logistic regression to recalibrate the weights with real data. See Section 1.7 for details.

---

## 1.3 Urgency Scoring

### The Time-Decay Principle

Lead quality is not static. Most signals lose predictive power over time. A freshly expired listing is far more valuable than one that expired 6 months ago. Urgency scoring applies time-decay functions to each signal.

### Decay Functions

**Linear Decay**
Simple and easy to understand. Used for signals that degrade steadily:

```python
def linear_decay(days_since_event, half_life_days):
    """Score decays linearly to zero at 2x the half-life."""
    max_days = half_life_days * 2
    if days_since_event >= max_days:
        return 0.0
    return 1.0 - (days_since_event / max_days)
```

**Exponential Decay**
More realistic for most signals. Sharp initial decay, then long tail:

```python
import math

def exponential_decay(days_since_event, half_life_days):
    """Score halves every half_life_days."""
    return math.pow(0.5, days_since_event / half_life_days)
```

**Step Decay**
For signals with clear phase transitions:

```python
def step_decay(days_since_event):
    """Discrete urgency tiers."""
    if days_since_event <= 7:
        return 1.0    # Critical window
    elif days_since_event <= 30:
        return 0.75   # High urgency
    elif days_since_event <= 90:
        return 0.50   # Moderate urgency
    elif days_since_event <= 180:
        return 0.25   # Low urgency
    else:
        return 0.05   # Minimal (but not zero -- still a data point)
```

### Recommended Half-Lives by Signal Type

| Signal | Half-Life | Decay Type | Rationale |
|--------|-----------|------------|-----------|
| Expired listing | 21 days | Exponential | Seller frustration peaks right after expiry, cools fast |
| Price reduction | 14 days | Exponential | Recent cuts indicate active motivation |
| Pre-foreclosure (NOD) | 60 days | Linear | Legal timeline creates extended urgency window |
| Probate filing | 90 days | Linear | Probate process is slow; motivation persists longer |
| Divorce filing | 45 days | Step | Urgency spikes when court orders sale |
| Failed transaction | 14 days | Exponential | Seller emotional window is short |
| Tax delinquency | 120 days | Linear | Slow burn; urgency increases as auction approaches |
| Code violation | 60 days | Step | Deadline-driven; urgency jumps at fine milestones |
| Vacant property | 180 days | Linear | Slow carrying cost accumulation |
| Listing withdrawn | 30 days | Exponential | May relist with new agent; window is narrow |

### Applying Time Decay to Scores

```python
def calculate_urgency_adjusted_score(signal_weight, days_since_event, half_life, decay_type="exponential"):
    """Apply time decay to a signal's base weight."""
    if decay_type == "exponential":
        decay_factor = exponential_decay(days_since_event, half_life)
    elif decay_type == "linear":
        decay_factor = linear_decay(days_since_event, half_life)
    elif decay_type == "step":
        decay_factor = step_decay(days_since_event)

    return signal_weight * decay_factor
```

**Example**: An expired listing (weight = 15) that expired 45 days ago with a 21-day half-life:

```
decay_factor = 0.5^(45/21) = 0.5^2.14 = 0.227
adjusted_score = 15 * 0.227 = 3.4 points (down from 15)
```

### Urgency Escalation (Inverse Decay)

Some signals actually *increase* in urgency over time:

- **Pre-foreclosure**: Urgency increases as the auction date approaches
- **Tax sale deadlines**: Same pattern as foreclosure
- **Seasonal factors**: Listing in spring market has increasing urgency as summer approaches

```python
def escalating_urgency(days_until_deadline, total_window_days):
    """Urgency increases as deadline approaches."""
    days_remaining_pct = days_until_deadline / total_window_days
    if days_remaining_pct <= 0:
        return 1.0  # Past deadline -- maximum urgency
    return 1.0 - days_remaining_pct
```

### Freshness Premium

Apply a bonus for leads where the triggering event happened very recently (within 48 hours). This "breaking news" premium captures the value of being the first agent to reach out:

```python
def freshness_premium(hours_since_event):
    """Bonus multiplier for very fresh signals."""
    if hours_since_event <= 4:
        return 1.5   # First to know
    elif hours_since_event <= 24:
        return 1.3   # Same day
    elif hours_since_event <= 48:
        return 1.15  # Next day
    else:
        return 1.0   # No premium
```

---

## 1.4 Property Value Scoring

### Commission-Opportunity Weighting

Not all leads are equal from a business perspective. A $800K listing generates 3-4x the commission of a $200K listing with similar effort. Property value scoring ensures time is allocated to leads that maximize ROI.

### Value Tier System

```python
def property_value_score(estimated_value, market_median):
    """Score based on property value relative to market median."""
    ratio = estimated_value / market_median

    if ratio >= 3.0:
        return 20    # Luxury segment -- highest commission potential
    elif ratio >= 2.0:
        return 16    # Premium segment
    elif ratio >= 1.5:
        return 12    # Above average
    elif ratio >= 1.0:
        return 8     # Average market
    elif ratio >= 0.7:
        return 5     # Below average
    elif ratio >= 0.5:
        return 3     # Entry-level
    else:
        return 1     # Very low value -- minimal commission
```

### Estimated Commission Calculator

```python
def estimate_commission(sale_price, commission_rate=0.025, split_rate=0.70):
    """
    Estimate take-home commission.

    Args:
        sale_price: Expected sale price
        commission_rate: Listing side commission (2.5% typical post-NAR settlement)
        split_rate: Agent's split with brokerage (70% is common)

    Returns:
        Estimated agent take-home
    """
    gross_commission = sale_price * commission_rate
    agent_take_home = gross_commission * split_rate
    return agent_take_home
```

**Commission Impact by Price Point:**

| Sale Price | Gross Commission (2.5%) | Agent Take-Home (70% split) |
|-----------|------------------------|----------------------------|
| $150,000 | $3,750 | $2,625 |
| $300,000 | $7,500 | $5,250 |
| $500,000 | $12,500 | $8,750 |
| $750,000 | $18,750 | $13,125 |
| $1,000,000 | $25,000 | $17,500 |
| $2,000,000 | $50,000 | $35,000 |

### Equity-Based Scoring

A highly motivated seller with no equity may not be able to sell (underwater). Equity should factor into the score:

```python
def equity_score(estimated_value, mortgage_balance):
    """Score based on available equity."""
    if mortgage_balance is None or mortgage_balance == 0:
        equity_pct = 1.0  # Free and clear
    else:
        equity_pct = (estimated_value - mortgage_balance) / estimated_value

    if equity_pct >= 0.60:
        return 10    # High equity -- easy to sell at almost any price
    elif equity_pct >= 0.40:
        return 8     # Good equity -- healthy room to negotiate
    elif equity_pct >= 0.20:
        return 5     # Moderate equity -- can still sell but less room
    elif equity_pct >= 0.05:
        return 2     # Low equity -- tight margins, may need specific price
    else:
        return 0     # Underwater or near-zero equity -- difficult transaction
```

### ROI-Adjusted Lead Score

Combine motivation score with property value score for an ROI-adjusted ranking:

```python
def roi_adjusted_score(motivation_score, property_value_score, equity_score):
    """
    Final score that balances motivation with business opportunity.

    Motivation is weighted heavier (60%) because a motivated seller at
    any price is better than an unmotivated seller at a high price.
    """
    weighted = (
        motivation_score * 0.60 +
        property_value_score * 0.25 +
        equity_score * 0.15
    )
    return round(weighted, 1)
```

### Price Trajectory Analysis

Track how the asking price has moved over time as an additional motivation indicator:

```python
def price_trajectory_score(original_price, current_price, days_on_market):
    """Score based on price reduction pattern."""
    if original_price <= 0 or current_price <= 0:
        return 0

    total_reduction_pct = (original_price - current_price) / original_price
    reduction_per_day = total_reduction_pct / max(days_on_market, 1)

    # Aggressive price cutting = high motivation
    if total_reduction_pct >= 0.20:
        return 15   # 20%+ total reduction -- very motivated
    elif total_reduction_pct >= 0.15:
        return 12
    elif total_reduction_pct >= 0.10:
        return 9    # 10-15% reduction
    elif total_reduction_pct >= 0.05:
        return 6    # 5-10% reduction
    elif total_reduction_pct > 0:
        return 3    # Minor reduction
    else:
        return 0    # No reduction
```

---

## 1.5 Neighborhood Heat Mapping

### Concept

Not all neighborhoods are equal opportunities. Heat mapping scores geographic areas based on market activity to identify where listing opportunities are most abundant and valuable.

### Heat Score Components

#### Sales Velocity Score

```python
def sales_velocity_score(sales_last_90_days, total_properties_in_area):
    """
    Turnover rate indicates market activity.
    Higher turnover = more opportunity.
    """
    if total_properties_in_area == 0:
        return 0

    turnover_rate = sales_last_90_days / total_properties_in_area
    annualized = turnover_rate * 4  # Annualize from 90-day window

    # National average annual turnover is ~5-6%
    if annualized >= 0.12:
        return 10   # Very active market (12%+ annual turnover)
    elif annualized >= 0.08:
        return 8    # Active market
    elif annualized >= 0.06:
        return 6    # Average market
    elif annualized >= 0.04:
        return 4    # Slow market
    else:
        return 2    # Very slow
```

#### Price Appreciation Score

```python
def appreciation_score(median_price_current, median_price_12mo_ago):
    """Score based on year-over-year price appreciation."""
    if median_price_12mo_ago <= 0:
        return 0

    appreciation_pct = (median_price_current - median_price_12mo_ago) / median_price_12mo_ago

    if appreciation_pct >= 0.15:
        return 10   # Rapid appreciation -- sellers can cash in
    elif appreciation_pct >= 0.10:
        return 8
    elif appreciation_pct >= 0.05:
        return 6    # Healthy appreciation
    elif appreciation_pct >= 0.0:
        return 4    # Flat to slight growth
    elif appreciation_pct >= -0.05:
        return 2    # Slight decline
    else:
        return 0    # Declining market -- harder to sell
```

#### Listing Activity Score

```python
def listing_activity_score(new_listings_30_days, expired_listings_30_days, area_avg_monthly_listings):
    """
    Active listing environment suggests sellers are deciding to list.
    High expired count means opportunity to pick up frustrated sellers.
    """
    if area_avg_monthly_listings <= 0:
        return 0

    listing_ratio = new_listings_30_days / area_avg_monthly_listings
    expired_ratio = expired_listings_30_days / max(new_listings_30_days, 1)

    score = 0

    # Active listing market
    if listing_ratio >= 1.5:
        score += 5   # Lots of new listings -- active market
    elif listing_ratio >= 1.0:
        score += 3
    else:
        score += 1

    # Expired opportunity
    if expired_ratio >= 0.30:
        score += 5   # 30%+ of listings expiring -- lots of frustrated sellers
    elif expired_ratio >= 0.15:
        score += 3
    else:
        score += 1

    return score
```

#### Absorption Rate

The absorption rate measures how many months of inventory exist at the current sales pace:

```python
def absorption_rate_score(active_listings, sales_per_month):
    """
    Months of inventory. Lower = seller's market = easier to sell.
    Higher = buyer's market = harder to sell but more motivated sellers.
    """
    if sales_per_month <= 0:
        return 2  # No sales -- dead market

    months_of_inventory = active_listings / sales_per_month

    # For LISTING agents, a balanced-to-seller's market is ideal
    if months_of_inventory <= 2:
        return 10   # Extreme seller's market -- easy to sell
    elif months_of_inventory <= 4:
        return 8    # Seller's market
    elif months_of_inventory <= 6:
        return 6    # Balanced
    elif months_of_inventory <= 9:
        return 4    # Buyer's market
    else:
        return 2    # Heavy buyer's market -- motivated sellers though
```

### Composite Neighborhood Heat Score

```python
def neighborhood_heat_score(velocity, appreciation, listing_activity, absorption):
    """
    Combine all neighborhood metrics.
    Weight toward velocity and appreciation (most actionable).
    """
    return (
        velocity * 0.30 +
        appreciation * 0.25 +
        listing_activity * 0.25 +
        absorption * 0.20
    )
```

### Geographic Granularity

Define neighborhoods at multiple levels for different use cases:

| Level | Definition | Use Case |
|-------|-----------|----------|
| ZIP Code | 5-digit ZIP | Broad market overview, direct mail targeting |
| ZIP+4 | 9-digit ZIP | More specific neighborhoods |
| Census Tract | Census Bureau tracts | Demographic overlay |
| Subdivision | Named subdivision / HOA | Most precise for MLS analysis |
| Custom Polygon | Agent-defined farm area | Personalized territory management |

### Heat Map Visualization

For practical implementation, store heat scores in a format suitable for map display:

```python
# Data structure for heat map
neighborhood_data = {
    "zip_code": "75201",
    "name": "Uptown Dallas",
    "heat_score": 8.5,
    "velocity_score": 9,
    "appreciation_score": 8,
    "listing_activity_score": 8,
    "absorption_score": 9,
    "median_price": 485000,
    "avg_dom": 22,
    "active_listings": 47,
    "expired_last_90": 12,
    "sales_last_90": 38,
    "center_lat": 32.7940,
    "center_lng": -96.8010,
    "boundary_geojson": "..."  # GeoJSON polygon
}
```

---

## 1.6 Seller Motivation Matrix

### Framework Overview

The Seller Motivation Matrix categorizes leads along two axes:
1. **Motivation Level** (How much do they want/need to sell?)
2. **Timeline Pressure** (How soon do they need to sell?)

This creates four quadrants that dictate different outreach strategies.

### The Four Quadrants

```
                    HIGH MOTIVATION
                         |
        Q2: URGENT       |       Q1: DESPERATE
        "Need to sell    |       "Must sell NOW"
         soon"           |
                         |
  LONG TIMELINE ---------+--------- SHORT TIMELINE
                         |
        Q3: CONSIDERING  |       Q4: OPPORTUNISTIC
        "Might sell      |       "Would sell for the
         someday"        |        right price"
                         |
                    LOW MOTIVATION
```

### Quadrant Definitions and Strategies

#### Q1: Desperate (High Motivation + Short Timeline)
**Profile**: Pre-foreclosure, court-ordered sale, job relocation with deadline, estate liquidation with carrying costs.

| Attribute | Details |
|-----------|---------|
| Typical Signals | NOD/Lis Pendens, divorce decree ordering sale, job transfer with employer deadline, tax sale date scheduled |
| Timeline | 0-60 days |
| Price Sensitivity | Will accept below market to sell quickly |
| Best Approach | Immediate personal contact; present CMA and timeline; emphasize speed |
| Outreach Priority | Contact within 24 hours of signal detection |
| Script Focus | "I can help you resolve this quickly and get the best price possible given your timeline" |
| Commission Risk | Low -- they need an agent; but watch for discount expectations |

#### Q2: Urgent (High Motivation + Longer Timeline)
**Profile**: Expired listings, repeated price cuts, tired landlords, aging owners wanting to downsize.

| Attribute | Details |
|-----------|---------|
| Typical Signals | Expired 30-90 days ago, 3+ price reductions, code violations, tenant problems |
| Timeline | 60-180 days |
| Price Sensitivity | Realistic about market but frustrated with process |
| Best Approach | Consultative -- "here's why it didn't sell and here's my plan" |
| Outreach Priority | Contact within 48-72 hours |
| Script Focus | "I've studied why your home didn't sell last time, and I have a specific plan to change the outcome" |
| Commission Risk | Medium -- they may feel burned by previous agent; prove value |

#### Q3: Considering (Low Motivation + Longer Timeline)
**Profile**: Long-term owners, empty nesters not yet committed, investors considering portfolio changes.

| Attribute | Details |
|-----------|---------|
| Typical Signals | 20+ year ownership, kids moved out (inferred), recent retirement (public pension records), property in trust |
| Timeline | 6+ months |
| Price Sensitivity | Will only sell at or above perceived value |
| Best Approach | Long-term nurture; provide market updates showing appreciation; position as trusted advisor |
| Outreach Priority | Monthly touchpoints (market updates, neighborhood reports) |
| Script Focus | "Your home has appreciated significantly. Here's what it's worth today and what that means for your options" |
| Commission Risk | Low if you build the relationship; high if you rush them |

#### Q4: Opportunistic (Low Motivation + Short Timeline if Price is Right)
**Profile**: Investors, second-home owners, owners who received unsolicited offers, owners in rapidly appreciating areas.

| Attribute | Details |
|-----------|---------|
| Typical Signals | Investor-owned, high appreciation area, property recently paid off, multiple properties owned |
| Timeline | Variable -- will move fast if price is right |
| Price Sensitivity | Price-driven; will only sell at premium |
| Best Approach | Lead with market data showing peak pricing; create urgency around market timing |
| Outreach Priority | Periodic with market trigger events |
| Script Focus | "Properties like yours are commanding premium prices right now. Here's what your neighbors are getting" |
| Commission Risk | Low -- they're business-minded and understand agent value |

### Motivation Scoring by Quadrant

```python
def classify_quadrant(motivation_score, timeline_days):
    """
    Classify a lead into the motivation matrix quadrant.

    Args:
        motivation_score: 0-100 composite motivation score
        timeline_days: Estimated days until they need to act (0 = immediate)

    Returns:
        Quadrant label and recommended strategy
    """
    high_motivation = motivation_score >= 60
    short_timeline = timeline_days <= 90

    if high_motivation and short_timeline:
        return "Q1_DESPERATE", "immediate_personal_outreach"
    elif high_motivation and not short_timeline:
        return "Q2_URGENT", "consultative_outreach_48hrs"
    elif not high_motivation and not short_timeline:
        return "Q3_CONSIDERING", "long_term_nurture"
    else:  # not high_motivation and short_timeline
        return "Q4_OPPORTUNISTIC", "market_data_outreach"
```

### Signal-to-Timeline Mapping

Since we rarely know the exact timeline, estimate it from signals:

| Signal | Estimated Timeline (Days) |
|--------|--------------------------|
| NOD / Pre-foreclosure | 30-120 (varies by state) |
| Tax sale scheduled | Days until auction date |
| Divorce decree filed | 30-90 |
| Probate opened | 90-365 |
| Job relocation listing | 30-90 |
| Expired listing | 0-180 (already past initial timeline) |
| Code violation fine escalating | 30-60 per violation cycle |
| Tired landlord indicators | 90-365 |
| Long-term owner / downsizer | 180-730 |
| Investor portfolio adjustment | 90-365 |

---

## 1.7 Machine Learning Approaches

### Why ML for Lead Scoring

Traditional rule-based scoring (Sections 1.1-1.6) works well and is transparent, but ML models can:
1. Discover non-obvious signal interactions
2. Automatically calibrate weights from outcome data
3. Improve over time as more data accumulates
4. Handle hundreds of features without manual weight assignment

### Recommended Models

#### Logistic Regression (Start Here)

**Why**: Interpretable, fast, works well with limited data, outputs probabilities.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Features per lead
features = [
    'days_since_expired', 'num_price_reductions', 'total_reduction_pct',
    'dom', 'dom_vs_area_median', 'is_pre_foreclosure', 'is_probate',
    'is_divorce', 'is_tax_delinquent', 'is_absentee_owner', 'is_vacant',
    'owner_years', 'estimated_equity_pct', 'property_value',
    'property_value_vs_median', 'area_appreciation_rate',
    'area_absorption_rate', 'area_expired_rate', 'num_code_violations',
    'is_corporate_owned', 'days_since_last_sale_in_area'
]

# Target: did this lead result in a listing within 6 months?
# 1 = yes, 0 = no

model = LogisticRegression(
    C=1.0,
    class_weight='balanced',  # Handle imbalanced classes
    max_iter=1000
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
model.fit(X_train_scaled, y_train)

# Model coefficients show feature importance (like our manual weights)
for feature, coef in zip(features, model.coef_[0]):
    print(f"{feature}: {coef:.3f}")
```

**Minimum data needed**: 200-500 labeled examples (leads that converted vs. didn't).

#### Gradient Boosted Trees (XGBoost / LightGBM)

**Why**: Handles non-linear relationships, missing data, and feature interactions automatically. Best accuracy for tabular data.

```python
import xgboost as xgb

model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    min_child_weight=5,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=10,  # Adjust for class imbalance
    eval_metric='aucpr',
    random_state=42
)

model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=False
)

# Feature importance
importance = model.feature_importances_
for feature, imp in sorted(zip(features, importance), key=lambda x: -x[1]):
    print(f"{feature}: {imp:.4f}")
```

**Minimum data needed**: 500-2,000 labeled examples for good performance.

#### Random Forest

**Why**: Good balance between interpretability and performance. Less prone to overfitting than XGBoost with small datasets.

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=10,
    class_weight='balanced',
    random_state=42
)
```

**Minimum data needed**: 300-1,000 labeled examples.

### Feature Engineering

Raw data must be transformed into useful features. Key transformations:

```python
def engineer_features(lead):
    """Transform raw lead data into model features."""
    features = {}

    # Time-based features
    features['days_since_expired'] = lead.get('days_since_expired', -1)
    features['days_since_last_price_change'] = lead.get('days_since_last_price_change', -1)
    features['is_recently_expired'] = 1 if 0 < features['days_since_expired'] <= 30 else 0

    # Ratio features
    if lead.get('area_median_dom', 0) > 0:
        features['dom_ratio'] = lead['dom'] / lead['area_median_dom']
    else:
        features['dom_ratio'] = 0

    if lead.get('original_price', 0) > 0:
        features['price_reduction_pct'] = (
            (lead['original_price'] - lead['current_price']) / lead['original_price']
        )
    else:
        features['price_reduction_pct'] = 0

    # Categorical encoding
    features['is_distressed'] = 1 if lead.get('is_pre_foreclosure') or lead.get('is_tax_delinquent') else 0
    features['is_life_event'] = 1 if lead.get('is_probate') or lead.get('is_divorce') else 0

    # Interaction features (these capture signal stacking)
    features['expired_and_reduced'] = (
        1 if lead.get('is_expired') and lead.get('num_price_reductions', 0) >= 2 else 0
    )
    features['absentee_and_vacant'] = (
        1 if lead.get('is_absentee') and lead.get('is_vacant') else 0
    )
    features['distressed_and_high_equity'] = (
        1 if features['is_distressed'] and lead.get('equity_pct', 0) > 0.4 else 0
    )

    # Neighborhood context
    features['area_heat_score'] = lead.get('area_heat_score', 5)
    features['area_appreciation_12mo'] = lead.get('area_appreciation_12mo', 0)
    features['area_expired_rate'] = lead.get('area_expired_rate', 0)

    return features
```

### Training Data Sources

The biggest challenge is getting labeled training data. Here is where to find it:

| Source | What You Get | Label Strategy |
|--------|-------------|----------------|
| MLS historical data | Properties that sold, expired, or withdrew over past 2-5 years | Sold within 6 months of signal = positive label |
| Your own outreach records | Which leads you contacted and which converted | Direct conversion tracking |
| Public records + MLS cross-reference | Match NODs, probate, divorce to MLS listings | If property listed within 12 months of filing = positive |
| CRM data | All interactions and outcomes | Pipeline stage progression |
| County recorder | Sale recordings | Cross-reference with your lead lists |

**Label Definition**: The target variable should be clearly defined:

```python
# Recommended label: Did the property list (with any agent) within N months
# of the signal being detected?
#
# For YOUR conversion: Did the property list with YOUR agent within N months?
#
# Start with the broader label (listed with any agent) since you'll have
# more positive examples. Narrow to your-agent-specific once you have enough data.

LABEL_WINDOW_MONTHS = 6  # Adjust based on your market cycle
```

### Model Evaluation

Use metrics appropriate for imbalanced classification (most leads don't convert):

```python
from sklearn.metrics import (
    precision_recall_curve, average_precision_score,
    roc_auc_score, classification_report
)

# Precision-Recall AUC is more informative than ROC-AUC for imbalanced data
pr_auc = average_precision_score(y_test, model.predict_proba(X_test)[:, 1])

# At different threshold levels, what's our precision and recall?
precisions, recalls, thresholds = precision_recall_curve(
    y_test, model.predict_proba(X_test)[:, 1]
)

# Business-oriented metric: At our operating threshold (e.g., top 20% of leads),
# what % of actual conversions do we capture?
top_20_pct_threshold = sorted(model.predict_proba(X_test)[:, 1], reverse=True)[
    int(len(X_test) * 0.20)
]
```

**Target Performance Benchmarks:**

| Metric | Good | Great | Excellent |
|--------|------|-------|-----------|
| ROC-AUC | 0.70 | 0.80 | 0.90+ |
| PR-AUC | 0.30 | 0.45 | 0.60+ |
| Precision @ Top 20% | 0.25 | 0.40 | 0.55+ |
| Recall @ Top 20% | 0.50 | 0.65 | 0.80+ |

### Cold Start Problem

When you have no historical labeled data, use this bootstrap approach:

1. **Phase 1 (Months 1-3)**: Use the rule-based scoring from Sections 1.1-1.6. Track all leads and outcomes.
2. **Phase 2 (Months 3-6)**: With 100+ tracked outcomes, train a logistic regression. Compare its rankings to your rule-based scores. Use whichever performs better on holdout data.
3. **Phase 3 (Months 6-12)**: With 500+ tracked outcomes, train XGBoost. Implement an ensemble that averages rule-based and ML scores.
4. **Phase 4 (12+ months)**: Full ML pipeline with regular retraining. Use rule-based scores as one feature in the ML model.

### Recommended ML Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| Model Training | scikit-learn + XGBoost | Industry standard, well-documented |
| Feature Store | SQLite or PostgreSQL | Simple, local, reliable |
| Model Serving | Python Flask/FastAPI microservice | Lightweight, easy to deploy |
| Model Monitoring | Custom dashboard + MLflow | Track predictions vs. outcomes |
| Experiment Tracking | MLflow (free, open source) | Compare model versions |
| Retraining | Cron job (monthly) | Keep model current with market shifts |

---

# Part 2: Automation Opportunities

## 2.1 MLS Alert Automation

### Overview

MLS systems (Bright MLS, Stellar MLS, NTREIS, CRMLS, etc.) provide search and alert functionality. The key is configuring searches that surface high-probability leads automatically.

### Automated Search Types to Configure

#### Expired Listing Alert
```
Search Criteria:
- Status: Expired, Cancelled, Withdrawn
- Date range: Last 24 hours (run daily)
- Property type: Single Family, Condo, Townhouse
- Price range: [Your target market range]
- Area: [Your farm area ZIP codes or subdivisions]
```

#### Price Reduction Alert
```
Search Criteria:
- Status: Active
- Price change: Reduced in last 7 days
- Price reduction: >= 5% from original
- DOM: >= 30 days
- Area: [Your farm area]
```

#### Back-on-Market Alert
```
Search Criteria:
- Status: Active
- Previous status: Pending/Under Contract
- Status change date: Last 7 days
- Notes: "Back on market", "BOM"
```

#### High DOM Alert
```
Search Criteria:
- Status: Active
- DOM: >= 1.5x area average (e.g., >= 60 days if avg is 40)
- No price change in last 30 days (stale listing -- agent may not be adjusting)
```

#### FSBO-to-MLS Conversion Alert
```
Search Criteria:
- Status: Active
- DOM: 0-7 days (new listing)
- Remarks contain: "previously for sale by owner", "FSBO"
- OR: Property address matches known FSBO sites
```

### MLS API Access (RETS/RESO Web API)

Most MLS systems now offer RESO Web API (replacing the older RETS standard):

- **RESO Web API**: RESTful, OData-based API. Standardized across MLS systems.
- **Access**: Typically requires broker approval and a vendor agreement with the MLS.
- **Cost**: Free for members in some MLS systems; $50-$500/month for vendor access in others.
- **Data refresh**: Real-time or 15-minute intervals depending on the MLS.

```python
# Example RESO Web API query for expired listings
import requests

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

# OData query for recently expired listings
params = {
    '$filter': (
        "StandardStatus eq 'Expired' and "
        "StatusChangeTimestamp ge 2026-02-27T00:00:00Z and "
        "PropertyType eq 'Residential'"
    ),
    '$select': 'ListingId,ListPrice,OriginalListPrice,DaysOnMarket,PostalCode',
    '$top': 200,
    '$orderby': 'StatusChangeTimestamp desc'
}

response = requests.get(
    f'{mls_api_base_url}/Property',
    headers=headers,
    params=params
)

expired_listings = response.json()['value']
```

### Practical MLS Automation Without API Access

If direct API access is unavailable, most MLS platforms support:

1. **Saved Searches with Email Alerts**: Set up 10-20 saved searches covering all signal types. Results arrive via email.
2. **Email Parsing Automation**: Use a script to parse MLS alert emails and extract listing data.
3. **Auto-Prospecting Tools**: Some MLS platforms (e.g., Flexmls, Matrix) have built-in prospecting modules.
4. **MLS Export to CSV**: Schedule manual exports of search results (weekly) and ingest into your scoring system.

```python
# Example: Parse MLS alert email (using imaplib + email)
import imaplib
import email
from bs4 import BeautifulSoup

def parse_mls_alert_email(msg):
    """Extract listing data from MLS alert email HTML."""
    body = msg.get_payload(decode=True).decode()
    soup = BeautifulSoup(body, 'html.parser')

    listings = []
    for row in soup.find_all('tr', class_='listing-row'):
        listing = {
            'mls_number': row.find('td', class_='mls-num').text.strip(),
            'address': row.find('td', class_='address').text.strip(),
            'price': row.find('td', class_='price').text.strip(),
            'status': row.find('td', class_='status').text.strip(),
            'dom': int(row.find('td', class_='dom').text.strip()),
        }
        listings.append(listing)

    return listings
```

---

## 2.2 Public Record Monitoring

### Data Sources to Monitor

#### County Recorder / Clerk of Court

| Record Type | What It Reveals | Check Frequency |
|-------------|----------------|-----------------|
| Lis Pendens (NOD) | Pre-foreclosure initiated | Weekly |
| Probate filings | Death of property owner; estate settlement | Weekly |
| Divorce filings | Marital dissolution; possible property sale | Weekly |
| Tax liens | IRS or state tax liens against property | Monthly |
| Mechanic's liens | Contractor disputes; financial stress | Monthly |
| Deed transfers | Recent sales, quit-claim deeds (ownership changes) | Weekly |
| Mortgage recordings | New mortgages, refinances, HELOCs | Monthly |
| Bankruptcy filings (PACER) | Chapter 7/13 filings | Weekly |

#### County Tax Assessor

| Data Point | Use Case | Check Frequency |
|-----------|----------|-----------------|
| Delinquent tax list | Tax-distressed properties | Monthly (quarterly publication in most counties) |
| Assessment changes | Large increases may motivate sale | Annually |
| Exemption status | Homestead vs. non-homestead identifies non-owner-occupied | Annually |
| Owner mailing address | Identifies absentee owners (mailing != property address) | Quarterly |

#### Code Enforcement

| Data Point | Use Case | Check Frequency |
|-----------|----------|-----------------|
| Open violations | Owner may not want to fix; motivated to sell | Monthly |
| Condemnation notices | Urgent -- property may be demolished | Weekly |
| Repeated violations | Chronically neglected property | Monthly |

### Automation Approaches

#### Option 1: County Website Scraping (Where Legal)

Many county websites publish records online. Some allow automated access; others do not (check terms of service).

```python
# Conceptual example -- actual implementation depends on county website structure
# ALWAYS check the county's terms of service before scraping

import requests
from datetime import datetime, timedelta

def check_county_lis_pendens(county_url, date_from, date_to):
    """
    Check county recorder for new Lis Pendens filings.
    This is a conceptual example -- each county has different systems.
    """
    params = {
        'docType': 'LIS PENDENS',
        'dateFrom': date_from.strftime('%m/%d/%Y'),
        'dateTo': date_to.strftime('%m/%d/%Y'),
        'searchType': 'DocType'
    }

    response = requests.get(county_url, params=params)
    # Parse results (county-specific)
    return parse_county_results(response.text)
```

#### Option 2: Third-Party Data Aggregators

These services aggregate public records across thousands of counties:

| Service | Coverage | Cost | API Available |
|---------|----------|------|---------------|
| ATTOM Data | National, 155M+ properties | $500-$5,000/mo | Yes (REST API) |
| CoreLogic | National, most comprehensive | Enterprise pricing ($2K+/mo) | Yes |
| PropertyRadar | Western states focus | $99-$399/mo | Yes |
| DataTree (First American) | National | Per-report pricing | Yes |
| Reonomy | Commercial focus | $49-$249/mo | Yes |
| BatchData (by BatchService) | National | Pay-per-record ($0.03-$0.15) | Yes |

#### Option 3: PACER for Bankruptcy

Federal bankruptcy filings are available through PACER (Public Access to Court Electronic Records):

- **Cost**: $0.10 per page, $3.00 cap per document
- **API**: PACER has a CM/ECF system; no official REST API but can be automated with login
- **Alternative**: Subscribe to a bankruptcy data aggregator like BankruptcyWatch or CH11Cases

### Building a Public Record Monitoring Pipeline

```python
# Simplified monitoring pipeline architecture

class PublicRecordMonitor:
    def __init__(self, data_sources, check_schedule):
        self.sources = data_sources  # List of data source connectors
        self.schedule = check_schedule
        self.known_records = set()  # Track already-seen records

    def run_check(self):
        """Run all scheduled checks and return new records."""
        new_records = []

        for source in self.sources:
            if self.is_due(source):
                raw_records = source.fetch_new_records()

                for record in raw_records:
                    record_id = record.unique_id()
                    if record_id not in self.known_records:
                        self.known_records.add(record_id)

                        # Enrich with property data
                        enriched = self.enrich_record(record)

                        # Score the lead
                        enriched['lead_score'] = self.score_lead(enriched)

                        new_records.append(enriched)

        # Sort by score descending
        new_records.sort(key=lambda x: x['lead_score'], reverse=True)
        return new_records

    def enrich_record(self, record):
        """Add property details, owner info, and market context."""
        # Cross-reference with property database
        property_data = self.lookup_property(record['address'])
        record.update(property_data)

        # Add market context
        market_data = self.get_market_stats(record['zip_code'])
        record['area_median_price'] = market_data['median_price']
        record['area_appreciation'] = market_data['appreciation_12mo']

        return record
```

---

## 2.3 CRM Integration

### CRM Options for Real Estate Lead Scoring

| CRM | Best For | API | Lead Scoring Built-in | Monthly Cost |
|-----|----------|-----|----------------------|-------------|
| Follow Up Boss | Real estate teams | REST API | Basic (tags, stages) | $69-$499/mo |
| kvCORE (Inside Real Estate) | Brokerages | REST API | Yes (behavioral) | $299-$499/mo |
| LionDesk | Solo agents, small teams | REST API | Basic | $25-$83/mo |
| Wise Agent | Budget-conscious agents | REST API | Basic | $32-$49/mo |
| HubSpot | Tech-savvy agents | REST API (excellent) | Yes (fully custom) | Free-$800/mo |
| Salesforce | Large teams/brokerages | REST API (best) | Yes (Einstein AI) | $25-$300/user/mo |
| Real Geeks | Lead gen + CRM combo | Limited API | Basic | $299+/mo |
| Chime | AI-powered follow-up | REST API | Yes (AI-based) | $300+/mo |

### Integration Architecture

```
[Data Sources] --> [Lead Scoring Engine] --> [CRM API] --> [Agent Dashboard]

Specifically:
  MLS Alerts ----\
  Public Records --+--> Python Scoring --> CRM Contact Created
  County Data ----/     Engine             with:
  ATTOM API ---/                           - Lead score
                                           - Score tier (S/A/B/C/D)
                                           - Motivation quadrant
                                           - Key signals (tags)
                                           - Recommended action
                                           - Auto-assigned drip campaign
```

### Follow Up Boss Integration Example

Follow Up Boss is popular among real estate teams and has a good API:

```python
import requests

FUB_API_KEY = "your_api_key"
FUB_BASE_URL = "https://api.followupboss.com/v1"

def create_lead_in_fub(lead_data, score_data):
    """Create a new lead in Follow Up Boss with scoring data."""

    # Map score tier to FUB stage
    stage_map = {
        'S': 'Hot Lead',
        'A': 'Warm Lead',
        'B': 'Nurture',
        'C': 'Long Term',
        'D': 'Watch List'
    }

    # Build tags from signals
    tags = []
    if lead_data.get('is_expired'):
        tags.append('Expired Listing')
    if lead_data.get('is_pre_foreclosure'):
        tags.append('Pre-Foreclosure')
    if lead_data.get('is_probate'):
        tags.append('Probate')
    if lead_data.get('is_absentee'):
        tags.append('Absentee Owner')
    tags.append(f"Score: {score_data['tier']}")
    tags.append(f"Quadrant: {score_data['quadrant']}")

    payload = {
        "source": "TheLeadEdge",
        "type": "Seller",
        "person": {
            "firstName": lead_data.get('owner_first_name', ''),
            "lastName": lead_data.get('owner_last_name', ''),
            "emails": [{"value": lead_data.get('email', '')}] if lead_data.get('email') else [],
            "phones": [{"value": lead_data.get('phone', '')}] if lead_data.get('phone') else [],
            "addresses": [{
                "street": lead_data.get('property_address', ''),
                "city": lead_data.get('city', ''),
                "state": lead_data.get('state', ''),
                "code": lead_data.get('zip', '')
            }],
            "tags": tags
        },
        "property": {
            "street": lead_data.get('property_address', ''),
            "city": lead_data.get('city', ''),
            "state": lead_data.get('state', ''),
            "code": lead_data.get('zip', ''),
            "type": "Residential",
            "price": lead_data.get('estimated_value', 0)
        },
        "message": build_lead_summary(lead_data, score_data),
        "stage": stage_map.get(score_data['tier'], 'Nurture')
    }

    response = requests.post(
        f"{FUB_BASE_URL}/events",
        json=payload,
        auth=(FUB_API_KEY, '')
    )

    return response.json()

def build_lead_summary(lead_data, score_data):
    """Build a human-readable summary for the CRM note."""
    summary = f"""
LEADFINDER SCORE: {score_data['score']}/100 (Tier: {score_data['tier']})
MOTIVATION QUADRANT: {score_data['quadrant']}

PROPERTY: {lead_data.get('property_address', 'Unknown')}
EST. VALUE: ${lead_data.get('estimated_value', 0):,.0f}
EST. EQUITY: {lead_data.get('equity_pct', 0)*100:.0f}%

KEY SIGNALS:
{chr(10).join(f'  - {s}' for s in score_data.get('active_signals', []))}

RECOMMENDED ACTION: {score_data.get('recommended_action', 'Review and prioritize')}
    """
    return summary.strip()
```

### HubSpot Integration (More Flexible)

HubSpot offers fully custom lead scoring properties:

```python
import hubspot
from hubspot.crm.contacts import SimplePublicObjectInput

client = hubspot.Client.create(access_token="your_token")

def create_hubspot_contact(lead_data, score_data):
    """Create contact in HubSpot with custom scoring properties."""

    # Requires custom properties to be created first in HubSpot:
    # - leadfinder_score (number)
    # - leadfinder_tier (dropdown)
    # - leadfinder_quadrant (dropdown)
    # - leadfinder_signals (multi-checkbox)
    # - property_address (text)
    # - estimated_value (number)
    # - estimated_equity_pct (number)

    properties = {
        "firstname": lead_data.get('owner_first_name', ''),
        "lastname": lead_data.get('owner_last_name', ''),
        "email": lead_data.get('email', ''),
        "phone": lead_data.get('phone', ''),
        "address": lead_data.get('property_address', ''),
        "city": lead_data.get('city', ''),
        "state": lead_data.get('state', ''),
        "zip": lead_data.get('zip', ''),
        "leadfinder_score": score_data['score'],
        "leadfinder_tier": score_data['tier'],
        "leadfinder_quadrant": score_data['quadrant'],
        "leadfinder_signals": ";".join(score_data.get('active_signals', [])),
        "estimated_value": lead_data.get('estimated_value', 0),
        "estimated_equity_pct": lead_data.get('equity_pct', 0),
    }

    contact = SimplePublicObjectInput(properties=properties)
    response = client.crm.contacts.basic_api.create(contact)

    return response
```

---

## 2.4 Automated Outreach Sequences

### Outreach Strategy by Lead Tier

#### Tier S (Score 85-100): Immediate Personal Contact

```
Day 0 (within hours):
  - Phone call attempt #1
  - If no answer: personalized voicemail referencing specific situation
  - Send handwritten note (via service like Handwrytten or Yellow Letters)

Day 1:
  - Phone call attempt #2
  - Personalized email with CMA offer

Day 3:
  - Door knock (if geographically feasible)
  - OR: Send personal text message

Day 5:
  - Phone call attempt #3
  - Send market report for their neighborhood

Day 7:
  - Mail a professional packet (brochure + CMA + cover letter)

Day 14:
  - Phone call attempt #4
  - Downgrade to Tier A sequence if no response
```

#### Tier A (Score 70-84): Priority Outreach

```
Day 0:
  - Phone call attempt
  - Automated personalized email (template with property-specific merge fields)

Day 2:
  - Send direct mail piece (postcard with property photo + CMA teaser)

Day 5:
  - Phone call attempt #2
  - Email #2: neighborhood market update

Day 10:
  - Send second mail piece (handwritten-style card)

Day 15:
  - Phone call attempt #3
  - Email #3: "Your home's value has changed" update

Day 30:
  - Transition to monthly nurture if no response
```

#### Tier B (Score 55-69): Warm Drip Campaign

```
Week 1: Introduction email (who you are, why you're reaching out)
Week 2: Market update for their neighborhood
Week 3: Direct mail postcard
Week 4: Email with recent comparable sales
Week 6: "What's your home worth?" email
Week 8: Market report mail piece
Week 10: Check-in email
Week 12: Phone call (quarterly personal touch)
Then: Monthly email nurture + quarterly mail + quarterly call
```

#### Tier C-D (Score below 55): Long-Term Nurture

```
Monthly: Automated email newsletter (market updates)
Quarterly: Direct mail (just sold cards, market reports)
Bi-annually: Phone call or personal email
Trigger-based: If score increases due to new signal, escalate tier
```

### Automation Tools for Outreach

| Tool | Type | Integration | Cost |
|------|------|-------------|------|
| Mailchimp / ActiveCampaign | Email drip | API / Zapier | $15-$150/mo |
| Yellow Letters Complete | Handwritten-style mail | API available | $1.50-$3.00/piece |
| Handwrytten | Robotic handwritten notes | REST API | $3.25+/card |
| Click2Mail | Printed direct mail | REST API | $0.50-$1.50/piece |
| PostcardMania | Real estate postcards | Batch upload | $0.30-$0.80/piece |
| Slybroadcast | Ringless voicemail | API | $0.02-$0.05/message |
| Launch Control | Text/SMS campaigns | API | $97-$297/mo |
| CallAction | Call tracking + follow-up | Integration | $155+/mo |

### Drip Campaign Automation with Zapier/Make

```
Trigger: New lead created in CRM with tag "Tier_A" or "Tier_B"
  |
  +--> [Zapier/Make Workflow]
  |      |
  |      +--> If Tier S or A:
  |      |      - Create task in CRM: "Call {name} about {address}" (due today)
  |      |      - Send immediate email via ActiveCampaign
  |      |      - Queue handwritten note via Handwrytten API
  |      |
  |      +--> If Tier B:
  |      |      - Enroll in "Warm Seller" drip in ActiveCampaign
  |      |      - Queue postcard via Click2Mail API
  |      |
  |      +--> If Tier C or D:
  |             - Enroll in "Monthly Newsletter" list
  |             - Set reminder for quarterly check-in
```

---

## 2.5 Data Pipeline Architecture

### High-Level Architecture

```
+------------------+     +------------------+     +------------------+
|  DATA SOURCES    |     |  PROCESSING      |     |  OUTPUT          |
|                  |     |                  |     |                  |
| MLS (RESO API)   +--->+                  +---->+ CRM (FUB/HS)    |
| ATTOM API        |    | Ingestion Layer  |     | Lead Reports     |
| County Records   +--->+ (Python ETL)     +---->+ Email Alerts     |
| PropStream       |    |        |         |     | Dashboard        |
| Public Records   +--->+        v         +---->+ Direct Mail API  |
| Zillow/Redfin    |    | Scoring Engine   |     | Agent Mobile App |
|                  |    | (Python + ML)    |     |                  |
+------------------+    |        |         |     +------------------+
                        |        v         |
                        | SQLite/Postgres  |
                        | (Lead Database)  |
                        +------------------+
```

### Detailed Pipeline Components

#### 1. Data Ingestion Layer

```python
# ingestion/base.py
from abc import ABC, abstractmethod
from datetime import datetime
import logging

class DataSource(ABC):
    """Base class for all data source connectors."""

    def __init__(self, name, check_interval_hours=24):
        self.name = name
        self.check_interval = check_interval_hours
        self.last_check = None
        self.logger = logging.getLogger(f"ingestion.{name}")

    @abstractmethod
    def fetch_records(self, since_date=None):
        """Fetch new records from the data source."""
        pass

    @abstractmethod
    def normalize(self, raw_record):
        """Normalize raw record to standard Lead schema."""
        pass

    def is_due(self):
        """Check if this source is due for a refresh."""
        if self.last_check is None:
            return True
        hours_since = (datetime.now() - self.last_check).total_seconds() / 3600
        return hours_since >= self.check_interval


# ingestion/mls_source.py
class MLSSource(DataSource):
    def __init__(self, api_url, api_token):
        super().__init__("MLS", check_interval_hours=1)
        self.api_url = api_url
        self.api_token = api_token

    def fetch_records(self, since_date=None):
        # Fetch expired, price-reduced, back-on-market, high-DOM listings
        queries = [
            self._build_expired_query(since_date),
            self._build_price_reduced_query(since_date),
            self._build_bom_query(since_date),
            self._build_high_dom_query(since_date),
        ]

        all_records = []
        for query in queries:
            records = self._execute_query(query)
            all_records.extend(records)

        return all_records

    def normalize(self, raw_record):
        return {
            'source': 'MLS',
            'property_address': raw_record.get('UnparsedAddress'),
            'city': raw_record.get('City'),
            'state': raw_record.get('StateOrProvince'),
            'zip': raw_record.get('PostalCode'),
            'mls_number': raw_record.get('ListingId'),
            'list_price': raw_record.get('ListPrice'),
            'original_price': raw_record.get('OriginalListPrice'),
            'dom': raw_record.get('DaysOnMarket'),
            'status': raw_record.get('StandardStatus'),
            'property_type': raw_record.get('PropertyType'),
            'bedrooms': raw_record.get('BedroomsTotal'),
            'bathrooms': raw_record.get('BathroomsTotalInteger'),
            'sqft': raw_record.get('LivingArea'),
            'year_built': raw_record.get('YearBuilt'),
            'listing_agent': raw_record.get('ListAgentFullName'),
            'listing_remarks': raw_record.get('PublicRemarks'),
            'status_change_date': raw_record.get('StatusChangeTimestamp'),
            'fetched_at': datetime.now().isoformat(),
        }


# ingestion/attom_source.py
class ATTOMSource(DataSource):
    def __init__(self, api_key):
        super().__init__("ATTOM", check_interval_hours=168)  # Weekly
        self.api_key = api_key
        self.base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"

    def fetch_foreclosures(self, zip_code):
        """Fetch pre-foreclosure records for a ZIP code."""
        headers = {
            'apikey': self.api_key,
            'Accept': 'application/json'
        }

        response = requests.get(
            f"{self.base_url}/attomavm/detail",
            headers=headers,
            params={
                'postalcode': zip_code,
                'orderby': 'SaleSearchDate desc',
                'pagesize': 100
            }
        )
        return response.json()
```

#### 2. Lead Database Schema

```sql
-- Core tables for the lead database

CREATE TABLE properties (
    property_id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL,
    city TEXT,
    state TEXT,
    zip TEXT,
    county TEXT,
    latitude REAL,
    longitude REAL,
    property_type TEXT,
    bedrooms INTEGER,
    bathrooms REAL,
    sqft INTEGER,
    lot_sqft INTEGER,
    year_built INTEGER,
    estimated_value REAL,
    last_sale_price REAL,
    last_sale_date TEXT,
    mortgage_balance REAL,
    equity_pct REAL,
    owner_name TEXT,
    owner_mailing_address TEXT,
    owner_is_absentee BOOLEAN DEFAULT 0,
    owner_is_corporate BOOLEAN DEFAULT 0,
    ownership_years REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(address, city, state, zip)
);

CREATE TABLE signals (
    signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    signal_type TEXT NOT NULL,  -- 'expired', 'pre_foreclosure', 'price_reduction', etc.
    signal_date TEXT NOT NULL,
    signal_details TEXT,  -- JSON with signal-specific data
    source TEXT NOT NULL,  -- 'MLS', 'ATTOM', 'county_records', etc.
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

CREATE TABLE lead_scores (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    raw_score REAL,
    normalized_score REAL,  -- 0-100
    tier TEXT,  -- S, A, B, C, D, F
    quadrant TEXT,  -- Q1_DESPERATE, Q2_URGENT, Q3_CONSIDERING, Q4_OPPORTUNISTIC
    motivation_score REAL,
    urgency_score REAL,
    value_score REAL,
    neighborhood_score REAL,
    active_signals TEXT,  -- JSON array of active signal types
    recommended_action TEXT,
    scored_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

CREATE TABLE outreach_log (
    outreach_id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    outreach_type TEXT,  -- 'phone', 'email', 'mail', 'door_knock', 'text'
    outreach_date TEXT,
    outcome TEXT,  -- 'no_answer', 'voicemail', 'spoke_with', 'appointment_set', 'not_interested'
    notes TEXT,
    crm_synced BOOLEAN DEFAULT 0,
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

CREATE TABLE neighborhoods (
    neighborhood_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    zip_code TEXT,
    heat_score REAL,
    velocity_score REAL,
    appreciation_score REAL,
    listing_activity_score REAL,
    absorption_rate REAL,
    median_price REAL,
    avg_dom REAL,
    active_listings INTEGER,
    sales_last_90 INTEGER,
    expired_last_90 INTEGER,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_properties_zip ON properties(zip);
CREATE INDEX idx_signals_property ON signals(property_id);
CREATE INDEX idx_signals_type_date ON signals(signal_type, signal_date);
CREATE INDEX idx_scores_tier ON lead_scores(tier);
CREATE INDEX idx_scores_normalized ON lead_scores(normalized_score DESC);
```

#### 3. Scoring Engine

```python
# scoring/engine.py

class LeadScoringEngine:
    def __init__(self, db_connection, config=None):
        self.db = db_connection
        self.config = config or DEFAULT_SCORING_CONFIG

    def score_property(self, property_id):
        """Calculate comprehensive lead score for a property."""

        # Gather all data
        property_data = self.db.get_property(property_id)
        signals = self.db.get_active_signals(property_id)
        neighborhood = self.db.get_neighborhood(property_data['zip'])

        # Calculate component scores
        motivation = self._calculate_motivation_score(signals)
        urgency = self._calculate_urgency_score(signals)
        value = self._calculate_value_score(property_data, neighborhood)
        neighborhood_heat = neighborhood.get('heat_score', 5) if neighborhood else 5

        # Composite score
        raw_score = (
            motivation * self.config['motivation_weight'] +    # 0.40
            urgency * self.config['urgency_weight'] +          # 0.25
            value * self.config['value_weight'] +              # 0.20
            neighborhood_heat * self.config['neighborhood_weight']  # 0.15
        )

        # Apply signal stacking bonuses
        raw_score *= self._calculate_stack_bonus(signals)

        # Normalize to 0-100
        normalized = self._normalize(raw_score)

        # Classify
        tier = self._classify_tier(normalized)
        quadrant = self._classify_quadrant(motivation, urgency)

        return {
            'property_id': property_id,
            'raw_score': raw_score,
            'normalized_score': normalized,
            'tier': tier,
            'quadrant': quadrant,
            'motivation_score': motivation,
            'urgency_score': urgency,
            'value_score': value,
            'neighborhood_score': neighborhood_heat,
            'active_signals': [s['signal_type'] for s in signals],
            'recommended_action': self._get_recommended_action(tier, quadrant),
        }

    def batch_score(self, property_ids=None):
        """Score all properties (or a subset) and update the database."""
        if property_ids is None:
            property_ids = self.db.get_all_property_ids_with_signals()

        results = []
        for pid in property_ids:
            score = self.score_property(pid)
            self.db.upsert_score(score)
            results.append(score)

        return sorted(results, key=lambda x: x['normalized_score'], reverse=True)
```

#### 4. Scheduler

```python
# scheduler.py
import schedule
import time

def run_pipeline():
    """Main pipeline orchestration."""

    # 1. Ingest new data
    mls_source.fetch_and_store()
    attom_source.fetch_and_store()
    county_source.fetch_and_store()

    # 2. Deduplicate and merge
    deduplicator.merge_records()

    # 3. Score all leads with new signals
    scoring_engine.batch_score()

    # 4. Sync high-scoring leads to CRM
    crm_sync.push_new_leads(min_tier='B')

    # 5. Generate daily report
    report_generator.create_daily_report()

    # 6. Trigger outreach sequences for new Tier S/A leads
    outreach_engine.trigger_sequences()

# Schedule
schedule.every(1).hours.do(mls_source.fetch_and_store)  # MLS checks hourly
schedule.every().day.at("06:00").do(run_pipeline)        # Full pipeline daily at 6 AM
schedule.every().monday.at("07:00").do(report_generator.create_weekly_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 2.6 API Opportunities

### Real Estate Data APIs

#### ATTOM Data Solutions

**Coverage**: 155M+ properties, 99% of US residential
**Best For**: Property data, pre-foreclosure, tax data, AVM (automated valuation), ownership info

| Endpoint | What You Get |
|----------|-------------|
| Property Detail | Bedrooms, bathrooms, sqft, year built, lot size |
| AVM (Automated Valuation) | Estimated market value, confidence score |
| Sale History | All recorded sales, prices, dates |
| Mortgage Data | Active mortgages, balances, lender |
| Foreclosure Status | NOD, Lis Pendens, auction dates |
| Owner Info | Name, mailing address, ownership length |
| Tax Assessment | Assessed value, tax amount, delinquency |
| Neighborhood Stats | Median values, sales counts, demographics |

**Pricing**: Tiered by volume. Starts ~$250/month for 1,000 records. Enterprise: $2,000-$10,000/month for higher volumes. Pay-per-record options available (~$0.10-$0.50/record depending on data depth).

**API Format**: REST, JSON responses, API key authentication.

```python
# ATTOM API example: Get property detail + AVM
import requests

ATTOM_API_KEY = "your_api_key"

def get_property_detail(address):
    """Fetch property details from ATTOM."""
    headers = {'apikey': ATTOM_API_KEY, 'Accept': 'application/json'}

    response = requests.get(
        "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail",
        headers=headers,
        params={'address1': address, 'address2': ''}
    )
    return response.json()

def get_avm(attom_id):
    """Get automated valuation model estimate."""
    headers = {'apikey': ATTOM_API_KEY, 'Accept': 'application/json'}

    response = requests.get(
        "https://api.gateway.attomdata.com/propertyapi/v1.0.0/attomavm/detail",
        headers=headers,
        params={'attomid': attom_id}
    )
    return response.json()
```

#### CoreLogic

**Coverage**: Most comprehensive US property database (150M+ properties, 99.9% coverage)
**Best For**: Enterprise-grade applications, title data, risk assessment

| Product | Use Case |
|---------|----------|
| Property Data API | Property characteristics, ownership, mortgage |
| Digital Tax Data | Assessment, levy, delinquency |
| Listing Data | MLS data aggregation (broad MLS coverage) |
| ClaimsLytics | Insurance claims history |
| RealAVM | Institutional-grade valuations |

**Pricing**: Enterprise only. Expect $2,000-$20,000/month depending on data products and volume. Requires sales engagement.

**API Format**: REST and batch file delivery.

#### Zillow / Zestimate API (Bridge Interactive)

**Note**: Zillow deprecated its public API in 2021. Current options:

| Option | Details |
|--------|---------|
| Bridge Interactive API | Zillow Group's API platform for industry partners. MLS data, listings, Zestimates. Requires partnership application. |
| Zillow Data (manual) | Zillow publishes free research data (ZHVI, ZORI, etc.) at zillow.com/research/data |
| RapidAPI Zillow alternatives | Third-party APIs that aggregate Zillow-like data. Reliability varies. |

#### Realtor.com / Move API

**Access**: Limited. Realtor.com (owned by Move/News Corp) offers data partnerships for select industry applications. No public API.

**Alternative**: Use Realtor.com's published market statistics and data downloads.

#### Redfin Data

**Free Data**: Redfin publishes extensive market data CSV files for free:
- Housing market data by metro, state, county, ZIP
- Migration data
- New listings, price drops, pending sales
- Download at: redfin.com/news/data-center

**No public API**, but the CSV data is excellent for market analysis.

#### Rentcast API

**Best For**: Rental data, rent estimates, rental comparables
**Pricing**: Free tier (50 calls/month), $40/month (500 calls), $160/month (2,500 calls)

```python
# Rentcast API example
def get_rent_estimate(address):
    headers = {'X-Api-Key': RENTCAST_API_KEY}
    response = requests.get(
        "https://api.rentcast.io/v1/avm/rent/long-term",
        headers=headers,
        params={'address': address}
    )
    return response.json()
```

#### HouseCanary

**Best For**: Property valuations, market analytics, investment analysis
**Pricing**: Per-report or subscription. ~$2-$10 per property report. Enterprise pricing for API access.

#### BatchData (by BatchService)

**Best For**: Bulk skip tracing (finding owner contact info), property data enrichment
**Pricing**: Pay-per-record. Skip tracing: $0.03-$0.15/record. Property data: $0.05-$0.25/record.

```python
# BatchData skip tracing example
def skip_trace(first_name, last_name, address):
    """Find owner contact information."""
    response = requests.post(
        "https://api.batchdata.com/api/v1/person/skip-trace",
        headers={'Authorization': f'Bearer {BATCHDATA_API_KEY}'},
        json={
            "requests": [{
                "firstName": first_name,
                "lastName": last_name,
                "address": {
                    "street": address['street'],
                    "city": address['city'],
                    "state": address['state'],
                    "zip": address['zip']
                }
            }]
        }
    )
    return response.json()
```

#### Google Maps / Places API

**Best For**: Geocoding, neighborhood data, POI analysis, commute scoring
**Pricing**: $200/month free credit. Geocoding: $5/1,000 requests. Places: $17-$32/1,000 requests.

#### Census Bureau API

**Best For**: Demographics, income data, population trends. Free.
**API**: api.census.gov -- No API key required for most endpoints.

### API Cost Summary for a Typical Pipeline

| API | Monthly Use | Estimated Cost |
|-----|-------------|---------------|
| ATTOM (core property + AVM) | 2,000 records/mo | $500-$1,000 |
| BatchData (skip tracing) | 500 leads/mo | $25-$75 |
| Google Maps (geocoding) | 2,000 requests/mo | Free (within credit) |
| Rentcast (rental estimates) | 200 properties/mo | $40 |
| Census Bureau | Unlimited | Free |
| Redfin Data Center | Unlimited downloads | Free |
| **Total** | | **$565-$1,115/month** |

---

## 2.7 Web Scraping Considerations

### Legal Framework

Web scraping legality depends on multiple factors. This is a general guide, not legal advice.

#### What You CAN Generally Scrape

| Source | Legal Basis | Notes |
|--------|------------|-------|
| Public government records | Public record law (FOIA, state equivalents) | County recorder, tax assessor, court filings |
| Published real estate data (Zillow, Redfin public pages) | Legally gray; see hiQ v. LinkedIn (2022) | Respect robots.txt; don't overload servers |
| FSBO listings (Craigslist, Facebook Marketplace) | Generally public data | Craigslist ToS prohibits scraping; Facebook ToS very restrictive |
| Census and government data | Public domain | Use APIs when available (preferred) |
| Real estate auction sites | Varies by site | Most publish data publicly |

#### What You CANNOT Scrape

| Source | Why Not |
|--------|---------|
| MLS data (directly) | Protected by MLS terms of service; DMCA claims; contractual restriction |
| Private databases (CoreLogic, ATTOM) | Copyrighted databases; requires license |
| Facebook profiles | Violates ToS; potential CFAA issues |
| LinkedIn profiles | hiQ v. LinkedIn was narrow; scraping at scale risks CFAA claims |
| Behind-login content | Likely violates CFAA (Computer Fraud and Abuse Act) |
| Data protected by CCPA/GDPR | Personal data privacy regulations |

#### Key Legal Precedents

1. **hiQ Labs v. LinkedIn (2022)**: Scraping publicly accessible data is not a CFAA violation. But this is narrow and doesn't override contracts or copyright.
2. **Craigslist v. 3Taps (2013)**: Scraping after receiving a cease-and-desist can violate CFAA.
3. **CFAA**: Accessing a computer "without authorization" is a federal crime. Bypassing technical barriers (login walls, IP blocks) is risky.

### Safer Alternatives to Scraping

| Instead of Scraping... | Use This Alternative |
|----------------------|---------------------|
| Zillow property data | ATTOM API, Redfin free data downloads |
| County records | County APIs (where available), ATTOM, CoreLogic |
| MLS listings | RESO Web API (authorized access), MLS saved searches |
| FSBO listings | FSBO.com API, ForSaleByOwner.com partnerships, manual monitoring |
| Owner contact info | BatchData skip tracing API, PropStream |
| Foreclosure data | ATTOM foreclosure endpoints, HUD.gov, county court RSS feeds |
| Demographic data | Census Bureau API (free), ACS data, ESRI |

### If You Must Scrape: Best Practices

1. **Always check robots.txt** and respect it
2. **Rate limit** requests (1-2 per second maximum)
3. **Cache aggressively** -- don't re-fetch unchanged data
4. **Identify yourself** with a descriptive User-Agent string
5. **Don't bypass** login walls, CAPTCHAs, or IP blocks
6. **Read the ToS** -- if it prohibits scraping, don't do it
7. **Store only what you need** -- don't create copies of entire databases
8. **Use official APIs** whenever they exist, even if they cost money

### County Record Scraping: A Special Case

County government websites are generally the safest scraping target because:
- The data is public record by law
- Most counties want public access to this data
- Government websites typically don't have restrictive ToS

However, implementation is challenging because:
- Every county has a different website and format
- Many counties use third-party vendors (Tyler Technologies, Granicus, etc.)
- Some counties have older systems that break easily with automated access
- A few counties have started adding anti-bot measures

**Recommendation**: Use ATTOM or CoreLogic for multi-county coverage. Only scrape county sites for hyper-local data not available through aggregators, or to verify/supplement aggregator data.

---

## 2.8 Report Generation

### Daily Lead Report

Generate an automated daily report summarizing new leads and priority actions:

```python
from datetime import datetime, timedelta
import json

class LeadReportGenerator:
    def __init__(self, db, config):
        self.db = db
        self.config = config

    def generate_daily_report(self):
        """Generate daily lead report."""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        report = {
            'date': today,
            'type': 'daily',
            'sections': {}
        }

        # Section 1: New high-priority leads (Tier S and A)
        hot_leads = self.db.query("""
            SELECT p.*, ls.normalized_score, ls.tier, ls.quadrant,
                   ls.active_signals, ls.recommended_action
            FROM lead_scores ls
            JOIN properties p ON ls.property_id = p.property_id
            WHERE ls.tier IN ('S', 'A')
            AND ls.scored_at >= ?
            ORDER BY ls.normalized_score DESC
        """, [yesterday])

        report['sections']['hot_leads'] = {
            'title': 'NEW HOT LEADS (Action Required Today)',
            'count': len(hot_leads),
            'leads': hot_leads
        }

        # Section 2: Score changes (leads that moved up in tier)
        tier_upgrades = self.db.query("""
            SELECT p.address, ls_new.tier as new_tier, ls_old.tier as old_tier,
                   ls_new.normalized_score as new_score
            FROM lead_scores ls_new
            JOIN lead_scores ls_old ON ls_new.property_id = ls_old.property_id
                AND ls_old.scored_at < ls_new.scored_at
            JOIN properties p ON ls_new.property_id = p.property_id
            WHERE ls_new.scored_at >= ?
            AND ls_new.tier < ls_old.tier  -- 'A' < 'B' alphabetically = upgrade
            ORDER BY ls_new.normalized_score DESC
        """, [yesterday])

        report['sections']['tier_upgrades'] = {
            'title': 'SCORE UPGRADES (Leads Getting Hotter)',
            'count': len(tier_upgrades),
            'leads': tier_upgrades
        }

        # Section 3: New signals detected
        new_signals = self.db.query("""
            SELECT p.address, s.signal_type, s.signal_details, s.source
            FROM signals s
            JOIN properties p ON s.property_id = p.property_id
            WHERE s.created_at >= ?
            ORDER BY s.signal_date DESC
        """, [yesterday])

        report['sections']['new_signals'] = {
            'title': 'NEW SIGNALS DETECTED',
            'count': len(new_signals),
            'signals': new_signals
        }

        # Section 4: Pipeline summary
        pipeline = self.db.query("""
            SELECT tier, COUNT(*) as count,
                   AVG(normalized_score) as avg_score,
                   SUM(p.estimated_value) as total_value
            FROM lead_scores ls
            JOIN properties p ON ls.property_id = p.property_id
            WHERE ls.is_active = 1
            GROUP BY tier
            ORDER BY tier
        """)

        report['sections']['pipeline'] = {
            'title': 'PIPELINE SUMMARY',
            'tiers': pipeline
        }

        # Section 5: Neighborhood heat update
        hot_neighborhoods = self.db.query("""
            SELECT name, zip_code, heat_score, median_price,
                   sales_last_90, expired_last_90
            FROM neighborhoods
            WHERE heat_score >= 7
            ORDER BY heat_score DESC
            LIMIT 10
        """)

        report['sections']['hot_neighborhoods'] = {
            'title': 'HOTTEST NEIGHBORHOODS',
            'neighborhoods': hot_neighborhoods
        }

        return report

    def format_email_report(self, report):
        """Format report as HTML email."""
        html = f"""
        <html>
        <head><style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; }}
            .tier-s {{ background: #ff4444; color: white; padding: 2px 8px; border-radius: 4px; }}
            .tier-a {{ background: #ff8800; color: white; padding: 2px 8px; border-radius: 4px; }}
            .tier-b {{ background: #ffcc00; padding: 2px 8px; border-radius: 4px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #f5f5f5; }}
            .section {{ margin: 20px 0; }}
            h2 {{ color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 5px; }}
        </style></head>
        <body>
        <h1>TheLeadEdge Daily Report - {report['date']}</h1>
        """

        # Hot leads section
        hot = report['sections']['hot_leads']
        html += f"<div class='section'><h2>{hot['title']} ({hot['count']})</h2>"
        if hot['leads']:
            html += "<table><tr><th>Address</th><th>Score</th><th>Tier</th>"
            html += "<th>Signals</th><th>Action</th></tr>"
            for lead in hot['leads']:
                tier_class = f"tier-{lead['tier'].lower()}"
                html += f"""<tr>
                    <td>{lead['address']}</td>
                    <td>{lead['normalized_score']:.0f}</td>
                    <td><span class='{tier_class}'>{lead['tier']}</span></td>
                    <td>{lead['active_signals']}</td>
                    <td>{lead['recommended_action']}</td>
                </tr>"""
            html += "</table>"
        else:
            html += "<p>No new hot leads today.</p>"
        html += "</div>"

        html += "</body></html>"
        return html
```

### Weekly Summary Report

```python
def generate_weekly_report(self):
    """Generate comprehensive weekly summary."""
    report = {
        'date_range': f"{self.week_start} to {self.week_end}",
        'type': 'weekly',
        'metrics': {
            'new_leads_total': self._count_new_leads(7),
            'new_leads_by_tier': self._count_new_leads_by_tier(7),
            'leads_contacted': self._count_outreach(7),
            'appointments_set': self._count_outcomes('appointment_set', 7),
            'conversion_rate': self._calculate_conversion_rate(7),
            'total_pipeline_value': self._pipeline_value(),
            'top_10_leads': self._get_top_leads(10),
            'neighborhood_changes': self._neighborhood_heat_changes(7),
            'signal_distribution': self._signal_distribution(7),
            'outreach_effectiveness': self._outreach_stats(7),
        }
    }
    return report
```

### Report Delivery Options

| Method | Tool | Cost | Best For |
|--------|------|------|----------|
| Email (HTML) | SendGrid API / Amazon SES | Free-$15/mo | Daily reports |
| SMS summary | Twilio | $0.0079/msg | Urgent Tier S alerts |
| Slack channel | Slack Webhook API | Free | Team notification |
| PDF attachment | ReportLab (Python) | Free (library) | Weekly formal reports |
| Web dashboard | Streamlit / Dash | Free (self-hosted) | Interactive exploration |
| Google Sheets | Google Sheets API | Free | Shareable, editable |
| Push notification | Pushover / OneSignal | Free-$5/mo | Mobile alerts |

---

# Part 3: Tools & Platforms

## 3.1 Existing Tools in the Market

### PropStream

**What it does**: All-in-one property data and lead generation platform. Widely considered the industry standard for investors and agents doing off-market lead gen.

**Key Features**:
- Nationwide property data (150M+ properties)
- Pre-foreclosure, probate, divorce, tax lien lists
- Skip tracing built in
- Comparables and valuations
- Direct mail integration
- MLS listing data in some markets
- List stacking (combine multiple filters)
- Driving for Dollars mobile app

**Strengths**: Comprehensive data, good UI, list stacking is powerful, mobile app.
**Weaknesses**: Data accuracy varies by county, skip tracing hit rate ~60-70%, no real lead scoring (just filtering).

**Pricing**: $99/month for 10,000 property lookups. Skip tracing: $0.12-$0.15/record extra. Marketing add-ons extra.

### BatchLeads

**What it does**: Lead generation platform focused on distressed properties and skip tracing.

**Key Features**:
- Property data and owner info
- Skip tracing ($0.10-$0.15/record)
- Driving for Dollars
- Direct mail campaigns
- Vacant property detection
- Comps and valuations
- List building with filters

**Strengths**: Good skip tracing rates (~70%+), clean interface, competitive pricing.
**Weaknesses**: Smaller feature set than PropStream, less MLS integration.

**Pricing**: $77/month (Lite), $117/month (Standard), $177/month (Pro). Skip tracing extra.

### REIPro

**What it does**: CRM + lead generation for real estate investors.

**Key Features**:
- Property data and lead lists
- Built-in CRM with deal tracking
- Comps and ARV calculator
- Direct mail campaigns
- Rehab cost estimator
- Automated follow-up sequences

**Strengths**: Good for investors (not just agents), deal analyzer built in, CRM included.
**Weaknesses**: Dated UI, less data depth than PropStream.

**Pricing**: $99/month (Basic), $149/month (Pro).

### DealMachine

**What it does**: Driving for Dollars app that lets you photograph properties and instantly pull owner info.

**Key Features**:
- Mobile app: photograph a property -> get owner info instantly
- Skip tracing integration
- Direct mail from app
- Route tracking (map your driving routes)
- Team management
- Postcard and letter sending

**Strengths**: Best-in-class Driving for Dollars experience, very easy to use, fast owner lookup.
**Weaknesses**: Limited to mobile workflow, not a full data platform, expensive per-record costs.

**Pricing**: $49/month (Starter, 500 properties), $99/month (Pro, 2,000 properties). Skip tracing: $0.15/record.

### PropertyRadar

**What it does**: Property data and analytics platform, particularly strong in Western US states.

**Key Features**:
- Deep property data (ownership, mortgage, tax, transfer history)
- Pre-foreclosure tracking
- List building with 200+ filters
- Market analytics and heat maps
- Direct mail integration
- Trigger alerts (get notified when a property matches criteria)

**Strengths**: Excellent data depth, great filtering, strong in CA/AZ/NV/OR/WA. Trigger alerts are true automation.
**Weaknesses**: Limited coverage east of the Mississippi (though expanding), higher price point.

**Pricing**: $99/month (Essentials), $199/month (Professional), $399/month (Enterprise).

### Realeflow

**What it does**: End-to-end real estate investing platform.

**Key Features**:
- Lead generation and property data
- CRM and deal management
- Marketing automation (mail, email, SMS)
- Rehab estimator
- Contract generation
- Website builder

**Strengths**: All-in-one for investors, good marketing tools.
**Weaknesses**: Jack of all trades; data quality not as strong as PropStream.

**Pricing**: $99/month.

### InvestorLift

**What it does**: Wholesale deal distribution platform. Not lead gen, but useful for wholesaler-adjacent work.

**Pricing**: $147/month+.

### ListSource (by CoreLogic)

**What it does**: Mailing list creation from CoreLogic's database.

**Key Features**:
- CoreLogic data (highest quality in industry)
- Demographic and property filters
- Pre-built list categories (pre-foreclosure, absentee, etc.)
- Download as CSV for mail campaigns

**Pricing**: Pay-per-record. Typically $0.05-$0.15/record.

---

## 3.2 Pricing and Capabilities Comparison

### Feature Comparison Matrix

| Feature | PropStream | BatchLeads | REIPro | DealMachine | PropertyRadar |
|---------|-----------|------------|--------|-------------|---------------|
| **Monthly Cost** | $99 | $77-$177 | $99-$149 | $49-$99 | $99-$399 |
| **Property Data** | Excellent | Good | Good | Basic | Excellent |
| **Pre-Foreclosure** | Yes | Yes | Yes | No | Yes |
| **Probate Data** | Yes | Yes | Limited | No | Yes |
| **Divorce Data** | Yes | Limited | No | No | Limited |
| **Tax Liens** | Yes | Yes | Yes | No | Yes |
| **Vacant Detection** | Yes | Yes | No | Yes (manual) | Limited |
| **Skip Tracing** | $0.12-0.15 | $0.10-0.15 | Included | $0.15 | No (integrate) |
| **Built-in CRM** | No | No | Yes | Basic | No |
| **Direct Mail** | Yes | Yes | Yes | Yes | Yes |
| **MLS Data** | Some markets | No | No | No | No |
| **List Stacking** | Excellent | Good | Basic | No | Excellent |
| **Lead Scoring** | No | No | No | No | No |
| **Automation/Alerts** | Basic | Basic | Basic | Basic | Good (triggers) |
| **API Access** | No | Yes | No | No | No |
| **Mobile App** | Yes | Yes | No | Yes (core) | Yes |
| **Coverage** | National | National | National | National | Western US expanding |

### Cost Analysis: Tool Stacking

A typical agent/investor might use multiple tools:

| Stack Option | Tools | Monthly Cost | Best For |
|-------------|-------|-------------|----------|
| Budget | PropStream alone | $99 | Solo agent, starting out |
| Standard | PropStream + DealMachine | $148-$198 | Active prospecting agent |
| Professional | PropStream + Follow Up Boss + BatchLeads | $245-$375 | Team with active outreach |
| Enterprise | PropertyRadar + HubSpot + Custom pipeline | $300-$600+ | Data-driven team operation |

---

## 3.3 Gaps a Custom Solution Could Fill

### Critical Gap 1: True Lead Scoring

**The problem**: None of the existing tools offer real lead scoring. They provide data and filtering, but the agent must mentally evaluate each lead. There is no composite score, no signal weighting, no time decay, and no prioritization.

**Custom solution opportunity**: Build the scoring engine described in Part 1. Ingest data from PropStream exports or ATTOM API, apply multi-signal scoring, and output a prioritized, scored lead list.

**Value**: Instead of reviewing 200 expired listings manually, the agent gets a ranked list where #1 is a pre-foreclosure, expired, absentee-owned property with 3 price reductions -- and #200 is a mildly aged listing with no other signals. This saves hours per day.

### Critical Gap 2: Cross-Source Signal Stacking

**The problem**: Existing tools keep data in silos. PropStream shows you pre-foreclosures OR expired listings OR absentee owners. Finding properties that match MULTIPLE criteria requires manual list stacking, and it doesn't combine MLS data with public records intelligently.

**Custom solution opportunity**: Build a data pipeline that ingests from MLS (via RESO API or saved search exports), public record APIs (ATTOM), and county records. Match properties across sources and identify convergence of signals.

**Value**: Discover leads that no single-source tool would surface. Example: a property where the owner filed for divorce (court records) + is 2 months behind on taxes (county assessor) + had a listing expire 45 days ago (MLS) + lives in another state (ATTOM). Each signal alone is common; the combination is gold.

### Critical Gap 3: Time-Aware Automation

**The problem**: Existing tools are snapshot-based. You query, get results, and then manually check back later. There is no concept of "this lead was warm last week but is now cooling" or "this property just had its third price reduction -- urgency just increased."

**Custom solution opportunity**: Build the urgency scoring and time-decay system from Section 1.3. Run it on a schedule. Alert the agent when leads move between tiers.

**Value**: Automated escalation and de-escalation. The agent gets a push notification when a Tier B lead becomes Tier A because a new signal was detected, rather than discovering it manually days later.

### Critical Gap 4: Intelligent Outreach Orchestration

**The problem**: CRMs can do drip campaigns, but they don't adapt based on lead score changes. A lead that suddenly became hot still gets the same generic weekly email.

**Custom solution opportunity**: Connect the scoring engine to the CRM. When a lead's score changes, automatically adjust the outreach sequence. Move hot leads to immediate personal follow-up. Move cooling leads to low-touch nurture.

**Value**: The right message at the right time. No hot leads slip through the cracks; no effort wasted on cold leads.

### Critical Gap 5: Market Timing Intelligence

**The problem**: Existing tools show current data but don't analyze trends. Is this neighborhood getting hotter or cooling? Are expired listings increasing in this ZIP code (suggesting a market shift)?

**Custom solution opportunity**: Build the neighborhood heat mapping from Section 1.5 with trend analysis. Track heat scores over time and alert when patterns change.

**Value**: Farm area selection backed by data. Instead of guessing which neighborhoods to focus on, the system identifies emerging opportunities.

### Critical Gap 6: Consolidated Dashboard

**The problem**: Agents juggle 3-5 tools and tabs. MLS in one window, PropStream in another, CRM in a third, county records in a fourth.

**Custom solution opportunity**: Build a single dashboard (Streamlit, Dash, or web app) that shows:
- Today's priority leads (scored and ranked)
- Pipeline summary by tier
- Neighborhood heat map
- Outreach tasks due today
- New signals detected
- Performance metrics (conversion rates)

**Value**: One screen that tells the agent exactly what to do today.

### Build vs. Buy Recommendation

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| Property data | Buy (ATTOM API or PropStream exports) | Impossible to replicate; expensive to build |
| Skip tracing | Buy (BatchData API) | Specialized service; not worth building |
| Lead scoring engine | Build (custom Python) | This IS the competitive advantage; no good tool exists |
| CRM | Buy (Follow Up Boss or HubSpot) | Mature products; not worth reinventing |
| Outreach automation | Buy (CRM + mail service) | Commoditized; use existing tools |
| Dashboard | Build (Streamlit / custom web) | Customization needed; nothing fits exactly |
| Data pipeline | Build (Python ETL + SQLite) | Glue between bought components; must be custom |
| ML model | Build (scikit-learn + XGBoost) | Proprietary advantage; trained on your data |
| Neighborhood analytics | Build (custom Python) | Unique analysis not available in any tool |
| Report generation | Build (Python + email) | Simple to build; customization matters |

---

## 3.4 Free vs Paid Data Sources

### Free Data Sources

| Source | Data Available | Format | Update Frequency | URL |
|--------|---------------|--------|-----------------|-----|
| **Redfin Data Center** | Market stats by ZIP/metro, price drops, new listings, inventory, migration | CSV download | Weekly | redfin.com/news/data-center |
| **Zillow Research Data** | ZHVI (home values), ZORI (rents), inventory, price cuts, new listings by ZIP | CSV download | Monthly | zillow.com/research/data |
| **Census Bureau (ACS)** | Demographics, income, housing characteristics, population | API (JSON) / CSV | Annual (ACS), Decennial | api.census.gov |
| **HUD.gov** | FHA foreclosures, fair market rents, housing statistics | CSV / API | Varies | hud.gov/program_offices |
| **FHFA House Price Index** | Home price appreciation by metro, state, ZIP | CSV / API | Quarterly | fhfa.gov/DataTools |
| **FRED (Federal Reserve)** | Mortgage rates, housing starts, economic indicators | API (JSON) | Daily-Monthly | fred.stlouisfed.org |
| **County Recorder Websites** | Deed transfers, liens, NODs, mortgage recordings | HTML (varies) | Daily-Weekly | (county-specific) |
| **County Tax Assessor** | Assessed values, tax status, owner info, exemptions | HTML / CSV (varies) | Annual + updates | (county-specific) |
| **State Court Records** | Probate, divorce, bankruptcy, civil filings | HTML (varies) | Daily | (state-specific) |
| **USPS NCOA** | National Change of Address (requires licensing) | Batch file | Monthly | Requires USPS agreement |
| **SEC EDGAR** | Corporate filings (useful for REIT/institutional sellers) | API / HTML | Daily | sec.gov/edgar |
| **Google Maps Platform** | Geocoding, Street View (limited free tier) | API | Real-time | $200/mo free credit |
| **OpenStreetMap** | Geographic data, POIs, boundaries | API / bulk download | Real-time | openstreetmap.org |

### Paid Data Sources (Tiered by Cost)

#### Low Cost ($0-$100/month)

| Source | Cost | What You Get |
|--------|------|-------------|
| Rentcast | $0-$160/mo | Rent estimates, rental comps |
| ListSource (CoreLogic) | Pay-per-record ($0.05-$0.15) | Mailing lists with property + owner data |
| BatchData | Pay-per-record ($0.03-$0.15) | Skip tracing, property data |
| PropStream | $99/mo | Comprehensive property data + tools |
| BatchLeads | $77-$177/mo | Lead lists + skip tracing |
| DealMachine | $49-$99/mo | Driving for Dollars + owner lookup |

#### Medium Cost ($100-$500/month)

| Source | Cost | What You Get |
|--------|------|-------------|
| PropertyRadar | $99-$399/mo | Deep property data, triggers, Western US focus |
| ATTOM Data API | $250-$1,000/mo | National property data via API |
| REIPro | $99-$149/mo | Property data + CRM + deal analysis |
| HouseCanary | Varies ($2-$10/report) | Valuations, market analytics |

#### High Cost ($500+/month)

| Source | Cost | What You Get |
|--------|------|-------------|
| CoreLogic | $2,000-$20,000/mo | Most comprehensive property database |
| ATTOM Enterprise | $5,000-$10,000/mo | High-volume API access |
| Black Knight (ICE) | Enterprise pricing | MLS aggregation, property data, analytics |
| CoStar | $300-$1,000+/mo | Commercial real estate data (if needed) |

### Recommended Stack by Budget

#### Bootstrapper ($0-$50/month)
- Redfin Data Center (free) for market analysis
- Zillow Research Data (free) for home values and trends
- Census API (free) for demographics
- County websites (free) for public records (manual process)
- Google Sheets for tracking
- Total: $0/month + time investment

#### Starter ($100-$200/month)
- PropStream ($99) for property data and list building
- Redfin + Zillow free data for market context
- County websites for supplemental records
- Free CRM (HubSpot free tier)
- Total: ~$99/month

#### Professional ($200-$500/month)
- ATTOM API ($250-$500) for property data pipeline
- BatchData (pay-per-record) for skip tracing
- Follow Up Boss ($69) for CRM
- Redfin + Zillow + Census for market data
- Custom scoring engine (build it -- free)
- Total: ~$320-$570/month

#### Advanced ($500-$1,500/month)
- ATTOM API ($500-$1,000) for comprehensive data
- BatchData ($50-$150) for skip tracing at volume
- Follow Up Boss ($149) for team CRM
- PropertyRadar ($199) for trigger-based alerts
- Custom pipeline + scoring + dashboard (build cost, not subscription)
- SendGrid ($15) for report emails
- Total: ~$915-$1,515/month

---

## Appendix A: Quick-Start Implementation Plan

### Phase 1: Foundation (Week 1-2)
1. Set up the SQLite database with the schema from Section 2.5
2. Build MLS alert saved searches (Section 2.1) -- 10-15 searches covering all signal types
3. Sign up for ATTOM API trial or PropStream
4. Build the basic additive scoring model (Section 1.1)
5. Create a simple daily report script

### Phase 2: Data Pipeline (Week 3-4)
1. Build data ingestion from MLS exports (CSV parsing)
2. Add ATTOM API integration for property enrichment
3. Implement time-decay urgency scoring (Section 1.3)
4. Build the first version of the neighborhood heat map (Section 1.5)
5. Set up scheduled pipeline execution

### Phase 3: CRM + Outreach (Week 5-6)
1. Connect scoring engine to CRM via API (Section 2.3)
2. Configure drip campaigns by tier (Section 2.4)
3. Set up automated email reports (Section 2.8)
4. Build a basic Streamlit dashboard

### Phase 4: Machine Learning (Month 3-6)
1. Accumulate labeled training data (Section 1.7)
2. Train initial logistic regression model
3. A/B test ML scores vs. rule-based scores
4. Iterate and improve

### Phase 5: Optimization (Ongoing)
1. Calibrate weights based on conversion data
2. Add new data sources as they become available
3. Refine outreach sequences based on response rates
4. Expand geographic coverage
5. Build advanced dashboard features

---

## Appendix B: Key Metrics to Track

| Metric | Definition | Target |
|--------|-----------|--------|
| Lead Volume | New scored leads per week | 50-200 depending on market size |
| Tier S/A Rate | % of leads scoring Tier S or A | 5-15% |
| Contact Rate | % of Tier S/A leads contacted within SLA | 90%+ |
| Response Rate | % of contacted leads that respond | 5-15% for cold, 20-40% for warm |
| Appointment Rate | % of responses that become appointments | 30-50% |
| Listing Rate | % of appointments that become listings | 40-60% |
| Close Rate | % of listings that close | 85-95% (market dependent) |
| Revenue per Lead | Average commission / total leads scored | Track and maximize |
| Cost per Lead | Total tool costs / leads generated | Track and minimize |
| Score Accuracy | Correlation between score and conversion | Improve over time |
| Time to Contact | Hours between signal detection and first outreach | < 24 hrs for Tier S |
| Signal Hit Rate | % of each signal type that converts | Use to recalibrate weights |

---

*This document is a living research reference. Update as new data sources emerge, tools change pricing, or conversion data allows weight recalibration.*
