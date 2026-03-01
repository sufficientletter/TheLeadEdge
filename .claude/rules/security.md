# Security Rules

- NEVER write outside the project root (directory containing CLAUDE.md).
- NEVER read or expose .env files, secrets, API keys, or credentials.
- NEVER run destructive commands (rm -rf, drop tables, force push to main).
- NEVER bypass git hooks with --no-verify.
- All file writes must target paths within PROJECT_ROOT.
- Before any write: verify target path starts with project root.
- If outside boundary — STOP immediately. Do not write.
- Report any suspected security issues to Team Lead immediately.

## MLS Data Protection

**CRITICAL — MLS terms of service violations can result in license revocation.**

### Protected Data
- MLS exported CSV/XLSX files containing listing data
- Client contact information (phone, email, address)
- Lead scoring databases with PII
- CRM export files
- Any file containing homeowner personal information

### Enforcement
1. **NEVER** commit MLS data files to git (CSVs, exports, databases with PII)
2. **NEVER** share MLS data outside authorized systems
3. **NEVER** log or print client PII (phone numbers, emails, addresses)
4. **ALWAYS** use .gitignore to exclude Data/ directory
5. **ALWAYS** respect MLS terms of service — no scraping, no redistribution
6. **ALWAYS** comply with DNC (Do Not Call) regulations
7. **ALWAYS** follow CAN-SPAM for email outreach
8. If uncertain whether an operation exposes PII — STOP and ask

### Why This Matters
MLS access is the Realtor's competitive moat and livelihood.
Violating MLS ToS = license suspension or revocation.
Violating privacy laws = fines and legal liability.
The cost of caution is zero. The cost of violations is catastrophic.
