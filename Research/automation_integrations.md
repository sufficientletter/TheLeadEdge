# Automation & Integrations Research

> **Project**: TheLeadEdge — Real Estate Lead Generation Dashboard
> **Created**: 2026-02-28
> **Purpose**: Third-party integrations, automation opportunities, and AI/LLM integration

---

## 1. MLS Data Access Methods

### 1.1 RESO Web API (Current Standard)

The **RESO Web API** is the modern standard replacing legacy RETS feeds. Based on OData v4, it provides RESTful access to MLS data.

**How to Get Access**:
1. The Realtor's MLS board membership includes data access rights
2. Contact the MLS board's IT/tech department and request API credentials
3. Some boards use third-party platforms (Trestle, Bridge, Spark) to serve the API
4. You'll receive: base URL, client ID, client secret, and scope
5. May require a signed data license agreement

**Authentication**: OAuth 2.0 client credentials flow

**Key Endpoints**:
```
GET /Property           — Listings (active, expired, sold, withdrawn)
GET /Member             — Agent/broker information
GET /Office             — Brokerage office data
GET /OpenHouse          — Open house schedules
GET /Media              — Property photos
```

**OData Query Examples**:
```
# Expired listings in last 7 days
/Property?$filter=StandardStatus eq 'Expired'
  and StatusChangeTimestamp gt 2026-02-21T00:00:00Z

# Active listings with 90+ DOM
/Property?$filter=StandardStatus eq 'Active'
  and DaysOnMarket ge 90
  &$orderby=DaysOnMarket desc

# Price reductions in specific ZIP
/Property?$filter=StandardStatus eq 'Active'
  and PostalCode eq '85281'
  and ListPrice lt OriginalListPrice

# Withdrawn and relisted (CDOM > DOM indicates reset)
/Property?$filter=StandardStatus eq 'Active'
  and CumulativeDaysOnMarket gt DaysOnMarket

# Select specific fields only
&$select=ListingKey,StandardStatus,ListPrice,OriginalListPrice,
  DaysOnMarket,PostalCode,StreetAddress,ListAgentKey
```

### 1.2 MLS Data Platform Comparison

| Platform | Coverage | API Standard | Authentication | Cost | Notes |
|----------|----------|-------------|----------------|------|-------|
| **Trestle** | 600+ MLSs | RESO Web API | OAuth 2.0 | Via MLS membership | Largest aggregator, owned by CoreLogic |
| **Bridge Interactive** | 300+ MLSs | RESO Web API | OAuth 2.0 | Via MLS membership | Good documentation, Zillow-backed |
| **Spark API** | 200+ MLSs | Custom + RESO | API key | Via MLS membership | FBS (FlexMLS) platform |
| **MLS Grid** | 100+ MLSs | RESO Web API | OAuth 2.0 | Via MLS membership | Growing, focused on data standardization |
| **RETS (Legacy)** | Most MLSs | XML-based | Digest auth | Via MLS membership | Being phased out — avoid if possible |

**Recommendation**: Check which platform the Realtor's MLS board uses first. Most Arizona boards use Trestle or Spark.

### 1.3 Access Strategy (Prioritized)

| Priority | Method | Effort | Data Quality | Real-Time |
|----------|--------|--------|-------------|-----------|
| 1 | **RESO Web API** via Realtor's board | Medium | Best | Yes |
| 2 | **Trestle/Bridge** aggregator | Medium | Best | Yes |
| 3 | **MLS saved search exports** (CSV) | Low | Good | Daily |
| 4 | **Manual MLS portal checks** | None | Good | Manual |

Start with option 3 (CSV exports) to validate the system, then upgrade to option 1 or 2 for automation.

### 1.4 Rate Limits & Best Practices

- Most RESO APIs limit to 200-500 records per request
- Use `$top` and `$skip` for pagination
- Typical rate limits: 1,000-5,000 requests per hour
- Cache responses — MLS data changes daily, not minutely
- Use `$filter` with timestamps for incremental syncs (only fetch changes since last sync)
- Respect `Retry-After` headers on 429 responses
- Schedule heavy syncs during off-peak hours (midnight to 6 AM)

---

## 2. Public Records Data Automation

### 2.1 County Recorder APIs

Most county recorders do NOT offer APIs. Access methods:

| Method | Availability | Cost | Automation |
|--------|-------------|------|-----------|
| County website search | Most counties | Free | Selenium/Playwright scraping |
| County data downloads | Some counties | Free-$50 | CSV/bulk downloads |
| FOIA/public records requests | All counties | Free-$25 | Manual + tracking |
| **Aggregator APIs** (ATTOM, PropertyRadar) | Nationwide | $50-300/mo | Full API access |

**Arizona-Specific Resources**:
- Maricopa County Recorder: recorder.maricopa.gov — searchable online, no API
- Pima County Recorder: Online search available
- Most AZ counties offer online deed/lien search

### 2.2 Aggregated Public Records (Recommended Path)

**ATTOM Data** (~$250/mo):
- Pre-foreclosure/NOD filings
- Tax delinquency data
- Property ownership history
- Deed transfers
- Building permits
- AVM (Automated Valuation Model)
- Coverage: Nationwide, 155M+ properties

**PropertyRadar** (~$100/mo):
- Pre-foreclosure monitoring
- Probate filings (select counties)
- Divorce filings (select counties)
- Code violations (select counties)
- Absentee owner identification
- Best for: Western US markets

**BatchData** (~$50/mo):
- Property data enrichment
- Skip tracing (owner contact info)
- Bulk processing
- Good value for the price

### 2.3 Court Records Monitoring

**Probate Court**:
- Check probate court dockets weekly
- Search for new real property filings
- Many AZ courts use iCourt or Odyssey systems
- Set up manual alerts where available
- ATTOM provides some probate data

**Divorce Filings**:
- Family court records are public in most states
- Search for cases with real property listed
- Ethical consideration: wait 30+ days before outreach, use empathetic messaging
- Some aggregators include divorce data

### 2.4 FOIA Request Templates

For utility disconnection data (indicates vacancy):

```
Subject: Public Records Request — Utility Service Disconnections

Dear [Municipal Utility Department],

Pursuant to [State Public Records Act], I am requesting the following records:

1. A list of residential properties that have had water/electric
   service disconnected or placed on inactive status within the
   last 90 days in ZIP codes [list target ZIPs].

2. For each property, I request: service address, disconnection
   date, and account status (voluntary disconnect vs. non-payment).

I am willing to pay reasonable fees for this request. Please
advise of any costs before processing.

Format preference: CSV or Excel spreadsheet.

Thank you,
[Name]
```

Track FOIA requests in a simple table:
```sql
CREATE TABLE foia_requests (
    id          INTEGER PRIMARY KEY,
    agency      TEXT NOT NULL,
    data_type   TEXT NOT NULL,
    submitted   DATE,
    due_date    DATE,  -- Statutory response deadline
    status      TEXT DEFAULT 'submitted',  -- submitted, acknowledged, received, denied
    file_path   TEXT,  -- Path to received data file
    notes       TEXT
);
```

---

## 3. CRM Integration

### 3.1 Follow Up Boss API

Follow Up Boss (FUB) is the recommended CRM due to its excellent API and real estate focus.

**API Overview**:
- Base URL: `https://api.followupboss.com/v1`
- Auth: API key via HTTP Basic Auth (key as username, blank password)
- Format: JSON
- Rate limit: 120 requests/minute

```python
import httpx
import base64

class FollowUpBossClient:
    BASE_URL = "https://api.followupboss.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        credentials = base64.b64encode(f"{api_key}:".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }

    async def create_person(self, lead: dict) -> dict:
        """Push a new lead to FUB"""
        payload = {
            "firstName": lead.get("first_name"),
            "lastName": lead.get("last_name"),
            "emails": [{"value": lead.get("email")}] if lead.get("email") else [],
            "phones": [{"value": lead.get("phone")}] if lead.get("phone") else [],
            "tags": lead.get("tags", []),  # e.g., ["S-Tier", "Expired", "TheLeadEdge"]
            "source": "TheLeadEdge",
            "customFields": {
                "leadfinder_score": str(lead.get("score", 0)),
                "leadfinder_tier": lead.get("tier", "D"),
                "leadfinder_signals": lead.get("signal_summary", ""),
                "property_address": lead.get("address", ""),
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/people",
                json=payload,
                headers=self.headers
            )
            return response.json()

    async def add_note(self, person_id: int, note: str) -> dict:
        """Add a note to a FUB contact"""
        payload = {"personId": person_id, "body": note}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/notes",
                json=payload,
                headers=self.headers
            )
            return response.json()

    async def get_person_by_phone(self, phone: str) -> dict | None:
        """Check if lead already exists in FUB"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/people",
                params={"phone": phone},
                headers=self.headers
            )
            data = response.json()
            people = data.get("people", [])
            return people[0] if people else None

    async def update_tags(self, person_id: int, tags: list[str]) -> dict:
        """Update tags on a FUB contact"""
        payload = {"tags": tags}
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.BASE_URL}/people/{person_id}",
                json=payload,
                headers=self.headers
            )
            return response.json()
```

### 3.2 Two-Way Sync Pattern

```python
class CRMSyncService:
    """Bidirectional sync between TheLeadEdge and Follow Up Boss"""

    async def push_lead_to_crm(self, lead: Lead, property: Property):
        """TheLeadEdge → FUB: Push new leads or updates"""
        # Check if already in CRM
        existing = await self.fub.get_person_by_phone(property.owner_phone)

        if existing:
            # Update existing contact with new score/signals
            await self.fub.update_tags(existing["id"], [
                f"LF-{lead.tier}-Tier",
                f"LF-Score-{lead.current_score:.0f}",
                "TheLeadEdge"
            ])
            await self.fub.add_note(
                existing["id"],
                f"TheLeadEdge Update: Score {lead.current_score:.0f} ({lead.tier}-Tier)\n"
                f"Signals: {lead.signal_summary}\n"
                f"Property: {property.address}"
            )
            lead.crm_id = str(existing["id"])
        else:
            # Create new contact
            result = await self.fub.create_person({
                "first_name": property.owner_name.split()[0] if property.owner_name else "",
                "last_name": " ".join(property.owner_name.split()[1:]) if property.owner_name else "",
                "phone": property.owner_phone,
                "email": property.owner_email,
                "score": lead.current_score,
                "tier": lead.tier,
                "signal_summary": lead.signal_summary,
                "address": property.address,
                "tags": [f"LF-{lead.tier}-Tier", "TheLeadEdge"]
            })
            lead.crm_id = str(result.get("id"))

        lead.crm_synced_at = datetime.utcnow()

    async def pull_status_from_crm(self):
        """FUB → TheLeadEdge: Pull lead status updates back"""
        # Use FUB webhooks for real-time, or poll periodically
        # When the Realtor marks a contact as "Listing Signed" in FUB,
        # update the lead status in TheLeadEdge
        pass
```

### 3.3 CRM Comparison

| Feature | Follow Up Boss | LionDesk | kvCORE | Sierra Interactive |
|---------|---------------|----------|--------|-------------------|
| **Price** | $69/mo | $25/mo | $500/mo (team) | Custom pricing |
| **API Quality** | Excellent | Good | Limited | Limited |
| **Integrations** | 250+ | 100+ | Built-in IDX | Built-in IDX |
| **Real Estate Focus** | Pure RE | Pure RE | Pure RE + IDX | Pure RE + IDX |
| **Webhook Support** | Yes | Limited | Limited | No |
| **Custom Fields** | Yes | Yes | Yes | Yes |
| **Best For** | API integration | Budget option | All-in-one teams | Full website + CRM |

**Recommendation**: Follow Up Boss for API quality and integration ecosystem.

---

## 4. Communication Automation

### 4.1 Automated CMA Generation

```python
class CMAGenerator:
    """Generate Comparative Market Analysis for outreach"""

    async def generate_cma(self, property: Property) -> dict:
        """Pull comps and generate CMA data"""
        # Find comparable sales within last 6 months, 0.5 mile radius
        comps = await self.find_comps(
            lat=property.latitude,
            lng=property.longitude,
            radius_miles=0.5,
            beds_range=(property.bedrooms - 1, property.bedrooms + 1),
            sqft_range=(property.sqft * 0.8, property.sqft * 1.2),
            sold_within_days=180
        )

        if not comps:
            # Expand search if no comps found
            comps = await self.find_comps(
                lat=property.latitude, lng=property.longitude,
                radius_miles=1.0,
                beds_range=(property.bedrooms - 1, property.bedrooms + 1),
                sqft_range=(property.sqft * 0.7, property.sqft * 1.3),
                sold_within_days=365
            )

        avg_price_sqft = sum(c.sold_price / c.sqft for c in comps) / len(comps) if comps else 0
        estimated_value = int(avg_price_sqft * property.sqft)

        return {
            "subject_property": property,
            "comparables": comps[:6],  # Top 6 most similar
            "avg_price_per_sqft": avg_price_sqft,
            "estimated_value": estimated_value,
            "value_range": (int(estimated_value * 0.95), int(estimated_value * 1.05)),
            "generated_at": datetime.utcnow()
        }
```

### 4.2 Direct Mail Integration

**Click2Mail API** (automated printed mail):
```python
class Click2MailClient:
    """Send physical mail pieces via Click2Mail API"""

    BASE_URL = "https://batch.click2mail.com/molpro/documents"

    async def send_letter(self, to_address: dict, template: str, merge_data: dict):
        """Send a single letter"""
        # Click2Mail supports:
        # - Letters (8.5x11)
        # - Postcards (4x6, 6x9, 6x11)
        # - Handwritten-style font options
        # Pricing: ~$0.75-$2.00 per piece depending on format
        pass
```

**Handwrytten API** (robotic handwritten notes — highest response rate):
```python
class HandwryttenClient:
    """Send handwritten notes via Handwrytten API"""
    # Pricing: ~$3.25-$4.50 per card
    # Response rate: 3-5x higher than printed mail
    # Best for: S-Tier and A-Tier leads only (ROI justified)
    pass
```

### 4.3 TCPA SMS Compliance

Rules for automated text messaging to leads:

| Requirement | Details |
|-------------|---------|
| **Prior express consent** | Required BEFORE sending marketing texts |
| **Opt-in mechanism** | Must have verifiable written consent |
| **Opt-out** | Must include opt-out instructions in every message |
| **Time restrictions** | No texts before 8 AM or after 9 PM local time |
| **Caller ID** | Must display accurate caller information |
| **DNC list** | Must check National Do Not Call Registry |
| **Record keeping** | Maintain consent records for 5 years |
| **Penalties** | $500-$1,500 per violation |

**Recommendation**: Do NOT send automated marketing texts without explicit opt-in. Use text only for leads who have responded and consented. Initial outreach should be phone call or mail.

---

## 5. AI/LLM Integration Opportunities

### 5.1 Claude API for Lead Summaries

```python
import anthropic

class LeadAnalyzer:
    """Use Claude API to generate natural language lead insights"""

    def __init__(self):
        self.client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

    async def generate_lead_summary(self, lead: Lead, property: Property,
                                     signals: list[Signal]) -> str:
        """Generate a natural language summary of why this lead is hot"""
        signal_descriptions = "\n".join(
            f"- {s.signal_type}: {s.description} ({s.points} pts)"
            for s in signals
        )

        prompt = f"""You are a real estate lead analyst. Summarize this lead for a Realtor
in 2-3 sentences. Be direct and actionable — tell them WHY this is a good lead
and WHAT to do about it.

Property: {property.address}, {property.city} {property.state} {property.zip_code}
Type: {property.bedrooms}bd/{property.bathrooms}ba, {property.sqft} sqft
List Price: ${property.list_price:,} (Original: ${property.original_list_price:,})
Days on Market: {property.days_on_market}
Owner: {property.owner_name} {'(Absentee - ' + property.owner_address + ')' if property.is_absentee else '(Owner-occupied)'}

Score: {lead.current_score}/100 ({lead.tier}-Tier)
Signals Detected:
{signal_descriptions}

Write a brief, actionable summary."""

        message = self.client.messages.create(
            model="claude-haiku-4-5-20251001",  # Fast + cheap for summaries
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
```

**Example Output**:
> "This expired listing at 123 Main St is a high-priority lead with 4 converging signals. The owner is out-of-state (California), the property has been on market 142 days with 3 price drops totaling $46K, and a pre-foreclosure NOD was filed two weeks ago. Call today with a CMA showing the $410K estimated value — the owner likely needs to sell quickly to preserve equity."

### 5.2 Automated Outreach Drafting

```python
async def draft_outreach_email(self, lead: Lead, property: Property,
                                approach: str = "expired") -> str:
    """Generate personalized outreach email"""
    templates = {
        "expired": "Their listing just expired. Empathize with frustration, offer fresh approach.",
        "pre_foreclosure": "Facing foreclosure. Be sensitive, position as helper not vulture.",
        "price_reduction": "Multiple price drops indicate motivation. Offer realistic pricing strategy.",
        "absentee": "Out-of-area owner. Emphasize local expertise and hands-off management.",
    }

    prompt = f"""Write a short, warm email from a Realtor to a potential seller.
Tone: {templates.get(approach, 'Professional and helpful')}

Property: {property.address}
Owner: {property.owner_name}
Situation: {lead.signal_summary}

Keep it under 150 words. Be genuine, not salesy. Don't use exclamation marks.
Include a soft call to action (offer a free market analysis or coffee meeting).
Sign off with the Realtor's name and contact info placeholder."""

    message = self.client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
```

### 5.3 Natural Language Dashboard Queries

```python
async def nl_to_query(self, question: str) -> str:
    """Convert natural language to SQL query for the dashboard"""
    schema_context = """
    Tables: leads (current_score, tier, status, detected_at),
    properties (address, city, zip_code, list_price, bedrooms, bathrooms, sqft, days_on_market, mls_status),
    signals (signal_type, signal_category, points, detected_at)
    Tiers: S (80-100), A (60-79), B (40-59), C (20-39), D (0-19)
    """

    prompt = f"""Convert this natural language question into a SQLite query.
Schema: {schema_context}
Question: "{question}"
Return ONLY the SQL query, nothing else."""

    message = self.client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
```

**Example Queries**:
- "Show me all hot leads in 85281" → `SELECT * FROM leads l JOIN properties p ON ... WHERE l.tier = 'S' AND p.zip_code = '85281'`
- "How many expireds this week?" → `SELECT COUNT(*) FROM signals WHERE signal_type = 'expired_listing' AND detected_at > ...`
- "What's my best ZIP code for leads?" → `SELECT p.zip_code, COUNT(*) as lead_count, AVG(l.current_score) FROM ...`

### 5.4 Cost Estimate for AI Features

| Feature | Model | Calls/Day | Tokens/Call | Daily Cost | Monthly Cost |
|---------|-------|-----------|-------------|------------|-------------|
| Lead Summaries | Haiku | ~20 | ~500 | $0.01 | $0.30 |
| Outreach Drafts | Haiku | ~10 | ~600 | $0.005 | $0.15 |
| NL Queries | Haiku | ~10 | ~300 | $0.003 | $0.09 |
| Weekly Reports | Sonnet | 1/week | ~2000 | $0.004 | $0.12 |
| **Total** | | | | | **~$0.66/mo** |

Using Haiku for most features keeps costs extremely low. Even heavy usage would be under $5/month.

---

## 6. Monitoring & Analytics

### 6.1 Lead Source ROI Tracking

```python
class ROITracker:
    """Track which lead sources produce the best conversion rates"""

    async def get_source_performance(self, days: int = 90) -> list[dict]:
        """ROI by lead source over time period"""
        query = """
            SELECT
                s.signal_type as source,
                COUNT(DISTINCT l.id) as total_leads,
                SUM(CASE WHEN l.status = 'contacted' THEN 1 ELSE 0 END) as contacted,
                SUM(CASE WHEN l.status = 'meeting' THEN 1 ELSE 0 END) as meetings,
                SUM(CASE WHEN l.status = 'listing' THEN 1 ELSE 0 END) as listings,
                SUM(CASE WHEN l.status = 'closed' THEN 1 ELSE 0 END) as closed,
                ROUND(100.0 * SUM(CASE WHEN l.status = 'listing' THEN 1 ELSE 0 END) /
                    NULLIF(COUNT(DISTINCT l.id), 0), 1) as conversion_pct,
                AVG(l.current_score) as avg_score
            FROM signals s
            JOIN leads l ON s.lead_id = l.id
            WHERE s.detected_at > datetime('now', ? || ' days')
              AND s.is_active = TRUE
            GROUP BY s.signal_type
            ORDER BY conversion_pct DESC
        """
        return await db.fetch_all(query, (-days,))
```

### 6.2 Dashboard Usage Analytics

Track what the Realtor actually uses to optimize the dashboard:

```sql
CREATE TABLE usage_analytics (
    id          INTEGER PRIMARY KEY,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    page        TEXT,       -- briefing, leads, map, pipeline, settings
    action      TEXT,       -- view, click, filter, sort, search, call, cma
    details     TEXT,       -- JSON with specifics
    duration_ms INTEGER     -- Time spent on page/action
);

-- Weekly analysis queries:
-- Most visited pages
SELECT page, COUNT(*) as visits FROM usage_analytics
WHERE timestamp > datetime('now', '-7 days') GROUP BY page ORDER BY visits DESC;

-- Most used actions
SELECT action, COUNT(*) as uses FROM usage_analytics
WHERE timestamp > datetime('now', '-7 days') GROUP BY action ORDER BY uses DESC;

-- Average session duration
SELECT AVG(duration_ms) / 1000.0 / 60.0 as avg_minutes FROM usage_analytics
WHERE action = 'view' AND page = 'briefing';
```

---

## 7. Workflow Automation Tools

### 7.1 n8n vs Make vs Zapier

| Feature | n8n | Make (Integromat) | Zapier |
|---------|-----|-------------------|--------|
| **Pricing** | Free (self-hosted) | $9/mo (10K ops) | $20/mo (750 tasks) |
| **Self-Hosted** | Yes (Docker) | No | No |
| **Complexity** | High customization | Visual, moderate | Simplest |
| **Webhook Support** | Excellent | Good | Good |
| **Custom Code** | JavaScript/Python nodes | Limited | Limited |
| **Real Estate Integrations** | Via HTTP nodes | Pre-built connectors | Most pre-built |
| **Best For** | Custom workflows, cost-conscious | Visual automation | Quick setup |

**Recommendation**: Self-hosted **n8n** for maximum flexibility at zero cost. Deploy alongside TheLeadEdge in Docker.

### 7.2 When Workflow Tools vs Custom Code

| Use Case | Workflow Tool | Custom Code |
|----------|--------------|-------------|
| Simple A→B data transfer | Workflow tool | Overkill |
| Complex data transformation | Custom code | Better control |
| Multi-step with branching | Either | Custom for complex logic |
| Monitoring & alerts | Workflow tool | Overkill |
| Core scoring engine | Custom code | Critical path |
| CRM sync | Either | Custom for two-way |
| Email notifications | Workflow tool | Simple enough |
| MLS data pipeline | Custom code | Complex parsing needed |

### 7.3 Webhook Patterns

```python
# NiceGUI + FastAPI webhook receiver for real-time updates
from nicegui import app
from fastapi import Request

@app.post("/webhooks/fub")
async def fub_webhook(request: Request):
    """Receive webhooks from Follow Up Boss"""
    payload = await request.json()
    event = payload.get("event")

    if event == "person.updated":
        # CRM contact was updated — sync status back to TheLeadEdge
        person_id = payload["data"]["id"]
        new_stage = payload["data"].get("stage")
        await sync_crm_status_to_lead(person_id, new_stage)

    elif event == "note.created":
        # New note added in CRM — log activity in TheLeadEdge
        lead_id = await find_lead_by_crm_id(payload["data"]["personId"])
        if lead_id:
            await log_activity(lead_id, "crm_note", payload["data"]["body"])

    return {"status": "ok"}

@app.post("/webhooks/mls-alert")
async def mls_alert_webhook(request: Request):
    """Receive MLS saved search alerts (if board supports webhooks)"""
    payload = await request.json()
    # Process new/changed listings
    for listing in payload.get("listings", []):
        await process_mls_listing(listing)
    return {"status": "ok"}
```

---

## 8. Implementation Priority Matrix

| Phase | Components | Monthly Cost | Timeline |
|-------|-----------|-------------|----------|
| **Phase 0: Bootstrap** | MLS saved searches (manual CSV), Google Alerts, manual public records | $0 | Week 1 |
| **Phase 1: Dashboard MVP** | NiceGUI dashboard, SQLite, manual data import, scoring engine | $0 | Week 2-4 |
| **Phase 2: CRM** | Follow Up Boss integration, lead push, status sync | $69 | Month 2 |
| **Phase 3: Data Feeds** | REDX expired/FSBO feeds, automated MLS sync | $129 | Month 2-3 |
| **Phase 4: Enrichment** | BatchLeads skip tracing, property data enrichment | $228 | Month 3 |
| **Phase 5: Full Pipeline** | ATTOM API, public records automation, AI summaries | $480 | Month 4-5 |
| **Phase 6: Advanced** | Direct mail automation, n8n workflows, ML scoring | $590 | Month 6+ |

---

## 9. Security & Compliance Checklist

### 9.1 Regulatory Compliance

| Regulation | Applies To | Key Requirement |
|-----------|-----------|-----------------|
| **Do Not Call (DNC)** | Phone outreach | Scrub lists against federal/state DNC registry |
| **CAN-SPAM** | Email outreach | Include unsubscribe link, physical address, accurate subject |
| **TCPA** | Text/auto-dial | Prior express written consent required |
| **Fair Housing Act** | All outreach | No discrimination based on protected classes |
| **MLS Terms of Service** | MLS data | Data for licensed use only, no resale |
| **FCRA** | Credit-related data | Cannot use credit data for marketing (not applicable if avoiding credit data) |
| **State Laws** | Varies | Some states restrict pre-foreclosure solicitation timing |

### 9.2 Data Security

```
.env file structure:
├── MLS_BASE_URL=https://api.mlsboard.com/reso/odata
├── MLS_CLIENT_ID=your_client_id
├── MLS_CLIENT_SECRET=your_client_secret
├── ATTOM_API_KEY=your_attom_key
├── BATCH_LEADS_API_KEY=your_batch_key
├── FUB_API_KEY=your_fub_key
├── ANTHROPIC_API_KEY=your_anthropic_key
├── SENDGRID_API_KEY=your_sendgrid_key
├── DASHBOARD_USERNAME=sarah
├── DASHBOARD_PASSWORD_HASH=sha256_hash_here
└── SECRET_KEY=random_secret_for_sessions

NEVER commit .env to git — add to .gitignore
```

### 9.3 API Key Management Best Practices

1. Store all keys in `.env` file, never in code
2. Add `.env` to `.gitignore`
3. Use different keys for development and production
4. Rotate keys every 90 days
5. Monitor API usage dashboards for unexpected spikes
6. Set up billing alerts on paid APIs
7. Use least-privilege: request only scopes you need

---

*This research covers the full integration landscape for TheLeadEdge, from MLS data access to CRM sync to AI-powered lead analysis, with a phased implementation plan that scales from $0 to a full production system.*
