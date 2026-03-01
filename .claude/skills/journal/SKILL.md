---
name: journal
description: Create or update today's Team Lead journal entry with session notes and decisions
user-invocable: true
allowed-tools: Read, Write, Glob
argument-hint: [notes to add]
---

# Journal Entry

Create or update today's Team Lead journal entry.

## Steps

1. **Determine today's date.** Use the current date in YYYY-MM-DD format.

2. **Check for existing entry.** Look for `TeamLeadJournal/YYYY-MM-DD_thoughts.md` using today's date. Also check if the `TeamLeadJournal/` directory exists — create it if it does not.

3. **If the journal file already exists:**
   - Read the existing file content.
   - Append a new section at the end of the file using this format:

   ```
   ## HH:MM — [Topic]

   [Content from $ARGUMENTS]
   ```

   Use the current time (24-hour format) for HH:MM. Derive the topic from the first few words of $ARGUMENTS or use a sensible short label. The content is the full text of $ARGUMENTS.

4. **If the journal file does NOT exist:**
   - Create it with this structure:

   ```
   # Team Lead Journal — YYYY-MM-DD

   ## HH:MM — [Topic]

   [Content from $ARGUMENTS]
   ```

5. **If no $ARGUMENTS were provided:**
   - If the file exists, read it and display the current contents to the user.
   - If the file does not exist, create it with a minimal header and note that no content was provided:

   ```
   # Team Lead Journal — YYYY-MM-DD

   ## HH:MM — Session Start

   New session started. No notes provided yet.
   ```

6. **Confirm.** Tell the user what was written and the file path.
