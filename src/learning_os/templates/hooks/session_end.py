#!/usr/bin/env python3
"""Session-end hook — cross-platform replacement for session-end.sh.

Cursor:      sessionEnd event  → .cursor/hooks/hooks.json
Claude Code: SessionEnd event  → .claude/settings.json

Called when a session ends. Acts as a safety net: if the user closes their
AI tool without running save-progress, this writes a minimal breadcrumb
entry to notes/session-notes.md so no session is invisible in the journal.

Input:  JSON on stdin (session context from the AI tool — currently unused)
Output: exit 0 always — hooks must never block the tool on failure
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    notes_file = project_root / "notes" / "session-notes.md"
    progress_file = project_root / ".learning-progress"

    try:
        sys.stdin.read()
    except Exception:
        pass

    today = datetime.now().strftime("%Y-%m-%d")

    if notes_file.exists():
        content = notes_file.read_text(encoding="utf-8")
        match = re.search(r"^## (\d{4}-\d{2}-\d{2})", content, re.MULTILINE)
        if match and match.group(1) == today:
            return
    else:
        content = ""

    notes_file.parent.mkdir(parents=True, exist_ok=True)

    if not content:
        content = "# Session notes\n\n"

    progress_summary = ""
    if progress_file.exists():
        try:
            data = json.loads(progress_file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "tracks" in data:
                parts = []
                for track, info in data["tracks"].items():
                    if not isinstance(info, dict):
                        continue
                    last = info.get("last_saved", "")
                    count = len(info.get("completed", []))
                    date = info.get("last_date", "")
                    parts.append(f"{track}: {last} ({count} chapter(s)) {date}".strip())
                progress_summary = ", ".join(parts)
        except (json.JSONDecodeError, ValueError, OSError):
            pass

    lines = content.split("\n", 2)
    header = "\n".join(lines[:2])
    rest = lines[2] if len(lines) > 2 else ""

    breadcrumb = f"## {today}\n\n"
    breadcrumb += "**Auto-captured:** Session ended without explicit save.\n"
    if progress_summary:
        breadcrumb += f"**Current progress:** {progress_summary}\n"
    breadcrumb += "\n_Run `save my progress` at the start of next session to add details._\n\n"

    notes_file.write_text(header + "\n" + breadcrumb + rest, encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
