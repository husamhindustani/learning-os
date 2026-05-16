# Future Work — Learning OS

A running list of feature ideas, design debt, and revisits. These are not committed plans — they're a memory aid for the next time we open the repo with energy to improve it.

Items are grouped by theme, not strictly by priority. Each entry includes the problem, a proposed direction, and any context worth remembering.

---

## Sessions as a first-class concept

**Problem.** Today, large chapters are split into "sessions" ad-hoc during the `learn` skill — the breakdown is negotiated in conversation, never persisted in any schema. We added a lightweight convention (2026-05-16) where `save-progress` writes a `Chapter session plan` block into `courses/<course-id>/session-notes.md`, and `learn` reads it back on resume. This works but is a string-matching contract over markdown, not real data.

**Proposed direction.**

1. **Extend `COURSE.yaml`** with an optional `sessions:` array per chapter:
   ```yaml
   - id: design-a-key-value-store
     topics: [...]
     large_chapter: true
     sessions:
       - id: setup
         title: "The Setup"
         topics: ["Single server vs distributed KV store", "CAP theorem"]
       - id: static-structure
         title: "The Static Structure"
         topics: ["Data partitioning", "Replication", "Quorum consensus"]
   ```
   Author-defined sessions become the default split. User can still override per-conversation.

2. **Extend `.learning-progress`** with an `in_progress` block:
   ```json
   {
     "tracks": {
       "system-design": {
         "completed": [...],
         "in_progress": {
           "design-a-key-value-store": {
             "sessions_completed": ["setup"],
             "last_session": "setup",
             "last_date": "..."
           }
         }
       }
     }
   }
   ```
   When all sessions complete, atomically move chapter from `in_progress` to `completed`.

3. **Update skills:**
   - `learn` — read structured progress instead of grepping notes.
   - `save-progress` — write structured progress; deprecate (but don't remove) the markdown convention for backward compatibility.
   - `learning-status` — read structured progress directly.
   - `create-course` and `create-course-from-book` — optionally elicit sessions when proposing chapter outlines for large chapters.

**Backward compatibility.** Courses without `sessions:` keep working — the ad-hoc split + notes convention continues to function. Migration is opt-in per course.

**Open design questions.**
- If a user splits differently from the COURSE.yaml `sessions`, do we honor user IDs or coerce to author IDs? Probably honor user IDs in `.learning-progress` and treat `sessions:` as default suggestions, not strict schema.
- Session ID stability — if an author renames a session after users have started, existing progress points to a missing ID. Resolve with lenient title-fallback matching or a one-time migration helper.

---

## Re-evaluate session-end auto-capture hook

**Status.** Disabled 2026-05-16 (in `scaffold.py`). Script preserved at `templates/hooks/session_end.py`.

**Original purpose.** Write a breadcrumb to the active course's `courses/<course-id>/session-notes.md` if the user closes their AI tool without running `save my progress`, so no session is invisible in the journal.

**Why disabled.** Both Claude Code and Cursor retain session context across reopens. The breadcrumb fires on every `SessionEnd` regardless of whether the user actually lost context — producing noise that has to be cleaned up by hand. In practice the user (and the agent) can reconstruct session intent from the live conversation when reopening.

**Possible revisits.**
- If multi-day breaks become common and the live conversation is genuinely gone, a breadcrumb has value. Consider re-enabling with a smarter trigger (only fire if no `save-progress` happened in the last 24h, say).
- Or: replace the hook with an in-skill nudge — when `learn` is invoked and the user hasn't saved in N days, prompt "want me to save the previous session first?"

---

## learning-status CLI command parity

**Problem.** The `learning-status` skill was updated (2026-05-16) to display in-progress chapters from the notes-based session plan. The CLI command `learning-os list` still shows only `.learning-progress.completed` and won't reflect partial-chapter state.

**Proposed direction.** Bring the CLI to parity — for each course, read `courses/<course-id>/session-notes.md` for `Chapter session plan` blocks, surface in-progress chapters in the listing output. Same logic as the skill, implemented in `scaffold.py` / `cli.py`.

**Priority.** Low. The skill covers the interactive case (where the user actually is when they ask). The CLI is for occasional external inspection.

---

## chapter-check session-level review

**Problem.** `chapter-check` has three modes: current session (no args), review chapter (chapter ID), focus topic (chapter + topic). There's no clean way to say *"review me on session 2 of design-a-key-value-store"* — it'd fall through to chapter-wide review.

**Proposed direction.** Add a session-aware pattern to Step 1 of `chapter-check/SKILL.md`:
- "review session N of [chapter]" → load only that session's topics (from notes' session plan block, or from COURSE.yaml `sessions:` once that exists)
- Use the per-session quiz coverage from the original session-notes entry as a starting point

**Priority.** Medium — useful as sessions become more common.

---

## Onboarding "Returning User" enhancement

**Problem.** The `onboarding` skill's Returning User flow reads `.learning-progress.last_date` and shows "you left off at [last completed chapter]". It doesn't surface in-progress chapters.

**Proposed direction.** Also scan notes for partial state; if a chapter is mid-progress, show "Last activity: Session 1 of [Chapter] (1 of 3 sessions complete)" instead of (or alongside) the last-completed line.

**Priority.** Low. Cosmetic.

---

## Notes on the lightweight session-plan convention (2026-05-16)

Recording the shape so we don't re-derive it when migrating to first-class sessions:

- **Where it lives:** Top entry in `courses/<course-id>/session-notes.md` per partial save.
- **Trigger for partial save:** Conversation context indicates "Session N of M" — not strictly tied to `large_chapter: true`.
- **Format:**
  ```markdown
  **Progress:** [Course] — [Chapter] (Session N of M) (quiz: X/Y)

  **Chapter session plan:**
  - ✅ **Session 1 — Title:** topics
  - ⏳ **Session 2 — Title:** topics
  - ⏳ **Session 3 — Title:** topics
  ```
- **`.learning-progress` rule:** NOT updated for partial saves. Only updated when chapter's final session completes (then chapter is appended to `completed`).
- **Resume logic:** `learn` reads top notes entry; if it finds a plan block with ⏳ entries, the first ⏳ is the next session.
- **Display:** `learning-status` skill shows `In progress: [Chapter] (1/3 sessions)`.

This convention is fully self-contained in notes — no schema changes were needed. When the first-class sessions feature lands, the structured data takes precedence and this markdown contract becomes a fallback for old entries (or is migrated and dropped).
