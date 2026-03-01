# Dashboard UI/UX Design Research

> **Project**: LeadFinder — Real Estate Lead Generation Dashboard
> **Created**: 2026-02-28
> **Purpose**: Design patterns, color systems, and UX principles for a Realtor-facing dashboard

---

## 1. Real Estate Dashboard Design Inspiration

### 1.1 Existing PropTech UI Patterns

**KVCore / Inside Real Estate**
- Clean card-based layout for leads
- Activity timeline showing lead engagement (page views, favorites, searches)
- Smart suggestions for follow-up timing
- What works: Behavioral tracking visualization, clean timeline
- What's missing: No signal stacking, no motivation scoring, no urgency visualization

**BoomTown**
- Lead categorization (Hot, Warm, Watch, Archive)
- Engagement scoring based on website activity
- Automatic lead routing and assignment
- What works: Simple tier system, action-oriented interface
- What's missing: No multi-source signals, no market context, purely online-activity-based

**Zillow Premier Agent / Flex**
- Connection-style lead delivery with accept/decline
- Lead quality indicators (timeline, budget, pre-approval)
- Simple "interested / not interested" workflow
- What works: Forced quick action (respond in 5 minutes), simple UX
- What's missing: No scoring transparency, no signal details, one-dimensional leads

**Follow Up Boss**
- Clean contact management with tagging
- Call/text/email directly from interface
- Smart Lists with saved filters
- What works: Best CRM integration, fast actions, great API
- What's missing: No property intelligence, no public records, no map visualization

**HubSpot (Non-RE but excellent UX)**
- Deal pipeline with drag-and-drop Kanban
- Contact timeline with all touchpoints
- Dashboard widgets with drag-and-drop customization
- What works: Best-in-class pipeline visualization, clean data density
- What to borrow: Pipeline design, activity timeline, dashboard composition

### 1.2 Critical Gaps in Existing Tools

| Gap | What's Missing | LeadFinder Opportunity |
|-----|---------------|----------------------|
| Signal Stacking Visualization | No tool shows WHY a lead is hot | Visual signal badges with point values |
| Morning Briefing | No tool generates a daily action summary | Auto-generated morning view |
| Motivation Scoring | Basic engagement scoring only | Multi-source motivation scoring with urgency decay |
| Map + Signals | Maps show properties, not intelligence | Overlay signals, scores, and tiers on map |
| Price History Visualization | Static price display | Sparklines showing reduction velocity |
| Urgency Decay | No time-based score adjustment | Visual countdown/freshness indicators |

---

## 2. Color Schemes & Visual Design

### 2.1 Primary Color Palette

```
Brand Colors:
  Primary Blue:    #1E3A5F (dark navy — trust, professionalism)
  Primary Light:   #3B82F6 (bright blue — interactive elements)
  Accent:          #10B981 (emerald green — positive metrics, growth)
  Background:      #F8FAFC (off-white — light mode)
  Surface:         #FFFFFF (white — cards, panels)
  Text Primary:    #0F172A (near-black — headings)
  Text Secondary:  #64748B (gray — labels, descriptions)
  Text Muted:      #94A3B8 (light gray — timestamps, metadata)
  Border:          #E2E8F0 (subtle gray — card borders, dividers)
```

### 2.2 Lead Tier Color System

```
S-Tier (Hot):      #EF4444  (Red 500)     — bg: #FEF2F2  — Immediate action
A-Tier (High):     #F97316  (Orange 500)   — bg: #FFF7ED  — Priority follow-up
B-Tier (Warm):     #EAB308  (Yellow 500)   — bg: #FEFCE8  — Scheduled outreach
C-Tier (Nurture):  #3B82F6  (Blue 500)     — bg: #EFF6FF  — Drip campaign
D-Tier (Watch):    #6B7280  (Gray 500)     — bg: #F9FAFB  — Monitor only
```

### 2.3 Signal Type Colors

```
MLS Signals:       #8B5CF6  (Purple 500)   — Expired, price drop, DOM, withdrawn
Public Records:    #EC4899  (Pink 500)     — Foreclosure, probate, divorce, tax
Life Events:       #06B6D4  (Cyan 500)     — Job change, retirement, inheritance
Market Signals:    #F59E0B  (Amber 500)    — Neighborhood trend, comp gap, investor
Digital Signals:   #10B981  (Emerald 500)  — Zillow activity, FSBO, online search
```

### 2.4 Status & Feedback Colors

```
Success:           #22C55E  (Green 500)    — Completed actions, positive trends
Warning:           #F59E0B  (Amber 500)    — Score changes, approaching thresholds
Error:             #EF4444  (Red 500)      — Failed actions, expired leads
Info:              #3B82F6  (Blue 500)     — New data, informational alerts
```

### 2.5 Dark Mode Palette

```
Background:        #0F172A  (Slate 900)
Surface:           #1E293B  (Slate 800)
Surface Elevated:  #334155  (Slate 700)
Text Primary:      #F1F5F9  (Slate 100)
Text Secondary:    #94A3B8  (Slate 400)
Border:            #334155  (Slate 700)
```

Tier colors stay the same in dark mode — they pop against dark backgrounds.

### 2.6 Typography

```
UI Font:           Inter (or system-ui fallback)
  - Headings:      Inter 600 (Semi-Bold)
  - Body:          Inter 400 (Regular)
  - Labels:        Inter 500 (Medium), uppercase, tracking-wide

Data Font:         JetBrains Mono (or monospace fallback)
  - Scores:        JetBrains Mono 700 (Bold)
  - Prices:        JetBrains Mono 500 (Medium)
  - Addresses:     Inter 500 (Medium) — NOT monospace

Size Scale:
  - KPI Value:     text-4xl (36px) — large dashboard numbers
  - Page Title:    text-2xl (24px)
  - Card Title:    text-lg (18px)
  - Body:          text-sm (14px) — default for dense data
  - Caption:       text-xs (12px) — timestamps, metadata
```

### 2.7 Number Formatting Rules

```
Prices:        $425,000  (comma-separated, no decimals for whole dollars)
Percentages:   23.4%     (one decimal)
Scores:        87        (no decimals, no leading zeros)
Counts:        12        (plain number for small), 1.2K (abbreviated for 1000+)
Dates:         Feb 28    (short), February 28, 2026 (full)
Relative Time: 2h ago, 3d ago, 2w ago (abbreviated)
Phone:         (602) 555-1234 (standard US format)
```

---

## 3. Dashboard Layout Patterns

### 3.1 Morning Briefing View (Default Landing Page)

This is what the Realtor sees when they open LeadFinder at 7am:

```
┌──────────────────────────────────────────────────────────────────┐
│  LeadFinder          Good morning, Sarah!     Feb 28, 2026  🌓  │
│  [Briefing] [Leads] [Map] [Pipeline] [Analytics]                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐│
│  │ 🔥 5        │ │ 📥 12       │ │ 💰 $2.4M    │ │ ✅ 23%     ││
│  │ Hot Leads   │ │ New Today   │ │ Pipeline    │ │ Conv. Rate ││
│  │ ▲2 vs yday  │ │ ▲4 vs avg  │ │ ▲$400K      │ │ ▲2.1%      ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘│
│                                                                  │
│  TODAY'S PRIORITY ACTIONS                              5 items   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ ● 🔴 Call 123 Main St owner — Expired yesterday, Score: 92  ││
│  │   Pre-foreclosure + expired + absentee   [📞 Call] [📋 CMA] ││
│  ├──────────────────────────────────────────────────────────────┤│
│  │ ● 🟠 Follow up 456 Oak Ave — 3rd price reduction today      ││
│  │   Price: $425K → $399K → $379K, DOM: 142  [📞 Call] [📧]   ││
│  ├──────────────────────────────────────────────────────────────┤│
│  │ ● 🟠 Send CMA to 789 Elm Dr — Expired 3 days, no new agent ││
│  │   Est value: $340K, Last list: $315K       [📋 CMA] [📧]   ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────┐ ┌──────────────────────────────┐│
│  │ NEW LEADS TODAY        12   │ │ SCORE CHANGES                ││
│  │                             │ │                              ││
│  │ 🔴 S-Tier: 2               │ │ ▲ 456 Oak: 58→71 (+13)     ││
│  │ 🟠 A-Tier: 3               │ │ ▲ 321 Pine: 42→55 (+13)    ││
│  │ 🟡 B-Tier: 4               │ │ ▼ 654 Maple: 67→52 (-15)   ││
│  │ 🔵 C-Tier: 3               │ │   (listing went pending)     ││
│  │                             │ │                              ││
│  │ [View All New Leads →]      │ │ [View All Changes →]         ││
│  └─────────────────────────────┘ └──────────────────────────────┘│
│                                                                  │
│  MARKET PULSE                                                    │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ Expireds this week: 23 (▲15% vs last week)                  ││
│  │ Avg DOM in 85281: 67 days (▲8 days vs last month)           ││
│  │ New price reductions: 31 (▲22% vs last week)                ││
│  └──────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Signal Stacking Indicators

Visual badges showing WHY a lead scored high — the key differentiator:

```
Signal Badge Design:
┌──────────────────┐
│ 🏠 EXPIRED  +15  │  ← Icon + label + point value
│ 3 days ago       │  ← Context
└──────────────────┘

Compact Badge (for lists):
[🔴 Expired +15] [🟡 Pre-Foreclosure +20] [🟠 Absentee +8]

Signal Stack Summary:
Score: 87 ████████░░  S-Tier
├── 🔴 Expired listing (+15) — 3 days ago
├── 🟡 Pre-foreclosure NOD (+20) — filed Feb 15
├── 🟠 Absentee owner (+8) — owner in California
├── 🔵 High DOM (+10) — 142 days on market
└── 🟢 Freshness bonus (×1.5) — detected 2 hours ago
```

### 3.3 Property Card Designs

**Compact Card (List View)**:
```
┌──────────────────────────────────────────────────────┐
│ 87 │ 123 Main Street, Phoenix AZ     │ $379,000     │
│ S  │ 3bd/2ba · 1,850sf · Built 1998  │ ▼ from $425K │
│    │ [Expired] [Pre-Forecl] [Absent] │ DOM: 142     │
│    │                          [📞] [📋] [📧] [···] │
└──────────────────────────────────────────────────────┘
```

**Expanded Card (Detail View)**:
```
┌──────────────────────────────────────────────────────┐
│                    [Property Photo]                   │
│  ┌────┐                                              │
│  │ 87 │  123 Main Street, Phoenix AZ 85281           │
│  │ S  │  3 bed · 2 bath · 1,850 sqft · Built 1998   │
│  └────┘                                              │
├──────────────────────────────────────────────────────┤
│  Price History        ─╲_╱─╲___  ($425K → $379K)    │
│  Est. Value: $410,000   Equity: ~$180,000            │
├──────────────────────────────────────────────────────┤
│  SIGNALS (4 detected)                                │
│  [🔴 Expired +15] [🟡 Pre-Forecl +20]               │
│  [🟠 Absentee +8] [🔵 High DOM +10]                 │
├──────────────────────────────────────────────────────┤
│  Owner: John Smith · (602) 555-1234                  │
│  Owner Address: 456 Sunset Blvd, Los Angeles CA      │
├──────────────────────────────────────────────────────┤
│  ACTIVITY                                            │
│  Feb 28 — Lead detected, scored 87 (S-Tier)          │
│  Feb 25 — 3rd price reduction ($399K → $379K)        │
│  Feb 15 — NOD filed (pre-foreclosure)                │
│  Jan 15 — Listed at $425,000                         │
├──────────────────────────────────────────────────────┤
│  [📞 Call Owner]  [📋 Send CMA]  [📧 Email]  [+ CRM]│
└──────────────────────────────────────────────────────┘
```

**Mobile Card**:
```
┌────────────────────────────┐
│ 87  123 Main St       $379K│
│  S  3/2 · 1,850sf         │
│ [Expired] [Forecl] [Abs]  │
│ [📞 Call]  [📋 CMA]       │
└────────────────────────────┘
```

### 3.4 Map + List Split Pane

```
┌────────────────────────────┬───────────────────────┐
│                            │ Sort: Score ▼  Filter │
│     Interactive Map        │ ┌───────────────────┐ │
│                            │ │ 87 S 123 Main St  │◄── Selected
│   🔴 🟠                    │ │    $379K  DOM:142  │    (highlighted
│        🟠                  │ │    [Exp][Fore][Ab] │     on map too)
│   🟡        🔴             │ └───────────────────┘ │
│      🔵  🟡                │ ┌───────────────────┐ │
│                            │ │ 72 A 456 Oak Ave  │ │
│   Layers:                  │ │    $525K  DOM:89   │ │
│   ☑ Lead Pins              │ │    [PriceRed][DOM] │ │
│   ☐ Heat Map               │ └───────────────────┘ │
│   ☐ Boundaries             │ ┌───────────────────┐ │
│   ☐ Sold Comps             │ │ 58 B 789 Elm Dr   │ │
│                            │ │    $315K  DOM:45   │ │
│                            │ │    [Expired]       │ │
│                            │ └───────────────────┘ │
│                            │                       │
│                            │ Showing 47 of 47      │
└────────────────────────────┴───────────────────────┘
```

Pin colors match tier: 🔴 S, 🟠 A, 🟡 B, 🔵 C, ⚪ D. Pin size scales with score.

### 3.5 Mobile Responsive Breakpoints

```
Desktop:  ≥1280px  — Full split-pane layout, all columns visible
Tablet:   768-1279px — Stacked layout, collapsible panels
Mobile:   <768px    — Single column, bottom tab navigation

Mobile Bottom Tab Bar:
┌──────┬──────┬──────┬──────┬──────┐
│  📊  │  📋  │  🗺️  │  🔔  │  ⚙️  │
│Brief │Leads │ Map  │Alert │ More │
└──────┴──────┴──────┴──────┴──────┘
```

---

## 4. Data Visualization Best Practices

### 4.1 Sparklines for Trend Indicators

Small inline charts showing trends without taking up space:

```
Price History:  ─╲_╱─╲___    ($425K → $379K, 3 reductions)
DOM Trend:      ___╱─────    (accelerating time on market)
Score History:  ─────╱╱      (score increasing — more signals)
Market Trend:   ╱╱╱──────    (market heating up, then flat)
```

Use in: KPI cards (delta sparkline), lead list (price trend column), market pulse.

### 4.2 Score Gauges

**Radial Gauge** (for lead detail panel):
```
      ╭───────╮
    ╱           ╲
   │      87     │    Color fills based on tier:
   │    S-Hot    │    0-19: Gray, 20-39: Blue,
    ╲           ╱     40-59: Yellow, 60-79: Orange,
      ╰───────╯      80-100: Red
```

**Linear Progress Bar** (for lead lists — more space-efficient):
```
Score: 87  ████████░░  S-Tier
Score: 72  ███████░░░  A-Tier
Score: 58  █████░░░░░  B-Tier
Score: 35  ███░░░░░░░  C-Tier
Score: 12  █░░░░░░░░░  D-Tier
```

### 4.3 Neighborhood Heat Maps

Six map layer types for different intelligence views:

| Layer | Visualization | Data Source | Color Scale |
|-------|--------------|-------------|-------------|
| Lead Density | Heat map gradient | Lead locations | Blue → Red (more leads) |
| Lead Score | Colored dots/bubbles | Lead scores | Green → Red (higher score) |
| Price Trends | Choropleth by ZIP | MLS sold data | Red → Green (appreciation) |
| DOM Average | Choropleth by area | MLS active data | Green → Red (longer DOM) |
| Expired Rate | Choropleth by ZIP | MLS expired data | Green → Red (more expireds) |
| Signal Density | Hex bins | Signal locations | Low → High density |

### 4.4 Activity Timeline

Vertical timeline for lead activity history:

```
│
├─● Feb 28, 8:02am — Lead detected & scored
│    Score: 87 (S-Tier) — 4 signals stacked
│
├─● Feb 25 — 3rd price reduction
│    $399,000 → $379,000 (-5.0%)
│    Score updated: 75 → 87 (+12)
│
├─● Feb 15 — NOD filed (pre-foreclosure)
│    County Recorder case #2026-1234
│    Score updated: 55 → 75 (+20)
│
├─● Jan 15 — Original listing
│    Listed at $425,000 with Agent Jane Doe
│    Agent historical expire rate: 34%
│
├─● Dec 10 — Tax delinquency flagged
│    2024 property tax unpaid ($3,200)
│
```

### 4.5 Conversion Funnel

```
                    ┌─────────────────────────────┐
   Leads Detected   │████████████████████████  247 │
                    └─────────────────────────────┘
                      ┌───────────────────────┐
   Contacted          │██████████████████  142 │  57%
                      └───────────────────────┘
                        ┌─────────────────┐
   Meeting Set          │████████████  63  │  44%
                        └─────────────────┘
                          ┌───────────┐
   Listing Signed         │████████ 28│  44%
                          └───────────┘
                            ┌──────┐
   Closed                   │███ 12│  43%
                            └──────┘

   Overall Conversion: 4.9%    Avg Commission: $12,400
   Total Revenue: $148,800     ROI: 24:1 vs tool cost
```

### 4.6 Before/After Comparison Cards

For showing impact of signal stacking:

```
┌─────────────────────┐    ┌─────────────────────┐
│  WITHOUT LeadFinder  │    │  WITH LeadFinder     │
│                      │    │                      │
│  Leads/month:   ~20  │ →  │  Leads/month:   ~80  │
│  S-Tier:         0   │    │  S-Tier:        12   │
│  Avg response:  48hr │    │  Avg response:  2hr  │
│  Conversion:    2%   │    │  Conversion:   8%    │
│  Commission:   $24K  │    │  Commission: $120K   │
└─────────────────────┘    └─────────────────────┘
```

---

## 5. Notification & Alert Design

### 5.1 Four-Tier Priority System

| Priority | Visual | Sound | Persistence | Example |
|----------|--------|-------|-------------|---------|
| **Critical** | Red banner, pulse animation | Alert chime | Until dismissed | New S-Tier lead with 80+ score |
| **High** | Orange toast, top-right | Soft chime | 30 seconds | Score jumped to A-Tier |
| **Medium** | Blue toast, top-right | None | 10 seconds | New price reduction detected |
| **Low** | Gray notification in feed | None | Feed only | Weekly market summary ready |

### 5.2 Toast Notification Specs

```
┌──────────────────────────────────────┐
│ 🔥 New S-Tier Lead                  │  Width: 380px
│                                      │  Position: top-right
│ 123 Main St scored 92               │  Animation: slide-in from right
│ Expired + Pre-Foreclosure + Absentee│  Border-left: 4px solid tier color
│                                      │  Shadow: lg
│ [View Lead]  [Call Now]   [Dismiss]  │  Timeout: 0 (critical = persist)
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ 📈 Score Change                      │  Timeout: 10s (medium priority)
│                                      │  Border-left: 4px solid blue
│ 456 Oak Ave: 58 → 71 (+13)          │
│ New signal: 3rd price reduction      │
│                                      │
│ [View]                    [Dismiss]  │
└──────────────────────────────────────┘
```

### 5.3 Daily Digest Email Layout

```
Subject: LeadFinder Morning Briefing — Feb 28, 2026

╔══════════════════════════════════════════════════╗
║  LEADFINDER MORNING BRIEFING                     ║
║  Friday, February 28, 2026                       ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  🔥 HOT LEADS REQUIRING ACTION                  ║
║                                                  ║
║  1. 123 Main St — Score: 92 (S-Tier)             ║
║     Expired + Pre-Foreclosure + Absentee         ║
║     Owner: John Smith · (602) 555-1234           ║
║     → CALL TODAY                                 ║
║                                                  ║
║  2. 456 Oak Ave — Score: 71 (A-Tier)             ║
║     3rd price reduction yesterday                ║
║     → SEND CMA                                   ║
║                                                  ║
║  📊 OVERNIGHT CHANGES                            ║
║  • 12 new leads detected (2 S-tier, 3 A-tier)   ║
║  • 5 score increases, 2 decreases                ║
║  • 3 new expireds in your target ZIPs            ║
║                                                  ║
║  [Open Dashboard →]                              ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

### 5.4 Badge & Counter Specifications

```
Navigation badges:
  [Leads 💀12]  ← Red badge for unread S/A-tier leads
  [Alerts 🔴5]  ← Red dot for unread critical alerts

Counter behavior:
  - Badge shows count of unactioned items
  - Clears when user views the item
  - Pulses (animation) for first 30 seconds after new critical item
  - Maximum display: "99+" for counts over 99
```

---

## 6. Component Libraries & Design Systems

### 6.1 Recommended Stack for NiceGUI

| Component | Library | Purpose |
|-----------|---------|---------|
| **CSS Framework** | Tailwind CSS (built into NiceGUI) | Utility-first styling |
| **UI Components** | Quasar (built into NiceGUI) | Material Design components |
| **Data Tables** | AG Grid (via `ui.aggrid`) | Sortable, filterable lead tables |
| **Charts** | ECharts (via `ui.echart`) | Gauges, funnels, sparklines, trends |
| **Maps** | Leaflet (via `ui.leaflet`) | Property maps, heat maps, clusters |
| **Icons** | Material Icons (Quasar built-in) | Action icons, status indicators |
| **Notifications** | `ui.notify()` (built-in) | Toast notifications |
| **Dialogs** | `ui.dialog()` (built-in) | Lead details, confirmation prompts |

### 6.2 Tailwind Custom Color Config

```python
# In NiceGUI, add custom Tailwind classes via ui.add_head_html
ui.add_head_html('''
<style>
  /* Lead Tier Colors */
  .tier-s { background-color: #FEF2F2; border-left: 4px solid #EF4444; }
  .tier-a { background-color: #FFF7ED; border-left: 4px solid #F97316; }
  .tier-b { background-color: #FEFCE8; border-left: 4px solid #EAB308; }
  .tier-c { background-color: #EFF6FF; border-left: 4px solid #3B82F6; }
  .tier-d { background-color: #F9FAFB; border-left: 4px solid #6B7280; }

  /* Signal Type Colors */
  .signal-mls { background-color: #F5F3FF; color: #7C3AED; }
  .signal-public { background-color: #FDF2F8; color: #DB2777; }
  .signal-life { background-color: #ECFEFF; color: #0891B2; }
  .signal-market { background-color: #FFFBEB; color: #D97706; }
  .signal-digital { background-color: #ECFDF5; color: #059669; }

  /* Score bar gradient */
  .score-bar { background: linear-gradient(90deg, #22C55E 0%, #EAB308 40%, #F97316 70%, #EF4444 100%); }
</style>
''')
```

### 6.3 NiceGUI Component Mapping to LeadFinder Features

| Feature | NiceGUI Component | Notes |
|---------|------------------|-------|
| KPI Cards | `ui.card()` + `ui.label()` | Tailwind classes for styling |
| Lead Table | `ui.aggrid()` | Column defs, row selection, custom cell renderers |
| Map | `ui.leaflet()` | Markers, popups, tile layers, GeoJSON |
| Score Gauge | `ui.echart()` | Gauge chart type |
| Pipeline Kanban | `ui.card()` + drag events | Custom implementation |
| Notifications | `ui.notify()` | Type, position, timeout configurable |
| Dialogs | `ui.dialog()` | Lead detail popups |
| Dark Mode | `ui.dark_mode()` | Built-in toggle |
| Navigation | `ui.tabs()` + `ui.tab_panels()` | Page routing |
| Search | `ui.input()` with autocomplete | Filter leads by address |
| Filters | `ui.select()`, `ui.checkbox()` | Tier, signal type, ZIP, date range |
| Timeline | `ui.timeline()` (Quasar) | Activity history |
| File Upload | `ui.upload()` | Import CSV leads |
| Download | `ui.download()` | Export lead lists |
| Auth | `app.storage.user` | Session-based authentication |

### 6.4 ECharts Chart Components for LeadFinder

| Chart Type | Use Case | ECharts Type |
|-----------|----------|-------------|
| Gauge | Lead score display | `gauge` |
| Line | Price history, market trends | `line` with area fill |
| Bar | Leads by source, weekly comparison | `bar` |
| Funnel | Conversion pipeline | `funnel` |
| Pie/Donut | Lead tier distribution | `pie` with radius |
| Scatter | Score vs. DOM correlation | `scatter` |
| Heatmap | Calendar view of lead activity | `heatmap` |
| Radar | Lead quality dimensions | `radar` |

---

## 7. Accessibility & Usability for Non-Technical Users

### 7.1 The "Sarah Test" — User Persona

```
Name:        Sarah (the Realtor wife)
Age:         35-45
Tech Level:  Comfortable with phone/tablet, uses Zillow, Instagram
Daily Tools: iPhone, MLS portal, Follow Up Boss, email, text
Pain Point:  Spends 2+ hours manually searching for leads
Goal:        Open dashboard → see what to do today → take action → close
Time Budget: 10-15 minutes per morning with the dashboard
```

**Every feature must pass the Sarah Test:**
- Can Sarah understand it in 3 seconds?
- Can Sarah take action in 1 click?
- Does Sarah need to learn anything to use it?

### 7.2 Jargon-to-Plain-Language Translation

| Technical Term | Dashboard Label | Why |
|---------------|----------------|-----|
| Lead Score | "Match Score" or "Priority" | Score implies judgment |
| Signal Stacking | "Why This Lead" | Explains the concept |
| Urgency Decay | "Freshness" with 🟢🟡🔴 | Visual, intuitive |
| DOM (Days on Market) | "Days Listed" | Plain English |
| NOD (Notice of Default) | "Pre-Foreclosure" | More descriptive |
| FSBO | "For Sale By Owner" | Spell it out |
| CMA | "Market Analysis" or "Home Value Report" | Client-friendly |
| Absentee Owner | "Out-of-Area Owner" | Clearer |
| Tier S/A/B/C/D | "Hot / High / Warm / Nurture / Watch" | Action-oriented labels |

### 7.3 One-Click Action Specs

```
Primary Actions (always visible on lead cards):
  [📞 Call]    → Opens phone dialer with owner number pre-filled
  [📋 CMA]    → Generates and sends Comparative Market Analysis
  [📧 Email]  → Opens email with pre-drafted outreach template

Secondary Actions (in "···" overflow menu):
  [+ CRM]     → Push lead to Follow Up Boss
  [📝 Note]   → Add a note to this lead
  [🔕 Snooze] → Hide for X days, re-surface later
  [❌ Pass]   → Mark as not interested, move to archive
```

### 7.4 Five-Item Navigation Structure

Keep navigation to 5 items maximum (the cognitive limit for quick scanning):

```
1. 📊 Briefing  — Morning briefing, KPIs, action items (DEFAULT)
2. 📋 Leads     — Full lead list with filters, search, sorting
3. 🗺️ Map       — Geographic view with layers and pins
4. 📈 Pipeline  — Kanban board of lead stages
5. ⚙️ Settings  — Preferences, integrations, account
```

Alerts/notifications accessible via bell icon 🔔 in header (not a main nav item).

### 7.5 Quick-Glance vs Deep-Dive Modes

**Quick-Glance (Morning Briefing)**:
- 10-second scan: KPI cards at top
- 30-second review: Priority action list
- 2-minute deep read: New leads, score changes, market pulse
- Total morning routine: 5-10 minutes

**Deep-Dive (Lead Research)**:
- Full lead detail panel with all signals
- Property history timeline
- Comparable sales view
- Neighborhood analytics
- Owner contact information and history

### 7.6 Loading & Empty States

```
Loading State:
┌──────────────────────────────────────┐
│  ┌────┐  ░░░░░░░░░░░░░░░░░░░░░░░░  │  Skeleton loading
│  │░░░░│  ░░░░░░░░░░░░░░░░           │  (pulsing gray blocks)
│  │░░░░│  ░░░░░░░░░░                 │
│  └────┘                              │
└──────────────────────────────────────┘

Empty State (No Leads Yet):
┌──────────────────────────────────────┐
│                                      │
│         🏠                           │
│   No leads found yet                 │
│                                      │
│   Leads will appear here once the    │
│   data pipeline starts running.      │
│                                      │
│   [Set Up Data Sources →]            │
│                                      │
└──────────────────────────────────────┘

Empty State (No Results for Filter):
┌──────────────────────────────────────┐
│                                      │
│         🔍                           │
│   No leads match your filters        │
│                                      │
│   Try adjusting your filters or      │
│   broadening your search area.       │
│                                      │
│   [Clear Filters]                    │
│                                      │
└──────────────────────────────────────┘
```

### 7.7 Onboarding Tooltip Patterns

First-time user experience — 5 tooltips max:

```
Step 1: "This is your morning briefing — check it every day for new leads"
Step 2: "Each lead has a score — higher means more likely to sell"
Step 3: "Colored badges show WHY a lead scored high"
Step 4: "Click Call or CMA to take action instantly"
Step 5: "Use the map to see leads in your target neighborhoods"

[Skip Tour]  [Next →]  (3 of 5)
```

---

## 8. Design Principles

1. **Action-First**: Every screen answers "what should I do right now?"
2. **Glanceable**: Key information visible in 3 seconds without scrolling
3. **Signal Transparency**: Always show WHY a lead scored high, not just the number
4. **One-Click Actions**: Call, CMA, and email should never be more than 1 click away
5. **Mobile-Ready**: Realtors are on the go — design for phone first, enhance for desktop
6. **Progressive Disclosure**: Simple by default, detailed on demand
7. **Consistent Color Language**: Red = hot/urgent, blue = informational, green = positive — everywhere

---

## 9. Phased Build Roadmap (UX Perspective)

| Phase | Focus | Key UX Deliverable |
|-------|-------|-------------------|
| 1 | Core Layout | Navigation, KPI cards, dark mode toggle, responsive shell |
| 2 | Lead List | AG Grid table, tier badges, signal badges, action buttons |
| 3 | Lead Detail | Full detail panel, signal stacking view, activity timeline |
| 4 | Morning Briefing | Auto-generated view, priority actions, score changes |
| 5 | Map View | Leaflet map, colored pins, popups, layer toggles |
| 6 | Pipeline | Kanban board, drag-and-drop, stage tracking |
| 7 | Notifications | Toast alerts, notification feed, daily digest email |
| 8 | Mobile Polish | Bottom tab bar, responsive cards, swipe actions |

---

## Appendix: Full Color Reference

```
BRAND
  Navy:          #1E3A5F    Primary brand color
  Blue:          #3B82F6    Interactive elements
  Emerald:       #10B981    Positive metrics

TIERS
  S-Hot:         #EF4444    bg: #FEF2F2
  A-High:        #F97316    bg: #FFF7ED
  B-Warm:        #EAB308    bg: #FEFCE8
  C-Nurture:     #3B82F6    bg: #EFF6FF
  D-Watch:       #6B7280    bg: #F9FAFB

SIGNALS
  MLS:           #8B5CF6    bg: #F5F3FF
  Public Rec:    #EC4899    bg: #FDF2F8
  Life Event:    #06B6D4    bg: #ECFEFF
  Market:        #F59E0B    bg: #FFFBEB
  Digital:       #10B981    bg: #ECFDF5

STATUS
  Success:       #22C55E
  Warning:       #F59E0B
  Error:         #EF4444
  Info:          #3B82F6

LIGHT MODE
  Background:    #F8FAFC
  Surface:       #FFFFFF
  Text:          #0F172A
  Text Muted:    #64748B
  Border:        #E2E8F0

DARK MODE
  Background:    #0F172A
  Surface:       #1E293B
  Text:          #F1F5F9
  Text Muted:    #94A3B8
  Border:        #334155
```

---

*This design system provides a comprehensive visual language for LeadFinder, optimized for a non-technical Realtor user who needs to quickly identify high-priority leads and take action.*
