---
name: onboarding
description: >-
  Welcome a new user to Learning OS and guide them through workspace setup.
  Use when the user opens this workspace for the first time, when
  courses/REGISTRY.md is empty or missing, when the user says 'hello',
  'help', 'how do I start', 'what is this', or 'get started'.
---

# Learning OS Onboarding

Welcome the user and get them set up with their first course.

## When to activate

Activate this skill when any of these are true:
- `courses/REGISTRY.md` exists but has no active courses listed (fresh install)
- The user says "hello", "help", "how do I start", "what is this", "get started"
- No `.learning-progress` entries exist yet

## Step 1: Detect state

Check `courses/REGISTRY.md`:
- If it has active courses → go to **Returning User** flow
- If it is empty or only has the template header → go to **Fresh Install** flow

## Fresh Install Flow

### Welcome message

Say something like:

> Welcome to **Learning OS** — an AI-powered learning workspace.
>
> Here's how it works:
> - You create **courses** on any topic you want to learn
> - I teach you one concept at a time, check your understanding, and quiz you
> - Your progress is saved automatically so you can pick up where you left off
>
> To get started, let's create your first course. What would you like to learn?
>
> Examples:
> - "I want to learn Python basics"
> - "Teach me system design fundamentals"
> - "I'm studying React hooks"
> - "Help me learn Spanish vocabulary"

Wait for the user's response, then hand off to the `create-course` skill.

### After course creation

Once the first course is created, explain the core three interactions:

> You're all set! Here's how to use your workspace going forward:
>
> **Learn:** Just tell me what you want to learn — "teach me [chapter]" or "let's start [topic]"
>
> **Quiz:** When you finish a chapter, say "quiz me" or "check my understanding"
>
> **Save:** Say "save my progress" or "I'm done for today" to record what you covered
>
> Your progress and session notes are saved automatically in this repo.
> Ready? Say "teach me [first chapter name]" to begin!

## Returning User Flow

If the user already has courses set up:

1. Read `.learning-progress` to find the most recently updated track
2. Read `courses/REGISTRY.md` to find that course's details
3. Read `courses/[course-id]/COURSE.yaml` to find the current chapter
4. Show a brief status:

> Welcome back! Here's where you left off:
>
> **[Course Title]** — [Current Chapter]
> Last updated: [timestamp]
>
> Ready to continue? Say "continue" or "teach me [next chapter]".
> Or say "show my progress" to see everything.

## Notes

- Keep the welcome message warm and short — don't overwhelm with features
- The goal is to get them to their first learning session as fast as possible
- If they describe a topic, immediately start the `create-course` skill — don't ask clarifying questions first
- This is the only skill that handles "what is this" questions — all other skills assume setup is done
