# Interim Data Playbook: What We Can Do Before the API

**Date**: 2026-03-03
**Status**: Actionable NOW — no API key required
**Cost**: $0 for everything below

---

## The Big Picture

We don't need to wait for the API. The Phase 1 MVP pipeline already works:
**CSV drop → signal detection (12 signals) → scoring → morning briefing**

The system is hungry for data. Here are 3 categories of data we can feed it today:

1. **Matrix CSV Exports** — the MLS data Yani already has access to
2. **County Public Records** — free bulk downloads from Lee & Collier county
3. **Free Online Sources** — FSBO sites, market data, Google Alerts

---

## TIER 1: Matrix CSV Exports (Start TODAY)

Yani logs into Matrix every day. With 30 minutes of setup and 5-10 minutes daily, she can feed The Lead Edge everything it needs.

### One-Time Setup: Create the Export Template

1. In Matrix, click agent name → Settings → Custom Exports → Add Export
2. Name it **"TheLeadEdge Export"**
3. Add all 46 fields from our field mapping (the system handles both Name and Label headers)
4. Set separator to comma
5. Save — this template is now available on every search

### One-Time Setup: Create Saved Searches

| Search Name | Criteria | Why |
|-------------|----------|-----|
| **LE - Fresh Expireds** | Status = Expired, StatusChange = last 7 days, all SWFLA ZIPs | Highest-value leads — seller still wants to sell |
| **LE - Price Drops** | Status = Active, PriceChange = last 48 hours | Urgency signal — seller getting anxious |
| **LE - Withdrawn** | Status = Withdrawn, StatusChange = last 14 days | Seller pulled listing but may still be motivated |
| **LE - Cancelled** | Status = Cancelled, StatusChange = last 7 days | Agent relationship ended — opportunity |
| **LE - High DOM** | Status = Active, DOM >= 90 days | Stale listings — frustrated sellers |
| **LE - Back on Market** | Status = Active, CDOM > DOM (relisted) | Deal fell through — seller frustrated |
| **LE - Severe Price Cut** | Status = Active, price drop >= 15% from original | Desperate seller signal |

### One-Time Setup: Hot Sheets (Real-Time Monitoring)

Matrix supports up to 10 Hot Sheets. Configure these 5:

1. **Fresh Expireds** — Status change to Expired, all residential, SWFLA
2. **Price Drops** — Price decrease, Active status, target ZIPs
3. **Withdrawn & Cancelled** — Status change to Withdrawn or Cancelled, last 7 days
4. **Back on Market** — Status change from non-Active to Active, CDOM > 0
5. **High DOM Active** — Active listings, DOM > 90 days (monthly review)

### One-Time Setup: Auto Email Notifications

Turn saved searches into push notifications:
- **Daily at 8:00 AM**: Fresh Expireds, Price Drops
- **ASAP (immediate)**: Back on Market
- **Weekly**: Withdrawn, Cancelled, High DOM

**Limit**: 250 listings per Auto Email. Split by county or price range if exceeded.

### Daily Workflow (5-10 minutes)

1. Open Matrix, check Hot Sheets for overnight changes
2. Run the **"LE - Fresh Expireds"** and **"LE - Price Drops"** saved searches
3. Select All → Export using the "TheLeadEdge Export" template
4. Save CSV to `Data/mls_imports/` folder
5. Done — the pipeline picks it up automatically

### Fields to Consider Adding to the Export

These aren't in our 46-field mapping yet but are available in Matrix and valuable:

| Field | Why |
|-------|-----|
| `PublicRemarks` | NLP gold — "must sell", "as-is", "bring all offers", "estate sale" |
| `SpecialListingConditions` | RESO enum: Short Sale, REO, Probate Estate, Auction |
| `Concessions` | Seller concessions offered = motivation signal |
| `AssociationFee` | High HOA fees can indicate distress |
| `TaxAnnualAmount` | High taxes on low-value property = burden |
| `ShowingInstructions` | "Easy to show" vs. "appointment only" correlates with urgency |

---

## TIER 2: Free County Public Records (Huge Untapped Resource)

Both Lee and Collier counties provide **free bulk data downloads**. This is structured, machine-readable CSV data that maps directly to our 8 pre-configured but unactivated signal types.

### Collier County Property Appraiser — BEST Free Source

**Download Page**: https://www.collierappraiser.com/Main_Data/DataDownloads.html
**How-To Guide**: https://www.collierappraiser.com/Main_Data/HowtoUsetheFiles.html

**Available CSV files (all FREE, all joinable on PARCELID):**

| File | Contents | Lead Gen Use |
|------|----------|-------------|
| **Parcels** | Owner name, mailing address, site address, values, exemptions | Absentee owner detection, equity analysis |
| **Sales** | Sale date, price, document number, transfer details | Long-term ownership, flip detection |
| **Buildings** | Year built, sqft, building class (per structure) | Age/condition filtering |
| **Legal** | Full legal descriptions | Parcel identification |
| **Values History** | 5 years of assessed values | Value decline = distress signal |
| **All (CSV bundle)** | Everything above + lookup tables | One download gets it all |

**Immediate actions:**
- Download the Parcels + Sales CSVs
- Filter where mailing address ≠ site address → **absentee owners**
- Filter for no homestead exemption in residential zones → **investor-owned**
- Join with Sales to find properties with no recent sale (15+ years) → **high equity**

### Lee County Property Appraiser (LEEPA)

**Tax Roll Data**: https://www.leepa.org/Roll/TaxRoll.aspx (NAL files, free)
**Sale Data Files**: https://www.leepa.org/Roll/SDFTxt.aspx (17 years of sales history, free)
**Parcel List Generator**: https://www.leepa.org/OnlineReports/ParcelListGenerator.aspx

The **Parcel List Generator** is a killer tool — build custom parcel lists filtered by:
- Property classification
- Sale prices and dates
- Bedrooms, bathrooms
- Owner information
- **Exports directly to CSV**

**Immediate actions:**
- Download the tax roll (NAL files) for absentee owner analysis
- Use the Parcel List Generator to build a targeted CSV of single-family absentee-owned properties in target ZIPs
- Download Sale Data Files for ownership duration analysis

### Pre-Foreclosure (Lis Pendens) — Weekly Monitoring

**Lee County Clerk**: https://www.leeclerk.org/departments/official-records-services/search-official-records
**Collier County Clerk**: https://app.collierclerk.com/CORPublicAccess/Search/Document

**Weekly workflow:**
1. Go to Official Records Search
2. Filter Document Type = "Lis Pendens"
3. Set date range = last 7 days
4. Results show plaintiff (lender), defendant (borrower), recording date
5. Cross-reference borrower name with Property Appraiser to find the property

**Why this matters**: Florida is a judicial foreclosure state — the process takes 6-18 months. That's a huge window for a traditional sale. Pre-foreclosure leads score 20 points in our system (highest base score of any signal).

### Probate Records — Monthly Monitoring

**Lee County**: https://matrix.leeclerk.org/ (search case type "Probate" or "PB")
**Collier County**: https://cms.collierclerk.com/showcaseweb/

**Workflow:**
1. Search for probate cases filed in last 60-90 days
2. Note decedent name and personal representative
3. Search Property Appraiser for properties owned by decedent
4. If property found → high-value lead (heirs often want to liquidate)

**Note**: Online access to probate may be limited. In-person visits to the Clerk's office may yield better results.

### Divorce Filings — Monthly Monitoring

**Lee County**: https://matrix.leeclerk.org/ (search case type "DR" or "FM")
**Collier County**: https://cms.collierclerk.com/showcaseweb/

Divorce filings are **public records in Florida** (Sunshine Law). Joint-owned property typically must be sold or refinanced. Cross-reference with Property Appraiser for jointly-owned homes.

### Tax Delinquency Lists — Seasonal (Feb-May)

**Lee County**: https://leetc.com/delinquent-taxes/
**Collier County**: https://colliertaxcollector.com/

Florida tax certificate sales happen in May. The delinquent list is published 3 weeks before in local newspapers. Both counties must provide this as a public record if requested.

**Best timing**: Request the list in February-April, before the May sale. First-time delinquents are most responsive.

### Foreclosure Auction Calendars — Weekly Check

**Lee County**: https://lee.realforeclose.com/
**Collier County**: https://collier.realforeclose.com/

The goal isn't to buy at auction — it's to contact the owner BEFORE the auction and offer a market-rate listing. Monitor upcoming auctions, cross-reference with PA for owner contact info.

### Code Violations — Monthly Scan

**Lee County (unincorporated)**: https://aca-prod.accela.com/LEECO/Cap/CapHome.aspx?module=CodeEnforcement
**Collier County**: https://cvportal.collier.gov/cityviewweb
**Cape Coral**: https://www.capecoral.gov/departments/development_services/permitting_services_division/energov_citizen_self_service_css.php

Repeat violations signal neglect/absentee ownership. Properties with code liens have accumulating penalties — strong motivation to sell.

### Florida Sunbiz (LLC/Corporation Records)

**Search**: https://search.sunbiz.org/
**Bulk Downloads**: https://dos.fl.gov/sunbiz/other-services/data-downloads/ (quarterly, free)

Cross-reference LLC names with property appraiser data to identify investor-owned residential properties. LLCs that fail to file annual reports (status = Inactive) may signal distressed/abandoned entities.

---

## TIER 3: Free Online Sources

### Redfin Data Center — Market Baselines (FREE, Best in Class)

**URL**: https://www.redfin.com/news/data-center/

Free downloadable CSVs of housing market metrics at ZIP code, city, and county level:
- Median sale price, homes sold, new listings
- Days on market, price drops, inventory
- Sale-to-list ratio
- Weekly and monthly updates

**Use**: Calibrate DOM thresholds, price reduction percentages, and seasonal patterns in the scoring engine. If the average DOM in a ZIP is 45 days, a property at 90 days is 2x the market — that's a stronger signal than in a market where 90 days is normal.

### FSBO Monitoring (Manual, Weekly)

| Source | URL | What to Look For |
|--------|-----|-----------------|
| Zillow (FSBO filter) | zillow.com | Filter "For Sale by Owner" in SWFLA |
| Facebook Marketplace | facebook.com/marketplace | Housing → For Sale, Cape Coral/Fort Myers/Naples |
| Craigslist | fortmyers.craigslist.org | Real Estate → By Owner |
| ForSaleByOwner.com | forsalebyowner.com | Search SWFLA area |
| FSBO.com | fsbo.com | Search by ZIP |

FSBO sellers who've been listed 30+ days are increasingly frustrated and receptive to agent outreach. Lead with value (market data, buyer access), not pitch.

### Google Alerts (Set and Forget)

**URL**: google.com/alerts

Set up these free alerts:

| Alert Query | Frequency |
|-------------|-----------|
| `"for sale by owner" "Cape Coral" OR "Fort Myers" OR "Naples"` | As-it-happens |
| `"must sell" OR "motivated seller" "Lee County" OR "Collier County"` | As-it-happens |
| `"estate sale" "Cape Coral" OR "Fort Myers" OR "Naples"` | Daily |
| `"foreclosure" "Lee County Florida"` | Daily |
| `site:craigslist.org "for sale by owner" "Cape Coral" OR "Fort Myers"` | Daily |

### Skip Tracing (For Contact Info After Lead Identification)

**Free tools** (for high-priority leads):
- TruePeopleSearch.com — phone, email, addresses
- FastPeopleSearch.com — similar coverage
- That'sThem.com — limited free searches/day

**Low-cost** (when volume warrants, $0.02-$0.10 per record):
- Tracerfy ($0.02/lead)
- BatchData ($0.03-$0.10/record, has API)
- REISkip (~$0.10/record, 85-90% match rate)

---

## How This Maps to Our Pipeline

### Currently Active (12 signals from MLS CSV data)

| Signal | Source | Status |
|--------|--------|--------|
| Expired listing (fresh) | Matrix CSV | ACTIVE |
| Expired listing (stale) | Matrix CSV | ACTIVE |
| Price reduction | Matrix CSV | ACTIVE |
| Multiple price reductions | Matrix CSV | ACTIVE |
| Severe price reduction (15%+) | Matrix CSV | ACTIVE |
| High days on market | Matrix CSV | ACTIVE |
| Withdrawn/relisted | Matrix CSV | ACTIVE |
| Back on market | Matrix CSV | ACTIVE |
| Low price range set | Matrix CSV | ACTIVE |
| Foreclosure flag | Matrix CSV | ACTIVE |
| Short sale flag | Matrix CSV | ACTIVE |
| Absentee owner | Matrix CSV | ACTIVE |

### Pre-Configured But Waiting for Data (8 signals)

These are already defined in `config/scoring_weights.yaml` with point values and decay functions. They just need data sources connected:

| Signal | Points | Source Needed | Available From |
|--------|--------|--------------|----------------|
| Pre-foreclosure | 20 | Lis Pendens filings | Clerk of Court (free) |
| Tax delinquent | 13 | Tax delinquency lists | Tax Collector (free) |
| Code violation | 12 | Code enforcement records | County portals (free) |
| Probate | 18 | Probate filings | Clerk of Court (free) |
| Divorce | 16 | Domestic relations filings | Clerk of Court (free) |
| Vacant property | 10 | Property appraiser + utility data | County PA (free) |
| Neighborhood hot | 5 | Market trend data | Redfin Data Center (free) |
| Agent churn | 7 | MLS listing agent history | Matrix CSV (free) |

### Signal Stacking (Already Configured)

When these data sources come online, the stacking multipliers activate automatically:

| Combo | Signals | Multiplier |
|-------|---------|-----------|
| Distressed Seller | expired + multiple price cuts + high DOM | 1.5x |
| Financial Distress | pre-foreclosure + tax delinquent | 2.0x |
| Life Event + Vacant | probate + absentee + vacant | 2.5x |
| Tired Landlord | absentee + code violation | 1.8x |
| Failed Sale | expired + withdrawn/relisted | 1.4x |
| Divorce Property | divorce + high DOM | 1.6x |

---

## Recommended Schedule

### Daily (Yani — 5-10 min)

- [ ] Check Matrix Hot Sheets for overnight changes
- [ ] Export expired + price drop searches using TheLeadEdge template
- [ ] Drop CSV into `Data/mls_imports/`

### Weekly (Trevor — 30 min)

- [ ] Search Lee Clerk for new Lis Pendens (last 7 days)
- [ ] Search Collier Clerk for new Lis Pendens (last 7 days)
- [ ] Quick scan of Craigslist/Zillow FSBO listings
- [ ] Check foreclosure auction calendars (lee.realforeclose.com, collier.realforeclose.com)

### Monthly (Trevor — 1-2 hours)

- [ ] Download fresh Collier County PA bulk data (Parcels + Sales CSVs)
- [ ] Download fresh LEEPA tax roll data
- [ ] Run absentee owner analysis (mailing ≠ site address)
- [ ] Check code violation portals for repeat violations
- [ ] Search both Clerks for new probate + divorce filings
- [ ] Download Redfin market data for scoring calibration

### Quarterly

- [ ] Download Sunbiz bulk file, cross-reference LLC-owned residential properties
- [ ] Review and update scoring weights based on any conversion data

### Annually (Feb-April)

- [ ] Request tax delinquency lists from Lee + Collier Tax Collectors
- [ ] Pre-foreclosure outreach window before May tax certificate sales

---

## Immediate Next Steps (This Week)

1. **Yani**: Create the TheLeadEdge custom export template in Matrix (one-time, 15 min)
2. **Yani**: Create the 7 saved searches listed above (one-time, 30 min)
3. **Yani**: Set up 5 Hot Sheets (one-time, 15 min)
4. **Yani**: Do first CSV export and drop into `Data/mls_imports/`
5. **Trevor**: Download Collier County PA bulk data from collierappraiser.com
6. **Trevor**: Download LEEPA tax roll + sale data from leepa.org
7. **Trevor**: Set up weekly Lis Pendens search routine at both Clerks
8. **Trevor**: Set up Google Alerts for FSBO/distress keywords
9. **Trevor**: Fix the MissingGreenlet bug in briefing pipeline
10. **Trevor**: Run first end-to-end test: CSV → import → score → briefing

---

## Key URLs Quick Reference

### MLS (Matrix)
- SWFLA MLS Matrix: matrix.swflamls.com
- NABOR Member Portal: mdweb.mmsi2.com/naples/

### Lee County
- Property Appraiser: leepa.org
- Parcel List Generator: leepa.org/OnlineReports/ParcelListGenerator.aspx
- Tax Roll Downloads: leepa.org/Roll/TaxRoll.aspx
- Sale Data Files: leepa.org/Roll/SDFTxt.aspx
- Clerk Official Records: leeclerk.org (search for Lis Pendens, probate, divorce)
- Code Enforcement: aca-prod.accela.com/LEECO/
- Tax Collector: leetc.com
- Foreclosure Auctions: lee.realforeclose.com

### Collier County
- Property Appraiser: collierappraiser.com
- Bulk Data Downloads: collierappraiser.com/Main_Data/DataDownloads.html
- Clerk Records Search: collierclerk.com/records-search/
- Code Enforcement: cvportal.collier.gov/cityviewweb
- Tax Collector: colliertaxcollector.com
- Foreclosure Auctions: collier.realforeclose.com

### State of Florida
- Sunbiz (LLC records): search.sunbiz.org
- Sunbiz Bulk Downloads: dos.fl.gov/sunbiz/other-services/data-downloads/
- DBPR License Search: myfloridalicense.com

### Free Market Data
- Redfin Data Center: redfin.com/news/data-center/

### Free Skip Tracing
- TruePeopleSearch.com
- FastPeopleSearch.com
- That'sThem.com

---

*Compiled from MLS Data Specialist (x2) and Systems Architect research, 2026-03-03*
