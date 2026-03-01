---
name: code-review
description: Review code changes for correctness, security, and adherence to project standards
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash
argument-hint: [file or branch to review]
---

# Code Review

Review code changes for correctness, security, and adherence to project standards.

## Steps

1. **Determine what to review.** Based on $ARGUMENTS:
   - If $ARGUMENTS is a **file path** (contains `/` or `\` or ends in a code extension like `.py`, `.ts`, `.js`, `.html`, `.css`): review that specific file.
   - If $ARGUMENTS is a **branch name** (no path separators, no code extension): run `git diff main...$ARGUMENTS` to see all changes on that branch relative to main.
   - If **no arguments** are provided: run `git diff` to review all uncommitted changes (both staged and unstaged). Also run `git diff --cached` to see staged-only changes.

2. **Read the code.** For file-based reviews, read the entire file. For diff-based reviews, analyze the diff output carefully.

3. **Load project context.** Read `CLAUDE.md` briefly to understand project conventions and architectural patterns that the code should follow.

4. **PII Safety Check (CRITICAL).** For any code that handles lead data, verify:
   - PII (names, phones, emails, addresses) is never logged or printed
   - MLS data is never committed to git
   - .env files are never read or exposed in code output
   - API keys are loaded from environment variables, never hardcoded
   - Flag any violation as **CRITICAL**

5. **Perform the review.** Check for the following categories:

   ### Critical
   - Logic errors and bugs that would cause incorrect behavior
   - Security vulnerabilities (injection, auth bypass, hardcoded secrets, PII exposure)
   - MLS terms of service violations (scraping, data redistribution)
   - Data corruption risks
   - Resource leaks (file handles, database connections)

   ### Warning
   - Missing error handling at system boundaries (I/O, network, API calls)
   - Missing input validation on CSV imports
   - API misuse or deprecated function calls
   - Code that contradicts project architecture defined in CLAUDE.md
   - DNC/CAN-SPAM compliance issues in outreach code

   ### Suggestion
   - Code style inconsistencies with the rest of the codebase
   - Performance improvements (unnecessary allocations, redundant operations)
   - Readability improvements (naming, structure)
   - DRY violations (duplicated logic)

6. **Report findings.** Present results grouped by severity. For each finding:
   - State the severity: **CRITICAL**, **WARNING**, or **SUGGESTION**
   - Identify the file and line number (or diff hunk)
   - Describe the issue clearly
   - Provide a recommended fix

   If no issues are found, explicitly state that the code looks clean.

7. **Summary.** End with a brief overall assessment: is this code ready to ship, or does it need changes? Count the findings by severity.
