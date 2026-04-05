# learning-os

An AI-native learning workspace scaffold. Turns any directory into a structured, self-improving learning system powered by [Agent Skills](https://agentskills.io/) (open standard).

Works with **Cursor**, **Claude Code**, and any AI tool that supports the Agent Skills standard.

---

## Install

Requires Python 3.9+.

**Recommended** — isolated CLI with [pipx](https://pip.pypa.io/en/stable/installation/) (install `pipx` with `pip install pipx` if needed):

```bash
pipx install learning-os
```

**Alternative** — inside a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install learning-os
```

To create courses from PDF/EPUB books, install with the book parsing extra:

```bash
pipx install 'learning-os[book]'
# or, in a venv:
pip install 'learning-os[book]'
```

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

Learning OS installs seven **Agent Skills** into your workspace. Skills are discovered automatically by the AI — no slash commands needed.

| Skill | Activates when you say... |
|---|---|
| `onboarding` | "hello", "help", "how do I start" (first time) |
| `learn` | "teach me X", "start chapter Y", "continue" |
| `chapter-check` | "quiz me", "test my understanding", "review [chapter]" |
| `save-progress` | "save my progress", "I'm done for today" |
| `create-course` | "create a course on X", "I want to learn Y" |
| `create-course-from-book` | "create a course from this book", "create a course from \<slug\>" |
| `learning-status` | "where am I?", "show my progress", "what's next?" |

### The workflow

```
1. Create a course   →  "create a course on Python basics"
                        or from a book: learning-os add-book <file>
                        then "create a course from <slug>"
2. Learn a chapter   →  "teach me python-basics data-types"
3. Do exercises      →  shown inline after teaching
4. Quiz yourself     →  "quiz me"
5. Save progress     →  "save my progress"
6. Repeat
```

Progress is saved to `.learning-progress` (JSON — tracks all completed chapters per course) and `notes/session-notes.md` (your learning journal) — readable, yours, and version-controlled if you choose to commit them.

---

## What gets installed

```
your-workspace/
├── .cursor/                        ← Cursor-specific (cursor, both)
│   ├── skills/                     ← 7 Agent Skills (or symlinks when --tool both)
│   ├── rules/
│   │   └── learning-mode.mdc       ← Pedagogical rule (globs: courses/**)
│   └── hooks/
│       └── hooks.json              ← Wires sessionEnd only
├── .claude/                        ← Claude Code-specific (claude, both)
│   ├── skills/                     ← Same 7 skills (or symlinks when --tool both)
│   ├── rules/
│   │   └── learning-mode.md        ← Same rule body (paths: courses/**)
│   └── settings.json               ← Wires SessionEnd only
├── CLAUDE.md                       ← Yours to customise; imports engine context via @
├── .learning-os/
│   ├── skills/                     ← Canonical skills (--tool both only)
│   ├── hooks/
│   │   └── session_end.py          ← Cross-platform session breadcrumb script
│   ├── CONTEXT.md                  ← Engine context imported by CLAUDE.md (auto-updated)
│   ├── config.json                 ← Workspace config (tool choice, used by upgrade)
│   └── version                     ← Engine version stamp
├── courses/                        ← your content (never touched by upgrades)
│   └── REGISTRY.md
├── books/                          ← imported books (created by add-book command)
│   └── <slug>/
│       ├── <original>.pdf
│       ├── book-outline.yaml
│       └── book-content/           ← extracted chapter text as markdown
├── notes/                          ← your session journal
└── .learning-progress              ← JSON progress file (written by save-progress skill)
```

Your `courses/`, `notes/`, and `.learning-progress` are **never touched** by upgrades — they belong to you.

`CLAUDE.md` is written once on `init` and never overwritten — customise it freely. The engine skills reference and constraints live in `.learning-os/CONTEXT.md`, which is refreshed on every `upgrade`.

When you use `--tool both`, skills are stored once in `.learning-os/skills/` and symlinked into `.cursor/skills/` and `.claude/skills/` to avoid duplication.

---

## AI Tool Support

Both Cursor and Claude Code are fully supported. All features work on both.

| Feature | Cursor | Claude Code |
|---|---|---|
| Skills | `.cursor/skills/` | `.claude/skills/` |
| Always-on context | `.cursor/rules/learning-mode.mdc` | `CLAUDE.md` → `@.learning-os/CONTEXT.md` |
| Session-end hook | `.cursor/hooks/hooks.json` → `sessionEnd` | `.claude/settings.json` → `SessionEnd` |
| Hook script | `.learning-os/hooks/session_end.py` (shared, cross-platform) | same |
| Progress tracking | `save-progress` skill writes `.learning-progress` directly | same |

The `session_end.py` hook is a safety net — if you close the AI tool without running `save-progress`, it writes a breadcrumb entry to `notes/session-notes.md`. Both hook configs are generated with the exact Python interpreter path at init time, so they work correctly regardless of platform or virtual environment.

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

The `create-course` skill handles this interactively — describe what you want to learn, answer a few targeted questions, and the agent proposes a full chapter outline for your approval before writing any files.

### Courses from books

Import a PDF or EPUB, then create a course from it:

```bash
learning-os add-book ~/books/system-design-interview.pdf
```

This extracts the table of contents and chapter text into `books/<slug>/`. Then in the AI chat, say "create a course from system-design-interview" — the agent reads the extracted content, maps book chapters to course chapters (grouping where needed), identifies gaps, and proposes a teaching plan.

During learning, the agent teaches from the book's content in its own words, supplemented with its own knowledge. Quizzes draw from both the book and the teaching session.

> Requires the `[book]` extra — see **Install**.

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

learning-os add-book <file>          Import a PDF/EPUB and extract chapters
  --dir <workspace>                 Workspace directory (default: current)

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

# Include book parsing support
pip install -e ".[dev,book]"

# Run tests
pytest tests/ -v
```

### Releasing (maintainers)

Releases are published to [PyPI](https://pypi.org/project/learning-os/) by GitHub Actions when you push a version tag matching `v*` (for example `v1.0.1`).

1. Bump the `version` in `pyproject.toml` on `main` (or your release branch) and merge.
2. Create and push the tag from the commit you want to ship:

   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

3. The **Publish to PyPI** workflow builds with Hatch and uploads using [trusted publishing](https://docs.pypi.org/trusted-publishers/) (OIDC). The PyPI project must have that integration configured for this repository’s `pypi` environment (see the comment in `.github/workflows/publish.yml`).

---

## License

MIT
