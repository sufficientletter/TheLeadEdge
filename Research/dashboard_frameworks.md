# Dashboard Frameworks Research

> **Project**: TheLeadEdge — Real Estate Lead Generation Dashboard
> **Created**: 2026-02-28
> **Purpose**: Evaluate frameworks for building a beautiful, data-rich browser dashboard

---

## 1. Top Python Dashboard Frameworks

### 1.1 Streamlit

**Description**: The most popular Python dashboard framework. Renders widgets top-to-bottom in a script-like flow.

**Pros**:
- Fastest prototyping — working dashboard in under an hour
- Huge community, extensive component ecosystem (1,000+ community components)
- Built-in caching (`@st.cache_data`), session state, file uploads
- Free hosting on Streamlit Community Cloud
- Native support for Plotly, Altair, Matplotlib, deck.gl maps
- `st.columns`, `st.tabs`, `st.expander` for layout

**Cons**:
- Re-runs entire script on every interaction (performance bottleneck)
- Limited layout control — fundamentally a single-column flow
- No true real-time push (uses polling via `st.experimental_rerun`)
- Looks like Streamlit — hard to escape the "Streamlit look"
- No native component system — custom components require React + iframe bridge
- Not suitable for complex multi-page apps with shared state

**Visual Quality**: 3/5 — Clean but generic. Recognizably "Streamlit."
**Real-Time**: Limited (polling only, no WebSocket push)
**Map Support**: Good — `st.map`, `st.pydeck_chart`, Folium via `streamlit-folium`
**Best For**: Quick prototypes, data exploration, proof of concept

---

### 1.2 Dash (Plotly)

**Description**: Enterprise-grade analytical dashboard framework by Plotly. Uses Flask under the hood. Callback-based reactivity.

**Pros**:
- Best-in-class charting via Plotly.js (50+ chart types)
- Callback system is powerful for complex interactions
- Dash Enterprise offers authentication, deployment, job queues
- Native Mapbox integration for beautiful maps
- `dash-bootstrap-components` and `dash-mantine-components` for modern UI
- Multi-page app support, long callbacks, background jobs

**Cons**:
- Callback hell — complex apps become hard to manage
- Steeper learning curve than Streamlit
- Verbose boilerplate for layouts (nested `html.Div` trees)
- Community components lag behind Streamlit ecosystem
- Dash Enterprise is expensive ($15K+/year) — open-source version lacks auth

**Visual Quality**: 4/5 — Plotly charts are beautiful. Layouts require effort.
**Real-Time**: Good — `dcc.Interval` for polling, Dash extensions for WebSocket
**Map Support**: Excellent — native Plotly Mapbox, Scattermapbox, Choropleth
**Best For**: Data-heavy analytical dashboards, chart-centric UIs

---

### 1.3 Panel (HoloViz)

**Description**: Part of the HoloViz ecosystem. Flexible — works in notebooks, scripts, and as apps. Supports multiple plotting libraries.

**Pros**:
- Works with any Python plotting library (Matplotlib, Bokeh, Plotly, Altair, hvPlot)
- Reactive programming model (`param` library)
- Good for scientific/geospatial visualization via GeoViews
- Template system for multi-page layouts
- Can run in Jupyter notebooks AND as standalone apps

**Cons**:
- Smaller community, fewer resources
- UI looks dated compared to modern frameworks
- Documentation can be confusing (many related libraries)
- Steeper learning curve due to HoloViz ecosystem complexity
- Limited mobile responsiveness out of the box

**Visual Quality**: 2.5/5 — Functional but dated looking
**Real-Time**: Good — native WebSocket via Bokeh server
**Map Support**: Good — GeoViews, hvPlot with geographic projections
**Best For**: Scientific/geospatial applications, Jupyter-centric workflows

---

### 1.4 Gradio

**Description**: Originally built for ML model demos. Rapidly expanding into general-purpose dashboards.

**Pros**:
- Dead simple API — `gr.Interface` creates UI in 3 lines
- Great for input/output workflows (upload → process → display)
- Built-in sharing via Gradio links
- Growing component ecosystem
- Owned by Hugging Face — strong backing

**Cons**:
- Designed for ML demos, not business dashboards
- Limited layout customization
- No native map support
- Not suitable for complex multi-view dashboards
- Limited theming options

**Visual Quality**: 3/5 — Modern but limited
**Real-Time**: Limited
**Map Support**: None native
**Best For**: ML model demos, simple input/output tools — NOT for this project

---

### 1.5 NiceGUI ⭐ RECOMMENDED

**Description**: Full-featured Python UI framework built on Quasar (Vue.js + Material Design) and Tailwind CSS. Creates beautiful, modern web applications.

**Pros**:
- **Best visual quality** of any Python framework — Material Design + Tailwind CSS
- Native Leaflet map integration (`ui.leaflet`)
- Native AG Grid data tables (`ui.aggrid`) — the industry standard grid
- Real-time WebSocket push built-in (bidirectional client-server communication)
- True component model — compose UIs from reusable elements
- Single Python process — no separate frontend build step
- Tailwind CSS utility classes available directly in Python
- Dark mode built-in via Quasar
- File upload, download, notification toasts, dialogs, menus all native
- Active development, responsive maintainer, growing community
- Runs on FastAPI under the hood — easy to add REST API endpoints

**Cons**:
- Smaller community than Streamlit/Dash (but growing fast)
- Less charting variety than Plotly (uses ECharts — still very capable)
- Documentation improving but not as extensive as Streamlit
- Quasar/Vue.js knowledge helpful for advanced customization
- Fewer third-party extensions

**Visual Quality**: 5/5 — Material Design + Tailwind = polished, professional
**Real-Time**: Excellent — native WebSocket, `ui.timer`, server push
**Map Support**: Excellent — native `ui.leaflet` with markers, popups, layers
**Best For**: Beautiful internal tools, dashboards that need to look professional

---

### 1.6 Reflex

**Description**: Full-stack Python framework that compiles to Next.js. Write Python, get a React app.

**Pros**:
- Full React/Next.js power without writing JavaScript
- Component-based architecture
- SEO-friendly (server-side rendering)
- State management built-in
- Growing ecosystem, active development
- Can use any React component via wrapping

**Cons**:
- Compiles to Next.js — adds build complexity
- Slower development iteration (compile step)
- Relatively new — fewer production deployments
- Heavier infrastructure requirements (Node.js + Python)
- State sync between Python and JS can be tricky

**Visual Quality**: 4.5/5 — React/Tailwind quality
**Real-Time**: Good — WebSocket state sync
**Map Support**: Via React component wrapping (react-leaflet, react-map-gl)
**Best For**: Full web applications that need SPA-quality interactions

---

### 1.7 FastHTML

**Description**: Minimalist Python web framework by Jeremy Howard (fast.ai). Uses HTMX for interactivity.

**Pros**:
- Extremely lightweight — minimal dependencies
- HTMX for modern interactivity without JavaScript
- Fast server-side rendering
- Simple mental model — Python generates HTML
- Created by respected ML educator

**Cons**:
- Very new — small ecosystem
- No built-in component library
- Need to bring your own CSS framework
- Limited charting support
- No native map integration

**Visual Quality**: 3/5 — depends entirely on your CSS skills
**Real-Time**: Good — HTMX SSE/WebSocket extensions
**Map Support**: Manual integration required
**Best For**: Lightweight tools, developers who prefer HTML-centric approach

---

### 1.8 Mesop (Google)

**Description**: Google's Python UI framework. Component-based, Material Design.

**Pros**:
- Google backing and Material Design
- Clean component model
- Type-safe state management
- Good developer experience

**Cons**:
- Very new, small community
- Limited ecosystem
- Primarily designed for internal Google use cases
- Limited third-party integrations
- Uncertain long-term commitment from Google

**Visual Quality**: 4/5 — Material Design
**Real-Time**: Limited
**Map Support**: None native
**Best For**: Simple internal tools — too early for production use

---

### 1.9 Comparison Matrix

| Feature | Streamlit | Dash | Panel | NiceGUI | Reflex | FastHTML |
|---------|-----------|------|-------|---------|--------|---------|
| **Visual Quality** | 3/5 | 4/5 | 2.5/5 | **5/5** | 4.5/5 | 3/5 |
| **Learning Curve** | Easy | Medium | Hard | Easy | Medium | Easy |
| **Real-Time Push** | No | Partial | Yes | **Yes** | Yes | Yes |
| **Native Maps** | pydeck | Mapbox | GeoViews | **Leaflet** | Wrapped | Manual |
| **Data Tables** | Basic | DataTable | Tabulator | **AG Grid** | Wrapped | Manual |
| **Charting** | Many libs | **Plotly** | Many libs | ECharts | Wrapped | Manual |
| **Mobile Ready** | Partial | Partial | No | **Yes** | Yes | Manual |
| **Dark Mode** | Theme | Manual | Manual | **Built-in** | Manual | Manual |
| **Single Process** | Yes | Yes | Yes | **Yes** | No | Yes |
| **Community Size** | Huge | Large | Small | Growing | Growing | Small |
| **Production Ready** | Yes | Yes | Yes | **Yes** | Partial | Early |

---

## 2. Full-Stack Options

### 2.1 FastAPI + React/Next.js

**When to choose**: Team of 2+, need pixel-perfect custom UI, complex client-side state, eventually going to market as a product.

- **Backend**: FastAPI (Python) — async, fast, auto-generated OpenAPI docs
- **Frontend**: React + Next.js + Tailwind + shadcn/ui
- **Maps**: react-leaflet or react-map-gl (Mapbox)
- **Tables**: TanStack Table or AG Grid React
- **Charts**: Recharts, Nivo, or Tremor
- **Effort**: 3-5x more than NiceGUI for same features
- **Advantage**: Unlimited UI customization, better performance at scale

### 2.2 FastAPI + Svelte/SvelteKit

**When to choose**: Solo dev who knows Svelte, want lighter framework than React.

- Svelte compiles away — smaller bundles, faster runtime
- Less ecosystem than React but growing fast
- SvelteKit handles routing, SSR, data loading

### 2.3 Django + HTMX

**When to choose**: Need robust ORM, admin panel, user auth out of the box.

- Django's admin panel is free — great for data management
- HTMX adds interactivity without JavaScript framework
- Mature, battle-tested, huge ecosystem
- Heavier than needed for a single-user internal tool

### 2.4 Flask + Alpine.js

**When to choose**: Want minimal framework, maximum control.

- Lightweight — Flask is micro, Alpine.js is 15KB
- Good for simple tools, overkill for complex dashboards
- Need to build everything from scratch

### When Full-Stack vs. Python Framework?

| Scenario | Choose | Why |
|----------|--------|-----|
| Solo dev, internal tool | **NiceGUI** | Fastest to production, beautiful out of box |
| Going to market as product | **FastAPI + React** | Need custom branding, performance, scale |
| Team of 3+ devs | **FastAPI + React** | Frontend/backend separation, parallel work |
| Prototype/MVP first | **NiceGUI** | Build fast, validate ideas, migrate later if needed |
| Heavy geospatial focus | **NiceGUI or Dash** | Native map support, less integration work |
| ML/AI-heavy with UI | **Streamlit** | Quickest path, good enough UI |

---

## 3. Real Estate Dashboard Design Patterns

### 3.1 KPI Cards (Top Row)

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  🔥 12      │ │  📈 $2.4M   │ │  ✅ 23%     │ │  📋 47      │
│  Hot Leads  │ │  Pipeline   │ │  Conversion │ │  Total Leads│
│  ▲ 3 today  │ │  ▲ $400K    │ │  ▲ 2.1%     │ │  ▲ 8 new    │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

Each card shows: metric value, label, trend indicator (up/down + delta).

### 3.2 Lead Pipeline / Kanban

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ NEW (12) │ │CONTACTED │ │ MEETING  │ │ LISTING  │ │ CLOSED   │
│          │ │   (8)    │ │  SET (4) │ │ SIGNED(2)│ │   (1)    │
│ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │
│ │Lead 1│ │ │ │Lead 5│ │ │ │Lead 9│ │ │ │Ld 11 │ │ │ │Ld 13 │ │
│ │ S-Hot│ │ │ │A-High│ │ │ │A-High│ │ │ │B-Warm│ │ │ │ SOLD │ │
│ └──────┘ │ │ └──────┘ │ │ └──────┘ │ │ └──────┘ │ │ └──────┘ │
│ ┌──────┐ │ │ ┌──────┐ │ │          │ │          │ │          │
│ │Lead 2│ │ │ │Lead 6│ │ │          │ │          │ │          │
│ │ S-Hot│ │ │ │B-Warm│ │ │          │ │          │ │          │
│ └──────┘ │ │ └──────┘ │ │          │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### 3.3 Map + List Hybrid (Split Pane)

```
┌──────────────────────────┬──────────────────────┐
│                          │  Lead List            │
│      Interactive Map     │  ┌──────────────────┐ │
│                          │  │ 123 Main St      │ │
│   [pin] [pin]            │  │ Score: 87 (S-Hot)│ │
│          [pin]           │  │ Signals: 3       │ │
│     [pin]                │  │ [Call] [CMA]     │ │
│              [pin]       │  └──────────────────┘ │
│                          │  ┌──────────────────┐ │
│   [cluster: 5]           │  │ 456 Oak Ave      │ │
│                          │  │ Score: 72 (A)    │ │
│                          │  │ Signals: 2       │ │
│                          │  │ [Call] [CMA]     │ │
│  ┌─────────────────┐     │  └──────────────────┘ │
│  │ Layers: □Heat   │     │                       │
│  │ □Scores □Signals│     │  Showing 47 leads     │
│  └─────────────────┘     │  Sort: Score ▼        │
└──────────────────────────┴──────────────────────┘
```

### 3.4 Lead Detail Panel with Signal Stacking

```
┌──────────────────────────────────────────────────┐
│  123 Main Street, Phoenix AZ 85281               │
│  Score: 87/100 (S-Tier — HOT)    ████████░░      │
├──────────────────────────────────────────────────┤
│  SIGNALS DETECTED:                               │
│  ┌────────────────┐ ┌──────────────────┐         │
│  │ 🔴 Expired     │ │ 🟡 Pre-Foreclosure│        │
│  │ +15 pts        │ │ +20 pts           │        │
│  │ Expired 3 days │ │ NOD filed 2/15    │        │
│  └────────────────┘ └──────────────────┘         │
│  ┌────────────────┐ ┌──────────────────┐         │
│  │ 🟠 Absentee    │ │ 🔵 High DOM      │        │
│  │ +8 pts         │ │ +10 pts          │         │
│  │ Owner in CA    │ │ 142 days         │         │
│  └────────────────┘ └──────────────────┘         │
├──────────────────────────────────────────────────┤
│  Property: 3bd/2ba, 1,850 sqft, Built 1998      │
│  List Price: $425,000 → $399,000 → $379,000     │
│  Est. Value: $410,000  |  Equity: ~$180,000      │
├──────────────────────────────────────────────────┤
│  [📞 Call Owner]  [📧 Send CMA]  [📋 Add to CRM]│
└──────────────────────────────────────────────────┘
```

### 3.5 Alert / Notification Feed

```
┌──────────────────────────────────────────────────┐
│  🔔 Recent Alerts                     View All → │
├──────────────────────────────────────────────────┤
│  🔴 2 min ago — NEW S-TIER LEAD                  │
│     789 Elm St scored 92 (Expired + Foreclosure) │
│     [View] [Call Now]                            │
├──────────────────────────────────────────────────┤
│  🟡 1 hr ago — Score Change                      │
│     456 Oak Ave: 58 → 71 (new price reduction)   │
│     [View]                                       │
├──────────────────────────────────────────────────┤
│  🔵 3 hrs ago — Market Alert                     │
│     5 new expireds in 85281 this morning         │
│     [View List]                                  │
└──────────────────────────────────────────────────┘
```

---

## 4. Map & Geospatial Libraries

### 4.1 Leaflet

- **Type**: Open-source JavaScript map library
- **Pros**: Free, lightweight (42KB), huge plugin ecosystem, easy to use
- **Cons**: Less visually polished than Mapbox, no 3D, basic vector tiles
- **NiceGUI Integration**: Native `ui.leaflet()` — first-class support
- **Best For**: TheLeadEdge — free, great for property markers, heat maps, boundaries
- **Plugins**: Leaflet.heat (heat maps), Leaflet.markercluster (clustering), Leaflet.draw (drawing)

### 4.2 Mapbox GL JS

- **Type**: Commercial map platform with generous free tier (50K loads/month)
- **Pros**: Beautiful vector maps, 3D buildings, smooth animations, custom styles
- **Cons**: Requires API key, costs at scale, proprietary
- **NiceGUI Integration**: Via custom JavaScript element or iframe
- **Best For**: Production apps needing beautiful, customized maps

### 4.3 deck.gl

- **Type**: WebGL-powered large-scale data visualization by Uber
- **Pros**: Handles millions of data points, beautiful 3D effects, GPU-accelerated
- **Cons**: Complex API, overkill for hundreds of leads, heavy bundle
- **NiceGUI Integration**: Via `pydeck` wrapper
- **Best For**: Large-scale geospatial analysis (10K+ points), 3D visualization

### 4.4 Folium

- **Type**: Python wrapper for Leaflet
- **Pros**: Pure Python API, generates standalone HTML, easy choropleth
- **Cons**: Static output (no real-time updates), generates HTML files
- **NiceGUI Integration**: Embed via `ui.html()`
- **Best For**: Static map generation, reports, email embeds

### 4.5 Kepler.gl

- **Type**: Uber's geospatial analysis tool
- **Pros**: Beautiful out-of-box, powerful filtering, GPU-rendered
- **Cons**: Designed for data exploration not apps, heavy, limited programmatic control
- **NiceGUI Integration**: Limited — better suited for standalone analysis
- **Best For**: One-off geospatial analysis, not embedded dashboards

### 4.6 pydeck

- **Type**: Python bindings for deck.gl
- **Pros**: Python API for deck.gl, good Streamlit integration
- **Cons**: Same complexity as deck.gl, limited interactivity
- **NiceGUI Integration**: Via custom element
- **Best For**: Streamlit-based map visualizations

### Map Library Recommendation for TheLeadEdge

**Primary: Leaflet** (via NiceGUI's native `ui.leaflet`)
- Free, no API key needed
- Native NiceGUI support — markers, popups, layers, events all in Python
- Leaflet.heat plugin for heat maps
- MarkerCluster plugin for dense areas
- Neighborhood boundaries via GeoJSON overlays

**Optional upgrade: Mapbox** for production polish if needed later.

---

## 5. Real-Time & Notification Features

### 5.1 WebSocket Support by Framework

| Framework | WebSocket Support | Push from Server | Implementation |
|-----------|------------------|-----------------|----------------|
| Streamlit | No (polling only) | No | `st.experimental_rerun` + timer |
| Dash | Partial | Via extensions | `dash-extensions` WebSocket |
| Panel | Yes (Bokeh server) | Yes | Native via Tornado |
| **NiceGUI** | **Yes (native)** | **Yes** | **Built into architecture** |
| Reflex | Yes | Yes | State sync via WebSocket |
| FastHTML | Yes (HTMX SSE) | Yes | HTMX SSE extension |

### 5.2 Morning Briefing Pattern

```python
# NiceGUI morning briefing auto-generation
from nicegui import ui
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=6, minute=30)
async def generate_morning_briefing():
    """Runs at 6:30 AM daily — generates briefing before Realtor wakes up"""
    new_expireds = await fetch_new_expireds(last_24_hours=True)
    price_reductions = await fetch_price_reductions(min_reductions=3)
    score_changes = await detect_score_changes()
    hot_leads = await get_leads_by_tier('S')

    briefing = {
        'date': today(),
        'new_expireds': new_expireds,
        'price_reductions': price_reductions,
        'score_changes': score_changes,
        'hot_leads': hot_leads,
        'action_items': prioritize_actions(hot_leads)
    }

    await save_briefing(briefing)
    await send_notification('Morning briefing ready!')
```

### 5.3 Real-Time Lead Alerts (NiceGUI)

```python
# Server push — notify dashboard when new hot lead detected
async def on_new_lead_scored(lead):
    if lead.score >= 80:  # S-tier
        # Push notification to all connected clients
        ui.notify(
            f'🔥 New S-Tier Lead: {lead.address} (Score: {lead.score})',
            type='warning',
            position='top-right',
            timeout=0  # Persist until dismissed
        )
```

### 5.4 Auto-Refresh Patterns

- **Dashboard KPIs**: Refresh every 5 minutes via `ui.timer(300, refresh_kpis)`
- **Lead list**: Refresh on tab focus or manual pull-to-refresh
- **Map markers**: Update in real-time when new leads scored
- **Notification feed**: WebSocket push — instant

---

## 6. Deployment Options

### 6.1 Local Server (Recommended for Start)

- **Setup**: `python main.py` — NiceGUI runs on `localhost:8080`
- **Cost**: $0
- **Pros**: Zero deployment complexity, fast iteration, full data privacy
- **Cons**: Only accessible on local network, no mobile access outside home
- **LAN access**: Set `ui.run(host='0.0.0.0')` — accessible from the Realtor's phone on same WiFi

### 6.2 Docker

- **Setup**: Single `Dockerfile`, `docker compose up`
- **Cost**: $0 locally, $5-20/mo on cloud
- **Pros**: Reproducible, easy to move between machines, includes database
- **Cons**: Docker knowledge required, slightly more complex local dev

### 6.3 Cloud Hosting

| Provider | Cost | Pros | Cons |
|----------|------|------|------|
| **Railway** | $5-20/mo | Easy deploy, auto-scaling, PostgreSQL addon | Newer platform |
| **Render** | $7-25/mo | Good free tier, managed PostgreSQL, auto-deploy from Git | Cold starts on free tier |
| **Fly.io** | $5-15/mo | Edge deployment, persistent volumes, global CDN | CLI-focused, steeper learning |
| **Hetzner VPS** | €4-8/mo | Cheapest, full control, European privacy | Self-managed, manual setup |
| **DigitalOcean** | $6-24/mo | Droplets or App Platform, managed DB | More expensive for what you get |

### 6.4 Desktop App Wrapping

| Wrapper | Bundle Size | Native Feel | Effort |
|---------|-------------|-------------|--------|
| **PyWebView** | Small (~5MB) | Good (native webview) | Low — just wraps NiceGUI |
| **Tauri** | Very small (~3MB) | Excellent | Medium — Rust-based |
| **Electron** | Large (~150MB) | Good | Medium — Node.js required |

**Recommendation**: Start local, add Docker when stable, deploy to Railway or Render when mobile access needed.

---

## 7. Final Recommendation

### Primary Framework: NiceGUI

**Why NiceGUI wins for TheLeadEdge:**

1. **Best visual quality** — Material Design (Quasar) + Tailwind CSS = professional without CSS expertise
2. **Native maps** — `ui.leaflet()` with markers, popups, heat maps, clustering
3. **Native data tables** — `ui.aggrid()` with sorting, filtering, pagination, row selection
4. **Real-time push** — WebSocket built into architecture, server can push to all clients
5. **Single Python process** — no frontend build, no npm, no webpack, no React
6. **FastAPI under the hood** — add REST API endpoints alongside dashboard
7. **Dark mode** — one toggle, Quasar handles everything
8. **Active development** — frequent releases, responsive maintainer on GitHub

### Recommended Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | NiceGUI 2.x | Dashboard UI |
| **Maps** | Leaflet (via `ui.leaflet`) | Property mapping, heat maps |
| **Tables** | AG Grid (via `ui.aggrid`) | Lead lists, sortable/filterable |
| **Charts** | ECharts (via `ui.echart`) | Trends, funnels, gauges |
| **Database** | SQLite → PostgreSQL | Lead storage, scoring history |
| **ORM** | SQLModel (SQLAlchemy + Pydantic) | Type-safe database access |
| **Scheduling** | APScheduler | Morning briefing, data refresh |
| **HTTP Client** | httpx (async) | API calls to MLS, ATTOM, etc. |
| **Geocoding** | Nominatim (free) or Mapbox | Address → coordinates |
| **Auth** | NiceGUI built-in auth | Dashboard login |
| **Deployment** | Local → Docker → Railway | Progressive deployment |

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    NiceGUI App                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Morning  │  │ Lead     │  │ Map View         │  │
│  │ Briefing │  │ Pipeline │  │ (Leaflet)        │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │              │                 │             │
│  ┌────┴──────────────┴─────────────────┴──────────┐ │
│  │              FastAPI Backend                     │ │
│  │  ┌──────────┐ ┌───────────┐ ┌───────────────┐  │ │
│  │  │ Scoring  │ │ Data Sync │ │ Notifications │  │ │
│  │  │ Engine   │ │ Service   │ │ Service       │  │ │
│  │  └────┬─────┘ └─────┬─────┘ └───────┬───────┘  │ │
│  └───────┼─────────────┼───────────────┼───────────┘ │
│          │             │               │             │
│  ┌───────┴─────────────┴───────────────┴──────────┐ │
│  │              SQLite / PostgreSQL                 │ │
│  │  Properties | Leads | Signals | Scores | History│ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
         │              │               │
    ┌────┴────┐   ┌─────┴─────┐   ┌────┴─────┐
    │ MLS API │   │ ATTOM API │   │ County   │
    │ (RESO)  │   │           │   │ Records  │
    └─────────┘   └───────────┘   └──────────┘
```

### Development Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Skeleton | Week 1 | NiceGUI app running, page routing, auth, dark mode |
| 2. Database | Week 2 | Schema, models, seed data, CRUD operations |
| 3. Lead List | Week 3 | AG Grid table, filtering, sorting, lead detail panel |
| 4. Map View | Week 4 | Leaflet map, property markers, popups, clustering |
| 5. Scoring | Week 5 | Scoring engine, signal stacking display, tier badges |
| 6. Morning Briefing | Week 6 | Auto-generated daily view, KPI cards, action items |
| 7. Data Pipeline | Week 7-8 | MLS sync, public records, scheduled jobs |
| 8. Polish | Week 9-10 | Mobile responsive, notifications, CRM integration |

### Starter Code Example

```python
from nicegui import ui, app
from datetime import datetime

# Dark mode toggle
dark = ui.dark_mode()

@ui.page('/')
async def dashboard():
    with ui.header().classes('bg-blue-900 text-white'):
        ui.label('TheLeadEdge').classes('text-2xl font-bold')
        ui.space()
        ui.label(datetime.now().strftime('%B %d, %Y'))
        ui.switch('Dark Mode', on_change=dark.toggle)

    # KPI Cards Row
    with ui.row().classes('w-full gap-4 p-4'):
        for title, value, delta in [
            ('Hot Leads', '12', '▲ 3 today'),
            ('Pipeline', '$2.4M', '▲ $400K'),
            ('Conversion', '23%', '▲ 2.1%'),
            ('Total Leads', '47', '▲ 8 new'),
        ]:
            with ui.card().classes('flex-1'):
                ui.label(value).classes('text-3xl font-bold')
                ui.label(title).classes('text-gray-500')
                ui.label(delta).classes('text-green-500 text-sm')

    # Map + Lead List Split
    with ui.row().classes('w-full gap-4 p-4'):
        with ui.card().classes('flex-1'):
            m = ui.leaflet(center=(33.4484, -112.0740), zoom=11)
            m.classes('h-96')
            m.marker(latlng=(33.45, -112.07))

        with ui.card().classes('flex-1'):
            ui.aggrid({
                'columnDefs': [
                    {'field': 'address', 'headerName': 'Address'},
                    {'field': 'score', 'headerName': 'Score', 'sort': 'desc'},
                    {'field': 'tier', 'headerName': 'Tier'},
                    {'field': 'signals', 'headerName': 'Signals'},
                ],
                'rowData': [
                    {'address': '123 Main St', 'score': 87, 'tier': 'S-Hot', 'signals': 3},
                    {'address': '456 Oak Ave', 'score': 72, 'tier': 'A-High', 'signals': 2},
                    {'address': '789 Elm Dr', 'score': 58, 'tier': 'B-Warm', 'signals': 2},
                ],
            }).classes('h-96')

ui.run(title='TheLeadEdge', port=8080)
```

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| NiceGUI is relatively new | Active development, MIT license, can fork if abandoned |
| ECharts less known than Plotly | ECharts is actually more popular globally, excellent docs |
| Leaflet less polished than Mapbox | Free tile providers (CartoDB, Stamen) look great, upgrade to Mapbox later if needed |
| Single Python process scalability | More than sufficient for single-user internal tool |
| Learning curve for Quasar/Tailwind | NiceGUI abstracts most of it — Python API handles 90% of needs |

---

*This research recommends NiceGUI as the primary framework for TheLeadEdge based on visual quality, native map/table support, real-time capabilities, and developer productivity for a solo developer building an internal tool.*
