"""Tests for workspace scaffolding and upgrade logic."""

import json
import sys
from pathlib import Path

from learning_os.scaffold import (
    scaffold_workspace,
    upgrade_workspace,
    _ensure_gitignore,
    _GITIGNORE_MARKER,
)
from learning_os import __version__


def test_scaffold_creates_workspace_structure(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="cursor", with_sample=False, console=quiet_console)

    assert (tmp_workspace / ".cursor" / "skills" / "learn" / "SKILL.md").exists()
    assert (tmp_workspace / ".cursor" / "rules" / "learning-mode.mdc").exists()
    assert (tmp_workspace / ".cursor" / "hooks" / "hooks.json").exists()
    assert (tmp_workspace / ".learning-os" / "hooks" / "session_end.py").exists()
    assert (tmp_workspace / ".learning-os" / "version").exists()
    assert (tmp_workspace / "courses" / "REGISTRY.md").exists()
    assert (tmp_workspace / "notes").is_dir()
    assert (tmp_workspace / ".learning-progress").exists()


def test_scaffold_claude_creates_claude_files(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="claude", with_sample=False, console=quiet_console)

    assert (tmp_workspace / ".claude" / "skills" / "learn" / "SKILL.md").exists()
    assert (tmp_workspace / ".claude" / "rules" / "learning-mode.md").exists()
    assert (tmp_workspace / ".claude" / "settings.json").exists()
    assert (tmp_workspace / "CLAUDE.md").exists()
    assert (tmp_workspace / ".learning-os" / "CONTEXT.md").exists()
    # CLAUDE.md stub must reference the engine context via @-import
    assert "@.learning-os/CONTEXT.md" in (tmp_workspace / "CLAUDE.md").read_text()
    assert not (tmp_workspace / ".cursor").exists()


def test_upgrade_does_not_overwrite_claude_md(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="claude", with_sample=False, console=quiet_console)

    claude_md = tmp_workspace / "CLAUDE.md"
    claude_md.write_text("# My custom notes\n\n@.learning-os/CONTEXT.md\n")

    upgrade_workspace(str(tmp_workspace), console=quiet_console)

    assert claude_md.read_text() == "# My custom notes\n\n@.learning-os/CONTEXT.md\n"


def test_upgrade_refreshes_context_md(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="claude", with_sample=False, console=quiet_console)

    context = tmp_workspace / ".learning-os" / "CONTEXT.md"
    context.write_text("# old engine content\n")

    upgrade_workspace(str(tmp_workspace), console=quiet_console)

    assert "# old engine content" not in context.read_text()
    assert "Learning OS" in context.read_text()


def test_scaffold_both_creates_symlinks(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="both", with_sample=False, console=quiet_console)

    shared = tmp_workspace / ".learning-os" / "skills" / "learn"
    assert shared.is_dir()

    cursor_link = tmp_workspace / ".cursor" / "skills" / "learn"
    claude_link = tmp_workspace / ".claude" / "skills" / "learn"

    assert cursor_link.exists()
    assert claude_link.exists()

    assert (cursor_link / "SKILL.md").exists()
    assert (claude_link / "SKILL.md").exists()

    if cursor_link.is_symlink():
        assert shared.resolve() == cursor_link.resolve()
    if claude_link.is_symlink():
        assert shared.resolve() == claude_link.resolve()


def test_scaffold_with_sample(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="cursor", with_sample=True, console=quiet_console)

    assert (tmp_workspace / "courses" / "sample-course" / "COURSE.yaml").exists()
    assert (tmp_workspace / "courses" / "sample-course" / "LEARNING_PLAN.md").exists()


def test_version_stamp_written(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="cursor", with_sample=False, console=quiet_console)

    version_file = tmp_workspace / ".learning-os" / "version"
    assert version_file.exists()
    assert version_file.read_text().strip() == __version__


def test_upgrade_preserves_user_content(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="cursor", with_sample=True, console=quiet_console)

    custom_note = tmp_workspace / "notes" / "session-notes.md"
    custom_note.write_text("# My notes\n")
    progress = tmp_workspace / ".learning-progress"
    progress.write_text(json.dumps({
        "tracks": {
            "sample": {
                "completed": ["data-types"],
                "last_saved": "data-types",
                "last_date": "2026-01-01 10:00",
            }
        }
    }))

    upgrade_workspace(str(tmp_workspace), console=quiet_console)

    assert custom_note.read_text() == "# My notes\n"
    assert "data-types" in progress.read_text()
    assert (tmp_workspace / "courses" / "sample-course" / "COURSE.yaml").exists()


def test_upgrade_updates_version_stamp(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="cursor", with_sample=False, console=quiet_console)

    version_file = tmp_workspace / ".learning-os" / "version"
    version_file.write_text("0.9.0\n")

    upgrade_workspace(str(tmp_workspace), console=quiet_console)

    assert version_file.read_text().strip() == __version__


def test_upgrade_cleans_old_bash_hook(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="cursor", with_sample=False, console=quiet_console)

    old_sh = tmp_workspace / ".learning-os" / "hooks" / "session-end.sh"
    old_sh.write_text("#!/bin/bash\nexit 0\n")

    upgrade_workspace(str(tmp_workspace), console=quiet_console)

    assert not old_sh.exists()
    assert (tmp_workspace / ".learning-os" / "hooks" / "session_end.py").exists()


def test_gitignore_idempotent(tmp_workspace, quiet_console):
    _ensure_gitignore(tmp_workspace, quiet_console)
    content1 = (tmp_workspace / ".gitignore").read_text()

    _ensure_gitignore(tmp_workspace, quiet_console)
    content2 = (tmp_workspace / ".gitignore").read_text()

    assert content1 == content2
    assert content1.count(_GITIGNORE_MARKER) == 1


def test_gitignore_does_not_include_learning_progress(tmp_workspace, quiet_console):
    _ensure_gitignore(tmp_workspace, quiet_console)
    content = (tmp_workspace / ".gitignore").read_text()

    assert ".learning-progress" not in content


def test_gitignore_respects_existing_entries(tmp_workspace, quiet_console):
    gitignore = tmp_workspace / ".gitignore"
    gitignore.write_text("*.pyc\n__pycache__/\nbooks/\n")

    _ensure_gitignore(tmp_workspace, quiet_console)
    content = gitignore.read_text()

    assert _GITIGNORE_MARKER not in content


def test_session_end_hook_uses_sys_executable(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="cursor", with_sample=False, console=quiet_console)

    hooks_json = tmp_workspace / ".cursor" / "hooks" / "hooks.json"
    command = json.loads(hooks_json.read_text())["hooks"]["sessionEnd"][0]["command"]
    assert sys.executable in command
    assert "session_end.py" in command


def test_claude_settings_hook_uses_sys_executable(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="claude", with_sample=False, console=quiet_console)

    settings = tmp_workspace / ".claude" / "settings.json"
    command = json.loads(settings.read_text())["hooks"]["SessionEnd"][0]["hooks"][0]["command"]
    assert sys.executable in command
    assert "session_end.py" in command


def test_scaffold_writes_config(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="claude", with_sample=False, console=quiet_console)

    config_path = tmp_workspace / ".learning-os" / "config.json"
    assert config_path.exists()
    assert json.loads(config_path.read_text())["tool"] == "claude"


def test_upgrade_uses_config_not_directory_sniffing(tmp_workspace, quiet_console):
    """Upgrade must read tool from config.json, not infer it from directory layout."""
    scaffold_workspace(str(tmp_workspace), tool="claude", with_sample=False, console=quiet_console)

    # Tamper: add a .cursor/rules dir to confuse directory-sniffing logic
    (tmp_workspace / ".cursor" / "rules").mkdir(parents=True, exist_ok=True)

    upgrade_workspace(str(tmp_workspace), console=quiet_console)

    # Config should still report claude, and no cursor skills should be installed
    config = json.loads((tmp_workspace / ".learning-os" / "config.json").read_text())
    assert config["tool"] == "claude"
    assert not (tmp_workspace / ".cursor" / "skills").exists()


def test_scaffold_creates_all_skills(tmp_workspace, quiet_console):
    scaffold_workspace(str(tmp_workspace), tool="cursor", with_sample=False, console=quiet_console)

    expected_skills = [
        "chapter-check", "create-course", "create-course-from-book",
        "learn", "learning-status", "onboarding", "save-progress",
    ]
    skills_dir = tmp_workspace / ".cursor" / "skills"
    actual = sorted(d.name for d in skills_dir.iterdir() if d.is_dir())
    assert actual == expected_skills
