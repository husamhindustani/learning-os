# COURSE.yaml Schema Reference

Every course in a Learning OS workspace is defined by a `COURSE.yaml` file. This document describes every field.

## Location

```
courses/
└── [course-id]/
    ├── COURSE.yaml       ← described here
    ├── LEARNING_PLAN.md
    ├── EXERCISES.md
    └── ...
```

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
