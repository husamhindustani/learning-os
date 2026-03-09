# Learning OS Workspace

This is a Learning OS workspace — an AI-native learning environment for any topic.

## What this workspace is

Learning OS provides a structured, self-improving learning system. You have six Agent Skills available that handle all learning interactions:

- **onboarding** — activates automatically on first use or when no courses exist
- **learn** — teaches chapter content one concept at a time
- **chapter-check** — quizzes after a chapter (current session or historical review)
- **save-progress** — saves session notes and updates progress tracking
- **create-course** — scaffolds a new course for any topic
- **learning-status** — shows progress across all courses

## How to behave

When the user is doing learning-related work (teaching, quizzing, saving progress, creating courses), activate the appropriate skill automatically — do not wait for explicit slash commands.

When the user is in `courses/` or asking about a concept they are learning, apply the pedagogical approach from `learn` skill's `references/PEDAGOGY.md`:
- One concept at a time
- Examples before definitions
- Check understanding before moving on

## File structure

```
courses/              ← user's learning content (never modify without instruction)
  REGISTRY.md         ← course catalog
  [course-id]/
    COURSE.yaml       ← course definition (schema in learn skill references)
    LEARNING_PLAN.md
    EXERCISES.md
notes/
  session-notes.md    ← learning journal (append-only, newest entry at top)
.learning-progress    ← key-value progress snapshot (written by save-progress skill)
.learning-os/
  hooks/              ← shared automation scripts (session breadcrumb only)
```

## Important constraints

- Never delete or overwrite files in `courses/`, `notes/`, or `.learning-progress` without explicit user instruction
- Session notes are append-only — always add new entries at the top
- COURSE.yaml files follow the canonical schema (see `learn` skill references/COURSE_SCHEMA.md)
