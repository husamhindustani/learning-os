# learning-os

An AI-native learning workspace scaffold. Turns any directory into a structured, self-improving learning system powered by [Agent Skills](https://agentskills.io/) (open standard).

Works with **Cursor**, **Claude Code**, and any AI tool that supports the Agent Skills standard.

---

## Install

```bash
pipx install learning-os
```

> Requires Python 3.9+. Install `pipx` with `pip install pipx` if needed.

---

## Quick Start

```bash
# Create a new learning workspace
mkdir my-learning && cd my-learning
learning-os init

# Or scaffold into an existing directory
learning-os init ~/my-learning

# Include a sample course to see the structure
learning-os init --with-sample
```

Then open the directory in Cursor (or your AI tool) and start a new chat. The onboarding skill will guide you through creating your first course.

---

## How it works

Learning OS installs six **Agent Skills** into your workspace. Skills are discovered automatically by the AI — no slash commands needed.

| Skill | Activates when you say... |
|---|---|
| `onboarding` | "hello", "help", "how do I start" (first time) |
| `learn` | "teach me X", "start chapter Y", "continue" |
| `chapter-check` | "quiz me", "test my understanding", "review [chapter]" |
| `save-progress` | "save my progress", "I'm done for today" |
| `create-course` | "create a course on X", "I want to learn Y" |
| `learning-status` | "where am I?", "show my progress", "what's next?" |

### The workflow

```
1. Create a course   →  "create a course on Python basics"
2. Learn a chapter   →  "teach me python-basics data-types"
3. Do exercises      →  shown inline after teaching
4. Quiz yourself     →  "quiz me"
5. Save progress     →  "save my progress"
6. Repeat
```

Progress is saved to `.learning-progress` and `notes/session-notes.md` in your workspace — readable, yours, and version-controlled if you choose to commit them.

---

## What gets installed

```
your-workspace/
├── .cursor/                        ← Cursor-specific (cursor, both)
│   ├── skills/                     ← 6 Agent Skills (or symlinks when --tool both)
│   │   ├── onboarding/
│   │   ├── learn/
│   │   ├── chapter-check/
│   │   ├── save-progress/
│   │   ├── create-course/
│   │   └── learning-status/
│   ├── rules/
│   │   └── learning-mode.mdc       ← Pedagogical rule (globs: courses/**)
│   └── hooks/
│       └── hooks.json              ← Wires sessionEnd only
├── .claude/                        ← Claude Code-specific (claude, both)
│   ├── skills/                     ← Same 6 skills (or symlinks when --tool both)
│   ├── rules/
│   │   └── learning-mode.md        ← Same rule body (paths: courses/**)
│   └── settings.json               ← Wires SessionEnd only
├── CLAUDE.md                       ← Always-on context for Claude Code
├── .learning-os/
│   ├── skills/                     ← Canonical skills (--tool both only)
│   ├── hooks/
│   │   └── session_end.py          ← Cross-platform session breadcrumb script
│   └── version                     ← Engine version stamp
├── courses/                        ← your content (never touched by upgrades)
│   └── REGISTRY.md
├── notes/                          ← your session journal
└── .learning-progress              ← progress snapshot (written by save-progress skill)
```

Your `courses/`, `notes/`, and `.learning-progress` are **never touched** by upgrades — they belong to you.

When you use `--tool both`, skills are stored once in `.learning-os/skills/` and symlinked into `.cursor/skills/` and `.claude/skills/` to avoid duplication.

---

## AI Tool Support

Both Cursor and Claude Code are fully supported. All features work on both.

| Feature | Cursor | Claude Code |
|---|---|---|
| Skills | `.cursor/skills/` | `.claude/skills/` |
| Always-on context | `.cursor/rules/learning-mode.mdc` | `CLAUDE.md` + `.claude/rules/learning-mode.md` |
| Session-end hook | `.cursor/hooks/hooks.json` → `sessionEnd` | `.claude/settings.json` → `SessionEnd` |
| Hook script | `.learning-os/hooks/session_end.py` (shared, cross-platform) | `.learning-os/hooks/session_end.py` (shared, cross-platform) |
| Progress tracking | `save-progress` skill writes `.learning-progress` directly | same |

The `session_end.py` hook is a safety net only — if you close the AI tool without running `save-progress`, it writes a breadcrumb entry to `notes/session-notes.md`. Progress tracking itself is handled entirely by the skill. When you choose `--tool both`, skills are installed in both `.cursor/` and `.claude/`, and both tools' configs are written.

When you run `learning-os init`, you're asked which tool you use. Choose `both` to configure for both.

---

## Courses

Learning OS ships with no courses — you create your own. Courses can cover any topic: programming languages, system design, language learning, music theory, anything.

Each course lives in `courses/[course-id]/` and is defined by a `COURSE.yaml` file:

```yaml
id: python-basics
title: "Python Basics"
track: python
type: programming
chapters:
  - id: data-types
    title: "Data Types & Variables"
    topics: ["int, float, str, bool", "Variables", "Type conversion"]
    exercises_section: "data-types"
progress:
  track_name: python
  section_mapping:
    data-types: "Data Types"
```

The `create-course` skill scaffolds the full structure for you — just describe what you want to learn.

### Sharing courses

Export a course to share it:

```bash
learning-os export python-basics -o python-basics.zip
```

Import a course from someone else:

```bash
learning-os import python-basics.zip
```

---

## Upgrade

```bash
# Update skills, hooks, and rules to the latest version
learning-os upgrade

# Upgrade a specific workspace
learning-os upgrade ~/my-learning
```

Upgrades never touch your `courses/`, `notes/`, or `.learning-progress`. The upgrade shows which version you're upgrading from and to.

---

## Commands

```
learning-os init [directory]        Scaffold a new workspace
  --with-sample                     Include a sample course
  --tool [cursor|claude|both]       AI tool to configure for

learning-os upgrade [directory]     Upgrade engine, preserve content

learning-os validate [directory]    Validate workspace and COURSE.yaml files

learning-os list [directory]        List courses and show progress

learning-os export <course-id>      Export a course as a .zip file
  --dir <workspace>                 Workspace directory (default: current)
  -o, --output <path>               Output file path

learning-os import <archive>        Import a course from a .zip file
  --dir <workspace>                 Workspace directory (default: current)
```

---

## Development

```bash
# Install in development mode with test dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

---

## License

MIT
