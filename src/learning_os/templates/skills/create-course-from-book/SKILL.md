---
name: create-course-from-book
description: >-
  Create a learning course from a book (PDF or EPUB). Use when the user says
  'create a course from this book', 'create a course from <book-slug>',
  'I have a book I want to study', 'teach me from this PDF', 'make a course
  from <filename>', or references a book in the books/ directory.
---

# Create Course from Book

Build a structured learning course around a book that has been imported with `learning-os add-book`. The book's extracted outline and chapter content are used to design a teaching plan — the AI is not just transcribing the book, it's building a better learning experience around it.

**Rule: do not create any files until the user has approved the proposed outline in Step 4.**

See [../create-course/assets/COURSE_TEMPLATE.yaml](../create-course/assets/COURSE_TEMPLATE.yaml) for the canonical COURSE.yaml template.

---

## Step 1: Locate the book

Find the book the user is referring to:

1. If the user gave a slug (e.g. "create a course from clean-code"), look for `books/clean-code/book-outline.yaml`
2. If the user gave a file path, check if a matching slug exists under `books/`
3. If unclear, list available books: `ls books/*/book-outline.yaml`

**If the book hasn't been imported yet:**
> "I don't see that book imported yet. Run this first:
>
> ```
> learning-os add-book <path-to-your-file.pdf>
> ```
>
> Then come back and say 'create a course from `<slug>`'."

Once found, read `books/<slug>/book-outline.yaml` to get the book's structure.

---

## Step 2: Analyze the book structure

Read the book outline and **skim the first ~50 lines of each chapter content file** (in `books/<slug>/book-content/`) to understand:

- How the book is organized (sequential, modular, reference-style)
- Which chapters are substantial vs. short/introductory
- The overall scope and depth

Then ask the user **2–3 targeted questions** in one message:

- **Goal** — "Are you reading this to apply at work, for interviews, general understanding, or something else?"
- **Scope** — "The book has N chapters. Want to cover it all, or focus on specific parts?" (list chapter titles for reference)
- **Depth** — "Should I follow the book's structure closely, or reorganize into a more teachable sequence?"

Wait for answers before proceeding.

---

## Step 3: Propose a chapter mapping

This is the key creative step. Design course chapters by **mapping book chapters to course chapters**. The mapping is rarely 1:1 — a good course:

- **Groups** related book chapters into single course chapters (most books have 15-30 chapters; a course should have 5-10)
- **Reorders** when the book's sequence isn't the best learning order
- **Identifies gaps** — topics the book misses, handles poorly, or where content is outdated
- **Notes supplementation** — where you'll teach beyond the book's content

Present the proposal:

```
Here's what I'm proposing:

**[Course Title]**
ID: `[course-id]` · Type: [conceptual|mixed] · Track: `[track-name]`
Source: "[Book Title]" by [Authors]

[What this course covers and the learning outcome]

Chapters:
1. **[Course Chapter Title]** — [What it covers]
   📖 Book chapters: [list which book chapters map here]
   ➕ Supplementing: [anything you'll add beyond the book]

2. **[Course Chapter Title]** — [What it covers]
   📖 Book chapters: [list]
   ⚠️ Note: [Book's coverage of X is outdated — I'll supplement with current practices]

3. ...

Does this structure work? You can:
- Say **yes** to create the course
- Ask me to **add, remove, or reorder** chapters
- Ask to **split** a chapter that covers too much
- Ask to **skip** book chapters you're not interested in
```

Wait for approval.

---

## Step 4: Refine until approved

Handle adjustments the same way as `create-course`:

- "Skip chapters 8-10" → remove them, note adjusted mapping
- "Split chapter 3" → break into two with clearer boundaries
- "Add a chapter on testing" → add with note that it's supplementary (no book source)

Once approved:
```
Got it — creating the course now.
```

Proceed immediately.

---

## Step 5: Create course structure

```
courses/[course-id]/
├── COURSE.yaml           ← filled in with source references
├── LEARNING_PLAN.md      ← sections per chapter, with book references and gap notes
├── EXERCISES.md          ← if type is mixed (most book courses are)
└── chapters/
    └── .gitkeep
```

Also create `resources/` with `.gitkeep`.

---

## Step 6: Fill in COURSE.yaml

Use the template from [../create-course/assets/COURSE_TEMPLATE.yaml](../create-course/assets/COURSE_TEMPLATE.yaml) and add the `source` block:

```yaml
id: course-id
title: "Course Title"
description: "Description"
track: track-name
type: conceptual  # or mixed

learning_plan: LEARNING_PLAN.md

source:
  type: book
  title: "Book Title"
  authors:
    - "Author Name"
  file: books/<slug>/<original-filename>
  outline: books/<slug>/book-outline.yaml

chapters:
  - id: chapter-one
    title: "Chapter One Title"
    topics:
      - "Topic A"
      - "Topic B"
    source:
      book_chapters: ["intro", "ch-1", "ch-2"]
      content_files:
        - books/<slug>/book-content/ch-01-intro.md
        - books/<slug>/book-content/ch-02-basics.md
      supplementary_notes: "Book doesn't cover X — will teach from own knowledge"

  - id: chapter-two
    title: "Chapter Two Title"
    topics:
      - "Topic C"
    source:
      book_chapters: ["ch-3"]
      content_files:
        - books/<slug>/book-content/ch-03-advanced.md

progress:
  track_name: track-name
  section_mapping:
    chapter-one: "Chapter One"
    chapter-two: "Chapter Two"
```

Key rules for the `source` block:
- `source.book_chapters` lists the IDs from `book-outline.yaml` that map to this course chapter
- `source.content_files` lists the extracted markdown files the `learn` skill should read when teaching
- `source.supplementary_notes` (optional) tells the `learn` skill what to add beyond the book

---

## Step 7: Create LEARNING_PLAN.md

```markdown
# [Course Title]

Based on "[Book Title]" by [Authors].

[Description — what this course covers and the learning outcome]

---

## How to use this course

- Each chapter is built around sections of the book, supplemented with additional context
- The AI teaches from the book's content in its own words, adding examples and clarification
- Say "save my progress" when you complete a chapter
- Ask questions freely — tangents are encouraged

---

## Progress checklist

- [ ] [Chapter 1 title]
- [ ] [Chapter 2 title]
- ...

---

## [Chapter 1 Title]

**Focus:** [What this chapter covers]

**Book source:** [Book chapter titles/numbers that map here]

### Topics
- [Topic 1] — [One line description]
- [Topic 2] — [One line description]

### Beyond the book
[If applicable: what the AI will supplement — outdated content, missing exercises, related modern practices. If the book covers this well, omit this section.]

---

## [Chapter 2 Title]

[Repeat structure]

---

## After this course

[What to do next — deeper reading, related courses, practice projects]
```

---

## Step 8: Create EXERCISES.md (if type is mixed)

Follow the same format as `create-course` Step 7. Design exercises that:
- Test understanding of the book's content
- Go beyond the book where possible (apply concepts to real scenarios)
- Reference the book when useful: "Using the pattern from Chapter 3..."

---

## Step 9: Update courses/REGISTRY.md

Add to the "Active Courses" section:

```markdown
### [Course Title]
- **ID:** `[course-id]`
- **Path:** `courses/[course-id]/`
- **Track:** `[track-name]`
- **Type:** [Type]
- **Source:** "[Book Title]" by [Authors]
- **Status:** Not started
- **Description:** [Description]

**Chapters:**
1. [Chapter 1 title] — 📖 [book chapters]
2. [Chapter 2 title] — 📖 [book chapters]
```

---

## Step 10: Confirm

```
Course created: [Course Title]
Source: "[Book Title]" by [Authors]

  courses/[course-id]/
  ├── COURSE.yaml
  ├── LEARNING_PLAN.md
  [other files]

  Book content: books/<slug>/book-content/ ([N] chapter files)

Next: Say "teach me [course-id]" to start learning!
```

---

## Notes

- Course chapters should be 5–10 even if the book has 20+. Group aggressively.
- The `learn` skill will read `source.content_files` to teach from actual book content — don't copy text into LEARNING_PLAN.md
- For supplementary chapters (no book source), omit the `source` block — the AI teaches from its own knowledge, same as a regular course
- Always use `chapters` (never `modules`) per the Learning OS schema
- `track` and `section_mapping` must be consistent — the `save-progress` skill reads them
