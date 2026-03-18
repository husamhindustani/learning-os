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

- Read `.learning-progress` (JSON format) for per-track completion data
- Read `courses/REGISTRY.md` for the list of courses

**`.learning-progress` format:**
```json
{
  "tracks": {
    "[track-name]": {
      "completed": ["chapter-id-1", "chapter-id-2"],
      "last_saved": "chapter-id-2",
      "last_date": "YYYY-MM-DD HH:MM"
    }
  }
}
```

- `completed` — all chapter IDs the user has saved progress for (the authoritative completion list)
- `last_saved` — most recently saved chapter
- `last_date` — timestamp of last save


### 2. For each course in REGISTRY.md

- Read `courses/[course-id]/COURSE.yaml`
- Get the track name from the `track` field (or `progress.track_name` if set)
- Look up `tracks.[track-name]` in the progress data
- **Progress:** count how many chapter `id` values from `chapters` appear in `completed`
- **Next up:** the first chapter whose `id` is NOT in `completed`

### 3. Display format

```
Learning Progress
=================

[Course Title] ([course-id])
  Last completed: [Chapter Title]
  Progress:       [N]/[total] chapters ([%]%)
  Last saved:     [YYYY-MM-DD HH:MM]
  Next up:        [Next Chapter Title] — say "teach me [course-id] [next-chapter-id]"

[Course Title 2] ([course-id-2])
  Status: Not started — say "teach me [course-id-2]" to begin

---
Total: [N] chapters completed across [M] course(s)
```

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
