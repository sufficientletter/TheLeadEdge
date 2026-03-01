---
name: data-health
description: Check data pipeline health — import status, data quality, source connectivity
user-invocable: true
allowed-tools: Read, Bash, Glob, Grep
---

# Data Health Check

Check the health and freshness of all data sources feeding the lead pipeline.

## Steps

1. **MLS data.** Check the `Data/` directory for MLS CSV exports:
   - Most recent file and its timestamp
   - Record count in the most recent import
   - Any duplicate detection results
   - Schema validation status (expected columns present)

2. **Public records.** Check connectivity and freshness for each configured public records source:
   - County assessor data (last fetch date)
   - Pre-foreclosure/lis pendens (last fetch date)
   - Probate filings (last fetch date)
   - Code violations (last fetch date)

3. **Database health.** If SQLite database exists:
   - Check file size and table counts
   - Run integrity check
   - Count total records by source
   - Check for orphaned or stale records

4. **Scheduled jobs.** Check if APScheduler jobs are configured and running:
   - List configured job schedules
   - Last run time for each job
   - Any failed job executions

5. **Present the summary.** Format as a clean health report:

   ```
   ## Data Health — YYYY-MM-DD

   ### MLS Data
   Status: [HEALTHY|STALE|MISSING]
   Last import: [date] ([N] records)

   ### Public Records
   [Source]: [HEALTHY|STALE|NOT CONFIGURED] (last: [date])

   ### Database
   Status: [HEALTHY|NEEDS ATTENTION|NOT CREATED]
   Size: [N] MB | Records: [N]

   ### Scheduled Jobs
   [Job]: [RUNNING|STOPPED|NOT CONFIGURED] (last: [date])
   ```

   If components haven't been built yet, report "NOT BUILT" and reference the build phase.
