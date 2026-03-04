# Clerk of Court Records Automation Research: Lee County & Collier County, FL

> **Project**: TheLeadEdge -- Real Estate Lead Generation System
> **Created**: 2026-03-03
> **Purpose**: Technical feasibility assessment for automating Clerk of Court record monitoring
> **Prerequisite Reading**: [public_records_strategies.md](public_records_strategies.md), [local_data_sources.md](local_data_sources.md)

---

## Executive Summary

**Bottom line**: Neither Lee County nor Collier County offers a public REST API for their clerk records systems. Both use form-based web applications that would require browser automation (Playwright/Selenium) or periodic public records requests (Florida Sunshine Law, Chapter 119) to access programmatically. The foreclosure auction platform (RealAuction/realforeclose.com) is a ColdFusion application with no public API. However, several viable automation paths exist, ranging from low-effort (manual + email parsing) to high-effort (browser automation + OCR).

**Recommended approach for MVP**: Periodic Florida Sunshine Law public records requests for bulk data exports (lis pendens, probate filings) combined with manual weekly checks of the clerk websites. Browser automation is a Phase 4+ enhancement.

---

## Table of Contents

1. [Lee County Clerk (leeclerk.org)](#1-lee-county-clerk)
2. [Collier County Clerk (collierclerk.com)](#2-collier-county-clerk)
3. [RealAuction / Foreclosure Sales Platform](#3-realauction--foreclosure-sales-platform)
4. [Code Enforcement Systems](#4-code-enforcement-systems)
5. [Florida Sunshine Law (Public Records Requests)](#5-florida-sunshine-law-public-records-requests)
6. [Third-Party Aggregator Alternatives](#6-third-party-aggregator-alternatives)
7. [Automation Feasibility Matrix](#7-automation-feasibility-matrix)
8. [Recommended Implementation Strategy](#8-recommended-implementation-strategy)

---

## 1. Lee County Clerk

### 1.1 Official Records Search (or.leeclerk.org)

**System**: Custom web application (likely Hyland-based). Accessed via leeclerk.org, redirecting to or.leeclerk.org for official records search.

**Document types searchable**: Liens, plats, certificates of title, mortgages, **lis pendens**, marriage licenses, deeds, judgments, death certificates, military discharges. Records date back to 1887.

**Search interface**:
- Form-based HTML search (not a REST API)
- Search fields: Name (grantor/grantee), document type, date range, book/page, instrument number
- Address search may or may not be available (varies by system version)
- Results displayed in paginated HTML tables

**Access requirements**:
- Free to search the index
- Viewing actual document images: $0.50-$2.00 per page
- E-certified copies: $8 per document, delivered via email
- No login required for basic index searches (unconfirmed -- the matrix.leeclerk.org system may require account creation)

**Programmatic access assessment**:
- **No public API** -- confirmed by search results
- The matrix.leeclerk.org system timed out on fetch, suggesting heavy JavaScript rendering or bot protection
- Form submissions likely use standard HTTP POST but may include CSRF tokens, CAPTCHAs, or session validation
- **Verdict**: Playwright/Selenium required for automation. Not feasible with httpx alone.

### 1.2 Court Case Records (matrix.leeclerk.org)

**System**: Custom records inquiry system (the "Matrix" system). This is separate from official records -- it covers court cases.

**Case types available**: Civil, Criminal, Probate, Guardianship, Domestic Relations, Mental Health, Juvenile, Traffic.

**Important access restrictions**:
- Mental Health, Probate, Guardianship, Juvenile, and Domestic Relations cases have **restricted access** per the Florida Supreme Court's Access Security Matrix (14 access levels)
- General public searches on these case types return **incomplete results**
- Many cases opened before 2004 are not available online
- Full access requires specific user group membership (attorneys, parties, etc.)

**Search interface**:
- Form-based search with text fields and dropdowns
- Includes a court calendar search feature ("View Court Calendar" checkbox)
- Results appear in HTML tables with links to case detail pages
- E-certified documents available for $8 each via the search interface

**Programmatic access assessment**:
- **No public API**
- JavaScript-heavy interface (the page timed out on standard fetch, strongly suggesting dynamic rendering)
- The Florida Supreme Court Access Security Matrix means automated access to probate/family cases will return limited data for unauthenticated users
- **Verdict**: Playwright/Selenium needed. Even then, probate and divorce case data will be limited compared to what a registered attorney/party can see.

### 1.3 Foreclosure & Tax Deed Sales

**Platform**: Lee County uses **RealAuction** at lee.realforeclose.com for online foreclosure auctions.

**Data available**: Auction calendar, case numbers, judgment amounts, parcel IDs, property addresses, sale dates, bidding status.

**See Section 3 below for detailed RealAuction analysis.**

---

## 2. Collier County Clerk

### 2.1 Official Records / Document Search (app.collierclerk.com)

**System**: COR (Clerk of Records) Public Access system at app.collierclerk.com/CORPublicAccess/Search/Document. Uses both the CORE system (court records) and Acclaim (official records).

**Search interface** (confirmed via web fetch):
- **Form-based search** with multiple parameter sections
- **Party Name**: Last name, first name, or business name
- **Document Identification**: Instrument number, or book and page numbers
- **Document Type Selection**: 40+ document categories available for multi-select, including deeds, mortgages, liens, judgments, easements, certificates, **lis pendens**, probate records, powers of attorney, declarations of condominium
- **Date Range**: Optional start and end date filtering
- Input validation with JavaScript (exclamation icons for invalid characters)
- Date picker uses client-side JavaScript

**Access requirements**:
- No login required for basic public access searches
- Registered agency access (for title companies, law firms) requires a notarized Agency Registration Agreement mailed to the CIT Department
- Subscription-based bulk access available for frequent users (title companies, legal professionals)

**Programmatic access assessment**:
- **No public REST API** -- confirmed
- The form-based interface suggests standard HTTP POST for searches
- JavaScript validation on the client side, but the actual search may be a server-side form submission
- The page rendered successfully via web fetch (unlike Lee County's Matrix system), suggesting less aggressive bot protection
- The document type multi-select with 40+ options is valuable -- **lis pendens is a selectable document type**
- **Verdict**: Potentially automatable with httpx if form submissions use standard POST without CSRF tokens. More likely needs Playwright for reliability. This is the more promising of the two county systems for automation.

### 2.2 Court Case Search (ShowCase -- cms.collierclerk.com)

**System**: ShowCase Case Management System at cms.collierclerk.com/showcaseweb/

**Case types**: Civil, Criminal, **Probate**, Traffic. Also includes Court Events, Set Court Date, and School Completion functions.

**Search interface**:
- Web-based case search
- The main page at cms.collierclerk.com loaded as empty content during fetch, suggesting heavy JavaScript rendering or iframe-based architecture
- The actual search interface is at cms.collierclerk.com/showcaseweb/

**Access requirements**:
- Public access for basic case information
- Detailed case documents may have restricted access
- Information is "provisional" per their disclaimer

**Programmatic access assessment**:
- **No public API**
- ShowCase is a third-party CMS platform used by multiple Florida counties
- Heavy JavaScript rendering likely (failed to fetch content from main page)
- **Verdict**: Playwright/Selenium required. The ShowCase platform is known to be JavaScript-heavy and may have bot protection.

### 2.3 Foreclosure Sales

**Platform**: Collier County has its own **Foreclosure Auction Calendar** through the clerk's website (not confirmed to use realforeclose.com based on the clerk's foreclosure page, which does not mention it).

**Process details** (from clerk's website):
- Properties sold after final judgment, scheduled 20-35 days after judgment
- Sold to highest bidder, often the foreclosing lender
- Certificate of sale issued within 1 day; certificate of title after 10 days
- Court registry fees: 3% on first $500, 1.5% on balance, plus documentary stamps
- Sales published in local newspaper twice, second publication at least 5 days before sale
- Physical location: Main Courthouse, 3315 Tamiami Trail East, Naples, FL

**Note**: PropertyOnion.com and ForeclosureAuctionData.com both aggregate Collier County foreclosure data if direct clerk access proves difficult.

---

## 3. RealAuction / Foreclosure Sales Platform

### 3.1 Platform Overview

**Vendor**: RealAuction.com LLC -- the largest online foreclosure auction software provider in the US, covering 11 states.

**URLs**:
- Lee County: lee.realforeclose.com
- Collier County: collier.realforeclose.com (if used)

**Technology**: ColdFusion application (confirmed by .cfm file extensions in URLs, e.g., `index.cfm?zaction=user&zmethod=calendar`). This is significant because ColdFusion applications often:
- Use server-side session management
- Render pages server-side (less JavaScript, more traditional form posts)
- Have predictable URL parameter patterns

### 3.2 Data Available

Based on URL patterns observed:
- **Auction Calendar**: `index.cfm?zaction=user&zmethod=calendar` -- monthly calendar view with auction dates
- **Day List**: `index.cfm?AUCTIONDATE=MM/DD/YYYY&Zmethod=DAYLIST&zaction=AUCTION` -- properties scheduled for a specific day
- Each listing typically includes: case number, plaintiff, defendant, property address, parcel ID, judgment amount, auction time

### 3.3 Programmatic Access Assessment

- **No public API** -- RealAuction does not offer developer documentation or data feeds to the public
- The ColdFusion URL structure with query parameters suggests server-side rendering
- Calendar data might be fetchable via httpx with proper session handling
- Day list pages likely return HTML tables that can be parsed
- Registration may be required to view full property details
- **Verdict**: Moderately promising for httpx-based scraping due to server-side ColdFusion rendering. However, CAPTCHA, login requirements, and terms of service must be checked. Playwright as fallback.

### 3.4 Alternative: Third-Party Aggregators

Rather than scraping RealAuction directly, these services aggregate the same data:

| Service | Coverage | Pricing | Data Export |
|---------|----------|---------|-------------|
| **ForeclosureAuctionData.com** | All 67 FL counties | $29/mo (single county), $99/mo (all counties) | Spreadsheet views, search by address/owner/parcel/case |
| **PropertyOnion.com** | All FL counties | Subscription-based (free trial) | Interactive maps, auction history, property data |
| **leeforeclosures.com** | Lee County | Unknown | Lee County specific foreclosure data |

**Recommendation**: ForeclosureAuctionData.com at $29/month for Lee County (or $99/month for both counties) is likely more cost-effective and reliable than building and maintaining a scraper for realforeclose.com.

---

## 4. Code Enforcement Systems

### 4.1 Lee County Code Enforcement

**System**: **Accela Citizen Access** at aca-prod.accela.com/LEECO/

**Search capabilities** (confirmed via web fetch):
- **Address search**: Street number, street name, unit number, city, state, ZIP
- **Parcel number search**: No dashes, spaces, or special characters
- **Record type filter**: Code Enforcement Complaint, Code Violation, Hearing Examiner, Inoperable/Unregistered Vehicles, Lot Mowing, Minimum Housing, Nuisance Accumulation, Right-of-Way, Truck Citations, Unsafe Building Violations
- **Additional fields**: Record number, project name, status, date ranges, contact name, business name, license info

**Supplementary tool**: Lee County launched a **Nuisance Accumulation Story Map** -- an interactive map showing color-coded code enforcement data across the county.

**Programmatic access**:
- Accela has a **REST API** (developer.accela.com) that supports Records, Inspections, Citizens, and other endpoints
- The Accela Construct API is a public developer platform with documentation
- **HOWEVER**: The API requires agency authorization. Lee County would need to grant API access. This is not a public self-service API -- it is designed for agency-contracted developers.
- The Citizen Access web portal itself is form-based and could be scraped with Playwright
- **Verdict**: The Accela REST API is technically the best option if Lee County grants access. Otherwise, Playwright automation of the Citizen Access portal. Contact Lee County DCD at (239) 533-8895 or codeenforcement@leegov.com to inquire about API access.

### 4.2 Collier County Code Enforcement

**System**: **CityView Portal** at cvportal.colliercountyfl.gov/CityViewWeb/

**Search capabilities**:
- Requires a **case number** to view case status online
- Without a case number, must call (239) 252-2440 and provide the property address
- Registration required to request lien searches or other services

**Programmatic access**:
- Very limited public search capability (case number required)
- No known public API for CityView
- **Verdict**: This is the weakest source for automation. A Florida Sunshine Law public records request for code violation data is the only practical bulk access method.

---

## 5. Florida Sunshine Law (Public Records Requests)

### 5.1 Legal Framework

**Statute**: Florida Statute Chapter 119 (Public Records Law), specifically Section 119.07.

**Key provisions**:
- Every person has the right to inspect or copy any public record made or received in connection with official business of any public body, officer, or employee
- Requests can be made **in person, by phone, fax, email, or regular mail**
- No requirement to state a reason for the request
- No requirement to identify yourself (though in practice, you need to provide contact info for delivery)
- The agency must respond **promptly** and in **good faith** (no statutory deadline in days)

### 5.2 Costs

| Item | Cost |
|------|------|
| Inspection of records | **Free** (you can look at them, just pay to copy) |
| Standard copies (first 50 pages) | Free in some agencies, or up to $0.15/page |
| Standard copies (after 50 pages) | $0.15/page (one-sided), $0.20/page (double-sided) |
| Certified copies | $1.00/page + $2.00 certification fee per document |
| Electronic records (email delivery) | **Actual cost of duplication only** (no labor, no overhead) -- this can be near-zero |
| Extensive use of IT resources or staff | "Special service charge" based on **actual labor cost** incurred |

**Critical insight**: Under F.S. 119.07, if the records already exist in electronic format and the agency routinely uses email, they **cannot charge labor costs** for simply emailing you a database export. They can only charge the "actual cost of duplication" (essentially the cost of the media). This makes electronic delivery of existing data extremely cheap.

### 5.3 Response Time

- No statutory deadline (unlike federal FOIA's 20-day requirement)
- Must be "prompt" and in "good faith"
- In practice, simple requests (existing data in electronic format) are often fulfilled within **3-10 business days**
- Complex requests requiring data compilation, review, or redaction may take **2-6 weeks**
- You have the right to request a cost estimate before the work begins
- Agencies can be compelled to respond via lawsuit, and the requester can recover attorney's fees

### 5.4 Public Records Request Templates

**Template 1: Lis Pendens Filings (Monthly)**

```
Subject: Public Records Request -- Lis Pendens Filings

Dear Custodian of Public Records,

Pursuant to Florida Statute 119.07, I am requesting access to the following
public records:

All lis pendens recorded in [Lee County / Collier County] Official Records
for the period [START DATE] through [END DATE].

For each filing, I request the following data fields (to the extent they are
maintained in your electronic records system):
  - Instrument number
  - Recording date
  - Document type
  - Grantor/plaintiff name(s)
  - Grantee/defendant name(s)
  - Property address or legal description
  - Case number (if associated with a court case)
  - Book and page number

I request this data in electronic format (CSV, Excel, or database export
preferred). If the records exist in electronic format, I request delivery
via email to [YOUR EMAIL].

Per F.S. 119.07(4)(d), if this request requires extensive use of information
technology resources or clerical assistance, please provide a cost estimate
before proceeding.

Thank you for your prompt attention to this request.

[YOUR NAME]
[YOUR PHONE]
[YOUR EMAIL]
```

**Template 2: Probate Case Filings (Monthly)**

```
Subject: Public Records Request -- Probate Case Index Data

Dear Custodian of Public Records,

Pursuant to Florida Statute 119.07, I am requesting access to the following
public records:

An index listing of all probate cases filed in [Lee County / Collier County]
Circuit Court for the period [START DATE] through [END DATE].

For each case, I request the following data fields:
  - Case number
  - Filing date
  - Case type/subtype (e.g., formal administration, summary administration,
    disposition without administration)
  - Decedent name
  - Personal representative name (if public record)
  - Attorney of record (if public record)
  - Case status (open/closed)

I request this data in electronic format (CSV, Excel, or database export
preferred). If the records exist in electronic format, I request delivery
via email to [YOUR EMAIL].

Per F.S. 119.07(4)(d), if this request requires extensive use of information
technology resources or clerical assistance, please provide a cost estimate
before proceeding.

Thank you for your prompt attention to this request.

[YOUR NAME]
[YOUR PHONE]
[YOUR EMAIL]
```

**Template 3: Code Enforcement Violations (Quarterly)**

```
Subject: Public Records Request -- Code Enforcement Violations

Dear Custodian of Public Records,

Pursuant to Florida Statute 119.07, I am requesting access to the following
public records:

A listing of all code enforcement cases opened or active in
[Lee County / Collier County] for the period [START DATE] through [END DATE].

For each case, I request the following data fields:
  - Case/complaint number
  - Date opened
  - Property address
  - Parcel/folio number
  - Violation type/category
  - Current status (open, closed, hearing scheduled, lien recorded)
  - Date of most recent action

I request this data in electronic format (CSV, Excel, or database export
preferred). If the records exist in electronic format, I request delivery
via email to [YOUR EMAIL].

Per F.S. 119.07(4)(d), if this request requires extensive use of information
technology resources or clerical assistance, please provide a cost estimate
before proceeding.

Thank you for your prompt attention to this request.

[YOUR NAME]
[YOUR PHONE]
[YOUR EMAIL]
```

### 5.5 Where to Send Requests

| County | Entity | Contact | Address |
|--------|--------|---------|---------|
| **Lee County** | Clerk of Court | leeclerk.org/services/public-records-request | PO Box 2278, Fort Myers, FL 33902 |
| **Lee County** | County Government (code enforcement) | leegov.com/publicrecords | PO Box 398, Fort Myers, FL 33902 |
| **Collier County** | Clerk of Court | Contact Renata Robbins, Custodian of Public Records | 3315 Tamiami Trail E, Suite 102, Naples, FL 34112; (239) 252-2646 |
| **Collier County** | County Government (code enforcement) | collier.gov/public-record-requests | 3299 Tamiami Trail E, Suite 303, Naples, FL 34112 |

### 5.6 Standing/Recurring Requests

Florida law allows **standing requests** for records that are created on an ongoing basis. Per AG opinions, you can ask an agency to provide you with new records as they are created (e.g., "all lis pendens filed each week"). However:
- Agencies are not legally obligated to honor standing requests (some do, some do not)
- The practical approach is to submit monthly requests on a regular schedule
- Building a relationship with the records custodian significantly improves cooperation

---

## 6. Third-Party Aggregator Alternatives

Before building scrapers, consider these services that already aggregate the data:

### 6.1 ATTOM Data Solutions (attomdata.com)

- **Coverage**: Nationwide, including Lee and Collier counties
- **Data available**: Pre-foreclosure/lis pendens, foreclosure auctions, bank-owned (REO), tax liens, deed transfers, property characteristics
- **Access**: REST API with JSON responses
- **Pricing**: Starts around $150-250/month for API access (property-level queries)
- **Pros**: Clean API, nationwide coverage, well-documented
- **Cons**: Expensive for a single-market operation; may have data lag vs. direct county access

### 6.2 PropertyRadar (propertyradar.com)

- **Coverage**: Strong in Western states, expanding; covers Florida
- **Data available**: Pre-foreclosure, probate, divorce, absentee owners, equity analysis
- **Access**: Web platform with list-building and export tools
- **Pricing**: ~$100/month
- **Pros**: Good filtering and list-building tools, lead list export
- **Cons**: Florida coverage may be less complete than Western state coverage

### 6.3 ForeclosureAuctionData.com

- **Coverage**: All 67 Florida counties (Florida-specific)
- **Data available**: Foreclosure auctions, tax deed auctions, property details, valuation, sales history
- **Access**: Web platform, spreadsheet views, search tools
- **Pricing**: $29/month (single county), $99/month (all counties)
- **Pros**: Florida-specific focus, affordable, covers both Lee and Collier
- **Cons**: No API; web-only access

### 6.4 PropertyOnion.com

- **Coverage**: All Florida counties
- **Data available**: Foreclosures, tax deeds, wholesale deals, property data, interactive maps
- **Access**: Web platform with subscription
- **Pricing**: Subscription-based (free trial available)
- **Pros**: Florida-specific, interactive maps, auction history
- **Cons**: No API; focused on investors more than agents

### 6.5 Recommendation

For **TheLeadEdge MVP**, the most cost-effective approach is:
1. **ForeclosureAuctionData.com** ($29-99/month) for foreclosure/auction monitoring
2. **Monthly Sunshine Law requests** (near-free) for lis pendens and probate filings
3. **Manual weekly checks** of clerk websites for time-sensitive signals
4. **ATTOM Data API** ($150+/month) only when scaling to Phase 4+

---

## 7. Automation Feasibility Matrix

### 7.1 By Data Source

| Source | System | httpx Feasible? | Playwright Needed? | API Available? | RSS/Email? | Best Approach |
|--------|--------|-----------------|-------------------|----------------|------------|---------------|
| Lee Official Records (or.leeclerk.org) | Custom web app | Unlikely (bot protection) | Yes | No | No | Sunshine Law request |
| Lee Court Cases (matrix.leeclerk.org) | Matrix system | No (JS-heavy, timed out) | Yes, with limitations | No | No | Sunshine Law request |
| Lee Foreclosures (lee.realforeclose.com) | ColdFusion (RealAuction) | Possibly (server-rendered) | Fallback | No | No | 3rd party aggregator |
| Lee Code Enforcement (Accela) | Accela Citizen Access | No (form-based) | Yes | Accela API (needs county auth) | No | Sunshine Law request |
| Collier Document Search (app.collierclerk.com) | COR Public Access | Possibly (rendered for fetch) | Recommended | No | No | Sunshine Law request |
| Collier Court Cases (cms.collierclerk.com) | ShowCase CMS | No (JS-heavy) | Yes | No | No | Sunshine Law request |
| Collier Foreclosures | Clerk calendar | Unknown | Likely | No | No | 3rd party aggregator |
| Collier Code Enforcement (CityView) | CityView Portal | No (case # required) | Very limited | No | No | Sunshine Law request |

### 7.2 Effort vs. Value Assessment

| Approach | Setup Effort | Maintenance Effort | Data Quality | Data Freshness | Cost |
|----------|-------------|-------------------|-------------|----------------|------|
| **Sunshine Law requests (monthly)** | Low | Low (template-based) | High (authoritative) | Monthly lag | Near-free |
| **Manual weekly clerk website checks** | None | Medium (15-30 min/week) | High | Weekly | Free |
| **Playwright browser automation** | High (10-20 hrs each source) | High (breaks with site changes) | High | Can be daily | Free (dev time) |
| **3rd party aggregator subscription** | Low | Low | Good (slight lag) | Daily-weekly | $29-250/month |
| **ATTOM Data API integration** | Medium (coding time) | Low | Good | Daily | $150+/month |

---

## 8. Recommended Implementation Strategy

### Phase 2 (Automated Pipeline) -- Near-term

1. **Submit initial Sunshine Law requests** to both Lee and Collier County clerks for:
   - Lis pendens filings (last 90 days, then monthly going forward)
   - Probate case index (last 90 days, then monthly)
   - Code enforcement violations (last 6 months, then quarterly)

2. **Subscribe to ForeclosureAuctionData.com** ($29/month for Lee County, or $99 for both) for foreclosure auction monitoring.

3. **Build a CSV import pipeline** for Sunshine Law response data (reuse the existing MLS CSV import infrastructure with new field mappings).

4. **Establish a manual weekly check routine** for clerk websites (lis pendens by date range), taking 15-30 minutes per county.

### Phase 4 (Integrations) -- Medium-term

5. **Build Playwright automation** for the Collier County Document Search (app.collierclerk.com) as the first automation target (it rendered successfully, suggesting lighter bot protection):
   - Automate: Select document type "Lis Pendens" + date range + search + parse results
   - Run daily or weekly on a schedule
   - Parse HTML results into structured data

6. **Build Playwright automation** for lee.realforeclose.com auction calendar:
   - Fetch calendar page, parse auction dates
   - For each auction date, fetch day list, parse property details
   - Run weekly

7. **Inquire about Accela API access** for Lee County code enforcement data. If granted, build a direct API integration.

### Phase 5 (Intelligence) -- Longer-term

8. **Evaluate ATTOM Data API** for broader pre-foreclosure and public records data if the business justifies the $150+/month cost.

9. **Build a newspaper legal notice parser** -- Florida requires foreclosure sale publication in local newspapers. The News-Press (Lee) and Naples Daily News (Collier) publish these. Some newspapers have online legal notice sections that could be scraped.

---

## Appendix A: Contact Information

| Entity | Purpose | Contact |
|--------|---------|---------|
| Lee County Clerk -- Public Records | Sunshine Law requests | leeclerk.org/services/public-records-request |
| Lee County Clerk -- CRI Accounts | Account/access questions | CRIaccounts@leeclerk.org |
| Lee County Code Enforcement | Code violations, API inquiry | (239) 533-8895, codeenforcement@leegov.com |
| Collier County Clerk -- Public Records | Sunshine Law requests | Renata Robbins, (239) 252-2646 |
| Collier County Clerk -- CIT Dept | Agency registration, technical access | 3315 Tamiami Trail E, Suite 102, Naples, FL 34112 |
| Collier County Code Enforcement | Code violations | (239) 252-2440 |
| RealAuction.com | Auction platform vendor | sales@realauction.com |
| ForeclosureAuctionData.com | FL foreclosure data aggregator | foreclosureauctiondata.com/contact |

## Appendix B: Broward County API -- Reference Model

Broward County (17th Judicial Circuit) is the only Florida county confirmed to offer a **public commercial API** for court records. Key details as a reference for what Lee/Collier might eventually offer:

- **URL**: api.browardclerk.org
- **Type**: Web API (likely REST)
- **Case types**: Felony, Traffic & Misdemeanor, Circuit & County Civil, Probate, Domestic Violence, Family
- **Endpoints**: Case search, case detail (summaries, parties, events, hearings, related cases, arrests, charges, warrants, bonds, pleas, dispositions, sentencing, judgments, guardianship)
- **Pricing**: Subscription-based, unit purchase model (see "Cost of Purchasing Units" document)
- **Requirements**: Notarized Commercial Data Services registration agreement
- **Limitation**: Electronic document downloads not available via API (index data only)
- **Contact**: publicaccesshelpdesk@browardclerk.org

This demonstrates that programmatic court records access is possible in Florida, but requires county-level adoption. Lee and Collier counties have not adopted this model.

## Appendix C: Key Legal Considerations

1. **Terms of Service**: Before scraping any clerk website, review their Terms of Service/Use. Automated access may violate ToS even if the data is public.

2. **Florida Computer Abuse and Data Recovery Act** (F.S. 668.801-805): Unauthorized access to computer systems is a state crime. However, accessing public-facing search interfaces within their intended use is generally not a violation.

3. **Rate limiting**: If automating searches, implement respectful rate limiting (minimum 3-5 seconds between requests) to avoid overloading public infrastructure.

4. **No PII logging**: Per project security rules, never log or store defendant/homeowner names, phone numbers, email addresses, or home addresses in application logs. Only store in the secured database with proper access controls.

5. **MLS data separation**: Public records data and MLS data are governed by different rules. Keep them separated in the data model and be clear about the source of each lead signal.

6. **Sunshine Law is the safest path**: Public records requests under Chapter 119 are the legally cleanest way to obtain bulk data. The data is provided by the custodial agency in their format, eliminating any question about unauthorized access.
