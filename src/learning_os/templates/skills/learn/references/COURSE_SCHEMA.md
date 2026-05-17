# COURSE.yaml Schema Reference

Every course in a Learning OS workspace is defined by a `COURSE.yaml` file. This document describes every field.

## Location

```
courses/
└── [course-id]/
    ├── COURSE.yaml       ← described here
    ├── LEARNING_PLAN.md
    ├── EXERCISES.md
    ├── resources/        ← conventional home for chapter code samples
    │   └── [chapter-id]/ │   created by the `learn` skill when teaching
    │       └── ...       │   code-heavy topics (see PEDAGOGY.md)
    └── ...
```

### `resources/` directory convention

When the `learn` skill teaches a code-heavy topic, it saves runnable code samples under `courses/<course-id>/resources/<chapter-id>/` so the user has a persistent reference for revision. This is a convention, not a schema field — no entry in COURSE.yaml is required. See `learn` skill's `references/PEDAGOGY.md` → "Show, don't hand-wave."

## Full Schema

```yaml
# Required fields
id: course-id             # kebab-case, unique across workspace, matches directory name
title: "Course Title"
description: "1-2 sentence description of what this course covers."
track: track-name         # short alphanumeric identifier, used as the key in .learning-progress
type: programming         # programming | conceptual | mixed

# Content files
learning_plan: LEARNING_PLAN.md   # relative to course directory
exercises: EXERCISES.md           # optional; relative to course directory

# Chapters (always 'chapters', never 'modules')
chapters:
  - id: chapter-id               # kebab-case
    title: "Chapter Title"
    topics:                      # list of topic strings
      - "Topic 1"
      - "Topic 2"
    exercises_section: "section-name"  # section heading in EXERCISES.md
    large_chapter: false               # optional; true triggers split offer (6+ topics)
    content_file: "SPECIAL.md"         # optional; dedicated content file for this chapter
    demos:                             # optional; paths to runnable demo files
      - src/main/java/com/example/Demo.java
    source:                            # optional; book source for this chapter
      book_chapters: ["ch-1", "ch-2"]  # IDs from book-outline.yaml
      content_files:                   # extracted markdown the learn skill reads
        - books/<slug>/book-content/ch-01-xxx.md
      supplementary_notes: "What to add beyond the book"  # optional

# Progress tracking
progress:
  track_name: track-name        # same as 'track' above
  section_mapping:              # maps chapter id → display name stored in .learning-progress
    chapter-id: "display-name"
    another-chapter: "another-name"

# Build configuration (optional, for programming courses)
build:
  tool: maven                  # maven | npm | cargo | python | etc.
  compile: "mvn clean compile"
  run_demo: "mvn exec:java -q -Dexec.mainClass=\"{class}\""

# Book source (optional — for courses created from a book)
source:
  type: book
  title: "Book Title"
  authors:
    - "Author Name"
  file: books/<slug>/<original-filename>.pdf
  outline: books/<slug>/book-outline.yaml

# Prerequisites (optional)
prerequisites:
  - "Basic knowledge of X"
  - "Y installed"

# What to do after completing this course (optional)
next_course: other-course-id
```

## Field Details

### `id`
- Must match the directory name exactly
- kebab-case: lowercase letters, numbers, hyphens
- Example: `java-evolution`, `react-advanced`, `system-design`

### `track`
- Used by the `save-progress` skill as the key in `.learning-progress` (`TRACK_[track-name]=...`)
- Should be short and unique: `java`, `react`, `system-design`
- The skill reads this from COURSE.yaml — no hardcoding needed

### `chapters[].exercises_section`
- The section heading (case-insensitive) to find in EXERCISES.md
- Example: `"java8"` matches `## Java 8` or `## java8` in the file
- The `learn` skill uses this to display exercises after teaching

### `chapters[].large_chapter`
- Set to `true` when a chapter has 6+ topics
- Triggers the "break into smaller sessions?" offer in the `learn` skill
- Also triggered automatically if the topics list has 6+ items (even without this flag)

### `source` (course-level)
- Present only for courses created from a book via `create-course-from-book`
- `source.type` — always `"book"` for now
- `source.title` — the book's title
- `source.authors` — list of author names
- `source.file` — path to the original PDF/EPUB (relative to workspace root)
- `source.outline` — path to the parsed `book-outline.yaml`

### `chapters[].source` (chapter-level)
- Maps this course chapter to sections of the source book
- `book_chapters` — list of chapter IDs from `book-outline.yaml` that this course chapter covers
- `content_files` — list of extracted markdown files the `learn` skill reads when teaching this chapter
- `supplementary_notes` — optional note about what the AI should teach beyond the book's content (outdated material, missing topics, etc.)

### `progress.section_mapping`
- Maps each chapter `id` to a display name stored in `.learning-progress` by the `save-progress` skill
- The stored name also appears in session notes
- Example: `streams-deep-dive: "Streams Deep Dive"`

## Minimal Example (conceptual course)

```yaml
id: system-design
title: "System Design Fundamentals"
description: "Core concepts for designing scalable distributed systems."
track: system-design
type: conceptual

learning_plan: LEARNING_PLAN.md

chapters:
  - id: scalability
    title: "Scalability Basics"
    topics:
      - "Horizontal vs vertical scaling"
      - "Load balancing"
      - "Stateless services"

  - id: caching
    title: "Caching Strategies"
    topics:
      - "Cache-aside"
      - "Write-through"
      - "Eviction policies"

progress:
  track_name: system-design
  section_mapping:
    scalability: "Scalability Basics"
    caching: "Caching Strategies"
```

## Minimal Example (programming course)

```yaml
id: python-basics
title: "Python Basics"
description: "Hands-on introduction to Python for beginners."
track: python
type: programming
language: python

learning_plan: LEARNING_PLAN.md
exercises: EXERCISES.md

chapters:
  - id: data-types
    title: "Data Types & Variables"
    topics:
      - "int, float, str, bool"
      - "Variables and assignment"
      - "Type conversion"
    exercises_section: "data-types"

progress:
  track_name: python
  section_mapping:
    data-types: "Data Types"

build:
  tool: python
  run_demo: "python {file}"
```

## Minimal Example (book-based course)

```yaml
id: clean-code
title: "Clean Code Essentials"
description: "Key principles from Clean Code, restructured for efficient learning."
track: clean-code
type: conceptual

learning_plan: LEARNING_PLAN.md

source:
  type: book
  title: "Clean Code"
  authors:
    - "Robert C. Martin"
  file: books/clean-code/clean-code.pdf
  outline: books/clean-code/book-outline.yaml

chapters:
  - id: naming-and-functions
    title: "Naming and Functions"
    topics:
      - "Meaningful names"
      - "Small functions"
      - "Function arguments"
    source:
      book_chapters: ["meaningful-names", "functions"]
      content_files:
        - books/clean-code/book-content/ch-01-meaningful-names.md
        - books/clean-code/book-content/ch-02-functions.md

  - id: comments-and-formatting
    title: "Comments and Formatting"
    topics:
      - "Good vs bad comments"
      - "Vertical and horizontal formatting"
    source:
      book_chapters: ["comments", "formatting"]
      content_files:
        - books/clean-code/book-content/ch-03-comments.md
        - books/clean-code/book-content/ch-04-formatting.md
      supplementary_notes: "Book examples are Java-centric — supplement with Python/JS examples"

progress:
  track_name: clean-code
  section_mapping:
    naming-and-functions: "Naming and Functions"
    comments-and-formatting: "Comments and Formatting"
```
