---
name: delegate
description: Delegate a task to a specialist agent using the Team Lead workflow pattern
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, WebSearch, WebFetch
argument-hint: [agent-name] [task description]
---

# Delegate to Agent

Delegate a task to a specialist agent following the Team Lead workflow pattern.

## Steps

1. **Parse arguments.** Split $ARGUMENTS so that the first word is the agent name and the remainder is the task description. For example: `systems-architect implement the CSV ingestion module` means agent = `systems-architect`, task = `implement the CSV ingestion module`.

   If no arguments are provided, list the available agents by searching for agent definition files in `.claude/agents/` directories, then ask the user which agent to delegate to and what the task is.

2. **Load agent definition.** Look for the agent's definition file in these locations (in order):
   - `.claude/agents/<agent-name>/<agent-name>.md`
   - `.claude/agents/<agent-name>.md`

   Read the file to understand the agent's Role, Responsibilities, Authority, Inputs, Outputs, Constraints, and Logging requirements.

3. **Execute as the agent.** Adopt the agent's role and constraints as defined in their file. Perform the task described in $ARGUMENTS while:
   - Respecting the agent's defined authority boundaries
   - Following the agent's output format
   - Adhering to all constraints listed in the agent definition
   - Remembering that ONLY the Systems Architect agent is authorized to write code/config files
   - All other agents produce specs, research findings, and recommendations only

4. **Return results.** Present the agent's output clearly, prefixed with the agent name for clarity:

   ```
   ## [Agent Name] — [Task Summary]

   [Agent's output here]
   ```

5. **Log the delegation.** If a `logs/` directory exists, note the delegation in today's journal or log file.
