---
name: learning-status
description: >-
  Show learning progress across all courses. Use when the user asks 'where
  am I?', 'what have I done?', 'show my progress', 'what is next?',
  'how far along am I?', 'learning status', or 'what courses do I have?'.
---

# Learning Status

Show an overview of all courses and the user's progress.

## What to display

### 1. Read progress data

- Read `.learning-progress` (JSON format) for per-track completion and in-progress data
- Read `courses/REGISTRY.md` for the list of courses

The schema:

```json
{
  "tracks": {
    "[track-name]": {
      "completed": ["chapter-id-1", "chapter-id-2"],
      "last_saved": "chapter-id-2",
      "last_date": "YYYY-MM-DD HH:MM",
      "in_progress": {
        "chapter_id": "...",
        "sessions": [
          {"id": "...", "title": "...", "topics": [...], "completed_date": "YYYY-MM-DD"},
          {"id": "...", "title": "...", "topics": [...]}
        ]
      }
    }
  }
}
```

- `completed` — authoritative completion list (chapter IDs)
- `last_saved` / `last_date` — most recent save
- `in_progress` — present only when a chapter is mid-way through a user-defined split. Sessions with `completed_date` are done; those without are pending. Do not read session-notes.md for plan state — `in_progress` is the source of truth.

### 2. For each course in REGISTRY.md

- Read `courses/[course-id]/COURSE.yaml`
- Get the track name from `progress.track_name` (falling back to `track`)
- Look up `tracks.[track-name]` in the progress data
- **Progress:** count how many chapter `id` values from `chapters` appear in `completed`
- **In progress:** if `in_progress` exists, resolve `chapter_id` → chapter title from `COURSE.yaml.chapters[]`, count sessions with `completed_date` vs total
- **Next up:**
  - If `in_progress` exists → next session (first without `completed_date`); display its title.
  - Else → first chapter whose `id` is NOT in `completed`.

### 3. Display format

```
Learning Progress
=================

[Course Title] ([course-id])
  Last completed: [Chapter Title]
  In progress:    [Chapter Title] ([sessions completed]/[total sessions] sessions)   ← only if applicable
  Progress:       [N]/[total] chapters ([%]%)
  Last saved:     [YYYY-MM-DD HH:MM]
  Next up:        [Next Chapter Title] — say "teach me [course-id] [next-chapter-id]"

[Course Title 2] ([course-id-2])
  Status: Not started — say "teach me [course-id-2]" to begin

---
Total: [N] chapters completed across [M] course(s)
```

**When `in_progress` is present for the track:**
- Show the `In progress:` line between `Last completed:` and `Progress:`.
- Set `Next up:` to point at the next session, e.g. `Session N — [session title] of [Chapter Title] — say "continue [course-id]"`.
- Do NOT count the in-progress chapter toward the completed total (it isn't done yet).

### 4. If no progress at all

```
No progress saved yet.

You have [N] course(s) available:
  - [course-id]: [Course Title]
  - [course-id-2]: [Course Title 2]

Say "teach me [course-id]" to start learning.
```

### 5. If no courses exist

```
No courses set up yet.

Say "create a course" and I'll help you set one up for any topic you want to learn.
```

## Additional context

After showing status, offer to help:
- "Say 'continue' to pick up where you left off"
- "Say 'review [chapter]' to quiz yourself on a past chapter"
- "Say 'create a course' to add a new topic"
