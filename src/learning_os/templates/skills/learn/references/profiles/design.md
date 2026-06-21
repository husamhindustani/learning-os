# Teaching Profile: System Design

For "Design X" / architecture chapters (course `track: system-design`, `data-systems`, or any chapter whose goal is designing a system). Layers on top of PEDAGOGY.md — the generic principles still apply.

## Teaching arc per design chapter

Teach in this order; it mirrors how a design is actually reasoned about:

1. **Scope & requirements** — clarifying questions, scale, constraints.
2. **User flows + read/write model** — the flows the system serves, each tagged write / push / pull. Do this *before any component* — it's the map everything else hangs on (this is the "big picture before the parts" principle for design).
3. **High-level architecture** — the major components and how a request/message flows through them.
4. **Component deep-dives** — one at a time, the *mechanism* not just the box: how things are located, routed, stored. Don't hand-wave "it goes to the right place."
5. **Data model** — one table/store per access pattern; show the keys and why.
6. **Estimation / sizing** — back-of-the-envelope: load, storage, node counts, and what *bounds* each tier.
7. **Reliability & failure modes** — delivery guarantees, retries, what happens when a component dies.

## Artifacts (per PEDAGOGY "Show, don't hand-wave")

- **Runnable code** for any mechanism a learner would otherwise wonder "but how does that *actually* work?" (routing, dedup, fan-out cost, etc.). Save under `resources/<chapter-id>/`.
- **Flow diagrams** (text-based) for each end-to-end flow.

## End-of-chapter deliverables (one per design)

- `INTERVIEW-GUIDE.md` — 6 sections: 45-min script · domain cheat sheet · component glossary · interview gotchas · leadership design-review questions · meta-lesson. Match the gold-standard template in an existing design chapter's `resources/`.
- `FLOWS.md` — text diagrams for every flow.

## Framing

- Per topic, give a crisp **interview soundbite** (the spoken-answer version).
- Bias commentary toward **trade-offs, business risk, and design-review questions**.
- **Reinforce recurring patterns** across chapters (e.g. push-small/pull-large, store-references-not-payloads, at-least-once + dedup, one-table-per-access-pattern). Naming the repeat is half the learning.
