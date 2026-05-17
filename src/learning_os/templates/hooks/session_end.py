#!/usr/bin/env python3
"""Session-end hook — cross-platform replacement for session-end.sh.

Cursor:      sessionEnd event  → .cursor/hooks/hooks.json
Claude Code: SessionEnd event  → .claude/settings.json

Called when a session ends. Acts as a safety net: if the user closes their
AI tool without running save-progress, this writes a minimal breadcrumb
entry to the most recently active course's session-notes.md so no session
is invisible in the journal.

Resolution: read .learning-progress, pick the track with the newest
last_date, find the course whose COURSE.yaml maps to that track, and
write to courses/<course-id>/session-notes.md. If the active course
cannot be resolved, exit silently — a global breadcrumb is no longer
written.

Input:  JSON on stdin (session context from the AI tool — currently unused)
Output: exit 0 always — hooks must never block the tool on failure
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore


def _resolve_active_course(project_root: Path, progress_file: Path):
    """Return (course_dir, progress_summary_str) for the most recently active
    course, or (None, "") if it cannot be resolved.
    """
    if not progress_file.exists():
        return None, ""

    try:
        data = json.loads(progress_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError, OSError):
        return None, ""

    tracks = data.get("tracks") if isinstance(data, dict) else None
    if not isinstance(tracks, dict) or not tracks:
        return None, ""

    best = None
    for name, info in tracks.items():
        if not isinstance(info, dict):
            continue
        last_date = info.get("last_date", "")
        if best is None or last_date > best[1].get("last_date", ""):
            best = (name, info)
    if best is None:
        return None, ""

    track_name, info = best
    last = info.get("last_saved", "")
    count = len(info.get("completed", []) or [])
    date = info.get("last_date", "")
    summary = f"{track_name}: {last} ({count} chapter(s)) {date}".strip()

    courses_dir = project_root / "courses"
    if not courses_dir.is_dir():
        return None, summary

    for course_dir in sorted(courses_dir.iterdir()):
        course_yaml = course_dir / "COURSE.yaml"
        if not course_yaml.is_file():
            continue
        try:
            text = course_yaml.read_text(encoding="utf-8")
        except OSError:
            continue
        if yaml is not None:
            try:
                doc = yaml.safe_load(text)
            except yaml.YAMLError:
                doc = None
            if isinstance(doc, dict):
                progress_block = doc.get("progress")
                if isinstance(progress_block, dict) and progress_block.get("track_name") == track_name:
                    return course_dir, summary
                if doc.get("track") == track_name:
                    return course_dir, summary
                continue
        # YAML unavailable — fall back to a tolerant string match
        pattern = rf'^\s*(track|track_name):\s*["\']?{re.escape(track_name)}["\']?\s*$'
        if re.search(pattern, text, re.MULTILINE):
            return course_dir, summary

    return None, summary


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    progress_file = project_root / ".learning-progress"

    try:
        sys.stdin.read()
    except Exception:
        pass

    course_dir, progress_summary = _resolve_active_course(project_root, progress_file)
    if course_dir is None:
        return  # no active course resolvable — nothing to breadcrumb

    notes_file = course_dir / "session-notes.md"
    today = datetime.now().strftime("%Y-%m-%d")

    if notes_file.exists():
        content = notes_file.read_text(encoding="utf-8")
        match = re.search(r"^## (\d{4}-\d{2}-\d{2})", content, re.MULTILINE)
        if match and match.group(1) == today:
            return
    else:
        content = ""

    if not content:
        content = "# Session notes\n\n"

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
