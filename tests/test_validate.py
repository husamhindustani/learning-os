"""Tests for workspace and course validation."""

from pathlib import Path

from learning_os.validate import validate_workspace


def _setup_workspace(tmp_workspace, quiet_console):
    """Set up a minimal valid workspace for validation tests."""
    from learning_os.scaffold import scaffold_workspace
    scaffold_workspace(str(tmp_workspace), tool="cursor", with_sample=True, console=quiet_console)


def test_valid_workspace_passes(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    errors, warnings = validate_workspace(str(tmp_workspace))
    assert errors == []


def test_missing_courses_dir(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    import shutil
    shutil.rmtree(tmp_workspace / "courses")

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("Missing courses/" in e for e in errors)


def test_missing_required_field(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    course_yaml = tmp_workspace / "courses" / "sample-course" / "COURSE.yaml"
    course_yaml.write_text("title: Missing ID\ntype: programming\n")

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("Missing required field 'id'" in e for e in errors)
    assert any("Missing required field 'chapters'" in e for e in errors)


def test_id_mismatch(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    course_yaml = tmp_workspace / "courses" / "sample-course" / "COURSE.yaml"
    course_yaml.write_text(
        "id: wrong-id\ntitle: X\ntrack: x\ntype: programming\nchapters: []\n"
    )

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("does not match directory name" in e for e in errors)


def test_invalid_type(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    course_yaml = tmp_workspace / "courses" / "sample-course" / "COURSE.yaml"
    course_yaml.write_text(
        "id: sample-course\ntitle: X\ntrack: x\ntype: invalid\nchapters: []\n"
    )

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("Invalid type 'invalid'" in e for e in errors)


def test_duplicate_chapter_ids(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    course_yaml = tmp_workspace / "courses" / "sample-course" / "COURSE.yaml"
    course_yaml.write_text("""\
id: sample-course
title: X
track: x
type: programming
chapters:
  - id: dup
    title: First
    topics: ["a"]
  - id: dup
    title: Second
    topics: ["b"]
""")

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("Duplicate chapter id 'dup'" in e for e in errors)


def test_track_name_mismatch(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    course_yaml = tmp_workspace / "courses" / "sample-course" / "COURSE.yaml"
    course_yaml.write_text("""\
id: sample-course
title: X
track: alpha
type: programming
chapters:
  - id: ch1
    title: Ch1
    topics: ["a"]
progress:
  track_name: beta
  section_mapping:
    ch1: "Ch1"
""")

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("does not match track" in e for e in errors)


def test_missing_content_file_warning(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    course_yaml = tmp_workspace / "courses" / "sample-course" / "COURSE.yaml"
    course_yaml.write_text("""\
id: sample-course
title: X
track: x
type: programming
learning_plan: DOES_NOT_EXIST.md
chapters:
  - id: ch1
    title: Ch1
    topics: ["a"]
""")

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("DOES_NOT_EXIST.md" in w and "not found" in w for w in warnings)


def test_section_mapping_warnings(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    course_yaml = tmp_workspace / "courses" / "sample-course" / "COURSE.yaml"
    course_yaml.write_text("""\
id: sample-course
title: X
track: x
type: programming
chapters:
  - id: ch1
    title: Ch1
    topics: ["a"]
  - id: ch2
    title: Ch2
    topics: ["b"]
progress:
  track_name: x
  section_mapping:
    ch1: "Chapter One"
    ghost: "Does Not Exist"
""")

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("missing entry for chapter 'ch2'" in w for w in warnings)
    assert any("'ghost' but no matching chapter" in w for w in warnings)


def test_invalid_yaml(tmp_workspace, quiet_console):
    _setup_workspace(tmp_workspace, quiet_console)
    course_yaml = tmp_workspace / "courses" / "sample-course" / "COURSE.yaml"
    course_yaml.write_text(":\n  - :\n  bad: [yaml: {")

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("Invalid YAML" in e for e in errors)


def test_no_ai_tool_configured(tmp_workspace, quiet_console):
    import shutil
    (tmp_workspace / "courses").mkdir()
    (tmp_workspace / "notes").mkdir()
    (tmp_workspace / ".learning-progress").touch()

    errors, warnings = validate_workspace(str(tmp_workspace))
    assert any("No AI tool configured" in e for e in errors)
