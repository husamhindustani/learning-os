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

`.learning-progress` is a JSON file that tracks completed chapters per course:

```json
{
  "tracks": {
    "[track-name]": {
      "completed": ["[chapter-id-1]", "[chapter-id-2]"],
      "last_saved": "[chapter-id]",
      "last_date": "YYYY-MM-DD HH:MM"
    }
  }
}
```

- `completed` — ordered list of all chapter IDs saved so far (append-only, never remove)
- `last_saved` — the chapter ID saved this session
- `last_date` — current timestamp

**How to update it:**
1. Read `.learning-progress` (start with `{"tracks": {}}` if the file is missing or empty)
2. Parse as JSON; find or create the key `tracks.[track-name]` (where `track-name` comes from `progress.track_name` in COURSE.yaml, falling back to `track`)
3. Append the chapter ID to `completed` if it is not already in the list
4. Set `last_saved` to the chapter ID
5. Set `last_date` to the current `YYYY-MM-DD HH:MM`
6. Write the file back as formatted JSON

**Example:** For java-evolution, chapter java9, track "java" (java8 was saved previously):
```json
{
  "tracks": {
    "java": {
      "completed": ["java8", "java9"],
      "last_saved": "java9",
      "last_date": "2026-01-15 10:30"
    }
  }
}
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

## Step 3a: Partial chapter saves (multi-session chapters)

When a chapter is taught across multiple sessions (typical for `large_chapter: true`, but also possible whenever the user has split a chapter by choice), capture the **chapter session plan** inside the notes entry so a fresh agent — Claude Code, Cursor, or any other Skills-compatible tool — can resume cleanly from notes alone.

**Differences from a normal save:**

1. **Skip Step 2** — do NOT add the chapter to `.learning-progress.completed` until the **final** session of that chapter. For partial saves, notes alone carry the record.

2. **Append `(Session N of M)`** to the Progress line after the chapter title.

3. **Insert a "Chapter session plan" block** between the Progress line and the Session summary. List all planned sessions with status markers:
   - ✅ for completed sessions
   - ⏳ for upcoming sessions

**Example partial entry:**

```markdown
## 2026-05-16

**Progress:** System Design Vol 1 — Design a Key-Value Store (Session 1 of 3) (quiz: 7/7)

**Chapter session plan:**
- ✅ **Session 1 — The Setup:** Single server vs distributed KV store, CAP theorem
- ⏳ **Session 2 — The Static Structure:** Data partitioning, replication, consistency models (quorum)
- ⏳ **Session 3 — The Dynamic Behavior:** Handling failures (gossip, merkle trees), write/read paths

**Session summary:**
- [usual session content]
- **Other learning:** [tangents, etc.]
```

**Subsequent partial saves:** the latest entry's `Chapter session plan` block is the source of truth. Carry it forward with updated checkmarks — copy the same plan block into the new entry and tick off the session that just completed.

**Final session save:** run Step 2 normally (add chapter to `completed`). The final entry's plan should show all sessions ✅.

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
