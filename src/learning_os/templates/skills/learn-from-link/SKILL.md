---
name: learn-from-link
description: >-
  Teach a single web article interactively, no course scaffold. Use when the
  user says 'teach me from <url>', 'explain this article: <url>', 'help me
  understand <url>', or shares a single link and asks for help reading it. For
  multiple articles or a hub page (collection), use create-course-from-links
  instead.
---

# Learn from Link

Lightweight, one-off teaching for a single article. No course files, no
REGISTRY entry, no `.learning-progress` tracking — just fetch, teach, and
optionally save notes.

This skill applies the same pedagogy as the `learn` skill (see
[../learn/references/PEDAGOGY.md](../learn/references/PEDAGOGY.md)), scaled
down to a single article session.

---

## When to use this skill vs. create-course-from-links

| Situation | Use |
|---|---|
| Single article, casual read | **learn-from-link** (this skill) |
| Single article, want tracked progress + persistent notes | `create-course-from-links` (1-chapter course) |
| Multiple URLs / hub page (e.g. dora.dev/capabilities) | `create-course-from-links` |

If the user provides multiple URLs or a hub page, hand off to `create-course-from-links` instead.

---

## Step 1: Fetch the article

Use whatever web-fetch tool is available (WebFetch, browse, an MCP) to
retrieve the article. Extract the main content as markdown — drop nav, ads,
sidebars, comments.

**If you have no web-fetch tool:**

> "I don't have a web tool in this environment. Could you paste the article
> content? I'll teach from what you paste."

If the fetch fails (paywall, JS-only, 404):

> "I couldn't fetch that article ([reason]). You can either paste the
> content directly, or share an alternate URL."

---

## Step 2: Skim and plan

Before teaching, read the full article and identify:

- **3–5 core ideas** — what the article is fundamentally about
- **Structure** — does it build sequentially, or is it a collection of points?
- **Gaps** — anything the article skips, glosses over, or treats as
  prerequisite that the user may not know
- **Outdated bits** — anything you know is stale, superseded, or wrong
- **Code examples** — does the article use code? If so, in what language?

Briefly tell the user what you're about to do:

```
I've read the article. Here's the plan:

This is about [one-sentence framing]. I'll walk you through:
1. [Core idea 1]
2. [Core idea 2]
3. [Core idea 3]

[Optional: I noticed [gap/dated bit] — I'll supplement that with [what].]

Ready to start? You can interrupt anytime with questions.
```

Wait for the user to say go (or ask a question first).

---

## Step 3: Teach per PEDAGOGY.md

Apply [../learn/references/PEDAGOGY.md](../learn/references/PEDAGOGY.md) in full:

- **One concept at a time** — don't dump all ideas at once
- **Context before content** — why does this exist, what problem does it solve
- **Teach in your own words** — don't paraphrase the article line by line; use
  the article as your source material and re-explain
- **Examples** — use clear, practical examples; favour the user's familiar
  language for code
- **Check understanding** — pause after each core idea and ask a probing
  question or invite a question from the user
- **Encourage tangents** — if the user asks a "why" or "how" outside the
  article, follow it
- **Show, don't hand-wave** — if the article involves code/algorithms and a
  learner could plausibly walk away wondering "but how does that actually
  work in code?", produce a short runnable example

**Differences from the `learn` skill:**

- No `EXERCISES.md` to surface (no course)
- No `save-progress` handoff (no progress file)
- One session, not a chapter sequence

---

## Step 4: Optional end-of-session quiz

After teaching, offer:

> "Want me to quiz you on the key points to lock it in?"

If yes, ask 3–5 questions in the same style as the `chapter-check` skill:
mix recall, application, and "what would happen if…" questions. Give
feedback after each answer. Don't make it feel like an exam — it's a
self-check.

---

## Step 5: Optional save notes

After teaching (and after the optional quiz), offer:

> "Want me to save the key takeaways and your questions as notes for later?"

If yes, write to:

```
reading-notes/YYYY-MM-DD-<article-slug>.md
```

Create the `reading-notes/` directory if it doesn't exist (alongside
`courses/`, `books/` at workspace root).

File template:

```markdown
# [Article Title]

**Source:** [URL]
**Read on:** YYYY-MM-DD
**Author:** [if known]

---

## Key takeaways

- [Takeaway 1 — one or two sentences in your own words]
- [Takeaway 2]
- [Takeaway 3]

---

## Questions you asked

- **Q:** [User's question]
  **A:** [Short summary of the answer given]

---

## Beyond the article

[If applicable: notes the AI added that weren't in the article — supplementary
context, corrections, related ideas.]

---

## Open threads

[If applicable: questions left unanswered, things to follow up on]
```

If the user says no, that's fine — don't write anything. Just confirm and end.

---

## Notes

- **Do not create a course.** No `COURSE.yaml`, no REGISTRY edits, no
  `.learning-progress` entries. This skill is deliberately lightweight.
- **Do not snapshot the full article to disk by default.** The notes file
  (if saved) captures takeaways; if the user wants a full local archive,
  that's a `create-course-from-links` use case.
- If the user repeatedly invokes this skill for articles in the same topic
  area, suggest at the end: *"You've worked through a few articles on X —
  want me to turn these into a tracked course?"* Then hand off to
  `create-course-from-links`.
