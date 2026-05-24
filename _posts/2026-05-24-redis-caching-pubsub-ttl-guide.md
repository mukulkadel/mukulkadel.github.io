---
layout: post
title: "Redis — Caching, Pub/Sub, and TTL: A Practical Guide"
date: "2026-05-24 00:00:00 +0530"
slug: redis-caching-pubsub-ttl-guide
description: "Learn how to use Redis for caching, publish/subscribe messaging, and TTL-based expiry with practical code examples in Python and CLI."
categories: ["Programming", "wiki"]
tags: ["redis", "caching", "pub/sub", "ttl", "in-memory", "backend", "performance", "key-value", "nosql", "tutorial"]
---

Redis is one of those tools that shows up everywhere once you start looking — caching API responses, managing session tokens, powering real-time leaderboards, and brokering messages between services. It's an in-memory data store that's fast by design (sub-millisecond reads) and versatile enough to replace several dedicated systems at once. In this guide we'll cover the three most common use cases: caching with TTL, pub/sub messaging, and a few data structure tricks worth knowing.

## Getting Redis Running

The quickest way to get started locally is with Docker:

```bash
$ docker run -d -p 6379:6379 --name redis redis:7-alpine
$ docker exec -it redis redis-cli ping
PONG
```

Or on macOS with Homebrew:

```bash
$ brew install redis
$ brew services start redis
$ redis-cli ping
PONG
```

For Python, install the official client:

```bash
$ pip install redis
```

## Connecting in Python

```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.ping()  # True
```

`decode_responses=True` makes Redis return strings instead of bytes — almost always what you want.

## Caching with TTL

The most common Redis pattern: store the result of an expensive operation and expire it automatically after N seconds.

```python
import json
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_user(user_id: int) -> dict:
    cache_key = f"user:{user_id}"

    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # Simulate a slow DB query
    user = {"id": user_id, "name": "Alice", "email": "alice@example.com"}

    r.setex(cache_key, 300, json.dumps(user))  # expire in 5 minutes
    return user
```

`setex(key, seconds, value)` is shorthand for `SET key value EX seconds`. You can also set TTL separately:

```bash
$ redis-cli SET user:42 '{"name":"Alice"}'
OK
$ redis-cli EXPIRE user:42 300
(integer) 1
$ redis-cli TTL user:42
(integer) 298
```

### Cache invalidation

When the underlying data changes, delete the key explicitly:

```python
def update_user(user_id: int, data: dict):
    # ... update in DB ...
    r.delete(f"user:{user_id}")
```

### Checking if a key exists

```python
if r.exists("user:42"):
    print("cache hit")
```

## Common Data Structures

Redis isn't just a key-value store — it ships with several data structures that let you avoid writing logic that Redis can handle natively.

### Hashes (object-like storage)

Instead of serializing to JSON, store fields individually:

```bash
$ redis-cli HSET user:42 name Alice email alice@example.com role admin
(integer) 3
$ redis-cli HGET user:42 name
"Alice"
$ redis-cli HGETALL user:42
1) "name"
2) "Alice"
3) "email"
4) "alice@example.com"
5) "role"
6) "admin"
```

In Python:

```python
r.hset("user:42", mapping={"name": "Alice", "email": "alice@example.com"})
r.hget("user:42", "name")     # "Alice"
r.hgetall("user:42")          # {"name": "Alice", "email": "alice@example.com"}
```

### Sorted Sets (leaderboards, rate limiting)

```python
# Add scores
r.zadd("leaderboard", {"alice": 1500, "bob": 1200, "carol": 1750})

# Top 3
r.zrevrange("leaderboard", 0, 2, withscores=True)
# [('carol', 1750.0), ('alice', 1500.0), ('bob', 1200.0)]

# Increment score
r.zincrby("leaderboard", 50, "bob")
```

### Lists (queues, recent activity)

```python
r.lpush("recent_logins", "alice", "bob")  # push to head
r.lrange("recent_logins", 0, 9)           # last 10 logins
r.ltrim("recent_logins", 0, 99)           # keep only 100 entries
```

## Pub/Sub Messaging

Redis pub/sub lets processes communicate asynchronously without a dedicated message broker. One process publishes to a channel; any number of subscribers receive the message.

### Publisher

```python
import redis
import json
import time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

for i in range(5):
    message = json.dumps({"event": "order_placed", "order_id": i})
    r.publish("orders", message)
    print(f"Published: {message}")
    time.sleep(1)
```

### Subscriber

```python
import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
pubsub = r.pubsub()
pubsub.subscribe("orders")

print("Waiting for messages...")
for message in pubsub.listen():
    if message["type"] == "message":
        data = json.loads(message["data"])
        print(f"Received order: {data['order_id']}")
```

Run the subscriber in one terminal and the publisher in another. Messages arrive in real time.

### Pattern subscriptions

Subscribe to multiple channels with a glob pattern:

```python
pubsub.psubscribe("orders.*")  # matches orders.new, orders.cancelled, etc.
```

### Limitations to know

Pub/sub in Redis is fire-and-forget — messages sent while a subscriber is offline are lost. If you need durability or replay, use **Redis Streams** (`XADD`/`XREAD`) instead, which behave more like Kafka.

## Rate Limiting with Redis

A clean sliding-window rate limiter using a sorted set:

```python
import time
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def is_rate_limited(user_id: str, limit: int = 10, window: int = 60) -> bool:
    key = f"rate:{user_id}"
    now = time.time()
    cutoff = now - window

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, cutoff)     # remove old entries
    pipe.zadd(key, {str(now): now})           # add current request
    pipe.zcard(key)                           # count requests in window
    pipe.expire(key, window)
    results = pipe.execute()

    request_count = results[2]
    return request_count > limit
```

The pipeline batches all four commands into a single round trip, avoiding race conditions for most use cases.

## Atomic Operations

Redis executes each command atomically. For multi-step logic use `MULTI`/`EXEC` (transactions) or Lua scripts:

```bash
$ redis-cli
127.0.0.1:6379> MULTI
OK
127.0.0.1:6379> INCR counter
QUEUED
127.0.0.1:6379> INCR counter
QUEUED
127.0.0.1:6379> EXEC
1) (integer) 1
2) (integer) 2
```

In Python: `r.execute_command()` or use a `Pipeline` with `transaction=True`.

## Persistence Options

By default Redis is in-memory only — a restart loses all data. You can enable persistence:

- **RDB** (snapshots): periodic point-in-time dumps to disk. Fast restarts, risk of data loss between snapshots.
- **AOF** (append-only file): logs every write command. Slower but near-zero data loss.

For a pure cache where a cold start is acceptable, persistence is optional. For session storage or queues, enable at least AOF.

```bash
# In redis.conf
appendonly yes
appendfsync everysec
```

## Conclusion

Redis shines as a cache, a lightweight message bus, and a home for data structures that databases handle poorly — sorted sets, rate counters, session tokens. The TTL mechanism means expiry is automatic and you never have to write a cleanup job. Pub/sub is useful for decoupling services, though Redis Streams are worth knowing for any use case that requires durability. Once you have it in your stack, you'll reach for it constantly.
