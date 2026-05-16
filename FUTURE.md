# Future Work — Learning OS

A running list of feature ideas, design debt, and revisits. These are not committed plans — they're a memory aid for the next time we open the repo with energy to improve it.

Each entry includes the problem, a proposed direction, and a priority. Items are sorted by priority (highest first), then by ratio of value to effort within each band.

**Priority key:**
- **P1 — High.** Clear user value, modest effort, evidence the gap matters.
- **P2 — Medium.** Useful when the context arises; low-to-medium effort.
- **P3 — Low.** Cosmetic, hypothetical, or busywork. Pick up only if itching.

---

## Spaced retention prompts

**Priority.** P1.

**Problem.** Learners manually note "revisit this chapter in 1-2 weeks" — the System Design notes have at least two such reminders the user wrote by hand. The system already knows when each chapter was last touched (`.learning-progress.tracks.[track].last_date` and per-chapter dates in journal entries) but never surfaces "this is due for a refresh."

**Proposed direction.**
- Add a staleness threshold (default ~30 days since chapter completion; per-track override possible later).
- In `learning-status`, append a "Review due" section listing completed chapters past the threshold, each with a `review [chapter]` hint.
- In `onboarding` Returning User flow, if any chapters are due, mention one — "It's been [N] days since you finished **[chapter]**. Want a quick refresh? Say 'review [chapter]'."
- `chapter-check` review mode already exists — this just creates demand for it.

**Open questions.**
- Cadence: single global threshold vs. per-course in `COURSE.yaml`? Start global; add overrides only if needed.
- Risk of nagging — gate behind a "show me what's due" prompt rather than firing unprompted on every status check.

**Why P1.** Real user behavior is being done by hand; the data already exists; the change is contained to two skills.

---

## Followups tracker

**Priority.** P1.

**Problem.** At the end of session notes, learners frequently write `**Topics to pick up later:**` sections — concrete callbacks like "build a hot-key caching project with Redis pub/sub" or "do a sharding deep dive if News Feed chapter doesn't cover it." The System Design journal has at least three such open followups across different entries. None of them surface anywhere; the user has to remember they wrote them.

**Proposed direction.**
- Formalize a `followups:` array on each track in `.learning-progress`, with entries like `{"text": "...", "from_chapter": "...", "added_date": "..."}`.
- `save-progress` parses any `**Topics to pick up later:**` block in the journal entry and appends to `followups[]` (deduped by text).
- `learning-status` shows an "Open followups" section per course; `onboarding` Returning User can surface one if any exist.
- A small action verb in conversation closes them: "done with the sharding followup" → mark resolved (or remove).

**Why P1.** Same as retention — real user behavior, data already being written, change is contained. Pair-ships naturally with retention prompts since both surface in `learning-status` / `onboarding`.

---

## chapter-check session-level review

**Priority.** P2.

**Problem.** `chapter-check` has three modes: current session (no args), review chapter (chapter ID), focus topic (chapter + topic). There's no clean way to say *"review me on session 2 of design-a-key-value-store"* — it'd fall through to chapter-wide review.

**Proposed direction.** Add a session-aware pattern to Step 1 of `chapter-check/SKILL.md`:
- "review session N of [chapter]" → if the chapter is currently in `.learning-progress.in_progress`, load only that session's `topics` (from `in_progress.sessions[]`) and quiz on them.
- For completed chapters, this is a gap: `in_progress` is cleared on completion. If the use case becomes real, archive the final session list into the `completed` entry (today it's a flat list of chapter IDs; would become a list of `{id, sessions: [...]}` objects).

**Why P2.** Cheap addition for the in-progress half (~5 lines in the skill). The completed-chapter gap needs a schema change and may never bite — defer it.

---

## Schema versioning for `.learning-progress`

**Priority.** P2.

**Problem.** The shape of `.learning-progress` has evolved twice in the last few sessions (added `in_progress`, then simplified its inner shape). Each time, hand-migration was needed across workspaces. There's no version field, so a skill running against an older workspace can't tell whether `in_progress.sessions[].completed_date` vs `completed` is in play. Today this is handled by "upgrade all workspaces in lockstep," which is brittle.

**Proposed direction.**
- Add a top-level `"schema_version": N` field. Bump on breaking shape changes.
- `learn` / `save-progress` / `learning-status` read the version; if it's older than the engine expects, run a small in-skill migration (or print a one-line "run `learning-os migrate-progress`" hint).
- Optional CLI: `learning-os migrate-progress` reads the file, detects the shape, rewrites in the latest format with a `.bak`.

**Why P2.** Preventive maintenance. Pays off the next time we evolve the shape — which we will. Without it, every shape change needs the manual ritual we just did three times.

---

## Cross-workspace aggregator

**Priority.** P2.

**Problem.** The user runs multiple workspaces (currently three: `hands-on-books`, `hands-on`, `hands-on-infra`) plus the engine repo. There's no unified view — "how am I doing across everything?" requires cd-ing into each workspace and running `learning-status` separately.

**Proposed direction.**
- New CLI: `learning-os summary <path>...` (or with `--workspaces-from ~/.learning-os/workspaces.txt`).
- For each path, read `.learning-progress` and emit a compact roll-up: total chapters complete, in-progress chapter (if any), last activity date, days-since.
- Bonus: detect stale workspaces (no activity in N days) — useful with retention prompts.
- Could also surface from an Agent Skill running in any workspace, but the CLI is the simpler implementation.

**Why P2.** Useful when the number of workspaces grows; with three, it's manageable manually. The hard part is convention — where does the list of workspaces live? `~/.learning-os/workspaces.txt`? CLI args? Pick something simple.

---

## Persisted quiz history

**Priority.** P2.

**Problem.** `chapter-check` review mode references "original quiz score (if any)" by parsing free text from journal entries. The actual questions, the user's answers, and per-question correctness are not stored — only a final score like `(quiz: 7/7)` makes it into notes. That means historical review can compare scores but not answers. The user has explicitly noted "revisit X in 1-2 weeks for retrieval practice" — they'd benefit from "you got Q4 wrong last time; let's try again."

**Proposed direction.**
- Add `courses/[course-id]/quizzes/[chapter-id]/[YYYY-MM-DD].json` — `{questions: [{prompt, correct_answer, user_answer, correct: bool}], score: "7/7"}`.
- `chapter-check` writes the file at the end of every quiz (current and review modes).
- `chapter-check` review mode reads prior files for the chapter, surfaces "questions you got wrong before" as priority candidates, shows "last time you said X; correct is Y" feedback.

**Why P2.** Powerful when paired with retention prompts (the "review due" item). On its own, valuable but not urgent. The cost is real — a new directory of structured data per chapter — so do it once retention is shipping.

---

## Stale hook tests cleanup

**Priority.** P3.

**Problem.** `tests/test_scaffold.py::test_session_end_hook_uses_sys_executable` and `test_claude_settings_hook_uses_sys_executable` have been failing since the disable commit (`aefece5`). They expect a `sessionEnd` / `SessionEnd` key in the hooks config that the scaffold no longer writes (the hook is currently disabled). Every test run requires `--deselect` to stay green.

**Proposed direction.** Either delete both tests (the disabled-hook state is captured implicitly by the scaffold writing `{"hooks": {}}`) or rewrite them as positive assertions that the hooks dict is empty. Five-minute change.

**Why P3.** Pure debt; no behavior impact. Worth picking up alongside any other test-suite change.

---

## Code artifact index per course

**Priority.** P3.

**Problem.** `PEDAGOGY.md` and `COURSE_SCHEMA.md` document a code-artifact convention: code-heavy topics get a runnable file saved to `courses/<id>/resources/<chapter-id>/`. The System Design course has these already (e.g. consistent-hashing Java + Python). There's no index — to find them later, you grep the filesystem or remember.

**Proposed direction.**
- Auto-maintain `courses/[course-id]/resources/INDEX.md` from `learn` whenever it saves a code artifact. Each row: chapter → file path → one-line description.
- `chapter-check` review mode could surface "we wrote [file] for this — want to re-run?"

**Why P3.** Small, mostly automation. Real but modest convenience win. Skip until artifact volume makes the gap obvious.

---

## Course operations: rename / merge / split

**Priority.** P3.

**Problem.** Courses evolve. The user has already done this manually once (splitting "Streams Deep Dive" out of `java-evolution` into its own chapter, per Feb 2026 notes). Doing it well requires editing `COURSE.yaml`, updating `REGISTRY.md`, renaming the course directory, fixing chapter-id references in `.learning-progress.completed`, and possibly moving section-mapping entries. All manual today.

**Proposed direction.**
- `learning-os course rename <old-id> <new-id>` — atomically move the directory, fix REGISTRY.md, rewrite chapter-id references in `.learning-progress`.
- `learning-os course split <id>` — interactive; pick chapters to extract into a new course; preserve completion history.
- `learning-os course merge <id1> <id2>` — same energy in reverse.

**Why P3.** Happens rarely; manual is workable; the operations are easy to get wrong (`.learning-progress` corruption). Build only if course-shaping becomes frequent.

---

## Re-evaluate session-end auto-capture hook

**Priority.** P3.

**Status.** Disabled 2026-05-16 (in `scaffold.py`). Script preserved at `templates/hooks/session_end.py` and updated to write per-course paths if re-enabled.

**Original purpose.** Write a breadcrumb to the active course's `courses/<course-id>/session-notes.md` if the user closes their AI tool without running `save my progress`, so no session is invisible in the journal.

**Why disabled.** Both Claude Code and Cursor retain session context across reopens. The breadcrumb fires on every `SessionEnd` regardless of whether the user actually lost context — producing noise that has to be cleaned up by hand. In practice the user (and the agent) can reconstruct session intent from the live conversation when reopening.

**Possible revisits.**
- If multi-day breaks become common and the live conversation is genuinely gone, a breadcrumb has value. Consider re-enabling with a smarter trigger (only fire if no `save-progress` happened in the last 24h).
- Or: replace the hook with an in-skill nudge — when `learn` is invoked and the user hasn't saved in N days, prompt "want me to save the previous session first?"

**Why P3.** User disabled it deliberately; no evidence the gap matters. The in-skill nudge is the cleaner replacement if it ever does — the hook itself probably never comes back.

---

## learning-status CLI command parity

**Priority.** P3.

**Problem.** The `learning-status` skill displays in-progress chapters by reading `.learning-progress.tracks.[track].in_progress`. The CLI command `learning-os list` still shows only `completed` and won't reflect partial-chapter state.

**Proposed direction.** Bring the CLI to parity — read `.learning-progress.in_progress` for each track, surface in-progress chapters in the listing output. Same logic as the skill, implemented in `scaffold.py` / `cli.py`.

**Why P3.** The skill covers the interactive case (where the user actually is when they ask). The CLI is for occasional external inspection. Re-implementing display logic in two places is busywork unless someone genuinely scripts against `learning-os list`.
