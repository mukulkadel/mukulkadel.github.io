---
layout: post
title: "Rate Limiting — Algorithms and Implementation Patterns"
date: "2026-05-25 00:00:00 +0530"
slug: rate-limiting-algorithms-explained
description: "Learn the four main rate limiting algorithms — fixed window, sliding window, token bucket, and leaky bucket — and how to implement them with Redis and Nginx."
categories: ["wiki", "Programming"]
tags: ["rate limiting", "token bucket", "leaky bucket", "sliding window", "api", "backend", "nginx", "redis", "performance"]
---

Without rate limiting, a single misbehaving client can exhaust your API's capacity and trigger cascading failures across your backend. Rate limiting puts a ceiling on how fast any one entity can make requests. The interesting part isn't the concept — it's choosing the right algorithm. Each one has different fairness properties, burst characteristics, and implementation complexity.

## Why Rate Limiting Matters

Rate limits protect against:
- **Accidental abuse**: a client with a bug sending thousands of requests per second
- **Intentional scraping**: competitors extracting your data en masse
- **Cost control**: when your API calls paid upstream services (LLMs, SMS providers)
- **Cascading failures**: one slow service overwhelming a downstream dependency

## Algorithm 1: Fixed Window Counter

The simplest approach: count requests in a fixed time window (e.g., per minute) and reset the counter at the boundary.

```python
import redis
import time

r = redis.Redis()

def is_allowed(user_id: str, limit: int = 100) -> bool:
    window = int(time.time() // 60)   # current minute bucket
    key = f"rate:{user_id}:{window}"

    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)

    return count <= limit
```

**The boundary problem**: a burst attack straddling the window can send 2x the limit. With a 100/min limit, a client can send 100 requests at 12:00:59 and 100 more at 12:01:00 — 200 requests within two seconds.

## Algorithm 2: Sliding Window Log

Track the timestamp of every request. Count how many timestamps fall within the last `window_size` seconds.

```python
import redis
import time

r = redis.Redis()

def is_allowed(user_id: str, limit: int = 100, window_secs: int = 60) -> bool:
    now = time.time()
    key = f"rate:log:{user_id}"

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_secs)  # evict old entries
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_secs)
    _, _, count, _ = pipe.execute()

    return count <= limit
```

Accurate and fair — no boundary burst. The trade-off: storing one timestamp per request is memory-intensive at scale. 1,000 users × 100 requests = 100,000 sorted set entries in Redis.

## Algorithm 3: Sliding Window Counter (Hybrid)

A practical middle ground: combine two fixed-window counters with a weighted formula to approximate a true sliding window.

```python
import redis
import time

r = redis.Redis()

def is_allowed(user_id: str, limit: int = 100, window_secs: int = 60) -> bool:
    now = time.time()
    current_window = int(now // window_secs)
    prev_window = current_window - 1

    elapsed_fraction = (now % window_secs) / window_secs

    prev_key = f"rate:{user_id}:{prev_window}"
    curr_key = f"rate:{user_id}:{current_window}"

    prev_count = int(r.get(prev_key) or 0)
    curr_count = r.incr(curr_key)
    if curr_count == 1:
        r.expire(curr_key, window_secs * 2)

    # The previous window contributes its remaining (unused) fraction
    weighted = prev_count * (1 - elapsed_fraction) + curr_count
    return weighted <= limit
```

This approximation is accurate to within a few percent of the true sliding window, at a fraction of the memory cost.

## Algorithm 4: Token Bucket

Each user has a bucket that refills with tokens at a fixed rate. Each request consumes one token. If the bucket is empty, the request is rejected.

- Allows **bursting** up to the bucket capacity
- Long-term average rate is governed by the refill rate

```python
import redis
import time

r = redis.Redis()

def is_allowed(
    user_id: str,
    capacity: int = 20,
    refill_rate: float = 10,   # tokens per second
) -> bool:
    key = f"rate:bucket:{user_id}"
    now = time.time()

    data = r.hgetall(key)
    tokens = float(data.get(b"tokens", capacity))
    last_refill = float(data.get(b"last_refill", now))

    elapsed = now - last_refill
    tokens = min(capacity, tokens + elapsed * refill_rate)

    if tokens < 1:
        return False

    tokens -= 1
    r.hset(key, mapping={"tokens": tokens, "last_refill": now})
    r.expire(key, 3600)
    return True
```

Token bucket is the right choice when you want to permit short bursts (a user firing 5 API calls in quick succession) while still enforcing a long-term average rate.

## Algorithm 5: Leaky Bucket

Requests enter a queue (the bucket) and are processed at a fixed output rate. If the bucket is full, new requests are dropped. Unlike the token bucket, leaky bucket smooths output — it's often used for traffic shaping rather than access control.

In practice, leaky bucket requires a FIFO queue with a rate-limited consumer, which is more complex to implement in stateless request handlers. It's more common in network equipment and proxy layers than in application-level API rate limiting.

## Choosing the Right Algorithm

| Algorithm | Burst handling | Memory | Accuracy | Best for |
|---|---|---|---|---|
| Fixed window | Double burst at boundary | Low | Low | Simple, non-critical limits |
| Sliding window log | No burst | High | Exact | Low-volume, strict limits |
| Sliding window counter | Small burst only | Low | ~95% | General-purpose API limits |
| Token bucket | Configurable burst | Low | Exact | User-facing APIs with burst allowance |
| Leaky bucket | No burst (smooth output) | Medium | Exact | Traffic shaping, queuing |

## Rate Limiting with Nginx

For IP-based limiting without application code:

```nginx
http {
    # Shared memory zone: 10MB stores ~160,000 IPs
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            limit_req_status 429;
            proxy_pass http://backend;
        }
    }
}
```

- `rate=10r/s`: token bucket refill rate (10 tokens per second)
- `burst=20`: bucket capacity — allows up to 20 queued requests before rejecting
- `nodelay`: burst requests are served immediately (not queued), up to `burst`; excess requests get 429

## Returning the Right Response

When a request is rate limited, return `429 Too Many Requests` with retry guidance:

```
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1748134800
Retry-After: 47

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Try again in 47 seconds."
  }
}
```

Always include `Retry-After`. Without it, well-intentioned clients with retry logic will immediately retry and make the problem worse.

## Choosing Your Rate Limit Key

What you're limiting on matters as much as the algorithm:

- **IP address**: protects against anonymous abuse but over-limits shared IPs (office NATs, Cloudflare exit nodes)
- **API key / user ID**: accurate per-client limiting; requires authentication upstream
- **Endpoint + user**: different limits for expensive endpoints (`/search`, `/export`) vs cheap ones (`/ping`)
- **Tenant / organization**: for multi-tenant SaaS, limit at the account level to prevent one customer from starving others

Combine keys for layered protection: a global IP limit to stop floods, a per-user limit for fair use, and a per-endpoint limit for your most expensive operations.

## Conclusion

Rate limiting is most effective when you choose the algorithm that matches your traffic pattern. Token bucket is the most versatile for user-facing APIs — it permits legitimate bursts while enforcing a long-term ceiling. Back it with Redis for distributed enforcement across multiple app servers, and layer Nginx upstream for infrastructure-level protection. Always include `Retry-After` in your 429 responses so well-behaved clients know when to back off, and design your limit keys to target the right entity at each layer.
