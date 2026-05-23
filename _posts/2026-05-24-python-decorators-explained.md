---
layout: post
title: "Python Decorators: What They Are and When to Use Them"
date: "2026-05-24 00:00:00 +0530"
slug: python-decorators-explained
description: "A practical guide to Python decorators — how they work, how to write your own, and when they genuinely simplify code versus when they add unnecessary magic."
categories: ["Programming", "wiki"]
tags: ["python", "decorators", "functools", "metaprogramming", "tutorial", "functions", "flask", "backend", "design patterns"]
---

Decorators are one of Python's most elegant features — and one of the easiest to misuse. At their core they're just functions that wrap other functions, but the syntax makes them look more mysterious than they are. Once you understand the mechanism, you'll see them everywhere: Flask routes, Django views, retry logic, caching, access control. Let's break them down from first principles.

## Functions Are Objects

The key insight: in Python, functions are first-class objects. You can pass them around, store them in variables, and return them from other functions.

```python
def greet(name):
    return f"Hello, {name}!"

say_hello = greet
print(say_hello("Alice"))  # Hello, Alice!
```

A decorator is a function that accepts a function and returns a (usually modified) function.

## A Decorator From Scratch

```python
def loud(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Done")
        return result
    return wrapper

def add(a, b):
    return a + b

add = loud(add)   # manually applying the decorator
print(add(2, 3))
```

```
Calling add
Done
5
```

The `@` syntax is just syntactic sugar for that last line:

```python
@loud
def add(a, b):
    return a + b
```

This is exactly equivalent to `add = loud(add)`.

## Preserving Metadata with `functools.wraps`

Without `@wraps`, the wrapped function loses its name, docstring, and other metadata — which breaks tools like debuggers, `help()`, and logging:

```python
from functools import wraps

def loud(func):
    @wraps(func)           # copies __name__, __doc__, etc. from func
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print("Done")
        return result
    return wrapper
```

Always use `@wraps` when writing decorators. It's a one-liner that prevents a class of frustrating bugs.

## Decorators with Arguments

A decorator that accepts arguments needs an extra layer of nesting — a factory that returns the actual decorator:

```python
from functools import wraps

def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def say(message):
    print(message)

say("hello")
```

```
hello
hello
hello
```

The call chain: `repeat(3)` returns `decorator`, which is applied to `say`.

## Real-World Patterns

### Timing / Profiling

```python
import time
from functools import wraps

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timeit
def slow_query(n):
    time.sleep(0.1 * n)
    return n * n

slow_query(3)
```

```
slow_query took 0.3002s
```

### Retry Logic

```python
import time
from functools import wraps

def retry(times=3, delay=1.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(times=3, delay=0.5, exceptions=(ConnectionError,))
def fetch_data(url):
    # ... make HTTP request
    pass
```

### Caching with `functools.lru_cache`

Python ships a production-ready caching decorator:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(50))  # 12586269025 — instant, not recursive explosion
```

`@cache` (Python 3.9+) is an unbounded version with no `maxsize` argument.

### Access Control

```python
from functools import wraps
from flask import g, abort

def require_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(g, "user", None) or not g.user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return wrapper

@app.route("/admin/users")
@require_admin
def list_users():
    return render_template("users.html")
```

Note the order: `@app.route` is applied last (outermost), `@require_admin` is applied first (innermost). Decorators stack bottom-up.

## Class-Based Decorators

A class can act as a decorator if it implements `__call__`:

```python
from functools import wraps

class CountCalls:
    def __init__(self, func):
        wraps(func)(self)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call #{self.count} to {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
greet("Bob")
print(greet.count)  # 2
```

Class-based decorators are useful when the decorator needs to maintain state between calls.

## When to Use Decorators — and When Not To

**Good fit:**
- Cross-cutting concerns that apply to many functions: logging, timing, authentication, caching, retrying
- Framework hooks where the pattern is standardized (`@route`, `@property`, `@staticmethod`)
- Marking functions for registration or discovery

**Poor fit:**
- One-off logic for a single function — just write it inline
- Cases where the decoration changes behavior dramatically and isn't obvious to a reader
- Stacking many decorators on one function — it becomes hard to reason about the execution order

The rule of thumb: a decorator should do one thing transparently. If someone reading `@my_decorator` above a function can't easily guess what it does, it's probably adding unnecessary magic.

## Conclusion

Decorators are most valuable when you have behavior that needs to be applied consistently across many functions — timing, retrying, auth checks, caching. The pattern is always the same: a wrapper function that receives the original, does something before or after (or both), and returns the result. Use `@functools.wraps` every time, structure argument-accepting decorators as factories, and resist the urge to decorate things just because it looks elegant. The best decorators are invisible to the caller and obvious to the reader.
