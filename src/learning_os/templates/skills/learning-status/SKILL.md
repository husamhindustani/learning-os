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

- Read `.learning-progress` for current track positions and timestamps
- Read `courses/REGISTRY.md` for the list of courses

### 2. For each course in REGISTRY.md

- Read `courses/[course-id]/COURSE.yaml`
- Find the last completed chapter: match `TRACK_[track]` value from `.learning-progress` against the chapter `id` fields in `chapters`
- **Important:** the stored chapter-id is the LAST COMPLETED chapter — the user has finished it and should move to the NEXT one
- Calculate progress: count chapters up to and including the last completed one
- Find next chapter: the chapter immediately after the last completed one in the `chapters` array

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
