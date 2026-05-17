---
name: learn
description: >-
  Start or continue a learning chapter for any course. Use when the user
  says 'teach me X', 'let's learn Y', 'start chapter Z', 'continue learning',
  'I want to study X', or 'begin [topic]'. Also activates when user specifies
  a course and chapter like 'learn java-evolution java9'.
---

# Learn

Start or continue a learning session for any course chapter.

## Instructions

See [references/COURSE_SCHEMA.md](references/COURSE_SCHEMA.md) for how to read COURSE.yaml files.
See [references/PEDAGOGY.md](references/PEDAGOGY.md) for the teaching approach to follow.

### 1. Determine course and chapter

**From explicit user input:**
- "teach me java-evolution java8" → course: java-evolution, chapter: java8
- "learn react-advanced hooks" → course: react-advanced, chapter: hooks
- "continue" or "continue learning" → read `.learning-progress` for last track

**From context:**
- Check current conversation for course/chapter mentions
- Look at recently referenced files (e.g., files in `courses/java-evolution/`)

**From `.learning-progress`:**
- **Identify the active track.** For bare "continue", pick the `tracks.[track-name]` with the most recent `last_date`. For explicit "continue [course]", look up that course's `progress.track_name` (or `track`) in `COURSE.yaml` and use it.
- **Check for an in-progress chapter** — if `tracks.[track-name].in_progress` exists, the user is mid-split:
  - Resume `in_progress.chapter_id`.
  - The next session is the first entry in `in_progress.sessions[]` with `completed: false`.
  - Use that session's `topics` list as the teaching agenda — do NOT re-teach sessions with `completed: true`.
  - Announce: "Resuming **[Chapter Title]** at **Session N — [session title]**. We'll cover: [topics]."
  - Resolve the course-id from `chapter_id` by scanning `courses/*/COURSE.yaml` for one that contains a matching chapter id; load that COURSE.yaml.
- **Otherwise**, pick the next chapter: `last_saved` is the last completed; suggest the next chapter not in `completed`.

**Collision check (explicit chapter request):**
If the user says "learn [course] [chapter-Y]" and `tracks.[track-name].in_progress` exists for a different `chapter_id`, do **not** silently switch. Prompt:

> You're mid-way through **[in_progress chapter title]** — [N of M] sessions complete. Resume that, or abandon and start [chapter-Y]?

If the user picks abandon, delete `in_progress` from `.learning-progress` before continuing. If resume, ignore the explicit request and go to the in-progress chapter.

**If still unclear:**
- Read `courses/REGISTRY.md` and list available courses
- Ask: "Which course would you like? Available: [list]"

**Error handling:**
- Course not found → "Course '[id]' not found. Available: [list from REGISTRY.md]"
- Chapter not found → "Chapter '[id]' not found in [course]. Chapters: [list from COURSE.yaml]"

### 2. Load course metadata

1. Read `courses/[course-id]/COURSE.yaml`
2. Find the chapter by `id` in the `chapters` array
3. Extract: `title`, `topics`, `demos`, `exercises_section`, `large_chapter`

### 3. Check chapter size

If chapter has `large_chapter: true` OR has 6+ topics:

> "This chapter covers [N] topics: [list]. That's a lot for one session. Would you like to:
>
> A) Cover all topics now
> B) Break it into 2-3 smaller sessions
> C) Focus on specific topics (you pick)
>
> What works best?"

Wait for choice before proceeding.

**If the user picks B (break into sessions):**

1. Propose a split (titles + topic-per-session assignment), confirm with the user.
2. Once confirmed, **write the split to `.learning-progress` immediately, before teaching Session 1.** Update `tracks.[track-name].in_progress`:

   ```json
   "in_progress": {
     "chapter_id": "[chapter-id]",
     "sessions": [
       {"title": "[Session title]", "topics": ["topic 1", "topic 2"], "completed": false},
       {"title": "[Session title]", "topics": ["topic 3", "topic 4"], "completed": false}
     ]
   }
   ```

   - Titles are plain strings (the same way you'd reference them in conversation). Identity is by exact title match. If the user doesn't title the sessions, fall back to `Session 1`, `Session 2`, etc. Titles must be unique within the array.
   - `topics` is the subset of the chapter's topics this session will cover.
   - All sessions start with `"completed": false`. `save-progress` flips them to `true` as each session finishes.

3. Teach Session 1's topics (the first session in the array). When that session is saved, `save-progress` will flip `completed` and the next "continue" will pick up Session 2.

**If the user picks A:** No `in_progress` block. Teach all topics, save normally as a full chapter.

**If the user picks C:** No `in_progress` block. Teach only the picked topics. This is a one-shot pass, not a multi-session split — if the user later wants the rest, they ask explicitly.

### 4. Load chapter content

**Priority order:**
1. If chapter has a `source` block with `content_files` → read each file listed (paths are relative to workspace root, e.g. `books/<slug>/book-content/ch-01-xxx.md`). These contain extracted book text — use it as your primary teaching material but **teach in your own words**, adding context and examples
2. If chapter has `content_file` field → read `courses/[course-id]/[content_file]`
3. Otherwise → read `courses/[course-id]/LEARNING_PLAN.md`, find the section for this chapter
4. If course has `chapters/` directory → look for `courses/[course-id]/chapters/[chapter-id].md`

**For book-based chapters** (those with `source.content_files`):
- Read the source content files to understand what the book says
- Check for `source.supplementary_notes` — these tell you what to add beyond the book
- Do NOT just repeat the book verbatim. Teach the concepts in your own words, reorganize for clarity, add examples the book doesn't have, and note when content is outdated
- If the chapter maps to multiple book chapters, synthesize them into a coherent flow rather than teaching them sequentially

### 5. Teach one topic at a time

Follow the pedagogical approach in [references/PEDAGOGY.md](references/PEDAGOGY.md).

For each topic:
1. **Context** — Why does this exist? What problem does it solve?
2. **What it is** — Clear definition with a simple example
3. **How it works** — Key mechanics, syntax, important details
4. **When to use** — Practical guidance
5. **Connection** — How it relates to previous/upcoming concepts
6. **Check** — "Does this make sense?" Wait for confirmation before moving on
7. **Code artifact (when applicable)** — for code-heavy topics, save a runnable example to `courses/<course-id>/resources/<chapter-id>/` and reference the file path in the response. See PEDAGOGY.md → "Show, don't hand-wave."

### 6. After teaching all topics — show exercises

1. Read the exercises file: `courses/[course-id]/EXERCISES.md` (from COURSE.yaml `exercises` field)
2. Find the section for this chapter (use `exercises_section` field)
3. **Check coverage:** Compare topics taught vs exercises available
4. **If important topics have no exercises:** Create new exercises on the spot, append them to the file
5. **Display exercises directly inline** — do not say "see file X", show the actual content

When creating new exercises:
- Match style and difficulty of existing exercises
- Focus on practical application
- Include expected output or behavior
- Mention: "I've added [N] new exercise(s) to cover [topics]"

### 7. Show demos (if any)

List demo files from COURSE.yaml `demos` field:
- Show file path
- Explain what it demonstrates
- Show run command from COURSE.yaml `build.run_demo` field

### 8. Next steps

Tell the user:

> **Now:** Run the demos, complete the exercises above, ask questions freely.
>
> **When done:** Say "quiz me" to test your understanding, or "save my progress" to record this session.
>
> [If partial chapter:] "When you're ready for [remaining topics], just say 'continue [course] [chapter]'."
