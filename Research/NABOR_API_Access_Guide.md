# NABOR MLS API Access Guide

**Date**: 2026-03-03
**Purpose**: Comprehensive guide to obtaining programmatic API access to SWFLA MLS through NABOR
**Status**: Research complete — ready for action

---

## Executive Summary

The Realtor is a licensed member of **NABOR (Naples Area Board of REALTORS)** with access to **SWFLA MLS (Southwest Florida MLS)**. The goal is to obtain API credentials to replace manual CSV exports with automated data pulls for TheLeadEdge lead generation system.

**Bottom line**: The primary path is **CoreLogic Trestle** (RESO Web API). NABOR runs on CoreLogic Matrix and distributes data through Trestle. Bridge Interactive is a secondary option, primarily relevant for Bonita Springs-Estero data.

**Estimated cost**: ~$500 first year, ~$250/year after
**Estimated timeline**: 1-3 weeks from application to credentials
**License type needed**: Back Office Feed (internal analytics, not public display)

---

## The Two API Platforms

### Option 1: CoreLogic Trestle (RECOMMENDED — Primary Path)

| Attribute | Detail |
|-----------|--------|
| **What it is** | CoreLogic's RESO Web API data distribution platform |
| **Why it's primary** | NABOR runs on CoreLogic Matrix — Trestle is the native API layer |
| **RESO Certification** | Platinum Certified, DD 2.0 vendor certified |
| **Protocol** | RESO Web API (OData v4, RESTful JSON) |
| **Authentication** | OAuth 2.0 Client Credentials |
| **Token endpoint** | `https://api.cotality.com/trestle/oidc/connect/token` |
| **Base URL** | `https://api.cotality.com/trestle/odata/` |
| **Token lifetime** | 8 hours |
| **Rate limits** | 7,200 requests/hour, 180/minute |
| **Page size** | 200 records max |
| **Data freshness** | 5 minutes for listings, 15 minutes for images |
| **Coverage** | 600+ MLS organizations nationwide |
| **Support** | trestlesupport@cotality.com + Slack channel |
| **Documentation** | https://trestle-documentation.corelogic.com/ |
| **Registration** | https://trestle.corelogic.com/SubscriptionWizard |

**Why Trestle wins for NABOR**:
- Same vendor ecosystem (Matrix + Trestle = CoreLogic)
- Fastest data freshness (5-minute latency)
- Highest rate limits among providers
- Direct MLS support path
- Both RPCRA/FGCMLS (Fort Myers/Cape Coral) and NABOR (Naples) use Trestle

### Option 2: Bridge Interactive (Secondary — Bonita Springs-Estero)

| Attribute | Detail |
|-----------|--------|
| **What it is** | Zillow Group's data distribution platform |
| **Why it exists on portal** | Bonita Springs-Estero (BER) distributes IDX data via Bridge |
| **RESO Certification** | Platinum Certified |
| **Protocol** | RESO Web API (OData v4) |
| **Authentication** | OAuth 2.0 + Server Token |
| **Base URL** | `https://api.bridgedataoutput.com/api/v2/OData/{dataset}` |
| **Rate limits** | ~2,000 requests/hour |
| **Page size** | 200 records max |
| **Cost** | No fees from Bridge — only MLS licensing costs |
| **Support** | BridgeAPI@bridgeinteractive.com |
| **Documentation** | https://bridgedataoutput.com/docs/platform/ |

**When Bridge matters**: Only if you specifically need Bonita Springs-Estero data through a separate feed. Since SWFLA MLS is a unified system, Trestle likely covers all listings.

### Platform Comparison

| Factor | Trestle | Bridge |
|--------|---------|--------|
| NABOR relationship | Native (same vendor) | Third-party |
| Data freshness | 5-minute latency | ~10-minute latency |
| Rate limits | 7,200/hour | ~2,000/hour |
| Token lifetime | 8 hours | ~1 hour |
| Additional fees | Possible (~$15/month) | None from Bridge |
| RESO certification | Platinum + DD 2.0 | Platinum |
| SWFLA MLS coverage | NABOR + RPCRA/FGCMLS | BER (Bonita Springs-Estero) |

---

## SWFLA MLS Ecosystem Map

The Southwest Florida MLS is a **merged system** with a unified front-end (Matrix at `matrix.swflamls.com`) but **split data distribution**:

| Association | Coverage Area | MLS Platform | API Provider |
|-------------|--------------|-------------|--------------|
| **NABOR** | Naples, Collier County | CoreLogic Matrix | **Trestle** |
| **RPCRA/FGCMLS** | Fort Myers, Cape Coral, Lee County | CoreLogic Matrix | **Trestle** |
| **BER/BEAR** | Bonita Springs, Estero | Part of SWFLA MLS | **Bridge** |

**Key portal systems**:
- Member portal (SSO): `mdweb.mmsi2.com` (Relevate AMS, formerly MMSI)
- MLS search: `matrix.swflamls.com` (CoreLogic Matrix)
- API gateway: CoreLogic Trestle

---

## Available Data Resources

The RESO Web API provides access to these standard resources:

| Resource | Description | Lead Gen Value |
|----------|-------------|---------------|
| **Property** | All listing data | CRITICAL — core of all lead queries |
| **Member** | Agent/broker info | HIGH — agent pattern tracking |
| **Office** | Brokerage data | MEDIUM — market share analysis |
| **Media** | Photos/virtual tours | LOW — future CMA use |
| **OpenHouse** | Showing schedules | LOW |
| **HistoryTransactional** | Price/status change history | HIGH — signal detection |
| **CustomProperty** | SWFLA-specific fields (e.g., Gulf Access) | MEDIUM |

### Key Fields for Lead Generation

| RESO Field | Signal Value |
|------------|-------------|
| `StandardStatus` | Status changes (Expired, Withdrawn, etc.) |
| `ListPrice` / `OriginalListPrice` | Price reduction detection |
| `DaysOnMarket` / `CumulativeDaysOnMarket` | Stale listing / DOM reset detection |
| `StatusChangeTimestamp` | Fresh expirations, withdrawals, back-on-market |
| `ExpirationDate` | Predict upcoming expirations |
| `ModificationTimestamp` | Incremental sync anchor |
| `SpecialListingConditions` | Distressed properties (Short Sale, REO, Probate) |
| `PublicRemarks` | NLP motivation signals ("must sell", "as-is") |
| `ListAgentKey` | Agent pattern analysis |
| `PriceChangeTimestamp` | Price reduction velocity |

---

## Feed Types and License Categories

### Back Office Feed (BBO) — What We Need

TheLeadEdge is an **internal analytics tool**, not a public website. This makes it a **Back Office Feed** use case under NAR Policy Statement 8.7.

**BBO is explicitly permitted for:**
1. Brokerage management systems (internal only)
2. CRM and transaction management tools
3. Agent productivity and ranking tools
4. Marketplace statistical analysis and reports

**BBO advantages over IDX/VOW:**
- Broadest field access (includes fields restricted from public display)
- No seller opt-out provision (all listings available)
- No display attribution requirements (internal tool)
- No user registration requirements
- Simplest compliance path for internal tools

| Feed Type | Public? | For TheLeadEdge? |
|-----------|---------|-----------------|
| **IDX** | Yes — public website display | NO |
| **VOW** | Yes — behind client login | NO |
| **Back Office (BBO)** | No — internal only | **YES** |

---

## How to Get API Credentials — Step by Step

### Step 1: Contact NABOR (This Week)

**Phone**: 239-597-1666
**Website**: nabor.com/realtor-tools/mls-products

**What to say**: "I am a member and want to set up a back-office data feed via the RESO Web API for internal market analysis and lead prioritization. What is the application process?"

### Step 2: Apply Through Trestle

**URL**: https://trestle.corelogic.com/SubscriptionWizard

**Application will ask for:**
- MLS member ID (license number)
- Business type: Broker
- Business purpose: "Custom internal market analysis and CRM tool for my licensed real estate practice"
- Application name: "TheLeadEdge"
- Data usage: Internal analysis, lead prioritization, private back-office use
- Acknowledgment of data usage policies

### Step 3: Sign Data License Agreement

NABOR will provide a license agreement covering:
- Permitted data use (internal BBO only)
- Data retention limits
- Security requirements
- Audit provisions (MLS can audit usage)
- Termination obligations (delete data if license ends)

**Budget**: ~$500 first year ($250 setup + $250 annual license)

### Step 4: Receive Credentials

Upon approval (typically 5 business days), you receive:
- **Client ID** — application identifier
- **Client Secret** — application secret (store in `.env`, NEVER in code)
- **Token endpoint** — OAuth URL
- **Base URL** — API endpoint
- **Scope** — `api`

### Step 5: Test and Build

1. Query `$metadata` endpoint to discover available fields
2. Map Trestle RESO field names to existing `config/mls_fields.yaml`
3. Build API ingestion module to supplement CSV imports
4. Implement incremental sync using `ModificationTimestamp`

### Alternative: Explore Bridge Quick Link

While waiting for Trestle credentials, click the **Bridge Interactive** link on the NABOR member portal to see if it offers a faster provisioning path. If it leads to Bridge API registration, you could potentially get Bridge credentials as a secondary data source.

---

## Cost Summary

| Item | First Year | Annual (after) |
|------|-----------|---------------|
| NABOR data license setup | $250 | — |
| NABOR annual license | $250 | $250 |
| Trestle platform fee (estimated) | ~$180 | ~$180 |
| Bridge API fee | $0 | $0 |
| **Total (Trestle path)** | **~$680** | **~$430** |

---

## Compliance Checklist (Pre-API Access)

### Must Do Before Getting Credentials

- [ ] Contact NABOR IT/Tech Support — request BBO/RESO Web API access
- [ ] Sign data license agreement — read carefully, retain copy
- [ ] Name developer as authorized designee in agreement
- [ ] Confirm with managing broker — broker must know and approve
- [ ] Ask NABOR about: data retention limits, BBO analytics use, offline storage rules
- [ ] Confirm NABOR's 2026 NAR Handbook compliance status

### Must Build Before Going Live with API Data

- [ ] Automated data retention enforcement (weekly purge of expired records)
- [ ] Data deletion capability (for license termination)
- [ ] Credential security (`.env` only, never in code/logs/git)
- [ ] Rate limit handling (respect 429 + Retry-After headers)
- [ ] Incremental sync (ModificationTimestamp-based, not full rescan)

### Ongoing Compliance

- [ ] Scrub against federal AND Florida state DNC lists before phone outreach
- [ ] Never display MLS data publicly (internal tool only)
- [ ] Never share raw MLS data with unlicensed persons
- [ ] Respect data retention limits (delete expired records)
- [ ] Florida is two-party consent for call recording — always disclose

---

## Data Retention Rules

| Data Type | Max Retention | Action |
|-----------|-------------|--------|
| Active listings | While active | Update on status change |
| Sold/Closed | 12-36 months after close | Auto-purge after limit |
| Expired/Withdrawn | 6-12 months after status change | Auto-purge after limit |
| Deleted listings | Remove within 24-48 hours | Delete on detection |
| Property photos | While listing is active | Use URL references, don't store locally |
| Agent/Member data | Current only | Update on sync, no historical PII |

---

## Risk Assessment

| Item | Risk | Status |
|------|------|--------|
| License type (BBO for internal tool) | LOW | Correct category |
| Data license agreement | MEDIUM | Must sign before access |
| Local data storage | MEDIUM | Retention limits must be enforced |
| Automated querying | LOW | Within rate limits and permitted use |
| Deterministic scoring/analysis | LOW | Standard CRM analytics |
| Privacy/security | LOW | Project safeguards already in place |
| Internal-only use (no redistribution) | LOW | Strongest compliance position |
| Developer as designee | MEDIUM | Document authorization in agreement |
| Florida DNC compliance | MEDIUM | Scrub federal + state lists |
| Fair Housing in scoring | HIGH | Never use protected class characteristics |

**No compliance vetoes.** Internal lead gen tool for a licensed Realtor member is the lowest-risk MLS data use case.

---

## Technical Integration Notes

### Authentication Flow (Trestle)
```
POST https://api.cotality.com/trestle/oidc/connect/token
Content-Type: application/x-www-form-urlencoded

client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials&scope=api
```

Response provides Bearer token valid for 8 hours.

### Sample Query — Expired Listings
```
GET https://api.cotality.com/trestle/odata/Property
  ?$filter=StandardStatus eq 'Expired'
    and StatusChangeTimestamp gt 2026-03-01T00:00:00Z
    and PostalCode in ('33901','33903','33904','33914','33919')
  &$select=ListingKey,ListPrice,OriginalListPrice,DaysOnMarket,StandardStatus,
    StatusChangeTimestamp,StreetNumberNumeric,StreetName,City,PostalCode,
    ListAgentKey,ListAgentFullName
  &$orderby=StatusChangeTimestamp desc
  &$top=200
```

### Rate Limit Headers to Monitor
```
Minute-Quota-Limit: 180
Hour-Quota-Limit: 7200
Hour-Quota-Available: 7150
Hour-Quota-ResetTime: 2026-03-03T19:00:00Z
```

### Incremental Sync Pattern
Use `ModificationTimestamp` to pull only changed records:
```
$filter=ModificationTimestamp gt 2026-03-03T12:00:00Z
```

---

## Key Contacts

| Contact | Purpose | Details |
|---------|---------|---------|
| NABOR main | General MLS questions | 239-597-1666, nabor.com |
| NABOR MLS Products | Data feed applications | nabor.com/realtor-tools/mls-products |
| RPCRA data licensing | Lee County MLS data | mlstrestle@rpcra.org |
| BER tech support | Bonita Springs-Estero data | Tech@BERealtors.org |
| Trestle support | API technical issues | trestlesupport@cotality.com |
| Bridge API support | Bridge-specific questions | BridgeAPI@bridgeinteractive.com |

---

## Key URLs

| Resource | URL |
|----------|-----|
| NABOR member portal | mdweb.mmsi2.com/naples/ |
| SWFLA MLS (Matrix) | matrix.swflamls.com |
| Trestle documentation | trestle-documentation.corelogic.com |
| Trestle registration | trestle.corelogic.com/SubscriptionWizard |
| Bridge API docs | bridgedataoutput.com/docs/platform/ |
| NABOR MLS rules (Feb 2025) | nabor.com (MLS Resources section) |
| NAR BBO Policy 8.7 | nar.realtor/handbook-on-multiple-listing-policy |

---

## What RETS? It's Dead.

NABOR discontinued RETS, Data Replicator, and legacy MLS Add-on support as of **December 31, 2024**. All new integrations must use the RESO Web API. Do not pursue RETS credentials.

---

## Next Steps (Recommended Order)

1. **This week**: Realtor calls NABOR at 239-597-1666 requesting BBO RESO Web API access
2. **This week**: Click Bridge Interactive link on member portal to explore that path
3. **While waiting**: Continue using CSV exports (Phase 1 MVP already supports this)
4. **On credential receipt**: Query `$metadata` to discover available fields
5. **Build Phase 4**: API ingestion module to supplement/replace CSV imports
6. **Map fields**: RESO DD field names to existing `config/mls_fields.yaml` (should be nearly 1:1)

---

*Compiled from research by MLS Data Specialist (x3) and Compliance Specialist agents, 2026-03-03*
