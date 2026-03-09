#!/usr/bin/env bash
# session-end.sh — shared session-end hook for Cursor and Claude Code
#
# Cursor:      sessionEnd event     → .cursor/hooks/hooks.json
# Claude Code: SessionEnd event     → .claude/settings.json
#
# Called when a session ends. Acts as a safety net: if the user closes their
# AI tool without running save-progress, this writes a minimal breadcrumb
# entry to notes/session-notes.md so no session is invisible in the journal.
#
# Input:  JSON object on stdin (Cursor: session context; Claude: session metadata)
# Output: exit 0 always — hooks must never block the tool on failure

set -euo pipefail

# Resolve project root: this script lives at .learning-os/hooks/session-end.sh
# so project root is two levels up.
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NOTES_FILE="$PROJECT_ROOT/notes/session-notes.md"
PROGRESS_FILE="$PROJECT_ROOT/.learning-progress"

# Read stdin input (Cursor passes session context as JSON)
INPUT="$(cat)"

# Only write a breadcrumb if session-notes.md was NOT already updated this session.
# We detect this by checking if the top entry's date matches today.
TODAY="$(date '+%Y-%m-%d')"

if [[ -f "$NOTES_FILE" ]]; then
  LAST_DATE="$(grep -m1 '^## [0-9]' "$NOTES_FILE" | grep -o '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' || true)"
  if [[ "$LAST_DATE" == "$TODAY" ]]; then
    # Session notes already updated today — no breadcrumb needed
    exit 0
  fi
fi

# Write a minimal breadcrumb entry so the session isn't invisible in the journal
{
  mkdir -p "$(dirname "$NOTES_FILE")"
  
  if [[ ! -f "$NOTES_FILE" ]]; then
    echo "# Session notes" > "$NOTES_FILE"
    echo "" >> "$NOTES_FILE"
  fi

  # Read current progress for context
  PROGRESS_SUMMARY=""
  if [[ -f "$PROGRESS_FILE" ]]; then
    PROGRESS_SUMMARY="$(grep '^TRACK_' "$PROGRESS_FILE" | sed 's/TRACK_[^=]*=//g' | tr '\n' ', ' | sed 's/, $//')"
  fi

  # Insert at top (after header)
  TMPFILE="$(mktemp)"
  head -2 "$NOTES_FILE" > "$TMPFILE"
  echo "## $TODAY" >> "$TMPFILE"
  echo "" >> "$TMPFILE"
  echo "**Auto-captured:** Session ended without explicit save." >> "$TMPFILE"
  if [[ -n "$PROGRESS_SUMMARY" ]]; then
    echo "**Current progress:** $PROGRESS_SUMMARY" >> "$TMPFILE"
  fi
  echo "" >> "$TMPFILE"
  echo "_Run \`save my progress\` at the start of next session to add details._" >> "$TMPFILE"
  echo "" >> "$TMPFILE"
  tail -n +3 "$NOTES_FILE" >> "$TMPFILE"
  mv "$TMPFILE" "$NOTES_FILE"
} 2>/dev/null || true  # Never fail — hook must not block Cursor

exit 0
