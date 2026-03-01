---
name: compliance-check
description: Scan for compliance issues — MLS ToS, DNC, CAN-SPAM, PII exposure, credential safety
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash
---

# Compliance Check

Scan the codebase and data files for compliance and security issues.

## Steps

1. **Credential scan.** Search the entire project for exposed credentials:
   - Hardcoded API keys, passwords, tokens
   - .env files that might be tracked by git
   - Credentials in code comments or documentation
   - Check `.gitignore` includes: `.env`, `.env.*`, `Data/`, `*.key`, `*.pem`, `credentials.json`

2. **PII exposure scan.** Search code for potential PII logging or exposure:
   - print() or logging calls that might output client names, phones, emails
   - Log files in `logs/` that contain PII patterns (phone numbers, email addresses)
   - CSV files outside `Data/` directory that might contain client info

3. **MLS ToS compliance.** Check for potential MLS terms of service violations:
   - Any web scraping code targeting MLS portals
   - MLS data being redistributed or shared outside the system
   - MLS data stored in git-tracked files
   - Automated MLS login attempts

4. **Outreach compliance.** Check outreach-related code for:
   - DNC (Do Not Call) list checking before phone outreach
   - CAN-SPAM compliance (unsubscribe mechanism, physical address, honest subject lines)
   - TCPA compliance for text messages (prior consent)
   - State-specific cold calling regulations

5. **Data handling.** Verify proper data handling practices:
   - PII encrypted at rest (or plan to encrypt)
   - Data retention policies implemented
   - Proper access controls on database files
   - Backup procedures for lead data

6. **Present findings.** Format as a compliance report:

   ```
   ## Compliance Check — YYYY-MM-DD

   ### Credential Safety
   [PASS|FAIL] — [details]

   ### PII Protection
   [PASS|FAIL] — [details]

   ### MLS ToS
   [PASS|FAIL] — [details]

   ### Outreach Compliance
   [PASS|FAIL|NOT APPLICABLE] — [details]

   ### Data Handling
   [PASS|FAIL] — [details]

   ### Overall: [CLEAN|NEEDS ATTENTION|CRITICAL ISSUES]
   ```

   Flag any CRITICAL issues at the top of the report.
