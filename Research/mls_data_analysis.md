# MLS Data Mining Strategies for High-Probability Lead Generation

> **Purpose**: Actionable playbook for a licensed Realtor with MLS access to identify motivated sellers and buyers through systematic data analysis and pattern recognition.
>
> **Philosophy**: Every MLS status change, price adjustment, and timeline anomaly tells a story. This guide teaches you to read those stories before your competitors do.

---

## Table of Contents

1. [Expired Listings](#1-expired-listings)
2. [Price Reduction Patterns](#2-price-reduction-patterns)
3. [Days on Market (DOM) Analysis](#3-days-on-market-dom-analysis)
4. [Withdrawn & Relisted Properties](#4-withdrawn--relisted-properties)
5. [FSBO Conversions](#5-fsbo-conversions)
6. [Pocket Listings & Coming Soon](#6-pocket-listings--coming-soon)
7. [Rental to Sale Conversions](#7-rental-to-sale-conversions)
8. [MLS Status History Mining](#8-mls-status-history-mining)
9. [Agent Activity Patterns](#9-agent-activity-patterns)
10. [Comparable Sales Gaps](#10-comparable-sales-gaps)
11. [Building a Daily Workflow](#11-building-a-daily-workflow)
12. [Lead Scoring Matrix](#12-lead-scoring-matrix)

---

## 1. Expired Listings

Expired listings represent sellers who **wanted to sell, committed to the process, and failed**. Their motivation has been tested and proven -- they did not withdraw voluntarily. Something went wrong, and they are now sitting without representation and often frustrated.

### What Data to Look For

- **Status = Expired** in your MLS (some systems use "E", "EXP", or "Expired")
- **Original list date** -- how long was it on the market before expiring?
- **List price vs. assessed value** -- was it priced unrealistically?
- **Number of price reductions before expiration** -- did the seller resist adjusting?
- **Previous listing agent's production volume** -- low-production agent may indicate poor marketing
- **Property condition notes** -- "as-is", "investor special", deferred maintenance keywords
- **Listing photos quality** -- poor photos on expired = fixable problem = opportunity
- **Tax records** -- cross-reference for owner-occupied vs. absentee (absentee owners who expire are extremely motivated)

### How to Filter/Search in MLS

```
Status: Expired
Date Range: Last 1-30 days (primary), 31-90 days (secondary)
Property Type: [Your target -- SFR, Condo, Multi-family]
Price Range: [Your farm area range]
Geographic Area: [Your farm zip codes or neighborhoods]
```

**Advanced filters to add:**
- Exclude properties that have since relisted (Status History check)
- Sort by expiration date (newest first for urgency)
- Filter by DOM > 90 before expiration (indicates systemic pricing or condition problem you can solve)
- Filter by number of price changes >= 2 (seller who adjusted but still could not sell = likely to listen to a new strategy)

### What Makes This a High-Probability Lead

**Tier 1 -- Best Expired Leads (contact same day):**
- Owner-occupied with equity (they live there, they need to sell, they have room to negotiate)
- Expired after 90+ DOM with 2+ price reductions (seller tried everything with the last agent)
- Property in a neighborhood with strong recent comps (the house should have sold -- the agent failed, not the market)
- No relisting within 7 days of expiration (they have not been picked up yet)

**Tier 2 -- Strong Expired Leads (contact within 3 days):**
- Absentee owner with expired listing (tired landlord or inherited property)
- Expired with zero price reductions (agent may not have given honest pricing guidance -- you can)
- Properties where the listing agent had fewer than 10 transactions in the last 12 months

**Tier 3 -- Worth Monitoring:**
- Luxury or unique properties that expired (smaller buyer pool, longer timeline, but high commission)
- Properties that expired with offers that fell through (check MLS remarks for "back on market" history)

### Suggested Approach/Timing

| Timeframe | Action |
|-----------|--------|
| **Day 0** (expiration date) | Pull the list at 12:01 AM or as soon as MLS updates. Every agent in town gets this list. Speed wins. |
| **Day 0, morning** | Send a personalized CMA (Comparative Market Analysis) by mail or email. Do NOT lead with "I saw your listing expired." Lead with value: "I prepared a market analysis for your home at [address] that shows current buyer activity in your neighborhood." |
| **Day 1-3** | Phone call. Acknowledge their frustration without bashing the previous agent. Ask what they feel went wrong. Listen more than you talk. |
| **Day 7** | If no response, send a "neighborhood activity update" -- recent sales near them, pending sales, new listings. Show you are actively working in their area. |
| **Day 14** | Second call attempt or door knock with a printed CMA and a marketing plan specific to their home. |
| **Day 30-90** | Monthly check-in mailer. Many expired sellers take 30-90 days to recover emotionally and re-engage. |

### Estimated Conversion Rate

- **Industry average**: 3-5% of expired listings convert to a new listing with consistent follow-up
- **With same-day contact + CMA**: 8-12%
- **With systematic 90-day follow-up sequence**: 15-20% over the full period
- **Top producers report**: 1 in 5 expired listings they contact will eventually list with them if they maintain consistent (non-aggressive) follow-up over 6 months

### Pro Tips

- Set up a **daily auto-email/hot sheet** in your MLS for new expired listings in your farm area. This should hit your inbox before you start your day.
- Build a spreadsheet tracking every expired listing you contact: date of expiration, contact attempts, owner response, eventual outcome. Patterns will emerge over 90 days about what messaging works.
- The **#1 mistake** agents make with expireds: bashing the previous agent. Never do it. The seller chose that agent. Bashing them insults the seller's judgment. Instead: "Every home has its timeline. Let me show you what I would do differently with my marketing plan."

---

## 2. Price Reduction Patterns

Price reductions are **real-time motivation signals**. A seller who reduces their price is telling the market: "I need this to move." Multiple reductions tell a louder story: "I am getting increasingly desperate."

### What Data to Look For

- **Number of price reductions** on a single listing (2+ is a strong signal, 3+ is urgent)
- **Magnitude of reductions** -- are they meaningful (3-5%+) or token ($1,000 on a $500K home)?
- **Frequency of reductions** -- weekly reductions signal panic; monthly reductions signal a methodical agent
- **Cumulative reduction percentage** -- total drop from original list price (10%+ cumulative = serious motivation)
- **Price reduction relative to comps** -- is the current price now below recent comps? (Seller may be ahead of the market decline or truly desperate)
- **Time between listing and first reduction** -- reductions within 14 days suggest the agent overpriced knowingly to win the listing
- **Listing remarks changes** -- look for language shifts: "motivated seller", "bring all offers", "price improvement" appearing after reductions

### How to Filter/Search in MLS

```
Status: Active
Price Change: Yes (within last 7/14/30 days)
Number of Price Changes: >= 2 (if your MLS supports this filter)
Geographic Area: [Your farm]
DOM: > 30 (combine with price reduction for maximum motivation signal)
```

**Manual analysis approach (when filters are limited):**
1. Pull all active listings in your farm area with DOM > 21
2. Click into each listing and review Price History tab
3. Flag any listing with 2+ reductions
4. Create a separate tracking spreadsheet with columns: Address, Original Price, Current Price, Total % Reduced, Number of Reductions, DOM, Agent

### Distinguishing Desperate vs. Strategic Reductions

**Desperate Reductions (High-Probability Leads):**
- Multiple small reductions in rapid succession (weekly or bi-weekly)
- Reductions accompanied by listing remark changes adding urgency language
- Reduction that brings price below assessed value
- Reduction pattern accelerating (first drop after 30 days, second after 14, third after 7)
- Agent concessions appearing: "seller to pay closing costs", "home warranty included"
- Listing photos updated or virtual tour added after reductions (throwing everything at the wall)

**Strategic Reductions (Lower Priority, Still Worth Monitoring):**
- Single planned reduction at the 30-day mark (common agent strategy)
- Reduction to just below a search threshold ($505K to $499K -- capturing $400-500K searchers)
- Seasonal adjustment (e.g., reducing in November to attract winter buyers)
- Reduction paired with a listing refresh (new photos, updated description -- agent is managing the process)

### What Makes This a High-Probability Lead

This strategy is about finding **active listings where the current agent is failing** and either:
- **A)** Positioning yourself to pick up the listing when it expires (build the relationship now)
- **B)** Bringing a buyer to the property (the seller's agent will be highly cooperative)
- **C)** Identifying a pattern in a neighborhood that signals broader opportunity

**Highest probability signals:**
- 3+ reductions totaling 10%+ cumulative drop
- DOM > 60 with ongoing reductions
- Property in a neighborhood where similar homes sold within 30 days (this specific home has a problem -- price, condition, or agent marketing)
- Owner is absentee (check tax records) and reducing aggressively (wants out of the investment)

### Suggested Approach/Timing

**If you have a buyer:**
- Contact the listing agent immediately after a 3rd+ reduction. Say: "I have a qualified buyer interested in [neighborhood]. Your listing at [address] could be a fit. What is the seller's current motivation level?" Listing agents with desperate sellers will tell you everything.

**If you are prospecting for a listing (future expired):**
- Track the listing. When it expires (and with 3+ reductions, it very likely will), you already know the property's full history and can present a detailed analysis on Day 0.
- Before expiration, you can also send the homeowner a "neighborhood market report" mailer that includes recent sold comps. This is not soliciting their listing (they are under contract with another agent) -- it is providing market information, which is generally permissible.

**Timeline for active reductions:**
- After 2nd reduction: Add to your watch list
- After 3rd reduction: Research the property fully (comps, tax records, owner info)
- After 4th reduction or expiration: Initiate direct contact

### Estimated Conversion Rate

- Listings with 3+ price reductions have a **35-40% chance of expiring** rather than selling
- If you contact them on expiration day with a pre-built CMA: **10-15% listing conversion rate**
- If you bring a buyer to a 3+ reduction listing: **high showing-to-offer ratio** -- these sellers are ready to negotiate

---

## 3. Days on Market (DOM) Analysis

DOM is the single most visible metric of listing distress. Every day on market costs the seller money (mortgage, taxes, insurance, opportunity cost) and erodes their negotiating position. Understanding DOM thresholds lets you time your outreach for maximum effectiveness.

### What Data to Look For

- **Cumulative DOM (CDOM)** -- total days across all listing periods (some MLS systems track this separately from current-period DOM; always use CDOM when available)
- **DOM relative to neighborhood average** -- a listing at 60 DOM in a neighborhood averaging 15 DOM is in trouble
- **DOM by price point** -- luxury homes naturally have higher DOM; what matters is DOM relative to the cohort
- **DOM combined with showing activity** (if your MLS tracks showing requests through ShowingTime or similar)
- **DOM and open house frequency** -- multiple open houses with high DOM = agent trying hard, market not responding
- **DOM reset attempts** -- check if the property was withdrawn and relisted to reset the DOM counter (covered in Section 4)

### How to Filter/Search in MLS

```
Status: Active
DOM: > [threshold based on your market -- see below]
Geographic Area: [Your farm]
Price Range: [Your target segment]
```

**Market-specific DOM thresholds:**

| Market Type | "Getting Stale" | "Distressed" | "Severely Overpriced" |
|-------------|----------------|--------------|----------------------|
| Hot market (avg DOM < 15) | 30+ days | 60+ days | 90+ days |
| Normal market (avg DOM 30-45) | 60+ days | 90+ days | 150+ days |
| Slow market (avg DOM 60+) | 90+ days | 150+ days | 240+ days |

**To determine your market's average DOM:**
1. Pull all sold listings in your farm area for the last 90 days
2. Calculate the median DOM (not average -- median eliminates outlier distortion)
3. Any active listing at 2x the median DOM is a lead; 3x is a strong lead

### Sweet Spots for Outreach

**The DOM Psychology Timeline:**

| DOM Range | Seller Psychology | Outreach Strategy |
|-----------|-------------------|-------------------|
| **0-14 days** | Optimistic, not yet concerned | Not a lead yet. Monitor only. |
| **15-30 days** | Starting to wonder. First doubts. | If in a hot market, send a "market conditions" mailer. |
| **30-45 days** | Concerned. Asking their agent "what's wrong?" | Begin tracking. Research the property and owner. |
| **45-60 days** | Frustrated. Considering a price reduction. | If they have not reduced yet, they are about to. Watch for the reduction as a trigger. |
| **60-90 days** | Angry or defeated. Blaming the agent. Open to alternatives. | **Primary outreach window.** If the listing expires in this range, contact immediately. If still active, prepare your CMA for the eventual expiration. |
| **90-120 days** | Emotionally exhausted. Some sellers pull the listing. Others become "resigned" -- willing to take almost any reasonable offer. | **Bring a buyer.** Or prepare a detailed "what I would do differently" presentation. |
| **120-180 days** | Many sellers have detached emotionally. The listing is "furniture" -- it is just there. They may have already moved or rented. | **Second wind outreach.** Some sellers reactivate interest after a break. Approach with "I recently helped a neighbor sell their home in [X] days. I would love to share what we did." |
| **180+ days** | Either truly not motivated (testing the market) or have a price/condition problem they refuse to address. | Lower probability. Contact once, provide value, move on unless they engage. |

### What Makes This a High-Probability Lead

- DOM at 2-3x the neighborhood median AND the listing has had at least one price reduction = seller is trying but failing
- High DOM + owner-occupied + mortgage balance visible in public records showing low equity = potential distress situation
- High DOM + listing agent is a low-volume agent (< 6 transactions/year) = marketing/exposure problem, not a property problem
- High DOM in a neighborhood where every other listing sold in < 30 days = something specific is wrong, and a new set of eyes (yours) can diagnose it

### Suggested Approach/Timing

1. **Run a weekly DOM report** -- every Monday, pull all active listings in your farm area sorted by DOM descending
2. **Flag the "danger zone"** -- any listing that has crossed 2x your market's median DOM gets added to your active prospecting list
3. **Research before contact** -- before reaching out, know: the owner's name, whether it is owner-occupied, the tax assessed value, any public records (liens, permits, etc.), and the full listing history
4. **Lead with data, not criticism** -- "I track every home in [neighborhood] and noticed your property has been on the market longer than similar homes that have sold recently. I put together a brief analysis showing what those homes had in common and what made them sell. Can I share it with you?"

### Estimated Conversion Rate

- Properties at 2x median DOM: **25-30% will expire**
- Properties at 3x median DOM: **50-60% will expire**
- Contacting expired high-DOM listings with a pre-built CMA: **10-15% conversion to listing appointment**
- Bringing a buyer to an active high-DOM listing: **high offer-acceptance rate** -- sellers at 90+ DOM accept offers 5-8% below list price on average

---

## 4. Withdrawn & Relisted Properties

This is one of the most **underutilized** MLS mining strategies. When a listing is withdrawn and relisted, it almost always signals a problem: agent-seller conflict, failed marketing, buyer financing collapse, or strategic DOM manipulation. Each scenario is an opportunity.

### What Data to Look For

- **Status = Withdrawn (W)** in your MLS
- **Properties that appear as new listings but have CDOM (Cumulative DOM) significantly higher than current DOM** -- this is the smoking gun for a DOM reset
- **Same address appearing with different MLS numbers** within a 6-12 month period
- **Agent change on relisting** -- the property relisted but with a different listing agent (the seller fired their agent)
- **Price difference between withdrawn price and relisted price** -- often the new agent prices differently
- **Listing remarks differences** -- compare original and new listing descriptions for changed narratives
- **Photo changes** -- same photos = lazy relist; new photos = new agent or renovated
- **Seller concessions appearing on the relist** that were not on the original

### How to Filter/Search in MLS

**Finding Withdrawn Listings:**
```
Status: Withdrawn
Date Range: Last 90 days
Geographic Area: [Your farm]
```

**Finding DOM Resets (relisted properties):**
```
Status: Active
CDOM: > 60 (or your market's threshold)
Current DOM: < 14
```
This filter catches properties where CDOM is high but current DOM is low -- meaning the listing was recently restarted. Most MLS systems that track CDOM make this possible.

**Finding Agent Changes:**
This usually requires manual comparison:
1. Pull withdrawn listings for the past 90 days
2. Search for the same addresses in active listings
3. Compare the listing agent on each

### Why Agents Withdraw Listings (and What It Means for You)

| Withdrawal Reason | How to Identify | Opportunity |
|-------------------|-----------------|-------------|
| **Agent fired by seller** | Relisted with different agent | Limited -- new agent is already in place. But if the new agent also fails, you have deep history on the property. |
| **Agent withdrew to reset DOM** | Same agent, new MLS number, similar price, same photos | Medium -- the agent is playing games. If the property still does not sell, the seller will eventually catch on. |
| **Seller needs a break** | Withdrawn with no relist for 30+ days | High -- the seller is frustrated and taking time off. Contact at the 30-45 day mark with a soft approach. |
| **Major repair issue discovered** | Withdrawn after inspection period of a failed deal | High if you have investors or renovation-minded buyers. Check for new permits filed after withdrawal. |
| **Seasonal strategy** | Withdrawn in Nov/Dec, plan to relist in spring | Medium -- contact in January/February to win the spring relisting before they recommit to the old agent. |
| **Life circumstances changed** | Withdrawn and no activity for 60+ days | Varies -- could be that they no longer need to sell, or could be that they are overwhelmed. One contact attempt is warranted. |

### What Makes This a High-Probability Lead

**Best withdrawn listing leads:**
- Withdrawn after 90+ DOM with no relist for 30+ days AND owner-occupied (seller is frustrated, agent relationship likely damaged, homeowner still lives there)
- Withdrawn with agent change AND the new agent repriced significantly lower (seller is now realistic but burned -- if the new agent also fails, you are next in line)
- Withdrawn 2+ times (same property withdrawn and relisted multiple times) -- this is a seller who desperately wants to sell but keeps failing. They need a fundamentally different approach, which you can offer.

### Suggested Approach/Timing

| Scenario | Timing | Approach |
|----------|--------|----------|
| Freshly withdrawn, no relist | Wait 7-14 days (respect the cooling-off period) | Mail a handwritten note: "I noticed your home was recently on the market. If you decide to re-enter the market in the future, I would welcome the opportunity to share a fresh marketing perspective." |
| Withdrawn 30+ days, no relist | Contact now | Call or door knock. "I specialize in [neighborhood] and work with several buyers looking in this area. Are you still considering selling?" |
| Relisted with new agent | Monitor only | Add to watch list. If it expires again, you contact immediately with: "I have been following this property's market history. I have a specific plan for why this time would be different." |
| DOM reset (same agent) | Monitor, prepare | Build your CMA now. When it expires (likely), you have a data-driven presentation showing you tracked the full history. |

### Estimated Conversion Rate

- Withdrawn listings contacted after 30+ days with no relist: **5-8% listing conversion**
- Properties withdrawn 2+ times, contacted after latest withdrawal: **12-18%** (these sellers are running out of options and patience)
- Seasonal withdrawals contacted 4-6 weeks before typical spring listing season: **15-20%** (you are catching them before they re-sign with the previous agent)

---

## 5. FSBO Conversions

For Sale By Owner properties that fail represent one of the **highest-converting lead sources** in real estate. The owner has already demonstrated motivation to sell, invested time and energy, and discovered firsthand how difficult it is. When they fail, they are pre-qualified as motivated and often humbled enough to hire professional help.

### What Data to Look For

**In MLS:**
- Properties with a recent listing history showing an **agent-represented listing that was preceded by FSBO activity** (some MLS systems track FSBO entries separately)
- New listings where the **seller previously appeared on FSBO sites** (Zillow FSBO, ForSaleByOwner.com, Craigslist, Facebook Marketplace)
- **New MLS listings with owner as a party** and a note like "seller previously marketed independently"

**Outside MLS (cross-reference sources):**
- Zillow "For Sale By Owner" filter
- ForSaleByOwner.com
- Craigslist real estate section (your metro area)
- Facebook Marketplace -- "homes for sale" in your area
- Local FSBO yard signs (drive your farm area weekly)
- Nextdoor app posts ("thinking of selling" or "for sale" posts from homeowners)

**Combined signal (highest value):**
- Property appeared on FSBO sites 60-90 days ago AND is not currently on any FSBO site AND has not entered MLS = the seller tried, failed, and is sitting idle. This is your sweet spot.

### How to Filter/Search in MLS

Most MLS systems do not have a direct "former FSBO" filter. Instead:

**Method 1 -- New Listings with FSBO History:**
```
Status: Active
DOM: < 14 (newly listed)
Listing Type: Exclusive Right to Sell (meaning they now have an agent)
```
Then cross-reference the address against your FSBO tracking list (see workflow below).

**Method 2 -- MLS Entries by FSBO-Friendly Brokerages:**
Some flat-fee MLS entry services are well-known in each market. Filter by those office names to find listings that are essentially FSBOs paying for MLS exposure:
```
Status: Active
Listing Office: [Known flat-fee MLS entry offices in your market]
```
These sellers are still handling their own showings and negotiations. They are paying $300-500 for MLS placement but not getting agent services. Many will convert to full-service after experiencing the difficulty.

### What Makes This a High-Probability Lead

**Tier 1 -- Contact Immediately:**
- FSBO that has been active for 60+ days with no price reduction (stubborn on price, but the passage of time is eroding their confidence)
- FSBO that has reduced their price (they are learning that the market does not validate their original number)
- Former FSBO that is no longer actively marketing but has not listed with an agent (they gave up but still need to sell)

**Tier 2 -- Build Relationship:**
- Active FSBO that just listed (< 14 days) -- they are still optimistic. Plant the seed, do not push.
- FSBO with a property that has obvious marketing gaps (bad photos, no virtual tour, limited description)

**Tier 3 -- Monitor:**
- FSBO in a hot market at a reasonable price -- they might succeed. Check back in 30 days.

### Suggested Approach/Timing

**The FSBO Timeline Strategy:**

| FSBO Age | Action |
|----------|--------|
| **Week 1** | Introduction only. "I work extensively in [neighborhood] and wanted to introduce myself. If you have any questions about the market or the selling process, please don't hesitate to reach out. Here's my card." Provide value: local comps printout, no strings attached. |
| **Week 2-3** | Follow up with market data. "I wanted to share some recent sales near you that might be useful for your pricing." Include 3-5 nearby comps with sold prices. |
| **Week 4-6** | Offer a specific service. "I work with several pre-qualified buyers in this price range. Would you be open to me bringing a buyer through your home? You would not owe me anything -- my buyer would compensate me." This gets you in the door and builds trust. |
| **Week 6-8** | If still active and not sold: "Many homeowners I work with tell me that after a few weeks, they realize how much time showings and negotiations take. I have a flexible listing program that might work for you. Can I share the details?" |
| **Week 8+** | If the FSBO goes dark (removes listing, stops marketing): Wait 2 weeks, then contact. "I noticed your home is no longer actively listed. Have your plans changed, or are you taking a break? Either way, I would love to be a resource if you decide to re-enter the market." |

### Estimated Conversion Rate

- **Industry data**: Approximately 36% of FSBO sellers eventually list with an agent (National Association of Realtors data)
- Active FSBO contacted within the first 2 weeks with a comp package: **5-8% convert within 30 days**
- FSBO at 60+ days with consistent follow-up: **15-25% convert**
- Former FSBO that went dark, contacted 2-4 weeks after going inactive: **20-30% conversion to listing appointment**
- The key statistic: FSBOs that do sell on their own achieve a **median sale price roughly 23-26% lower** than agent-assisted sales (NAR data). This is your most powerful talking point once rapport is established.

---

## 6. Pocket Listings & Coming Soon

Pre-market opportunities give you a **first-mover advantage**. Identifying properties before they hit the open MLS means you can connect your buyers first or position yourself as the listing agent before the homeowner commits to someone else.

### What Data to Look For

**In MLS:**
- **Status = Coming Soon** (many MLS systems now have this as a formal status per NAR Clear Cooperation Policy)
- **Private/Office Exclusive listings** (some MLS systems allow a limited marketing period before full MLS entry)
- **New listings with a future "Active" date** -- some agents enter listings early with a delayed go-live
- **Agent remarks** (non-public section) mentioning "coming soon", "pre-market", or "off-market opportunity"

**Outside MLS:**
- Agent social media posts: Instagram, Facebook, LinkedIn -- agents frequently preview coming listings on social media before they hit MLS
- Brokerage "coming soon" pages on their websites
- Real estate networking groups (Facebook groups, local agent meetups, mastermind groups)
- New construction permit filings -- a completed renovation often precedes a sale
- Pre-listing home inspections (some inspectors post statistics or aggregated data about inspection volume by neighborhood)

**Public Records Signals That Predict Upcoming Listings:**
- **Recent home improvement permits** (kitchen, bath, roof) -- sellers often renovate before listing
- **Property listed for rent AND owner has purchased a new home** (check tax records for recent acquisitions by the same owner name)
- **Estate/probate filings** -- inherited properties frequently sell within 6-12 months
- **Divorce filings** (public record) -- the marital home typically sells during or after proceedings
- **Pre-foreclosure notices (lis pendens)** -- homeowner needs to sell before foreclosure
- **Code violation notices** -- sometimes triggers a decision to sell rather than repair

### How to Filter/Search in MLS

```
Status: Coming Soon
Geographic Area: [Your farm or buyer search area]
Price Range: [Buyer's criteria]
```

For identifying potential future listings:
```
Status: Active (Rental listings)
Owner Name: [Cross-reference with tax records showing recent property purchases]
```

### What Makes This a High-Probability Lead

**For Buyer Clients:**
- Coming Soon listings are the highest probability because the seller is committed to selling -- they are in the pipeline. Getting your buyer a showing before the public flood of interest is an enormous advantage.
- Pocket listings (true off-market) are valuable when the seller wants discretion (celebrity, divorce, financial distress). If you can match your buyer, both sides appreciate the privacy.

**For Listing Prospecting:**
- Identifying homeowners who are likely to sell BEFORE they choose an agent is the ultimate lead. Signals include:
  - Recent renovation permits + no homestead exemption change (they did not move in after renovating = preparing to sell)
  - Same owner name appearing on a new purchase in tax records (they already bought their next home = must sell current one)
  - Property actively rented + rising vacancy rates in the area (landlord may be looking to exit)

### Suggested Approach/Timing

| Signal | Timing | Approach |
|--------|--------|----------|
| Coming Soon in MLS | Immediately | For buyers: contact listing agent to arrange earliest possible showing. For prospecting: too late, they have an agent. |
| Social media preview | Immediately | Contact the posting agent to discuss buyer interest or to network. |
| Renovation permits filed | 2-4 months after permit issuance (renovation completion timeline) | Mail a "thinking of selling after your renovation?" letter with recent comp data. |
| Same owner bought new home | Within 30 days of the new purchase recording | "Congratulations on your new home! If you're considering selling [old address], I specialize in this neighborhood and would love to help you maximize your return." |
| Probate filing | 30-60 days after filing (allow for the initial grieving/legal period) | Gentle, informative mailer about estate property options. Never aggressive. |
| Pre-foreclosure notice | Within 14 days of notice filing | Informative letter about options: sell before foreclosure, short sale, etc. Provide value, not pressure. |

### Estimated Conversion Rate

- Coming Soon listings matched to your active buyers: **30-40% showing-to-offer rate** (reduced competition)
- Renovation permit mailer to likely future sellers: **2-4% response rate**, of which **30-50% will eventually list** (long lead time)
- Probate property outreach: **5-10% listing conversion** (3-12 month timeline)
- Pre-foreclosure outreach: **3-8% listing conversion** (time-sensitive, high competition from investors)

---

## 7. Rental to Sale Conversions

Landlords who decide to sell their rental properties are some of the **most motivated sellers** you will encounter. They are often dealing with tenant issues, rising maintenance costs, changing tax laws, or simply portfolio rebalancing. The key is identifying the transition signal.

### What Data to Look For

**In MLS:**
- Properties previously listed for rent in MLS that now appear for sale
- **Status History showing**: Rental Active -> Rental Expired/Withdrawn -> For Sale Active
- Properties listed for sale with **"tenant occupied"** in remarks (current rental being sold)
- Listings noting **"investment property"**, **"rental income"**, **"currently leased"**
- For-sale listings where the **owner address on tax records differs from the property address** (absentee/investor owner)

**Outside MLS:**
- Properties listed on rental platforms (Zillow Rentals, Apartments.com, Craigslist) that later appear for sale
- Properties with increasing rental vacancy periods (longer time between tenants = landlord fatigue)
- Properties with multiple tenant turnover in a short period (check utility connection records if available in your area)

**Public Records Cross-Reference:**
- Owners who own 2+ properties and are filing eviction notices (landlord frustration signal)
- Properties with building code violations in rental inspection programs
- Rental license renewals that lapse (owner may be planning to exit)

### How to Filter/Search in MLS

**Method 1 -- Direct Filter:**
```
Status: Active (Sale)
Previous Status: [Rental/Lease -- if your MLS tracks this]
Owner Occupancy: Non-Owner Occupied / Investment
Geographic Area: [Your farm]
```

**Method 2 -- Manual Cross-Reference:**
1. Pull all rental listings that expired or were withdrawn in the last 6 months
2. Search for those same addresses in the sale listings (active, coming soon, or recently listed)
3. Flag matches -- these are confirmed rental-to-sale conversions

**Method 3 -- Absentee Owner Filter on Active Sales:**
```
Status: Active (Sale)
Listing Remarks Contains: "tenant" OR "lease" OR "rental income" OR "investment"
DOM: > 30
```

### What Makes This a High-Probability Lead

**Strongest signals (contact immediately):**
- Rental listing expired 2+ times and now listed for sale (landlord gave up on renting)
- Investor owner with a recent eviction filing now listing for sale
- Rental property with code violations now listed for sale (owner does not want to invest in repairs)
- Out-of-state owner selling a local rental property (tired of remote management)

**Medium signals (monitor and prepare):**
- Rental listed at market rate with no tenant for 60+ days (carrying costs are accumulating)
- Long-term rental (10+ years) where the owner is approaching retirement age (checked via public records -- voter registration, etc.)
- Neighborhoods with declining rents but rising property values (better to sell than hold)

### Suggested Approach/Timing

**For Listing the Property:**
- Contact the owner within 7 days of their rental listing expiring for the 2nd time
- Lead with: "I noticed your property at [address] has been between tenants. Many landlords in [neighborhood] are finding that current property values make this an excellent time to sell. Would you like to see what your property could sell for in today's market?"
- Provide a **dual analysis**: what they could earn annually in rent vs. what they would net from a sale, invested elsewhere. Show the math.

**For Buyer Clients (Investors):**
- Tired landlords selling tenant-occupied properties often sell below market because the tenant complicates showings and the buyer pool is smaller
- Alert your investor buyers to these properties -- they can buy at a discount, inherit a paying tenant, and add to their portfolio

### Estimated Conversion Rate

- Expired rental listing owners contacted about selling: **8-12%** will list within 6 months
- Owners with recent eviction + rental listing: **15-20%** will seriously consider selling
- Out-of-state landlord with expired rental: **12-18%** listing conversion
- Providing a "sell vs. hold" analysis with the initial contact increases response rates by **40-60%** compared to a generic listing pitch

---

## 8. MLS Status History Mining

The full status history of a property across all MLS entries is a **goldmine of intelligence** that most agents never examine. Every status change is a data point about the seller's journey, motivation, and relationship with their agent.

### What Data to Look For

- **Full status change timeline**: Active -> Pending -> Back on Market -> Price Reduction -> Pending -> Withdrawn -> Relisted -> Active
- **Number of times a property has been Pending and then returned to Active** ("fallen through" deals)
- **Time gaps between statuses** (e.g., Withdrawn for 45 days then Relisted = cooling-off period)
- **Listing agent changes** between listing periods
- **Price trajectory** across all listing periods (is it trending down with each relist?)
- **Buyer-side agent on failed pendings** (was it the same buyer agent multiple times? Or different ones each time?)
- **Cumulative time on market** across ALL listing periods (the true DOM the market has imposed on this property)

### How to Filter/Search in MLS

Most MLS systems allow you to view the full history of a property by address. Here is the workflow:

**Step 1 -- Identify Target Properties:**
```
Status: Active
CDOM: > [2x your market median]
Geographic Area: [Your farm]
```

**Step 2 -- Deep Dive on Each:**
- Click into the listing
- Navigate to "Property History" or "Status History" tab
- Document every status change, date, price, and agent

**Step 3 -- Pattern Recognition:**
Look for these specific patterns:

### Key Status Patterns and Their Meanings

| Pattern | What It Means | Opportunity |
|---------|---------------|-------------|
| **Active -> Expired -> Active -> Expired** (repeat) | Serial failure. Likely a pricing or condition issue the seller refuses to address. | High if you can have an honest pricing conversation. Bring a detailed CMA and a marketing plan that directly addresses why it has not sold. |
| **Active -> Pending -> Active -> Pending -> Active** | Deals keep falling apart. Could be inspection issues, appraisal gaps, seller inflexibility on repairs, or title problems. | Research the likely cause. If it is inspections: bring a buyer who is flexible on condition. If it is appraisal: the property is overpriced. |
| **Active -> Withdrawn -> Active (different agent) -> Withdrawn -> Active (3rd agent)** | The seller is churning through agents. Potentially a difficult client, but also potentially an owner who keeps hiring the wrong agent. | Approach with caution but confidence. Your pitch: "I have reviewed this property's complete market history and I have a specific diagnosis for why it has not sold. Can I share it with you?" |
| **Active -> Temporarily Off Market -> Active (same agent, same price)** | Seasonal break or personal circumstances. Not distressed. | Low urgency. Note for long-term follow-up. |
| **Active -> Pending (7+ days in pending) -> Active** | A deal fell through late, likely during inspections, appraisal, or financing. Seller is now psychologically battered -- they thought it was done. | **High opportunity.** Contact immediately when it goes back to Active. "I understand your sale fell through. That must be frustrating after getting so far in the process. I have several qualified, pre-approved buyers. Can I bring one through this week?" |

### What Makes This a High-Probability Lead

- **3+ status changes in 12 months** = distressed listing history, high motivation
- **2+ fallen-through pendings** = either a property problem (fixable with right buyer) or a seller problem (fixable with right agent)
- **Agent changes + price drops** = seller is learning the hard way. By the 2nd or 3rd agent, they are much more coachable.
- **Long gaps between listing periods** = seller took time off but came back, meaning they still need to sell

### Suggested Approach/Timing

1. **Build a "Chronic Listings" database** -- properties in your farm area that have had 3+ listing periods in the past 24 months
2. **Create a one-page property history summary** for each -- timeline of every listing, every agent, every price, every status change
3. **When the current listing expires**: present this summary to the seller. No other agent will have this. It shows extraordinary preparation and market knowledge.
4. **For active "chronic listings"**: prepare a buyer shortlist. These properties often sell at a discount, making them attractive to investors and renovation buyers.

### Estimated Conversion Rate

- Properties with 3+ listing periods contacted with a full history analysis on expiration: **18-25%** listing conversion (the highest of any expired listing subcategory, because you demonstrate expertise no other agent offers)
- Fallen-through pendings contacted within 48 hours of returning to Active status: **12-15%** of sellers will entertain your offer to bring a new buyer

---

## 9. Agent Activity Patterns

Every listing agent's track record is visible in MLS data. By analyzing **which agents consistently fail to sell their listings**, you can **predict future expired listings** and pre-position yourself to win them.

### What Data to Look For

- **Agent production reports**: total listings taken vs. total listings sold in the past 12 months
- **Agent's listing-to-sold ratio** -- what percentage of their listings actually close?
- **Agent's average DOM** compared to market average DOM
- **Agent's list-to-sale price ratio** -- do they consistently overprice (listing at $500K, selling at $450K)?
- **Agent's expired listing count** -- how many of their listings expired in the last 12 months?
- **Agent's active listing count vs. closed count** -- an agent with 20 active listings and 5 closings in 12 months has a problem
- **Repeat expired patterns** -- does the same agent have listings expire in the same price range or neighborhood repeatedly?

### How to Filter/Search in MLS

**Method 1 -- Agent Production Search:**
Most MLS systems have an agent production or agent roster feature:
```
Agent Search
Date Range: Last 12 months
Status: Expired
Sort By: Number of expired listings (descending)
Geographic Area: [Your farm]
```

**Method 2 -- Manual Agent Analysis:**
1. Pull all expired listings in your farm area for the last 12 months
2. Export to a spreadsheet (most MLS systems support CSV export)
3. Pivot table by listing agent name
4. Sort by count of expired listings
5. Calculate: (Expired Listings) / (Total Listings Taken) = Failure Rate

**Method 3 -- Current Active Listing Risk Assessment:**
1. Identify agents with high failure rates from Method 2
2. Pull their current active listings
3. These active listings have a higher-than-average probability of expiring
4. Pre-build CMAs for these properties NOW

### Building Agent Profiles

Create a spreadsheet or database with columns:

| Agent Name | Office | Total Listings (12mo) | Sold | Expired | Withdrawn | Failure Rate | Avg DOM | Common Price Range | Common Area |
|------------|--------|----------------------|------|---------|-----------|-------------|---------|-------------------|-------------|

**High-failure-rate agents (failure rate > 30%) are your lead generators.** Their current active listings are your future prospecting list.

### What Makes This a High-Probability Lead

**The math is compelling:**
- If Agent X has a 40% failure rate and currently has 8 active listings, statistically 3 of those listings will expire
- If you pre-build CMAs for all 8, you will have a presentation ready on Day 0 for the 3 that expire
- You will be the most prepared agent contacting those sellers on expiration day

**Highest probability scenarios:**
- Agent with high failure rate + their listing has DOM > 60 + at least one price reduction = extremely likely to expire
- Agent who is part-time or newly licensed with listings in the higher price ranges (mismatched experience to property value)
- Agent at a small office with limited marketing resources listing a property that needs maximum exposure

### Suggested Approach/Timing

**Phase 1 -- Research (ongoing, weekly):**
- Update your agent failure-rate database monthly
- Every Monday, check the active listings of your top 10 highest-failure-rate agents
- Flag any of their listings approaching key DOM thresholds (60, 90, 120 days)

**Phase 2 -- Preparation (2-4 weeks before expected expiration):**
- Build a CMA for each flagged listing
- Research the property owner (tax records, public records)
- Draft a personalized letter for each property
- Prepare a side-by-side comparison: "Here is what was done to market your home. Here is what I would do."

**Phase 3 -- Execution (expiration day):**
- Contact on Day 0 with your pre-built materials
- Your pitch: "I have been tracking the market in your neighborhood closely, and I noticed your listing agreement has ended. I have already prepared a market analysis and a customized marketing plan for your home. Can I share it with you today?"

### Ethical Considerations

- **Never disparage another agent** to a potential client. Let your preparation and data speak for itself.
- **Never contact a seller while their listing agreement is still active** to solicit business. This violates MLS rules and Realtor ethics codes.
- **You ARE allowed to**: track agent performance data, prepare materials in advance, and contact homeowners promptly after their listing agreement expires.

### Estimated Conversion Rate

- Pre-identified high-probability expireds contacted on Day 0 with a prepared CMA: **15-22%** listing appointment conversion
- This is significantly higher than the 3-5% cold expired rate because your preparation demonstrates competence and the property is one you have specifically studied
- Over a 12-month period, tracking 10 high-failure-rate agents and systematically targeting their expireds can yield **15-25 listing appointments** per year from this single source

---

## 10. Comparable Sales Gaps

This is the most **creative and least competitive** strategy in this entire guide. Instead of chasing properties already on the market, you are identifying properties that **should list based on market conditions** but have not yet. You are predicting future sellers before they even know they want to sell.

### What Data to Look For

- **Recent sold comps in a neighborhood** at prices significantly above the tax-assessed value (indicating strong appreciation that homeowners may not be aware of)
- **Neighborhoods where 3+ homes have sold in the last 90 days** at record-high prices per square foot (momentum that other owners could capitalize on)
- **Streets or blocks where every property has sold in the last 2-3 years EXCEPT a few** -- those holdout owners are sitting on appreciated value and may not realize it
- **Properties purchased 5-7 years ago** that have likely doubled or significantly appreciated -- these owners have maximum equity and may be ready to cash out
- **Neighborhoods where new construction is going up at prices above existing home values** -- existing homeowners can sell for close to new construction prices without the new construction premium
- **Zip codes or neighborhoods with net positive migration** (more people moving in than out) -- sustained demand signals
- **Properties with recently paid-off mortgages** (satisfaction of mortgage recorded) -- no monthly payment pressure = maximum flexibility to time a sale for maximum price

### How to Filter/Search in MLS

**Step 1 -- Identify Hot Neighborhoods:**
```
Status: Sold
Date Range: Last 90 days
Geographic Area: [Your farm -- broad]
Sort By: Sale Price per Square Foot (descending)
```
Calculate the median price per square foot by neighborhood. Identify neighborhoods where this number has increased 10%+ year-over-year.

**Step 2 -- Find the Gaps:**
For each hot neighborhood:
```
Status: Sold
Date Range: Last 24 months
Geographic Area: [Specific hot neighborhood]
```
Map every sold property. Then look at the tax rolls for that neighborhood and identify properties that have NOT sold. These are your targets.

**Step 3 -- Qualify the Gaps:**
For each non-sold property in a hot neighborhood:
- Check tax records for: owner name, purchase date, purchase price, current assessed value
- Calculate estimated equity: (current comp-based value) - (estimated mortgage balance based on purchase price and time)
- Check for: homestead exemption (owner-occupied), length of ownership, any liens or encumbrances

### What Makes This a High-Probability Lead

**Tier 1 -- Highest Probability:**
- Owner purchased 7+ years ago at a price that is 40%+ below current comp values
- Owner is in a neighborhood where 5+ homes sold in the last 6 months (neighbors are selling = social proof + "I wonder what my house is worth" thinking)
- Owner has paid off their mortgage (satisfaction of mortgage recorded in public records)
- Owner is 55+ years old (public records) and living in a home larger than they likely need (3,000+ sq ft) -- potential downsizer

**Tier 2 -- Strong Probability:**
- Home purchased 5-10 years ago in a neighborhood that has gentrified or significantly improved
- Neighboring homes recently sold at prices that would represent a 100%+ return on the owner's original purchase
- Owner has recently obtained a home equity line of credit (recorded in public records) -- they know their equity exists and are accessing it, which could indicate planning

**Tier 3 -- Worth a Mailer:**
- Any owner in a hot neighborhood who has not sold in 5+ years -- they may not know what their home is worth today

### Suggested Approach/Timing

**The "Hidden Equity" Campaign:**

This is a direct mail and door-knocking campaign targeting homeowners who may not realize how much their property has appreciated.

**Step 1 -- The Data Mailer:**
Send a personalized letter or postcard:
> "3 homes on [Street Name] sold in the last 6 months at an average price of [$$]. Based on comparable sales, your home at [Address] could be valued at approximately [$range]. If you have ever wondered what your home is worth in today's market, I have prepared a complimentary analysis. No obligation. Just information."

**Step 2 -- The Neighborhood Sold Report:**
Follow up 2 weeks later with a visually compelling neighborhood map showing recent sales, pending sales, and active listings -- with their property highlighted as "not yet listed." This is powerful psychological framing.

**Step 3 -- The Door Knock (Optional):**
For Tier 1 prospects, a door knock with a printed CMA is the highest-converting approach. Lead with: "I just sold [neighbor's address] for [$$$] and I wanted to let you know that your home would likely generate significant interest in the current market."

**Timing considerations:**
- Best delivered in spring (March-May) when sellers are naturally thinking about the market
- Second-best: early fall (August-September) before the holiday slowdown
- For retirement-age owners: January-February is effective (New Year's resolution to downsize/simplify)

### Estimated Conversion Rate

- Personalized comp mailer to qualified gap properties: **1-3% response rate**, of which **20-30% will list within 12 months**
- Door knock with CMA to Tier 1 gap properties: **5-10% listing conversation rate**, of which **25-40% will list within 12 months**
- This is a longer-term strategy with a lower immediate conversion rate but a **much larger addressable market** than expired/withdrawn listings. There are far more properties that have not listed than properties that have listed and failed.
- **Lifetime value is high**: these sellers have no negative baggage from a failed listing. They are starting fresh and are often easy clients.

---

## 11. Building a Daily Workflow

Consistency transforms these strategies from interesting ideas into a lead generation machine. Here is a structured daily and weekly workflow.

### Daily Morning Routine (30 minutes)

**6:30 AM -- Before Other Agents Wake Up:**

1. **Pull Expired Listings** (5 minutes)
   - Filter: Expired yesterday in your farm area
   - Prioritize: Owner-occupied, 90+ DOM, 2+ price reductions
   - Action: Queue calls and prepare CMAs for top 3

2. **Pull New Price Reductions** (5 minutes)
   - Filter: Price changed in last 24 hours in your farm area
   - Flag: 3rd+ reductions, reductions > 5%
   - Action: Add to watch list or bring to buyer matches

3. **Review Back-on-Market Listings** (5 minutes)
   - Filter: Status changed from Pending to Active in last 24 hours
   - Action: Contact listing agent if you have a matching buyer

4. **Check Coming Soon / New Listings** (5 minutes)
   - Filter: Coming Soon and New Active (< 24 hours) in your farm area and your buyer search areas
   - Action: Match to your active buyer list; schedule showings

5. **Review Withdrawn Listings** (5 minutes)
   - Filter: Withdrawn in last 7 days
   - Research: Who is the owner? What happened?
   - Action: Add to 14-day follow-up queue

6. **FSBO Check** (5 minutes)
   - Review Zillow FSBO, Craigslist, and Facebook Marketplace
   - Cross-reference: Any new FSBOs in your farm area?
   - Action: Add to FSBO contact sequence

### Weekly Deep Dive (60 minutes, choose a slow day)

1. **DOM Report** (15 minutes)
   - Pull all active listings sorted by DOM
   - Flag anything crossing the 2x median threshold
   - Update your DOM watch list

2. **Agent Failure Rate Update** (15 minutes)
   - Check your top 10 high-failure-rate agents' current active listings
   - Flag any approaching expiration or key DOM thresholds
   - Pre-build CMAs for the most likely expireds

3. **Comp Gap Analysis** (15 minutes)
   - Review sold listings from the past week in your farm area
   - Identify any new "gap" properties (neighbors of recently sold homes)
   - Queue for direct mail campaign

4. **Rental-to-Sale Check** (15 minutes)
   - Review expired rental listings from the past 30 days
   - Cross-reference for new sale listings
   - Contact landlords who have not relisted for rent or sale

### Monthly Strategic Session (90 minutes)

1. **Review your lead pipeline conversion rates** -- which strategies are producing?
2. **Update agent failure rate database** with fresh 12-month rolling data
3. **Plan direct mail campaigns** for comp gap targets
4. **Review FSBO conversion success** -- refine your approach based on what has worked
5. **Analyze your market's DOM median** -- has it shifted? Adjust your thresholds.

---

## 12. Lead Scoring Matrix

Not all leads are created equal. Use this scoring system to prioritize your time.

### Point-Based Scoring System

| Signal | Points |
|--------|--------|
| **Listing Status Signals** | |
| Expired listing (0-7 days ago) | +30 |
| Expired listing (8-30 days ago) | +20 |
| Expired listing (31-90 days ago) | +10 |
| Withdrawn, no relist for 30+ days | +25 |
| Multiple listing periods (3+) | +20 |
| Failed pending (back on market) | +25 |
| FSBO for 60+ days | +20 |
| | |
| **Price Signals** | |
| 3+ price reductions | +20 |
| Cumulative reduction > 10% | +15 |
| Current price below tax assessed value | +15 |
| Price below recent comp median | +10 |
| | |
| **DOM Signals** | |
| DOM > 2x market median | +15 |
| DOM > 3x market median | +25 |
| DOM > 180 days | +10 (actually lower priority -- may not be motivated) |
| | |
| **Owner Signals** | |
| Owner-occupied | +15 |
| Absentee owner (landlord) | +10 |
| Out-of-state owner | +15 |
| Mortgage satisfaction recorded (paid off) | +5 |
| Recent purchase of another property | +25 |
| Probate/estate filing | +20 |
| Pre-foreclosure notice | +25 |
| Divorce filing | +20 |
| | |
| **Agent Signals** | |
| Listing agent failure rate > 30% | +15 |
| Listing agent < 6 transactions/year | +10 |
| Agent change between listing periods | +10 |
| | |
| **Market Context Signals** | |
| Neighborhood with strong recent comp activity | +10 |
| Property would represent 100%+ appreciation from purchase | +10 |
| New construction in neighborhood at higher prices | +5 |

### Priority Tiers

| Score | Priority | Action |
|-------|----------|--------|
| **70+** | Immediate -- Hot Lead | Contact today. Prepare CMA. This is a high-probability listing opportunity. |
| **50-69** | High -- Contact This Week | Strong lead. Research fully, prepare materials, schedule outreach within 3 business days. |
| **30-49** | Medium -- Active Nurture | Good potential. Add to a systematic follow-up sequence (mailers, market updates, periodic calls). |
| **15-29** | Low -- Passive Monitor | Keep in your database. Send neighborhood market reports quarterly. |
| **< 15** | Archive | Not enough motivation signals yet. Revisit if new signals appear. |

### Example Scored Lead

**Property: 123 Oak Street**
- Expired listing 5 days ago: +30
- Was on market 95 days (3x market median of 30): +25
- Had 3 price reductions totaling 12%: +20 + 15
- Owner-occupied: +15
- Listing agent had 4 transactions last year: +10
- Neighborhood had 6 sales in last 90 days at record prices: +10
- **Total Score: 125 -- Immediate / Hot Lead**

This homeowner should be contacted today with a pre-built CMA and a clear marketing plan that differs from what their previous agent offered.

---

## Appendix A: MLS Filter Quick Reference

| Strategy | Primary MLS Filter | Secondary Filters | Update Frequency |
|----------|-------------------|-------------------|------------------|
| Expired Listings | Status = Expired, Last 1-30 days | DOM, Price Changes, Owner Type | Daily |
| Price Reductions | Price Changed = Yes, Last 7 days | Number of Changes >= 2, DOM > 30 | Daily |
| DOM Analysis | Status = Active, DOM > [2x median] | Price Changes, CDOM vs DOM | Weekly |
| Withdrawn/Relisted | Status = Withdrawn, Last 90 days | CDOM vs DOM discrepancy, Agent Changes | Weekly |
| FSBO Conversions | External tracking + MLS cross-reference | Flat-fee brokerage filter | Daily |
| Coming Soon | Status = Coming Soon | Price Range, Property Type | Daily |
| Rental to Sale | Status History: Rental -> Sale | Absentee Owner, Eviction History | Bi-weekly |
| Status History Mining | Address History search, CDOM > 60 | Multiple Listing Periods, Agent Changes | Weekly |
| Agent Activity | Agent Production Reports | Failure Rate Calculation, Current Actives | Monthly |
| Comp Gaps | Sold Last 90 Days + Tax Roll Cross-Reference | Purchase Date, Equity Estimate, Owner Age | Monthly |

## Appendix B: Conversion Rate Summary

| Strategy | Contact-to-Appointment Rate | Appointment-to-Listing Rate | Overall Conversion | Timeline |
|----------|---------------------------|----------------------------|--------------------|----------|
| Expired (same-day, prepared) | 15-20% | 50-60% | 8-12% | Immediate |
| Expired (90-day follow-up) | 25-35% | 40-50% | 15-20% | 1-3 months |
| Price Reductions (post-expiration) | 15-20% | 50-60% | 10-15% | 2-6 weeks |
| High DOM (post-expiration) | 12-18% | 50-60% | 10-15% | 1-3 months |
| Withdrawn (30+ days, no relist) | 8-12% | 40-50% | 5-8% | 2-4 weeks |
| FSBO (60+ day, consistent follow-up) | 20-30% | 50-60% | 15-25% | 1-3 months |
| Coming Soon (buyer matching) | 30-40% | N/A (buyer side) | 30-40% showing-to-offer | Immediate |
| Rental to Sale | 10-15% | 50-60% | 8-12% | 1-6 months |
| Status History (chronic listings) | 20-30% | 60-70% | 18-25% | Immediate on expiration |
| Agent Pattern (pre-identified) | 18-25% | 55-65% | 15-22% | Pre-planned |
| Comp Gaps (mailer) | 1-3% response | 20-30% of responders | 0.5-1% | 3-12 months |
| Comp Gaps (door knock) | 5-10% conversation | 25-40% of conversations | 2-4% | 3-12 months |

## Appendix C: Legal and Ethical Guardrails

- **Never contact a homeowner about listing their property while they are under an active listing agreement** with another agent. This violates MLS rules and NAR Code of Ethics Article 16.
- **All MLS data must be used in accordance with your local MLS Terms of Service.** Do not share raw MLS data publicly or with non-members.
- **FSBO contact is permissible** since they do not have an exclusive agent agreement. However, be professional and never aggressive.
- **Public records are public.** Using tax records, court filings, and permit data for outreach is legal. However, be sensitive with probate and divorce-related outreach -- lead with empathy, not salesmanship.
- **Do Not Call compliance**: check all phone numbers against the Do Not Call registry before calling. Expired listings and FSBOs have implied consent for real estate inquiries, but verify your state's specific rules.
- **CAN-SPAM compliance**: all emails must include opt-out mechanisms and your physical business address.
- **Fair Housing**: never target or exclude prospects based on race, color, national origin, religion, sex, familial status, or disability. Your targeting should be based exclusively on property characteristics and market behavior signals.

---

*This document is a living research resource. Update conversion rates based on your own experience, adjust DOM thresholds as your market shifts, and refine the lead scoring matrix as you learn which signals predict success in your specific market.*
