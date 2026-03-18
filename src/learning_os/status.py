"""Course listing and progress status."""

import json
from pathlib import Path
from typing import Dict

import yaml
from rich.console import Console
from rich.table import Table


def list_courses(directory: str, console: Console):
    """List all courses and show progress."""
    target = Path(directory).resolve()
    courses_dir = target / "courses"
    progress_file = target / ".learning-progress"

    if not courses_dir.is_dir():
        console.print(
            "[yellow]No courses/ directory found. "
            "Is this a Learning OS workspace?[/yellow]"
        )
        return

    progress = _read_progress(progress_file)

    courses = []
    for course_dir in sorted(courses_dir.iterdir()):
        if not course_dir.is_dir():
            continue
        course_yaml = course_dir / "COURSE.yaml"
        if not course_yaml.exists():
            continue
        try:
            data = yaml.safe_load(course_yaml.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                courses.append(data)
        except yaml.YAMLError:
            continue

    if not courses:
        console.print(
            "[yellow]No courses found. Create one with "
            "'learning-os init --with-sample' or via your AI tool.[/yellow]"
        )
        return

    table = Table(
        title="Learning Progress", show_header=True, header_style="bold cyan"
    )
    table.add_column("Course", style="bold")
    table.add_column("Track")
    table.add_column("Type")
    table.add_column("Chapters", justify="right")
    table.add_column("Progress", justify="right")
    table.add_column("Last Saved")
    table.add_column("Next Up")

    total_chapters = 0
    total_completed = 0

    for course in courses:
        title = course.get("title", course.get("id", "?"))
        track = course.get("track", "")
        ctype = course.get("type", "?")
        chapters = course.get("chapters", [])
        num_chapters = len(chapters)
        total_chapters += num_chapters

        track_data = progress.get(track)
        completed = 0
        next_chapter = None
        last_saved = ""

        if track_data:
            completed_ids = set(track_data.get("completed", []))
            last_saved = track_data.get("last_date", "")

            # Count only chapters that exist in this course AND are in completed list
            course_chapter_ids = {
                ch.get("id")
                for ch in chapters
                if isinstance(ch, dict) and ch.get("id")
            }
            completed = len(completed_ids & course_chapter_ids)

            # Next chapter: first chapter whose id is not yet completed
            for ch in chapters:
                if isinstance(ch, dict) and ch.get("id") not in completed_ids:
                    next_chapter = ch
                    break

        total_completed += completed

        progress_str = f"{completed}/{num_chapters}"
        if num_chapters > 0:
            pct = int(completed / num_chapters * 100)
            progress_str += f" ({pct}%)"

        if completed == num_chapters and num_chapters > 0:
            next_str = "[green]Complete[/green]"
        elif next_chapter and isinstance(next_chapter, dict):
            next_str = next_chapter.get("title", next_chapter.get("id", "?"))
        elif completed == 0 and num_chapters > 0 and isinstance(chapters[0], dict):
            next_str = chapters[0].get("title", chapters[0].get("id", "?"))
        else:
            next_str = ""

        table.add_row(title, track, ctype, str(num_chapters), progress_str, last_saved, next_str)

    console.print(table)
    console.print()
    console.print(
        f"[dim]Total: {total_completed} chapters completed "
        f"across {len(courses)} course(s)[/dim]"
    )


def _read_progress(progress_file: Path) -> Dict[str, dict]:
    """Read .learning-progress into a dict of track_name → progress data.

    Format::

        {
          "tracks": {
            "java": {
              "completed": ["java8", "java9"],
              "last_saved": "java9",
              "last_date": "2026-01-15 14:30"
            }
          }
        }

    Returns a dict keyed by track name.
    """
    if not progress_file.exists():
        return {}
    text = progress_file.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "tracks" in data:
            return {k: v for k, v in data["tracks"].items() if isinstance(v, dict)}
    except (json.JSONDecodeError, ValueError):
        pass
    return {}
