---
name: lead-pipeline
description: Check lead pipeline status — active leads, scoring distribution, recent signals detected
user-invocable: true
allowed-tools: Read, Bash, Glob, Grep
argument-hint: [optional filter: expired|fsbo|preforeclosure|probate|all]
---

# Lead Pipeline Status

Show current lead pipeline health and statistics.

## Steps

1. **Check data freshness.** Look for the most recent CSV imports in `Data/` directory. Note when the last MLS export was imported and how many records it contained.

2. **Scoring distribution.** If a lead database exists (SQLite or CSV), query for the current distribution of leads across scoring tiers:
   - S-Tier (90-100): Immediate action required
   - A-Tier (75-89): High priority, contact within 24 hours
   - B-Tier (50-74): Warm leads, contact within 1 week
   - C-Tier (25-49): Nurture leads, add to drip campaign
   - D-Tier (0-24): Monitor only

3. **Signal detection.** Check which signals have been detected in the most recent pipeline run:
   - Price reductions (count and average reduction %)
   - Expired listings (count)
   - High DOM listings (count above threshold)
   - Withdrawn/relisted (count)
   - FSBO conversions (count)
   - Pre-foreclosure filings (count)
   - Probate filings (count)

4. **Filter by type.** If $ARGUMENTS specifies a lead type (expired, fsbo, preforeclosure, probate), filter the output to show only that category with additional detail.

5. **Recent activity.** Show the last 5 leads that were scored or updated, with their current tier and primary signals.

6. **Present the summary.** Format as a clean pipeline report:

   ```
   ## Lead Pipeline — YYYY-MM-DD

   ### Data Freshness
   Last MLS import: [date/time] ([N] records)

   ### Tier Distribution
   S: [N] | A: [N] | B: [N] | C: [N] | D: [N] | Total: [N]

   ### Active Signals
   [Signal counts from most recent run]

   ### Recently Scored
   [Last 5 leads with tier and primary signal]
   ```

   If the pipeline hasn't been built yet, report that and reference `MASTER_BUILD_PLAN.md` for when it's scheduled.
