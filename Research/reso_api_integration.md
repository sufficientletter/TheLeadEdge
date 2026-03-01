# RESO Web API & MLS Technical Integration

> **Project**: LeadFinder -- Real Estate Lead Generation System
> **Created**: 2026-02-28
> **Purpose**: Comprehensive technical reference for integrating with MLS data via the RESO Web API standard
> **Audience**: Developer building automated lead generation tools for a licensed Realtor

---

## Table of Contents

1. [RESO Web API Standard](#1-reso-web-api-standard)
2. [RESO Data Dictionary](#2-reso-data-dictionary)
3. [How to Get API Access](#3-how-to-get-api-access)
4. [Key Endpoints for Lead Generation](#4-key-endpoints-for-lead-generation)
5. [Sample API Queries](#5-sample-api-queries)
6. [Python Integration](#6-python-integration)
7. [Data Freshness & Sync Strategies](#7-data-freshness--sync-strategies)
8. [MLS-Specific Variations](#8-mls-specific-variations)
9. [Compliance Requirements](#9-compliance-requirements)
10. [Fallback Approaches](#10-fallback-approaches)

---

## 1. RESO Web API Standard

### 1.1 What Is RESO?

The **Real Estate Standards Organization (RESO)** is an industry body that develops and maintains data standards for real estate technology. Founded in 2011 as a subsidiary of NAR (National Association of Realtors), RESO has become the governing authority for how MLS data is structured, accessed, and exchanged.

The **RESO Web API** is the modern, RESTful standard for programmatic access to MLS data. It replaces the legacy RETS (Real Estate Transaction Standard) protocol, which was officially deprecated and sunset for new implementations as of late 2021, with most MLS boards completing migration by 2023-2024. Some legacy RETS endpoints still operate, but all new development should target the RESO Web API.

### 1.2 Current Version & Specification

**RESO Web API 2.0.0** is the current production standard. Key specification details:

| Aspect | Detail |
|--------|--------|
| **Standard** | RESO Web API 2.0.0 |
| **Transport** | HTTPS (TLS 1.2+) |
| **Protocol** | OData v4.0 (OASIS Standard) |
| **Data Format** | JSON (default), XML (optional) |
| **Query Language** | OData system query options ($filter, $select, $orderby, etc.) |
| **Authentication** | OAuth 2.0 (client credentials or authorization code grant) |
| **Metadata** | OData $metadata endpoint (CSDL/EDMX format) |
| **Certification** | RESO tests and certifies MLS providers for compliance |

The RESO Web API is built directly on the **OData v4** standard from OASIS. This means any OData-compatible client library can be used to interact with the API. The URL patterns, query syntax, and response formats all follow OData conventions.

### 1.3 How It Works

The RESO Web API follows a standard RESTful architecture:

```
Client (Your App)
    |
    |  1. OAuth 2.0 token request (client_id + client_secret)
    v
Token Endpoint (e.g., https://api.mlsboard.com/oauth2/token)
    |
    |  2. Returns access_token (Bearer token, typically expires in 3600s)
    v
Client (Your App)
    |
    |  3. API request with Authorization: Bearer <token>
    |     GET /odata/Property?$filter=StandardStatus eq 'Expired'
    v
RESO Web API Server (MLS Data Platform)
    |
    |  4. Returns JSON response with matching records
    v
Client processes response, paginates if needed via @odata.nextLink
```

**Request/Response Cycle:**

1. **Authenticate**: POST to the OAuth token endpoint with your client credentials.
2. **Query**: Send GET requests to resource endpoints with OData query parameters.
3. **Paginate**: Follow `@odata.nextLink` URLs to retrieve additional pages.
4. **Refresh**: Re-authenticate when the token expires (typically every 60 minutes).

### 1.4 Authentication: OAuth 2.0

The RESO Web API uses OAuth 2.0. The most common flow for server-to-server applications (like LeadFinder) is the **Client Credentials Grant**:

```http
POST /oauth2/token HTTP/1.1
Host: api.mlsboard.com
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
&scope=api
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "api"
}
```

Some MLS platforms (particularly those using Bridge Interactive or Trestle) may use slightly different token endpoint paths or require additional parameters. The token is then sent in subsequent requests:

```http
GET /odata/Property?$top=10 HTTP/1.1
Host: api.mlsboard.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```

**Token Lifecycle Considerations:**
- Tokens typically expire in 3600 seconds (1 hour)
- Some providers use shorter lifetimes (900-1800 seconds)
- Do NOT request a new token for every API call -- cache and reuse
- Implement token refresh logic that triggers before expiration
- Store the token in memory only, never persist to disk or logs

### 1.5 Rate Limits

Rate limits vary by MLS platform and access tier, but general patterns:

| Platform | Typical Rate Limit | Page Size Limit | Daily Quota |
|----------|-------------------|-----------------|-------------|
| **Trestle (CoreLogic)** | 1,200 requests/hour | 200 records/page | Varies by agreement |
| **Bridge Interactive** | 2,000 requests/hour | 200 records/page | No hard daily cap |
| **Spark API (FBS)** | 500 requests/hour | 1,000 records/page | 50,000 records/day |
| **MLS Grid** | 1,000 requests/hour | 200 records/page | Varies |
| **RESO Minimum** | Varies | 200 records/page (standard) | Varies |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 1200
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1709164800
Retry-After: 30
```

When you hit a 429 (Too Many Requests), always respect the `Retry-After` header. Implement exponential backoff as a secondary strategy.

### 1.6 OData Query Options Reference

The RESO Web API supports these OData v4 system query options:

| Option | Purpose | Example |
|--------|---------|---------|
| `$filter` | Filter records by criteria | `$filter=StandardStatus eq 'Active'` |
| `$select` | Choose specific fields to return | `$select=ListingKey,ListPrice,StandardStatus` |
| `$orderby` | Sort results | `$orderby=ListPrice desc` |
| `$top` | Limit number of results | `$top=100` |
| `$skip` | Skip N records (pagination) | `$skip=200` |
| `$count` | Include total record count | `$count=true` |
| `$expand` | Include related entities | `$expand=Media` |
| `$search` | Full-text search (limited support) | `$search=pool waterfront` |

**OData Filter Operators:**

| Operator | Meaning | Example |
|----------|---------|---------|
| `eq` | Equal | `StandardStatus eq 'Expired'` |
| `ne` | Not equal | `StandardStatus ne 'Active'` |
| `gt` | Greater than | `ListPrice gt 200000` |
| `ge` | Greater than or equal | `DaysOnMarket ge 90` |
| `lt` | Less than | `ListPrice lt 500000` |
| `le` | Less than or equal | `DaysOnMarket le 30` |
| `and` | Logical AND | `ListPrice gt 200000 and BedroomsTotal ge 3` |
| `or` | Logical OR | `StandardStatus eq 'Expired' or StandardStatus eq 'Withdrawn'` |
| `not` | Logical NOT | `not StandardStatus eq 'Active'` |
| `contains()` | String contains | `contains(PublicRemarks, 'motivated')` |
| `startswith()` | String starts with | `startswith(PostalCode, '852')` |
| `endswith()` | String ends with | `endswith(StreetName, 'Ave')` |

**OData Functions in Filters:**

| Function | Purpose | Example |
|----------|---------|---------|
| `year()` | Extract year | `year(ListingContractDate) eq 2025` |
| `month()` | Extract month | `month(CloseDate) eq 6` |
| `day()` | Extract day | `day(ExpirationDate) ge 15` |
| `now()` | Current datetime | `ModificationTimestamp gt now() sub duration'P7D'` |
| `geo.distance()` | Geographic distance (if supported) | `geo.distance(Coordinates, geography'POINT(-111.94 33.41)') le 5` |

---

## 2. RESO Data Dictionary

### 2.1 Overview

The **RESO Data Dictionary** (DD) standardizes field names, data types, and enumerations across all MLS systems. Before RESO DD, every MLS used its own field names (one might call it "ListPrice", another "LP", another "AskingPrice"). The Data Dictionary eliminates this fragmentation.

**Current Version**: Data Dictionary 2.0 (DD 2.0)

The Data Dictionary defines:
- **Resources** (entities/tables): Property, Member, Office, Media, OpenHouse, etc.
- **Fields** (columns): StandardStatus, ListPrice, DaysOnMarket, etc.
- **Lookups** (enumerations): Allowed values for enumerated fields
- **Data Types**: String, Decimal, Integer, Date, Timestamp, Boolean, Collection

### 2.2 Core Resources

| Resource | Description | Key Use for LeadFinder |
|----------|-------------|----------------------|
| **Property** | Listing data -- the primary resource | All lead generation queries |
| **Member** | Agent/broker information | Identifying listing agents, tracking agent behavior |
| **Office** | Brokerage office data | Market share analysis, team identification |
| **Media** | Photos, virtual tours, documents | Not critical for lead gen, but useful for CMA |
| **OpenHouse** | Open house schedules | Not critical for lead gen |
| **HistoryTransactional** | Historical listing changes | Price change history, status change tracking |
| **Teams** | Agent team structures | Agent team analysis |
| **OUID** | Organization unique IDs | Cross-MLS identification |
| **Contacts** | Agent contacts/leads | Not typically accessible |

### 2.3 Critical Property Fields for Lead Generation

These are the most important fields for identifying motivated sellers and high-probability leads:

#### Listing Status & Dates

| Field Name | Type | Description | Lead Gen Value |
|------------|------|-------------|----------------|
| `ListingKey` | String | Unique listing identifier | Primary key for tracking |
| `ListingId` | String | MLS number | Human-readable ID |
| `StandardStatus` | Enum | Current listing status | Core filter for all queries |
| `MlsStatus` | Enum | MLS-specific status (more granular) | Board-specific statuses |
| `StatusChangeTimestamp` | Timestamp | When status last changed | Detect recent expirations/withdrawals |
| `ListingContractDate` | Date | Date listing agreement was signed | Calculate true time on market |
| `ExpirationDate` | Date | Listing agreement expiration date | Predict upcoming expirations |
| `OnMarketDate` | Date | Date listing went live on MLS | Active marketing period start |
| `ContractStatusChangeDate` | Date | When contract status changed | Track pending/sold transitions |
| `WithdrawnDate` | Date | When listing was withdrawn | Withdrawn listing mining |
| `CancelationDate` | Date | When listing was cancelled | Cancelled listing mining |
| `CloseDate` | Date | Closing/settlement date | Sold property analysis |
| `ModificationTimestamp` | Timestamp | Last modified datetime | Incremental sync anchor |
| `OriginalEntryTimestamp` | Timestamp | First entry into MLS | True listing history |

#### Pricing Fields

| Field Name | Type | Description | Lead Gen Value |
|------------|------|-------------|----------------|
| `ListPrice` | Decimal | Current asking price | Current ask |
| `OriginalListPrice` | Decimal | Initial asking price | Calculate total price reduction |
| `PreviousListPrice` | Decimal | Price before latest change | Recent price drop amount |
| `ClosePrice` | Decimal | Final sale price | Comp analysis, market reality check |
| `PriceChangeTimestamp` | Timestamp | When price last changed | Detect fresh price reductions |
| `ListPriceLow` | Decimal | Low end of range pricing | Range-priced listings (desperation signal) |

**Derived Calculations:**
```
Total Price Reduction = OriginalListPrice - ListPrice
Price Reduction % = (OriginalListPrice - ListPrice) / OriginalListPrice * 100
Spread = ListPrice - ClosePrice (on sold comps)
```

#### Days on Market

| Field Name | Type | Description | Lead Gen Value |
|------------|------|-------------|----------------|
| `DaysOnMarket` | Integer | Days since current listing | Current listing period |
| `CumulativeDaysOnMarket` | Integer | Total days across all listing periods | True total exposure (survives relisting) |
| `OriginalOnMarketTimestamp` | Timestamp | Original on-market date across all periods | True first listing date |

**Key Insight**: When `CumulativeDaysOnMarket > DaysOnMarket`, the property was withdrawn and relisted (DOM was reset). This is a signal of agent change, strategy change, or desperation.

#### Property Details

| Field Name | Type | Description | Lead Gen Value |
|------------|------|-------------|----------------|
| `PropertyType` | Enum | Residential, Land, Commercial, etc. | Filter to relevant types |
| `PropertySubType` | Enum | SingleFamily, Condo, Townhouse, etc. | Granular filtering |
| `BedroomsTotal` | Integer | Number of bedrooms | CMA matching |
| `BathroomsTotalInteger` | Integer | Number of bathrooms | CMA matching |
| `LivingArea` | Decimal | Square footage | CMA matching, price/sqft |
| `LotSizeAcres` | Decimal | Lot size in acres | Land value analysis |
| `YearBuilt` | Integer | Year constructed | Age-related issues, renovation potential |
| `StreetNumberNumeric` | String | Street number | Address construction |
| `StreetName` | String | Street name | Address construction |
| `City` | String | City name | Geographic filtering |
| `StateOrProvince` | String | State abbreviation | Geographic filtering |
| `PostalCode` | String | ZIP code | Geographic filtering |
| `CountyOrParish` | String | County name | Public records cross-reference |
| `Latitude` | Decimal | GPS latitude | Mapping, radius searches |
| `Longitude` | Decimal | GPS longitude | Mapping, radius searches |

#### Agent & Office Information

| Field Name | Type | Description | Lead Gen Value |
|------------|------|-------------|----------------|
| `ListAgentKey` | String | Listing agent identifier | Track agent patterns |
| `ListAgentFullName` | String | Listing agent name | Outreach context |
| `ListAgentEmail` | String | Agent email | Agent contact (be careful with usage) |
| `ListOfficeName` | String | Listing brokerage | Track brokerage patterns |
| `BuyerAgentKey` | String | Buyer's agent identifier | Buyer agent activity analysis |
| `CoListAgentKey` | String | Co-listing agent identifier | Team listings |

#### Remarks & Descriptions

| Field Name | Type | Description | Lead Gen Value |
|------------|------|-------------|----------------|
| `PublicRemarks` | String | Public listing description | NLP for motivation signals |
| `PrivateRemarks` | String | Agent-only remarks | MLS member-only insights (if accessible) |
| `ShowingInstructions` | String | How to arrange showings | Vacancy indicators, lockbox = vacant |
| `SpecialListingConditions` | Collection | REO, short sale, auction, etc. | Distressed property identification |

### 2.4 StandardStatus Enum Values

The `StandardStatus` field is the most important field for lead generation queries:

| Value | Meaning | Lead Gen Relevance |
|-------|---------|-------------------|
| `Active` | Currently for sale on MLS | DOM analysis, price reduction mining |
| `Active Under Contract` | Under contract but still showing | Backup offer opportunities |
| `Pending` | Under contract, no longer showing | Monitor for fallthrough |
| `Closed` | Sold and recorded | Comp data, market analysis |
| `Expired` | Listing agreement expired | **HIGH VALUE** -- motivated sellers without agent |
| `Withdrawn` | Removed from active marketing | **HIGH VALUE** -- potential re-engagement |
| `Canceled` | Listing agreement terminated | Similar to withdrawn, different reason |
| `Coming Soon` | Pre-marketing (not yet active) | Early intelligence |
| `Delete` | Removed from MLS entirely | Data cleanup |
| `Hold` | Temporarily off market | Monitor for return |
| `Incomplete` | Listing data incomplete | Generally not useful |

### 2.5 SpecialListingConditions Values

| Value | Meaning | Lead Gen Signal |
|-------|---------|----------------|
| `Standard` | Normal sale | Baseline |
| `REO/Bank Owned` | Foreclosure completed, bank selling | Distressed |
| `Short Sale` | Selling for less than mortgage balance | Distressed |
| `Auction` | Sold at auction | Distressed / time-pressured |
| `Probate/Estate` | Owner deceased, estate selling | Motivated, often flexible on price |
| `HUD Owned` | Government-owned (FHA foreclosure) | Specific process, not lead gen |
| `Court Ordered` | Divorce, bankruptcy, etc. | Distressed, must sell |
| `Notice of Default` | Pre-foreclosure notice filed | **Extremely motivated** |

---

## 3. How to Get API Access

### 3.1 Access Path for a Licensed Realtor

Getting RESO Web API access follows this general process:

**Step 1: Identify Your MLS Board's Data Platform**

Your wife's MLS membership includes data access rights. First, determine which technology platform her MLS board uses to serve data:

```
MLS Board
   |
   +-- Uses a data platform to serve the RESO Web API
       |
       +-- Trestle (CoreLogic) -- ~600+ MLSs
       +-- Bridge Interactive (Zillow Group) -- ~300+ MLSs
       +-- Spark API (FBS/FlexMLS) -- ~200+ MLSs
       +-- MLS Grid -- ~100+ MLSs
       +-- Proprietary (some large boards run their own)
```

**How to find out**: Call the MLS board's tech support or check their member portal. Look for sections labeled "Developer Resources", "API Access", "Data Feeds", or "RETS/RESO". The board website usually lists their data platform partner.

**Step 2: Request API Credentials**

Contact the MLS board's IT department or the data platform directly:

| Contact Method | Who to Ask | What to Say |
|---------------|------------|-------------|
| MLS Board tech support | Board staff | "I'm a member and want API access for a custom application for my business" |
| Data platform portal | Self-service (some platforms) | Register at the platform's developer portal |
| Written application | Board compliance | Fill out the data license application |

**What they will ask for:**
- MLS member ID (your wife's license/member number)
- Business purpose (describe as "custom market analysis tool for my real estate practice")
- Application name ("LeadFinder" or similar)
- Intended data usage (display, analysis, internal business use)
- Acknowledgment of data usage policies
- Sometimes: proof of active license, E&O insurance info

**Step 3: Receive Credentials**

Upon approval, you receive:

| Credential | Description |
|-----------|-------------|
| `Base URL` | The API server URL (e.g., `https://api.trestle.corelogic.com/trestle/odata`) |
| `Client ID` | Your application identifier (public) |
| `Client Secret` | Your application secret (keep confidential) |
| `Token Endpoint` | OAuth token URL (e.g., `https://api.trestle.corelogic.com/trestle/oidc/connect/token`) |
| `Scope` | Authorized access scope (e.g., `api`) |

**Step 4: Sign the Data License Agreement**

Almost every MLS requires a signed data license agreement. Key terms you will agree to:

- Data used only in connection with licensed real estate business
- No resale or redistribution of raw MLS data
- Comply with display rules (IDX/VOW if applicable)
- Data retention and deletion policies
- Security requirements for stored data
- Audit rights (MLS can audit your data usage)

### 3.2 Vendor vs. Member Access

There are two types of API access, and they differ significantly:

| Aspect | Member Access | Vendor Access |
|--------|--------------|---------------|
| **Who** | Licensed Realtor/Broker | Technology company/developer |
| **Application** | Through MLS board membership | Formal vendor application |
| **Cost** | Included with MLS dues (usually) | Monthly/annual licensing fee ($500-$5,000+/mo) |
| **Data Scope** | Member's market area | Full MLS coverage |
| **Requirements** | Active MLS membership | Business license, E&O, vendor agreement |
| **Rate Limits** | Standard tier | Often higher limits |
| **Approval Time** | Days to weeks | Weeks to months |
| **Best For** | Our use case (personal business tool) | SaaS products serving multiple agents |

**For LeadFinder**: We want **Member Access** because the Realtor (wife) is using API access for her own licensed business. This is the simplest path with the lowest cost.

### 3.3 RETS vs. RESO Web API (Migration Status)

| Aspect | RETS (Legacy) | RESO Web API (Current) |
|--------|--------------|----------------------|
| **Status** | Deprecated (sunset 2021) | Active standard |
| **Protocol** | Custom XML-based | OData v4 (RESTful JSON) |
| **Authentication** | HTTP Digest Auth | OAuth 2.0 |
| **Query Language** | DMQL2 (proprietary) | OData $filter (standard) |
| **Data Format** | XML (COMPACT, COMPACT-DECODED) | JSON (primary), XML (optional) |
| **Metadata** | GetMetadata request | OData $metadata endpoint |
| **Pagination** | Offset-based (limited) | @odata.nextLink (cursor-based) |
| **Media** | GetObject (binary) | Media resource with URLs |
| **Industry Support** | Legacy only | All new development |
| **Libraries** | librets (C++/Python), rets-client (PHP) | Any OData or HTTP library |

**Migration status as of 2025-2026**: The vast majority of MLS boards have completed migration to RESO Web API. Some boards still maintain legacy RETS endpoints for backward compatibility, but these are not being enhanced and may be shut down at any time. All new integrations should use the RESO Web API exclusively.

**If your board still only offers RETS**: Contact them about RESO Web API availability. If truly RETS-only, consider using `rets-python` or `librets` as a bridge, but plan for migration.

### 3.4 Typical Timeline

| Step | Duration | Notes |
|------|----------|-------|
| Identify data platform | 1-2 days | Call MLS board, check member portal |
| Submit application | 1 day | Online form or email |
| Application review | 3-14 days | Board compliance review |
| Credential issuance | 1-3 days | After approval |
| Initial testing | 2-5 days | Test queries, understand schema |
| **Total** | **1-3 weeks** | Varies significantly by board |

---

## 4. Key Endpoints for Lead Generation

### 4.1 Primary Endpoint: Property Resource

The `/Property` endpoint is the workhorse for lead generation. All listing data is accessed through this single resource with different filters applied.

```
GET {base_url}/Property?$filter={criteria}&$select={fields}&$orderby={sort}&$top={limit}
```

### 4.2 Lead Generation Query Categories

#### Category 1: Expired Listings

Expired listings represent sellers who wanted to sell, failed, and now lack agent representation. This is the highest-value lead category.

**Query Logic:**
- StandardStatus = Expired
- StatusChangeTimestamp within recent days
- Optional: filter by area, price range, property type

**Use Case**: Daily scan for newly expired listings. Contact the homeowner before competing agents.

#### Category 2: Price Reductions

Sellers who reduce their price are signaling increased motivation. Multiple reductions indicate urgency.

**Query Logic:**
- StandardStatus = Active
- ListPrice < OriginalListPrice (at least one reduction)
- PriceChangeTimestamp within recent days (to catch fresh reductions)
- Calculate reduction percentage for severity

**Use Case**: Daily monitoring for new price drops, especially aggressive ones (>5% in a single drop or >10% cumulative).

#### Category 3: High Days on Market (DOM)

Properties lingering on market far beyond the market average indicate pricing, condition, or motivation issues.

**Query Logic:**
- StandardStatus = Active
- DaysOnMarket above a threshold (90+ days as a starting point, adjust for market conditions)
- Optionally compare to market average DOM by ZIP/price range

**Use Case**: Weekly sweep for stale listings. These sellers are increasingly frustrated and may be open to a new agent with a fresh strategy.

#### Category 4: Withdrawn and Relisted

When a property is withdrawn and relisted, the DOM counter resets. CumulativeDaysOnMarket reveals the true exposure time. This indicates strategy changes, agent changes, or desperation.

**Query Logic:**
- StandardStatus = Active
- CumulativeDaysOnMarket > DaysOnMarket (proves a reset occurred)
- The larger the gap, the more times it has been cycled

**Use Case**: Identify properties being "recycled" on the MLS -- a strong sign of a motivated but poorly served seller.

#### Category 5: Status Changes (Withdrawn, Cancelled, Hold)

Properties changing from Active to Withdrawn/Cancelled may indicate seller frustration, agent conflict, or personal circumstances. These sellers often re-enter the market.

**Query Logic:**
- StandardStatus in (Withdrawn, Canceled, Hold)
- StatusChangeTimestamp within recent days
- Cross-reference with later Active status to detect relisting

**Use Case**: Monitor recent withdrawals and cancellations. Wait 2-4 weeks, then reach out with a fresh approach.

#### Category 6: Back on Market (Failed Contracts)

Properties that were Pending or Active Under Contract but return to Active status indicate a deal fell through. The seller is now frustrated and under time pressure.

**Query Logic:**
- StandardStatus = Active
- Previous status was Pending or Active Under Contract
- StatusChangeTimestamp within recent days
- Some MLS boards have a "Back on Market" status or flag

**Use Case**: Immediate opportunity -- the seller was expecting to close, the deal fell apart, and they need to start over. High motivation.

#### Category 7: Approaching Expiration

Listings whose expiration date is coming up within 2-4 weeks are a proactive lead source. Contact the seller before the listing expires while they are evaluating their next move.

**Query Logic:**
- StandardStatus = Active
- ExpirationDate is within 14-30 days from today
- High DOM or price reductions amplify the signal

**Use Case**: Pre-expire outreach. The seller is already thinking about what happens next.

#### Category 8: FSBO Indicators

True FSBO (For Sale By Owner) is not in the MLS by definition. However, some MLS boards have FSBO-entry options, "Entry Only" listing types, or minimal-service listing categories. Additionally, recently expired/withdrawn listings may go FSBO.

**Query Logic:**
- Look for `ListAgentKey` associated with entry-only/flat-fee brokerages
- `ListingAgreement` = 'Entry Only' (if field is available)
- Very low commission offerings in `BuyerAgencyCompensation`
- Listings with minimal photos, no virtual tour, sparse remarks

**Use Case**: FSBO sellers struggle statistically (lower prices, longer timelines). They are excellent conversion targets for a full-service agent.

#### Category 9: Distressed Properties

Properties flagged with distressed conditions in the MLS.

**Query Logic:**
- SpecialListingConditions contains 'Short Sale', 'REO/Bank Owned', 'Auction', 'Notice of Default', or 'Probate/Estate'
- StandardStatus = Active
- Often combined with price and area filters

**Use Case**: Distressed properties often have motivated sellers, tight timelines, and specific needs for experienced agents.

### 4.3 Supporting Endpoints

| Endpoint | Use for Lead Gen |
|----------|-----------------|
| `GET /Member` | Look up listing agent details, phone, email |
| `GET /Office` | Identify brokerage, useful for tracking market share |
| `GET /Media` | Retrieve listing photos (for CMA reports) |
| `GET /OpenHouse` | Minimal lead gen value, but can indicate activity level |
| `GET /HistoryTransactional` | Track full history of price changes and status changes on a listing |

---

## 5. Sample API Queries

Below are practical OData queries for each lead generation scenario. All queries assume a base URL like `https://api.mlsboard.com/odata` and use standard RESO Data Dictionary 2.0 field names.

### Query 1: Recently Expired Listings (Last 7 Days)

```
GET /Property?
  $filter=StandardStatus eq 'Expired'
    and StatusChangeTimestamp gt 2026-02-21T00:00:00Z
  &$select=ListingKey,ListingId,StandardStatus,ListPrice,OriginalListPrice,
    StreetNumberNumeric,StreetName,City,PostalCode,
    BedroomsTotal,BathroomsTotalInteger,LivingArea,
    DaysOnMarket,CumulativeDaysOnMarket,
    ListAgentFullName,ListOfficeName,
    ListingContractDate,ExpirationDate,StatusChangeTimestamp,
    Latitude,Longitude
  &$orderby=StatusChangeTimestamp desc
  &$top=200
```

**What it returns**: All listings that expired within the last 7 days, sorted by most recent first. Includes address, pricing, agent info, and market timing data.

### Query 2: Active Listings with Price Reductions (Last 3 Days)

```
GET /Property?
  $filter=StandardStatus eq 'Active'
    and PriceChangeTimestamp gt 2026-02-25T00:00:00Z
    and ListPrice lt OriginalListPrice
  &$select=ListingKey,ListingId,ListPrice,OriginalListPrice,PreviousListPrice,
    PriceChangeTimestamp,StreetNumberNumeric,StreetName,City,PostalCode,
    DaysOnMarket,BedroomsTotal,BathroomsTotalInteger,LivingArea,
    ListAgentFullName,PublicRemarks,Latitude,Longitude
  &$orderby=PriceChangeTimestamp desc
  &$top=200
```

**Enhancement**: To calculate reduction severity in your application:
```python
reduction_pct = (record['OriginalListPrice'] - record['ListPrice']) / record['OriginalListPrice'] * 100
recent_drop = record['PreviousListPrice'] - record['ListPrice']
```

### Query 3: Stale Listings (90+ Days on Market)

```
GET /Property?
  $filter=StandardStatus eq 'Active'
    and DaysOnMarket ge 90
  &$select=ListingKey,ListingId,ListPrice,OriginalListPrice,
    DaysOnMarket,CumulativeDaysOnMarket,
    StreetNumberNumeric,StreetName,City,PostalCode,
    BedroomsTotal,BathroomsTotalInteger,LivingArea,YearBuilt,
    ListAgentFullName,ListOfficeName,OnMarketDate,
    Latitude,Longitude,PublicRemarks
  &$orderby=DaysOnMarket desc
  &$top=200
```

**Tiered thresholds**: Adjust the DOM threshold based on your local market:
- Hot market (Phoenix metro): 60+ days is stale
- Normal market: 90+ days is stale
- Slow market: 120+ days is stale

### Query 4: Withdrawn and Relisted Properties (DOM Reset Detected)

```
GET /Property?
  $filter=StandardStatus eq 'Active'
    and CumulativeDaysOnMarket gt DaysOnMarket
  &$select=ListingKey,ListingId,ListPrice,OriginalListPrice,
    DaysOnMarket,CumulativeDaysOnMarket,
    StreetNumberNumeric,StreetName,City,PostalCode,
    BedroomsTotal,BathroomsTotalInteger,LivingArea,
    ListAgentFullName,ListOfficeName,
    OnMarketDate,OriginalOnMarketTimestamp,
    Latitude,Longitude
  &$orderby=CumulativeDaysOnMarket desc
  &$top=200
```

**Interpretation**: A property with DOM=15 but CDOM=180 was relisted 15 days ago after sitting for ~165 days previously. The seller likely changed agents or strategy.

### Query 5: Recently Withdrawn/Cancelled Listings (Last 14 Days)

```
GET /Property?
  $filter=(StandardStatus eq 'Withdrawn' or StandardStatus eq 'Canceled')
    and StatusChangeTimestamp gt 2026-02-14T00:00:00Z
  &$select=ListingKey,ListingId,StandardStatus,ListPrice,OriginalListPrice,
    DaysOnMarket,CumulativeDaysOnMarket,
    StreetNumberNumeric,StreetName,City,PostalCode,
    BedroomsTotal,BathroomsTotalInteger,LivingArea,
    ListAgentFullName,StatusChangeTimestamp,
    WithdrawnDate,CancelationDate,
    Latitude,Longitude
  &$orderby=StatusChangeTimestamp desc
  &$top=200
```

**Follow-up**: After pulling these, wait 2-4 weeks and check if they relist. If not, they may have gone FSBO or given up temporarily -- prime outreach targets.

### Query 6: Listings Approaching Expiration (Next 30 Days)

```
GET /Property?
  $filter=StandardStatus eq 'Active'
    and ExpirationDate ge 2026-02-28
    and ExpirationDate le 2026-03-30
  &$select=ListingKey,ListingId,ListPrice,OriginalListPrice,
    DaysOnMarket,ExpirationDate,
    StreetNumberNumeric,StreetName,City,PostalCode,
    BedroomsTotal,BathroomsTotalInteger,LivingArea,
    ListAgentFullName,ListOfficeName,
    Latitude,Longitude
  &$orderby=ExpirationDate asc
  &$top=200
```

**Strategy**: Properties expiring within 14 days with high DOM and/or price reductions are the highest priority -- the seller is about to become an expired listing.

### Query 7: Distressed Properties (Short Sales, REO, Probate)

```
GET /Property?
  $filter=StandardStatus eq 'Active'
    and (contains(SpecialListingConditions, 'Short Sale')
      or contains(SpecialListingConditions, 'REO')
      or contains(SpecialListingConditions, 'Probate')
      or contains(SpecialListingConditions, 'Auction'))
  &$select=ListingKey,ListingId,ListPrice,OriginalListPrice,
    SpecialListingConditions,StandardStatus,
    DaysOnMarket,StreetNumberNumeric,StreetName,City,PostalCode,
    BedroomsTotal,BathroomsTotalInteger,LivingArea,YearBuilt,
    ListAgentFullName,PublicRemarks,
    Latitude,Longitude
  &$orderby=ModificationTimestamp desc
  &$top=200
```

**Note on SpecialListingConditions**: This field can be a multi-value collection in some implementations. The `contains()` function works for string matching, but some MLS platforms may require `has` or lambda expressions for collection types. Check your MLS platform's specific OData implementation.

### Query 8: Back on Market (Failed Contracts)

```
GET /Property?
  $filter=StandardStatus eq 'Active'
    and StatusChangeTimestamp gt 2026-02-21T00:00:00Z
    and DaysOnMarket gt 30
    and ModificationTimestamp gt 2026-02-21T00:00:00Z
  &$select=ListingKey,ListingId,ListPrice,OriginalListPrice,
    DaysOnMarket,CumulativeDaysOnMarket,
    StatusChangeTimestamp,ContractStatusChangeDate,
    StreetNumberNumeric,StreetName,City,PostalCode,
    BedroomsTotal,BathroomsTotalInteger,LivingArea,
    ListAgentFullName,PublicRemarks,
    Latitude,Longitude
  &$orderby=StatusChangeTimestamp desc
  &$top=200
```

**Challenge**: Most MLS systems do not provide a direct "Back on Market" filter or previous-status field in the Property resource. The most reliable approach is to:
1. Track listing statuses over time in your own database
2. Detect when a listing transitions from Pending/Active Under Contract back to Active
3. Use the HistoryTransactional resource if available for retroactive analysis

### Query 9: Incremental Sync (All Changes Since Last Sync)

```
GET /Property?
  $filter=ModificationTimestamp gt 2026-02-27T18:30:00Z
  &$select=ListingKey,ListingId,StandardStatus,MlsStatus,
    ListPrice,OriginalListPrice,PreviousListPrice,
    PriceChangeTimestamp,StatusChangeTimestamp,ModificationTimestamp,
    DaysOnMarket,CumulativeDaysOnMarket,
    StreetNumberNumeric,StreetName,City,PostalCode,
    BedroomsTotal,BathroomsTotalInteger,LivingArea,YearBuilt,
    ListAgentFullName,ListOfficeName,
    ExpirationDate,OnMarketDate,
    SpecialListingConditions,PublicRemarks,
    Latitude,Longitude
  &$orderby=ModificationTimestamp asc
  &$top=200
```

**This is the most important query for ongoing operation.** Run this every 15-60 minutes. Compare changes against your local database to detect:
- New expirations (status changed to Expired)
- New price drops (ListPrice changed, PriceChangeTimestamp updated)
- New withdrawals (status changed to Withdrawn/Canceled)
- Back on market (status changed from Pending to Active)
- New listings (newly inserted records)

### Query 10: Geographic Radius Search (If Supported)

```
GET /Property?
  $filter=StandardStatus eq 'Active'
    and geo.distance(
      Coordinates,
      geography'POINT(-111.9400 33.4150)'
    ) le 8.04672
  &$select=ListingKey,ListingId,ListPrice,
    StreetNumberNumeric,StreetName,City,PostalCode,
    DaysOnMarket,ListAgentFullName,
    Latitude,Longitude
  &$orderby=ListPrice desc
  &$top=100
```

**Note**: Geographic functions (`geo.distance`) are part of OData v4 but not universally supported by all MLS platforms. The distance is in kilometers (8.04672 km = 5 miles). If geo functions are unavailable, use bounding-box filtering with Latitude/Longitude ranges:

```
$filter=Latitude ge 33.38 and Latitude le 33.45
  and Longitude ge -111.97 and Longitude le -111.91
```

---

## 6. Python Integration

### 6.1 Recommended Libraries

| Library | Purpose | Install |
|---------|---------|---------|
| `httpx` | Async HTTP client (superior to requests for async) | `pip install httpx` |
| `requests` | Sync HTTP client (simpler for scripts) | `pip install requests` |
| `pydantic` | Data validation and parsing | `pip install pydantic` |
| `tenacity` | Retry logic with exponential backoff | `pip install tenacity` |
| `python-dotenv` | Environment variable management | `pip install python-dotenv` |
| `arrow` or `pendulum` | Timezone-aware datetime handling | `pip install arrow` |

**Note on RESO-specific libraries**: There is no widely-maintained, high-quality Python library specifically for the RESO Web API. Because the API is standard OData over HTTP, using `httpx` (or `requests`) directly with proper wrapper classes is the recommended approach. Some community libraries exist but are often outdated or poorly maintained.

### 6.2 Complete Client Implementation

```python
"""
reso_client.py - RESO Web API client for LeadFinder

A production-grade client for interacting with MLS data via the RESO Web API.
Handles authentication, pagination, rate limiting, and error recovery.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs

import httpx
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class RESOConfig(BaseModel):
    """Configuration for RESO Web API connection."""
    base_url: str = Field(..., description="Base OData URL, e.g. https://api.trestle.corelogic.com/trestle/odata")
    token_url: str = Field(..., description="OAuth2 token endpoint URL")
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    scope: str = Field(default="api", description="OAuth2 scope")
    page_size: int = Field(default=200, description="Records per page (max varies by provider)")
    max_retries: int = Field(default=3, description="Max retry attempts for failed requests")
    rate_limit_buffer: float = Field(default=0.1, description="Seconds to wait between requests")


# ---------------------------------------------------------------------------
# Token Management
# ---------------------------------------------------------------------------

class TokenInfo(BaseModel):
    """Cached OAuth2 token with expiration tracking."""
    access_token: str
    token_type: str = "Bearer"
    expires_at: float  # Unix timestamp when token expires
    scope: str = ""

    @property
    def is_expired(self) -> bool:
        """Check if token is expired or about to expire (60-second buffer)."""
        return time.time() >= (self.expires_at - 60)


# ---------------------------------------------------------------------------
# RESO Web API Client
# ---------------------------------------------------------------------------

class RESOClient:
    """
    Async client for the RESO Web API.

    Handles OAuth 2.0 authentication, automatic token refresh,
    pagination, rate limiting, and retry logic.

    Usage:
        config = RESOConfig(
            base_url="https://api.trestle.corelogic.com/trestle/odata",
            token_url="https://api.trestle.corelogic.com/trestle/oidc/connect/token",
            client_id="your_client_id",
            client_secret="your_client_secret",
        )

        async with RESOClient(config) as client:
            expired = await client.get_properties(
                filter_expr="StandardStatus eq 'Expired'",
                select=["ListingKey", "ListPrice", "StandardStatus"],
                orderby="StatusChangeTimestamp desc",
                top=100,
            )
    """

    def __init__(self, config: RESOConfig):
        self.config = config
        self._token: Optional[TokenInfo] = None
        self._client: Optional[httpx.AsyncClient] = None
        self._last_request_time: float = 0

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    # ---- Authentication ----

    async def _authenticate(self) -> TokenInfo:
        """Obtain or refresh OAuth 2.0 access token."""
        logger.info("Requesting new OAuth2 token...")

        response = await self._client.post(
            self.config.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "scope": self.config.scope,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()

        data = response.json()
        token = TokenInfo(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_at=time.time() + data.get("expires_in", 3600),
            scope=data.get("scope", ""),
        )

        logger.info("Token obtained, expires in %d seconds", data.get("expires_in", 3600))
        return token

    async def _get_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if self._token is None or self._token.is_expired:
            self._token = await self._authenticate()
        return self._token.access_token

    def _auth_headers(self, token: str) -> dict:
        """Build authorization headers."""
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    # ---- Rate Limiting ----

    async def _rate_limit_wait(self):
        """Enforce minimum time between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.config.rate_limit_buffer:
            await _async_sleep(self.config.rate_limit_buffer - elapsed)
        self._last_request_time = time.time()

    # ---- Core Request Method ----

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError)),
    )
    async def _request(self, url: str, params: Optional[dict] = None) -> dict:
        """
        Make an authenticated GET request with retry logic.

        Handles:
        - Token refresh on 401
        - Rate limiting on 429
        - Retries with exponential backoff on transient errors
        """
        await self._rate_limit_wait()
        token = await self._get_token()

        response = await self._client.get(
            url,
            params=params,
            headers=self._auth_headers(token),
        )

        # Handle 401 - token may have expired between check and use
        if response.status_code == 401:
            logger.warning("Got 401, refreshing token...")
            self._token = None
            token = await self._get_token()
            response = await self._client.get(
                url,
                params=params,
                headers=self._auth_headers(token),
            )

        # Handle 429 - rate limited
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 30))
            logger.warning("Rate limited, waiting %d seconds...", retry_after)
            await _async_sleep(retry_after)
            raise httpx.HTTPStatusError(
                "Rate limited",
                request=response.request,
                response=response,
            )

        response.raise_for_status()
        return response.json()

    # ---- Pagination ----

    async def _paginate(
        self,
        url: str,
        params: Optional[dict] = None,
        max_records: Optional[int] = None,
    ) -> list[dict]:
        """
        Fetch all pages of results, following @odata.nextLink.

        Args:
            url: Initial request URL
            params: OData query parameters
            max_records: Maximum total records to fetch (None = all)

        Returns:
            List of all records across all pages
        """
        all_records = []
        current_url = url
        current_params = params
        page_count = 0

        while current_url:
            page_count += 1
            logger.info("Fetching page %d (total records so far: %d)", page_count, len(all_records))

            data = await self._request(current_url, current_params)

            records = data.get("value", [])
            all_records.extend(records)

            # Check if we have reached max_records
            if max_records and len(all_records) >= max_records:
                all_records = all_records[:max_records]
                break

            # Follow pagination link
            next_link = data.get("@odata.nextLink")
            if next_link:
                current_url = next_link
                current_params = None  # nextLink includes all params
            else:
                break

        logger.info("Pagination complete: %d records across %d pages", len(all_records), page_count)
        return all_records

    # ---- Public API Methods ----

    async def get_properties(
        self,
        filter_expr: Optional[str] = None,
        select: Optional[list[str]] = None,
        orderby: Optional[str] = None,
        top: Optional[int] = None,
        max_records: Optional[int] = None,
        expand: Optional[str] = None,
        count: bool = False,
    ) -> list[dict]:
        """
        Query the Property resource.

        Args:
            filter_expr: OData $filter expression
            select: List of field names to return
            orderby: OData $orderby expression
            top: Page size ($top)
            max_records: Maximum total records across all pages
            expand: OData $expand expression
            count: Include total count in response

        Returns:
            List of property records (dicts)
        """
        url = f"{self.config.base_url}/Property"
        params = {}

        if filter_expr:
            params["$filter"] = filter_expr
        if select:
            params["$select"] = ",".join(select)
        if orderby:
            params["$orderby"] = orderby
        if top:
            params["$top"] = str(top)
        elif self.config.page_size:
            params["$top"] = str(self.config.page_size)
        if expand:
            params["$expand"] = expand
        if count:
            params["$count"] = "true"

        return await self._paginate(url, params, max_records)

    async def get_property_by_key(self, listing_key: str) -> Optional[dict]:
        """Fetch a single property by its ListingKey."""
        url = f"{self.config.base_url}/Property('{listing_key}')"
        try:
            return await self._request(url)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def get_members(
        self,
        filter_expr: Optional[str] = None,
        select: Optional[list[str]] = None,
        top: Optional[int] = None,
    ) -> list[dict]:
        """Query the Member resource (agent/broker data)."""
        url = f"{self.config.base_url}/Member"
        params = {}
        if filter_expr:
            params["$filter"] = filter_expr
        if select:
            params["$select"] = ",".join(select)
        if top:
            params["$top"] = str(top)
        return await self._paginate(url, params)

    async def get_metadata(self) -> str:
        """Fetch OData metadata document ($metadata)."""
        url = f"{self.config.base_url}/$metadata"
        token = await self._get_token()
        response = await self._client.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/xml",
            },
        )
        response.raise_for_status()
        return response.text

    async def get_record_count(self, filter_expr: Optional[str] = None) -> int:
        """Get total count of records matching a filter."""
        url = f"{self.config.base_url}/Property/$count"
        params = {}
        if filter_expr:
            params["$filter"] = filter_expr
        token = await self._get_token()
        response = await self._client.get(
            url,
            params=params,
            headers=self._auth_headers(token),
        )
        response.raise_for_status()
        return int(response.text.strip())


async def _async_sleep(seconds: float):
    """Async sleep helper."""
    import asyncio
    await asyncio.sleep(seconds)
```

### 6.3 Lead-Specific Query Methods

```python
"""
lead_queries.py - Pre-built lead generation queries using the RESO client.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from reso_client import RESOClient


# Standard fields to request for lead generation records
LEAD_GEN_FIELDS = [
    "ListingKey", "ListingId", "StandardStatus", "MlsStatus",
    "ListPrice", "OriginalListPrice", "PreviousListPrice",
    "PriceChangeTimestamp", "StatusChangeTimestamp", "ModificationTimestamp",
    "DaysOnMarket", "CumulativeDaysOnMarket",
    "StreetNumberNumeric", "StreetName", "UnitNumber",
    "City", "StateOrProvince", "PostalCode", "CountyOrParish",
    "BedroomsTotal", "BathroomsTotalInteger", "LivingArea", "YearBuilt",
    "PropertyType", "PropertySubType",
    "ListAgentFullName", "ListAgentKey", "ListOfficeName",
    "ListingContractDate", "ExpirationDate", "OnMarketDate",
    "CloseDate", "ClosePrice",
    "SpecialListingConditions", "PublicRemarks",
    "Latitude", "Longitude",
]


class LeadQueryService:
    """Pre-built queries for common lead generation scenarios."""

    def __init__(self, client: RESOClient):
        self.client = client

    async def get_expired_listings(
        self,
        days_back: int = 7,
        zip_codes: Optional[list[str]] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
    ) -> list[dict]:
        """Fetch recently expired listings."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()

        filters = [
            "StandardStatus eq 'Expired'",
            f"StatusChangeTimestamp gt {cutoff}",
        ]

        if zip_codes:
            zip_filter = " or ".join(f"PostalCode eq '{z}'" for z in zip_codes)
            filters.append(f"({zip_filter})")
        if min_price:
            filters.append(f"ListPrice ge {min_price}")
        if max_price:
            filters.append(f"ListPrice le {max_price}")

        return await self.client.get_properties(
            filter_expr=" and ".join(filters),
            select=LEAD_GEN_FIELDS,
            orderby="StatusChangeTimestamp desc",
        )

    async def get_price_reductions(
        self,
        days_back: int = 3,
        min_reduction_pct: float = 0.0,
        zip_codes: Optional[list[str]] = None,
    ) -> list[dict]:
        """Fetch active listings with recent price reductions."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()

        filters = [
            "StandardStatus eq 'Active'",
            f"PriceChangeTimestamp gt {cutoff}",
            "ListPrice lt OriginalListPrice",
        ]

        if zip_codes:
            zip_filter = " or ".join(f"PostalCode eq '{z}'" for z in zip_codes)
            filters.append(f"({zip_filter})")

        results = await self.client.get_properties(
            filter_expr=" and ".join(filters),
            select=LEAD_GEN_FIELDS,
            orderby="PriceChangeTimestamp desc",
        )

        # Client-side filter for minimum reduction percentage
        if min_reduction_pct > 0:
            filtered = []
            for r in results:
                orig = r.get("OriginalListPrice", 0)
                curr = r.get("ListPrice", 0)
                if orig and orig > 0:
                    pct = ((orig - curr) / orig) * 100
                    if pct >= min_reduction_pct:
                        r["_reduction_pct"] = round(pct, 2)
                        r["_reduction_amount"] = orig - curr
                        filtered.append(r)
            results = filtered

        return results

    async def get_stale_listings(
        self,
        min_dom: int = 90,
        zip_codes: Optional[list[str]] = None,
    ) -> list[dict]:
        """Fetch active listings with high days on market."""
        filters = [
            "StandardStatus eq 'Active'",
            f"DaysOnMarket ge {min_dom}",
        ]

        if zip_codes:
            zip_filter = " or ".join(f"PostalCode eq '{z}'" for z in zip_codes)
            filters.append(f"({zip_filter})")

        return await self.client.get_properties(
            filter_expr=" and ".join(filters),
            select=LEAD_GEN_FIELDS,
            orderby="DaysOnMarket desc",
        )

    async def get_withdrawn_relisted(self) -> list[dict]:
        """Fetch active listings where DOM was reset (CDOM > DOM)."""
        return await self.client.get_properties(
            filter_expr=(
                "StandardStatus eq 'Active'"
                " and CumulativeDaysOnMarket gt DaysOnMarket"
            ),
            select=LEAD_GEN_FIELDS,
            orderby="CumulativeDaysOnMarket desc",
        )

    async def get_recent_withdrawals(
        self,
        days_back: int = 14,
    ) -> list[dict]:
        """Fetch recently withdrawn or cancelled listings."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()

        return await self.client.get_properties(
            filter_expr=(
                "(StandardStatus eq 'Withdrawn' or StandardStatus eq 'Canceled')"
                f" and StatusChangeTimestamp gt {cutoff}"
            ),
            select=LEAD_GEN_FIELDS,
            orderby="StatusChangeTimestamp desc",
        )

    async def get_approaching_expiration(
        self,
        days_ahead: int = 30,
    ) -> list[dict]:
        """Fetch active listings expiring within N days."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        future = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        return await self.client.get_properties(
            filter_expr=(
                "StandardStatus eq 'Active'"
                f" and ExpirationDate ge {today}"
                f" and ExpirationDate le {future}"
            ),
            select=LEAD_GEN_FIELDS,
            orderby="ExpirationDate asc",
        )

    async def get_distressed_properties(self) -> list[dict]:
        """Fetch properties with distressed conditions."""
        return await self.client.get_properties(
            filter_expr=(
                "StandardStatus eq 'Active'"
                " and (contains(SpecialListingConditions, 'Short Sale')"
                " or contains(SpecialListingConditions, 'REO')"
                " or contains(SpecialListingConditions, 'Probate')"
                " or contains(SpecialListingConditions, 'Auction')"
                " or contains(SpecialListingConditions, 'Notice of Default'))"
            ),
            select=LEAD_GEN_FIELDS,
            orderby="ModificationTimestamp desc",
        )

    async def get_incremental_changes(
        self,
        since: datetime,
    ) -> list[dict]:
        """
        Fetch all properties modified since a given timestamp.
        This is the core incremental sync query.
        """
        since_str = since.isoformat()

        return await self.client.get_properties(
            filter_expr=f"ModificationTimestamp gt {since_str}",
            select=LEAD_GEN_FIELDS,
            orderby="ModificationTimestamp asc",
        )
```

### 6.4 Usage Example

```python
"""
example_usage.py - Demonstration of LeadFinder RESO integration.
"""

import asyncio
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from reso_client import RESOClient, RESOConfig
from lead_queries import LeadQueryService


async def main():
    load_dotenv()

    config = RESOConfig(
        base_url=os.getenv("MLS_BASE_URL"),
        token_url=os.getenv("MLS_TOKEN_URL"),
        client_id=os.getenv("MLS_CLIENT_ID"),
        client_secret=os.getenv("MLS_CLIENT_SECRET"),
        scope=os.getenv("MLS_SCOPE", "api"),
    )

    async with RESOClient(config) as client:
        leads = LeadQueryService(client)

        # 1. Get today's expired listings
        expired = await leads.get_expired_listings(days_back=1)
        print(f"\n--- Expired Today: {len(expired)} listings ---")
        for prop in expired[:5]:
            print(f"  {prop.get('StreetNumberNumeric', '')} {prop.get('StreetName', '')}, "
                  f"{prop.get('City', '')} {prop.get('PostalCode', '')} - "
                  f"${prop.get('ListPrice', 0):,.0f} - "
                  f"DOM: {prop.get('DaysOnMarket', 'N/A')}")

        # 2. Get recent price reductions (>5%)
        reductions = await leads.get_price_reductions(
            days_back=3,
            min_reduction_pct=5.0,
        )
        print(f"\n--- Price Reductions >5%: {len(reductions)} listings ---")
        for prop in reductions[:5]:
            orig = prop.get("OriginalListPrice", 0)
            curr = prop.get("ListPrice", 0)
            pct = prop.get("_reduction_pct", 0)
            print(f"  {prop.get('StreetNumberNumeric', '')} {prop.get('StreetName', '')} - "
                  f"${orig:,.0f} -> ${curr:,.0f} ({pct:.1f}% drop)")

        # 3. Get stale listings (90+ DOM)
        stale = await leads.get_stale_listings(min_dom=90)
        print(f"\n--- Stale Listings (90+ DOM): {len(stale)} listings ---")

        # 4. Get withdrawn/relisted
        relisted = await leads.get_withdrawn_relisted()
        print(f"\n--- Withdrawn & Relisted: {len(relisted)} listings ---")

        # 5. Approaching expiration
        expiring = await leads.get_approaching_expiration(days_ahead=14)
        print(f"\n--- Expiring in 14 Days: {len(expiring)} listings ---")

        # 6. Distressed properties
        distressed = await leads.get_distressed_properties()
        print(f"\n--- Distressed Properties: {len(distressed)} listings ---")


if __name__ == "__main__":
    asyncio.run(main())
```

### 6.5 Environment Configuration

```bash
# .env file for RESO Web API connection
# NEVER commit this file to version control

# --- MLS/RESO API ---
MLS_BASE_URL=https://api.trestle.corelogic.com/trestle/odata
MLS_TOKEN_URL=https://api.trestle.corelogic.com/trestle/oidc/connect/token
MLS_CLIENT_ID=your_client_id_here
MLS_CLIENT_SECRET=your_client_secret_here
MLS_SCOPE=api

# Platform-specific examples:
# Trestle (CoreLogic):
#   MLS_BASE_URL=https://api-prod.corelogic.com/trestle/odata
#   MLS_TOKEN_URL=https://api-prod.corelogic.com/trestle/oidc/connect/token
#
# Bridge Interactive:
#   MLS_BASE_URL=https://api.bridgedataoutput.com/api/v2/OData
#   MLS_TOKEN_URL=https://api.bridgedataoutput.com/api/v2/oauth/token
#
# Spark API (FBS):
#   MLS_BASE_URL=https://sparkapi.com/v1
#   MLS_TOKEN_URL=https://sparkapi.com/v1/oauth2/token
#   (Note: Spark uses a hybrid API, not pure OData)
#
# MLS Grid:
#   MLS_BASE_URL=https://api.mlsgrid.com/v2
#   MLS_TOKEN_URL=https://api.mlsgrid.com/v2/oauth2/token
```

---

## 7. Data Freshness & Sync Strategies

### 7.1 Incremental Sync via ModificationTimestamp

The `ModificationTimestamp` field is the backbone of efficient data synchronization. Every time any field on a listing changes (price, status, remarks, photos), this timestamp updates.

**Sync Algorithm:**

```python
"""
sync_service.py - Incremental MLS data sync service.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)


class MLSSyncService:
    """
    Manages incremental synchronization of MLS data.

    Strategy:
    1. Store the latest ModificationTimestamp from each sync run
    2. On next sync, query for all records modified after that timestamp
    3. Upsert records into local database
    4. Update the sync watermark
    """

    def __init__(self, reso_client, database):
        self.client = reso_client
        self.db = database

    async def get_last_sync_timestamp(self) -> Optional[datetime]:
        """Retrieve the last successful sync timestamp from the database."""
        result = await self.db.fetch_one(
            "SELECT MAX(value) FROM sync_metadata WHERE key = 'last_sync_timestamp'"
        )
        if result and result[0]:
            return datetime.fromisoformat(result[0])
        return None

    async def set_last_sync_timestamp(self, ts: datetime):
        """Store the sync watermark."""
        await self.db.execute(
            """INSERT OR REPLACE INTO sync_metadata (key, value)
               VALUES ('last_sync_timestamp', ?)""",
            (ts.isoformat(),)
        )

    async def run_incremental_sync(self) -> dict:
        """
        Execute an incremental sync cycle.

        Returns:
            Summary dict with counts of new, updated, and status-changed records.
        """
        last_sync = await self.get_last_sync_timestamp()

        if last_sync is None:
            # First sync ever -- pull last 30 days of data
            logger.info("No previous sync found. Running initial sync (30 days)...")
            last_sync = datetime.now(timezone.utc) - timedelta(days=30)

        logger.info("Syncing changes since %s", last_sync.isoformat())

        # Fetch all modified records since last sync
        changes = await self.client.get_properties(
            filter_expr=f"ModificationTimestamp gt {last_sync.isoformat()}",
            orderby="ModificationTimestamp asc",
        )

        stats = {"new": 0, "updated": 0, "status_changes": 0, "total": len(changes)}
        max_timestamp = last_sync

        for record in changes:
            listing_key = record.get("ListingKey")
            mod_ts = record.get("ModificationTimestamp")

            if mod_ts:
                record_ts = datetime.fromisoformat(mod_ts.replace("Z", "+00:00"))
                if record_ts > max_timestamp:
                    max_timestamp = record_ts

            # Check if record exists in our database
            existing = await self.db.fetch_one(
                "SELECT listing_key, standard_status, list_price FROM properties WHERE listing_key = ?",
                (listing_key,)
            )

            if existing is None:
                # New listing -- insert
                await self._insert_property(record)
                stats["new"] += 1
            else:
                # Existing listing -- check for important changes
                old_status = existing[1]
                new_status = record.get("StandardStatus")
                old_price = existing[2]
                new_price = record.get("ListPrice")

                # Detect status change
                if old_status != new_status:
                    stats["status_changes"] += 1
                    await self._record_status_change(
                        listing_key, old_status, new_status
                    )

                # Detect price change
                if old_price and new_price and old_price != new_price:
                    await self._record_price_change(
                        listing_key, old_price, new_price
                    )

                # Update the record
                await self._update_property(record)
                stats["updated"] += 1

        # Update the sync watermark
        await self.set_last_sync_timestamp(max_timestamp)

        logger.info(
            "Sync complete: %d total, %d new, %d updated, %d status changes",
            stats["total"], stats["new"], stats["updated"], stats["status_changes"],
        )

        return stats

    async def _insert_property(self, record: dict):
        """Insert a new property record into the local database."""
        # Implementation: map RESO fields to local schema columns
        # and execute INSERT
        pass

    async def _update_property(self, record: dict):
        """Update an existing property record."""
        # Implementation: map RESO fields and execute UPDATE
        pass

    async def _record_status_change(
        self, listing_key: str, old_status: str, new_status: str
    ):
        """
        Log a status change event for lead detection.

        Key transitions to trigger lead alerts:
        - Active -> Expired (new expired listing lead)
        - Active -> Withdrawn/Canceled (potential re-engagement lead)
        - Pending -> Active (back on market / failed contract lead)
        - Any -> Active with DOM reset (relisted lead)
        """
        logger.info(
            "Status change: %s: %s -> %s",
            listing_key, old_status, new_status,
        )
        # Insert into status_changes table for lead scoring
        pass

    async def _record_price_change(
        self, listing_key: str, old_price: float, new_price: float
    ):
        """Log a price change event."""
        change_pct = ((old_price - new_price) / old_price) * 100
        direction = "reduction" if new_price < old_price else "increase"
        logger.info(
            "Price %s: %s: $%,.0f -> $%,.0f (%.1f%%)",
            direction, listing_key, old_price, new_price, abs(change_pct),
        )
        pass
```

### 7.2 Sync Database Schema

```sql
-- Sync metadata tracking
CREATE TABLE IF NOT EXISTS sync_metadata (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL,
    updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Local property cache
CREATE TABLE IF NOT EXISTS properties (
    listing_key             TEXT PRIMARY KEY,
    listing_id              TEXT,
    standard_status         TEXT NOT NULL,
    mls_status              TEXT,
    list_price              REAL,
    original_list_price     REAL,
    previous_list_price     REAL,
    close_price             REAL,
    days_on_market          INTEGER,
    cumulative_dom          INTEGER,
    street_number           TEXT,
    street_name             TEXT,
    unit_number             TEXT,
    city                    TEXT,
    state                   TEXT,
    postal_code             TEXT,
    county                  TEXT,
    bedrooms                INTEGER,
    bathrooms               INTEGER,
    living_area             REAL,
    year_built              INTEGER,
    property_type           TEXT,
    property_subtype        TEXT,
    list_agent_name         TEXT,
    list_agent_key          TEXT,
    list_office_name        TEXT,
    listing_contract_date   DATE,
    expiration_date         DATE,
    on_market_date          DATE,
    close_date              DATE,
    status_change_ts        DATETIME,
    price_change_ts         DATETIME,
    modification_ts         DATETIME,
    special_conditions      TEXT,
    public_remarks          TEXT,
    latitude                REAL,
    longitude               REAL,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(standard_status);
CREATE INDEX IF NOT EXISTS idx_properties_postal ON properties(postal_code);
CREATE INDEX IF NOT EXISTS idx_properties_dom ON properties(days_on_market);
CREATE INDEX IF NOT EXISTS idx_properties_mod_ts ON properties(modification_ts);
CREATE INDEX IF NOT EXISTS idx_properties_status_change ON properties(status_change_ts);
CREATE INDEX IF NOT EXISTS idx_properties_price_change ON properties(price_change_ts);
CREATE INDEX IF NOT EXISTS idx_properties_expiration ON properties(expiration_date);

-- Status change log (for lead detection)
CREATE TABLE IF NOT EXISTS status_changes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_key     TEXT NOT NULL,
    old_status      TEXT,
    new_status      TEXT NOT NULL,
    changed_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_key) REFERENCES properties(listing_key)
);

CREATE INDEX IF NOT EXISTS idx_status_changes_listing ON status_changes(listing_key);
CREATE INDEX IF NOT EXISTS idx_status_changes_new ON status_changes(new_status, changed_at);

-- Price change log (for price reduction tracking)
CREATE TABLE IF NOT EXISTS price_changes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_key     TEXT NOT NULL,
    old_price       REAL,
    new_price       REAL NOT NULL,
    change_pct      REAL,
    changed_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_key) REFERENCES properties(listing_key)
);

CREATE INDEX IF NOT EXISTS idx_price_changes_listing ON price_changes(listing_key);
```

### 7.3 Polling Intervals & Scheduling

| Sync Type | Frequency | Purpose | Time Window |
|-----------|-----------|---------|-------------|
| **Full incremental sync** | Every 15-60 minutes | Catch all changes | Business hours (6 AM - 10 PM) |
| **Expired listing check** | Every 15 minutes, 12 AM - 2 AM | First to catch midnight expirations | Late night/early morning |
| **Price reduction scan** | Every 30 minutes | Catch fresh price drops | Business hours |
| **Status change detection** | Every 15 minutes | Catch withdrawals, back-on-market | Business hours |
| **Full resync** | Weekly (Sunday night) | Catch any missed changes, data integrity | Off-peak |

```python
"""
scheduler.py - Sync scheduling configuration.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


def configure_scheduler(sync_service) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    # Primary incremental sync - every 30 minutes during business hours
    scheduler.add_job(
        sync_service.run_incremental_sync,
        IntervalTrigger(minutes=30),
        id="incremental_sync",
        name="MLS Incremental Sync",
        max_instances=1,  # Prevent overlapping runs
    )

    # Expired listing priority check - every 15 min from midnight to 2 AM
    # (Many MLS boards process expirations at midnight)
    scheduler.add_job(
        sync_service.check_new_expirations,
        CronTrigger(hour="0-1", minute="*/15"),
        id="expiration_check",
        name="Expired Listing Priority Check",
        max_instances=1,
    )

    # Weekly full resync - Sunday at 2 AM
    scheduler.add_job(
        sync_service.run_full_resync,
        CronTrigger(day_of_week="sun", hour=2, minute=0),
        id="weekly_resync",
        name="Weekly Full Resync",
        max_instances=1,
    )

    return scheduler
```

### 7.4 Webhook Availability

Webhooks for real-time push notifications are still uncommon in the MLS ecosystem, but growing:

| Platform | Webhook Support | Status |
|----------|----------------|--------|
| **Trestle** | Limited -- via custom notification setup | Available for some boards |
| **Bridge Interactive** | Webhooks available | Supported, requires setup |
| **Spark API** | No native webhooks | Poll-based only |
| **MLS Grid** | Webhooks available | Supported in API v2 |
| **Most MLS boards** | No native webhooks | Poll via ModificationTimestamp |

**Recommendation**: Do not depend on webhooks for initial implementation. Build the polling-based sync first, then add webhook listeners as an optimization if your MLS platform supports them.

### 7.5 Handling Deletes

Deleted listings are one of the trickiest aspects of MLS data synchronization. When a listing is removed from the MLS entirely (not just status-changed to "Deleted" -- actually removed from the API), it simply disappears from query results.

**Strategies for detecting deletes:**

1. **Replication endpoint** (if available): Some RESO implementations provide a dedicated replication endpoint that includes tombstone records (records with only the key and a deletion timestamp).

2. **StandardStatus = 'Delete'**: Some MLS boards set the status to "Delete" rather than physically removing the record. Query for this status periodically.

3. **Periodic reconciliation**: Periodically query all active ListingKeys from the API and compare against your local database. Records in your database but not in the API have been deleted.

```python
async def reconcile_deletes(self, batch_size: int = 5000):
    """
    Detect locally stored records that have been deleted from the MLS.
    Run weekly during off-peak hours.
    """
    # Get all listing keys from local database
    local_keys = set(await self.db.fetch_column(
        "SELECT listing_key FROM properties WHERE standard_status NOT IN ('Closed', 'Delete')"
    ))

    # Get all listing keys from MLS (paginated)
    remote_keys = set()
    records = await self.client.get_properties(
        filter_expr="StandardStatus ne 'Closed'",
        select=["ListingKey"],
        max_records=None,  # Get all
    )
    for r in records:
        remote_keys.add(r["ListingKey"])

    # Find keys that exist locally but not remotely
    deleted_keys = local_keys - remote_keys

    if deleted_keys:
        logger.info("Found %d deleted listings", len(deleted_keys))
        for key in deleted_keys:
            await self.db.execute(
                "UPDATE properties SET standard_status = 'Delete', updated_at = CURRENT_TIMESTAMP WHERE listing_key = ?",
                (key,)
            )
```

---

## 8. MLS-Specific Variations

### 8.1 Overview of Major MLS Data Platforms

While the RESO Web API standardizes the interface, real-world implementations vary significantly. Here are the major platforms and their characteristics:

### 8.2 Trestle (CoreLogic)

**Coverage**: 600+ MLS organizations, largest data platform in the US.

| Aspect | Details |
|--------|---------|
| **API Standard** | RESO Web API 2.0 (OData v4) |
| **Base URL Pattern** | `https://api-prod.corelogic.com/trestle/odata` |
| **Token URL** | `https://api-prod.corelogic.com/trestle/oidc/connect/token` |
| **Auth** | OAuth 2.0 client credentials |
| **Page Size** | 200 records max (default 100) |
| **Rate Limits** | ~1,200 requests/hour |
| **Unique Features** | Good RESO DD compliance, reliable uptime |
| **Quirks** | Some local fields use `x_` prefix (extensions), token endpoint path can vary by board |

### 8.3 Bridge Interactive (Zillow Group)

**Coverage**: 300+ MLS organizations, strong documentation and developer experience.

| Aspect | Details |
|--------|---------|
| **API Standard** | RESO Web API 2.0 (with some Bridge-specific extensions) |
| **Base URL Pattern** | `https://api.bridgedataoutput.com/api/v2/OData/{dataset}` |
| **Token URL** | `https://api.bridgedataoutput.com/api/v2/oauth/token` |
| **Auth** | OAuth 2.0 client credentials |
| **Page Size** | 200 records max |
| **Rate Limits** | ~2,000 requests/hour |
| **Unique Features** | Excellent documentation, dataset-specific endpoints, strong support |
| **Quirks** | Requires dataset ID in URL path, some non-standard field mappings |

### 8.4 Spark API (FBS / FlexMLS)

**Coverage**: 200+ MLS organizations using the FlexMLS platform.

| Aspect | Details |
|--------|---------|
| **API Standard** | Hybrid -- partially RESO Web API, partially custom Spark API |
| **Base URL Pattern** | `https://sparkapi.com/v1` or MLS-specific subdomain |
| **Auth** | API key + OAuth 2.0 hybrid |
| **Page Size** | Up to 1,000 records |
| **Rate Limits** | ~500 requests/hour |
| **Unique Features** | Larger page sizes, robust search, saved search support |
| **Quirks** | Not pure OData -- uses some custom query syntax, field names may not match RESO DD exactly |

### 8.5 MLS Grid

**Coverage**: 100+ MLS organizations, newer platform focused on data standardization.

| Aspect | Details |
|--------|---------|
| **API Standard** | RESO Web API 2.0 (strong compliance) |
| **Base URL Pattern** | `https://api.mlsgrid.com/v2` |
| **Token URL** | `https://api.mlsgrid.com/v2/oauth2/token` |
| **Auth** | OAuth 2.0 client credentials |
| **Page Size** | 200 records max |
| **Rate Limits** | ~1,000 requests/hour |
| **Unique Features** | Replication API (efficient bulk sync), strong RESO DD compliance |
| **Quirks** | Newer platform, growing coverage |

### 8.6 Bright MLS

**Coverage**: Mid-Atlantic region (DC, MD, VA, PA, NJ, DE, WV) -- one of the largest single MLSs.

| Aspect | Details |
|--------|---------|
| **API Standard** | RESO Web API 2.0 via Trestle |
| **Coverage** | ~100,000+ active listings across the Mid-Atlantic |
| **Access** | Through Bright MLS membership, request API credentials from their tech team |
| **Unique Features** | Extensive historical data, comprehensive showing data |
| **Quirks** | Large dataset -- pagination management is critical |

### 8.7 California Regional MLS (CRMLS)

**Coverage**: Southern California -- the largest MLS in the US by listings.

| Aspect | Details |
|--------|---------|
| **API Standard** | RESO Web API 2.0 |
| **Coverage** | ~130,000+ active listings |
| **Access** | Through CRMLS membership |
| **Unique Features** | Massive dataset, strong RESO compliance |
| **Quirks** | Very large result sets, aggressive rate limiting, field extensions for CA-specific disclosures |

### 8.8 Stellar MLS

**Coverage**: Florida (Central and parts of South Florida).

| Aspect | Details |
|--------|---------|
| **API Standard** | RESO Web API 2.0 |
| **Coverage** | ~80,000+ active listings |
| **Access** | Through Stellar MLS membership |
| **Unique Features** | Strong Florida-specific fields (flood zone, HOA, etc.) |
| **Quirks** | Florida-specific listing conditions, hurricane shutters as a searchable field |

### 8.9 Handling Variations in Code

```python
"""
platform_adapters.py - Platform-specific configuration adapters.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PlatformConfig:
    """Platform-specific API configuration."""
    name: str
    base_url: str
    token_url: str
    page_size: int = 200
    rate_limit_per_hour: int = 1000

    # Field name overrides (if MLS uses non-standard names)
    field_map: dict = None  # {"StandardFieldName": "LocalFieldName"}

    # OData quirks
    supports_geo_distance: bool = False
    supports_contains_on_collections: bool = True
    requires_dataset_id: bool = False
    dataset_id: Optional[str] = None

    def __post_init__(self):
        if self.field_map is None:
            self.field_map = {}


# Pre-configured platform profiles
PLATFORM_PROFILES = {
    "trestle": PlatformConfig(
        name="Trestle (CoreLogic)",
        base_url="https://api-prod.corelogic.com/trestle/odata",
        token_url="https://api-prod.corelogic.com/trestle/oidc/connect/token",
        page_size=200,
        rate_limit_per_hour=1200,
        supports_geo_distance=False,
    ),
    "bridge": PlatformConfig(
        name="Bridge Interactive",
        base_url="https://api.bridgedataoutput.com/api/v2/OData",
        token_url="https://api.bridgedataoutput.com/api/v2/oauth/token",
        page_size=200,
        rate_limit_per_hour=2000,
        requires_dataset_id=True,
    ),
    "spark": PlatformConfig(
        name="Spark API (FBS)",
        base_url="https://sparkapi.com/v1",
        token_url="https://sparkapi.com/v1/oauth2/token",
        page_size=1000,
        rate_limit_per_hour=500,
        # Spark uses some non-standard field names
        field_map={
            "StandardStatus": "MlsStatus",
            "StatusChangeTimestamp": "StatusChangeDate",
        },
    ),
    "mlsgrid": PlatformConfig(
        name="MLS Grid",
        base_url="https://api.mlsgrid.com/v2",
        token_url="https://api.mlsgrid.com/v2/oauth2/token",
        page_size=200,
        rate_limit_per_hour=1000,
    ),
}


class FieldMapper:
    """
    Maps standard RESO DD field names to platform-specific names.

    When writing queries, always use standard RESO DD names.
    This mapper translates them for the specific MLS platform.
    """

    def __init__(self, platform: PlatformConfig):
        self.field_map = platform.field_map or {}
        # Reverse map for response parsing
        self.reverse_map = {v: k for k, v in self.field_map.items()}

    def to_platform(self, field_name: str) -> str:
        """Convert standard RESO field name to platform-specific name."""
        return self.field_map.get(field_name, field_name)

    def to_standard(self, field_name: str) -> str:
        """Convert platform-specific field name to standard RESO name."""
        return self.reverse_map.get(field_name, field_name)

    def translate_filter(self, filter_expr: str) -> str:
        """Replace standard field names in an OData filter expression."""
        result = filter_expr
        for standard, platform in self.field_map.items():
            result = result.replace(standard, platform)
        return result

    def translate_select(self, fields: list[str]) -> list[str]:
        """Replace standard field names in a $select list."""
        return [self.to_platform(f) for f in fields]

    def normalize_record(self, record: dict) -> dict:
        """Convert platform-specific field names in a record to standard RESO names."""
        normalized = {}
        for key, value in record.items():
            standard_key = self.to_standard(key)
            normalized[standard_key] = value
        return normalized
```

---

## 9. Compliance Requirements

### 9.1 MLS Data Usage Rules

MLS data comes with strict usage restrictions enforced by the local MLS board, NAR, and state/local regulations. Violating these rules can result in fines, license suspension, or loss of MLS access.

**Core Principles:**
- MLS data is licensed, not owned -- you are granted access, not ownership
- Data can only be used in connection with the licensed Realtor's business
- Data cannot be resold, sublicensed, or shared with unauthorized parties
- All access must be under the member's credentials (wife's MLS membership)

### 9.2 IDX vs. VOW vs. Internal Use

There are three main categories of MLS data usage, each with different rules:

| Category | Full Name | Use Case | Display Rules | Our Category |
|----------|-----------|----------|---------------|-------------|
| **IDX** | Internet Data Exchange | Public-facing property search websites | Extensive rules on display, attribution, updates | Not applicable for LeadFinder |
| **VOW** | Virtual Office Website | Client-only portal (behind login) | More flexible, requires registration/login | Possible future feature |
| **Internal Use** | Back-office / Private | Agent's own business analysis tools | Most flexible -- minimal display rules | **This is LeadFinder** |

**LeadFinder falls under "Internal Use"** -- it is a private business intelligence tool for a licensed Realtor. This is the most permissive category because the data is not being displayed publicly.

### 9.3 Internal Use Compliance Checklist

For internal/private business tools like LeadFinder:

| Requirement | Status | Notes |
|-------------|--------|-------|
| Licensed Realtor is the authorized user | Required | Wife's MLS membership |
| Data used only for licensed real estate business | Required | Lead generation for her practice |
| No public display of MLS data | Required | Dashboard is private, login-protected |
| No data resale or sharing with unauthorized parties | Required | Data stays within our system |
| Data accuracy maintained (synced regularly) | Required | Incremental sync keeps data current |
| Data retention limits respected | Required | Follow board-specific retention rules |
| API credentials secured | Required | .env file, never in code or version control |
| Data license agreement signed | Required | Through MLS board |
| Proper attribution where required | Varies | Some boards require MLS attribution even internally |

### 9.4 Data Retention Limits

Most MLS boards impose data retention rules:

| Data Type | Typical Retention Rule | Action Required |
|-----------|----------------------|-----------------|
| Active listings | Keep current while active | Sync regularly, mark inactive when status changes |
| Sold listings | 12-36 months after close | Delete or archive after retention period |
| Expired/Withdrawn | 6-12 months after status change | Delete or archive after retention period |
| Deleted listings | Remove within 24-48 hours | Delete promptly when detected |
| Agent/Member data | Keep current only | Update on sync, no historical retention |
| Property photos | Remove when listing is no longer active | Delete media when listing leaves active status |

**Implementation**: Build a data retention job that runs weekly:

```python
async def enforce_data_retention(self):
    """Delete records that exceed retention limits."""
    # Delete properties that have been closed for more than 12 months
    await self.db.execute("""
        DELETE FROM properties
        WHERE standard_status = 'Closed'
          AND close_date < date('now', '-12 months')
    """)

    # Delete expired/withdrawn listings older than 6 months
    await self.db.execute("""
        DELETE FROM properties
        WHERE standard_status IN ('Expired', 'Withdrawn', 'Canceled', 'Delete')
          AND status_change_ts < datetime('now', '-6 months')
    """)

    # Clean up orphaned records in related tables
    await self.db.execute("""
        DELETE FROM status_changes
        WHERE listing_key NOT IN (SELECT listing_key FROM properties)
    """)
    await self.db.execute("""
        DELETE FROM price_changes
        WHERE listing_key NOT IN (SELECT listing_key FROM properties)
    """)
```

### 9.5 What Can and Cannot Be Stored Locally

| Data Element | Can Store? | Notes |
|-------------|-----------|-------|
| Listing data (price, address, status, DOM) | Yes | Core data for lead gen, subject to retention limits |
| Agent contact info (name, email, phone) | Yes (limited) | For professional context only, not for marketing to agents |
| Property photos | With restrictions | Many boards prohibit local storage of photos; use URL references instead |
| Public remarks | Yes | For lead analysis only, not for public display |
| Private remarks | Depends on board | Some boards restrict storage of agent-only remarks |
| Sold/closed data | Yes (time-limited) | For comp analysis; respect retention limits |
| Historical price changes | Yes | Derived from your sync -- you are tracking changes over time |
| Owner contact info | Not from MLS | MLS does not typically include owner contact; get from skip tracing |

### 9.6 Important Legal Considerations

1. **MLS Terms of Service**: Always read your specific MLS board's terms. They vary. Some are more restrictive than others.

2. **NAR Policies**: NAR's MLS policy statements establish minimum standards, but local boards can (and do) add additional restrictions.

3. **State Real Estate Commission Rules**: Some states have additional rules about data usage, advertising, and solicitation that apply to MLS data.

4. **Fair Housing**: All outreach based on MLS data must comply with the Fair Housing Act. Never target or exclude based on race, color, religion, sex, familial status, national origin, or disability.

5. **Anti-Solicitation Laws**: Some states restrict solicitation of homeowners in certain circumstances (e.g., recently bereaved, disaster areas, foreclosure timing restrictions). Check Arizona-specific rules.

6. **Do Not Call**: If using MLS data to identify leads and then contacting them by phone, comply with federal and state Do Not Call regulations.

---

## 10. Fallback Approaches

### 10.1 If RESO Web API Is Not Available

Not every MLS board has a well-functioning RESO Web API. Some smaller boards lag in implementation, and credential approval can be delayed. Here are fallback strategies, ranked by preference:

### 10.2 Fallback 1: RETS Legacy Access

If your MLS board still offers RETS alongside or instead of the RESO Web API:

| Aspect | RETS Approach |
|--------|---------------|
| **Protocol** | XML-based, uses DMQL2 query language |
| **Authentication** | HTTP Digest Auth |
| **Python Library** | `librets` (C++ with Python bindings) or `rets-python` |
| **Pros** | Widely available, well-understood, mature tooling |
| **Cons** | Deprecated, complex XML parsing, less efficient |
| **When to use** | Board does not yet offer RESO Web API |

```python
# Example RETS query (using a hypothetical Python RETS client)
# Note: RETS uses DMQL2, not OData
#
# DMQL2 equivalent of: StandardStatus eq 'Expired' and ModificationTimestamp gt 2026-02-21
# Query: (Status=|EXP),(ModificationTimestamp=2026-02-21T00:00:00+)
#
# This is NOT recommended for new development -- use RESO Web API if at all possible.
```

### 10.3 Fallback 2: MLS Portal Saved Search Exports (CSV)

This is the simplest fallback and requires zero API access:

**How it works:**
1. Wife logs into the MLS portal (e.g., FlexMLS, Matrix, Paragon)
2. Creates saved searches for each lead category (expired, price reductions, etc.)
3. Exports results as CSV on a regular schedule (daily)
4. LeadFinder imports and processes the CSV files

**Advantages:**
- Zero setup cost or API credentials needed
- Works with any MLS board
- Good starting point before API access is approved
- Wife already knows how to use the MLS portal

**Disadvantages:**
- Manual process (must export and upload daily)
- Not real-time -- at best, daily data
- Limited fields in export (portal may not export all fields)
- No incremental sync -- full export each time

**Implementation:**

```python
"""
csv_importer.py - Import MLS data from CSV exports.
"""

import csv
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


# Map common MLS portal CSV column headers to standard RESO field names.
# This varies by MLS portal.  Adjust for your specific MLS export format.
CSV_FIELD_MAP = {
    # FlexMLS / Spark exports
    "MLS #": "ListingId",
    "MLS Number": "ListingId",
    "Status": "StandardStatus",
    "List Price": "ListPrice",
    "Original List Price": "OriginalListPrice",
    "DOM": "DaysOnMarket",
    "CDOM": "CumulativeDaysOnMarket",
    "Address": "FullStreetAddress",
    "City": "City",
    "State": "StateOrProvince",
    "Zip": "PostalCode",
    "Zip Code": "PostalCode",
    "Beds": "BedroomsTotal",
    "Baths": "BathroomsTotalInteger",
    "Sq Ft": "LivingArea",
    "Year Built": "YearBuilt",
    "List Agent": "ListAgentFullName",
    "List Office": "ListOfficeName",
    "Listing Date": "ListingContractDate",
    "Expiration Date": "ExpirationDate",
    "Status Date": "StatusChangeTimestamp",
    "Remarks": "PublicRemarks",

    # Matrix exports (slightly different headers)
    "List #": "ListingId",
    "Listing Price": "ListPrice",
    "Days on Market": "DaysOnMarket",
    "Street Address": "FullStreetAddress",
    "Bedrooms": "BedroomsTotal",
    "Bathrooms": "BathroomsTotalInteger",
    "SqFt": "LivingArea",
    "Listing Agent": "ListAgentFullName",
    "Listing Office": "ListOfficeName",
}

# Status value normalization (MLS portals use different status labels)
STATUS_MAP = {
    "A": "Active",
    "ACT": "Active",
    "Active": "Active",
    "P": "Pending",
    "PND": "Pending",
    "Pending": "Pending",
    "S": "Closed",
    "SLD": "Closed",
    "Sold": "Closed",
    "Closed": "Closed",
    "E": "Expired",
    "EXP": "Expired",
    "Expired": "Expired",
    "W": "Withdrawn",
    "WDN": "Withdrawn",
    "Withdrawn": "Withdrawn",
    "C": "Canceled",
    "CAN": "Canceled",
    "Cancelled": "Canceled",
    "Canceled": "Canceled",
}


class CSVImporter:
    """Import MLS data from CSV exports."""

    def __init__(self, database):
        self.db = database

    async def import_file(self, file_path: Path) -> dict:
        """
        Import a CSV file of MLS data.

        Returns:
            Summary dict with import statistics.
        """
        stats = {"total": 0, "imported": 0, "skipped": 0, "errors": 0}

        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                stats["total"] += 1
                try:
                    # Normalize field names
                    normalized = {}
                    for csv_col, value in row.items():
                        csv_col_clean = csv_col.strip()
                        reso_field = CSV_FIELD_MAP.get(csv_col_clean, csv_col_clean)
                        normalized[reso_field] = value.strip() if value else None

                    # Normalize status
                    raw_status = normalized.get("StandardStatus", "")
                    normalized["StandardStatus"] = STATUS_MAP.get(raw_status, raw_status)

                    # Clean price fields (remove $, commas)
                    for price_field in ["ListPrice", "OriginalListPrice", "ClosePrice"]:
                        if normalized.get(price_field):
                            cleaned = normalized[price_field].replace("$", "").replace(",", "").strip()
                            try:
                                normalized[price_field] = float(cleaned) if cleaned else None
                            except ValueError:
                                normalized[price_field] = None

                    # Clean numeric fields
                    for int_field in ["DaysOnMarket", "CumulativeDaysOnMarket", "BedroomsTotal",
                                     "BathroomsTotalInteger", "YearBuilt"]:
                        if normalized.get(int_field):
                            try:
                                normalized[int_field] = int(float(normalized[int_field]))
                            except (ValueError, TypeError):
                                normalized[int_field] = None

                    if normalized.get("LivingArea"):
                        try:
                            cleaned = normalized["LivingArea"].replace(",", "").strip()
                            normalized["LivingArea"] = float(cleaned) if cleaned else None
                        except (ValueError, TypeError):
                            normalized["LivingArea"] = None

                    # Upsert into database
                    await self._upsert_property(normalized)
                    stats["imported"] += 1

                except Exception as e:
                    logger.error("Error importing row %d: %s", stats["total"], e)
                    stats["errors"] += 1

        logger.info(
            "CSV import complete: %d total, %d imported, %d skipped, %d errors",
            stats["total"], stats["imported"], stats["skipped"], stats["errors"],
        )
        return stats

    async def _upsert_property(self, record: dict):
        """Insert or update a property record from CSV data."""
        listing_id = record.get("ListingId")
        if not listing_id:
            return

        # Use ListingId as the key for CSV imports (since we do not have ListingKey)
        existing = await self.db.fetch_one(
            "SELECT listing_id FROM properties WHERE listing_id = ?",
            (listing_id,)
        )

        if existing:
            # Update existing record
            await self.db.execute("""
                UPDATE properties SET
                    standard_status = ?,
                    list_price = ?,
                    original_list_price = ?,
                    days_on_market = ?,
                    cumulative_dom = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE listing_id = ?
            """, (
                record.get("StandardStatus"),
                record.get("ListPrice"),
                record.get("OriginalListPrice"),
                record.get("DaysOnMarket"),
                record.get("CumulativeDaysOnMarket"),
                listing_id,
            ))
        else:
            # Insert new record
            # (Simplified -- full implementation maps all fields)
            await self.db.execute("""
                INSERT INTO properties (
                    listing_key, listing_id, standard_status, list_price,
                    original_list_price, days_on_market, cumulative_dom,
                    city, state, postal_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                listing_id,  # Use listing_id as listing_key for CSV imports
                listing_id,
                record.get("StandardStatus"),
                record.get("ListPrice"),
                record.get("OriginalListPrice"),
                record.get("DaysOnMarket"),
                record.get("CumulativeDaysOnMarket"),
                record.get("City"),
                record.get("StateOrProvince"),
                record.get("PostalCode"),
            ))
```

### 10.4 Fallback 3: Third-Party Data Feeds

If direct MLS API access is delayed or limited, third-party services provide pre-processed lead data:

| Service | Data Type | Monthly Cost | API? | Best For |
|---------|-----------|-------------|------|----------|
| **REDX** | Expired, FSBO, pre-foreclosure, GeoLeads | $60-$200 | No (portal + downloads) | Expired/FSBO leads with phone numbers |
| **Vulcan7** | Expired, FSBO, neighborhood | $250-$350 | No (portal) | Similar to REDX, strong phone data |
| **Bridge Interactive (Data Feeds)** | Full MLS data | Varies (via MLS) | Yes (RESO Web API) | If your MLS uses Bridge as platform |
| **BatchLeads** | Skip trace, property data | $50-$150 | Yes (REST API) | Enrichment (owner info, phone, email) |
| **PropStream** | MLS + public records | $100 | Limited API | All-in-one data with filtering |
| **ATTOM Data** | Public records, AVM, foreclosure | $250-$500 | Yes (REST API) | Deep public records data |
| **PropertyRadar** | Public records, pre-foreclosure | $100 | Yes (REST API) | Western US markets |

**Integration with LeadFinder**: These services can supplement MLS data. For example, use MLS data (via API or CSV) for listing intelligence, and use ATTOM or BatchLeads for owner contact information and public records enrichment.

### 10.5 Fallback 4: Manual MLS Portal Workflow

If neither API access nor CSV exports are practical initially, a structured manual workflow:

**Daily Manual Routine (15-20 minutes):**

1. **Log into MLS portal** (8:00 AM)
2. **Check expired listings** -- run saved search for "Expired in last 24 hours"
3. **Check price reductions** -- run saved search for "Price changed in last 24 hours, reduced"
4. **Check DOM threshold** -- run saved search for "Active, DOM > 90 days"
5. **Manually enter high-priority leads** into LeadFinder dashboard
6. **Weekly**: Check withdrawn/cancelled, approaching expirations

This manual workflow is the Phase 0 approach described in the existing automation_integrations.md. It requires zero technical setup and can start immediately.

### 10.6 Migration Path: Manual to Automated

```
Phase 0 (Week 1)         Phase 1 (Weeks 2-4)        Phase 2 (Month 2-3)
┌─────────────────┐      ┌──────────────────┐       ┌───────────────────┐
│ Manual MLS      │      │ CSV Export +     │       │ RESO Web API      │
│ portal searches │ ---> │ CSV Importer     │ ----> │ Full automated    │
│ + manual entry  │      │ + LeadFinder     │       │ sync + scoring    │
│                 │      │ dashboard        │       │ + alerts          │
└─────────────────┘      └──────────────────┘       └───────────────────┘

Effort:  15 min/day       5 min/day (export)         0 min/day (automated)
Data:    Partial           Good                       Complete + real-time
Leads:   Manual tracking   Dashboard tracking         Full pipeline
```

### 10.7 What NOT to Do: MLS Portal Scraping

**Do not scrape the MLS web portal.** This is explicitly prohibited in every MLS board's terms of service and can result in:

- Immediate termination of MLS membership
- License suspension or revocation
- Legal action from the MLS board
- NAR ethics complaints
- Loss of all data access

Web scraping (using Selenium, Playwright, Puppeteer, or similar tools against the MLS member portal) is not a legitimate fallback. Even if technically possible, it violates the terms of service that come with MLS membership. The approaches above (API, CSV export, third-party feeds) are all legitimate alternatives.

---

## Appendix A: Quick Reference Card

### Essential OData Filter Patterns

```
# Expired in last N days
StandardStatus eq 'Expired' and StatusChangeTimestamp gt {iso_timestamp}

# Active with price reduction
StandardStatus eq 'Active' and ListPrice lt OriginalListPrice

# High DOM
StandardStatus eq 'Active' and DaysOnMarket ge {threshold}

# Withdrawn/relisted (DOM reset)
StandardStatus eq 'Active' and CumulativeDaysOnMarket gt DaysOnMarket

# Recent withdrawals
(StandardStatus eq 'Withdrawn' or StandardStatus eq 'Canceled') and StatusChangeTimestamp gt {iso_timestamp}

# Approaching expiration
StandardStatus eq 'Active' and ExpirationDate ge {today} and ExpirationDate le {future_date}

# Distressed properties
StandardStatus eq 'Active' and contains(SpecialListingConditions, 'Short Sale')

# Incremental sync (all changes since last sync)
ModificationTimestamp gt {last_sync_timestamp}

# ZIP code filter (combine with any above)
and PostalCode eq '{zip_code}'

# Price range filter (combine with any above)
and ListPrice ge {min_price} and ListPrice le {max_price}

# Property type filter
and PropertyType eq 'Residential'
```

### Authentication Quick Start

```python
import httpx, os, time
from dotenv import load_dotenv

load_dotenv()

# 1. Get token
token_resp = httpx.post(os.getenv("MLS_TOKEN_URL"), data={
    "grant_type": "client_credentials",
    "client_id": os.getenv("MLS_CLIENT_ID"),
    "client_secret": os.getenv("MLS_CLIENT_SECRET"),
    "scope": os.getenv("MLS_SCOPE", "api"),
})
token = token_resp.json()["access_token"]

# 2. Query
resp = httpx.get(
    f"{os.getenv('MLS_BASE_URL')}/Property",
    params={"$filter": "StandardStatus eq 'Expired'", "$top": "10"},
    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
)
listings = resp.json().get("value", [])
```

### Python Requirements

```
# requirements.txt (RESO integration dependencies)
httpx>=0.27.0
pydantic>=2.0
tenacity>=8.2
python-dotenv>=1.0
apscheduler>=3.10
aiosqlite>=0.19
arrow>=1.3
```

---

## Appendix B: Metadata Discovery

Before writing queries, explore the MLS's metadata to understand what fields and resources are available:

```python
async def explore_metadata(client: RESOClient):
    """
    Fetch and examine the OData metadata document.

    The $metadata endpoint returns a CSDL (Common Schema Definition Language)
    document describing all available resources, fields, and their types.
    """
    metadata_xml = await client.get_metadata()

    # Parse with xml.etree.ElementTree
    import xml.etree.ElementTree as ET
    root = ET.fromstring(metadata_xml)

    # Namespace for OData CSDL
    ns = {"edmx": "http://docs.oasis-open.org/odata/ns/edmx",
          "edm": "http://docs.oasis-open.org/odata/ns/edm"}

    # List all entity types (resources)
    for entity_type in root.findall(".//edm:EntityType", ns):
        name = entity_type.get("Name")
        properties = entity_type.findall("edm:Property", ns)
        print(f"\nResource: {name} ({len(properties)} fields)")
        for prop in properties[:10]:  # Show first 10 fields
            print(f"  {prop.get('Name')}: {prop.get('Type')}")
```

**Why this matters**: Not every MLS implements every RESO DD field. The metadata document tells you exactly what is available on your specific MLS board's API. Run this once during initial setup and again periodically (monthly) to discover newly added fields.

---

## Appendix C: Error Handling Reference

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Process response |
| 204 | No content (empty result) | Valid -- zero records match |
| 400 | Bad request (malformed query) | Fix OData syntax |
| 401 | Unauthorized (token expired/invalid) | Refresh token and retry |
| 403 | Forbidden (insufficient permissions) | Check credentials/scope with MLS board |
| 404 | Not found (invalid endpoint/key) | Check URL and resource name |
| 429 | Too many requests (rate limited) | Wait `Retry-After` seconds, then retry |
| 500 | Server error (MLS platform issue) | Retry with exponential backoff |
| 502/503 | Service unavailable | Retry after delay; platform may be in maintenance |

---

*This document provides the complete technical foundation for integrating LeadFinder with MLS data via the RESO Web API. Start with Section 3 (getting access), use the Python client in Section 6 for implementation, and follow the sync strategies in Section 7 for ongoing operation. If API access is delayed, Section 10 provides immediate alternatives to begin generating leads.*
