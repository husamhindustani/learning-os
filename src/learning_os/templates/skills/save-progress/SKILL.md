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

## Step 1: Determine course, chapter, and save type

**Identify course and chapter from conversation context:**
- Course names mentioned (e.g., "java-evolution", "react-advanced")
- Chapter/topic discussed (e.g., "Java 8", "hooks", "scalability")
- Files opened or referenced during the session
- Explicit input like "save progress for java-evolution java9"

**Load course metadata from `courses/[course-id]/COURSE.yaml`:**
- `title` → course display name
- `chapters[id]` → chapter display name
- `progress.track_name` → track identifier (key in `.learning-progress`); falls back to `track`
- `progress.section_mapping[chapter-id]` → chapter code

**If unclear:** Ask "Which course and chapter should I save? (e.g., 'java-evolution java9')"

**Then classify the save type** — this decides which JSON update path runs in Step 2:

| Save type | When |
|---|---|
| **Full chapter** | Chapter was taught in a single session (no split was negotiated). |
| **Partial session** | Chapter was split into sessions and a non-final session just completed. |
| **Final session** | Chapter was split, and the session that just completed is the last one in the plan. |
| **Plan revision** | The user changed the session breakdown mid-chapter (added/removed/retitled sessions). Combine with one of the above. |

The split state lives in `.learning-progress.tracks.[track-name].in_progress`. Read it first to see what's active for this track.

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
          {"id": "setup",            "title": "The Setup",            "topics": ["..."], "completed_date": "YYYY-MM-DD"},
          {"id": "static-structure", "title": "The Static Structure", "topics": ["..."]},
          {"id": "dynamic-behavior", "title": "The Dynamic Behavior", "topics": ["..."]}
        ]
      }
    }
  }
}
```

- `completed` — append-only list of completed chapter IDs
- `last_saved` / `last_date` — most recent save
- `in_progress` — present only while a chapter is split mid-way; cleared when the chapter completes
  - One in-progress chapter per track (enforced by `learn`)
  - Each session has `id` (slug of title), `title`, `topics` (list), and `completed_date` (set once the session is saved)
  - Session ordering is the array order

### Update path by save type

**Full chapter save:**
1. Read `.learning-progress` (start with `{"tracks": {}}` if missing/empty).
2. Find or create `tracks.[track-name]`.
3. Append `chapter-id` to `completed` if not already present.
4. Set `last_saved = chapter-id`, `last_date = now (YYYY-MM-DD HH:MM)`.
5. There should be no `in_progress` for this track. If there is one and its `chapter_id` matches the current chapter, treat as **Final session** instead (the user did one big session covering all remaining sessions).

**Partial session save (non-final):**
1. Read `.learning-progress`. The `in_progress` block for this track must already exist (created by `learn` when the user agreed to split).
2. Find the session in `in_progress.sessions[]` that was just completed (match by `id`, or by position = first session without `completed_date`).
3. Set its `completed_date` to today (`YYYY-MM-DD`).
4. Do **not** touch `completed`, `last_saved`, or `last_date` — those reflect chapter-level state, not session-level.
5. If `in_progress` is missing despite the user clearly being mid-split: create it now from conversation context (titles, topics per session). This is the only place `save-progress` can mint the block; normally `learn` does it.

**Final session save:**
1. Set the just-completed session's `completed_date` (as in partial).
2. Verify all sessions in `in_progress.sessions[]` now have `completed_date`. If any are missing, ask the user — final means final.
3. Append `in_progress.chapter_id` to `completed`.
4. Set `last_saved = chapter_id`, `last_date = now`.
5. Delete `in_progress` from this track.

**Plan revision (anytime):**
The user can change the split mid-chapter ("let's make this 4 sessions instead of 3" / "merge sessions 2 and 3" / "rename session 3").
1. Read existing `in_progress.sessions[]`.
2. Build the new sessions array per the user's revised plan.
3. For each new session whose `id` matches an existing one, preserve its `completed_date`.
4. If a session with `completed_date` would be removed by the revision, **stop and confirm** with the user ("you've already completed 'static-structure' — drop it anyway?"). Do not silently discard completion history.
5. Write back. If this revision happens alongside a save, run the appropriate Partial/Final flow after.

### Examples

**Partial session save** — Session 1 of 3 of design-a-key-value-store just completed:

```json
{
  "tracks": {
    "system-design": {
      "completed": ["scaling-zero-to-millions", "consistent-hashing", "rate-limiter", "estimation-and-design-framework"],
      "last_saved": "estimation-and-design-framework",
      "last_date": "2026-04-26 11:00",
      "in_progress": {
        "chapter_id": "design-a-key-value-store",
        "sessions": [
          {"id": "setup",            "title": "The Setup",            "topics": ["Single server vs distributed KV store", "CAP theorem"], "completed_date": "2026-05-16"},
          {"id": "static-structure", "title": "The Static Structure", "topics": ["Data partitioning", "Replication", "Consistency models (quorum)"]},
          {"id": "dynamic-behavior", "title": "The Dynamic Behavior", "topics": ["Handling failures (gossip, merkle trees)", "Write/read paths"]}
        ]
      }
    }
  }
}
```

Note: `completed` and `last_saved` are unchanged from the previous chapter; only the session inside `in_progress` got a date.

**Final session save** — Session 3 of 3 just completed:

```json
{
  "tracks": {
    "system-design": {
      "completed": ["scaling-zero-to-millions", "consistent-hashing", "rate-limiter", "estimation-and-design-framework", "design-a-key-value-store"],
      "last_saved": "design-a-key-value-store",
      "last_date": "2026-06-04 19:00"
    }
  }
}
```

`in_progress` is gone; chapter is in `completed`.

## Step 3: Write session notes

Append a new entry to the top of `courses/[course-id]/session-notes.md` (create the file with `# Session notes\n\n` header if missing). Session notes are per-course.

**Entry structure (any save type):**

```markdown
## YYYY-MM-DD

**Progress:** [Course Title] — [Chapter Title] [quiz score if taken, e.g. (quiz: 5/6)]

**Session summary:**
- [1-2 sentences covering main topics, exercises completed, demos run]
- **Other learning:** [Tangential topics, doubts addressed, clarifications, tools discussed. "None" if nothing.]
```

**For partial/final session saves**, prepend two things to the Progress line + add a plan block:

1. Append `(Session N of M)` to the Progress line (`N` is the 1-based index of the session that just completed, `M` is the total session count).
2. Insert a **Chapter session plan** block between the Progress line and the Session summary — derived from `.learning-progress.in_progress.sessions[]`:
   - ✅ for sessions with `completed_date`
   - ⏳ for sessions without

The plan block is for human readers of the journal. It is **derived from JSON, not the source of truth.** Never carry it forward by hand-editing — regenerate from `in_progress` each save.

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

**What to capture in the summary:**
- Main topics taught and exercises completed
- Doubts or questions the user had and how they were resolved
- Quiz results (score, notable right/wrong answers)
- Tangential topics explored
- Workflow changes (new skills, updated rules, etc.)

## Step 4: Confirm

Reply briefly:

> Progress saved: **[Course Title]** at **[Chapter Title]**[Session N of M if partial]. Session notes updated.

Do not ask for confirmation when the course and chapter are obvious from context.

## Notes

- Always write detailed session notes — they are the user's primary learning journal
- Capture doubts and clarifications — they are valuable for `chapter-check` review mode
- `.learning-progress` is the authoritative source for chapter and session state; the journal is narrative
- The Chapter session plan block in notes is derived display, not data — never trust it over `in_progress`
