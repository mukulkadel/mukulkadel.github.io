---
layout: post
title: "Writing Idiomatic Python: Common Patterns and Anti-Patterns"
date: "2026-09-02 00:00:00 +0530"
slug: idiomatic-python-patterns-anti-patterns
description: "A practical guide to writing idiomatic Python, covering list comprehensions, generators, context managers, and the anti-patterns that give code away as non-Pythonic."
categories: ["Programming", "wiki"]
tags: ["python", "idiomatic", "best practices", "patterns", "list comprehensions", "generators", "context managers", "pythonic", "code quality"]
---

Python code that "works" and Python code that's idiomatic are two different things, and the gap between them usually isn't about cleverness — it's about using the language's own vocabulary instead of translating patterns from whatever language you learned first. Code written by someone who learned Python as a second language often has a distinct smell: manual index loops, explicit `is True` checks, verbose `if/else` where a one-liner would do. This post walks through the patterns that mark code as genuinely Pythonic, and the anti-patterns that mark it as a translation.

## Looping: Stop Reaching for `range(len(...))`

The most common tell that someone is writing Python like it's Java or C is manual index management in loops.

```python
# Anti-pattern
fruits = ["apple", "banana", "cherry"]
for i in range(len(fruits)):
    print(i, fruits[i])
```

```
0 apple
1 banana
2 cherry
```

Python gives you `enumerate()` specifically so you never need to do this:

```python
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits):
    print(i, fruit)
```

```
0 apple
1 banana
2 cherry
```

The same principle applies to iterating two lists together — reach for `zip()` instead of indexing both by a shared counter:

```python
names = ["Alice", "Bob", "Carol"]
scores = [92, 87, 95]

for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

```
Alice: 92
Bob: 87
Carol: 95
```

## List Comprehensions: Know Where They Stop Helping

Comprehensions are one of the most identifiably Pythonic constructs, and for good reason — they express "build a new collection from this one" more directly than a manual loop with an `append()` call.

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Anti-pattern: manual accumulation
squares = []
for n in numbers:
    if n % 2 == 0:
        squares.append(n ** 2)

# Idiomatic
squares = [n ** 2 for n in numbers if n % 2 == 0]
print(squares)
```

```
[4, 16, 36, 64, 100]
```

The anti-pattern here isn't the loop — it's writing the loop when the comprehension says the same thing more directly. But comprehensions can be pushed too far in the other direction. A comprehension with two nested `for` clauses and two `if` conditions is no longer more readable than a loop; it's a puzzle.

```python
# Anti-pattern: comprehension abuse
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
result = [x for row in matrix for x in row if x % 2 == 0 if x > 2]

# More readable as a loop once complexity rises
result = []
for row in matrix:
    for x in row:
        if x % 2 == 0 and x > 2:
            result.append(x)
```

Both produce `[4, 6, 8]`. The rule of thumb: one `for` and at most one `if` fits comfortably in a comprehension. Beyond that, a plain loop is more idiomatic, not less, because it's more readable.

## Generators: Don't Materialize What You Can Stream

A generator expression looks almost identical to a list comprehension, but the difference matters when you're processing data you don't need all at once.

```python
# Anti-pattern: builds the entire list in memory just to sum it
total = sum([n ** 2 for n in range(1_000_000)])

# Idiomatic: streams values one at a time, never holds the full list
total = sum(n ** 2 for n in range(1_000_000))
```

Both give the same `total`, but the generator version never allocates a million-element list — it produces values lazily as `sum()` consumes them. This matters more as the input grows; for reading a large log file line by line, the difference is the gap between constant memory and loading gigabytes into RAM:

```python
def error_lines(path):
    with open(path) as f:
        for line in f:
            if "ERROR" in line:
                yield line.strip()

for line in error_lines("app.log"):
    print(line)
```

## Context Managers: `with` Is Not Optional for Resources

Manually opening and closing resources is an anti-pattern because it's one exception away from a leak.

```python
# Anti-pattern
f = open("data.txt")
data = f.read()
f.close()  # never runs if read() raises
```

```python
# Idiomatic
with open("data.txt") as f:
    data = f.read()
```

The `with` statement guarantees `f.close()` runs even if an exception is raised inside the block. This isn't a style preference — it's the difference between a resource that's reliably released and one that leaks under error conditions you didn't test for.

Writing your own context managers is just as idiomatic, and `contextlib` makes it nearly free:

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(label):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed:.4f}s")

with timer("sleep"):
    time.sleep(0.2)
```

```
sleep: 0.2003s
```

## Truthiness: Let Python's Own Rules Do the Work

Explicit comparisons against `True`, `False`, empty containers, or `None` are a common anti-pattern that adds noise without adding correctness.

```python
items = []

# Anti-pattern
if len(items) == 0:
    print("empty")

if items == []:
    print("empty")

# Idiomatic
if not items:
    print("empty")
```

The same applies to boolean checks:

```python
is_valid = True

# Anti-pattern
if is_valid == True:
    process()

# Idiomatic
if is_valid:
    process()
```

The one place this rule inverts is checking for `None` specifically — `if not value` is ambiguous when `0`, `""`, or `[]` are also falsy but valid values, so identity comparison is the correct, idiomatic choice there:

```python
value = 0

# Wrong: 0 is falsy, so this incorrectly treats a valid value as missing
if not value:
    print("missing")

# Idiomatic: only None means missing
if value is None:
    print("missing")
```

## Unpacking: Named Values Beat Index Access

Tuple unpacking replaces index-based access with names, which is both more readable and less error-prone when the structure changes.

```python
point = (3, 7)

# Anti-pattern
x = point[0]
y = point[1]

# Idiomatic
x, y = point
```

Extended unpacking handles the "first, last, and everything in between" pattern that would otherwise need slicing:

```python
scores = [92, 87, 95, 78, 88]

first, *middle, last = scores
print(first, middle, last)
```

```
92 [87, 95, 78] 88
```

## Dictionaries: `.get()` and Comprehensions Over Manual Checks

Checking for key existence before accessing a dictionary is a pattern carried over from languages without a cleaner option.

```python
config = {"host": "localhost"}

# Anti-pattern
if "port" in config:
    port = config["port"]
else:
    port = 8080

# Idiomatic
port = config.get("port", 8080)
```

Building a dictionary from another iterable follows the same comprehension logic as lists:

```python
words = ["apple", "banana", "cherry"]

# Idiomatic
lengths = {word: len(word) for word in words}
print(lengths)
```

```
{'apple': 5, 'banana': 6, 'cherry': 6}
```

## Conclusion

Idiomatic Python isn't about knowing obscure tricks — it's about defaulting to the constructs the language was actually designed around: `enumerate()` and `zip()` instead of manual indices, comprehensions and generators instead of accumulator loops, `with` instead of manual cleanup, and truthiness instead of explicit comparisons. Each of these choices reads as more natural to someone fluent in Python, and several of them (context managers, generators) aren't just style — they fix real correctness and memory problems that the anti-pattern versions are prone to. The fastest way to internalize the difference is to read code that already does this well and notice, specifically, which construct it reached for and why.
