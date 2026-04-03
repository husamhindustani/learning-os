"""Workspace scaffolding and upgrade logic."""

import json
import os
import shutil
import stat
import sys
from pathlib import Path

from rich.console import Console

from learning_os import __version__


TEMPLATES_DIR = Path(__file__).parent / "templates"

# User-owned paths — never overwritten by init or upgrade.
USER_PATHS = [
    "courses/",
    "notes/",
    ".learning-progress",
]

_GITIGNORE_MARKER = "# Learning OS"


def scaffold_workspace(directory: str, tool: str, with_sample: bool, console: Console):
    """Scaffold a fresh Learning OS workspace."""
    target = Path(directory).resolve()
    target.mkdir(parents=True, exist_ok=True)

    console.print(f"[dim]Target:[/dim] {target}")
    console.print()

    _copy_engine(target, tool, console, is_upgrade=False)
    _write_workspace_config(target, tool)
    _scaffold_user_structure(target, console)

    if with_sample:
        _copy_sample(target, console)

    _write_version_stamp(target, console, is_upgrade=False)
    _init_git(target, console)

    tool_hint = "Cursor" if tool == "cursor" else "Claude Code" if tool == "claude" else "Cursor / Claude Code"
    console.print()
    console.print("[bold green]Done![/bold green] Your learning workspace is ready.")
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  1. Open this directory in {tool_hint}")
    console.print("  2. Start a new agent chat")
    console.print("  3. Type anything — the onboarding skill will guide you")
    console.print()
    console.print("[dim]Tip: Say 'create a course on Python basics' to get started.[/dim]")


def upgrade_workspace(directory: str, console: Console):
    """Upgrade an existing workspace — engine only, never user content."""
    target = Path(directory).resolve()

    if not target.exists():
        console.print(f"[red]Directory not found: {target}[/red]")
        raise SystemExit(1)

    version_file = target / ".learning-os" / "version"
    if version_file.exists():
        old_version = version_file.read_text().strip()
        if old_version == __version__:
            console.print(f"[dim]Already at v{__version__} — re-installing engine files[/dim]")
        else:
            console.print(f"[dim]Upgrading from v{old_version} → v{__version__}[/dim]")
    else:
        console.print(f"[dim]Upgrading to v{__version__} (no previous version stamp found)[/dim]")
    console.print()

    tool = _read_workspace_tool(target)

    _copy_engine(target, tool, console, is_upgrade=True)
    _write_workspace_config(target, tool)
    _write_version_stamp(target, console, is_upgrade=True)

    console.print()
    console.print("[bold green]Upgrade complete![/bold green]")
    console.print("[dim]Your courses, notes, and progress were not changed.[/dim]")


def _copy_engine(target: Path, tool: str, console: Console, is_upgrade: bool):
    """Copy all engine files into the workspace.

    Layout produced:
      When --tool both:
        .learning-os/skills/*/              — Canonical skill copies (shared)
        .cursor/skills/*/                   — Symlinks → .learning-os/skills/*
        .claude/skills/*/                   — Symlinks → .learning-os/skills/*

      When --tool cursor or --tool claude:
        .<tool>/skills/*/                   — Direct copies

      Always:
        .cursor/rules/learning-mode.mdc     — Cursor rule (globs: frontmatter)
        .claude/rules/learning-mode.md      — Claude Code rule (paths: frontmatter)
        CLAUDE.md                           — Claude Code always-on context
        .cursor/hooks/hooks.json            — Cursor hook wiring
        .claude/settings.json               — Claude Code hook wiring
        .learning-os/hooks/session_end.py   — Cross-platform session breadcrumb script
        .learning-os/version                — Engine version stamp
    """
    action = "~" if is_upgrade else "+"
    skills_src = TEMPLATES_DIR / "skills"
    rules_src = TEMPLATES_DIR / "rules"
    hooks_src = TEMPLATES_DIR / "hooks"
    claude_src = TEMPLATES_DIR / "claude"

    use_cursor = tool in ("cursor", "both")
    use_claude = tool in ("claude", "both")
    use_both = tool == "both"

    # ── Skills ────────────────────────────────────────────────────────────────
    if use_both:
        shared_skills = target / ".learning-os" / "skills"
        for skill_dir in sorted(skills_src.iterdir()):
            if not skill_dir.is_dir():
                continue
            _copy_tree(
                skill_dir,
                shared_skills / skill_dir.name,
                console,
                label=f"{action} .learning-os/skills/{skill_dir.name}/",
            )

        for tool_dir in (".cursor", ".claude"):
            tool_skills = target / tool_dir / "skills"
            tool_skills.mkdir(parents=True, exist_ok=True)
            for skill_dir in sorted(skills_src.iterdir()):
                if not skill_dir.is_dir():
                    continue
                link = tool_skills / skill_dir.name
                rel_target = os.path.relpath(
                    shared_skills / skill_dir.name, tool_skills
                )
                if link.is_symlink():
                    link.unlink()
                elif link.exists():
                    shutil.rmtree(link)
                try:
                    link.symlink_to(rel_target)
                except OSError:
                    shutil.copytree(shared_skills / skill_dir.name, link)
            console.print(
                f"  [green]{action}[/green] {tool_dir}/skills/ → .learning-os/skills/ (linked)"
            )
    else:
        for skill_dir in sorted(skills_src.iterdir()):
            if not skill_dir.is_dir():
                continue
            if use_cursor:
                _copy_tree(
                    skill_dir,
                    target / ".cursor" / "skills" / skill_dir.name,
                    console,
                    label=f"{action} .cursor/skills/{skill_dir.name}/",
                )
            if use_claude:
                _copy_tree(
                    skill_dir,
                    target / ".claude" / "skills" / skill_dir.name,
                    console,
                    label=f"{action} .claude/skills/{skill_dir.name}/",
                )

    # ── Rules ─────────────────────────────────────────────────────────────────
    if use_cursor:
        cursor_rules = target / ".cursor" / "rules"
        cursor_rules.mkdir(parents=True, exist_ok=True)
        src = rules_src / "learning-mode.mdc"
        shutil.copy2(src, cursor_rules / "learning-mode.mdc")
        console.print(f"  [green]{action}[/green] .cursor/rules/learning-mode.mdc")

    if use_claude:
        claude_rules = target / ".claude" / "rules"
        claude_rules.mkdir(parents=True, exist_ok=True)
        src = rules_src / "learning-mode.md"
        shutil.copy2(src, claude_rules / "learning-mode.md")
        console.print(f"  [green]{action}[/green] .claude/rules/learning-mode.md")

        # Engine context — always refreshed so skills/schema docs stay current
        context_dest = target / ".learning-os" / "CONTEXT.md"
        context_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(claude_src / "CONTEXT.md", context_dest)
        console.print(f"  [green]{action}[/green] .learning-os/CONTEXT.md")

        # CLAUDE.md — user-owned after first write; never overwritten on upgrade
        claude_md_dest = target / "CLAUDE.md"
        if not claude_md_dest.exists():
            shutil.copy2(claude_src / "CLAUDE.md", claude_md_dest)
            console.print(f"  [green]+[/green] CLAUDE.md")

    # ── Shared hook scripts ────────────────────────────────────────────────────
    shared_hooks_dest = target / ".learning-os" / "hooks"
    shared_hooks_dest.mkdir(parents=True, exist_ok=True)
    for py_file in hooks_src.glob("*.py"):
        dest = shared_hooks_dest / py_file.name
        shutil.copy2(py_file, dest)
        dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        console.print(f"  [green]{action}[/green] .learning-os/hooks/{py_file.name}")

    # Clean up legacy bash hooks from pre-1.1.0 workspaces
    old_sh = shared_hooks_dest / "session-end.sh"
    if old_sh.exists():
        old_sh.unlink()

    # ── Hook config: Cursor ────────────────────────────────────────────────────
    if use_cursor:
        cursor_hooks_dir = target / ".cursor" / "hooks"
        cursor_hooks_dir.mkdir(parents=True, exist_ok=True)
        _write_cursor_hooks_json(cursor_hooks_dir / "hooks.json", action, console)

    # ── Hook config: Claude Code ───────────────────────────────────────────────
    if use_claude:
        claude_dir = target / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        _write_claude_settings_json(claude_dir / "settings.json", action, console)


def _python_command() -> str:
    """Return a shell-safe reference to the current Python interpreter.

    Uses sys.executable so the hook always runs with the same interpreter
    that installed learning-os, regardless of platform (avoids the 'python3'
    vs 'python' split on Windows and venv path issues everywhere).
    Quotes the path to handle spaces (e.g. C:\\Program Files\\Python312\\...).
    """
    exe = sys.executable
    return f'"{exe}"' if " " in exe else exe


def _write_cursor_hooks_json(dest: Path, action: str, console: Console):
    """Write Cursor hooks.json pointing to the shared session-end script."""
    config = {
        "version": 1,
        "hooks": {
            "sessionEnd": [
                {
                    "command": f"{_python_command()} .learning-os/hooks/session_end.py",
                    "description": "Auto-capture session breadcrumb to notes/session-notes.md",
                }
            ],
        },
    }
    dest.write_text(json.dumps(config, indent=2) + "\n")
    console.print(f"  [green]{action}[/green] .cursor/hooks/hooks.json")


def _write_claude_settings_json(dest: Path, action: str, console: Console):
    """Write Claude Code settings.json pointing to the shared session-end script."""
    config = {
        "hooks": {
            "SessionEnd": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{_python_command()} .learning-os/hooks/session_end.py",
                        }
                    ]
                }
            ]
        }
    }
    dest.write_text(json.dumps(config, indent=2) + "\n")
    console.print(f"  [green]{action}[/green] .claude/settings.json")


def _scaffold_user_structure(target: Path, console: Console):
    """Create user-owned structure only if not already present."""
    registry_path = target / "courses" / "REGISTRY.md"
    if not registry_path.exists():
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TEMPLATES_DIR / "courses" / "REGISTRY.md", registry_path)
        console.print("  [green]+[/green] courses/REGISTRY.md")

    notes_dir = target / "notes"
    if not notes_dir.exists():
        notes_dir.mkdir(parents=True)
        (notes_dir / ".gitkeep").touch()
        console.print("  [green]+[/green] notes/")

    progress_file = target / ".learning-progress"
    if not progress_file.exists():
        progress_file.touch()
        console.print("  [green]+[/green] .learning-progress")

    _ensure_gitignore(target, console)


def _copy_sample(target: Path, console: Console):
    """Copy the sample course into courses/."""
    sample_src = TEMPLATES_DIR / "sample" / "sample-course"
    sample_dest = target / "courses" / "sample-course"
    if sample_dest.exists():
        console.print("  [yellow]=[/yellow] courses/sample-course/ (already exists, skipped)")
        return
    _copy_tree(sample_src, sample_dest, console, label="+ courses/sample-course/")


def _copy_tree(src: Path, dest: Path, console: Console, label: str):
    """Copy a directory tree, overwriting destination."""
    if dest.is_symlink():
        dest.unlink()
    elif dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    console.print(f"  [green]{label}[/green]")


def _ensure_gitignore(target: Path, console: Console):
    """Add Learning OS entries to .gitignore if not already present."""
    gitignore = target / ".gitignore"
    entries = ["*.pyc", "__pycache__/", "books/"]
    existing = gitignore.read_text() if gitignore.exists() else ""

    if _GITIGNORE_MARKER in existing:
        return

    additions = [e for e in entries if e not in existing]
    if not additions:
        return

    with gitignore.open("a") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write(f"\n{_GITIGNORE_MARKER}\n")
        f.write("\n".join(additions) + "\n")
    console.print("  [green]+[/green] .gitignore (updated)")


def _write_workspace_config(target: Path, tool: str):
    """Persist tool choice to .learning-os/config.json.

    Written at init and refreshed at upgrade so the upgrade command always
    knows which tool(s) to reinstall without guessing from directory layout.
    """
    config_path = target / ".learning-os" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({"tool": tool}, indent=2) + "\n")


def _read_workspace_tool(target: Path) -> str:
    """Return the tool choice stored in config.json.

    Falls back to directory-sniffing for workspaces created before config.json
    was introduced (pre-1.1.0 upgrades).
    """
    config_path = target / ".learning-os" / "config.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text())
            tool = data.get("tool", "")
            if tool in ("cursor", "claude", "both"):
                return tool
        except (json.JSONDecodeError, ValueError):
            pass
    # Legacy fallback: infer from installed directories
    has_cursor = (target / ".cursor" / "skills").exists() or (target / ".cursor" / "rules").exists()
    has_claude = (target / ".claude" / "skills").exists() or (target / ".claude" / "rules").exists()
    if has_cursor and has_claude:
        return "both"
    if has_claude:
        return "claude"
    return "cursor"


def _write_version_stamp(target: Path, console: Console, is_upgrade: bool):
    """Write the current version to .learning-os/version."""
    version_dir = target / ".learning-os"
    version_dir.mkdir(parents=True, exist_ok=True)
    (version_dir / "version").write_text(__version__ + "\n")
    action = "~" if is_upgrade else "+"
    console.print(f"  [green]{action}[/green] .learning-os/version ({__version__})")


def _init_git(target: Path, console: Console):
    """Initialize a git repo if one doesn't exist."""
    if not (target / ".git").exists():
        import subprocess
        result = subprocess.run(
            ["git", "init"], cwd=target, capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print("  [green]+[/green] git repository initialized")
