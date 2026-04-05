"""Smoke tests for CLI commands."""

import json
import zipfile
from pathlib import Path

from click.testing import CliRunner

from learning_os.cli import main


runner = CliRunner()


def test_version():
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_init_with_tool_flag(tmp_path):
    result = runner.invoke(main, ["init", str(tmp_path), "--tool", "cursor"])
    assert result.exit_code == 0
    assert "Done!" in result.output
    assert (tmp_path / ".cursor" / "skills" / "learn" / "SKILL.md").exists()


def test_init_both(tmp_path):
    result = runner.invoke(main, ["init", str(tmp_path), "--tool", "both"])
    assert result.exit_code == 0
    assert (tmp_path / ".learning-os" / "skills" / "learn").is_dir()
    assert (tmp_path / ".cursor" / "skills" / "learn").exists()
    assert (tmp_path / ".claude" / "skills" / "learn").exists()


def test_upgrade(tmp_path):
    runner.invoke(main, ["init", str(tmp_path), "--tool", "cursor"])
    result = runner.invoke(main, ["upgrade", str(tmp_path)])
    assert result.exit_code == 0
    assert "Upgrade complete!" in result.output


def test_validate_valid_workspace(tmp_path):
    runner.invoke(main, ["init", str(tmp_path), "--tool", "cursor", "--with-sample"])
    result = runner.invoke(main, ["validate", str(tmp_path)])
    assert result.exit_code == 0
    assert "Validation passed" in result.output


def test_validate_invalid_workspace(tmp_path):
    (tmp_path / "courses").mkdir()
    result = runner.invoke(main, ["validate", str(tmp_path)])
    assert result.exit_code != 0
    assert "Validation failed" in result.output


def test_list_empty_workspace(tmp_path):
    runner.invoke(main, ["init", str(tmp_path), "--tool", "cursor"])
    result = runner.invoke(main, ["list", str(tmp_path)])
    assert result.exit_code == 0
    assert "No courses found" in result.output


def test_list_with_courses(tmp_path):
    runner.invoke(main, ["init", str(tmp_path), "--tool", "cursor", "--with-sample"])
    result = runner.invoke(main, ["list", str(tmp_path)])
    assert result.exit_code == 0
    assert "sample" in result.output
    assert "0/3" in result.output


def test_export_and_import(tmp_path):
    workspace = tmp_path / "workspace"
    runner.invoke(main, ["init", str(workspace), "--tool", "cursor", "--with-sample"])

    zip_path = tmp_path / "exported.zip"
    result = runner.invoke(
        main, ["export", "sample-course", "--dir", str(workspace), "-o", str(zip_path)]
    )
    assert result.exit_code == 0
    assert zip_path.exists()

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        assert any("COURSE.yaml" in n for n in names)

    target = tmp_path / "target"
    runner.invoke(main, ["init", str(target), "--tool", "cursor"])
    result = runner.invoke(main, ["import", str(zip_path), "--dir", str(target)])
    assert result.exit_code == 0
    assert (target / "courses" / "sample-course" / "COURSE.yaml").exists()


def test_list_shows_chapter_completion_new_format(tmp_path):
    """New JSON progress format drives accurate chapter completion count."""
    runner.invoke(main, ["init", str(tmp_path), "--tool", "cursor", "--with-sample"])
    (tmp_path / ".learning-progress").write_text(json.dumps({
        "tracks": {
            "sample": {
                "completed": ["data-types"],
                "last_saved": "data-types",
                "last_date": "2026-01-01 10:00",
            }
        }
    }, indent=2))
    result = runner.invoke(main, ["list", str(tmp_path)])
    assert result.exit_code == 0
    assert "1/3" in result.output



def test_export_nonexistent_course(tmp_path):
    runner.invoke(main, ["init", str(tmp_path), "--tool", "cursor"])
    result = runner.invoke(
        main, ["export", "ghost", "--dir", str(tmp_path)]
    )
    assert result.exit_code != 0
    assert "not found" in result.output
