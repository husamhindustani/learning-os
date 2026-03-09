---
name: create-course
description: >-
  Create a new learning course in the workspace. Use when the user says
  'create a course', 'add a new course', 'I want to learn [topic]' (when
  no course exists for it), 'set up a course on [topic]', or 'new course'.
---

# Create Course

Scaffold a new course following the Learning OS standard structure.

See [assets/COURSE_TEMPLATE.yaml](assets/COURSE_TEMPLATE.yaml) for the canonical COURSE.yaml template.

## Step 1: Gather course information

Ask conversationally — don't present a form. You need:

**Required:**
- **Topic / name** (e.g., "Python Basics", "System Design", "React Hooks")
- **Course ID** — suggest kebab-case: "python-basics", "system-design", "react-hooks"
- **Type:** programming | conceptual | mixed
- **Track name** — suggest based on ID (e.g., "python", "system-design", "react")

**Optional:**
- Description (generate a good one if not provided)
- Programming language (if programming course)
- Prerequisites

Example conversation:
> "What would you like to learn? I'll set up a course for it."
> User: "I want to learn Docker"
> "Great — I'll create a 'docker-basics' course. Is this a programming course (hands-on with commands/code) or more conceptual (theory and architecture)?"

## Step 2: Ask about chapters

> "How many chapters will this course have? You can always add more later."

If they give a number, ask for each chapter:
- Chapter ID (kebab-case)
- Chapter title
- Main topics (keywords are fine: "images, containers, volumes")

If they say "I'll add them later" — create a COURSE.yaml with 2 placeholder chapters.

## Step 3: Create course structure

Create these files:

```
courses/[course-id]/
├── COURSE.yaml           ← from assets/COURSE_TEMPLATE.yaml, filled in
├── LEARNING_PLAN.md      ← template with sections per chapter
├── EXERCISES.md          ← if programming or mixed (template)
└── chapters/             ← optional, for conceptual courses with dedicated files
    └── .gitkeep
```

For programming courses, also create:
- `src/` or `examples/` directory (with `.gitkeep`)

For conceptual courses, also create:
- `resources/` directory (with `.gitkeep`)

## Step 4: Fill in COURSE.yaml

Use the template from [assets/COURSE_TEMPLATE.yaml](assets/COURSE_TEMPLATE.yaml) and fill in:
- All required fields with the information gathered
- `chapters` array with the defined chapters
- `progress.section_mapping` for each chapter

## Step 5: Create LEARNING_PLAN.md

```markdown
# [Course Title]

[Description]

---

## How to use this course

- Each section has explanations and examples
- [If programming:] `EXERCISES.md` has hands-on tasks for each chapter
- Say "save my progress" when you complete a chapter
- Ask questions freely — tangents are encouraged

---

## Progress checklist

- [ ] [Chapter 1 title]
- [ ] [Chapter 2 title]

---

## [Chapter 1 Title]

**Focus:** [What this chapter covers and why it matters]

### Topics
- [Topic 1] — [One line description]
- [Topic 2] — [One line description]

---

## [Chapter 2 Title]

[Repeat structure]

---

## After this course

[What to do next, related courses, where to apply the knowledge]
```

## Step 6: Create EXERCISES.md (programming/mixed courses)

```markdown
# [Course Title] — Exercises

---

## [Chapter 1 Title]

### Exercise 1: [Name]

**Task:** [Description]

**Steps:**
1. [Step 1]
2. [Step 2]

**Expected output:**
[example]

---

## [Chapter 2 Title]

[Repeat structure]
```

## Step 7: Update courses/REGISTRY.md

Add to the "Active Courses" section:

```markdown
### [Course Title]
- **ID:** `[course-id]`
- **Path:** `courses/[course-id]/`
- **Track:** `[track-name]`
- **Type:** [Type]
- **Status:** Not started
- **Description:** [Description]

**Chapters:**
1. [Chapter 1 title]
2. [Chapter 2 title]
```

Update the statistics section if present.

## Step 8: Confirm

```
Course created: [Course Title]

  courses/[course-id]/
  ├── COURSE.yaml
  ├── LEARNING_PLAN.md
  [other files listed]

Next: Say "teach me [first-chapter-id]" to begin learning!
```

## Notes

- Use the canonical COURSE.yaml schema from assets/COURSE_TEMPLATE.yaml
- Always use `chapters` (never `modules`) per the Learning OS schema
- The `track` and `section_mapping` fields must be consistent — the `save-progress` skill reads them to write `.learning-progress`
- Keep LEARNING_PLAN.md sections focused; detailed content can be added as you learn
