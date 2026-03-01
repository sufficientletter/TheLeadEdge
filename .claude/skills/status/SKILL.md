---
name: status
description: Quick project status overview — git state, recent changes, open tasks
user-invocable: true
allowed-tools: Read, Bash, Glob, Grep
---

# Project Status

Provide a quick, comprehensive project status overview.

## Steps

1. **Git state.** Run `git status` to show the current branch, staged changes, unstaged modifications, and untracked files. Present this cleanly.

2. **Recent commits.** Run `git log --oneline -5` to show the last 5 commits. Note the pace of development and what areas have been active.

3. **Latest journal entry.** Search `TeamLeadJournal/` for the most recent journal file (sort by filename descending since they use YYYY-MM-DD format). Read the most recent file and extract key highlights — decisions made, blockers noted, and next steps planned.

4. **Open tasks and TODOs.** Search the codebase for actionable markers using grep across all common source file types:
   - Search for `TODO`, `FIXME`, `HACK`, `XXX`, and `WARN` markers
   - Search in files matching: `*.py`, `*.ts`, `*.js`, `*.html`, `*.css`, `*.cfg`, `*.toml`, `*.yaml`, `*.yml`
   - List each finding with its file path, line number, and the marker text

5. **Build phase.** Reference `MASTER_BUILD_PLAN.md` to identify the current build phase and progress.

6. **Present the summary.** Format the output as a clean status report:

   ```
   ## Project Status — YYYY-MM-DD

   ### Branch & Working Tree
   [Current branch, clean/dirty state, summary of changes]

   ### Build Phase
   [Current phase from MASTER_BUILD_PLAN.md, progress]

   ### Recent Activity
   [Last 5 commits, one line each]

   ### Latest Journal Highlights
   [Key points from most recent TeamLeadJournal entry]

   ### Open TODOs
   [List of TODO/FIXME/HACK items, or "None found" if clean]
   ```

   Keep it concise. This is meant to be a quick orientation, not an exhaustive report.
