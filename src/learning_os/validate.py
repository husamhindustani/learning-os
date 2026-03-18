"""Workspace and course validation."""

from pathlib import Path
from typing import List, Tuple

import yaml


VALID_TYPES = {"programming", "conceptual", "mixed"}
REQUIRED_COURSE_FIELDS = {"id", "title", "track", "type", "chapters"}
REQUIRED_CHAPTER_FIELDS = {"id", "title", "topics"}


def validate_workspace(directory: str) -> Tuple[List[str], List[str]]:
    """Validate workspace structure and all courses.

    Returns (errors, warnings).
    """
    target = Path(directory).resolve()
    errors: List[str] = []
    warnings: List[str] = []

    if not (target / "courses").is_dir():
        errors.append("Missing courses/ directory")
    if not (target / "notes").is_dir():
        warnings.append("Missing notes/ directory")
    if not (target / ".learning-progress").exists():
        warnings.append("Missing .learning-progress file")

    has_cursor = (target / ".cursor" / "skills").exists()
    has_claude = (target / ".claude" / "skills").exists()
    if not has_cursor and not has_claude:
        errors.append(
            "No AI tool configured — missing both .cursor/skills/ and .claude/skills/"
        )

    version_file = target / ".learning-os" / "version"
    if not version_file.exists():
        warnings.append(
            "Missing .learning-os/version — run 'learning-os upgrade' to add it"
        )

    courses_dir = target / "courses"
    if courses_dir.is_dir():
        for course_dir in sorted(courses_dir.iterdir()):
            if not course_dir.is_dir():
                continue
            course_yaml = course_dir / "COURSE.yaml"
            if not course_yaml.exists():
                continue
            ce, cw = _validate_course(course_dir, course_yaml)
            errors.extend(ce)
            warnings.extend(cw)

    return errors, warnings


def _validate_course(
    course_dir: Path, course_yaml: Path
) -> Tuple[List[str], List[str]]:
    """Validate a single COURSE.yaml and its referenced files."""
    errors: List[str] = []
    warnings: List[str] = []
    prefix = f"courses/{course_dir.name}"

    try:
        data = yaml.safe_load(course_yaml.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        errors.append(f"{prefix}/COURSE.yaml: Invalid YAML — {e}")
        return errors, warnings

    if not isinstance(data, dict):
        errors.append(
            f"{prefix}/COURSE.yaml: Expected a YAML mapping, got {type(data).__name__}"
        )
        return errors, warnings

    for field in REQUIRED_COURSE_FIELDS:
        if field not in data:
            errors.append(f"{prefix}: Missing required field '{field}'")

    if "id" in data and data["id"] != course_dir.name:
        errors.append(
            f"{prefix}: id '{data['id']}' does not match directory name '{course_dir.name}'"
        )

    if "type" in data and data["type"] not in VALID_TYPES:
        errors.append(
            f"{prefix}: Invalid type '{data['type']}' "
            f"— must be one of: {', '.join(sorted(VALID_TYPES))}"
        )

    chapters = data.get("chapters", [])
    if not isinstance(chapters, list):
        errors.append(f"{prefix}: 'chapters' must be a list")
        chapters = []

    chapter_ids: set = set()
    for i, ch in enumerate(chapters):
        if not isinstance(ch, dict):
            errors.append(f"{prefix}: chapters[{i}] must be a mapping")
            continue
        for field in REQUIRED_CHAPTER_FIELDS:
            if field not in ch:
                errors.append(f"{prefix}: chapters[{i}] missing required field '{field}'")
        ch_id = ch.get("id")
        if ch_id:
            if ch_id in chapter_ids:
                errors.append(f"{prefix}: Duplicate chapter id '{ch_id}'")
            chapter_ids.add(ch_id)
        topics = ch.get("topics")
        if topics is not None and not isinstance(topics, list):
            errors.append(f"{prefix}: chapters[{i}].topics must be a list")
        elif isinstance(topics, list) and len(topics) == 0:
            warnings.append(
                f"{prefix}: chapters[{i}] ({ch_id or 'unnamed'}) has no topics"
            )

    progress = data.get("progress")
    if progress:
        if not isinstance(progress, dict):
            errors.append(f"{prefix}: 'progress' must be a mapping")
        else:
            track_name = progress.get("track_name")
            if track_name and "track" in data and track_name != data["track"]:
                errors.append(
                    f"{prefix}: progress.track_name '{track_name}' "
                    f"does not match track '{data['track']}'"
                )
            section_mapping = progress.get("section_mapping", {})
            if isinstance(section_mapping, dict):
                for ch_id in chapter_ids:
                    if ch_id not in section_mapping:
                        warnings.append(
                            f"{prefix}: progress.section_mapping missing entry "
                            f"for chapter '{ch_id}'"
                        )
                for key in section_mapping:
                    if key not in chapter_ids:
                        warnings.append(
                            f"{prefix}: progress.section_mapping has entry '{key}' "
                            f"but no matching chapter"
                        )
    elif chapters:
        warnings.append(f"{prefix}: No 'progress' section defined")

    if "learning_plan" in data:
        lp = course_dir / data["learning_plan"]
        if not lp.exists():
            warnings.append(
                f"{prefix}: learning_plan '{data['learning_plan']}' not found"
            )
    if "exercises" in data:
        ex = course_dir / data["exercises"]
        if not ex.exists():
            warnings.append(f"{prefix}: exercises '{data['exercises']}' not found")

    for ch in chapters:
        if isinstance(ch, dict) and "content_file" in ch:
            cf = course_dir / ch["content_file"]
            if not cf.exists():
                warnings.append(
                    f"{prefix}: chapter '{ch.get('id', '?')}' "
                    f"content_file '{ch['content_file']}' not found"
                )

    return errors, warnings
