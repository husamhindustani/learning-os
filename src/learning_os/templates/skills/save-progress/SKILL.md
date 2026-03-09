---
name: save-progress
description: >-
  Save learning progress and write session notes. Use when the user says
  'save my progress', 'save progress', 'I am done for today', 'wrap up',
  'end session', or has just finished a chapter and quiz and wants to record
  their work.
---

# Save Progress

Save session notes to the learning journal and update the progress snapshot.
No scripts or external tools — everything is a direct file write.

## Step 1: Determine course and chapter

**From conversation context:**
- Look for course names mentioned (e.g., "java-evolution", "react-advanced")
- Look at chapter/topic discussed (e.g., "Java 8", "hooks", "scalability")
- Look at files opened or referenced during the session

**From explicit user input:**
- "save progress for java-evolution java9" → use those directly

**Load course metadata from `courses/[course-id]/COURSE.yaml`:**
- `title` → course display name
- `chapters[id]` → chapter display name
- `progress.track_name` → track identifier (used as the key in `.learning-progress`)
- `progress.section_mapping[chapter-id]` → chapter code (used as the value)

**If unclear:** Ask "Which course and chapter should I save? (e.g., 'java-evolution java9')"

## Step 2: Update `.learning-progress`

`.learning-progress` is a plain key-value file. Each line tracks one course:

```
TRACK_[track-name]=[chapter-id] [YYYY-MM-DD HH:MM]
```

**How to update it:**
1. Read `.learning-progress` (create it if it doesn't exist)
2. Find the line starting with `TRACK_[track-name]=` (where `track-name` comes from `progress.track_name` in COURSE.yaml)
3. Replace that line with the updated value, or append it if not found
4. Write the file back

**Example:** For java-evolution, chapter java9, track "java":
```
TRACK_java=java9 2026-01-15 10:30
```

## Step 3: Write session notes

Append a new entry to `notes/session-notes.md` (create the file if it doesn't exist).

**New entries go at the TOP** of the file, directly after the `# Session notes` header.

**Entry structure:**

```markdown
## YYYY-MM-DD

**Progress:** [Course Title] — [Chapter Title] [quiz score if taken, e.g. (quiz: 5/6)]

**Session summary:**
- [1-2 sentences covering main topics, exercises completed, demos run]
- **Other learning:** [Tangential topics, doubts addressed, clarifications, tools discussed. "None" if nothing.]
```

**What to capture:**
- Main chapter topics taught and exercises completed
- Any doubts or questions the user had and how they were resolved
- Quiz results (score and notable right/wrong answers)
- Tangential topics explored (patterns, tools, related concepts)
- Workflow changes (new skills, updated rules, etc.)

**Example entry:**

```markdown
# Session notes

## 2026-03-10

**Progress:** Python Basics — Data Types & Variables (quiz: 5/6)

**Session summary:**
- Covered int, float, str, bool, variable assignment, and type conversion. Completed 3 exercises including a temperature converter and string formatter.
- **Other learning:** Discussed mutable vs immutable types in depth (user confused about why str is immutable). Clarified type() vs isinstance() — isinstance() is preferred. User asked about f-strings vs .format() — covered both.
```

## Step 4: Confirm

Reply briefly:

> Progress saved: **[Course Title]** at **[Chapter Title]**. Session notes updated.

Do not ask for confirmation when the course and chapter are obvious from context.

## Notes

- Always write detailed session notes — these are the user's primary learning journal
- Include quiz scores if a quiz was taken this session
- Capture doubts and clarifications — they are valuable for the review mode of `chapter-check`
- The session notes are also read by `chapter-check` review mode to reconstruct context
- `.learning-progress` is the fast-lookup index; `session-notes.md` is the full record
