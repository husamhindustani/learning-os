"""Workspace scaffolding and upgrade logic."""

import shutil
import stat
from pathlib import Path

from rich.console import Console


TEMPLATES_DIR = Path(__file__).parent / "templates"

# User-owned paths — never overwritten by init or upgrade.
USER_PATHS = [
    "courses/",
    "notes/",
    ".learning-progress",
]


def scaffold_workspace(directory: str, tool: str, with_sample: bool, console: Console):
    """Scaffold a fresh Learning OS workspace."""
    target = Path(directory).resolve()
    target.mkdir(parents=True, exist_ok=True)

    console.print(f"[dim]Target:[/dim] {target}")
    console.print()

    _copy_engine(target, tool, console, is_upgrade=False)
    _scaffold_user_structure(target, console)

    if with_sample:
        _copy_sample(target, console)

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

    # Detect which tool(s) were originally configured
    has_cursor = (target / ".cursor" / "skills").exists()
    has_claude = (target / ".claude" / "skills").exists()
    if has_cursor and has_claude:
        tool = "both"
    elif has_claude:
        tool = "claude"
    else:
        tool = "cursor"

    _copy_engine(target, tool, console, is_upgrade=True)

    console.print()
    console.print("[bold green]Upgrade complete![/bold green]")
    console.print("[dim]Your courses, notes, and progress were not changed.[/dim]")


def _copy_engine(target: Path, tool: str, console: Console, is_upgrade: bool):
    """Copy all engine files into the workspace.

    Layout produced:
      .cursor/skills/*/                 — Cursor skill discovery (cursor, both)
      .claude/skills/*/                 — Claude Code skill discovery (claude, both)
      .cursor/rules/learning-mode.mdc   — Cursor rule (globs: frontmatter)
      .claude/rules/learning-mode.md    — Claude Code rule (paths: frontmatter)
      CLAUDE.md                         — Claude Code always-on context (claude, both)
      .cursor/hooks/hooks.json          — Cursor hook wiring — sessionEnd only (cursor, both)
      .claude/settings.json             — Claude Code hook wiring — SessionEnd only (claude, both)
      .learning-os/hooks/session-end.sh — Shared session breadcrumb script (always)

    Progress tracking (.learning-progress) is written directly by the save-progress
    skill — no bash scripts involved.
    """
    action = "~" if is_upgrade else "+"
    skills_src = TEMPLATES_DIR / "skills"
    rules_src = TEMPLATES_DIR / "rules"
    hooks_src = TEMPLATES_DIR / "hooks"
    claude_src = TEMPLATES_DIR / "claude"

    use_cursor = tool in ("cursor", "both")
    use_claude = tool in ("claude", "both")

    # ── Skills ────────────────────────────────────────────────────────────────
    # Skills go to .cursor/skills/ for Cursor and .claude/skills/ for Claude.
    # Both locations are supported by the open Agent Skills standard.
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
    # Cursor: .cursor/rules/*.mdc  (globs: frontmatter)
    # Claude Code: .claude/rules/*.md  (paths: frontmatter)
    # The .mdc file uses 'globs:' and the .md file uses 'paths:' — same body.
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

        # CLAUDE.md — always-on context loaded at every Claude Code session
        claude_md_dest = target / "CLAUDE.md"
        if not claude_md_dest.exists() or is_upgrade:
            shutil.copy2(claude_src / "CLAUDE.md", claude_md_dest)
            console.print(f"  [green]{action}[/green] CLAUDE.md")

    # ── Shared hook scripts ────────────────────────────────────────────────────
    # Scripts live at .learning-os/hooks/ — a neutral location reachable by
    # both Cursor (.cursor/hooks.json) and Claude Code (.claude/settings.json).
    shared_hooks_dest = target / ".learning-os" / "hooks"
    shared_hooks_dest.mkdir(parents=True, exist_ok=True)
    for sh in hooks_src.glob("*.sh"):
        dest = shared_hooks_dest / sh.name
        shutil.copy2(sh, dest)
        dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        console.print(f"  [green]{action}[/green] .learning-os/hooks/{sh.name}")

    # ── Hook config: Cursor ────────────────────────────────────────────────────
    # hooks.json tells Cursor which events to listen for and where the scripts are.
    if use_cursor:
        cursor_hooks_dir = target / ".cursor" / "hooks"
        cursor_hooks_dir.mkdir(parents=True, exist_ok=True)
        _write_cursor_hooks_json(cursor_hooks_dir / "hooks.json", action, console)

    # ── Hook config: Claude Code ───────────────────────────────────────────────
    # settings.json tells Claude Code which events to listen for.
    # Uses SessionEnd only — progress tracking is handled directly by the skill.
    if use_claude:
        claude_dir = target / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(claude_src / "settings.json", claude_dir / "settings.json")
        console.print(f"  [green]{action}[/green] .claude/settings.json")



def _write_cursor_hooks_json(dest: Path, action: str, console: Console):
    """Write Cursor hooks.json pointing to the shared session-end script."""
    import json
    config = {
        "version": 1,
        "hooks": {
            "sessionEnd": [
                {
                    "command": ".learning-os/hooks/session-end.sh",
                    "description": "Auto-capture session breadcrumb to notes/session-notes.md",
                }
            ],
        },
    }
    dest.write_text(json.dumps(config, indent=2) + "\n")
    console.print(f"  [green]{action}[/green] .cursor/hooks/hooks.json")


def _scaffold_user_structure(target: Path, console: Console):
    """Create user-owned structure only if not already present."""
    # courses/REGISTRY.md
    registry_path = target / "courses" / "REGISTRY.md"
    if not registry_path.exists():
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TEMPLATES_DIR / "courses" / "REGISTRY.md", registry_path)
        console.print("  [green]+[/green] courses/REGISTRY.md")

    # notes/
    notes_dir = target / "notes"
    if not notes_dir.exists():
        notes_dir.mkdir(parents=True)
        (notes_dir / ".gitkeep").touch()
        console.print("  [green]+[/green] notes/")

    # .learning-progress
    progress_file = target / ".learning-progress"
    if not progress_file.exists():
        progress_file.touch()
        console.print("  [green]+[/green] .learning-progress")

    # .gitignore (merge or create)
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
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    console.print(f"  [green]{label}[/green]")


def _ensure_gitignore(target: Path, console: Console):
    """Add Learning OS entries to .gitignore if not already present."""
    gitignore = target / ".gitignore"
    entries = [
        "# Learning OS — auto-generated, do not delete",
        ".learning-progress",
        "*.pyc",
        "__pycache__/",
    ]
    existing = gitignore.read_text() if gitignore.exists() else ""
    additions = [e for e in entries if e not in existing and not e.startswith("#")]
    if additions:
        with gitignore.open("a") as f:
            if existing and not existing.endswith("\n"):
                f.write("\n")
            f.write("\n# Learning OS\n")
            f.write("\n".join(additions) + "\n")
        console.print("  [green]+[/green] .gitignore (updated)")


def _init_git(target: Path, console: Console):
    """Initialize a git repo if one doesn't exist."""
    if not (target / ".git").exists():
        import subprocess
        result = subprocess.run(
            ["git", "init"], cwd=target, capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print("  [green]+[/green] git repository initialized")
