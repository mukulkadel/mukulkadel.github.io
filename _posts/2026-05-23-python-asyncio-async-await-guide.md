---
layout: post
title: "Python asyncio — Async/Await Explained with Examples"
date: "2026-05-23 00:00:00 +0530"
slug: python-asyncio-async-await-guide
description: "Learn how Python's asyncio event loop, coroutines, and async/await syntax work, with practical examples covering concurrent HTTP requests and async I/O."
categories: ["Programming", "wiki"]
tags: ["python", "asyncio", "async", "await", "concurrency", "event loop", "coroutines", "tutorial", "backend"]
---

If you've ever written a Python script that calls an API in a loop and thought "this should be faster," `asyncio` is probably what you're missing. Python's async/await model lets you run thousands of I/O-bound operations concurrently without threads, using a single-threaded event loop. It's the foundation of frameworks like FastAPI, aiohttp, and Starlette — and once the mental model clicks, it changes how you think about Python I/O.

## The Core Problem: Blocking I/O

Synchronous code blocks the entire program while waiting for I/O:

```python
import time
import requests

def fetch(url):
    return requests.get(url).json()

urls = ["https://httpbin.org/delay/1"] * 5

start = time.time()
results = [fetch(url) for url in urls]
print(f"Done in {time.time() - start:.1f}s")  # Done in 5.1s
```

Each request takes ~1 second and runs sequentially. With `asyncio`, all five requests run concurrently and the total time is just over 1 second.

## Coroutines and `async def`

A **coroutine** is a function defined with `async def`. It doesn't run when you call it — it returns a coroutine object that the event loop schedules.

```python
import asyncio

async def say_hello():
    print("Hello")
    await asyncio.sleep(1)  # suspends here, lets other coroutines run
    print("World")

# run it
asyncio.run(say_hello())
```

`await` is the key: it suspends the current coroutine and hands control back to the event loop, which can run other coroutines while waiting. You can only use `await` inside an `async def` function.

## Running Coroutines Concurrently

`await coroutine()` runs coroutines sequentially. `asyncio.gather()` runs them concurrently:

```python
import asyncio
import time

async def fetch_data(n):
    print(f"Starting fetch {n}")
    await asyncio.sleep(1)   # simulates an I/O wait
    print(f"Done fetch {n}")
    return f"result-{n}"

async def main():
    start = time.time()

    # sequential — takes 3 seconds
    r1 = await fetch_data(1)
    r2 = await fetch_data(2)
    r3 = await fetch_data(3)

    # concurrent — takes ~1 second
    results = await asyncio.gather(
        fetch_data(1),
        fetch_data(2),
        fetch_data(3),
    )
    print(results)            # ['result-1', 'result-2', 'result-3']
    print(f"{time.time() - start:.1f}s")

asyncio.run(main())
```

## Real HTTP Requests with `aiohttp`

`requests` is synchronous — it blocks. Use `aiohttp` for async HTTP:

```bash
$ pip install aiohttp
```

```python
import asyncio
import aiohttp
import time

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    urls = [f"https://jsonplaceholder.typicode.com/posts/{i}" for i in range(1, 11)]

    async with aiohttp.ClientSession() as session:
        start = time.time()
        results = await asyncio.gather(*[fetch(session, url) for url in urls])
        print(f"Fetched {len(results)} posts in {time.time() - start:.2f}s")

asyncio.run(main())
# Fetched 10 posts in 0.43s
```

The same 10 requests with `requests` in a loop would take ~4–5 seconds.

## Tasks: Firing and Forgetting

`asyncio.create_task()` schedules a coroutine to run in the background without waiting for it immediately:

```python
async def background_job(name):
    await asyncio.sleep(2)
    print(f"Job {name} complete")

async def main():
    task1 = asyncio.create_task(background_job("A"))
    task2 = asyncio.create_task(background_job("B"))

    print("Jobs started, doing other work...")
    await asyncio.sleep(0.5)
    print("Still doing other work...")

    # wait for both to finish
    await task1
    await task2
    print("All done")

asyncio.run(main())
# Jobs started, doing other work...
# Still doing other work...
# Job A complete
# Job B complete
# All done
```

## Common Pitfalls

**Calling blocking code in a coroutine.** Any synchronous blocking call — `time.sleep()`, `requests.get()`, file I/O with the built-in `open()` — blocks the entire event loop. Use async equivalents instead:

```python
# wrong — blocks the event loop
async def bad():
    time.sleep(1)
    data = open("file.txt").read()

# right
async def good():
    await asyncio.sleep(1)
    async with aiofiles.open("file.txt") as f:
        data = await f.read()
```

If you must call blocking code (a CPU-heavy function, a sync library), run it in a thread pool executor:

```python
import asyncio

def cpu_heavy(n):
    return sum(range(n))

async def main():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, cpu_heavy, 10_000_000)
    print(result)
```

**Forgetting `await`.** Calling a coroutine without `await` just creates the object — it never runs. Python 3.11+ will warn you about this, but it's a silent bug in older versions.

## asyncio in FastAPI

FastAPI is built on asyncio — route handlers can be async or sync:

```python
from fastapi import FastAPI
import aiohttp

app = FastAPI()

@app.get("/summary")
async def get_summary():
    async with aiohttp.ClientSession() as session:
        posts, users = await asyncio.gather(
            fetch(session, "https://jsonplaceholder.typicode.com/posts"),
            fetch(session, "https://jsonplaceholder.typicode.com/users"),
        )
    return {"post_count": len(posts), "user_count": len(users)}
```

FastAPI runs each request in an async context, so multiple requests can be served concurrently while any one of them is waiting on I/O.

## Conclusion

`asyncio` shines for I/O-bound workloads — network requests, database queries, file reads — where you'd otherwise waste time waiting. The mental model is: a single thread runs one coroutine at a time, but `await` points are where it can switch to another coroutine instead of sitting idle. Use `asyncio.gather()` for concurrent operations and `asyncio.create_task()` when you want to kick off background work. For CPU-bound tasks, asyncio won't help — that's where `multiprocessing` comes in.
