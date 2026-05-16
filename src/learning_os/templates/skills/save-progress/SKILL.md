---
name: save-progress
description: >-
  Save learning progress and write session notes. Use when the user says
  'save my progress', 'save progress', 'I am done for today', 'wrap up',
  'end session', or has just finished a chapter and quiz and wants to record
  their work.
---

# Save Progress

Three steps: identify the chapter, update `.learning-progress`, write a journal entry.

## Step 1: Identify the course and chapter

From conversation context or explicit input ("save progress for java-evolution java9"):
- **Course** (e.g., `java-evolution`) and **chapter** (e.g., `java9`)
- Files opened or referenced during the session

Load `courses/[course-id]/COURSE.yaml`:
- `title` → course display name
- `chapters[id]` → chapter display name and `topics` list
- `progress.track_name` (or `track`) → track key in `.learning-progress`

If unclear: ask "Which course and chapter should I save?"

## Step 2: Update `.learning-progress`

### Schema

```json
{
  "tracks": {
    "[track-name]": {
      "completed": ["chapter-id-1", "chapter-id-2"],
      "last_saved": "chapter-id-2",
      "last_date": "YYYY-MM-DD HH:MM",
      "in_progress": {
        "chapter_id": "design-a-key-value-store",
        "sessions": [
          {"title": "The Setup",            "topics": ["..."], "completed": true},
          {"title": "The Static Structure", "topics": ["..."], "completed": false},
          {"title": "The Dynamic Behavior", "topics": ["..."], "completed": false}
        ]
      }
    }
  }
}
```

- `completed` — append-only list of finished chapter IDs
- `last_saved` / `last_date` — most recent chapter-level save
- `in_progress` — present only while a chapter is mid-split. Each session has `title`, `topics`, `completed: true|false`. **Identity is by title.** Order in the array is the teaching order.

### The fork: is the chapter complete after this session?

Decide once. The rest of Step 2 is deterministic JSON updates.

A chapter is **complete** if every topic in `COURSE.yaml.chapters[id].topics` has been taught — either this session or in a prior session (whose topics are in `in_progress.sessions[].topics` with `completed: true`).

**Path A — Yes, the chapter is complete:**

1. Read `.learning-progress` (start with `{"tracks": {}}` if missing or empty).
2. Find or create `tracks.[track-name]`.
3. Append `chapter-id` to `completed` (only if not already there).
4. Set `last_saved = chapter-id`, `last_date = now (YYYY-MM-DD HH:MM)`.
5. If `in_progress` exists for this track, **delete it** — chapter is done.
6. Write the file.

**Path B — No, more sessions remain:**

1. Read `.learning-progress`.
2. **If `tracks.[track-name].in_progress` exists** for this chapter:
   - Find the session matching today's session by `title` (it's the session whose topics you taught this session — usually the first one with `completed: false`).
   - Set its `completed` to `true`.
3. **If `in_progress` does not exist** (user is mid-chapter but didn't pre-declare a split):
   - Mint it on the fly. Build `sessions[]`:
     - One session with today's topics, `"completed": true`.
     - One session with the remaining topics from `COURSE.yaml.chapters[id].topics`, `"completed": false`.
   - Titles can be plain ("Session 1 — [theme]" / "Session 2 — [theme]") inferred from the topic groups, or just `"Session 1"` / `"Session 2"` if no clean theme.
   - Confirm with the user in one line: *"Saving as Session 1 of 2 for **[chapter title]**. Today: [topics]. Remaining: [topics]. OK?"*
   - Wait for confirmation, then write `in_progress`.
4. Do **not** touch `completed`, `last_saved`, or `last_date`. Those are chapter-level; this is session-level.
5. Write the file.

### Plan revision (anytime)

If the user wants to change the split mid-chapter ("make this 4 sessions instead of 3" / "merge sessions 2 and 3"):

1. Rebuild `in_progress.sessions[]` per the user's new plan.
2. For each new session whose `title` matches an existing one, preserve its `completed` value.
3. If a session with `completed: true` would be removed, **stop and confirm**: *"You've already completed '[title]' — drop it anyway?"* Never silently discard completion history.
4. Write back. Continue with the appropriate fork (A or B) for this save.

### Examples

**Path A** — finishing `consistent-hashing` (one-shot, no split):

```json
{
  "tracks": {
    "system-design": {
      "completed": [..., "consistent-hashing"],
      "last_saved": "consistent-hashing",
      "last_date": "2026-04-26 18:31"
    }
  }
}
```

**Path B** — completing Session 1 of 3 for `design-a-key-value-store` (split was pre-declared in `learn`):

```json
{
  "tracks": {
    "system-design": {
      "completed": [..., "consistent-hashing"],
      "last_saved": "consistent-hashing",
      "last_date": "2026-04-26 18:31",
      "in_progress": {
        "chapter_id": "design-a-key-value-store",
        "sessions": [
          {"title": "The Setup",            "topics": ["Single server vs distributed KV store", "CAP theorem"], "completed": true},
          {"title": "The Static Structure", "topics": ["Data partitioning", "Replication", "Quorum consensus"], "completed": false},
          {"title": "The Dynamic Behavior", "topics": ["Handling failures (gossip, merkle trees)", "Write/read paths"], "completed": false}
        ]
      }
    }
  }
}
```

`completed` and `last_saved` are unchanged — they're chapter-level state.

**Path A on the final session** — Session 3 of 3 just completed, chapter is now done:

```json
{
  "tracks": {
    "system-design": {
      "completed": [..., "consistent-hashing", "design-a-key-value-store"],
      "last_saved": "design-a-key-value-store",
      "last_date": "2026-06-04 19:00"
    }
  }
}
```

`in_progress` is gone; chapter is in `completed`.

## Step 3: Write session notes

Append a new entry to the **top** of `courses/[course-id]/session-notes.md` (create with `# Session notes\n\n` header if missing). Session notes are per-course.

**Entry structure:**

```markdown
## YYYY-MM-DD

**Progress:** [Course Title] — [Chapter Title][optional: (Session N of M) if mid-split] [optional: (quiz: X/Y)]

[optional: Chapter session plan block — see below]

**Session summary:**
- [1-2 sentences covering main topics, exercises completed, demos run]
- **Other learning:** [Tangential topics, doubts addressed, clarifications, tools discussed. "None" if nothing.]
```

**Chapter session plan block** — include only when `in_progress` exists for this chapter (i.e. Path B was taken, or Path A on the final session of a previously-split chapter). Derive it from `in_progress.sessions[]`:
- ✅ for sessions with `completed: true`
- ⏳ for sessions with `completed: false`

The block is for human readers of the journal. **It is derived from JSON, never the source of truth** — never hand-carry it forward across entries; regenerate each save.

**Example partial entry:**

```markdown
## 2026-05-16

**Progress:** System Design Vol 1 — Design a Key-Value Store (Session 1 of 3) (quiz: 7/7)

**Chapter session plan:**
- ✅ **The Setup:** Single server vs distributed KV store, CAP theorem
- ⏳ **The Static Structure:** Data partitioning, replication, consistency models (quorum)
- ⏳ **The Dynamic Behavior:** Handling failures (gossip, merkle trees), write/read paths

**Session summary:**
- [usual session content]
- **Other learning:** [tangents, etc.]
```

**What to capture in the summary:**
- Topics taught, exercises completed, demos run
- Doubts the user had and how they were resolved
- Quiz results (score, notable right/wrong answers)
- Tangential topics explored
- Workflow changes

## Step 4: Confirm

Reply briefly:

> Progress saved: **[Course Title]** at **[Chapter Title]**[ (Session N of M) if mid-split]. Session notes updated.

Do not ask for confirmation when context is clear. The only required confirmation is the on-the-fly split mint in Path B step 3 (above).

## Notes

- `.learning-progress` is authoritative for chapter and session state; the journal is narrative
- The plan block in notes is derived display — never trust it over `in_progress`
- Capture doubts and clarifications in the journal — they feed `chapter-check` review mode
