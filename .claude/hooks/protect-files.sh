#!/usr/bin/env bash
# ============================================================================
# protect-files.sh — PreToolUse hook for Edit and Write operations
#
# Prevents accidental modification of:
#   1. Critical project files (constitution, rules, settings)
#   2. MLS data files and PII-containing exports
#
# Exit codes:
#   0 = allowed (proceed with the edit/write)
#   2 = blocked (tool call is rejected, message shown to user)
# ============================================================================

INPUT=$(cat)

# Extract file_path from tool_input JSON using Python (jq not guaranteed on Windows)
FILE_PATH=$(echo "$INPUT" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('tool_input', {}).get('file_path', ''))
except Exception:
    print('')
" 2>/dev/null)

# If we couldn't extract a file path, allow the operation
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

BASENAME=$(basename "$FILE_PATH")
NORMALIZED=$(echo "$FILE_PATH" | sed 's|\\|/|g' | tr '[:upper:]' '[:lower:]')
EXTENSION="${BASENAME##*.}"

# ============================================================================
# LAYER 1: Environment and Credential File Protection
# ============================================================================

# Block writes to .env files anywhere
if echo "$BASENAME" | grep -qiE '^\.env'; then
    echo "BLOCKED: Writing to .env files is FORBIDDEN. Credentials must be managed manually." >&2
    exit 2
fi

# Block writes to credential files
case "$BASENAME" in
    credentials.json|secrets.json|*.key|*.pem|*.p12)
        echo "BLOCKED: Writing to credential files is FORBIDDEN. Manage secrets manually." >&2
        exit 2
        ;;
esac

# ============================================================================
# LAYER 2: Critical Project File Protection
# ============================================================================

# 1. .claude/settings.json — team-shared config
if echo "$NORMALIZED" | grep -qE '\.claude/settings\.json$'; then
    echo "BLOCKED: .claude/settings.json is protected (shared config). Edit manually outside Claude Code." >&2
    exit 2
fi

# 2. Root CLAUDE.md — project constitution (allow CLAUDE.md in subdirectories)
if [ "$BASENAME" = "CLAUDE.md" ]; then
    if ! echo "$NORMALIZED" | grep -qE '/(agents|docs|research|teamleadjournal|logs|src|tests|\.claude|strategies|scripts)/'; then
        echo "BLOCKED: CLAUDE.md (project constitution) is protected. Edit manually outside Claude Code." >&2
        exit 2
    fi
fi

exit 0
