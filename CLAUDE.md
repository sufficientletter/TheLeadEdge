# CLAUDE.md

YaniVision — Yani's data-driven real estate lead generation system. Build intelligent tools that mine MLS data, public records, and digital signals to find motivated sellers and buyers before competitors.

## Master Build Plan

The definitive build specification is `MASTER_BUILD_PLAN.md`. All implementation must conform to that document. Read it before writing any code.

## Workflow

@.claude/rules/workflow.md
@.claude/rules/code-authority.md

## Security

@.claude/rules/security.md

Write boundary: all agents confined to project root (directory containing this file).
- Project root — READ/WRITE
- `C:\ClaudeProjects\MoenTactical_PatternEngine\` — READ ONLY (sister project reference)
- `C:\ClaudeProjects\DAEMON\` — READ ONLY (sister project reference)

### Credential & PII Protection (ABSOLUTE LAW)
**NEVER commit API keys, MLS credentials, or client PII to git.**
**NEVER log or print client names, phone numbers, email addresses, or home addresses.**
**All secrets stored in `.env` files (gitignored).**
**MLS data files (CSV exports) stored in Data/ (gitignored).**
Exposure of MLS credentials = unauthorized access, potential license revocation.
Exposure of client PII = privacy violation, legal liability.
The cost of caution is zero. The cost of exposure is catastrophic.

## Git

@.claude/rules/git-conventions.md

## Logging

@.claude/rules/logging.md

## Project Context
- **User**: Husband building tools for Yani (Ianula), his Realtor wife
- **Key Asset**: Yani has full MLS access (Multiple Listing Service)
- **Goal**: Find high-probability leads through creative data mining, not traditional cold-calling
- **Philosophy**: Work smarter — use data patterns, public records, and MLS insights to identify motivated sellers/buyers before competitors
- **Division of Labor**: We build the intelligence layer. Yani handles all client contact.

## Architecture Overview

```
Layer 1: Data Ingestion
  ├─ Module 1: MLS CSV Import — Parse, validate, deduplicate MLS exports
  ├─ Module 2: Public Records — Pre-foreclosure, probate, tax, code violations
  └─ Module 3: Digital Signals — Google Alerts, market APIs, Zillow patterns

Layer 2: Signal Detection & Scoring
  ├─ Module 4: Signal Detector — Extract behavioral signals from listing data
  ├─ Module 5: Scoring Engine — Multi-signal weighted scoring with decay
  └─ Module 6: Lead Lifecycle — Track leads from detection through conversion

Layer 3: Output & Automation
  ├─ Module 7: Daily Briefing — Email digest of top-tier leads at 6:30 AM
  ├─ Module 8: Dashboard — NiceGUI web interface for lead management
  └─ Module 9: CRM Integration — Follow Up Boss sync, action plans

Layer 4: Intelligence (Future)
  ├─ Market Analysis: Neighborhood momentum, comp analysis
  ├─ Predictive: Likelihood-to-sell modeling
  └─ Optimization: A/B test scoring algorithms
```

## Build Phases

| Phase | Focus | Status |
|-------|-------|--------|
| 0 | Research & Planning (19,800+ lines of research) | COMPLETE |
| 1 | MVP — CSV import → scoring → daily briefing email | ACTIVE |
| 2 | Automated Pipeline — schedulers, public records | PLANNED |
| 3 | Dashboard — NiceGUI web interface | PLANNED |
| 4 | Integrations — CRM, RESO API | PLANNED |
| 5 | Intelligence Engine — predictive modeling | PLANNED |
| 6 | Optimization — A/B testing, refinement | PLANNED |

## Technology Stack

- **Language:** Python 3.11+
- **Web Framework:** NiceGUI (dashboard)
- **Data Validation:** Pydantic v2
- **Database:** SQLAlchemy 2.0 async + SQLite (MVP) → PostgreSQL (scale)
- **Scheduling:** APScheduler
- **HTTP Client:** httpx (async)
- **Logging:** structlog
- **Testing:** pytest, hypothesis
- **Email:** aiosmtplib
- **CRM:** Follow Up Boss API

## Repository Structure

```
CLAUDE.md                                # Project constitution (this file)
MASTER_BUILD_PLAN.md                     # Master build plan (7 phases)
.claude/
  settings.json                          # Team permissions, hooks
  rules/                                 # Modular rules (auto-loaded)
    workflow.md
    security.md
    code-authority.md
    git-conventions.md
    logging.md
  skills/                                # Custom slash commands
    session-start/SKILL.md               # Initialize work session
    journal/SKILL.md                     # Create/update journal entry
    delegate/SKILL.md                    # Delegate work to agents
    code-review/SKILL.md                 # Review code changes
    status/SKILL.md                      # Project status overview
    lead-pipeline/SKILL.md              # Lead pipeline status
    data-health/SKILL.md                # Data pipeline health check
    compliance-check/SKILL.md           # Compliance and security scan
  agents/                                # Native agent definitions
    team-lead/team-lead.md
    systems-architect/systems-architect.md
    mls-data-specialist/mls-data-specialist.md
    scoring-engine-architect/scoring-engine-architect.md
    compliance-specialist/compliance-specialist.md
    outreach-strategist/outreach-strategist.md
  hooks/                                 # PreToolUse hooks
    protect-files.sh
Research/                                # Research corpus (16 files, 19,800+ lines)
  MASTER_RESEARCH.md                     # Research index and summary
TeamLeadJournal/                         # Session journals
logs/                                    # Agent action logs
src/                                     # Source code (created during build)
  yanivision/
    ingestion/                           # Module 1-3: Data ingestion
    signals/                             # Module 4: Signal detection
    scoring/                             # Module 5: Scoring engine
    lifecycle/                           # Module 6: Lead lifecycle
    output/                              # Module 7: Daily briefing
    dashboard/                           # Module 8: NiceGUI dashboard
    integrations/                        # Module 9: CRM integration
tests/                                   # Test suite
Data/                                    # MLS exports, CSVs (gitignored)
Strategies/                              # Validated lead-finding strategies
Docs/                                    # User guides and playbooks
```

## Agent Architecture

All 6 native agents specify `model: claude-opus-4-6` (latest, most capable) and demand absolute maximum effort. All follow: Role, Responsibilities, Authority, Inputs, Outputs, Constraints, Logging.

**Code authority:** Only Systems Architect writes code. All other agents are advisory — they produce specifications, research, and recommendations.

| Agent | Domain | Purpose |
|-------|--------|---------|
| Team Lead | Coordination | User interface, delegation, journaling, decisions |
| Systems Architect | Implementation | Sole code authority, architecture, all technical work |
| MLS Data Specialist | MLS/RESO | Data schemas, field mapping, signal extraction |
| Scoring Engine Architect | Algorithms | Lead scoring, signal weights, decay functions |
| Compliance Specialist | Legal/Ethics | MLS ToS, DNC, CAN-SPAM, privacy, Fair Housing |
| Outreach Strategist | Messaging | Scripts, drip campaigns, CRM workflows, conversion |

## Key Research Areas (Completed)
1. **MLS Data Mining** — Expired listings, price reductions, DOM patterns, withdrawn/relisted
2. **Public Records** — Pre-foreclosure, probate, divorce, tax delinquency, code violations
3. **Lead Scoring** — Signal stacking, temporal decay, tier calibration
4. **Automation** — Pipeline scheduling, CRM integration, daily briefings
5. **Legal Compliance** — MLS ToS, DNC, CAN-SPAM, TCPA, CCPA, Fair Housing
6. **Outreach Strategy** — Scripts by lead type, drip campaigns, contact timing

## Non-Obvious Gotchas

- MLS CSV exports have inconsistent schemas across boards — normalize early
- MLS terms of service vary by board — check before automating anything
- DNC lists update monthly — build in regular refresh
- Pre-foreclosure timelines vary dramatically by state (30 days to 12+ months)
- Probate leads require maximum sensitivity — empathy first, always
- Price reduction signals decay fast — contact within 48 hours or lose the edge
- Expired listing agents are bombarded by competitors — differentiation is everything
- FSBO sellers have already decided against agents — lead with value, not pitch
- Scoring models need calibration data — track conversions from Day 1
- Yani's personal touch is the product — we just surface the right leads at the right time
- Never automate the human contact — automation finds leads, humans build relationships
