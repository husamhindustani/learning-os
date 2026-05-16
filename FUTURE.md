# Future Work — Learning OS

A running list of feature ideas, design debt, and revisits. These are not committed plans — they're a memory aid for the next time we open the repo with energy to improve it.

Items are grouped by theme, not strictly by priority. Each entry includes the problem, a proposed direction, and any context worth remembering.

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

**Problem.** The `learning-status` skill displays in-progress chapters by reading `.learning-progress.tracks.[track].in_progress`. The CLI command `learning-os list` still shows only `completed` and won't reflect partial-chapter state.

**Proposed direction.** Bring the CLI to parity — read `.learning-progress.in_progress` for each track, surface in-progress chapters in the listing output. Same logic as the skill, implemented in `scaffold.py` / `cli.py`.

**Priority.** Low. The skill covers the interactive case (where the user actually is when they ask). The CLI is for occasional external inspection.

---

## chapter-check session-level review

**Problem.** `chapter-check` has three modes: current session (no args), review chapter (chapter ID), focus topic (chapter + topic). There's no clean way to say *"review me on session 2 of design-a-key-value-store"* — it'd fall through to chapter-wide review.

**Proposed direction.** Add a session-aware pattern to Step 1 of `chapter-check/SKILL.md`:
- "review session N of [chapter]" → if the chapter is currently in `.learning-progress.in_progress`, load only that session's `topics` and quiz on them.
- For completed chapters, this is a gap: `in_progress` is cleared on completion. If the use case becomes real, archive the final session list into the `completed` entry (today it's a flat list of chapter IDs; would become a list of `{id, sessions: [...]}` objects).

**Priority.** Medium — useful as sessions become more common.
