---
name: create-course
description: >-
  Create a new learning course in the workspace. Use when the user says
  'create a course', 'add a new course', 'I want to learn [topic]' (when
  no course exists for it), 'set up a course on [topic]', or 'new course'.
---

# Create Course

Design a course collaboratively with the user, then scaffold it once they approve the structure.

**Rule: do not create any files until the user has approved the proposed outline in Step 3.**

See [assets/COURSE_TEMPLATE.yaml](assets/COURSE_TEMPLATE.yaml) for the canonical COURSE.yaml template.

---

## Step 1: Ask targeted clarifying questions

Based on the topic the user mentioned, identify 2–4 questions that will meaningfully shape the course structure. Do not ask generic questions — make them specific to the subject.

**What to probe for (pick the most relevant):**

- **Starting point** — what they already know, so you can skip or condense prerequisites
  - e.g. "Are you coming from Java 8/11, or more recently Java 17?"
  - e.g. "Are you new to containers, or familiar with the idea and want the hands-on side?"

- **Depth vs breadth** — overview to get productive, or thorough understanding
  - e.g. "Do you want a working-knowledge overview of each feature, or deep dives into the internals?"
  - e.g. "Should we cover edge cases and gotchas, or focus on the common patterns?"

- **Focus / scope** — which aspects matter most for their goal
  - e.g. "Language features only, or also new/updated APIs and tooling?"
  - e.g. "Theory and architecture, or hands-on implementation, or both?"

- **Goal** — what they'll do with this knowledge
  - e.g. "Is this for migrating an existing codebase, or greenfield work?"
  - e.g. "Preparing for interviews, working on a real project, or general curiosity?"

Ask all your questions in **one message** — not one at a time. Keep the tone conversational, not form-like.

Example for "I want to learn changes in Java 21":
> A few quick questions to shape this well:
>
> 1. Which Java version are you coming from — 8, 11, 17, or something else? (Helps me skip what you already know.)
> 2. Do you want to cover just the language and API changes, or also migration patterns and tooling updates?
> 3. Working-knowledge overview, or deep dives into each feature?

Wait for the user's answers before proceeding.

---

## Step 2: Propose a chapter outline

Using your knowledge of the topic and the user's answers, design a complete chapter structure. Do not ask the user to enumerate chapters — that's your job.

Show the proposal as a numbered list with a one-line description per chapter. Include a suggested course ID, type, and track name.

Format:
```
Here's what I'm proposing:

**[Course Title]**
ID: `[course-id]` · Type: [programming|conceptual|mixed] · Track: `[track-name]`

[Short description of what this course covers and the outcome]

Chapters:
1. **[Chapter Title]** — [One sentence: what it covers and why it's in this position]
2. **[Chapter Title]** — [One sentence]
3. **[Chapter Title]** — [One sentence]
...

Does this structure work? You can:
- Say **yes** (or "looks good") to create the course
- Ask me to **add, remove, or reorder** chapters
- Ask to **go deeper** on a chapter (I'll split it)
- Ask to **combine** chapters if the scope feels too narrow
```

**Guidelines for the outline:**
- Order chapters so each one builds on the previous
- For a "changes in X version" course: order by concept dependency, not by JEP/spec number
- Aim for 4–8 chapters — split anything with 6+ distinct topics into two chapters
- Name chapters by concept, not by spec reference (e.g. "Records and Sealed Classes" not "JEP 395/409")

Wait for the user's response before creating any files.

---

## Step 3: Refine until approved

If the user requests changes, update the proposal and show the revised outline. Repeat until they approve.

Common adjustments:
- "Add a chapter on X" → insert it in the right position and renumber
- "Combine chapters 2 and 3" → merge and write a new one-liner
- "Go deeper on virtual threads" → split into two chapters and explain the split
- "Skip the migration chapter" → remove it and note the change

Once the user approves, confirm what you're about to create:
```
Got it — creating the course now.
```

Then proceed immediately to Step 4 without further questions.

---

## Step 4: Create course structure

```
courses/[course-id]/
├── COURSE.yaml           ← from assets/COURSE_TEMPLATE.yaml, filled in
├── LEARNING_PLAN.md      ← sections per chapter
├── EXERCISES.md          ← if programming or mixed
└── chapters/             ← optional, for conceptual courses with dedicated files
    └── .gitkeep
```

For programming courses, also create:
- `src/` or `examples/` directory (with `.gitkeep`)

For conceptual courses, also create:
- `resources/` directory (with `.gitkeep`)

---

## Step 5: Fill in COURSE.yaml

Use the template from [assets/COURSE_TEMPLATE.yaml](assets/COURSE_TEMPLATE.yaml) and fill in:
- All required fields with the agreed structure
- `chapters` array with the approved chapters
- `progress.section_mapping` for each chapter

---

## Step 6: Create LEARNING_PLAN.md

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

---

## Step 7: Create EXERCISES.md (programming/mixed courses)

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

---

## Step 8: Update courses/REGISTRY.md

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

---

## Step 9: Confirm

```
Course created: [Course Title]

  courses/[course-id]/
  ├── COURSE.yaml
  ├── LEARNING_PLAN.md
  [other files listed]

Next: Say "teach me [course-id]" to start learning!
```

---

## Notes

- Use the canonical COURSE.yaml schema from assets/COURSE_TEMPLATE.yaml
- Always use `chapters` (never `modules`) per the Learning OS schema
- The `track` and `section_mapping` fields must be consistent — the `save-progress` skill reads them to write `.learning-progress`
- Keep LEARNING_PLAN.md sections focused; detailed content is added as you learn
