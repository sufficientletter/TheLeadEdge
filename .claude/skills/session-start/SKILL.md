---
name: session-start
description: Initialize a new work session — read project constitution, create journal entry, review recent changes
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Write
argument-hint: [optional focus area]
---

# Session Start

Initialize a new work session for this project.

## Steps

1. **Load project context.** Read `CLAUDE.md` at the project root to understand the project constitution, architecture, and workflow rules. Then read `MASTER_BUILD_PLAN.md` to understand the current build plan and phase.

2. **Create today's journal entry.** Check if `TeamLeadJournal/` directory exists. If not, create it. Then check if a journal file for today already exists at `TeamLeadJournal/YYYY-MM-DD_thoughts.md` (using today's actual date). If it does NOT exist, create it with this template:

```
# Team Lead Journal — YYYY-MM-DD

## Session Start

Starting new session.
```

If it already exists, note that and move on.

3. **Review recent changes.** Run `git log --oneline -10` to see the last 10 commits and understand recent project momentum.

4. **Check current state.** Run `git status` to see the working tree — any uncommitted changes, staged files, or untracked files.

5. **Focus area.** If the user provided arguments ($ARGUMENTS), note the requested focus area and tailor the summary toward that topic. Look for relevant files, recent commits touching that area, and any TODOs related to it.

6. **Summarize and prompt.** Present a clean summary covering:
   - Project name and purpose (from CLAUDE.md)
   - Current build phase and progress (from MASTER_BUILD_PLAN.md)
   - Current git branch and state
   - Recent activity highlights (from git log)
   - Any uncommitted work in progress
   - Focus area context (if provided)

   Then ask the user: "What would you like to work on this session?"
