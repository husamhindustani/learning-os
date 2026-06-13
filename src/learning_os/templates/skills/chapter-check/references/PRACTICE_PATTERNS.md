# Practice Review Patterns

How to run a **practice (application) review** — the hands-on counterpart to a quiz. A quiz tests recall ("can you explain it?"); practice tests application ("can you actually do it?"). Use this when the user picks **practice** or **both** in `chapter-check` Review Mode.

The guiding principle: **the learner does the doing.** You present the task, then guide and react to what they report back. You don't perform the work for them — productive struggle is where application learning happens.

## Step 1: Load the practice material

Gather everything that makes the chapter *doable* (most of this is ignored by a pure quiz):

1. `courses/[course-id]/COURSE.yaml` — chapter `topics`, `exercises_section`, `demos`, and the `build` block (compile/run commands).
2. `courses/[course-id]/EXERCISES.md` — the chapter's exercises section (the primary script for the session).
3. `courses/[course-id]/resources/[chapter-id]/` — any runnable code artifacts saved by the `learn` skill. Re-running these at review time is high-value.
4. `demos` paths from COURSE.yaml — files to run/inspect.
5. `courses/[course-id]/session-notes.md` — what they struggled with before, and which exercises they've already done vs. skipped.

If a chapter has **no exercises, demos, or resources**: for conceptual chapters use the applied-scenario playbook below (that *is* practice for them); for others, there's nothing to run — say so and offer a quiz instead.

## Step 2: Pick the playbook by chapter nature

### Procedural playbook (programming / infra / tools / CLIs / APIs)

The learner performs real actions; you orchestrate and interpret.

- **Set the scene briefly** — what they'll build/run and why it reinforces the chapter.
- **Drive one exercise at a time.** Present the task in the learner's own environment terms; let them run it; ask them to paste the output or describe what happened.
- **React to real output.** This is the payoff: real runs surface things quizzes can't (config drift, ordering/timing, environment quirks, error messages). Dig into anything surprising.
- **Probe with "what would happen if…"** then have them try it — break a step on purpose, change a value, observe the failure mode. Failure modes teach.
- **Connect back to recall.** Tie each observation to the concept ("this is the readiness-vs-started distinction in action").
- **You may run read-only/idempotent checks yourself only if the learner asks** (e.g. listing state, reading a file). Mutating or creative steps stay with the learner by default.

### Applied-scenario playbook (conceptual chapters)

When there's nothing to literally execute, "application" means *using* the idea, not reciting it:

- Pose a **realistic scenario** and have the learner apply the chapter's concept to it ("design X under constraint Y", "this system is doing Z — what's wrong and how would you fix it?").
- Ask them to **trace / walk through** a process step by step.
- Have them make a **decision with trade-offs** and defend it ("which approach here, and why not the other?").
- React, correct, and connect — same as the procedural playbook, minus the terminal.

## Step 3: Adapt to performance (don't fix the count)

- Cover the exercises that matter; depth beats a target number.
- If the learner breezes through, raise difficulty (edge cases, "now make it fail", combine concepts).
- If a step reveals a gap, slow down and work it through before moving on.
- It's fine to stop early once application is clearly solid, or to go long if real issues surface.

## Quality rules

- **Make them do it** — resist the urge to run commands or write the answer for them.
- **Use the chapter's real assets** — exercises, demos, and saved `resources/` code, not invented toy tasks (unless coverage gaps require new ones, in which case match existing style).
- **Anchor every observation to a concept** — practice without reflection is just button-pushing.
- **Treat errors as the lesson, not an interruption** — a real error message is the best teaching moment available.

## Wrap-up

Summarize what was *done* and what it revealed:

```
Practice: [Chapter]

Completed: [exercises/demos run, artifacts re-run]
Observed:  [what worked, what broke, what surprised them]

Solid in practice: [topics they executed cleanly]
Shaky in practice: [topics where doing revealed a gap]

[If gaps]: Want to re-run [step], or revisit the concept behind it?
[If clean]: You can not just explain this — you can do it. That's mastery.
```

If this was a **both** review, hand these observations back to the `chapter-check` final summary so recall and application are reported together (a topic aced on the quiz but fumbled in practice — or the reverse — is the headline insight).

When finished, the learner can say "save my progress" — `save-progress` records the practice dimension (what was exercised and observed), so the next review knows what's already been drilled.
