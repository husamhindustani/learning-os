# Quiz Question Patterns

Reference patterns for generating effective quiz questions across different content types.

## Question Types

### Multiple Choice (4 options)
Best for: Concepts with clear right/wrong answers, syntax questions, "which method does X"

```
Q: Which method would you use to flatten a list of lists into a single list?
A) map()
B) flatMap()    ← correct
C) reduce()
D) filter()
```

Rules:
- One clearly correct answer
- Distractors should be plausible (related methods, not random)
- Vary which letter is correct — do NOT always put the right answer at the same position

### Short Answer
Best for: "What does X return?", "What is the difference between X and Y?", definitions

```
Q: What does Optional.orElseGet() do differently from orElse()?
Expected: orElseGet() takes a Supplier and evaluates lazily (only if empty),
          while orElse() always evaluates its argument.
```

### Code Reading — "What does this do?"
Best for: Testing practical understanding of syntax and behavior

```
Q: What does this code print?
   List<String> list = List.of("a", "b");
   list.add("c");

Expected: Throws UnsupportedOperationException — List.of() returns an immutable list.
```

### Code Reading — "Will this compile?"
Best for: Type safety, generics, nullability, checked exceptions

```
Q: Will this compile? If not, why?
   Optional<String> opt = Optional.of(null);

Expected: No — Optional.of() throws NullPointerException for null.
          Use Optional.ofNullable() instead.
```

### Comparison
Best for: Concepts that are commonly confused, similar APIs with different behavior

```
Q: What is the difference between map() and flatMap() on Optional?
Expected: map() wraps the result in another Optional (can produce Optional<Optional<T>>).
          flatMap() expects the function to return an Optional and does not double-wrap.
```

### Practical / Scenario
Best for: "When would you use X?", design decisions, trade-offs

```
Q: You have a list of orders, each with a list of items. You want a single flat list
   of all items. Which stream operation would you use and why?

Expected: flatMap() — because each element (order) maps to multiple results (items).
          map() would give you Stream<List<Item>>, not Stream<Item>.
```

## Question Quality Rules

### Test understanding, not memorization
- Bad: "What does the acronym PECS stand for?"
- Good: "You have a method that adds items to a collection. Should the parameter use `? extends T` or `? super T`? Why?"

### Match depth to discussion
- Topic discussed superficially → ask basic definitional question
- Topic discussed deeply with examples → ask a scenario or edge case question
- Topic the user struggled with → ask the specific thing they got wrong, then test it

### Vary question positions
- Never put the correct answer in the same position multiple times in a row
- In a 6-question quiz, distribute A/B/C/D answers across questions

### Cover the tangents
If the user asked about Builder pattern while learning about immutability — include one Builder pattern question. Tangents reveal genuine curiosity and deserve reinforcement.

### Use real code from the session
If you worked through a specific code example together, reference it:
- "Earlier we used `Optional.flatMap()` to chain `getAddress().getCity()`. What would have happened if we used `map()` instead?"

## Difficulty Calibration

| Chapter type | Question mix |
|---|---|
| Early chapters (fundamentals) | 60% basic, 30% practical, 10% edge cases |
| Mid chapters (intermediate) | 40% basic, 40% practical, 20% edge cases |
| Advanced chapters | 20% basic, 40% practical, 40% edge cases / comparisons |

## Feedback Patterns

### Correct answer
> "Correct! [One sentence reinforcing why this matters or how to remember it.]"

Example: "Correct! orElseGet() is the lazy version — use it whenever the fallback is expensive to compute."

### Wrong answer
> "Not quite. [Correct answer in one sentence.] [Explanation of the mistake in 1-2 sentences.]"

Example: "Not quite. flatMap() is the right choice here. map() would give you `Stream<List<Item>>` — a stream of lists, not a flat stream of items. flatMap() flattens by calling stream() on each inner list."

### Partial answer (short answer questions)
> "Mostly right! You got [X], but also worth knowing: [Y]."
