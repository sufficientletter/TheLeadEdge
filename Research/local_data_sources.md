# Local Market Data Sources & County-Level Public Records Access

> **Project**: TheLeadEdge — Real Estate Lead Generation System
> **Created**: 2026-02-28
> **Purpose**: Practical "how to actually access" guide for every public records data source identified in prior research
> **Prerequisite Reading**: [public_records_strategies.md](public_records_strategies.md) (identifies the 12 lead sources), [automation_integrations.md](automation_integrations.md) (automation layer)

---

## Executive Summary

Prior research identified 12 public record lead sources and explained *why* each is valuable. This document answers the practical question: **"How do I actually get this data?"**

For every data type, we cover:
- Where the data lives (county, state, federal, or third-party)
- What platform or system the source uses
- Whether you can get bulk/batch data or are limited to one-at-a-time lookups
- What it costs
- How to automate or semi-automate access
- State-by-state variations that matter

The bottom line: **You have three access tiers**, and most users should operate across all three simultaneously:

| Tier | Method | Cost | Effort | Best For |
|------|--------|------|--------|----------|
| 1 — DIY | County/court websites, manual searches | Free | High | Learning the data, small markets |
| 2 — Aggregator APIs | ATTOM, PropertyRadar, BatchData, CoreLogic | $50-500/mo | Low | Automation, multi-county coverage |
| 3 — FOIA/Custom Requests | Public records requests for data not online | Free-$50/request | Medium | Utility disconnects, unique datasets |

---

## Table of Contents

1. [County Recorder / Clerk Offices](#1-county-recorder--clerk-offices)
2. [Property Tax & Assessment Data](#2-property-tax--assessment-data)
3. [Court Records](#3-court-records)
4. [Code Enforcement & Building Permits](#4-code-enforcement--building-permits)
5. [Third-Party Data Aggregators](#5-third-party-data-aggregators)
6. [FOIA / Public Records Requests](#6-foia--public-records-requests)
7. [National Change of Address (NCOA)](#7-national-change-of-address-ncoa)
8. [Voter Registration & Vehicle Records](#8-voter-registration--vehicle-records)
9. [Automating Public Records Access](#9-automating-public-records-access)
10. [State-by-State Snapshot](#10-state-by-state-snapshot)

---

## 1. County Recorder / Clerk Offices

### 1.1 What the County Recorder Holds

The County Recorder (also called the Clerk of Court, Register of Deeds, or County Clerk depending on the state) is the repository for all recorded documents related to real property:

- **Deeds** (warranty, quitclaim, special warranty, trustee's deeds)
- **Mortgages / Deeds of Trust** (new liens, refinances, releases)
- **Notices of Default / Lis Pendens** (pre-foreclosure signals)
- **Notices of Trustee Sale** (foreclosure progression)
- **Mechanic's Liens** (unpaid contractors — can signal distress)
- **Affidavits of Heirship / Death** (estate and probate indicators)
- **Powers of Attorney** (can indicate elderly/incapacitated owner)
- **Releases of Lien** (mortgage paid off — owner has full equity)
- **Easements, Covenants, and Plats**

### 1.2 How County Recorder Websites Typically Work

Almost all counties have moved to electronic recording and offer some level of online search. Here is what to expect:

**Typical Search Interface:**
- Name search (grantor/grantee) — most common entry point
- Document type filter — critical for narrowing results
- Date range filter — use this to find recent filings
- Property address or legal description search — available in better systems
- Book/page or instrument number — for pulling a specific document you already know about

**What You Can Typically Do for Free:**
- Search the index (names, document types, dates, book/page numbers)
- See the summary information for each recording

**What Usually Costs Money:**
- Viewing the actual recorded document image (typically $0.50-$2.00 per page)
- Downloading or printing document images
- Some counties charge per search session or have subscription models

**Common Limitations:**
- Many counties only have electronic records going back to a certain date (commonly 1990-2005, though major counties may go back further)
- Older records require in-person visit to the physical office
- Search by address is often not available (you must know owner names)
- No bulk download or export in most county systems

### 1.3 Common County Recorder Platforms

Counties do not build their own software. They purchase from a small number of vendors. Recognizing the platform helps you know what features are available:

| Platform | Market Share | Notable Features | States Where Common |
|----------|-------------|-----------------|---------------------|
| **Tyler Technologies (Eagle Recorder)** | ~30% of US counties | Robust search, document imaging, some offer subscription access | Nationwide, dominant |
| **Cott Systems / Kofile** | ~15% of counties | Simpler interface, common in smaller counties | Midwest, South |
| **Granicus (GovQA)** | Growing | Modern UI, used more for FOIA portals but expanding into records | Nationwide |
| **Fidlar Technologies** | ~10% | Strong in Midwest | IA, IL, IN, WI, MN |
| **CSC (Corporation Service Company)** | Common for UCC filings | More focused on business/commercial filings | Nationwide |
| **Avenu / Harris Govern** | Regional | Integrated tax + recording | TX, OK, AL, southeast |
| **Hyland OnBase** | Enterprise | Document management, larger counties | Major metro counties |

**How to identify the platform**: Visit the county recorder website and look at the URL or footer. Tyler Technologies sites often have "tylerhost.net" or "fidlar.com" in the URL. The login page or about page usually names the vendor.

### 1.4 Online vs. In-Person Access

| Feature | Online | In-Person |
|---------|--------|-----------|
| Index search | Yes (most counties) | Yes |
| Document images | Paid, some free | Free viewing, paid copies |
| Historical records (pre-1990) | Often not available | Available |
| Bulk data requests | Rarely | Can request custom extracts |
| Staff assistance with complex searches | No | Yes (very valuable) |
| Hours | 24/7 | Business hours only |
| Automation potential | Yes (with effort) | None |

**Pro tip**: For your first visit to any county's data, go in person. The staff at the recorder's office can show you the search system, explain the document type codes unique to their county, and help you run sample searches. This saves hours of trial and error online.

### 1.5 Batch Download and Bulk Access

Most counties do NOT offer easy bulk download. Here are your options:

| Method | Availability | What You Get |
|--------|-------------|-------------|
| **County data subscription** | Some large counties (Maricopa, Cook, LA, etc.) | Periodic data dumps, sometimes real-time feed |
| **FOIA request for recording data** | All counties | One-time data extract, CSV or database file |
| **Third-party aggregator** | ATTOM, CoreLogic, DataTree | Nationwide recording data via API, already structured |
| **Title company data** | Via relationship | Title companies have access to full recording history; some will share leads |

**Counties known to offer direct data subscriptions or downloads:**
- Maricopa County, AZ (recorder.maricopa.gov) — offers bulk data products
- Cook County, IL (cookrecorder.com) — has a data download section
- Los Angeles County, CA (registrar-recorder) — subscription services available
- King County, WA — offers data sets via open data portal
- Harris County, TX — real property records available in bulk

### 1.6 Key Documents to Monitor for Lead Generation

Set up a regular monitoring cadence for these document types:

| Document Type | Lead Signal | Check Frequency |
|---------------|-------------|-----------------|
| Notice of Default / Lis Pendens | Pre-foreclosure | Weekly |
| Notice of Trustee Sale | Foreclosure advancing | Weekly |
| Death Affidavit / Affidavit of Heirship | Inherited property | Weekly |
| Quitclaim Deed (especially interspousal) | Divorce settlement | Weekly |
| Power of Attorney | Elderly/incapacitated owner | Monthly |
| Mechanic's Lien | Contractor dispute, potential distress | Monthly |
| Release of Lien / Satisfaction of Mortgage | Full equity owner | Monthly |
| Trustee's Deed Upon Sale | Foreclosure completed (REO) | Weekly |

---

## 2. Property Tax & Assessment Data

### 2.1 County Assessor vs. County Treasurer

These are separate offices with different data:

| Office | What They Have | Lead Value |
|--------|---------------|------------|
| **County Assessor** | Property valuations, owner names, mailing addresses, legal descriptions, property characteristics (bedrooms, sq ft, lot size, year built), assessed value history | Absentee owner identification, property details, ownership duration |
| **County Treasurer / Tax Collector** | Tax bills, payment history, delinquency status, tax lien information, tax sale schedules | Tax delinquency leads, upcoming tax sales |

### 2.2 Common GIS / Parcel Viewer Platforms

Most counties offer an interactive parcel map (GIS viewer) that is incredibly useful for property research. These are the dominant platforms:

| Platform | Description | Where Common | Key Features |
|----------|-------------|-------------|-------------|
| **Beacon / Schneider Corp** | Most popular parcel viewer in the US, now owned by Catalis | Nationwide, 1000+ counties | Clean interface, property cards, aerial imagery, tax data, owner search, export capabilities |
| **Tyler iasWorld** | Tyler Technologies' CAMA system | Large counties nationwide | Deep property data, comparable sales, assessment history |
| **Esri ArcGIS Online** | Enterprise GIS, many counties publish parcel layers | Major metro areas | Powerful mapping, custom layers, some offer open data downloads |
| **QPUBLIC (Grant Street Group)** | Popular in Southeast US | GA, AL, NC, SC, TN | Clean, searchable, free access, property cards with photos |
| **Vision Government Solutions** | Common in Northeast US | MA, CT, NH, VT, ME, NY | Assessment data, property cards, sales history |
| **Patriot Properties** | Northeast focused | MA, NH, CT | Detailed assessment cards |
| **CAMA (various vendors)** | Computer Assisted Mass Appraisal — generic term for assessment databases | Everywhere | The underlying database behind the parcel viewer; sometimes accessible directly |

**How to find your county's parcel viewer:**
1. Search "[County Name] parcel viewer" or "[County Name] GIS map"
2. Search "[County Name] property search" or "[County Name] assessor"
3. Check the county's main website for a "Property" or "GIS" link
4. Try publicrecords.netronline.com — it links to every county's property search

### 2.3 How to Identify Absentee Owners

This is one of the most valuable filters for lead generation. An absentee owner is someone whose **mailing address** (where tax bills are sent) differs from the **site address** (the property itself).

**Where to find the mailing address:**
- County Assessor website — most display both site and mailing address
- County Treasurer/Tax records — tax bills are sent to the mailing address
- GIS/Parcel viewer — usually shows "owner address" or "mail to" address

**How to filter for absentee owners:**
- If the county system allows export: Download all properties, then filter where mailing address != site address
- In aggregator tools (ATTOM, PropertyRadar, PropStream): Built-in "absentee owner" filter
- Manual approach: Search by ZIP code, visually scan for mailing addresses in different states/cities

**Types of absentee owners (each has different motivation):**

| Type | How to Identify | Motivation Level |
|------|----------------|-----------------|
| Out-of-state owner | Mailing address in different state | High — distance makes management hard |
| In-state, different city | Mailing address in same state, different city | Medium |
| Same city, different address | Likely an investor or inherited property | Medium |
| Corporate/LLC owner | Entity name on tax records | Variable — may be investor exiting |
| Trust owner | Trust name in owner field | Medium-High — often estate settlement |
| PO Box mailing address | Tax bills go to PO Box | Investigate further |

### 2.4 Tax Delinquency List Access

Tax delinquency lists are among the highest-value lead sources because they indicate financial distress. Accessing them varies significantly by county:

**Tier 1 — Published Online (easiest):**
Some counties publish delinquent tax lists on their website, often as a legal requirement before tax sales. Search for:
- "[County] delinquent tax list"
- "[County] tax sale list"
- "[County] tax lien sale"
- "[County] delinquent property taxes"

These are usually published as PDF lists 30-90 days before the annual tax sale.

**Tier 2 — Available Upon Request:**
Many counties will provide the delinquency list if you ask. Contact the County Treasurer's office and request:
- List of properties with delinquent taxes exceeding [1 year / 2 years / amount threshold]
- Request in electronic format (CSV or Excel)
- This may require a formal public records request (see Section 6)

**Tier 3 — FOIA Required:**
Some counties treat delinquency as confidential until the statutory publication period. You will need to file a public records request. Some counties charge fees for custom data extracts.

**Tier 4 — Third-Party Aggregators:**
ATTOM Data provides nationwide tax delinquency data through their API. PropertyRadar covers it for western states. This is the path of least resistance if you are covering multiple counties.

### 2.5 Annual Tax Sale Information

Tax sales are goldmines for lead generation — not just for purchasing at auction, but for identifying distressed owners *before* the sale who may prefer a traditional sale:

**Types of tax sales:**
- **Tax Lien Sales**: County sells the lien (right to collect back taxes + interest). Owner retains the property but has a redemption period. Common in FL, AZ, NJ, IL, CO, MD.
- **Tax Deed Sales**: County sells the property itself. Owner loses the property. Common in CA, TX, GA, NY, MI.
- **Hybrid / Redeemable Deed**: Some states use a hybrid approach.

**Finding tax sale information:**
1. County Treasurer website — look for "Tax Sale," "Tax Lien Auction," or "Delinquent Tax Sale"
2. Search "[County] annual tax lien sale [year]"
3. Many counties use third-party auction platforms:
   - **RealAuction** (realauction.com) — common in FL, TX
   - **GovEase** (govease.com) — growing platform for tax sales
   - **Bid4Assets** (bid4assets.com) — nationwide tax sale marketplace
   - **SRI (Sargent & Roberts Inc.)** — conducts tax sales for many counties

**Lead generation timing:**
- 60-90 days before the tax sale: Lists are published. Contact owners who still have equity.
- Owners on the list for the first time are most likely to respond to outreach about selling.
- After the sale: Properties that did not sell revert to the county (struck-off) and may be available directly.

---

## 3. Court Records

### 3.1 Court System Structure

Understanding where to search requires understanding how courts are organized:

```
FEDERAL COURTS (PACER)
├── Bankruptcy Court (Ch 7, 11, 13)
├── District Court (federal civil/criminal)
└── Appeals Court

STATE COURTS (varies by state)
├── Supreme Court / Court of Appeals
├── Superior Court / Circuit Court / District Court
│   ├── Civil Division (general lawsuits)
│   ├── Family Division (divorce, custody)
│   └── Probate Division (estates, guardianships)
├── County Court / Municipal Court
└── Small Claims / Justice Court
```

For lead generation, you primarily care about:
- **Probate Division** — inherited properties
- **Family Division** — divorce filings
- **Federal Bankruptcy Court** — bankruptcy filings (via PACER)
- **Civil Division** — foreclosure (in judicial foreclosure states)

### 3.2 Probate Court Case Search Platforms

Probate filings are your entry point for inherited property leads. Here is how to find them:

**Step 1: Identify your court system's platform**

| Platform | Coverage | URL Pattern | Notes |
|----------|----------|------------|-------|
| **Tyler Technologies Odyssey** | 1,500+ courts in 30+ states | Usually `[court].tylerhost.net/` | Most common. Look for "Odyssey Case Manager" or "Odyssey Portal" |
| **Tyler Technologies RE:Search** | Growing | Various | Newer portal interface |
| **Tybera (FullCourt)** | 500+ courts, rural/smaller counties | Various | Common in smaller jurisdictions |
| **Journal Technologies (eCourt)** | Several states (CA courts use this) | Various | Also known as Sustain/eCourt |
| **Thomson Reuters C-Track** | Various | Various | Larger courts |
| **Hensler NetworkCourt** | Regional | Various | Mostly Midwest |
| **State-specific portals** | Varies | See state-by-state section | Many states built their own |

**Step 2: Search for probate cases**

Once you find the court's online search portal:
1. Navigate to "Case Search" or "Public Access"
2. Select case type: look for "Probate," "Estate," "Decedent's Estate," "Succession," or "Surrogate"
3. Filter by filing date (last 30-90 days for fresh leads)
4. Look at the case details for:
   - Name of decedent
   - Name and address of personal representative (executor/administrator)
   - Whether real property is listed in the petition
5. Cross-reference the decedent's name with the county assessor to find their property

**Common probate case type codes:**

| Code | Description | States Where Used |
|------|-------------|-------------------|
| PB | Probate | Common |
| ES | Estate | Common |
| DE | Decedent's Estate | TX, others |
| PR | Probate | AZ, others |
| SU | Succession | LA |
| IN | Intestate | Various |
| TE | Testate (with will) | Various |
| GA / GC | Guardianship / Conservatorship | Various (not the target, but related) |

### 3.3 Family Court (Divorce) — What Is Public vs. Sealed

Divorce filings are public records in every state, but the level of accessible detail varies:

**Typically Public:**
- The fact that a divorce was filed (case number, parties' names, filing date)
- Case type and status
- Hearing dates and court orders (general)
- Final decree of divorce (the judgment itself)

**Typically Sealed or Restricted:**
- Financial declarations and asset disclosures
- Child custody evaluations
- Domestic violence protective orders (some states)
- Settlement agreement details (some jurisdictions seal these)
- Mental health or substance abuse records

**For lead generation, you only need the public information:**
1. Names of both parties
2. Filing date
3. Cross-reference names with county assessor to determine if they own property
4. If they own property, they are a potential lead (property will likely need to be sold or refinanced)

**How to search:**
- Same court portals listed above (Odyssey, etc.)
- Case type codes: "DR" (Dissolution/Domestic Relations), "FM" (Family), "DV" (Divorce), "DM" (Dissolution of Marriage), "FL" (Family Law)
- Filter by recent filings (last 30-90 days)
- Some states restrict online access to family court cases and require in-person searches

### 3.4 Federal PACER for Bankruptcy Filings

**PACER (Public Access to Court Electronic Records)** is the federal system for all federal court records, including bankruptcy.

**Access:**
- URL: pacer.uscourts.gov
- Registration: Free to register (requires name, address, and verification)
- Cost: $0.10 per page viewed (capped at $3.00 per document). First $30 per quarter is free (since the fee waiver threshold was raised). This means small-volume users effectively pay nothing.
- Note: PACER recently launched a new system called PACER Case Locator for cross-district searches

**Searching for Bankruptcy Filings:**
1. Go to pacer.uscourts.gov
2. Use the PACER Case Locator to search across all bankruptcy courts
3. Or go directly to the specific district's bankruptcy court (e.g., azb.uscourts.gov for Arizona Bankruptcy Court)
4. Search by debtor name, case number, or filing date
5. Filter by chapter: Chapter 7 (liquidation), Chapter 13 (reorganization/payment plan), Chapter 11 (business reorganization)

**Bankruptcy types relevant to real estate leads:**

| Chapter | What It Means | Lead Potential |
|---------|---------------|----------------|
| Chapter 7 | Liquidation — non-exempt assets sold | High — property may be sold by trustee |
| Chapter 13 | Payment plan — debtor keeps assets | Medium — indicates financial stress, may list later |
| Chapter 11 | Business reorganization | Lower for residential, high for commercial |
| Chapter 12 | Family farmer/fisherman | Niche — rural property opportunities |

**Key PACER fields to look for:**
- Debtor name and address
- Filing date and chapter
- Whether real property is listed in the schedules (Schedule A/B)
- Trustee name (for Chapter 7 sales)
- Whether the debtor has filed a motion to sell real property

**Automation note:** PACER does not offer a public API. However, third-party services like CourtListener (free.law) provide some PACER data for free and offer APIs. PACER also offers a RSS-like notification service called NextGen CM/ECF that can email you when new cases are filed in a specific court.

### 3.5 State Court E-Filing Portals

Many states have built statewide unified court portals. These are often the easiest way to search across all counties in a state:

| State | Portal Name | URL | Coverage |
|-------|------------|-----|----------|
| Arizona | AZCourt | azcourts.gov/publicaccess | Maricopa, Pima, and most counties |
| California | No unified portal; county-by-county | Various | LA uses lacourt.org, SF uses sfsuperiorcourt.org |
| Colorado | Colorado Judicial Branch | courts.state.co.us | Statewide |
| Florida | Clerks of Court portals | myflcourtaccess.com, clerk websites | County-level, some unified |
| Georgia | Georgia Courts (Odyssey) | Various by county | Large counties online |
| Illinois | Judici (many counties) | judici.com | 65+ counties |
| Indiana | MyCase / Odyssey | mycase.in.gov | Statewide |
| Michigan | Michigan Courts Case Search | courts.michigan.gov | Statewide |
| Minnesota | Minnesota Court Records Online | pa.courts.state.mn.us | Statewide |
| New York | eCourts | iapps.courts.state.ny.us | Statewide (complex system) |
| North Carolina | eCourts (Odyssey) | portal.nccourts.org | Statewide rollout in progress |
| Ohio | County-by-county | Various | Fragmented |
| Oregon | Oregon Judicial Dept | courts.oregon.gov/ojd | Statewide |
| Pennsylvania | UJS Portal | ujsportal.pacourts.us | Statewide |
| Texas | County-by-county | Various | Fragmented; large counties have good portals |
| Virginia | Court Case Information | courts.state.va.us | Statewide |
| Washington | JIS Link | dw.courts.wa.gov | Statewide |
| Wisconsin | CCAP | wcca.wicourts.gov | Statewide (excellent system) |

**Tip**: States with unified statewide portals (Indiana, Minnesota, Pennsylvania, Washington, Wisconsin) are the easiest to work with for multi-county searches.

---

## 4. Code Enforcement & Building Permits

### 4.1 Why This Data Is at the Municipal Level

Unlike recorder and tax data (which is at the **county** level), code enforcement and building permits are typically managed at the **city/municipality** level. This means:
- You need to check each city individually, not just the county
- Unincorporated areas are handled by the county
- Each city may use a different platform
- Small cities may not have online systems at all

### 4.2 Municipal Code Violation Databases

Code violations indicate distressed properties where owners cannot or will not maintain the property. This is a high-probability seller signal, especially when combined with absentee ownership or tax delinquency.

**Common types of code violations to look for:**
- Tall grass/weeds (neglect signal)
- Structural damage (roof, foundation)
- Unsafe/uninhabitable conditions
- Junk vehicles/debris accumulation
- Boarded-up or vacant property registrations
- Condemned/unfit for habitation orders
- Repeat violations on the same property (strongest signal)

**How to access:**
1. Search "[City Name] code enforcement" or "[City Name] code violation search"
2. Some cities have online searchable databases
3. Many do not have online search — you must file a public records request or visit in person
4. City council/planning commission meeting minutes often list properties with code actions

**Cities with online code violation search:**
- Most large cities (population 100,000+) have some form of online lookup
- Usually found in the city's "Development Services," "Neighborhood Services," or "Code Compliance" department
- Some cities use 311 systems (like SeeClickFix or QAlert) where violations are publicly visible

### 4.3 Building Permit Portals

Building permits are publicly available and reveal:
- **Demolition permits** — property being torn down (vacant land opportunity, or teardown/rebuild)
- **Major renovation permits** — owner investing in property (may sell after flip)
- **New construction permits** — development activity in a neighborhood
- **Roofing/HVAC/plumbing permits** — deferred maintenance being addressed
- **Electrical service upgrade** — often pulled before a listing to address inspection items

**Common permit portal platforms:**

| Platform | Description | Where Common | URL Clue |
|----------|-------------|-------------|----------|
| **Accela Citizen Access (ACA)** | Market leader for permitting software | 1,000+ jurisdictions nationwide | URL contains "citizenaccess.com" or "accela.com" |
| **Tyler Technologies EnerGov** | Growing competitor to Accela | Hundreds of cities | URL contains "energov" or "tylerhost.net" |
| **Citizenserve** | Mid-market permitting platform | Smaller cities | citizenserve.com |
| **OpenGov / Cartegraph** | Modern cloud platform | Growing adoption | opengov.com |
| **CommunityCore / ViewPoint** | Older platform, still in use | Various | Various |
| **iWorQ** | Cloud-based, smaller cities | Rural and suburban | iworq.net |
| **MyGovernmentOnline** | Southeast US focused | FL, GA, SC | mygovernmentonline.org |

**How to search for building permits:**
1. Search "[City Name] building permit search" or "[City Name] permit portal"
2. Navigate to the city's Building/Development Services department
3. Search by address, permit number, or owner name
4. Filter by permit type (demolition, new construction, alteration)
5. Look at permit valuation — high-value permits ($50,000+) indicate major work

### 4.4 How to Identify Key Permit Types

| Permit Type | What It Signals | Lead Strategy |
|-------------|----------------|---------------|
| **Demolition** | Property being cleared; new development or vacant land sale coming | Contact owner about selling the land; or track for new construction listing |
| **Major renovation ($50K+)** | Likely a flip investor; property may be listed in 3-6 months | Track the property; when renovation completes, investor may list |
| **Solar panel installation** | Owner likely staying long-term | Low-priority lead |
| **ADU / Accessory Dwelling Unit** | Owner adding rental income or multigenerational living | Moderate — may trigger future sale due to property value increase |
| **Foundation/structural repair** | Addressing major issues, possibly for sale preparation | Watch for listing in 1-3 months |
| **Multiple permits in 30 days** | Rapid improvement = likely preparing to sell | High priority — may list within 60 days |

### 4.5 Condemned Property Lists

Condemned properties are the most distressed of all code violations and represent highly motivated (or absent) owners:

**How to find condemned property lists:**
1. Contact the city's Code Enforcement or Building Department
2. Request the list of properties deemed "unfit for habitation," "condemned," or under a "vacate order"
3. Some cities maintain a "vacant building registry" or "abandoned property registry" — these are often public
4. Check city council meeting minutes and resolutions for condemnation actions
5. The city attorney's office may have lists of properties in receivership or where the city is pursuing demolition

**FOIA approach:**
File a public records request for: "A list of all residential properties currently classified as condemned, unfit for habitation, or subject to a demolition order within [City Name], including property address, owner name, date of condemnation, and current status."

---

## 5. Third-Party Data Aggregators

Third-party aggregators compile public records from thousands of counties and courts into unified, searchable, API-accessible databases. This is the most efficient path for multi-county coverage and automation.

### 5.1 ATTOM Data Solutions

**Overview**: The largest and most comprehensive property data aggregator in the US. ATTOM licenses data to real estate platforms, lenders, insurers, and investors.

**Data Coverage:**
- 155 million+ US properties
- 99%+ of US counties covered
- Recording data (deeds, mortgages, liens, NODs, foreclosures)
- Tax and assessment data
- Property characteristics (beds, baths, sq ft, lot size, year built, etc.)
- Transaction history (sales, prices, dates)
- Pre-foreclosure / foreclosure pipeline data
- Automated Valuation Models (AVMs)
- Natural hazard data
- Neighborhood/school data
- Building permits (select markets)

**API Capabilities:**
- RESTful API with JSON responses
- Endpoints organized by data type: Property, AVM, Sale, Assessment, Foreclosure, School, etc.
- Bulk endpoints for batch processing (up to 100 properties per call)
- Supports address lookup, APN lookup, and geographic (lat/lng + radius) queries
- Incremental data feeds for monitoring changes

**Pricing Tiers (approximate, as of 2025-2026):**

| Tier | Monthly Cost | API Calls | Best For |
|------|-------------|-----------|----------|
| Starter / Explorer | ~$100-150/mo | 5,000-10,000 calls | Testing, small-market agent |
| Professional | ~$250-350/mo | 25,000-50,000 calls | Single-market lead gen operation |
| Enterprise | ~$500-1,000+/mo | Unlimited / negotiated | Multi-market, heavy automation |
| Bulk Data License | Custom pricing | Full database access | Building a platform |

**Note**: ATTOM does not publicly list exact pricing. You must contact their sales team. Pricing depends heavily on which data products you license and your use case. Real estate lead generation is a standard use case they support.

**Key API endpoints for lead generation:**

```
/property/detail          — Property characteristics, owner info
/property/expandedprofile — Full property + assessment + tax data
/sale/history             — Transaction history
/assessment/detail        — Tax assessment data
/foreclosure/detail       — Pre-foreclosure, auction, REO status
/avm/detail               — Automated valuation
/property/address         — Address standardization/lookup
```

**Strengths**: Broadest coverage, most data types, best-documented API, strong developer support
**Weaknesses**: Most expensive, some data has 30-60 day lag from county recording, not real-time for court filings

### 5.2 PropertyRadar

**Overview**: Originally built for California/Western US markets, PropertyRadar is focused on property owner intelligence and has strong pre-foreclosure/foreclosure monitoring.

**Data Coverage:**
- Strong in Western US (CA, AZ, NV, OR, WA, CO, TX, UT, ID)
- Expanding nationally but not yet at ATTOM's coverage level
- Pre-foreclosure / NOD filings
- Foreclosure auction schedules
- Tax delinquency data
- Absentee owner identification
- Probate filings (select counties)
- Divorce filings (select counties)
- Code violations (select markets)
- Mailing lists with owner contact info

**Pricing:**

| Plan | Monthly Cost | Properties/Lists | Features |
|------|-------------|-----------------|----------|
| Essentials | ~$59/mo | Limited exports | Basic search, property details |
| Complete | ~$119/mo | More exports | Full data access, lists, mail merge |
| Professional | ~$199/mo | Bulk exports | API access, integrations, team features |

**Key Differentiators:**
- Purpose-built for real estate investors and agents (not a generic data company)
- Strong list-building and marketing workflow (build list -> skip trace -> mail)
- Map-based interface for geographic farming
- Alerts/monitoring for new filings in your target area
- Direct mail integration

**API**: Available on Professional plan. REST API with property search, list management, and monitoring endpoints.

**Strengths**: Best UI for agents/investors, strong foreclosure data in western states, integrated marketing workflows
**Weaknesses**: Coverage weaker outside Western US, less raw data depth than ATTOM, fewer property characteristics

### 5.3 CoreLogic

**Overview**: The largest property data company in the US (larger than ATTOM), but primarily serves enterprise clients (lenders, insurers, government). Their data feeds power many of the consumer-facing tools you already know (Zillow, Redfin, many MLS systems).

**What They Have:**
- Property data on virtually every US parcel
- MLS data aggregation (via Trestle, formerly ListHub)
- Title and deed data
- Tax data
- Flood/hazard data
- Mortgage data (origination, performance)
- Automated Valuation Models (AVMs)
- Rental analytics

**Who Uses It:**
- Banks, mortgage lenders, and servicers
- Insurance companies
- Government agencies
- Title companies
- MLS platforms (many run on CoreLogic technology)
- Large real estate brokerages

**Pricing:**
- Enterprise only. Not priced for individual agents or small operations
- Typically five-figure annual contracts minimum
- You are more likely to access CoreLogic data *through* another product (like your MLS, which probably runs on CoreLogic/Trestle, or through a title company that licenses CoreLogic)

**Relevance to TheLeadEdge**: You probably will not license CoreLogic directly. Instead, recognize that CoreLogic data already flows through your MLS system. Your RESO Web API access (through Trestle) is CoreLogic infrastructure.

### 5.4 Reonomy

**Overview**: Commercial real estate data platform with property owner intelligence. Has residential data as well, but the focus is commercial.

**Data Coverage:**
- Commercial and residential property data
- Owner identification and contact info (even behind LLCs)
- Mortgage and lien data
- Sale history and transaction data
- Tenant data for commercial properties
- Building permits

**Pricing:**
- Starts around $49/mo for basic access
- Professional plans $99-249/mo with more search volume
- Enterprise/API access requires sales discussion

**Relevance to TheLeadEdge**: Useful primarily if you want to identify commercial property owners or pierce the LLC veil (identify the actual person behind an LLC-owned property). For pure residential lead gen, ATTOM or PropertyRadar offer better value.

### 5.5 DataTree (First American)

**Overview**: DataTree is First American Financial Corporation's public-facing property data platform. First American is one of the "big four" title insurance companies, so they have deep title and recording data.

**Data Coverage:**
- Title chain data (who has owned the property, in order)
- Deed and mortgage recordings
- Tax and assessment data
- Property characteristics
- Lien data (all liens, not just mortgages)
- Document images (actual recorded document copies)
- Neighborhood data

**Pricing:**
- Subscription model, roughly $50-150/mo depending on volume
- Document image viewing is additional cost per page
- Bulk/API pricing available for higher volumes

**Key Differentiator**: DataTree is the best source for **title chain** data (the full history of ownership transfers, mortgages, and liens on a property). If you need to understand the complete encumbrance picture or verify ownership history, DataTree is the go-to.

**API**: Available. REST API for property search, owner lookup, document retrieval, and title chain.

### 5.6 BatchData

**Overview**: A newer entrant focused on providing property data and skip tracing (owner contact info) at lower price points, optimized for bulk operations.

**Data Coverage:**
- Property data (characteristics, ownership, valuation)
- Skip tracing (phone numbers, emails for property owners)
- Vacancy detection
- Property type classification
- Cash buyer identification
- Occupancy status

**Pricing:**

| Product | Pricing Model | Approximate Cost |
|---------|--------------|-----------------|
| Property Data API | Per-record | ~$0.03-0.10 per record |
| Skip Tracing | Per-record | ~$0.10-0.15 per record |
| Bulk Batch Processing | Volume discount | Lower per-record at scale |
| Monthly Subscription | Flat rate + usage | ~$50-100/mo base |

**API**: REST API designed for batch processing. Upload a list of addresses, get back enriched data.

**Strengths**: Best pricing for bulk operations, good skip tracing hit rates, simple API
**Weaknesses**: Less depth per property than ATTOM or DataTree, no court records, no foreclosure pipeline data

### 5.7 Aggregator Comparison Matrix

| Feature | ATTOM | PropertyRadar | CoreLogic | Reonomy | DataTree | BatchData |
|---------|-------|---------------|-----------|---------|----------|-----------|
| **Coverage** | 155M+ properties | Strong West US, growing | Virtually all US parcels | National, commercial focus | National (via First American) | National |
| **Foreclosure Data** | Excellent | Excellent (West US) | Excellent | Limited | Good | Limited |
| **Tax Delinquency** | Yes | Yes | Yes | Limited | Limited | No |
| **Probate/Divorce** | Limited | Select counties | No direct | No | No | No |
| **Property Characteristics** | Excellent | Good | Excellent | Good | Good | Basic |
| **Skip Tracing** | Limited | Yes (add-on) | No | Owner contact info | No | Excellent |
| **AVM/Valuation** | Yes | No | Yes (industry standard) | Basic | No | No |
| **Document Images** | Some markets | No | Through title affiliates | No | Yes (excellent) | No |
| **API Quality** | Excellent (REST, well-documented) | Good (REST) | Enterprise-grade | Good (REST) | Good (REST) | Good (REST, batch-oriented) |
| **Best For** | Comprehensive data + automation | Western US lead gen | Enterprise / indirect use | Commercial property | Title chain / deed research | Bulk skip tracing |
| **Monthly Cost** | $100-500+ | $59-199 | Enterprise (five figures) | $49-249 | $50-150 | $50-100 |
| **Data Freshness** | 30-60 day lag on recordings | Near-real-time foreclosure in core markets | Variable | Weekly updates | Near-real-time for recordings | Variable |

### 5.8 Recommended Stack for TheLeadEdge

Based on cost, coverage, and API quality:

| Priority | Service | Monthly Cost | What You Use It For |
|----------|---------|-------------|---------------------|
| 1 | **ATTOM Data** | ~$250/mo | Core property data, foreclosure pipeline, tax data, AVM, ownership history |
| 2 | **PropertyRadar** | ~$119/mo | Pre-foreclosure monitoring, absentee owner lists, direct mail workflow (if in Western US market) |
| 3 | **BatchData** | ~$50/mo | Skip tracing (owner phone/email), bulk data enrichment |
| Optional | **DataTree** | ~$75/mo | Title chain research when you need deep ownership history |

**Total**: ~$420-500/mo covers comprehensive data access across all lead sources except probate/divorce (which require direct court access — see Section 3).

---

## 6. FOIA / Public Records Requests

### 6.1 Overview

The Freedom of Information Act (FOIA) applies to **federal** agencies. Each state has its own equivalent law (often called "Open Records Act," "Public Records Act," "Right to Know Law," or "Sunshine Law") that governs access to **state and local** records.

For real estate lead generation, you are requesting records from **local** agencies (counties, cities, utility districts), so you will use the **state** public records law, not the federal FOIA. However, the term "FOIA" is commonly used colloquially for all public records requests.

### 6.2 When to Use a Public Records Request

File a public records request when:
- The data you want is not available online
- You need bulk data (a list, not individual lookups)
- The data is only available in-person but you want it electronically
- You want data that the agency tracks but does not publish (e.g., utility disconnections)

### 6.3 Template FOIA Request Letters

**Template 1: Utility Disconnection Records (Vacancy Detection)**

```
[Your Name]
[Your Address]
[Date]

[City/Municipal Utility Department]
[Address]

RE: Public Records Request — Utility Service Disconnections

Dear Records Custodian,

Pursuant to the [State Name] Public Records Act ([cite statute, e.g.,
"Arizona Revised Statutes Section 39-121" or "California Government
Code Section 6250"]), I am requesting the following records:

1. A list of all residential properties within [City Name / ZIP codes]
   that have had water and/or electric service disconnected, terminated,
   or placed on inactive/vacant status during the period of [start date]
   through [end date].

2. For each property, I request the following fields:
   - Service address
   - Date of disconnection or status change
   - Type of disconnection (voluntary, non-payment, or vacant)
   - Account holder name (if public record)

I request this data in electronic format (CSV, Excel, or similar
spreadsheet format) if available.

I understand there may be reasonable fees associated with this request
and am willing to pay up to $[50-100] without prior approval. If the
estimated cost exceeds this amount, please contact me before processing.

Please respond within the timeframe required by [State Public Records
Act] (typically 3-10 business days for acknowledgment).

Thank you for your assistance.

Sincerely,
[Your Name]
[Phone Number]
[Email Address]
```

**Template 2: Code Violation List**

```
[Your Name]
[Your Address]
[Date]

[City Code Enforcement / Neighborhood Services Department]
[Address]

RE: Public Records Request — Code Enforcement Violations

Dear Records Custodian,

Pursuant to the [State Name] Public Records Act, I am requesting
the following records:

1. A list of all residential properties with open/active code
   enforcement violations within [City Name / target area] as of
   [date], including:
   - Property address
   - Violation type/code
   - Date violation was issued
   - Current status (open, pending hearing, abated, etc.)
   - Property owner name (as recorded)

2. A list of all residential properties that have been declared
   condemned, unfit for habitation, or subject to a demolition
   order within the past 24 months, including property address,
   owner name, and date of order.

I request this data in electronic format (CSV, Excel, or database
export) if available.

I am willing to pay reasonable fees. Please advise of costs before
processing if they exceed $[50].

Thank you,
[Your Name]
[Phone Number]
[Email Address]
```

**Template 3: Tax Delinquency List**

```
[Your Name]
[Your Address]
[Date]

[County Treasurer / Tax Collector]
[Address]

RE: Public Records Request — Delinquent Property Tax List

Dear Records Custodian,

Pursuant to the [State Name] Public Records Act, I am requesting:

1. A list of all residential parcels in [County Name] with property
   taxes delinquent for [1 year / 2+ years / specify threshold],
   including:
   - Parcel number (APN)
   - Property address (situs address)
   - Owner name
   - Owner mailing address
   - Total delinquent amount
   - Years delinquent
   - Whether the property is scheduled for upcoming tax sale

I request this data in electronic format (CSV, Excel, or similar).

I am willing to pay reasonable fees up to $[100]. Please advise of
costs before processing if they exceed this amount.

Thank you,
[Your Name]
[Phone Number]
[Email Address]
```

### 6.4 Typical Response Times and Fees

| State Category | Acknowledgment | Fulfillment | Fees |
|---------------|---------------|-------------|------|
| **Strong open records states** (TX, FL, AZ, CA) | 3-5 business days | 10-30 days | Free-$25 for electronic |
| **Moderate states** (IL, OH, PA, MI) | 5-10 business days | 15-45 days | $5-50 for electronic |
| **Weaker states** (VA, NJ, NY, some rural) | 10-15 business days | 30-90+ days | $25-200+ depending on complexity |

**Common fee structures:**
- Many agencies charge for staff time to compile the data (typically $15-30/hour)
- Some charge per page for paper copies ($0.10-0.25/page)
- Electronic copies are usually cheaper but some agencies still charge
- Some charge a flat "records search fee" ($5-25)
- A few agencies provide standard reports at no cost

### 6.5 States with Strongest / Weakest Public Records Access

**Tier 1 — Strongest Access (most data available, fastest response, lowest cost):**

| State | Law | Why It Is Strong |
|-------|-----|-----------------|
| **Texas** | Texas Public Information Act | Broad access, 10-day response requirement, attorney general enforces quickly |
| **Florida** | Florida Sunshine Law | Everything is public (famously broad), 2-week typical response |
| **Arizona** | ARS 39-121 | Strong access rights, prompt response required, minimal fees |
| **California** | California Public Records Act (CPRA) | Broad access, 10-day response deadline, recent amendments strengthened it |
| **Oregon** | Oregon Public Records Law | Strong access, reasonable fees |
| **Washington** | Washington Public Records Act | Very strong, penalties for noncompliance |
| **Colorado** | Colorado Open Records Act (CORA) | Good access, 3-day response required |

**Tier 2 — Moderate Access:**
- Ohio, Michigan, Illinois, Georgia, North Carolina, Minnesota, Indiana, Wisconsin

**Tier 3 — Weaker Access (more exemptions, slower responses, higher fees):**

| State | Challenges |
|-------|-----------|
| **New York** | Slow response, expensive, agencies frequently delay or deny |
| **New Jersey** | OPRA is strong on paper but enforcement is inconsistent |
| **Virginia** | FOIA has broad exemptions, agencies can charge high fees |
| **Pennsylvania** | Moderate, but some agencies are slow |
| **Mississippi** | Weak enforcement, agencies may not respond timely |

### 6.6 Tips for Getting Electronic Format

1. **Always explicitly request electronic format** in your letter. If you do not specify, many agencies default to paper.
2. **Name the file format you want**: CSV, Excel (.xlsx), or tab-delimited text. Many databases can export these natively.
3. **Ask if they have a standard report**: Some agencies regularly produce the exact report you want (e.g., monthly delinquency report). This is faster and cheaper than a custom extract.
4. **Offer to bring a USB drive**: Some agencies will copy data to your flash drive rather than emailing it.
5. **Follow up in 5-7 days**: A polite follow-up call often speeds things up. Ask for the records custodian by name.
6. **Cite the statute**: Including the specific state statute in your request signals that you know your rights and discourages unnecessary delays.
7. **Do not explain why you want the data**: In most states, you do not have to explain your purpose. Providing a reason can sometimes lead to the agency deciding you do not have a "valid" reason (even though the law does not require one). Simply cite the public records law.
8. **If denied, appeal**: Most states have an appeal process (to the state attorney general, a records ombudsman, or a court). The appeal often resolves the issue quickly.

---

## 7. National Change of Address (NCOA)

### 7.1 How NCOA Data Works

The **National Change of Address (NCOA)** database is maintained by the United States Postal Service (USPS). When someone files a change of address form (mail forwarding), that information goes into the NCOA database.

**Key facts:**
- Contains approximately 160 million change-of-address records
- Records are retained for 48 months (4 years)
- Updated weekly by USPS
- NOT directly available to the public — you must access it through licensed service providers
- USPS requires that NCOA processing be done by certified providers (USPS NCOALink licensees)

### 7.2 Licensed NCOA Service Providers

USPS licenses NCOA data to certified processing agents. You cannot buy raw NCOA data; instead, you submit a mailing list and the processor matches it against the NCOA database and returns addresses that have changed.

**Major NCOA Service Providers:**

| Provider | Service Type | Approximate Cost | Notes |
|----------|-------------|-----------------|-------|
| **Melissa Data (melissa.com)** | Full NCOA processing, address verification | $0.01-0.03 per record processed | Industry leader, API available |
| **SmartyStreets / Smarty** | Address validation + NCOA | $0.01-0.05 per record | Developer-friendly API, easy integration |
| **AccuZIP** | Direct mail + NCOA processing | $0.01-0.02 per record | Popular with direct mail campaigns |
| **Lorton Data** | NCOA processing, list hygiene | $0.01-0.03 per record | Full-service data hygiene |
| **InfoUSA / Data.com / Infogroup** | Business and consumer data + NCOA | Varies | Broader data products |
| **Peachtree Data** | Presort + NCOA + mailing | $0.01-0.02 per record | Bundled with presort services |

### 7.3 How to Use NCOA to Detect Movers (Potential Sellers)

This is one of the most underutilized lead generation techniques in real estate:

**The logic:**
1. If someone files a change of address FROM a property they own, they may have moved without selling
2. A homeowner who has moved away from their property becomes an **absentee owner** — one of the strongest seller motivation signals
3. If they moved recently, they may be renting out the property, leaving it vacant, or still deciding whether to sell

**Implementation workflow:**

```
Step 1: Build a list of property owners in your target area
        (from county assessor data, ATTOM, or PropertyRadar)

Step 2: Submit the list to an NCOA processor
        (provide owner name + property address)

Step 3: NCOA processing returns results:
        - "Match" = the owner filed a change of address
        - "No Match" = no change of address on file
        - For matches, you get the NEW address (where they moved to)

Step 4: Filter matches to identify:
        - Owners who moved OUT OF STATE (highest motivation)
        - Owners who moved to a different city
        - Owners who moved locally (possibly downsized, upsized, or separated)

Step 5: Cross-reference with MLS to see if the property is listed
        - If NOT listed, this is a pre-market opportunity
        - If listed and sitting, you have context for why (they already moved)

Step 6: Outreach to the owner at their NEW address
```

### 7.4 Cost and Update Frequency

| Factor | Detail |
|--------|--------|
| Per-record cost | $0.01-0.05 depending on provider and volume |
| Minimum list size | Usually 100-500 records |
| Processing time | 1-24 hours for standard batch processing |
| How often to run | Quarterly is optimal; monthly if budget allows |
| Record retention | NCOA keeps records for 48 months |
| Lag time | 2-4 weeks from when the person files with USPS to when it appears in NCOA |

**Cost example:**
- 5,000 property owners in your farm area
- Run NCOA quarterly = 20,000 records/year
- At $0.02/record = $400/year
- If 2% of owners move each quarter = ~100 new mover leads per quarter
- Cost per lead: ~$1.00 (extremely cheap)

### 7.5 Integration with Lead Generation

**Combining NCOA with other signals creates powerful lead identification:**

| NCOA Result | Plus This Signal | Lead Quality |
|-------------|-----------------|-------------|
| Owner moved out of state | Property not listed on MLS | Very High — reach out immediately |
| Owner moved out of state | Property tax delinquent | Extremely High — distressed absentee |
| Owner moved locally | Divorce filing on record | High — likely one spouse moved out |
| Owner moved | Property has code violations | High — absent owner not maintaining |
| Owner moved | Utility disconnected (FOIA data) | High — likely vacant property |

**Technical integration:**
- Melissa Data and Smarty both offer APIs for programmatic NCOA processing
- Can be integrated directly into the TheLeadEdge Python pipeline
- Run as a scheduled batch job (quarterly or monthly)
- Results feed into the lead scoring engine as a signal

---

## 8. Voter Registration & Vehicle Records

### 8.1 Voter Registration Data

Voter registration records contain: name, address, date of birth (in many states), party affiliation, and voting history. For lead generation, the key value is **address change detection** — when a voter updates their registration to a new address.

**State-by-State Availability for Marketing Use:**

Voter registration data availability falls into three categories:

**Category 1 — Freely Available Online (bulk download):**

| State | Access Method | Cost | Notes |
|-------|-------------|------|-------|
| Colorado | cdos.colorado.gov | Free | Full voter file download |
| Connecticut | sots.ct.gov | Free | Available upon request |
| Michigan | michigan.gov/sos | Free | Full voter file |
| Nevada | nvsos.gov | Free | Voter file downloads |
| North Carolina | ncsbe.gov | Free download | Excellent data, frequently updated |
| Ohio | ohiosos.gov | Free | Available by county |
| Oklahoma | oklahoma.gov/elections | Free | Full file |
| Oregon | sos.oregon.gov | Free | Available upon request |
| Rhode Island | elections.ri.gov | Free | Small state, complete file |
| Vermont | sos.vermont.gov | Free | Small file, easy to work with |
| Virginia | elections.virginia.gov | Free | Good data quality |
| Washington | sos.wa.gov | Free | Full voter file download |
| Wisconsin | elections.wi.gov | Free | Regularly updated |

**Category 2 — Available for Purchase (nominal fee):**

| State | Approximate Cost | How to Obtain |
|-------|-----------------|---------------|
| Arizona | $62.50 for full state file | Request from Secretary of State |
| California | $0.005/record (statewide ~$100) | Secretary of State |
| Florida | $5.00-$15.00 depending on format | Division of Elections |
| Georgia | $250 for statewide | Secretary of State |
| Illinois | Varies by county | County Clerk offices |
| Indiana | $0.001/record | Secretary of State |
| Maryland | Free for residents, fees for non-residents | State Board of Elections |
| Minnesota | $46 per CD | Secretary of State |
| New York | $0.005/record | State Board of Elections |
| Pennsylvania | $20 | Department of State |
| Texas | Varies by county (some free, some $1-50) | County Voter Registrar |

**Category 3 — Restricted or Unavailable for Commercial Use:**

| State | Restriction |
|-------|-----------|
| Arkansas | Only available for electoral/political purposes |
| Hawaii | Restricted to political purposes and government use |
| Kentucky | Political purposes only |
| Mississippi | Very restricted |
| Montana | Only for electoral purposes |
| New Hampshire | Restricted to elections-related use |
| South Dakota | Government and political use only |
| Wyoming | Limited availability |

**Important legal note**: Many states restrict voter data to specific purposes (elections, political campaigns, law enforcement, journalism). Using voter data for **commercial marketing** (including real estate marketing) may violate state law in some states. Always check your state's specific regulations before using voter data for lead generation.

### 8.2 Address Change Detection from Voter Rolls

**The technique:**
1. Obtain voter registration data for your target area (ideally with registration date or last-update date)
2. Compare current registration address with property records
3. If a voter's registration address changes from a property they own to a different address, they may have moved without selling
4. This is similar to NCOA detection but uses a different data source

**Practical challenges:**
- Voter rolls are updated irregularly (many people do not update promptly)
- Not everyone is registered to vote
- The data is less timely than NCOA (people update voter registration months or years after moving)
- Legal restrictions in many states limit commercial use

**Recommendation**: NCOA is a better data source for address-change detection. Use voter data as a supplemental signal, not your primary source.

### 8.3 Vehicle Registration / DMV Records

Vehicle registration records (name, address, vehicle information) are governed by the **Driver's Privacy Protection Act (DPPA)**, a federal law.

**DPPA permits access for these purposes (among others):**
- Motor vehicle safety and theft
- Insurance investigations
- Court proceedings
- Government functions
- Legitimate business needs (verification of accuracy of information)

**DPPA does NOT permit access for:**
- Marketing solicitations (this is explicitly prohibited)
- General lead generation
- Unsolicited commercial contact

**Bottom line for real estate lead generation**: You generally **cannot** use DMV/vehicle registration data for marketing purposes. The DPPA specifically prohibits using this data for solicitation unless you have the individual's prior consent.

**Exception**: Some skip tracing services (BatchLeads, BatchData) aggregate DMV data in compliance with DPPA permissible uses (specifically, "legitimate business use" for verifying information). They use it to verify/update addresses, not as a primary lead source. This is a gray area — the skip tracing company handles DPPA compliance on their end.

**Recommendation**: Do not attempt to obtain vehicle registration data directly for lead generation. Instead, use skip tracing services that handle DPPA compliance, and use NCOA for address change detection.

---

## 9. Automating Public Records Access

### 9.1 The Automation Spectrum

Not all public records can be automated equally. Here is the spectrum from fully automated to fully manual:

| Automation Level | Data Source | Method |
|-----------------|------------|--------|
| **Fully automated (API)** | ATTOM, PropertyRadar, BatchData, PACER | REST API calls on a schedule |
| **Semi-automated (web monitoring)** | County recorder websites, court portals, tax sale lists | Web monitoring tools detect changes |
| **Batch processing** | NCOA, voter rolls, bulk data purchases | Periodic batch processing (monthly/quarterly) |
| **Manual + scheduling** | Municipal code violations, building permits | Calendar reminder to check specific sites weekly |
| **Fully manual (FOIA)** | Utility disconnections, condemned lists | Submit request, wait for response, process data |

### 9.2 APIs Available from County/State Systems

Most county/state systems do NOT offer public APIs. However, there are exceptions:

**Direct Government APIs:**
- **PACER (Federal Bankruptcy Court)**: NextGen CM/ECF has email notification capability
- **Some state court systems**: Indiana MyCase, Wisconsin CCAP, and a few others have unofficial or semi-public API access
- **Open data portals**: Some counties/cities publish datasets on open data platforms (data.gov, Socrata-based portals like data.cityofchicago.org) that have APIs
- **GIS/Map services**: Many county GIS systems run on Esri ArcGIS Server, which has REST APIs you can query for parcel data

**Checking for open data portals:**
1. Search "[City/County Name] open data"
2. Check if they use Socrata (now Tyler Technologies Data & Insights) — URL pattern: `data.[city/county].gov`
3. Check if they use Esri ArcGIS Hub — URL pattern: `hub.arcgis.com` or `[agency].maps.arcgis.com`
4. Major cities with good open data: Chicago, NYC, LA, San Francisco, Austin, Denver, Seattle, Portland

**Esri ArcGIS REST API (for parcel data):**
Many county GIS systems expose parcel data through ArcGIS REST services. You can query these programmatically:

```
# Typical ArcGIS REST query for parcels
https://gis.[county].gov/arcgis/rest/services/Parcels/MapServer/0/query
?where=OWNER_NAME LIKE '%SMITH%'
&outFields=PARCEL_ID,OWNER_NAME,SITE_ADDRESS,MAIL_ADDRESS,ASSESSED_VALUE
&f=json
```

This is technically a public-facing query endpoint, not a private API. Many counties inadvertently expose powerful query capabilities through their GIS servers.

### 9.3 RSS and Alert Features from Courts

Some court systems offer email or RSS alerts:

| System | Alert Capability |
|--------|-----------------|
| **PACER NextGen CM/ECF** | Email notifications for new filings in a specific court or matching specific criteria |
| **Tyler Odyssey** | Some jurisdictions enable "case alerts" — email when a case is updated |
| **State-specific portals** | Some states (FL, TX counties) offer email alerts for new filings by case type |
| **Google Alerts** | Set up alerts for specific property addresses or names to catch news/legal mentions |

**Setting up PACER email alerts:**
1. Log into PACER (pacer.uscourts.gov)
2. Navigate to the specific bankruptcy court
3. Look for "Utilities" -> "Court Calendar" or "Reports"
4. Some courts allow you to subscribe to daily filing reports by case type (e.g., all new Chapter 7 filings)
5. Not all courts offer this — check with the specific court

### 9.4 Using Aggregator APIs to Replace Manual Checks

The highest-ROI automation is to replace manual county website checks with aggregator API calls:

| Manual Task | Automated Alternative | Tool |
|-------------|---------------------|------|
| Check county recorder for new NODs weekly | ATTOM Foreclosure API with date filter | ATTOM |
| Search probate court for new estate filings | PropertyRadar alerts (select counties) | PropertyRadar |
| Check tax delinquency status for target properties | ATTOM Assessment API with delinquency flag | ATTOM |
| Look up property details (beds, baths, sq ft) | ATTOM Property Detail API or BatchData | ATTOM / BatchData |
| Find owner contact info (phone, email) | BatchData Skip Trace API | BatchData |
| Monitor tax sale lists | Set up web monitoring on county treasurer page | Distill.io / Visualping |

### 9.5 Web Monitoring Tools for Pages Without APIs

For government websites that do not offer APIs or alerts, use web monitoring tools to detect when pages change:

| Tool | Cost | How It Works | Best For |
|------|------|-------------|----------|
| **Distill.io** | Free (limited) / $15+/mo | Browser extension or cloud. Monitors specific page elements for changes | County recorder new filings pages, tax sale lists |
| **Visualping** | Free (limited) / $13+/mo | Cloud-based, monitors full pages or selected areas | Simpler page change detection |
| **ChangeTower** | $29+/mo | Cloud-based, monitors and archives changes | Government pages that update periodically |
| **Wachete** | Free (limited) / $5+/mo | Monitors web pages, sends email alerts | Budget option |
| **Custom Python script** | Free | Use `requests` + `beautifulsoup4` to check and diff pages | Full control, tailored to specific pages |

**Example: Monitoring a County Tax Sale Page with Distill.io**
1. Install the Distill.io browser extension
2. Navigate to the county treasurer's tax sale page
3. Click the Distill icon and select the area of the page with the tax sale list
4. Set the check interval (e.g., daily or weekly)
5. When the page content changes (new list posted), you get an email alert
6. Manually download and process the new list

**Example: Custom Python monitor for a court filing page**

```python
import requests
import hashlib
import smtplib
from datetime import datetime

def check_for_updates(url: str, previous_hash: str) -> tuple[bool, str]:
    """Check if a webpage has changed since the last check."""
    response = requests.get(url, timeout=30)
    current_hash = hashlib.md5(response.text.encode()).hexdigest()
    changed = current_hash != previous_hash
    return changed, current_hash

def monitor_page(url: str, name: str, hash_file: str):
    """Monitor a page and send alert if changed."""
    try:
        with open(hash_file, 'r') as f:
            previous_hash = f.read().strip()
    except FileNotFoundError:
        previous_hash = ""

    changed, current_hash = check_for_updates(url, previous_hash)

    if changed:
        with open(hash_file, 'w') as f:
            f.write(current_hash)
        send_alert(f"Page updated: {name}", f"The page at {url} has changed. Check for new data.")

# Schedule this to run daily via cron or APScheduler
```

### 9.6 Building a Public Records Polling Schedule

A practical schedule for a single-market Realtor:

| Frequency | Data Source | Method | Time Required |
|-----------|------------|--------|---------------|
| **Daily** | MLS expired/withdrawn/price reductions | RESO Web API or saved search export | 5 min (automated) |
| **Weekly (Monday AM)** | County recorder: new NODs, lis pendens, trustee sales | ATTOM API or manual county website check | 10 min automated, 30 min manual |
| **Weekly (Monday AM)** | Probate court: new estate filings | Court portal search, filtered by case type and date | 15-20 min manual |
| **Weekly (Monday AM)** | Family court: new divorce filings | Court portal search (if accessible online) | 15 min manual |
| **Bi-weekly** | Bankruptcy filings (PACER) | PACER Case Locator search for your district | 10 min |
| **Monthly (1st of month)** | City code violation database | Manual check or FOIA if no online access | 15-30 min |
| **Monthly (1st of month)** | Building permit activity | City permit portal search, filter for demolition and major renovation | 15 min |
| **Monthly (1st of month)** | Tax sale list updates | Web monitor alert + manual download | 5-10 min |
| **Quarterly** | NCOA processing | Submit owner list to NCOA processor, analyze results | 1-2 hours per batch |
| **Quarterly** | Absentee owner refresh | ATTOM API or county assessor data pull | 30 min automated |
| **Quarterly** | FOIA requests | Submit new requests for utility disconnects, code violations, etc. | 30 min to prepare and send |
| **Annually** | Tax delinquency list | County treasurer (published or FOIA) | 1-2 hours to obtain and process |

**Estimated weekly time commitment:**
- With automation (APIs + monitoring): ~1-2 hours/week
- Without automation (all manual): ~4-6 hours/week
- Hybrid approach (aggregator APIs for property data, manual for courts): ~2-3 hours/week

---

## 10. State-by-State Snapshot

A quick reference for the 10 most common real estate markets, grading how easy it is to access public records data. Grades reflect online accessibility, data quality, and cost.

### Grading Criteria

| Grade | Meaning |
|-------|---------|
| **A** | Excellent online access, most data free, bulk downloads available, fast FOIA response |
| **B** | Good online access, most data available with some effort, reasonable FOIA process |
| **C** | Mixed — some data online, some requires FOIA or in-person visit, moderate delays |
| **D** | Poor online access, most data requires FOIA or in-person, slow response, higher fees |

---

### Arizona

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | A | Maricopa County (recorder.maricopa.gov, mcassessor.maricopa.gov) has excellent online access. Most AZ counties have good online assessor/recorder search. |
| **Court Records** | B+ | AZCourts public access portal covers most counties. Odyssey-based. Probate and family court filings searchable. |
| **Code/Permits** | B | Major cities (Phoenix, Scottsdale, Tempe, Mesa) have online permit portals. Code violations vary by city. |
| **FOIA** | A | ARS 39-121 is strong. Prompt response required. Minimal fees typical. |
| **Overall** | **A-** | One of the easier states for public records access. |

**Key Portals:**
- Maricopa County Recorder: recorder.maricopa.gov
- Maricopa County Assessor: mcassessor.maricopa.gov
- AZ Courts: azcourts.gov/publicaccess
- Phoenix Permits: phoenix.gov/pdd (Accela-based)

---

### California

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | B+ | County-by-county (58 counties). LA County registrar-recorder excellent. Most major counties have good online access. |
| **Court Records** | B | No unified statewide portal. County-by-county. LA Superior Court (lacourt.org) is good. Many smaller counties limited. |
| **Code/Permits** | B | Major cities have good permit portals. LA, SF, San Diego have Accela or equivalent. Smaller cities vary. |
| **FOIA** | A | California Public Records Act is strong. 10-day response deadline. |
| **Overall** | **B+** | Good access in major metros, spotty in rural areas. Non-judicial foreclosure state (NODs recorded with county recorder, easy to find). |

**Key Portals:**
- LA County Registrar-Recorder: registrar.lacounty.gov
- LA Superior Court: lacourt.org
- SF Assessor-Recorder: sfassessor.org
- CA Court System: courts.ca.gov (links to each county)

---

### Colorado

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | A- | Most counties have good online assessor/clerk and recorder search. Denver, Arapahoe, Jefferson, El Paso counties all online. |
| **Court Records** | A- | Statewide court system (courts.state.co.us) with good online case search. |
| **Code/Permits** | B | Denver has good online permit search. Other cities vary. |
| **FOIA** | A | Colorado Open Records Act (CORA) is strong. 3-business-day response required. |
| **Overall** | **A-** | Excellent public records access statewide. |

**Key Portals:**
- CO Courts: courts.state.co.us
- Denver Assessor: denvergov.org/assessor
- County Clerk & Recorder: search by county at sos.state.co.us

---

### Florida

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | A | Most counties have excellent online property appraiser and tax collector websites. Strong open data culture. |
| **Court Records** | A- | Clerks of Court provide excellent online access. Many counties have full case search. Miami-Dade, Broward, Orange all excellent. Judicial foreclosure state, so foreclosure cases are in court records (easy to search). |
| **Code/Permits** | B+ | Major cities have good online permit portals. Code enforcement visibility varies. |
| **FOIA** | A+ | Florida Sunshine Law is among the strongest in the nation. Nearly everything is public. Fast response. |
| **Overall** | **A** | Best state for public records access. |

**Key Portals:**
- Miami-Dade Property Appraiser: miamidade.gov/pa
- Broward County Records: broward.org/recordstaxestreasury
- Orange County Comptroller: occompt.com
- FL Statewide Court Case Search: myflcourtaccess.com

---

### Georgia

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | B+ | Most counties use QPUBLIC (qpublic.net) — clean, searchable, free. |
| **Court Records** | B | County-by-county. Fulton County (Atlanta) has good online access. Many counties use Odyssey. |
| **Code/Permits** | B- | Atlanta and major cities have permit portals. Smaller cities/counties limited. |
| **FOIA** | B | Georgia Open Records Act is decent but less aggressive than FL or TX. 3-day response. |
| **Overall** | **B+** | Good for property data (thanks to QPUBLIC), mixed for court records. |

**Key Portals:**
- QPUBLIC parcel viewers: qpublic.net (links to each county)
- Fulton County Courts: fultoncountyga.gov
- Gwinnett County Tax: gwinnettcounty.com

---

### Illinois

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | B | Cook County (Chicago) has good online access but complex system. Downstate counties vary widely. |
| **Court Records** | B | Many counties use Judici (judici.com). Cook County has its own system (cookcountyclerkofcourt.org). |
| **Code/Permits** | B | Chicago has good permit data (via open data portal). Suburban and downstate cities vary. |
| **FOIA** | B+ | Illinois FOIA is moderate. 5-business-day response. Office of the Attorney General handles appeals. |
| **Overall** | **B** | Cook County is good; rest of state is mixed. |

**Key Portals:**
- Cook County Recorder: cookrecorder.com
- Cook County Assessor: cookcountyassessor.com
- Judici (downstate courts): judici.com
- Chicago Open Data: data.cityofchicago.org

---

### New York

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | B- | NYC has ACRIS (automated city register information system) — excellent for NYC. Upstate counties vary; many have limited online access. |
| **Court Records** | C+ | eCourts system is functional but can be slow and confusing. NYC Civil Court and Supreme Court have online case search. |
| **Code/Permits** | B (NYC) / C (upstate) | NYC has excellent open data (BIS for building permits, HPD for violations). Upstate cities limited. |
| **FOIA** | C+ | New York FOIL (Freedom of Information Law) exists but agencies are notoriously slow. 5-business-day acknowledgment, but fulfillment can take months. |
| **Overall** | **B- (NYC) / C (upstate)** | NYC is a special case with excellent data; rest of state is challenging. |

**Key Portals:**
- ACRIS (NYC deed/mortgage records): a836-acris.nyc.gov
- NYC ZOLA (zoning/land use): zola.planning.nyc.gov
- NYC Building Information System: a810-bisweb.nyc.gov
- NYC HPD (housing violations): hpdonline.nyc.gov
- eCourts: iapps.courts.state.ny.us

---

### North Carolina

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | B+ | Most counties have good online GIS/parcel viewers. Many use Beacon/Schneider or QPUBLIC. |
| **Court Records** | B+ | eCourts portal (Odyssey-based) rolling out statewide. Good online case search for participating counties. |
| **Code/Permits** | B | Charlotte, Raleigh, Durham have good permit portals. Smaller cities vary. |
| **FOIA** | B+ | NC Public Records Law is decent. 2-week typical response. |
| **Overall** | **B+** | Good and improving with eCourts rollout. |

**Key Portals:**
- NC eCourts: portal.nccourts.org
- Mecklenburg County (Charlotte): mecknc.gov/assessor
- Wake County (Raleigh): wakegov.com/realestate

---

### Texas

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | A | Every county appraisal district has a searchable website (required by state law). Most are excellent. Tax data easily accessible. |
| **Court Records** | B | County-by-county. Harris County (Houston), Dallas County, Bexar County (San Antonio) have good online access. Many use Odyssey or similar. No unified statewide portal. |
| **Code/Permits** | B | Major cities (Houston, Dallas, Austin, San Antonio) have permit portals. Houston is notably data-rich. |
| **FOIA** | A+ | Texas Public Information Act is among the strongest. 10-business-day response. AG enforces aggressively. |
| **Overall** | **A-** | Excellent for property data (every county appraisal district online). Court records require county-by-county work. |

**Key Portals:**
- Harris County (Houston) Appraisal District: hcad.org
- Dallas Central Appraisal District: dallascad.org
- Travis County (Austin) Appraisal District: traviscad.org
- Harris County Clerk: cclerk.hctx.net
- Texas courts: txcourts.gov (links to county courts)

---

### Washington

| Category | Grade | Details |
|----------|-------|---------|
| **Property/Tax Data** | A- | Most counties have good online assessor and recorder search. King County (Seattle) is excellent. |
| **Court Records** | A | JIS Link (dw.courts.wa.gov) provides statewide court case search — one of the best state systems. |
| **Code/Permits** | B+ | Seattle has excellent permit data (via Seattle Open Data). Other cities vary but generally good. |
| **FOIA** | A | Washington Public Records Act is very strong. Penalties for noncompliance. |
| **Overall** | **A-** | Strong across the board. Statewide court search is a major advantage. |

**Key Portals:**
- WA Courts (JIS Link): dw.courts.wa.gov
- King County (Seattle) Recorder: kingcounty.gov/recorder
- King County Assessor: kingcounty.gov/assessor
- Seattle Open Data: data.seattle.gov

---

## Quick Reference: Grading Summary

| State | Property/Tax | Court Records | Code/Permits | FOIA | Overall |
|-------|-------------|---------------|-------------|------|---------|
| **Florida** | A | A- | B+ | A+ | **A** |
| **Arizona** | A | B+ | B | A | **A-** |
| **Colorado** | A- | A- | B | A | **A-** |
| **Texas** | A | B | B | A+ | **A-** |
| **Washington** | A- | A | B+ | A | **A-** |
| **North Carolina** | B+ | B+ | B | B+ | **B+** |
| **Georgia** | B+ | B | B- | B | **B+** |
| **California** | B+ | B | B | A | **B+** |
| **Illinois** | B | B | B | B+ | **B** |
| **New York** | B- | C+ | B/C | C+ | **B-/C+** |

---

## Appendix A: Glossary of County/State Platforms

| Platform | What It Is | Where to Find |
|----------|-----------|---------------|
| **Tyler Odyssey** | Court case management system | Look for "Odyssey" or "Tyler" in court portal URLs |
| **Tyler Eagle Recorder** | County recording system | County recorder websites |
| **Tyler iasWorld** | Property assessment (CAMA) system | County assessor websites |
| **Beacon / Schneider / Catalis** | Parcel viewer / property search | Usually at beacon.schneidercorp.com or similar |
| **QPUBLIC** | Parcel viewer, popular in Southeast | qpublic.net |
| **Vision Government Solutions** | Assessment system, Northeast | visionappraisal.com |
| **Accela Citizen Access** | Building permit portal | Look for "citizenaccess" in city permit URLs |
| **Tyler EnerGov** | Building permit portal | Look for "energov" in city permit URLs |
| **Esri ArcGIS** | GIS/mapping platform | Look for "arcgis.com" in county GIS URLs |
| **Socrata / Tyler Data Insights** | Open data platform | data.[city/county].gov |
| **PACER** | Federal court records | pacer.uscourts.gov |
| **Judici** | Court case search (IL, IN, and others) | judici.com |

---

## Appendix B: First Steps Checklist

When setting up public records access for a new target market, follow this checklist:

### Week 1: Property Data Foundation
- [ ] Identify the county assessor website — bookmark it, learn the search interface
- [ ] Identify the county recorder website — bookmark it, learn document type codes
- [ ] Find the county GIS / parcel viewer — test searching by address and owner name
- [ ] Test whether the assessor data shows mailing address vs. site address (for absentee owner identification)
- [ ] Search for "[County Name] open data" — check if bulk data downloads are available
- [ ] Check if the county GIS runs on Esri ArcGIS (look for REST API endpoints)

### Week 2: Court Records Setup
- [ ] Find the court system for your county — identify the platform (Odyssey, eCourt, state portal)
- [ ] Test probate case search — search for recent filings, note the case type codes
- [ ] Test family court / divorce case search — note what information is public
- [ ] Register for PACER (pacer.uscourts.gov) — free to register
- [ ] Search for recent bankruptcy filings in your district on PACER
- [ ] Check if the court system offers email alerts or RSS feeds for new filings

### Week 3: Municipal Data
- [ ] Identify the building permit portal for each city in your target area
- [ ] Test searching for recent demolition permits and major renovation permits
- [ ] Search for "[City Name] code enforcement" — determine if online search exists
- [ ] If no online code violation search, prepare a FOIA request (use Template 2)
- [ ] Check if the city has an open data portal with code violation or permit data

### Week 4: Aggregator Evaluation
- [ ] Sign up for ATTOM Data free trial or request a demo
- [ ] Sign up for PropertyRadar trial (if in Western US)
- [ ] Compare aggregator data against what you found manually in Weeks 1-3
- [ ] Evaluate which aggregator best covers your specific county/market
- [ ] Assess your budget and decide on Tier 1/2/3 approach

### Week 5: FOIA and Specialty Data
- [ ] Submit FOIA request for utility disconnection data (Template 1)
- [ ] Submit FOIA request for tax delinquency list (Template 3) if not available online
- [ ] Research NCOA providers — get pricing for your list size
- [ ] Check your state's voter registration data availability and commercial use rules
- [ ] Set up web monitoring (Distill.io or similar) for county/court pages you check manually

### Ongoing
- [ ] Establish the weekly/monthly polling schedule from Section 9.6
- [ ] Track FOIA request status and response times (build your own records of which agencies are responsive)
- [ ] Build relationships with county/city staff — the helpful ones can save you hours
- [ ] Document county-specific quirks (unique document codes, search tips) as you learn them
- [ ] Evaluate automation opportunities as your manual process matures

---

## Appendix C: Data Source Quick-Reference Matrix

For each of the 12 lead sources from prior research, here is the fastest path to the data:

| Lead Source | Fastest Access Path | Backup Path | Automation Path |
|-------------|-------------------|-------------|-----------------|
| **Pre-Foreclosure / NOD** | ATTOM Foreclosure API | County recorder website (search for NOD/Lis Pendens) | ATTOM API on weekly schedule |
| **Probate / Inherited** | County probate court portal (Odyssey etc.) | AllTheLeads.com or USProbateLeads.com ($200-400/mo) | Manual court search weekly + web monitoring |
| **Divorce Filings** | County family court portal | Third-party lead services | Manual court search weekly |
| **Tax Delinquency** | County treasurer website or FOIA request | ATTOM Assessment API (delinquency flag) | ATTOM API quarterly + annual FOIA |
| **Code Violations** | City code enforcement website (if available) | FOIA request to city (Template 2) | Web monitoring on city pages |
| **Absentee Owners** | ATTOM Property API (mailing vs. site address) | County assessor data (manual compare) | ATTOM API quarterly refresh |
| **Long-Term Ownership** | ATTOM Sale History API (last sale date) | County assessor (year acquired) | ATTOM API, filter for 10+ year ownership |
| **Estate & Trust Transfers** | County recorder (search for trust deeds, affidavits of heirship) | ATTOM recording data | ATTOM API or county recorder web monitor |
| **Building Permits** | City permit portal (Accela, EnerGov, etc.) | FOIA request or open data portal | Web monitoring or open data API if available |
| **Tax Assessment Changes** | County assessor website (assessment history) | ATTOM Assessment API | ATTOM API, compare year-over-year |
| **Utility Disconnections** | FOIA request to municipal utility (Template 1) | No online alternative in most cases | Quarterly FOIA request on schedule |
| **Corporate-Owned Residential** | ATTOM Property API (owner type filter) | County assessor (owner name contains LLC, Corp, Trust) | ATTOM API with entity ownership filter |

---

*This document provides the practical access guide for every public records data source identified in prior TheLeadEdge research. It is designed to be a working reference — not a one-time read. Bookmark specific sections and return to them as you set up access to each data source in your target market.*
