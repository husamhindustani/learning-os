---
name: chapter-check
description: >-
  Reinforce learning on a chapter via quiz (recall) and/or hands-on practice
  (application). Use when the user says 'quiz me', 'test me', 'check my
  understanding', 'chapter check', 'practice [chapter]', or has just finished
  learning a chapter and wants to verify retention. Also use when user says
  'review [chapter]' or 'check [chapter-id]' to review a past chapter — offer
  quiz, practice, or both.
---

# Chapter Check

Reinforce learning — either from the current session or as a structured review of a past chapter.

**Review is multi-modal.** Recall and application test different things, and both matter:
- **Recall** — "can you retrieve and explain it?" → tested by a **quiz**.
- **Application** — "can you actually *do* it?" → tested by **practice** (performing the exercises/demos and observing real behavior).

For procedural/skill material (programming, infra, CLIs, tools, APIs) application is the truer test of mastery and surfaces gaps recall hides. Don't collapse review to quiz-only by default — pick the modality that fits the chapter and the learner.

See [references/QUIZ_PATTERNS.md](references/QUIZ_PATTERNS.md) for quiz question patterns and [references/PRACTICE_PATTERNS.md](references/PRACTICE_PATTERNS.md) for how to run a hands-on practice review.

## Step 1: Determine mode

**No arguments / just finished learning:**
→ **Current Session Mode** — quiz based on what was discussed this session

**User specifies a chapter (e.g., "quiz me on java8", "review streams-deep-dive"):**
→ **Review Mode** — review a past chapter from course materials and historical notes. Choose a modality (quiz / practice / both — see below).

**User specifies a chapter AND a topic (e.g., "check java8 lambdas"):**
→ **Focus Mode** — review that specific topic only. Quiz by default; if the user wants practice, follow [references/PRACTICE_PATTERNS.md](references/PRACTICE_PATTERNS.md) scoped to just the exercises/demos touching that topic.

---

## Current Session Mode — Deep Contextual Quiz

This is the primary mode. It creates a quiz that reflects the actual conversation, not just the chapter outline.

(If the user instead wants to *apply* what was just taught — e.g. "let me practice this" — follow [references/PRACTICE_PATTERNS.md](references/PRACTICE_PATTERNS.md) using the session context and the chapter's exercises, rather than quizzing.)

### Read the conversation

Look for:
- **Main topics taught** — what concepts were covered
- **Doubt areas** — topics with 3+ back-and-forth messages, re-explanations, "I don't get it"
- **Tangential topics** — related concepts explored beyond the chapter (patterns, tools, edge cases)
- **Specific questions asked** — "when to use X vs Y?" questions deserve quiz questions
- **Examples worked through** — code examples discussed deserve follow-up questions

### Set question count dynamically

- 1-2 questions per major concept taught
- +1-2 questions per topic with significant discussion (3+ messages)
- +1 question per important tangential topic explored
- Typical range: 5-8 questions, but adjust to conversation depth

### Prioritize questions

1. **Doubt areas first (40-50%)** — where they struggled or asked multiple questions
2. **Core concepts (30-40%)** — fundamental chapter topics
3. **Tangential topics (10-20%)** — related patterns/tools discussed
4. **Practical application (always 1-2)** — "when would you use X?"

### Make questions conversation-aware

Reference the session when relevant:
- "You asked about when to use flatMap vs map. Which would you use to..."
- "We discussed bounded wildcards. In this scenario..."
- "You struggled with [concept] — let's test it: ..."

---

## Review Mode — Structured Review of a Past Chapter

**First, choose the modality.** Ask: "Review **[chapter]** as a **quiz** (recall), **hands-on practice** (do the exercises/demos), or **both**?" Default suggestion: *both* for `programming`/`mixed` courses, *quiz* for `conceptual` ones (per COURSE.yaml `type`). If the user already said how (e.g. "practice [chapter]"), skip the question.

- **Practice** (or the practice half of **both**) → follow [references/PRACTICE_PATTERNS.md](references/PRACTICE_PATTERNS.md).
- **Quiz** (or the quiz half of **both**) → continue below. For **both**, run the quiz first, then practice.

### Load context

Load context from course materials and historical notes:

1. Read `courses/[course-id]/COURSE.yaml` — get chapter topics
2. Read the learning plan — find the chapter section, extract key concepts
3. Read `courses/[course-id]/EXERCISES.md` — find the chapter's exercises section
4. If the chapter has `source.content_files` in COURSE.yaml → read the book source content to draw quiz material from the original text as well as the teaching session
5. Read `courses/[course-id]/session-notes.md` — search for entries about this chapter:
   - What doubts they originally had
   - Original quiz score (if any)
   - Topics discussed in depth
   - Prior `(quiz: X/Y)` / `(practice: …)` tags — don't repeat the same drills unless the user asks

### Set question count

- Match original quiz count (from session notes) if available
- Otherwise: 5-8 questions covering all chapter topics
- Focus mode: 3-5 questions on the specific topic

### Prioritize questions

1. Core chapter topics (50-60%) — from COURSE.yaml topics list and learning plan
2. Book-specific content (10-20%) — concepts, definitions, or examples unique to the source book (only for book-based courses)
3. Historical struggle areas (20-30%) — from session notes
4. Practical application (1-2) — inspired by exercises

### Show comparison at end

```
Review Results: X/Y correct

Original session (YYYY-MM-DD): [score if found in session notes]
Today: X/Y
Improvement: +N / -N / First review

Strong areas: [topics]
[If gaps]: Consider reviewing: [specific topics]
```

---

## Present questions one at a time

Applies to the **quiz** paths only (Current Session, Review quiz, Focus quiz). A practice review uses `PRACTICE_PATTERNS.md` instead, not this section.

- Show one question
- Wait for answer
- Give immediate feedback:
  - Correct: "Correct! [brief reinforcement — one sentence]"
  - Incorrect: "Not quite. [correct answer] — [explanation of why]"
  - For current session mode: "Remember when we discussed [context from session]..."
- Move to next question

---

## Final summary

**Current session:**
```
Summary: X/Y correct

Strong areas: [topics]
Review recommended: [topics with wrong answers]

[Per-topic note referencing the session]:
- [Topic A]: Nailed it — our [example] really clicked
- [Topic B]: Small gap here — this was the [specific point] we covered

[If gaps]: Want me to clarify anything before you save progress?
[If clean]: Great work! Say "save my progress" when ready.
```

**Review mode (quiz):** see the "Show comparison at end" block above.

**Review mode (practice):** see [references/PRACTICE_PATTERNS.md](references/PRACTICE_PATTERNS.md) → "Wrap-up". For **both**, report the two axes together (Recall: X/Y; Application: what was done) and call out any gap that appears in one but not the other.

**Focus mode:**
```
[Topic] Quiz: X/Y correct

Understanding: Strong / Good / Needs review

[If needs review]: Want a quick refresher on [specific concept]?
[If strong]: Solid — you've got [topic] down.
```
