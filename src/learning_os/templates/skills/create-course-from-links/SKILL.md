---
name: create-course-from-links
description: >-
  Create a learning course from one or more web articles or a collection hub
  page. Use when the user says 'create a course from <url>', 'create a course
  from these links', 'teach me from this article collection', 'I want to learn
  from <hub-url>', or pastes a list of URLs and asks for a course. For a single
  one-off article, prefer the learn-from-link skill instead.
---

# Create Course from Links

Build a structured learning course around one or more web articles. The agent fetches each article, snapshots its content to disk inside the course, and designs a teaching plan — same downstream experience as a book-sourced course.

**Rule: do not create any files until the user has approved the proposed outline in Step 4.**

See [../create-course/assets/COURSE_TEMPLATE.yaml](../create-course/assets/COURSE_TEMPLATE.yaml) for the canonical COURSE.yaml template.

---

## Step 0: Decide course vs. one-off

If the user provided **a single URL** and didn't explicitly ask for a course:

> "This looks like a single article. I can either:
> 1. Just teach it to you in this session (no course scaffold) — use the `learn-from-link` skill
> 2. Build a one-chapter course around it (tracked progress, persistent notes)
>
> Which do you prefer?"

If they pick (1), hand off to `learn-from-link`. If (2), continue here. If they provided **multiple URLs** or a **hub URL**, proceed without asking.

---

## Step 1: Collect the URLs

Three input modes — figure out which one the user is using:

1. **Single URL** — proceed only if Step 0 confirmed they want a course.
2. **List of URLs** — pasted inline, or a path to a `.txt`/`.md` file with one URL per line.
3. **Hub URL** — a page like `https://dora.dev/capabilities/` that links to sub-articles.

For **hub mode**:
- Fetch the hub URL using whatever web tool is available to you (e.g. WebFetch, browse, a network MCP).
- Extract every link that points to a likely sub-article (same domain, distinct paths, skip nav/footer/social).
- Present the discovered list to the user:
  > "I found N candidate articles under this hub. Want to include all, or should I prune some? Here they are: [numbered list of title + URL]"
- Wait for confirmation/pruning before continuing.

**If you have no web-fetch tool available**, fall back to paste-mode:
> "I don't have a web tool in this environment. Please paste the article content directly — one block per article, separated by `---`, with the source URL on the first line of each block."

---

## Step 2: Build a lightweight outline

For each confirmed URL, fetch **just enough** to capture:
- `title` — page title or first H1
- `summary` — one to two sentences extracted from the article's intro/meta-description
- `est_reading_minutes` — rough estimate based on word count (200 wpm)

Do **not** fetch full bodies yet — that happens after the outline is approved. This keeps token cost low if the user wants to reshape the plan.

Ask the user **2–3 targeted questions** in one message:

- **Goal** — "Are you reading these to apply at work, for general understanding, for interviews, or something else?"
- **Depth** — "Should I teach each article in full depth, or focus on key takeaways?"
- **Scope** — only ask if there are 10+ articles: "Want to cover all N, or focus on a subset?"

Wait for answers before proceeding.

---

## Step 3: Propose a chapter mapping

Design course chapters by mapping articles to chapters. Heuristics:

- **Curated collection** (DORA capabilities, a reading list, a doc site) → often 1 article = 1 chapter. Acceptable to have 15–25 chapters when the source itself is structured that way.
- **Mixed bag of related articles** → group 2–4 short related articles into one chapter.
- **Long-form tutorial split across pages** → group the whole series into 3–5 chapters by theme.

Present the proposal:

```
Here's what I'm proposing:

**[Course Title]**
ID: `[course-id]` · Type: conceptual · Track: `[track-name]`
Source: [N] articles from [domain or "various sources"]

[What this course covers and the learning outcome]

Chapters:
1. **[Chapter Title]** — [what it covers]
   🔗 Articles:
     - [Article 1 title] (~M min)
     - [Article 2 title] (~M min)
   ➕ Supplementing: [anything to add beyond the articles, if relevant]

2. **[Chapter Title]** — [what it covers]
   🔗 Articles:
     - [Article 3 title] (~M min)

3. ...

Does this structure work? You can:
- Say **yes** to create the course
- Ask me to **add, remove, or reorder** chapters
- Ask to **split** a chapter that groups too many articles
- Ask to **drop** articles you're not interested in
```

Wait for approval.

---

## Step 4: Refine until approved

Handle adjustments the same way as `create-course`:

- "Drop articles 5–7" → remove them, note adjusted mapping
- "Split chapter 2" → break into two with clearer boundaries
- "Add a chapter on X" → add as supplementary (no article source)

Once approved:
```
Got it — fetching full content and creating the course now.
```

Proceed immediately.

---

## Step 5: Snapshot article content to disk

For **each** article in the approved plan, fetch the full page and extract main content as markdown (drop nav, ads, footers, comments). Write each to:

```
courses/[course-id]/sources/NN-<article-slug>.md
```

Where:
- `NN` is a two-digit index matching teaching order (01, 02, ...)
- `<article-slug>` is a kebab-case slug from the article title

The file should start with frontmatter:

```markdown
---
url: https://example.com/article
title: "Article Title"
fetched_at: 2026-05-19
author: "Author Name (if available)"
---

# Article Title

[main content as markdown]
```

If a fetch fails (paywall, JS-only page, 404), don't silently skip — tell the user and offer:
1. Skip this article and continue
2. Ask them to paste the content manually
3. Abort

---

## Step 6: Create course structure

```
courses/[course-id]/
├── COURSE.yaml          ← filled in with article source references
├── LEARNING_PLAN.md     ← sections per chapter, with article references
├── sources/             ← snapshotted article markdown (Step 5)
│   ├── 01-<slug>.md
│   └── 02-<slug>.md
└── chapters/
    └── .gitkeep
```

Also create `resources/` with `.gitkeep` (used by `learn` for runnable code).

If the user wants exercises (rare for article-based courses, but ask), set `type: mixed` and create `EXERCISES.md`. Default to `type: conceptual` otherwise.

---

## Step 7: Fill in COURSE.yaml

Use the template from [../create-course/assets/COURSE_TEMPLATE.yaml](../create-course/assets/COURSE_TEMPLATE.yaml) and add the `source` block:

```yaml
id: course-id
title: "Course Title"
description: "Description"
track: track-name
type: conceptual

learning_plan: LEARNING_PLAN.md

source:
  type: articles
  hub_url: https://example.com/topic/        # optional; only for hub mode
  article_count: 8

chapters:
  - id: chapter-one
    title: "Chapter One Title"
    topics:
      - "Topic A"
      - "Topic B"
    source:
      articles:
        - url: https://example.com/article-1
          title: "Article 1 Title"
          content_file: courses/course-id/sources/01-article-1.md
        - url: https://example.com/article-2
          title: "Article 2 Title"
          content_file: courses/course-id/sources/02-article-2.md
      supplementary_notes: "Articles don't cover X — will teach from own knowledge"

  - id: chapter-two
    title: "Chapter Two Title"
    topics:
      - "Topic C"
    source:
      articles:
        - url: https://example.com/article-3
          title: "Article 3 Title"
          content_file: courses/course-id/sources/03-article-3.md

progress:
  track_name: track-name
  section_mapping:
    chapter-one: "Chapter One"
    chapter-two: "Chapter Two"
```

Key rules for the `source` block:
- Course-level `source.type` is `articles` (vs `book` for book-sourced courses)
- Each chapter's `source.articles[]` lists URL + title + local snapshot path
- The `learn` skill reads `content_file` paths to teach — exact same machinery as book courses
- `supplementary_notes` (optional) tells the `learn` skill what to add beyond the articles

---

## Step 8: Create LEARNING_PLAN.md

```markdown
# [Course Title]

A course built from N curated articles[, sourced from [domain]].

[Description — what this course covers and the learning outcome]

---

## How to use this course

- Each chapter is built around one or more articles, snapshotted locally under `sources/`
- The AI teaches in its own words using the snapshotted content, adding examples and context
- Say "save my progress" when you complete a chapter
- Ask questions freely — tangents are encouraged
- Original URLs are recorded in COURSE.yaml for reference

---

## Progress checklist

- [ ] [Chapter 1 title]
- [ ] [Chapter 2 title]
- ...

---

## [Chapter 1 Title]

**Focus:** [What this chapter covers]

**Articles:**
- [Article 1 title] — [URL]
- [Article 2 title] — [URL]

### Topics
- [Topic 1] — [One line description]
- [Topic 2] — [One line description]

### Beyond the articles
[If applicable: what the AI will supplement. Omit if articles cover the topic well.]

---

## [Chapter 2 Title]

[Repeat structure]

---

## After this course

[What to do next — deeper reading, related courses, practice]
```

---

## Step 9: Update courses/REGISTRY.md

Add to the "Active Courses" section:

```markdown
### [Course Title]
- **ID:** `[course-id]`
- **Path:** `courses/[course-id]/`
- **Track:** `[track-name]`
- **Type:** Conceptual
- **Source:** [N] articles[ from [domain]]
- **Status:** Not started
- **Description:** [Description]

**Chapters:**
1. [Chapter 1 title] — 🔗 [N articles]
2. [Chapter 2 title] — 🔗 [N articles]
```

---

## Step 10: Confirm

```
Course created: [Course Title]
Source: [N] articles snapshotted to courses/[course-id]/sources/

  courses/[course-id]/
  ├── COURSE.yaml
  ├── LEARNING_PLAN.md
  ├── sources/   ([N] article files)
  └── ...

Next: Say "teach me [course-id]" to start learning!
```

---

## Notes

- For curated structured collections (e.g. DORA capabilities, a doc site index), 1:1 article→chapter is fine even at 20+ chapters. For loose reading lists, group aggressively.
- The `learn` skill reads `source.articles[].content_file` to teach from snapshotted content — same code path as book content_files.
- Snapshotting (not live re-fetch) protects against link rot, paywalls activating later, and offline sessions. Original `url` is preserved for citation.
- For supplementary chapters with no article source, omit the `source` block — the AI teaches from its own knowledge, same as a regular course.
- Always use `chapters` (never `modules`) per the Learning OS schema.
- `track` and `section_mapping` must be consistent — the `save-progress` skill reads them.
