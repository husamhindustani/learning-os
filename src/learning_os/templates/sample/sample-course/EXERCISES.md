# Python Basics — Exercises

---

## Data Types

### Exercise 1: Type detective

Look at each value below. Without running any code, identify its type:
- `42`
- `3.14`
- `"hello"`
- `True`
- `"42"`
- `int("3.14")`  ← will this work?

Then verify using `type()` in a Python shell.

### Exercise 2: Temperature converter

Write a function `celsius_to_fahrenheit(c)` that converts Celsius to Fahrenheit.
Formula: `F = (C × 9/5) + 32`

Test it with: 0°C → 32°F, 100°C → 212°F, -40°C → -40°F

### Exercise 3: Type conversion chain

Start with the string `"42"`. Using only `int()`, `float()`, and `str()`:
1. Convert it to an integer
2. Convert that to a float
3. Add 0.5 to it
4. Convert back to a string
5. Print the result

---

## Control Flow

### Exercise 1: FizzBuzz

Print numbers 1 to 30. For multiples of 3 print "Fizz", for multiples of 5 print "Buzz",
for multiples of both print "FizzBuzz".

### Exercise 2: Find the first even number

Given a list `[3, 7, 11, 4, 9, 6, 2]`, use a `for` loop with `break` to find and print
the first even number.

### Exercise 3: Countdown

Write a `while` loop that counts down from 10 to 1, then prints "Liftoff!".
Use `continue` to skip the number 5 (print "skipping 5" instead).

---

## Functions

### Exercise 1: Greeting function

Write a function `greet(name, greeting="Hello")` that prints `"[greeting], [name]!"`.
Test it with:
- `greet("Alice")` → `"Hello, Alice!"`
- `greet("Bob", "Hi")` → `"Hi, Bob!"`

### Exercise 2: Calculator

Write four functions: `add(a, b)`, `subtract(a, b)`, `multiply(a, b)`, `divide(a, b)`.
The divide function should return `None` (and print a warning) if `b` is 0.

### Exercise 3: Documented function

Write a function `is_palindrome(word)` that returns `True` if the word reads the same
forwards and backwards. Add a proper docstring explaining what it does, its parameter,
and its return value.
